from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSlider, QDoubleSpinBox, QLabel, QPushButton, QHBoxLayout, QComboBox, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
import uuid

class ControlPanel(QWidget):
    parameters_changed = pyqtSignal(dict)
    start_simulation = pyqtSignal()
    pause_simulation = pyqtSignal()
    reset_simulation = pyqtSignal()
    topology_changed = pyqtSignal(str)
    multilevel_changed = pyqtSignal(str)
    pwm_changed = pyqtSignal(str)
    design_changed = pyqtSignal(str)
    mppt_changed = pyqtSignal(str)
    control_changed = pyqtSignal(str)
    islanding_changed = pyqtSignal(bool)
    dc_source_changed = pyqtSignal(str)
    launch_tds = pyqtSignal()  # New signal for TDS window
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        self.setStyleSheet(self.getStyleSheet())
        
        params_group = QGroupBox("Inverter Control Panel")
        params_layout = QVBoxLayout()
        params_layout.setSpacing(15)
        params_group.setLayout(params_layout)
        
        # DC Source Selection
        self.dc_source_label = QLabel("DC Source:")
        self.dc_source_combo = QComboBox()
        self.dc_source_combo.addItems(["Fixed", "PV Panel", "Battery", "Fuel Cell", "Hybrid"])
        self.dc_source_combo.setCurrentText("Fixed")
        self.dc_source_combo.currentTextChanged.connect(self.emit_dc_source)
        
        # PV Parameters
        self.irradiance_label = QLabel("Irradiance (W/m²):")
        self.irradiance_spin = QDoubleSpinBox()
        self.irradiance_spin.setRange(100, 1500)
        self.irradiance_spin.setValue(1000)
        self.irradiance_spin.setSingleStep(10)
        self.irradiance_spin.setFixedHeight(40)
        
        self.temperature_label = QLabel("Temperature (°C):")
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(-20, 80)
        self.temperature_spin.setValue(25)
        self.temperature_spin.setSingleStep(1)
        self.temperature_spin.setFixedHeight(40)
        
        # Battery Parameter
        self.soc_label = QLabel("Battery SOC (0-1):")
        self.soc_spin = QDoubleSpinBox()
        self.soc_spin.setRange(0.1, 1.0)
        self.soc_spin.setValue(0.8)
        self.soc_spin.setSingleStep(0.01)
        self.soc_spin.setFixedHeight(40)
        
        # Fuel Cell Parameter
        self.load_current_label = QLabel("Fuel Cell Load Current (A):")
        self.load_current_spin = QDoubleSpinBox()
        self.load_current_spin.setRange(0, 20)
        self.load_current_spin.setValue(10)
        self.load_current_spin.setSingleStep(0.1)
        self.load_current_spin.setFixedHeight(40)
        
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
        
        # Design
        self.design_label = QLabel("Design:")
        self.design_combo = QComboBox()
        self.design_combo.addItems(["Transformerless", "Transformer-Based"])
        self.design_combo.setCurrentText("Transformerless")
        self.design_combo.currentTextChanged.connect(self.emit_design)
        
        # MPPT Algorithm
        self.mppt_label = QLabel("MPPT Algorithm:")
        self.mppt_combo = QComboBox()
        self.mppt_combo.addItems(["None", "Perturb & Observe", "Incremental Conductance", "Constant Voltage", "Constant Current", "Ripple Correlation Control"])
        self.mppt_combo.setCurrentText("None")
        self.mppt_combo.currentTextChanged.connect(self.emit_mppt)
        
        # Control Method
        self.control_label = QLabel("Control Method:")
        self.control_combo = QComboBox()
        self.control_combo.addItems(["PI", "PR", "Sliding Mode", "MPC"])
        self.control_combo.setCurrentText("PI")
        self.control_combo.currentTextChanged.connect(self.emit_control)
        
        # Islanding Detection
        self.islanding_label = QLabel("Islanding Detection:")
        self.islanding_check = QCheckBox("Enable")
        self.islanding_check.setChecked(True)
        self.islanding_check.stateChanged.connect(self.emit_islanding)
        
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
        self.tds_button = QPushButton("TDS")  # New TDS button
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.tds_button)
        
        self.start_button.clicked.connect(self.start_simulation.emit)
        self.pause_button.clicked.connect(self.pause_simulation.emit)
        self.reset_button.clicked.connect(self.reset_simulation.emit)
        self.tds_button.clicked.connect(self.launch_tds.emit)
        
        self.dc_voltage_spin.valueChanged.connect(self.emit_parameters)
        self.frequency_spin.valueChanged.connect(self.emit_parameters)
        self.mod_index_slider.valueChanged.connect(self.update_mod_index)
        self.irradiance_spin.valueChanged.connect(self.emit_parameters)
        self.temperature_spin.valueChanged.connect(self.emit_parameters)
        self.soc_spin.valueChanged.connect(self.emit_parameters)
        self.load_current_spin.valueChanged.connect(self.emit_parameters)
        
        params_layout.addWidget(self.dc_source_label)
        params_layout.addWidget(self.dc_source_combo)
        params_layout.addWidget(self.irradiance_label)
        params_layout.addWidget(self.irradiance_spin)
        params_layout.addWidget(self.temperature_label)
        params_layout.addWidget(self.temperature_spin)
        params_layout.addWidget(self.soc_label)
        params_layout.addWidget(self.soc_spin)
        params_layout.addWidget(self.load_current_label)
        params_layout.addWidget(self.load_current_spin)
        params_layout.addWidget(self.phase_label)
        params_layout.addWidget(self.phase_combo)
        params_layout.addWidget(self.multilevel_label)
        params_layout.addWidget(self.multilevel_combo)
        params_layout.addWidget(self.pwm_label)
        params_layout.addWidget(self.pwm_combo)
        params_layout.addWidget(self.design_label)
        params_layout.addWidget(self.design_combo)
        params_layout.addWidget(self.mppt_label)
        params_layout.addWidget(self.mppt_combo)
        params_layout.addWidget(self.control_label)
        params_layout.addWidget(self.control_combo)
        params_layout.addWidget(self.islanding_label)
        params_layout.addWidget(self.islanding_check)
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
    
    def getStyleSheet(self):
        return """
            QGroupBox {
                font-family: 'Consolas';
                font-size: 12pt;
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
                background-color: #C0C0C0;
            }
            QSlider, QDoubleSpinBox, QComboBox, QCheckBox {
                background-color: #FFFFFF;
                border: 2px inset #808080;
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
                border: 2px outset #808080;
                padding: 8px;
                min-height: 40px;
                min-width: 60px;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
                border: 2px inset #808080;
            }
            QLabel {
                font-family: 'Consolas';
                font-size: 12pt;
                font-weight: bold;
            }
        """

    def update_mod_index(self):
        value = self.mod_index_slider.value() / 100
        self.mod_index_value.setText(f"{value:.2f}")
        self.emit_parameters()
    
    def emit_parameters(self):
        params = {
            'dc_voltage': self.dc_voltage_spin.value(),
            'frequency': self.frequency_spin.value(),
            'mod_index': self.mod_index_slider.value() / 100,
            'irradiance': self.irradiance_spin.value(),
            'temperature': self.temperature_spin.value(),
            'SOC': self.soc_spin.value(),
            'load_current': self.load_current_spin.value()
        }
        self.parameters_changed.emit(params)
    
    def emit_phase_topology(self):
        self.topology_changed.emit(self.phase_combo.currentText())
    
    def emit_multilevel(self):
        self.multilevel_changed.emit(self.multilevel_combo.currentText())
    
    def emit_pwm(self):
        self.pwm_changed.emit(self.pwm_combo.currentText())
    
    def emit_design(self):
        self.design_changed.emit(self.design_combo.currentText())
    
    def emit_mppt(self):
        self.mppt_changed.emit(self.mppt_combo.currentText())
    
    def emit_control(self):
        self.control_changed.emit(self.control_combo.currentText())
    
    def emit_islanding(self):
        self.islanding_changed.emit(self.islanding_check.isChecked())
    
    def emit_dc_source(self):
        self.dc_source_changed.emit(self.dc_source_combo.currentText())
    
    def get_params(self):
        return {
            'dc_voltage': self.dc_voltage_spin.value(),
            'frequency': self.frequency_spin.value(),
            'mod_index': self.mod_index_slider.value() / 100,
            'irradiance': self.irradiance_spin.value(),
            'temperature': self.temperature_spin.value(),
            'SOC': self.soc_spin.value(),
            'load_current': self.load_current_spin.value()
        }
    
    def get_phase_topology(self):
        return self.phase_combo.currentText()
    
    def get_multilevel_topology(self):
        return self.multilevel_combo.currentText()
    
    def get_pwm(self):
        return self.pwm_combo.currentText()
    
    def get_design(self):
        return self.design_combo.currentText()
    
    def get_mppt(self):
        return self.mppt_combo.currentText()
    
    def get_control(self):
        return self.control_combo.currentText()
    
    def is_islanding_enabled(self):
        return self.islanding_check.isChecked()
    
    def get_dc_source(self):
        return self.dc_source_combo.currentText()