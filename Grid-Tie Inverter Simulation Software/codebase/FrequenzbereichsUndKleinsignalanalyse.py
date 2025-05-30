from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLabel, QPushButton, QComboBox, QApplication, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np
import csv
import os

class FrequencyDomainAnalysisWindow(QWidget):
    def __init__(self, inverter_simulation):
        super().__init__()
        self.inverter_simulation = inverter_simulation
        self.setWindowTitle("Frequency-Domain and Small-Signal Analysis")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.analysis_data = {'freqs': None, 'gain': None, 'phase': None}  # Initialize data storage
    
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
            QDoubleSpinBox, QPushButton, QComboBox {
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
        control_group = QGroupBox("Analysis Parameters")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        control_group.setLayout(control_layout)
        
        # Frequency Range
        self.freq_start_label = QLabel("Start Frequency (Hz):")
        self.freq_start_spin = QDoubleSpinBox()
        self.freq_start_spin.setRange(0.1, 1000.0)
        self.freq_start_spin.setValue(1.0)
        self.freq_start_spin.setSingleStep(0.1)
        self.freq_start_spin.setFixedHeight(40)
        
        self.freq_end_label = QLabel("End Frequency (Hz):")
        self.freq_end_spin = QDoubleSpinBox()
        self.freq_end_spin.setRange(10.0, 100000.0)
        self.freq_end_spin.setValue(10000.0)
        self.freq_end_spin.setSingleStep(100.0)
        self.freq_end_spin.setFixedHeight(40)
        
        # Analysis Type
        self.analysis_type_label = QLabel("Analysis Type:")
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Open-Loop", "Closed-Loop"])
        self.analysis_type_combo.setCurrentText("Open-Loop")
        
        # Perturbation Amplitude
        self.perturbation_label = QLabel("Perturbation Amplitude (%):")
        self.perturbation_spin = QDoubleSpinBox()
        self.perturbation_spin.setRange(0.1, 10.0)
        self.perturbation_spin.setValue(1.0)
        self.perturbation_spin.setSingleStep(0.1)
        self.perturbation_spin.setFixedHeight(40)
        
        # Run and Export Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self.run_analysis)
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.export_button)
        
        control_layout.addWidget(self.freq_start_label)
        control_layout.addWidget(self.freq_start_spin)
        control_layout.addWidget(self.freq_end_label)
        control_layout.addWidget(self.freq_end_spin)
        control_layout.addWidget(self.analysis_type_label)
        control_layout.addWidget(self.analysis_type_combo)
        control_layout.addWidget(self.perturbation_label)
        control_layout.addWidget(self.perturbation_spin)
        control_layout.addLayout(button_layout)
        control_layout.addStretch()
        
        # Plot Group
        plot_group = QGroupBox("Bode Plot")
        plot_layout = QVBoxLayout()
        plot_group.setLayout(plot_layout)
        
        # Gain Plot
        self.gain_plot = pg.PlotWidget()
        self.gain_plot.setBackground('k')
        self.gain_plot.showGrid(x=True, y=True, alpha=1.0)
        self.gain_plot.setLabel('left', 'Gain (dB)', color='white')
        self.gain_plot.setLabel('bottom', 'Frequency (Hz)', color='white')
        self.gain_plot.getAxis('left').setPen('w')
        self.gain_plot.getAxis('bottom').setPen('w')
        self.gain_plot.getAxis('left').setTextPen('w')
        self.gain_plot.getAxis('bottom').setTextPen('w')
        self.gain_plot.setLogMode(x=True)
        
        # Phase Plot
        self.phase_plot = pg.PlotWidget()
        self.phase_plot.setBackground('k')
        self.phase_plot.showGrid(x=True, y=True, alpha=1.0)
        self.phase_plot.setLabel('left', 'Phase (deg)', color='white')
        self.phase_plot.setLabel('bottom', 'Frequency (Hz)', color='white')
        self.phase_plot.getAxis('left').setPen('w')
        self.phase_plot.getAxis('bottom').setPen('w')
        self.phase_plot.getAxis('left').setTextPen('w')
        self.phase_plot.getAxis('bottom').setTextPen('w')
        self.phase_plot.setLogMode(x=True)
        
        plot_layout.addWidget(self.gain_plot)
        plot_layout.addWidget(self.phase_plot)
        
        layout.addWidget(control_group)
        layout.addWidget(plot_group)
    
    def run_analysis(self):
        # Get parameters
        f_start = self.freq_start_spin.value()
        f_end = self.freq_end_spin.value()
        analysis_type = self.analysis_type_combo.currentText()
        perturbation = self.perturbation_spin.value() / 100
        
        # Generate frequency points (logarithmic scale)
        freqs = np.logspace(np.log10(f_start), np.log10(f_end), 100)
        
        # Simplified small-signal model (PI controller + LC filter)
        Kp = 0.1  # Proportional gain (from control parameters)
        Ki = 10.0  # Integral gain
        L = 1e-3  # Filter inductance (H)
        C = 100e-6  # Filter capacitance (F)
        
        # Transfer function: G(s) = (Kp + Ki/s) * 1/(LCs^2 + Ls/R + 1)
        gain = []
        phase = []
        for f in freqs:
            s = 2j * np.pi * f
            # PI controller
            G_pi = Kp + Ki / s
            # LC filter (approximate R small)
            G_filter = 1 / (L * C * s**2 + 1)
            # Open-loop or closed-loop
            if analysis_type == "Open-Loop":
                G = G_pi * G_filter
            else:  # Closed-Loop
                G = (G_pi * G_filter) / (1 + G_pi * G_filter)
            
            # Apply perturbation
            G *= (1 + perturbation)
            
            # Compute gain (dB) and phase (degrees)
            gain.append(20 * np.log10(np.abs(G)))
            phase.append(np.angle(G, deg=True))
        
        # Store data for export
        self.analysis_data = {
            'freqs': freqs,
            'gain': np.array(gain),
            'phase': np.array(phase)
        }
        
        # Update plots
        self.gain_plot.clear()
        self.gain_plot.plot(freqs, gain, pen=pg.mkPen('b', width=2), name="Gain")
        
        self.phase_plot.clear()
        self.phase_plot.plot(freqs, phase, pen=pg.mkPen('r', width=2), name="Phase")
        
        # Force plot update
        QApplication.processEvents()
    
    def export_data(self):
        if self.analysis_data['freqs'] is None:
            return
        
        # Open file dialog to choose save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Data",
            os.path.expanduser("~"),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filename:
            return  # User canceled the dialog
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # Save to CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Frequency (Hz)', 'Gain (dB)', 'Phase (deg)'])
            for i in range(len(self.analysis_data['freqs'])):
                writer.writerow([
                    self.analysis_data['freqs'][i],
                    self.analysis_data['gain'][i],
                    self.analysis_data['phase'][i]
                ])