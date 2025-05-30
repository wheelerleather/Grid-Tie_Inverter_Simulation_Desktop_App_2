import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from ControlPanel import ControlPanel
from WaveformWidget import WaveformWidget
from InverterSimulation import InverterSimulation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid-Tie Inverter Simulator")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #C0C0C0;
            }
            QLabel {
                font-family: 'Consolas';
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        
        app_font = QFont('Consolas', 12)
        QApplication.instance().setFont(app_font)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)
        
        self.simulation = InverterSimulation()
        
        self.control_panel = ControlPanel()
        self.control_panel_frame = QFrame()
        self.control_panel_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.control_panel_frame.setLineWidth(3)
        self.control_panel_frame.setMinimumWidth(350)
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.addWidget(self.control_panel)
        self.control_panel_frame.setLayout(control_layout)
        
        self.waveform_widget = WaveformWidget()
        
        main_layout.addWidget(self.control_panel_frame, 1)
        main_layout.addWidget(self.waveform_widget, 3)
        
        self.control_panel.parameters_changed.connect(self.update_simulation)
        self.control_panel.topology_changed.connect(self.update_phase_topology)
        self.control_panel.multilevel_changed.connect(self.update_multilevel_topology)
        self.control_panel.pwm_changed.connect(self.update_pwm_technique)
        self.control_panel.start_simulation.connect(self.start_simulation)
        self.control_panel.pause_simulation.connect(self.pause_simulation)
        self.control_panel.reset_simulation.connect(self.reset_simulation)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveforms)
        
        self.update_simulation(self.control_panel.get_parameters())
        self.update_phase_topology(self.control_panel.get_phase_topology())
        self.update_multilevel_topology(self.control_panel.get_multilevel_topology())
        self.update_pwm_technique(self.control_panel.get_pwm_technique())
    
    def update_simulation(self, params):
        self.simulation.update_parameters(params)
    
    def update_phase_topology(self, topology):
        self.simulation.update_phase_topology(topology)
        self.waveform_widget.update_topology(topology)
    
    def update_multilevel_topology(self, topology):
        self.simulation.update_multilevel_topology(topology)
        self.waveform_widget.update_multilevel_topology(topology)
    
    def update_pwm_technique(self, pwm_technique):
        self.simulation.update_pwm_technique(pwm_technique)
        self.waveform_widget.update_pwm_technique(pwm_technique)
    
    def update_waveforms(self):
        data = self.simulation.generate_waveforms()
        self.waveform_widget.update_plot(data)
    
    def start_simulation(self):
        self.timer.start(100)
    
    def pause_simulation(self):
        self.timer.stop()
    
    def reset_simulation(self):
        self.timer.stop()
        self.simulation.reset()
        data = self.simulation.generate_waveforms()
        self.waveform_widget.update_plot(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())