import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from ControlPanel import ControlPanel
from WaveformWidget import WaveformWidget
from InverterSimulation import InverterSimulation
from GridSimulation import GridSimulationWindow
from Zeitbereichssimulation import TimeDomainSimulationWindow
from FrequenzbereichsUndKleinsignalanalyse import FrequencyDomainAnalysisWindow
import numpy as np
import csv
import os

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
        
        self.grid_window = None  # Initialize as None
        self.tds_window = None
        self.fsa_window = None
        
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
        self.control_panel.launch_tds.connect(self.launch_tds_window)
        self.control_panel.launch_fsa.connect(self.launch_fsa_window)
        self.control_panel.launch_grid.connect(self.launch_grid_window)  # Connect new signal
        self.control_panel.export_all_data.connect(self.export_all_data)
        
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
        if self.grid_window is not None:
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
        # Use default grid voltage if grid_window is not initialized
        grid_voltage = self.grid_window.generate_grid_voltage() if self.grid_window is not None else np.zeros(100)
        data = self.simulation.generate_waveforms(grid_voltage)
        self.waveform_widget.update_plot(data)
    
    def start_simulation(self):
        self.timer.start(100)
        if self.grid_window is not None:
            self.grid_window.timer.start(100)
    
    def pause_simulation(self):
        self.timer.stop()
        if self.grid_window is not None:
            self.grid_window.timer.stop()
    
    def reset_simulation(self):
        self.timer.stop()
        if self.grid_window is not None:
            self.grid_window.timer.stop()
        self.simulation.reset()
        if self.grid_window is not None:
            self.grid_window.reset()
        grid_voltage = self.grid_window.generate_grid_voltage() if self.grid_window is not None else np.zeros(100)
        data = self.simulation.generate_waveforms(grid_voltage)
        self.waveform_widget.update_plot(data)
    
    def launch_tds_window(self):
        if self.tds_window is None or not self.tds_window.isVisible():
            self.tds_window = TimeDomainSimulationWindow(self.simulation)
            self.tds_window.show()
    
    def launch_fsa_window(self):
        if self.fsa_window is None or not self.fsa_window.isVisible():
            self.fsa_window = FrequencyDomainAnalysisWindow(self.simulation)
            self.fsa_window.show()
    
    def launch_grid_window(self):
        if self.grid_window is None or not self.grid_window.isVisible():
            self.grid_window = GridSimulationWindow(self.simulation)
            self.grid_window.show()
    
    def export_all_data(self):
        # Collect data
        data = {}
        
        # Main simulation data
        grid_voltage = self.grid_window.generate_grid_voltage() if self.grid_window is not None else np.zeros(100)
        main_data = self.simulation.generate_waveforms(grid_voltage)
        num_phases = len(main_data['voltage'])
        data['main_simulation'] = {
            'time': main_data['time'],
            'voltages': main_data['voltage'],
            'currents': main_data['current']
        }
        
        # TDS data
        if self.tds_window is not None and self.tds_window.simulation_data['time'] is not None:
            data['tds'] = self.tds_window.simulation_data
        
        # FSA data
        if self.fsa_window is not None and self.fsa_window.analysis_data['freqs'] is not None:
            data['fsa'] = self.fsa_window.analysis_data
        
        # Parameters
        data['parameters'] = self.control_panel.get_params()
        data['parameters'].update({
            'phase_topology': self.control_panel.get_phase_topology(),
            'multilevel_topology': self.control_panel.get_multilevel_topology(),
            'pwm_technique': self.control_panel.get_pwm(),
            'design': self.control_panel.get_design(),
            'mppt': self.control_panel.get_mppt(),
            'control': self.control_panel.get_control(),
            'islanding_enabled': self.control_panel.is_islanding_enabled(),
            'dc_source': self.control_panel.get_dc_source()
        })
        
        # Open file dialog to choose directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Data", os.path.expanduser("~"))
        
        if not directory:
            return
        
        # Save main simulation data
        with open(os.path.join(directory, 'main_simulation.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Time (s)']
            for i in range(num_phases):
                header.append(f"Voltage Phase {i+1} (V)")
                header.append(f"Current Phase {i+1} (A)")
            writer.writerow(header)
            for j in range(len(data['main_simulation']['time'])):
                row = [data['main_simulation']['time'][j]]
                for i in range(num_phases):
                    row.append(data['main_simulation']['voltages'][i][j])
                    row.append(data['main_simulation']['currents'][i][j])
                writer.writerow(row)
        
        # Save TDS data
        if 'tds' in data:
            with open(os.path.join(directory, 'tds_data.csv'), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header = ['Time (s)']
                for i in range(len(data['tds']['voltages'])):
                    header.append(f"Voltage Phase {i+1} (V)")
                    header.append(f"Current Phase {i+1} (A)")
                writer.writerow(header)
                for j in range(len(data['tds']['time'])):
                    row = [data['tds']['time'][j]]
                    for i in range(len(data['tds']['voltages'])):
                        row.append(data['tds']['voltages'][i][j])
                        row.append(data['tds']['currents'][i][j])
                    writer.writerow(row)
        
        # Save FSA data
        if 'fsa' in data:
            with open(os.path.join(directory, 'fsa_data.csv'), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Frequency (Hz)', 'Gain (dB)', 'Phase (deg)'])
                for i in range(len(data['fsa']['freqs'])):
                    writer.writerow([
                        data['fsa']['freqs'][i],
                        data['fsa']['gain'][i],
                        data['fsa']['phase'][i]
                    ])
        
        # Save parameters
        with open(os.path.join(directory, 'parameters.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Parameter', 'Value'])
            for key, value in data['parameters'].items():
                writer.writerow([key, str(value)])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())