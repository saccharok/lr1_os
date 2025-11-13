import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel)
from PyQt6.QtCore import Qt

class Statistics(QWidget):    
    #конструктор
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.initUI()
    
    #сбор данных из истории выполнения ОС
    def collectRealData(self):
        history = self.simulation.os.history.copy()
        # Добавляем счетчики состояний CPU
        history['cpu_state_counts'] = self.simulation.os.getCpuStateCounts()
        return history
    
    #инициализация визуализации
    def initUI(self):
        main_layout = QVBoxLayout()
        
        title = QLabel("СТАТИСТИКА РАБОТЫ ОПЕРАЦИОННОЙ СИСТЕМЫ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin: 10px; color: #2c3e50;")
        main_layout.addWidget(title)
        
        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        main_layout.addWidget(self.info_container)
        
        self.setupGraphs()
        
        graphs_container = QWidget()
        self.graphs_layout = QGridLayout(graphs_container)
        self.graphs_layout.setSpacing(10)
        self.graphs_layout.setContentsMargins(10, 10, 10, 10)
        
        graphs_info = [
            (self.memory_plot, "Использование разделов памяти", ["Используемые разделы"]),
            (self.cpu_plot, "Распределение состояний процессора", [
                "Красный - ПРОСТОЙ", 
                "Зеленый - ВЫПОЛНЕНИЕ", 
                "Синий - ОЖИДАНИЕ В/В", 
                "Оранжевый - ПЕРЕГРУЗКА"
            ]),
            (self.tasks_plot, "Статусы задач", [
                "ОЖИДАНИЕ", 
                "ВЫПОЛНЕНИЕ", 
                "ВЫПОЛНЕНО"
            ]),
            (self.types_plot, "Типы задач", [
                "MATH задачи", 
                "INOUT задачи"
            ]),
            (self.free_mem_plot, "Свободная память", ["Свободная память %"]),
            (self.efficiency_plot, "Эффективность выполнения", ["% завершенных задач"])
        ]
        
        for i, (graph, title_text, legends) in enumerate(graphs_info):
            row = i // 3
            col = i % 3
            
            graph_container = QWidget()
            graph_container.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
            graph_layout = QVBoxLayout(graph_container)
            graph_layout.setContentsMargins(5, 5, 5, 5)
            graph_layout.setSpacing(5)
            
            title_label = QLabel(title_text)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3333FF; padding: 5px;")
            graph_layout.addWidget(title_label)
            
            if legends:
                legend_container = QWidget()
                legend_layout = QVBoxLayout(legend_container)
                legend_layout.setContentsMargins(5, 0, 5, 0)
                legend_layout.setSpacing(2)
                
                for legend_text in legends:
                    legend_label = QLabel(legend_text)
                    legend_label.setStyleSheet("font-size: 8pt; color: #666;")
                    legend_layout.addWidget(legend_label)
                
                graph_layout.addWidget(legend_container)
                
            graph.setMinimumSize(300, 180)
            graph.setMaximumSize(300, 180)
            graph_layout.addWidget(graph)
            
            self.graphs_layout.addWidget(graph_container, row, col)
        
        main_layout.addWidget(graphs_container)
        self.setLayout(main_layout)
        
        self.updateCharts()
    
    #обновление информации о симуляции
    def updateSimulationInfo(self):
        for i in reversed(range(self.info_layout.count())):
            widget = self.info_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        history = self.collectRealData()
        
        info_text = f"Всего тактов: {self.simulation.total_tacts} | " \
                   f"MATH задач: {history['task_types']['MATH']} | " \
                   f"INOUT задач: {history['task_types']['INOUT']} | " \
                   f"Разделов памяти: {self.simulation.max_blocks_count}"
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 12pt; color: #666; margin: 5px;")
        self.info_layout.addWidget(info_label)
        
        memory_changes = self.simulation.getMemoryChanges()
        if len(memory_changes) > 1:
            changes_text = "Изменения памяти: " + " → ".join([change.split(": ")[1].split(" ")[0] for change in memory_changes])
            changes_label = QLabel(changes_text)
            changes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            changes_label.setStyleSheet("font-size: 11pt; color: #2c3e50; margin: 3px; font-style: italic;")
            self.info_layout.addWidget(changes_label)
    
    #настройка графиков
    def setupGraphs(self):
        self.memory_plot = pg.PlotWidget()
        self.memory_plot.setBackground('w')
        self.memory_plot.setLabel('left', 'Количество разделов')
        self.memory_plot.setLabel('bottom', 'Такты')
        self.memory_plot.showGrid(x=True, y=True, alpha=0.3)
        self.memory_plot.setYRange(0, self.simulation.max_blocks_count)
        self.memory_curve = self.memory_plot.plot(pen=pg.mkPen('b', width=3))
        
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setBackground('w')
        self.cpu_plot.setLabel('left', 'Количество тактов')
        self.cpu_plot.setLabel('bottom', 'Состояния процессора')
        self.cpu_plot.showGrid(x=True, y=True, alpha=0.3)
        
        self.cpu_bars = None
            
        self.tasks_plot = pg.PlotWidget()
        self.tasks_plot.setBackground('w')
        self.tasks_plot.setLabel('left', 'Количество задач')
        self.tasks_plot.setLabel('bottom', 'Такты')
        self.tasks_plot.showGrid(x=True, y=True, alpha=0.3)
        
        task_colors = {
            'WAIT': '#ff6b6b',
            'RUN': '#4ecdc4',  
            'READY': '#45b7d1'
        }
        
        self.task_curves = {}
        for state, color in task_colors.items():
            self.task_curves[state] = self.tasks_plot.plot(pen=pg.mkPen(color, width=3))
            
        self.types_plot = pg.PlotWidget()
        self.types_plot.setBackground('w')
        self.types_pie = pg.PlotItem()
        self.types_plot.setCentralItem(self.types_pie)
        
        self.free_mem_plot = pg.PlotWidget()
        self.free_mem_plot.setBackground('w')
        self.free_mem_plot.setLabel('left', 'Проценты')
        self.free_mem_plot.setLabel('bottom', 'Такты')
        self.free_mem_plot.showGrid(x=True, y=True, alpha=0.3)
        self.free_mem_plot.setYRange(0, 100)
        self.free_mem_curve = self.free_mem_plot.plot(pen=pg.mkPen('g', width=3))
        
        self.efficiency_plot = pg.PlotWidget()
        self.efficiency_plot.setBackground('w')
        self.efficiency_plot.setLabel('left', 'Проценты')
        self.efficiency_plot.setLabel('bottom', 'Такты')
        self.efficiency_plot.showGrid(x=True, y=True, alpha=0.3)
        self.efficiency_plot.setYRange(0, 100)
        self.efficiency_curve = self.efficiency_plot.plot(pen=pg.mkPen('purple', width=3))
    
    #обновление графиков реальными данными
    def updateCharts(self):
        self.updateSimulationInfo()
        
        history = self.collectRealData()
        
        if not history['tacts']:
            self.showNoDataMessage()
            return
            
        tacts = history['tacts']
        
        if history['memory_blocks_used']:
            self.memory_curve.setData(tacts, history['memory_blocks_used'])
            
            self.memory_plot.setYRange(0, self.simulation.max_blocks_count)
            
        if 'cpu_state_counts' in history:
            state_counts = history['cpu_state_counts']
            
            print("=== ДАННЫЕ СОСТОЯНИЙ CPU ===")
            print(f"Всего тактов: {len(history['tacts'])}")
            print(f"Счетчики состояний: {state_counts}")
            print("============================")
            
            all_states = ["ПРОСТОЙ", "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ", "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА", "ПЕРЕГРУЗКА"]
            for state in all_states:
                if state not in state_counts:
                    state_counts[state] = 0
                    
            states = list(state_counts.keys())
            counts = list(state_counts.values())
            
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa726']
            
            if self.cpu_bars:
                self.cpu_plot.removeItem(self.cpu_bars)
                
            bg = pg.BarGraphItem(x=range(len(states)), height=counts, width=0.6, brushes=colors)
            self.cpu_plot.addItem(bg)
            self.cpu_bars = bg
            
            self.cpu_plot.getAxis('bottom').setTicks([[(i, self.getShortStateName(state)) for i, state in enumerate(states)]])
            self.cpu_plot.setXRange(-0.5, len(states) - 0.5)
            
            max_count = max(counts) if counts else 1
            self.cpu_plot.setYRange(0, max_count * 1.1)
            
        for state, curve in self.task_curves.items():
            if state in history['task_states'] and history['task_states'][state]:
                curve.setData(tacts, history['task_states'][state])
                
        self.updatePieChart()
        
        if history['memory_usage']:
            self.free_mem_curve.setData(tacts, history['memory_usage'])
            
        if history['task_states']['READY']:
            total_tasks = sum(history['task_types'].values())
            completed_tasks = history['task_states']['READY']
            completion_rate = [(tasks / total_tasks) * 100 if total_tasks > 0 else 0 
                            for tasks in completed_tasks]
            self.efficiency_curve.setData(tacts, completion_rate)

    #получение сокращенного названия состояния процессора
    def getShortStateName(self, full_name: str) -> str:
        short_names = {
            "ПРОСТОЙ": "ПРОСТОЙ",
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": "ВЫЧИСЛЕНИЯ", 
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": "ОЖИДАНИЕ В/В",
            "ПЕРЕГРУЗКА": "ПЕРЕГРУЗКА"
        }
        return short_names.get(full_name, full_name)
    
    #вывод сообщения об отсутствии данных
    def showNoDataMessage(self):
        for graph in [self.memory_plot, self.cpu_plot, self.tasks_plot, 
                     self.free_mem_plot, self.efficiency_plot]:
            graph.clear()
            text = pg.TextItem("Нет данных для отображения", color='red', anchor=(0.5, 0.5))
            text.setPos(5, 0)
            graph.addItem(text)
    
    #обновление круговой диаграммы
    def updatePieChart(self):
        history = self.collectRealData()
        math_count = history['task_types']['MATH']
        inout_count = history['task_types']['INOUT']
        
        self.types_pie.clear()
        
        if math_count == 0 and inout_count == 0:
            text = pg.TextItem("Нет данных", color='red', anchor=(0.5, 0.5))
            text.setPos(0, 0)
            self.types_pie.addItem(text)
            return
            
        total_tasks = math_count + inout_count
        math_angle = 2 * np.pi * math_count / total_tasks
        
        math_angles = np.linspace(0, math_angle, 100)
        math_x = np.cos(math_angles) * 0.8
        math_y = np.sin(math_angles) * 0.8
        math_curve = pg.PlotCurveItem(math_x, math_y, pen=pg.mkPen('#ff6b6b', width=4))
        self.types_pie.addItem(math_curve)
        
        inout_angles = np.linspace(math_angle, 2 * np.pi, 100)
        inout_x = np.cos(inout_angles) * 0.8
        inout_y = np.sin(inout_angles) * 0.8
        inout_curve = pg.PlotCurveItem(inout_x, inout_y, pen=pg.mkPen('#4ecdc4', width=4))
        self.types_pie.addItem(inout_curve)
        
        text_math = pg.TextItem("MATH", color='#ff6b6b', anchor=(0.5, 0.5))
        text_math.setPos(0.4, 0.4)
        self.types_pie.addItem(text_math)
        
        text_inout = pg.TextItem("INOUT", color='#4ecdc4', anchor=(0.5, 0.5))
        text_inout.setPos(-0.4, -0.4)
        self.types_pie.addItem(text_inout)
        
        if total_tasks > 0:
            percent_math = pg.TextItem(f"{math_count/total_tasks*100:.1f}%", 
                                     color='#ff6b6b', anchor=(0.5, 0.5))
            percent_math.setPos(0.2, 0.2)
            self.types_pie.addItem(percent_math)
            
            percent_inout = pg.TextItem(f"{inout_count/total_tasks*100:.1f}%", 
                                      color='#4ecdc4', anchor=(0.5, 0.5))
            percent_inout.setPos(-0.2, -0.2)
            self.types_pie.addItem(percent_inout)
    
    #метод для полного обновления статистики после новой симуляции
    def refreshStatistics(self):
        self.updateCharts()