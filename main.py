import sys
import random
import json

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QSpinBox, QMessageBox,
                             QLineEdit, QPushButton, QPlainTextEdit, QFileDialog, 
                             QDialog, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QGridLayout)
from PyQt6.QtGui import QKeyEvent, QPainter, QColor, QPen

from simulation import Simulation, Packet
from statisticsInfo import Statistics

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LR1 Zemskaya")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        headertext = "color: #3333FF; " \
                    "font-size: 25px; " \
                    "font-family: 'Century Gothic'; "
        maintext = "color: #000000; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        btntext = "color: #3333FF; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; " \
                    "background-color: #FFFFFF; "
        text = "color: #3333FF; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        
        self.mainlabel = QLabel('МОДЕЛИРОВАНИЕ РАБОТЫ\n' \
        'ОПЕРАЦИОННОЙ СИСТЕМЫ\n' \
        'РАБОТАЮЩЕЙ В ПАКЕТНОМ РЕЖИМЕ\n' \
        'С ИСПОЛЬЗОВАНИЕМ ПРИНЦИПА\n' \
        'КЛАССИЧЕСКОГО\n'\
        'МУЛЬТИПРОГРАММИРОВАНИЯ', self)
        self.mainlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainlabel.setStyleSheet(headertext+"font-weight: bold;")


        self.propertylabel = QLabel('Параметры системы', self)
        self.propertylabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.propertylabel.setStyleSheet(headertext)

        self.blocksvalue = QSpinBox(self)
        self.blocksvalue.setValue(1)
        self.blocksvalue.setMinimum(1)
        self.blocksvalue.setMaximum(64)
        self.blocksvalue.setStyleSheet(maintext)
        self.blockslabel = QLabel('Максимальное количество разделов', self)
        self.blockslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.blockslabel.setStyleSheet(maintext)

        self.tactsvalue = QSpinBox(self)
        self.tactsvalue.setValue(1)
        self.tactsvalue.setMinimum(1)
        self.tactsvalue.setMaximum(1000)
        self.tactsvalue.setStyleSheet(maintext)
        self.tactslabel = QLabel('Максимальное количество тактов (циклов)', self)
        self.tactslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tactslabel.setStyleSheet(maintext)

        self.ramvalue = QSpinBox(self)
        self.ramvalue.setValue(1)
        self.ramvalue.setMinimum(1)
        self.ramvalue.setMaximum(128)
        self.ramvalue.setStyleSheet(maintext)
        self.ramlabel = QLabel('RAM (ОП) в ГБ', self)
        self.ramlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ramlabel.setStyleSheet(maintext)

        self.packlabel = QLabel('Текущий пакет:', self)
        self.packlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.packlabel.setStyleSheet(maintext)
        self.filename = 'balanced_little_pack.json'
        self.packname = QLineEdit(self.filename, self)
        self.packname.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.packname.setReadOnly(True)
        self.packname.setStyleSheet(maintext)
        
        self.typepacklabel = QLabel('Тип текущего пакетa:', self)
        self.typepacklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.typepacklabel.setStyleSheet(maintext)
        
        self.typelabel = QLabel('', self)
        self.typelabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.typelabel.setStyleSheet(text)
        
        self.mathtasklabel = QLabel('Количество математических задач:', self)
        self.mathtasklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mathtasklabel.setStyleSheet(maintext)
        
        self.mathcountlabel = QLabel('', self)
        self.mathcountlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mathcountlabel.setStyleSheet(text)
        
        self.inouttasklabel = QLabel('Количество задач ввода/вывода:', self)
        self.inouttasklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.inouttasklabel.setStyleSheet(maintext)
        
        self.intoutcountlabel = QLabel('', self)
        self.intoutcountlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.intoutcountlabel.setStyleSheet(text)

        self.changepackbutton = QPushButton("Выбрать другой пакет",self)
        self.changepackbutton.setStyleSheet(btntext)
        self.changepackbutton.clicked.connect(self.changePacket)

        self.newpackbutton = QPushButton("Создать новый пакет",self)
        self.newpackbutton.setStyleSheet(btntext)
        self.newpackbutton.clicked.connect(self.createPacket)

        self.startbutton = QPushButton("СТАРТ СИМУЛЯЦИИ",self)
        self.startbutton.setStyleSheet(btntext)
        self.startbutton.clicked.connect(self.startSimulation)

        self.infolabel = QLabel('Для выхода из программы нажмите клавижу ESC', self)
        self.infolabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.infolabel.setStyleSheet(maintext)
        
        self.datatext = QPlainTextEdit('', self)
        self.datatext.setStyleSheet(maintext + "background-color: #D9D9D9; ")
        self.datatext.setReadOnly(True)

        self.top_graphs_container = QWidget(self)
        self.top_graphs_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #3333FF;")
        self.top_graphs_layout = QGridLayout(self.top_graphs_container)
        self.top_graphs_layout.setSpacing(5)
        self.top_graphs_layout.setContentsMargins(5, 5, 5, 5)
        
        self.bottom_graphs_container = QWidget(self)
        self.bottom_graphs_container.setStyleSheet("background-color: #FFFFFF; border: 1px solid #3333FF;")
        self.bottom_graphs_layout = QGridLayout(self.bottom_graphs_container)
        self.bottom_graphs_layout.setSpacing(5)
        self.bottom_graphs_layout.setContentsMargins(5, 5, 5, 5)
        
        self.top_graph_widgets = []
        self.bottom_graph_widgets = []
        
        for i in range(3):
            top_widget = QLabel(f"График {i+1}\n(запустите симуляцию)")
            top_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            top_widget.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCCCCC; color: #666666; font-size: 12px;")
            top_widget.setMinimumSize(200, 150)
            self.top_graph_widgets.append(top_widget)
            self.top_graphs_layout.addWidget(top_widget, 0, i)
            
            bottom_widget = QLabel(f"График {i+4}\n(запустите симуляцию)")
            bottom_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bottom_widget.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCCCCC; color: #666666; font-size: 12px;")
            bottom_widget.setMinimumSize(200, 150)
            self.bottom_graph_widgets.append(bottom_widget)
            self.bottom_graphs_layout.addWidget(bottom_widget, 0, i)

        self.getPackInfo()
        
        self.statistics_widget = None
        self.simulation = None
        self.statistics_initialized = False

        self.showFullScreen()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        width = self.width()
        height = self.height()
        cell_width = width // 3
        cell_height = height // 3
        
        left_column_width = 2 * cell_width
        left_section_height = height // 3
        
        self.datatext.setGeometry(0, 0, left_column_width, left_section_height)
        
        self.top_graphs_container.setGeometry(0, left_section_height, left_column_width, left_section_height)
        
        self.bottom_graphs_container.setGeometry(0, 2 * left_section_height, left_column_width, left_section_height)
        
        padding = 50
        
        self.mainlabel.setGeometry(2 * cell_width, 0, cell_width, cell_height)
        
        self.propertylabel.setGeometry(2 * cell_width, cell_height, cell_width, cell_height)

        self.blockslabel.setGeometry(2 * cell_width + padding * 2, cell_height + padding, cell_width, cell_height - padding)
        self.tactslabel.setGeometry(2 * cell_width + padding * 2, cell_height + padding * 2, cell_width, cell_height - padding * 2)
        self.ramlabel.setGeometry(2 * cell_width + padding * 2, cell_height + padding * 3, cell_width, cell_height - padding * 3)
        self.packlabel.setGeometry(2 * cell_width + 10, cell_height + padding * 4, cell_width, cell_height - padding * 4)

        self.blocksvalue.setGeometry(2 * cell_width + 10, cell_height + padding - 7, 80, 35)
        self.tactsvalue.setGeometry(2 * cell_width + 10, cell_height + padding * 2 - 7, 80, 35)
        self.ramvalue.setGeometry(2 * cell_width + 10, cell_height + padding * 3 - 7, 80, 35)
        self.packname.setGeometry(2 * cell_width + padding * 3, cell_height + padding * 4 - 7, 325, 35)

        self.changepackbutton.setGeometry(2 * cell_width + 10, cell_height + padding * 5 - 7, 195, 35)
        self.newpackbutton.setGeometry(2 * cell_width + 280, cell_height + padding * 5 - 7, 195, 35)

        self.typepacklabel.setGeometry(2 * cell_width + 10, cell_height + padding * 6 - 7, cell_width - 20, 30)
        self.typelabel.setGeometry(2 * cell_width + 300, cell_height + padding * 6 - 7, cell_width - 20, 30)

        self.mathtasklabel.setGeometry(2 * cell_width + 10, cell_height + padding * 7 - 7, cell_width - 20, 30)
        self.mathcountlabel.setGeometry(2 * cell_width + 300, cell_height + padding * 7 - 7, cell_width - 20, 30)

        self.inouttasklabel.setGeometry(2 * cell_width + 10, cell_height + padding * 8 - 7, cell_width - 20, 30)
        self.intoutcountlabel.setGeometry(2 * cell_width + 300, cell_height + padding * 8 - 13, cell_width - 20, 30)
        
        self.startbutton.setGeometry(2 * cell_width + 150, cell_height + padding * 9 - 7, 195, 45)

        self.infolabel.setGeometry(2*cell_width, 2*cell_height + padding * 5, cell_width, cell_height)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.fillRect(self.rect(), QColor("#D9D9D9"))

        pen = QPen(QColor("white"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        height = self.height()
        width = self.width()
        third_height = height // 3
        third_width = width // 3
        
        painter.drawLine(2 * third_width, 0, 2 * third_width, height)
        painter.drawLine(0, third_height, 2 * third_width, third_height)

    def getPackInfo(self):
        file = 'ready_packets/'+ str(self.packname.text())
        self.packet = Packet(file)
        self.typelabel.setText(self.packet.type.value)
        self.mathcountlabel.setText(str(self.packet.getMathTasks()))
        self.intoutcountlabel.setText(str(self.packet.getInOutTasks()))

    def changePacket(self):
        filename, ok = QFileDialog.getOpenFileName(
        self,
        "Выбрать пакет", 
        "ready_packets/", 
        "Packet (*.json)"
        )
        if ok and filename:
            self.packname.setText(filename.split('/')[-1])  
            self.getPackInfo()

    def startSimulation(self):
        try:
            self.datatext.clear()
            self.simulation = Simulation(
                max_blocks_count=self.blocksvalue.value(),
                ram=self.ramvalue.value(),
                json_file='ready_packets/' + self.packname.text(),
                max_tacts=self.tactsvalue.value()
            )
            self.simulation.os.setOutputCallback(self.outputCallback)
            self.simulation.start()
            
            QTimer.singleShot(100, self.setupStatisticsAfterSimulation)
            
            self.datatext.appendPlainText(f"Время выполнения симуляции: {self.simulation.getRunTime():.2f} секунд")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить симуляцию: {str(e)}")

    def setupStatisticsAfterSimulation(self):
        try:
            if self.simulation:
                if self.statistics_widget:
                    self.statistics_widget.simulation = self.simulation
                    if hasattr(self.statistics_widget, 'refreshStatistics'):
                        self.statistics_widget.refreshStatistics()
                    else:
                        self.statistics_widget = Statistics(self.simulation)
                        self.replaceGraphPlaceholders()
                else:
                    self.statistics_widget = Statistics(self.simulation)
                    self.replaceGraphPlaceholders()
                    
                if hasattr(self.statistics_widget, 'updateCharts'):
                    self.statistics_widget.updateCharts()
                
                self.statistics_initialized = True
                
        except Exception as e:
            print(f"Ошибка при создании статистики: {e}")

    def outputCallback(self, tact_info: str):
        self.datatext.appendPlainText(tact_info)
        cursor = self.datatext.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.datatext.setTextCursor(cursor)
        QApplication.processEvents()

    def replaceGraphPlaceholders(self):
        if not self.statistics_widget:
            return
        
        for i in reversed(range(self.top_graphs_layout.count())):
            widget = self.top_graphs_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        for i in reversed(range(self.bottom_graphs_layout.count())):
            widget = self.bottom_graphs_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        graphs = [
            self.statistics_widget.memory_plot,
            self.statistics_widget.cpu_plot,
            self.statistics_widget.tasks_plot,
            self.statistics_widget.types_plot,
            self.statistics_widget.free_mem_plot,
            self.statistics_widget.efficiency_plot
        ]
        
        titles = [
            "Использование памяти",
            "Состояния CPU", 
            "Статусы задач",
            "Типы задач",
            "Свободная память",
            "Эффективность"
        ]
        
        for i, (graph, title) in enumerate(zip(graphs, titles)):
            if i < 3:  
                container = self.top_graphs_container
                layout = self.top_graphs_layout
            else:  
                container = self.bottom_graphs_container
                layout = self.bottom_graphs_layout
                i = i - 3  
                
            graph_container = QWidget()
            graph_layout = QVBoxLayout(graph_container)
            graph_layout.setContentsMargins(2, 2, 2, 2)
            graph_layout.setSpacing(2)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3333FF;")
            graph_layout.addWidget(title_label)
            
            graph.setMinimumSize(250, 180)
            graph.setMaximumSize(250, 180)
            graph_layout.addWidget(graph)
            
            layout.addWidget(graph_container, 0, i)

    def createPacket(self):
        maintext = "color: #000000; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        btntext = "color: #3333FF; " \
                    "font-size: 10px; " \
                    "font-family: 'Century Gothic'; " \
                    "background-color: #FFFFFF; "
        dialog = QDialog(self)
        dialog.setWindowTitle("Создание нового пакета")
        dialog.setFixedSize(500, 600)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - 500) // 2
        y = (screen_geometry.height() - 600) // 2
        dialog.move(x, y)

        dialog.setStyleSheet("background-color: #D9D9D9;")

        tasks_list = []  
        task_counter = 1  
        
        central_widget = QWidget()
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        pack_name_layout = QHBoxLayout()
        pack_name_layout.setContentsMargins(0, 0, 0, 0)
        
        pack_name_label = QLabel('Имя пакета:')
        pack_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pack_name_label.setStyleSheet(maintext)
        pack_name_label.setFixedWidth(100)
        
        pack_name_edit = QLineEdit()
        pack_name_edit.setPlaceholderText("Введите имя пакета")
        pack_name_edit.setStyleSheet(maintext)
        pack_name_edit.setFixedWidth(200)
        
        pack_name_layout.addWidget(pack_name_label)
        pack_name_layout.addWidget(pack_name_edit)
        pack_name_layout.addStretch()
        
        main_layout.addLayout(pack_name_layout)
        
        blocksvalue = QSpinBox()
        blocksvalue.setValue(1)
        blocksvalue.setMinimum(1)
        blocksvalue.setMaximum(1000)
        blocksvalue.setStyleSheet(maintext)
        blocksvalue.setFixedWidth(60)
        
        blockslabel = QLabel('Количество задач:')
        blockslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        blockslabel.setStyleSheet(maintext)
        
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 0, 0)
        spinbox_layout.addWidget(blockslabel)
        spinbox_layout.addWidget(blocksvalue)
        spinbox_layout.addStretch()
        
        main_layout.addLayout(spinbox_layout)
        
        random_label = QLabel('Создать пакет рандомно')
        random_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        random_label.setStyleSheet(maintext)
        main_layout.addWidget(random_label)
        
        buttons_row_layout = QHBoxLayout()
        buttons_row_layout.setSpacing(8)
        buttons_row_layout.setContentsMargins(0, 0, 0, 0)
        
        compute_button = QPushButton("ВЫЧИСЛИТЕЛЬНЫЙ")
        compute_button.setStyleSheet(btntext)
        compute_button.setFixedSize(140, 35)
        
        io_button = QPushButton("ВВОД/ВЫВОД")
        io_button.setStyleSheet(btntext)
        io_button.setFixedSize(140, 35)
        
        balanced_button = QPushButton("СБАЛАНСИРОВАННЫЙ")
        balanced_button.setStyleSheet(btntext)
        balanced_button.setFixedSize(140, 35)
        
        buttons_row_layout.addWidget(compute_button)
        buttons_row_layout.addWidget(io_button)
        buttons_row_layout.addWidget(balanced_button)
        
        main_layout.addLayout(buttons_row_layout)
        
        manual_label = QLabel('Добавить позадачно:')
        manual_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        manual_label.setStyleSheet(maintext)
        main_layout.addWidget(manual_label)
        
        input_container_layout = QHBoxLayout()
        input_container_layout.setSpacing(15)
        
        left_input_layout = QVBoxLayout()
        left_input_layout.setSpacing(12)
        
        task_type_layout = QHBoxLayout()
        task_type_layout.setContentsMargins(0, 0, 0, 0)
        
        task_type_label = QLabel('Тип задачи:')
        task_type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        task_type_label.setStyleSheet(maintext)
        task_type_label.setFixedWidth(100)
        
        task_type_combo = QComboBox()
        task_type_combo.addItems(["MATH", "INOUT"])
        task_type_combo.setStyleSheet(maintext)
        task_type_combo.setFixedWidth(200)
        
        task_type_layout.addWidget(task_type_label)
        task_type_layout.addWidget(task_type_combo)
        task_type_layout.addStretch()
        
        left_input_layout.addLayout(task_type_layout)
        
        memory_layout = QHBoxLayout()
        memory_layout.setContentsMargins(0, 0, 0, 0)
        
        memory_label = QLabel('Память в МБ:')
        memory_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        memory_label.setStyleSheet(maintext)
        memory_label.setFixedWidth(100)
        
        memory_spinbox = QSpinBox()
        memory_spinbox.setValue(1)
        memory_spinbox.setMinimum(1)
        memory_spinbox.setMaximum(128 * 1024)
        memory_spinbox.setStyleSheet(maintext)
        memory_spinbox.setFixedWidth(200)
        
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(memory_spinbox)
        memory_layout.addStretch()
        
        left_input_layout.addLayout(memory_layout)
        
        add_task_button = QPushButton("Добавить\nзадачу")
        add_task_button.setStyleSheet(btntext + "font-size: 12px;")
        add_task_button.setFixedSize(100, 70)
        
        input_container_layout.addLayout(left_input_layout)
        input_container_layout.addWidget(add_task_button)
        
        main_layout.addLayout(input_container_layout)
        
        tasks_text = QPlainTextEdit()
        tasks_text.setStyleSheet(maintext + "background-color: #FFFFFF; border: 1px solid #3333FF;")
        tasks_text.setFixedHeight(150)
        tasks_text.setReadOnly(True)
        
        header = f"{'НОМЕР':<30} {'ТИП':<30} {'ПАМЯТЬ':<30}"
        separator = "-" * 80
        
        tasks_text.appendPlainText(header)
        tasks_text.appendPlainText(separator)
        
        main_layout.addWidget(tasks_text)

        main_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet(btntext)
        save_button.setFixedSize(100, 35)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet(btntext)
        cancel_button.setFixedSize(100, 35)
        cancel_button.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        def generateMathPacket():
            nonlocal tasks_list, task_counter
            tasks_list.clear()
            tasks_text.clear()
            tasks_text.appendPlainText(header)
            tasks_text.appendPlainText(separator)
            
            num_tasks = blocksvalue.value()
            
            math_ratio = random.uniform(0.7, 0.9)
            math_tasks = max(1, int(num_tasks * math_ratio))
            io_tasks = num_tasks - math_tasks
            
            for i in range(math_tasks):
                task_num = task_counter
                task_type = "MATH"
                memory = random.randint(100, 1000)
                
                tasks_list.append({
                    "num": task_num,
                    "type": task_type,
                    "memory": memory
                })
                
                task_line = f"{task_num:<30} {task_type:<30} {memory:<30}"
                tasks_text.appendPlainText(task_line)
                task_counter += 1
                
            for i in range(io_tasks):
                task_num = task_counter
                task_type = "INOUT"
                memory = random.randint(50, 500)
                
                tasks_list.append({
                    "num": task_num,
                    "type": task_type,
                    "memory": memory
                })
                
                task_line = f"{task_num:<30} {task_type:<30} {memory:<30}"
                tasks_text.appendPlainText(task_line)
                task_counter += 1

        def generateIOPacket():
            nonlocal tasks_list, task_counter
            tasks_list.clear()
            tasks_text.clear()
            tasks_text.appendPlainText(header)
            tasks_text.appendPlainText(separator)
            
            num_tasks = blocksvalue.value()
            
            io_ratio = random.uniform(0.7, 0.9)
            io_tasks = max(1, int(num_tasks * io_ratio))
            math_tasks = num_tasks - io_tasks
            
            for i in range(io_tasks):
                task_num = task_counter
                task_type = "INOUT"
                memory = random.randint(50, 500)
                
                tasks_list.append({
                    "num": task_num,
                    "type": task_type,
                    "memory": memory
                })
                
                task_line = f"{task_num:<30} {task_type:<30} {memory:<30}"
                tasks_text.appendPlainText(task_line)
                task_counter += 1
                
            for i in range(math_tasks):
                task_num = task_counter
                task_type = "MATH"
                memory = random.randint(100, 1000)
                
                tasks_list.append({
                    "num": task_num,
                    "type": task_type,
                    "memory": memory
                })
                
                task_line = f"{task_num:<30} {task_type:<30} {memory:<30}"
                tasks_text.appendPlainText(task_line)
                task_counter += 1

        def generateBalancedPacket():
            nonlocal tasks_list, task_counter
            tasks_list.clear()
            tasks_text.clear()
            tasks_text.appendPlainText(header)
            tasks_text.appendPlainText(separator)
            
            num_tasks = blocksvalue.value()
            
            if num_tasks % 2 != 0:
                num_tasks = num_tasks + 1
            
            math_tasks = num_tasks // 2
            io_tasks = num_tasks // 2
            
            all_tasks = []
            
            for i in range(math_tasks):
                all_tasks.append({
                    "type": "MATH",
                    "memory": random.randint(100, 1000)
                })
                
            for i in range(io_tasks):
                all_tasks.append({
                    "type": "INOUT",
                    "memory": random.randint(50, 500)
                })
                
            random.shuffle(all_tasks)
            
            for i, task in enumerate(all_tasks):
                task_num = task_counter + i
                tasks_list.append({
                    "num": task_num,
                    "type": task["type"],
                    "memory": task["memory"]
                })
                
                task_line = f"{task_num:<30} {task['type']:<30} {task['memory']:<30}"
                tasks_text.appendPlainText(task_line)
            
            task_counter += len(all_tasks)

        def addManualTask():
            nonlocal tasks_list, task_counter
            task_type = task_type_combo.currentText()
            memory = memory_spinbox.value()
            task_num = task_counter
            
            tasks_list.append({
                "num": task_num,
                "type": task_type,
                "memory": memory
            })
            
            task_line = f"{task_num:<30} {task_type:<30} {memory:<30}"
            tasks_text.appendPlainText(task_line)
            task_counter += 1

        def savePacket():
            if not tasks_list:
                QMessageBox.warning(dialog, "Ошибка", "Пакет не содержит задач!")
                return
            
            pack_name = pack_name_edit.text().strip()
            if not pack_name:
                QMessageBox.warning(dialog, "Ошибка", "Введите имя пакета!")
                return
            
            packet_data = {
                "tasks": tasks_list
            }
            
            filename = f"ready_packets/{pack_name}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(packet_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(dialog, "Успех", f"Пакет сохранен в файл: {filename}")
                dialog.close()
                
                self.packname.setText(f"{pack_name}.json")
                self.getPackInfo()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
                
        compute_button.clicked.connect(generateMathPacket)
        io_button.clicked.connect(generateIOPacket)
        balanced_button.clicked.connect(generateBalancedPacket)
        add_task_button.clicked.connect(addManualTask)
        save_button.clicked.connect(savePacket)
        
        dialog.exec()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()