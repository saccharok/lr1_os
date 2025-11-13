#симуляция
import time
from osys import OS
from packet import Packet
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Simulation:
    max_blocks_count: int  #начальное количество разделов памяти
    ram: int  #объем оперативной памяти в ГБ
    json_file: str  #файл с задачами в формате JSON
    max_tacts: int  #максимальное количество тактов выполнения
    os: Optional[OS] = None  #экземпляр операционной системы
    start_time: float = 0  #время начала симуляции
    end_time: float = 0  #время окончания симуляции
    total_tacts: int = 0  #фактическое количество выполненных тактов
    memory_changes: list = field(default_factory=list)  #история изменений памяти
    
    #пост-инициализации
    def __post_init__(self):
        self.os = OS(ram=self.ram, max_blocks_count=self.max_blocks_count)
        self.os.initialize(self.json_file)
        self.start_time = time.time()
        self.memory_changes = [f"Начальное количество: {self.max_blocks_count} разделов"]
    
    #изменения количества разделов в памяти во время выполнения
    def changeMemoryBlocks(self, new_count: int):
        if self.os:
            old_count = self.max_blocks_count
            self.os.changeMemoryBlocksCount(new_count)
            self.max_blocks_count = new_count
            
            change_info = f"Такт {self.total_tacts}: {old_count} → {new_count} разделов"
            self.memory_changes.append(change_info)
    
    #запуск симуляции
    def runSimulation(self):
        self.total_tacts = 0
        
        if self.os.output_callback:
            self.os.output_callback("СТАРТ")
            total_memory_mb = self.os.packet.getTasksMemory()
            total_memory_gb = total_memory_mb / 1024
            self.os.output_callback(f"Суммарно RAM пакета: {total_memory_gb:.1f} ГБ")
            self.os.output_callback(f"Всего задач: {self.os.packet.getTasksCount()}")
            self.os.output_callback(f"MATH задач: {self.os.packet.getMathTasks()}")
            self.os.output_callback(f"INOUT задач: {self.os.packet.getInOutTasks()}")
            self.os.output_callback(f"Начальное количество разделов памяти: {self.max_blocks_count}")
        
        for tact in range(self.max_tacts):
            self.total_tacts = tact + 1
            self.os.runTact()

            if self.isSimOver():
                break

        self.end_time = time.time()
        
        if self.os.output_callback:
            self.os.output_callback("\nФИНИШ")
            self.os.output_callback(f"Все задачи выполнены за {self.total_tacts} тактов")
            self.os.output_callback(f"Финальное количество разделов памяти: {self.max_blocks_count}")
            
            if len(self.memory_changes) > 1:
                self.os.output_callback("\nИстория изменений разделов памяти:")
                for change in self.memory_changes:
                    self.os.output_callback(f"  {change}")
    
    #проверка условий завершения симуляции
    def isSimOver(self) -> bool:
        return (
            len(self.os.wait_queue) == 0 and 
            len(self.os.running_tasks) == 0 and 
            len(self.os.io_wait_tasks) == 0 and
            all(task is None or task.state.value == "ВЫПОЛНЕНА" for task in self.os.memory_blocks)
        )
    
    #получить время выполнения симуляции
    def getRunTime(self) -> float:
        return self.end_time - self.start_time
    
    #история изменения разделов памяти
    def getMemoryChanges(self) -> list:
        return self.memory_changes.copy()
    
    #сброс симуляции к начальному состоянию
    def reset(self):
        if self.os:
            self.os.reset() 
    
        self.start_time = time.time()
        self.end_time = 0
        self.total_tacts = 0
        self.memory_changes = [f"Начальное количество: {self.max_blocks_count} разделов"]
    
    #запуск симуляции
    def start(self):
        self.runSimulation()

"""
if __name__ == "__main__":
    sim = Simulation(
        max_blocks_count=8,
        ram=16,
        json_file="ready_packets/balanced_big_pack.json",
        max_tacts=100  # Количество тактов как параметр класса
    )
    sim.start()
"""