from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np

class TimeDomainSimulationWindow(QWidget):
    def __init__(self, inverter_simulation):
        super().__init__()
        self.inverter_simulation = inverter_simulation
        self.setWindowTitle("Time-Domain Simulation")
        self.setMinimumSize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #C0C0C0;
                font-family: 'Consolas';
                font-size: 12pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 3px inset #808080;
                border-radius: 6px;
                margin-top: 15px;
                padding: 10px;
                background-color: #C0C0C0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
            }
            QDoubleSpinBox, QPushButton {
                background-color: #FFFFFF;
                border: 2px inset #808080;
                padding: 5px;
                min-height: 30px;
                font-family: 'Consolas';
                font-size: 12pt;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
                border: 2px inset #808080;
            }
            QLabel {
                font-weight: bold;
            }
        """)
        
        # Control Group
        control_group = QGroupBox("Simulation Parameters")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        control_group.setLayout(control_layout)
        
        # Time Step Settings
        self.time_step_label = QLabel("Base Time Step (ms):")
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.01, 10.0)
        self.time_step_spin.setValue(1.0)
        self.time_step_spin.setSingleStep(0.1)
        self.time_step_spin.setFixedHeight(40)
        
        self.variation_label = QLabel("Time Step Variation Factor (0-1):")
        self.variation_spin = QDoubleSpinBox()
        self.variation_spin.setRange(0.0, 1.0)
        self.variation_spin.setValue(0.2)
        self.variation_spin.setSingleStep(0.01)
        self.variation_spin.setFixedHeight(40)
        
        # Simulation Duration
        self.duration_label = QLabel("Simulation Duration (s):")
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 10.0)
        self.duration_spin.setValue(1.0)
        self.duration_spin.setSingleStep(0.1)
        self.duration_spin.setFixedHeight(40)
        
        # Run Button
        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        
        control_layout.addWidget(self.time_step_label)
        control_layout.addWidget(self.time_step_spin)
        control_layout.addWidget(self.variation_label)
        control_layout.addWidget(self.variation_spin)
        control_layout.addWidget(self.duration_label)
        control_layout.addWidget(self.duration_spin)
        control_layout.addWidget(self.run_button)
        control_layout.addStretch()
        
        # Plot Group
        plot_group = QGroupBox("Waveforms")
        plot_layout = QVBoxLayout()
        plot_group.setLayout(plot_layout)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#C0C0C0')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Amplitude (V/A)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.addLegend()
        
        plot_layout.addWidget(self.plot_widget)
        
        layout.addWidget(control_group)
        layout.addWidget(plot_group)
    
    def run_simulation(self):
        # Get parameters
        base_time_step = self.time_step_spin.value() / 1000  # Convert to seconds
        variation_factor = self.variation_spin.value()
        duration = self.duration_spin.value()
        
        # Generate variable time steps
        num_steps = int(duration / base_time_step)
        time_steps = base_time_step * (1 + variation_factor * np.sin(np.linspace(0, 2 * np.pi, num_steps)))
        
        # Precompute time array
        time = np.cumsum(np.concatenate(([0], time_steps[:-1])))
        
        # Initialize data arrays
        num_phases = 3 if isinstance(self.inverter_simulation.phase_topology, self.inverter_simulation.phase_topology.__class__.__bases__[0].__subclasses__()[1]) else 1
        voltages = [[] for _ in range(num_phases)]
        currents = [[] for _ in range(num_phases)]
        
        # Run simulation
        current_time = 0
        for dt in time_steps:
            # Temporarily override time step in inverter simulation
            original_time_step = self.inverter_simulation.time_step
            self.inverter_simulation.time_step = dt
            self.inverter_simulation.time_window = dt * 10  # Smaller window for single point
            self.inverter_simulation.current_time = current_time
            
            # Generate waveforms
            data = self.inverter_simulation.generate_waveforms()
            
            # Restore original time step
            self.inverter_simulation.time_step = original_time_step
            self.inverter_simulation.time_window = original_time_step * 40
            
            # Store single point (e.g., first point of each phase)
            for i in range(num_phases):
                voltages[i].append(data['voltage'][i][0])
                currents[i].append(data['current'][i][0])
            
            current_time += dt
        
        # Convert to numpy arrays for plotting
        voltages = [np.array(v) for v in voltages]
        currents = [np.array(c) for c in currents]
        
        # Update plot
        self.plot_widget.clear()
        for i in range(len(voltages)):
            phase_label = f"Phase {i+1}" if len(voltages) > 1 else "Single Phase"
            self.plot_widget.plot(time, voltages[i], pen=pg.mkPen('b', width=2), name=f"{phase_label} Voltage")
            self.plot_widget.plot(time, currents[i], pen=pg.mkPen('r', width=2), name=f"{phase_label} Current")