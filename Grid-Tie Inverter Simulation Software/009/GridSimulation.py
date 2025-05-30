import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import numpy as np

class GridSimulationWindow(QMainWindow):
    def __init__(self, inverter_simulation):
        super().__init__()
        self.inverter_simulation = inverter_simulation
        self.frequency = 50
        self.time_window = 0.04
        self.time_step = 0.001
        self.samples = int(self.time_window / self.time_step)
        self.current_time = 0
        self.R = 0.1  # Resistance (Ohm)
        self.L = 0.001  # Inductance (H)
        self.fault_mode = "Normal"
        self.fault_timer = 0
        self.weak_grid = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Grid Simulation")
        self.setMinimumSize(800, 600)
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
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#000000')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.setTitle("Grid Voltage", color='#FFFFFF', size='14pt')
        self.plot_widget.setLabel('left', 'Voltage (V)', color='#FFFFFF', size='12pt')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='#FFFFFF', size='12pt')
        font = QFont('Consolas', 12)
        self.plot_widget.getAxis('bottom').setStyle(tickFont=font)
        self.plot_widget.getAxis('left').setStyle(tickFont=font)
        self.plot_widget.getAxis('bottom').setTextPen('#FFFFFF')
        self.plot_widget.getAxis('left').setTextPen('#FFFFFF')
        self.plot_widget.setXRange(0, self.time_window, padding=0)
        
        self.voltage_curve = self.plot_widget.plot(pen=pg.mkPen(color='blue', width=3), name='Grid Voltage')
        legend = self.plot_widget.addLegend()
        legend.setBrush('#C0C0C0')
        legend.setPen(pg.mkPen(color='#808080', width=2))
        
        control_group = QWidget()
        control_layout = QHBoxLayout()
        control_group.setLayout(control_layout)
        
        self.fault_label = QLabel("Fault Type:")
        self.fault_combo = QComboBox()
        self.fault_combo.addItems(["Normal", "Sag", "Swell", "Harmonics", "Freq Shift"])
        self.fault_combo.currentTextChanged.connect(self.set_fault)
        
        self.weak_grid_button = QPushButton("Toggle Weak Grid")
        self.weak_grid_button.clicked.connect(self.toggle_grid)
        
        control_layout.addWidget(self.fault_label)
        control_layout.addWidget(self.fault_combo)
        control_layout.addWidget(self.weak_grid_button)
        
        layout.addWidget(self.plot_widget)
        layout.addWidget(control_group)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_grid)
        self.timer.start(100)
    
    def update_simulation_parameters(self, params):
        self.frequency = params['frequency']
    
    def set_fault(self, fault_type):
        self.fault_mode = fault_type
        self.fault_timer = 0.1  # Fault duration: 100ms
    
    def toggle_grid(self):
        self.weak_grid = not self.weak_grid
        self.R = 1.0 if self.weak_grid else 0.1
        self.L = 0.01 if self.weak_grid else 0.001
    
    def generate_grid_voltage(self):
        t = np.linspace(self.current_time, self.current_time + self.time_window, self.samples)
        V_nom = 230 * np.sqrt(2)
        freq = self.frequency
        voltage = V_nom * np.sin(2 * np.pi * freq * t)
        
        if self.fault_timer > 0:
            if self.fault_mode == "Sag":
                voltage *= 0.8
            elif self.fault_mode == "Swell":
                voltage *= 1.2
            elif self.fault_mode == "Harmonics":
                voltage += 0.05 * V_nom * np.sin(2 * np.pi * 5 * freq * t) + 0.05 * V_nom * np.sin(2 * np.pi * 7 * freq * t)
            elif self.fault_mode == "Freq Shift":
                freq += 2
                voltage = V_nom * np.sin(2 * np.pi * freq * t)
            self.fault_timer -= self.time_step
        
        # Apply impedance
        I_load = 10  # Simplified load current
        V_drop = self.R * I_load + self.L * 2 * np.pi * freq * I_load
        voltage -= V_drop
        
        return voltage
    
    def update_grid(self):
        voltage = self.generate_grid_voltage()
        self.voltage_curve.setData(np.linspace(0, self.time_window, self.samples), voltage)
        self.inverter_simulation.grid_voltage = voltage
        self.current_time += self.time_window / 2
    
    def reset(self):
        self.current_time = 0
        self.fault_mode = "Normal"
        self.fault_timer = 0
        self.weak_grid = False
        self.R = 0.1
        self.L = 0.001
        self.fault_combo.setCurrentText("Normal")