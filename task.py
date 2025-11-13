#задача

from enum import Enum
from dataclasses import dataclass

#типы задач
class TypeTask(Enum):
    MATH = "MATH"
    INOUT = "INOUT"

#состояние задачи
class StateTask(Enum):
    WAIT = "ОЖИДАНИЕ ВЫПОЛНЕНИЯ"
    RUN = "В ПРОЦЕССЕ ВЫПОЛНЕНИЯ"
    READY = "ВЫПОЛНЕНА"

@dataclass
class Task:
    num: int  #номер задачи
    type: TypeTask  #тип задачи
    memory: int  #объем памяти для задачи
    state: StateTask = StateTask.WAIT  #текущее состояние задачи
    execution_time: int = 0  #время, затраченное на выполнение
    required_time: int = 0  #общее требуемое время для выполнения
    
    #пост-инифиализация
    #устанавливает требуемое время в зависимости от типа задачи
    def __post_init__(self):
        if self.type == TypeTask.MATH:
            self.required_time = 3  #MATH задачи выполняются 3 такта
        else:
            self.required_time = 2  #INOUT задачи выполняются 2 такта
    
    #изменение состояния задачи
    def changeState(self, stateTask: StateTask):
        self.state = stateTask
    
    #выполнение одного такта задачи
    def execute(self) -> bool:
        if self.state == StateTask.RUN:
            self.execution_time += 1
            if self.execution_time >= self.required_time:
                self.changeState(StateTask.READY)
                return True
        return False