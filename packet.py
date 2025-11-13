#пакет
from task import Task, TypeTask, StateTask
from enum import Enum
from dataclasses import dataclass, field
import json

#тип пакета
class TypePacket(Enum):
    MATH_PACK = "ВЫЧИСЛИТЕЛЬНЫЙ"
    INOUT_PACK = "ВВОД/ВЫВОД"
    BALANCED_PACK = "СБАЛАНСИРОВАННЫЙ"

@dataclass
class Packet:
    tasks: list = field(default_factory=list)  #список задач в пакете
    type: TypePacket = None  #тип пакета

    #инициализация пустого пакета или пакета из файла
    def __init__(self, filename: str = None):
        if filename:
            tasks_list = self.createByJson(filename)
            self.tasks = tasks_list if len(tasks_list) > 0 else []
            if self.tasks:
                self.type = self.checkPacketType()
            else:
                self.type = None
        else:
            self.tasks = []
            self.type = None

    #автоматическое опредение типа пакета   
    def checkPacketType(self):
        inout = 0
        math = 0
        for task in self.tasks:  
            if task.type == TypeTask.MATH:
                math += 1
            else:
                inout += 1
        if math == inout:
            return TypePacket.BALANCED_PACK
        elif math > inout:
            return TypePacket.MATH_PACK
        else:
            return TypePacket.INOUT_PACK
    
    #получить общее количество задач
    def getTasksCount(self):
        return len(self.tasks)
    
    #получить общую память пакета
    def getTasksMemory(self):
        memory = 0
        for task in self.tasks:
            memory += task.memory
        return memory
    
    #получить количество задача в состоянии ожидания выполнения
    def getWaitTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.WAIT:
                count += 1
        return count
    
    #получить количество задача в состоянии выполнения
    def getRunTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.RUN:
                count += 1
        return count
    
    #получить количество выполненых задач   
    def getReadyTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.READY:
                count += 1
        return count
    
    #получить количество математических задач
    def getMathTasks(self):
        count = 0
        for task in self.tasks:
            if task.type == TypeTask.MATH:
                count += 1
        return count    
    
    #получить количество задач ввода-вывода
    def getInOutTasks(self):
        count = 0
        for task in self.tasks:
            if task.type == TypeTask.INOUT:
                count += 1
        return count

    #создать пакет из json-файла
    @classmethod
    def createByJson(cls, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)        
    
        tasks_list = []
        for task_data in data['tasks']:
            task = Task(
                num=task_data['num'],
                type=TypeTask[task_data['type']],
                memory=task_data['memory']
            )
            tasks_list.append(task)
        return tasks_list