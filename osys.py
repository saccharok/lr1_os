#операционная система

from packet import Packet, Task, TypeTask, StateTask
from cpu import CPU, StateCPU
from dataclasses import dataclass, field
from typing import List, Optional, Callable

@dataclass
class OS:
    """Класс операционной системы для управления задачами и ресурсами"""
    ram: int  #объем оперативной памяти в ГБ
    max_blocks_count: int  #максимальное количество разделов памяти
    packet: Optional[Packet] = None  #пакет задач для выполнения
    memory_blocks: List[Optional[Task]] = field(default_factory=list)  #разделы памяти с задачами
    wait_queue: List[Task] = field(default_factory=list)  #очередь ожидающих задач
    ready_queue: List[Task] = field(default_factory=list)  #очередь завершенных задач
    running_tasks: List[Task] = field(default_factory=list)  #список выполняющихся задач
    io_wait_tasks: List[Task] = field(default_factory=list)  #список задач, ожидающих ввод/вывод
    cpu: CPU = field(default_factory=CPU)  #процессор системы
    current_tact: int = 0  #текущий такт выполнения
    output_callback: Optional[Callable[[str], None]] = None  #функция для вывода информации
    
    #история выполнения для статистики
    history: dict = field(default_factory=lambda: {
        'tacts': [],
        'memory_blocks_used': [],
        'cpu_states': [],
        'task_states': {'WAIT': [], 'RUN': [], 'READY': []},
        'memory_usage': [],
        'task_types': {'MATH': 0, 'INOUT': 0}
    })
    
    #счетчики состояний процессора
    cpu_state_counts: dict = field(default_factory=lambda: {
        "ПРОСТОЙ": 0,
        "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
        "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
        "ПЕРЕГРУЗКА": 0
    })
    
    #инициализация системы
    def initialize(self, json_file: str):
        self.packet = Packet(json_file)
        self.wait_queue = self.packet.tasks.copy()
        self.memory_blocks = [None] * self.max_blocks_count
        self.current_tact = 0
        self.cpu.state = StateCPU.IDLE
        
        self.history = {
            'tacts': [],
            'memory_blocks_used': [],
            'cpu_states': [],
            'task_states': {'WAIT': [], 'RUN': [], 'READY': []},
            'memory_usage': [],
            'task_types': {
                'MATH': self.packet.getMathTasks(),
                'INOUT': self.packet.getInOutTasks()
            }
        }
        
        self.cpu_state_counts = {
            "ПРОСТОЙ": 0,
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
            "ПЕРЕГРУЗКА": 0
        }
    
    #изменение количества разделов памяти
    def changeMemoryBlocksCount(self, new_count: int):
        if new_count <= 0:
            raise ValueError("Количество разделов памяти должно быть положительным")
        
        old_count = self.max_blocks_count
        self.max_blocks_count = new_count
        
        current_tasks = [task for task in self.memory_blocks if task is not None]
        
        new_memory_blocks = [None] * new_count
        
        tasks_to_keep = min(len(current_tasks), new_count)
        for i in range(tasks_to_keep):
            new_memory_blocks[i] = current_tasks[i]
            
        for i in range(tasks_to_keep, len(current_tasks)):
            task = current_tasks[i]
            if task in self.running_tasks:
                self.running_tasks.remove(task)
            if task in self.io_wait_tasks:
                self.io_wait_tasks.remove(task)
            self.wait_queue.insert(0, task)  
        
        self.memory_blocks = new_memory_blocks
        
        self.updateCpuStateAfterMemoryChange()
        
        if self.output_callback:
            self.output(f"Изменено количество разделов памяти: {old_count} -> {new_count}")
            if len(current_tasks) > new_count:
                self.output(f"Возвращено в очередь: {len(current_tasks) - new_count} задач")
    
    #обновление состояния процессора после изменения настроек памяти
    def updateCpuStateAfterMemoryChange(self):
        used_blocks = sum(1 for block in self.memory_blocks if block is not None)
        
        if used_blocks > self.max_blocks_count:
            self.changeCpuState(StateCPU.OVERLOADED, "(перегрузка после изменения памяти)")
        elif self.cpu.state == StateCPU.OVERLOADED and used_blocks <= self.max_blocks_count:            
            self.changeToNormalState()
    
    #проверка и автоматическая настройка количества разделов памяти
    def checkAndAdjustMemoryBlocks(self):
        current_load = len(self.running_tasks)        
        if current_load < self.max_blocks_count // 2 and self.max_blocks_count > 2:
            new_count = max(self.max_blocks_count - 1, 2)
            self.changeMemoryBlocksCount(new_count)
            return True
                
        return False
    
    #установка функции обратного вызова для вывода информации
    def setOutputCallback(self, callback: Callable[[str], None]):
        self.output_callback = callback
    
    #вывод сообщения через установленный флаг
    def output(self, message: str):
        if self.output_callback:
            self.output_callback(message)
    
    #изменение состояние процессора с выводом информации о переходе из одного состояния в другое
    def changeCpuState(self, new_state: StateCPU, reason: str = ""):
        old_state = self.cpu.state
        if old_state != new_state:
            self.cpu.state = new_state
            self.output(f"ПЕРЕКЛЮЧЕНИЕ CPU: {old_state.value} -> {new_state.value} {reason}")
            
            current_used_blocks = sum(1 for block in self.memory_blocks if block is not None)
            math_count = len([task for task in self.running_tasks if task.type == TypeTask.MATH and task.state == StateTask.RUN])
            io_count = len([task for task in self.running_tasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN])
            self.output(f"Отладочная информация: Используется разделов={current_used_blocks}/{self.max_blocks_count}, MATH={math_count}, INOUT={io_count}")

    #сбор статистики за такт
    def collectStatistics(self):
        used_blocks = sum(1 for block in self.memory_blocks if block is not None)
        self.history['memory_blocks_used'].append(used_blocks)
        
        current_state = self.cpu.state.value
        self.history['cpu_states'].append(current_state)
        
        wait_count = len(self.wait_queue)
        run_count = len([task for task in self.running_tasks if task.state == StateTask.RUN])
        ready_count = len(self.ready_queue)
        
        self.history['task_states']['WAIT'].append(wait_count)
        self.history['task_states']['RUN'].append(run_count)
        self.history['task_states']['READY'].append(ready_count)
        
        used_memory_percent = (used_blocks / self.max_blocks_count) * 100
        free_memory_percent = max(0, 100 - used_memory_percent)
        self.history['memory_usage'].append(free_memory_percent)
        
        self.history['tacts'].append(self.current_tact)
    
    #возвращение счетчика состояний процессора для графика
    def getCpuStateCounts(self):
        return self.cpu_state_counts.copy()
    
    #управление переключением состояний процессора на основе текущей ситуации
    def manageCpuStates(self):
        self.checkOverload()
        
        if self.cpu.state != StateCPU.OVERLOADED:
            if self.cpu.state == StateCPU.IDLE:
                self.handleIdleState()
            elif self.cpu.state == StateCPU.EXECUTING:
                self.handleExecutingState()
            elif self.cpu.state == StateCPU.IO_WAIT:
                self.handleIoWaitState()
                
        current_state = self.cpu.state.value
        if current_state in self.cpu_state_counts:
            self.cpu_state_counts[current_state] += 1

    #проверка перегрузки системы
    def checkOverload(self):
        current_used_blocks = sum(1 for block in self.memory_blocks if block is not None)
    
        if current_used_blocks > self.max_blocks_count:
            if self.cpu.state != StateCPU.OVERLOADED:
                self.changeCpuState(StateCPU.OVERLOADED, 
                                f"(перегрузка памяти: {current_used_blocks} > {self.max_blocks_count} разделов)")
        else:
            if self.cpu.state == StateCPU.OVERLOADED:
                self.changeToNormalState()

    #возвращение процессора в нормальное состояние
    def changeToNormalState(self):
        math_tasks = [task for task in self.running_tasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        io_tasks = [task for task in self.running_tasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if math_tasks:
            self.changeCpuState(StateCPU.EXECUTING, "(система восстановилась, есть MATH задачи)")
        elif io_tasks:
            self.changeCpuState(StateCPU.IO_WAIT, "(система восстановилась, есть INOUT задачи)")
        else:
            self.changeCpuState(StateCPU.IDLE, "(система восстановилась, нет активных задач)")

    #обработка состояния простоя
    def handleIdleState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        math_tasks = [task for task in self.running_tasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        io_tasks = [task for task in self.running_tasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if math_tasks:
            self.changeCpuState(StateCPU.EXECUTING, f"(найдены {len(math_tasks)} активных MATH задач)")
        elif io_tasks:
            self.changeCpuState(StateCPU.IO_WAIT, f"(найдены {len(io_tasks)} активных INOUT задач)")

    #обработка состояния выполнения вычислений
    def handleExecutingState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        math_tasks = [task for task in self.running_tasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        io_tasks = [task for task in self.running_tasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if not math_tasks and io_tasks:
            self.changeCpuState(StateCPU.IO_WAIT, "(MATH задачи завершены, есть активные INOUT)")
        elif not math_tasks and not io_tasks:
            self.changeCpuState(StateCPU.IDLE, "(все активные задачи завершены)")

    #обработка состояния выполнения ввода/вывода
    def handleIoWaitState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        io_tasks = [task for task in self.running_tasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        math_tasks = [task for task in self.running_tasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        
        if not io_tasks and math_tasks:
            self.changeCpuState(StateCPU.EXECUTING, "(INOUT задачи завершены, есть активные MATH)")
        elif not io_tasks and not math_tasks:
            self.changeCpuState(StateCPU.IDLE, "(все активные задачи завершены)")
    
    #выполнение одного такта
    def runTact(self):
        self.current_tact += 1
        self.output(f"\nТакт-{self.current_tact}")
        
        self.output(f"Начальное состояние процессора: {self.cpu.state.value}")
        
        used_blocks = sum(1 for block in self.memory_blocks if block is not None)
        self.output(f"Используется разделов: {used_blocks}/{self.max_blocks_count}")
        
        memory_adjusted = self.checkAndAdjustMemoryBlocks()
        if memory_adjusted:
            used_blocks = sum(1 for block in self.memory_blocks if block is not None)
            self.output(f"После настройки: {used_blocks}/{self.max_blocks_count} разделов")
        
        for i, task in enumerate(self.memory_blocks):
            if task is not None:
                task_type = task.type.value
                self.output(f"Раздел {i+1}: Задача {task_type} {task.memory}MB {task.state.value}")
                    
        memory_freed = self.freeCompletedTasks()
        
        memory_loaded = self.loadTasksToMemory()
        
        if memory_freed or memory_loaded:
            used_blocks = sum(1 for block in self.memory_blocks if block is not None)
            self.output(f"Разделов памяти после загрузки/выгрузки: {used_blocks}/{self.max_blocks_count}")
                
        self.executeTasks()        
        self.manageCpuStates()        
        self.collectStatistics()        
        self.output(f"Финальное состояние процессора: {self.cpu.state.value}")
    
    #освобождение разделов памяти
    def freeCompletedTasks(self) -> bool:
        freed = False
        for i, task in enumerate(self.memory_blocks):
            if task and task.state == StateTask.READY:
                self.output(f"Задача {task.num} завершена, освобождается раздел {i+1}")
                self.memory_blocks[i] = None
                if task in self.running_tasks:
                    self.running_tasks.remove(task)
                if task in self.io_wait_tasks:
                    self.io_wait_tasks.remove(task)
                self.ready_queue.append(task)
                freed = True
        return freed
    
    #загрузка задачи в раздел
    def loadTasksToMemory(self) -> bool:
        loaded = False
    
        for i in range(len(self.memory_blocks)):
            if self.memory_blocks[i] is None and self.wait_queue:
                task = self.wait_queue.pop(0)
                self.memory_blocks[i] = task
                self.output(f"Задача {task.num} ({task.type.value}) загружена в раздел {i+1}")
                loaded = True
                
                current_used_blocks = sum(1 for block in self.memory_blocks if block is not None)
                if current_used_blocks > self.max_blocks_count:
                    self.output(f"ПРЕДУПРЕЖДЕНИЕ: Превышено максимальное количество разделов! ({current_used_blocks} > {self.max_blocks_count})")                   
        return loaded
    
    #выполнение задачи в разделе памяти
    def executeTasks(self):
        for i, task in enumerate(self.memory_blocks):
            if task and task.state == StateTask.WAIT:
                self.cpu.useToDoTask(task)
                self.output(f"Начато выполнение задачи {task.num} ({task.type.value}) в разделе {i+1}")
                
                if task.type == TypeTask.INOUT:
                    self.io_wait_tasks.append(task)
                
                self.running_tasks.append(task)
            
            elif task and task.state == StateTask.RUN:
                completed = task.execute()
                self.output(f"Задача {task.num} ({task.type.value}) выполняется: {task.execution_time}/{task.required_time} тактов")
                
                if completed:
                    self.output(f"Задача {task.num} ({task.type.value}) завершена!")
                    if task in self.io_wait_tasks:
                        self.io_wait_tasks.remove(task)
    
    #сброс состояния ОС к начальному (для перезапуска программы)
    def reset(self):
        if self.packet:
            self.wait_queue = self.packet.tasks.copy()
        else:
            self.wait_queue = []
        
        self.ready_queue = []
        self.running_tasks = []
        self.io_wait_tasks = []
        
        self.memory_blocks = [None] * self.max_blocks_count
        
        self.cpu.state = StateCPU.IDLE
        self.cpu.current_task = None
        
        self.current_tact = 0
        
        self.history = {
            'tacts': [],
            'memory_blocks_used': [],
            'cpu_states': [],
            'task_states': {'WAIT': [], 'RUN': [], 'READY': []},
            'memory_usage': [],
            'task_types': {
                'MATH': self.packet.getMathTasks() if self.packet else 0,
                'INOUT': self.packet.getInOutTasks() if self.packet else 0
            }
        }
        
        self.cpu_state_counts = {
            "ПРОСТОЙ": 0,
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
            "ПЕРЕГРУЗКА": 0
        }
        
        if self.packet:
            for task in self.packet.tasks:
                task.state = StateTask.WAIT
                task.execution_time = 0
        
        self.output("Система сброшена в начальное состояние")