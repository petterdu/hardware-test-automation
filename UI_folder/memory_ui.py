import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QProgressBar
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QThread
from functions.memory_test_function import MemoryTestWorker

class MemoryTestUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        # loading.gif   
        base_path = os.path.dirname(os.path.abspath(__file__))  #    
        gif_path = os.path.join(base_path, "loading.gif")

        # QMovie      
        self.loading_movie = QMovie(gif_path)
        self.loading_label = QLabel(self)  #    
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(30, 30)  #   (   )
        self.loading_label.setScaledContents(True)  # GIF     
        self.loading_label.hide()  #   

        #     
        horizontal_layout = QHBoxLayout()

        #    
        self.add_memory_test_title_label(horizontal_layout, "  ")

        #      
        button_layout = QVBoxLayout()
        self.add_memory_test_button(button_layout, "Memtester ", "Memtester ", self.start_memtester_test, test_type="memtester")
        self.add_memory_test_button(button_layout, "Stress-ng ", "Stress-ng ", self.start_stress_test, test_type="stress")

        #     
        horizontal_layout.addLayout(button_layout)
        self.layout.addLayout(horizontal_layout)

    def get_layout(self):
        return self.layout

    def add_memory_test_title_label(self, layout, label_text):
        #     
        title_label = QLabel("메모리 불량 테스트")
        title_label.setStyleSheet("""
            background-color: #d3d3d3;  /*   */
            border: 2px solid #000000;  /*   */
            padding: 10px;              /*   */
            border-radius: 5px;         /*    */
            font-weight: bold;          /*    */
            font-size: 14px;            /*    */
        """)
        title_label.setFixedHeight(100)  #   
        title_label.setFixedWidth(150)  #   
        layout.addWidget(title_label)

    def add_memory_test_button(self, layout, button_text, label_text, callback=None, test_type=None):
        horizontal_layout = QHBoxLayout()

        button = QPushButton(button_text)
        button.setEnabled(False)
        button.setFixedHeight(40)
        if callback:
            button.clicked.connect(lambda: callback(test_type))
        horizontal_layout.addWidget(button)

        if test_type == "memtester":
            self.memtester_button = button
        elif test_type == "stress":
            self.stress_button = button  # 이 부분을 추가하여 stress 버튼을 저장합니다.

        #    Memtester   
        if test_type == "memtester":
            horizontal_layout.addWidget(self.loading_label)

        if test_type == "stress":
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_bar.setFixedWidth(150)
            horizontal_layout.addWidget(progress_bar)
            self.stress_progress_bar = progress_bar

        result_label = QLabel(label_text)
        horizontal_layout.addWidget(result_label)

        if test_type == "memtester":
            self.memtester_result_label = result_label
        elif test_type == "stress":
            self.stress_result_label = result_label

        layout.addLayout(horizontal_layout)

    def start_memtester_test(self, test_type):
        # Memtester  
        self.start_memory_test(test_type)

    def start_stress_test(self, test_type):
        # Stress-ng  
        self.start_memory_test(test_type)

    def start_memory_test(self, test_type):
        #       
        if hasattr(self, 'start_memory_test_callback'):
            self.start_memory_test_callback(False)

        #    (Memtester )
        if test_type == "memtester":
            print("Memtester 테스트 시작")  # 디버깅 메시지 추가
            self.loading_label.show()
            self.loading_movie.start()

        # QThread  Worker 
        self.thread = QThread()
        self.worker = MemoryTestWorker(test_type=test_type)

        # Worker  
        self.worker.moveToThread(self.thread)

        #  
        self.thread.started.connect(self.worker.run_memory_test)
        self.worker.progress_signal.connect(lambda progress: self.update_memory_progress(progress, test_type))
        self.worker.result_signal.connect(lambda result: self.update_memory_result(result, test_type))
        self.worker.result_signal.connect(lambda: self.set_test_buttons_enabled(True))
        self.worker.result_signal.connect(lambda: self.start_memory_test_callback(True))  #   
        self.worker.result_signal.connect(lambda: self.loading_movie.stop() if test_type == "memtester" else None)  #   
        self.worker.result_signal.connect(lambda: self.loading_label.hide() if test_type == "memtester" else None)  #    
        self.worker.result_signal.connect(self.thread.quit)

        #  
        self.thread.start()
        print("메모리 테스트 스레드 시작")  # 디버깅 메시지 추가

    def update_memory_progress(self, progress, test_type):
        if test_type == "stress" and hasattr(self, 'stress_progress_bar'):
            self.stress_progress_bar.setValue(progress)
            print(f"Stress-ng 진행률: {progress}%")  # 디버깅 메시지 추가

    def update_memory_result(self, result, test_type):
        if test_type == "memtester" and hasattr(self, 'memtester_result_label'):
            if result == "success":
                print("Memtester 테스트 성공")  # 디버깅 메시지 추가
                self.memtester_result_label.setText("Memtester 테스트 성공!")
                self.memtester_result_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                print("Memtester 테스트 실패")  # 디버깅 메시지 추가
                self.memtester_result_label.setText("Memtester 테스트 실패")
                self.memtester_result_label.setStyleSheet("color: red; font-weight: bold;")
        elif test_type == "stress" and hasattr(self, 'stress_result_label'):
            if result == "success":
                print("Stress-ng 테스트 성공")  # 디버깅 메시지 추가
                self.stress_result_label.setText("Stress-ng 테스트 성공!")
                self.stress_result_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                print("Stress-ng 테스트 실패")  # 디버깅 메시지 추가
                self.stress_result_label.setText(" ")
                self.stress_result_label.setStyleSheet("color: red; font-weight: bold;")

    def set_test_buttons_enabled(self, enabled):
        print(f"버튼 활성화 상태 변경: {enabled}")  # 디버깅 메시지 추가
        if hasattr(self, 'memtester_button'):
            self.memtester_button.setEnabled(enabled)
        if hasattr(self, 'stress_button'):
            self.stress_button.setEnabled(enabled)

