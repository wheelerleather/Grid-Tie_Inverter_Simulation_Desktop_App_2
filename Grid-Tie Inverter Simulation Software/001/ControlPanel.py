from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSlider, QDoubleSpinBox, QLabel, QPushButton, QHBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

class ControlPanel(QWidget):
    parameters_changed = pyqtSignal(dict)
    start_simulation = pyqtSignal()
    pause_simulation = pyqtSignal()
    reset_simulation = pyqtSignal()
    topology_changed = pyqtSignal(str)
    multilevel_changed = pyqtSignal(str)
    pwm_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QGroupBox {
                font-family: 'Consolas';
                font-size: 12pt;
                font-weight: bold;
                border: 3px solid #808080;
                border-radius: 6px;
                margin-top: 15px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #C0C0C0;
            }
            QSlider, QDoubleSpinBox, QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #808080;
                padding: 5px;
                min-height: 30px;
                font-family: 'Consolas';
                font-size: 12pt;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #808080;
            }
            QSlider::handle:horizontal {
                background: #C0C0C0;
                border: 1px solid #000000;
                width: 20px;
                margin: -6px 0;
            }
            QPushButton {
                font-family: 'Segoe UI Emoji';
                font-size: 16pt;
                font-weight: bold;
                background-color: #C0C0C0;
                border: 2px solid #808080;
                padding: 8px;
                min-height: 40px;
                min-width: 60px;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
                border: 2px solid #000000;
            }
            QLabel {
                font-family: 'Consolas';
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        
        params_group = QGroupBox("Inverter Control Panel")
        params_layout = QVBoxLayout()
        params_layout.setSpacing(15)
        params_group.setLayout(params_layout)
        
        # Phase Topology
        self.phase_label = QLabel("Phase Topology:")
        self.phase_combo = QComboBox()
        self.phase_combo.addItems(["Single-Phase", "Three-Phase"])
        self.phase_combo.setCurrentText("Single-Phase")
        self.phase_combo.currentTextChanged.connect(self.emit_phase_topology)
        
        # Multilevel Topology
        self.multilevel_label = QLabel("Multilevel Topology:")
        self.multilevel_combo = QComboBox()
        self.multilevel_combo.addItems(["None", "NPC", "Flying Capacitor", "Cascaded H-Bridge", "MMC", "Reduced Switch Count", "Hybrid CHB+NPC"])
        self.multilevel_combo.setCurrentText("None")
        self.multilevel_combo.currentTextChanged.connect(self.emit_multilevel)
        
        # PWM Technique
        self.pwm_label = QLabel("PWM Technique:")
        self.pwm_combo = QComboBox()
        self.pwm_combo.addItems(["Multicarrier", "Space Vector"])
        self.pwm_combo.setCurrentText("Multicarrier")
        self.pwm_combo.currentTextChanged.connect(self.emit_pwm)
        
        # DC Voltage
        self.dc_voltage_label = QLabel("DC Input Voltage (V):")
        self.dc_voltage_spin = QDoubleSpinBox()
        self.dc_voltage_spin.setRange(100, 800)
        self.dc_voltage_spin.setValue(400)
        self.dc_voltage_spin.setSingleStep(10)
        self.dc_voltage_spin.setFixedHeight(40)
        
        # Grid Frequency
        self.frequency_label = QLabel("Grid Frequency (Hz):")
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(40, 70)
        self.frequency_spin.setValue(50)
        self.frequency_spin.setSingleStep(1)
        self.frequency_spin.setFixedHeight(40)
        
        # Modulation Index
        self.mod_index_label = QLabel("Modulation Index:")
        self.mod_index_slider = QSlider(Qt.Horizontal)
        self.mod_index_slider.setRange(0, 100)
        self.mod_index_slider.setValue(80)
        self.mod_index_slider.setFixedHeight(40)
        self.mod_index_value = QLabel("0.80")
        
        # Control Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.start_button = QPushButton("▶️")
        self.pause_button = QPushButton("⏸️")
        self.reset_button = QPushButton("🔄")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        
        self.start_button.clicked.connect(self.start_simulation.emit)
        self.pause_button.clicked.connect(self.pause_simulation.emit)
        self.reset_button.clicked.connect(self.reset_simulation.emit)
        
        self.dc_voltage_spin.valueChanged.connect(self.emit_parameters)
        self.frequency_spin.valueChanged.connect(self.emit_parameters)
        self.mod_index_slider.valueChanged.connect(self.update_mod_index)
        
        params_layout.addWidget(self.phase_label)
        params_layout.addWidget(self.phase_combo)
        params_layout.addWidget(self.multilevel_label)
        params_layout.addWidget(self.multilevel_combo)
        params_layout.addWidget(self.pwm_label)
        params_layout.addWidget(self.pwm_combo)
        params_layout.addWidget(self.dc_voltage_label)
        params_layout.addWidget(self.dc_voltage_spin)
        params_layout.addWidget(self.frequency_label)
        params_layout.addWidget(self.frequency_spin)
        params_layout.addWidget(self.mod_index_label)
        params_layout.addWidget(self.mod_index_slider)
        params_layout.addWidget(self.mod_index_value, alignment=Qt.AlignCenter)
        params_layout.addLayout(button_layout)
        
        layout.addWidget(params_group)
        layout.addStretch()
    
    def update_mod_index(self):
        value = self.mod_index_slider.value() / 100
        self.mod_index_value.setText(f"{value:.2f}")
        self.emit_parameters()
    
    def emit_parameters(self):
        params = {
            'dc_voltage': self.dc_voltage_spin.value(),
            'frequency': self.frequency_spin.value(),
            'mod_index': self.mod_index_slider.value() / 100
        }
        self.parameters_changed.emit(params)
    
    def emit_phase_topology(self):
        self.topology_changed.emit(self.phase_combo.currentText())
    
    def emit_multilevel(self):
        self.multilevel_changed.emit(self.multilevel_combo.currentText())
    
    def emit_pwm(self):
        self.pwm_changed.emit(self.pwm_combo.currentText())
    
    def get_parameters(self):
        return {
            'dc_voltage': self.dc_voltage_spin.value(),
            'frequency': self.frequency_spin.value(),
            'mod_index': self.mod_index_slider.value() / 100
        }
    
    def get_phase_topology(self):
        return self.phase_combo.currentText()
    
    def get_multilevel_topology(self):
        return self.multilevel_combo.currentText()
    
    def get_pwm_technique(self):
        return self.pwm_combo.currentText()