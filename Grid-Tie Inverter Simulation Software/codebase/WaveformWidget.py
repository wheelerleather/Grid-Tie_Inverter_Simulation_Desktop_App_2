import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QFont

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_topology = "Single-Phase"
        self.multilevel_topology = "None"
        self.pwm_technique = "Multicarrier"
        self.design = "Transformerless"
        self.mppt = "None"
        self.control = "PI"
        self.islanding_enabled = True
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)
        
        self.setStyleSheet("""
            background-color: #FFFFFF;
            border: 3px inset #808080;
            border-radius: 5px;
        """)
        
        self.plot_widgets = []
        self.voltage_curves = []
        self.current_curves = []
        self.setup_single_phase()
    
    def setup_single_phase(self):
        self.clear_plots()
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#000000')
        plot_widget.showGrid(x=True, y=True, alpha=0.5)
        plot_widget.getAxis('bottom').setGrid(255)
        plot_widget.getAxis('left').setGrid(255)
        title = self.get_plot_title()
        plot_widget.setTitle(title, color='#FFFFFF', size='14pt')
        plot_widget.setLabel('left', 'Amplitude (V/A)', color='#FFFFFF', size='12pt')
        plot_widget.setLabel('bottom', 'Time (s)', color='#FFFFFF', size='12pt')
        
        font = QFont('Consolas', 12)
        plot_widget.getAxis('bottom').setStyle(tickFont=font, textFillLimits=[(0, 0.8)])
        plot_widget.getAxis('left').setStyle(tickFont=font, textFillLimits=[(0, 0.8)])
        plot_widget.getAxis('bottom').setTextPen('#FFFFFF')
        plot_widget.getAxis('left').setTextPen('#FFFFFF')
        plot_widget.setXRange(0, 0.04, padding=0)
        
        plot_widget.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: 'Consolas';
                font-size: 12pt;
            }
        """)
        
        voltage_curve = plot_widget.plot(pen=pg.mkPen(color='b', width=3), name='Grid Voltage')
        current_curve = plot_widget.plot(pen=pg.mkPen(color='r', width=3), name='Inverter Current')
        legend = plot_widget.addLegend()
        legend.setBrush('#C0C0C0')
        legend.setPen(pg.mkPen(color='#808080', width=2))
        
        self.plot_widgets.append(plot_widget)
        self.voltage_curves.append([voltage_curve])
        self.current_curves.append([current_curve])
        self.layout.addWidget(plot_widget)
    
    def setup_three_phase(self):
        self.clear_plots()
        for phase in ['Phase A', 'Phase B', 'Phase C']:
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('#000000')
            plot_widget.showGrid(x=True, y=True, alpha=0.5)
            plot_widget.getAxis('bottom').setGrid(255)
            plot_widget.getAxis('left').setGrid(255)
            title = self.get_plot_title(phase)
            plot_widget.setTitle(title, color='#FFFFFF', size='14pt')
            plot_widget.setLabel('left', 'Amplitude (V/A)', color='#FFFFFF', size='12pt')
            plot_widget.setLabel('bottom', 'Time (s)', color='#FFFFFF', size='12pt')
            
            font = QFont('Consolas', 12)
            plot_widget.getAxis('bottom').setStyle(tickFont=font, textFillLimits=[(0, 0.8)])
            plot_widget.getAxis('left').setStyle(tickFont=font, textFillLimits=[(0, 0.8)])
            plot_widget.getAxis('bottom').setTextPen('#FFFFFF')
            plot_widget.getAxis('left').setTextPen('#FFFFFF')
            plot_widget.setXRange(0, 0.04, padding=0)
            
            plot_widget.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-family: 'Consolas';
                    font-size: 12pt;
                }
            """)
            
            voltage_curve = plot_widget.plot(pen=pg.mkPen(color='b', width=3), name=f'{phase} Voltage')
            current_curve = plot_widget.plot(pen=pg.mkPen(color='r', width=3), name=f'{phase} Current')
            legend = plot_widget.addLegend()
            legend.setBrush('#C0C0C0')
            legend.setPen(pg.mkPen(color='#808080', width=2))
            
            self.plot_widgets.append(plot_widget)
            self.voltage_curves.append([voltage_curve])
            self.current_curves.append([current_curve])
            self.layout.addWidget(plot_widget)
    
    def get_plot_title(self, phase=None):
        islanding = "Islanding Detection" if self.islanding_enabled else "No Islanding Detection"
        if self.multilevel_topology == "None" and self.mppt == "None" and self.control == "PI" and not self.islanding_enabled:
            return f"{phase} Waveforms" if phase else "Inverter Output Waveforms"
        return f"{phase} Waveforms ({self.multilevel_topology}, {self.pwm_technique}, {self.design}, {self.mppt}, {self.control}, {islanding})" if phase else f"Inverter Output Waveforms ({self.multilevel_topology}, {self.pwm_technique}, {self.design}, {self.mppt}, {self.control}, {islanding})"
    
    def clear_plots(self):
        for widget in self.plot_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        self.plot_widgets = []
        self.voltage_curves = []
        self.current_curves = []
    
    def set_phase_topology(self, topology):
        if topology != self.current_topology:
            self.current_topology = topology
            if topology == "Single-Phase":
                self.setup_single_phase()
            else:
                self.setup_three_phase()
    
    def set_multilevel_topology(self, multilevel_topology):
        self.multilevel_topology = multilevel_topology
        self.set_phase_topology(self.current_topology)
    
    def set_pwm_technique(self, pwm_technique):
        self.pwm_technique = pwm_technique
        self.set_phase_topology(self.current_topology)
    
    def set_design(self, design):
        self.design = design
        self.set_phase_topology(self.current_topology)
    
    def set_mppt(self, mppt):
        self.mppt = mppt
        self.set_phase_topology(self.current_topology)
    
    def set_control(self, control):
        self.control = control
        self.set_phase_topology(self.current_topology)
    
    def set_islanding_enabled(self, enabled):
        self.islanding_enabled = enabled
        self.set_phase_topology(self.current_topology)
    
    def update_plot(self, data):
        num_phases = len(data['voltage'])
        if num_phases == 1 and self.current_topology != "Single-Phase":
            self.set_phase_topology("Single-Phase")
        elif num_phases == 3 and self.current_topology != "Three-Phase":
            self.set_phase_topology("Three-Phase")
        
        if self.current_topology == "Single-Phase" and num_phases >= 1:
            self.voltage_curves[0][0].setData(data['time'], data['voltage'][0])
            self.current_curves[0][0].setData(data['time'], data['current'][0])
            self.plot_widgets[0].setXRange(data['time'][0], data['time'][-1], padding=0)
        elif self.current_topology == "Three-Phase" and num_phases == 3:
            for i in range(3):
                self.voltage_curves[i][0].setData(data['time'], data['voltage'][i])
                self.current_curves[i][0].setData(data['time'], data['current'][i])
                self.plot_widgets[i].setXRange(data['time'][0], data['time'][-1], padding=0)