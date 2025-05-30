from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLabel, QPushButton, QComboBox, QCheckBox, QProgressBar, QApplication, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np
import csv
import os

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
            QDoubleSpinBox, QPushButton, QComboBox, QCheckBox, QProgressBar {
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
        
        # Preset Configurations
        self.preset_label = QLabel("Preset Configuration:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Custom", "Fast", "Detailed", "Long-Run"])
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        
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
        
        self.adaptive_check = QCheckBox("Enable Adaptive Time Stepping")
        self.adaptive_check.setChecked(False)
        
        # Simulation Duration
        self.duration_label = QLabel("Simulation Duration (s):")
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 10.0)
        self.duration_spin.setValue(1.0)
        self.duration_spin.setSingleStep(0.1)
        self.duration_spin.setFixedHeight(40)
        
        # Plot Options
        self.plot_options_label = QLabel("Plot Options:")
        self.voltage_check = QCheckBox("Show Voltage")
        self.voltage_check.setChecked(True)
        self.current_check = QCheckBox("Show Current")
        self.current_check.setChecked(True)
        self.phase_combo = QComboBox()
        self.phase_combo.addItems(["All Phases", "Phase 1", "Phase 2", "Phase 3"])
        self.phase_combo.setCurrentText("All Phases")
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # Run and Export Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.export_button)
        
        control_layout.addWidget(self.preset_label)
        control_layout.addWidget(self.preset_combo)
        control_layout.addWidget(self.time_step_label)
        control_layout.addWidget(self.time_step_spin)
        control_layout.addWidget(self.variation_label)
        control_layout.addWidget(self.variation_spin)
        control_layout.addWidget(self.adaptive_check)
        control_layout.addWidget(self.duration_label)
        control_layout.addWidget(self.duration_spin)
        control_layout.addWidget(self.plot_options_label)
        control_layout.addWidget(self.voltage_check)
        control_layout.addWidget(self.current_check)
        control_layout.addWidget(self.phase_combo)
        control_layout.addWidget(self.progress_bar)
        control_layout.addLayout(button_layout)
        control_layout.addStretch()
        
        # Plot Group
        plot_group = QGroupBox("Waveforms")
        plot_layout = QVBoxLayout()
        plot_group.setLayout(plot_layout)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')  # Black background
        self.plot_widget.showGrid(x=True, y=True, alpha=1.0)  # White grid
        self.plot_widget.setLabel('left', 'Amplitude (V/A)', color='white')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='white')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')
        self.plot_widget.getAxis('left').setTextPen('w')
        self.plot_widget.getAxis('bottom').setTextPen('w')
        self.plot_widget.addLegend(brush='k', pen='w', labelTextColor='w')
        
        plot_layout.addWidget(self.plot_widget)
        
        layout.addWidget(control_group)
        layout.addWidget(plot_group)
        
        # Initialize data storage
        self.simulation_data = {'time': None, 'voltages': None, 'currents': None}
    
    def apply_preset(self, preset):
        if preset == "Fast":
            self.time_step_spin.setValue(2.0)
            self.variation_spin.setValue(0.1)
            self.duration_spin.setValue(0.5)
            self.adaptive_check.setChecked(False)
        elif preset == "Detailed":
            self.time_step_spin.setValue(0.1)
            self.variation_spin.setValue(0.3)
            self.duration_spin.setValue(1.0)
            self.adaptive_check.setChecked(True)
        elif preset == "Long-Run":
            self.time_step_spin.setValue(1.0)
            self.variation_spin.setValue(0.2)
            self.duration_spin.setValue(5.0)
            self.adaptive_check.setChecked(False)
        # Custom preset does nothing, allowing manual settings
    
    def run_simulation(self):
        # Get parameters
        base_time_step = self.time_step_spin.value() / 1000  # Convert to seconds
        variation_factor = self.variation_spin.value()
        duration = self.duration_spin.value()
        adaptive = self.adaptive_check.isChecked()
        
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
        prev_voltage = [0] * num_phases
        for i, dt in enumerate(time_steps):
            # Adaptive time step adjustment
            if adaptive:
                max_gradient = 0
                for j in range(num_phases):
                    if len(voltages[j]) > 0:
                        gradient = abs(voltages[j][-1] - prev_voltage[j]) / dt
                        max_gradient = max(max_gradient, gradient)
                if max_gradient > 1000:  # High gradient, reduce time step
                    dt *= 0.5
                elif max_gradient < 100:  # Low gradient, increase time step
                    dt *= 1.5
                dt = np.clip(dt, base_time_step * 0.1, base_time_step * 2.0)
            
            # Temporarily override time step in inverter simulation
            original_time_step = self.inverter_simulation.time_step
            self.inverter_simulation.time_step = dt
            self.inverter_simulation.time_window = dt * 10
            self.inverter_simulation.current_time = current_time
            
            # Generate waveforms
            data = self.inverter_simulation.generate_waveforms()
            
            # Restore original time step
            self.inverter_simulation.time_step = original_time_step
            self.inverter_simulation.time_window = original_time_step * 40
            
            # Store single point
            for j in range(num_phases):
                voltages[j].append(data['voltage'][j][0])
                currents[j].append(data['current'][j][0])
                prev_voltage[j] = data['voltage'][j][0]
            
            current_time += dt
            
            # Update progress bar
            self.progress_bar.setValue(int((i + 1) / num_steps * 100))
            QApplication.processEvents()
        
        # Convert to numpy arrays
        voltages = [np.array(v) for v in voltages]
        currents = [np.array(c) for c in currents]
        
        # Store data for export
        self.simulation_data = {'time': time, 'voltages': voltages, 'currents': currents}
        
        # Update plot
        self.plot_widget.clear()
        phase_selection = self.phase_combo.currentText()
        for i in range(len(voltages)):
            if phase_selection == "All Phases" or phase_selection == f"Phase {i+1}":
                phase_label = f"Phase {i+1}" if len(voltages) > 1 else "Single Phase"
                if self.voltage_check.isChecked():
                    self.plot_widget.plot(time, voltages[i], pen=pg.mkPen('b', width=2), name=f"{phase_label} Voltage")
                if self.current_check.isChecked():
                    self.plot_widget.plot(time, currents[i], pen=pg.mkPen('r', width=2), name=f"{phase_label} Current")
        
        self.progress_bar.setValue(0)
    
    def export_data(self):
        if self.simulation_data['time'] is None:
            return
        
        # Open file dialog to choose save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Simulation Data",
            os.path.expanduser("~"),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return  # User canceled the dialog
        
        # Ensure .csv extension if not provided
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Save to CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Time (s)']
            for i in range(len(self.simulation_data['voltages'])):
                header.append(f"Voltage Phase {i+1} (V)")
                header.append(f"Current Phase {i+1} (A)")
            writer.writerow(header)
            
            for j in range(len(self.simulation_data['time'])):
                row = [self.simulation_data['time'][j]]
                for i in range(len(self.simulation_data['voltages'])):
                    row.append(self.simulation_data['voltages'][i][j])
                    row.append(self.simulation_data['currents'][i][j])
                writer.writerow(row)