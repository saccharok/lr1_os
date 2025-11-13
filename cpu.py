#процессор
from packet import Task, StateTask
from dataclasses import dataclass, field
from enum import Enum

#состоение процессора
class StateCPU(Enum):
    IDLE = "ПРОСТОЙ"
    EXECUTING = "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ"
    IO_WAIT = "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА"
    OVERLOADED = "ПЕРЕГРУЗКА"

@dataclass
class CPU:
    state: StateCPU = StateCPU.IDLE  #текущее состояние процессора
    current_task: Task = None  #задача, выполняемая в данный момент
    
    #назначить задачу на выполнение
    def useToDoTask(self, task: Task):
        task.changeState(StateTask.RUN)
        self.current_task = task
    
    #выполнение задачи
    def doTask(self, task: Task):
        task.changeState(StateTask.READY)
        self.current_task = None