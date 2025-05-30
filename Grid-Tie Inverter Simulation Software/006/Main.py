import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from ControlPanel import ControlPanel
from WaveformWidget import WaveformWidget
from InverterSimulation import InverterSimulation
from GridSimulation import GridSimulationWindow

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
        QApplication.setFont(app_font)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QHBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(5, 5, 5, 5)
        main_widget.setLayout(self.layout)
        
        self.simulation = InverterSimulation()
        
        self.control_panel = ControlPanel()
        self.control_panel_frame = QFrame()
        self.control_panel_frame.setStyleSheet(self.getFrameStyleSheet())
        self.control_panel_frame.setMinimumWidth(350)
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(0, 10, 10, 10)
        control_layout.addWidget(self.control_panel)
        self.control_panel_frame.setLayout(control_layout)
        
        self.waveform_widget = WaveformWidget()
        
        self.layout.addWidget(self.control_panel_frame, 1)
        self.layout.addWidget(self.waveform_widget, 3)
        
        self.grid_window = GridSimulationWindow(self.simulation)
        self.grid_window.show()
        
        self.control_panel.parameters_changed.connect(self.update_simulation)
        self.control_panel.topology_changed.connect(self.update_phase_topology)
        self.control_panel.multilevel_changed.connect(self.update_multilevel_topology)
        self.control_panel.pwm_changed.connect(self.update_pwm_technique)
        self.control_panel.design_changed.connect(self.update_design)
        self.control_panel.mppt_changed.connect(self.update_mppt)
        self.control_panel.control_changed.connect(self.update_control)
        self.control_panel.islanding_changed.connect(self.update_islanding)
        self.control_panel.dc_source_changed.connect(self.update_dc_source)
        self.control_panel.start_simulation.connect(self.start_simulation)
        self.control_panel.pause_simulation.connect(self.pause_simulation)
        self.control_panel.reset_simulation.connect(self.reset_simulation)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveforms)
        
        self.update_params()
    
    def getFrameStyleSheet(self):
        return """
            border: 3px inset #808080;
            border-radius: 6px;
            background-color: #C0C0C0;
        """

    def update_params(self):
        self.update_simulation(self.control_panel.get_params())
        self.update_phase_topology(self.control_panel.get_phase_topology())
        self.update_multilevel_topology(self.control_panel.get_multilevel_topology())
        self.update_pwm_technique(self.control_panel.get_pwm())
        self.update_design(self.control_panel.get_design())
        self.update_mppt(self.control_panel.get_mppt())
        self.update_control(self.control_panel.get_control())
        self.update_islanding(self.control_panel.is_islanding_enabled())
        self.update_dc_source(self.control_panel.get_dc_source())
    
    def update_simulation(self, params):
        self.simulation.update_simulation_parameters(params)
        self.simulation.mppt_state.update({
            'irradiance': params['irradiance'],
            'temperature': params['temperature'],
            'SOC': params['SOC'],
            'load_current': params['load_current']
        })
        self.grid_window.update_simulation_parameters(params)
    
    def update_phase_topology(self, topology):
        self.simulation.update_phase_topology(topology)
        self.waveform_widget.set_phase_topology(topology)
    
    def update_multilevel_topology(self, topology):
        self.simulation.update_multilevel_topology(topology)
        self.waveform_widget.set_multilevel_topology(topology)
    
    def update_pwm_technique(self, pwm_technique):
        self.simulation.update_pwm_technique(pwm_technique)
        self.waveform_widget.set_pwm_technique(pwm_technique)
    
    def update_design(self, design):
        self.simulation.update_design(design)
        self.waveform_widget.set_design(design)
    
    def update_mppt(self, mppt):
        self.simulation.update_mppt(mppt)
        self.waveform_widget.set_mppt(mppt)
    
    def update_control(self, control):
        self.simulation.update_control(control)
        self.waveform_widget.set_control(control)
    
    def update_islanding(self, enabled):
        self.simulation.update_islanding_detection(enabled)
        self.waveform_widget.set_islanding_enabled(enabled)
    
    def update_dc_source(self, source_type):
        self.simulation.update_dc_source(source_type)
    
    def update_waveforms(self):
        data = self.simulation.generate_waveforms(self.grid_window.generate_grid_voltage())
        self.waveform_widget.update_plot(data)
    
    def start_simulation(self):
        self.timer.start(100)
        self.grid_window.timer.start(100)
    
    def pause_simulation(self):
        self.timer.stop()
        self.grid_window.timer.stop()
    
    def reset_simulation(self):
        self.timer.stop()
        self.grid_window.timer.stop()
        self.simulation.reset()
        self.grid_window.reset()
        data = self.simulation.generate_waveforms(self.grid_window.generate_grid_voltage())
        self.waveform_widget.update_plot(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())