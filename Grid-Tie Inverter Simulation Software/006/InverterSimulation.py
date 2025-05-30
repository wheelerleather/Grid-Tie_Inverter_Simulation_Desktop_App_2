from Wechselrichtertopologie import SinglePhaseTopology, ThreePhaseTopology
from MehrstufigeWechselrichter import NPCInverter, FlyingCapacitorInverter, CascadedHBridgeInverter, MMCInverter, ReducedSwitchCountInverter, HybridCHBPlusNPCInverter
from TransformatorlosUndTransformatorbasiert import TransformerlessDesign, TransformerBasedDesign
from MaximaleLeistungspunktverfolgung import PerturbAndObserve, IncrementalConductance, ConstantVoltage, ConstantCurrent
from Welligkeitskorrelationssteuerung import RippleCorrelationControl
from Phasenregelkreis import PLL
from IslandingDetection import IslandingDetector
from DCSource import DCSource, PVPanel, Battery, FuelCell, HybridSource
import numpy as np

class InverterSimulation:
    def __init__(self):
        self.dc_voltage = 400
        self.frequency = 50
        self.mod_index = 0.8
        self.time_window = 0.04
        self.time_step = 0.001
        self.current_time = 0
        self.samples = int(self.time_window / self.time_step)
        self.phase_topology = SinglePhaseTopology(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        self.multilevel_topology = None
        self.pwm_technique = "Multicarrier"
        self.design = TransformerlessDesign()
        self.mppt = None
        self.control = "PI"
        self.islanding_enabled = True
        self.dc_source = DCSource()  # Default DC source
        self.dc_source_type = "Fixed"
        self.mppt_state = {'voltage': self.dc_voltage, 'power': 0, 'current': 0}
        self.control_state = {
            'integral_error_i': 0,
            'prev_error_i': 0,
            'integral_error_v': 0,
            'prev_error_v': 0,
            'sliding_surface': 0,
            'prev_sliding_surface': 0,
            'mpc_horizon': 10
        }
        self.pll = PLL(self.frequency)
        self.islanding_detector = IslandingDetector(self.frequency)
    
    def update_simulation_parameters(self, params):
        self.frequency = params['frequency']
        self.mod_index = params['mod_index']
        if self.dc_source_type == "Fixed":
            self.dc_voltage = params['dc_voltage']
        self.mppt_state['voltage'] = self.dc_voltage
        self.phase_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
        if self.multilevel_topology:
            self.multilevel_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
        self.pll.update_parameters(self.frequency)
        self.islanding_detector.update_parameters(self.frequency)
    
    def update_dc_source(self, source_type):
        self.dc_source_type = source_type
        if source_type == "Fixed":
            self.dc_source = DCSource()
        elif source_type == "PV Panel":
            self.dc_source = PVPanel()
        elif source_type == "Battery":
            self.dc_source = Battery()
        elif source_type == "Fuel Cell":
            self.dc_source = FuelCell()
        elif source_type == "Hybrid":
            self.dc_source = HybridSource()
        self.dc_voltage = self.dc_source.voltage
    
    def update_phase_topology(self, topology_name):
        self.phase_topology = SinglePhaseTopology(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step) if topology_name == "Single-Phase" else ThreePhaseTopology(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        self.current_time = 0
    
    def update_multilevel_topology(self, topology_name):
        if topology_name == "None":
            self.multilevel_topology = None
        elif topology_name == "NPC":
            self.multilevel_topology = NPCInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        elif topology_name == "Flying Capacitor":
            self.multilevel_topology = FlyingCapacitorInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        elif topology_name == "Cascaded H-Bridge":
            self.multilevel_topology = CascadedHBridgeInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        elif topology_name == "MMC":
            self.multilevel_topology = MMCInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        elif topology_name == "Reduced Switch Count":
            self.multilevel_topology = ReducedSwitchCountInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        elif topology_name == "Hybrid CHB+NPC":
            self.multilevel_topology = HybridCHBPlusNPCInverter(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        self.current_time = 0
    
    def update_pwm_technique(self, pwm_technique):
        self.pwm_technique = pwm_technique
        self.current_time = 0
    
    def update_design(self, design_name):
        self.design = TransformerlessDesign() if design_name == "Transformerless" else TransformerBasedDesign()
        self.current_time = 0
    
    def update_mppt(self, mppt_name):
        if mppt_name == "None":
            self.mppt = None
        elif mppt_name == "Perturb & Observe":
            self.mppt = PerturbAndObserve()
        elif mppt_name == "Incremental Conductance":
            self.mppt = IncrementalConductance()
        elif mppt_name == "Constant Voltage":
            self.mppt = ConstantVoltage()
        elif mppt_name == "Constant Current":
            self.mppt = ConstantCurrent()
        elif mppt_name == "Ripple Correlation Control":
            self.mppt = RippleCorrelationControl()
        self.current_time = 0
    
    def update_control(self, control_name):
        self.control = control_name
        self.current_time = 0
    
    def update_islanding_detection(self, enabled):
        self.islanding_enabled = enabled
        self.current_time = 0
    
    def apply_control(self, data, phase_angle):
        V_grid = 230 * np.sqrt(2)
        I_ref = 10
        phases = [0, 2*np.pi/3, 4*np.pi/3] if len(data['voltage']) == 3 else [0]
        output = {'time': data['time'], 'voltage': [], 'current': []}
        
        for i in range(len(data['voltage'])):
            V_ref = V_grid * np.sin(data['time'] * 2 * np.pi * self.frequency + phase_angle + phases[i])
            I_ref_i = I_ref * np.sin(data['time'] * 2 * np.pi * self.frequency + phase_angle + phases[i])
            V_out = np.zeros_like(data['time'])
            I_out = np.zeros_like(data['time'])
            
            for j in range(len(data['time'])):
                error_v = V_ref[j] - data['voltage'][i][j]
                error_i = I_ref_i[j] - data['current'][i][j]
                
                if self.control == "PI":
                    Kp_v, Ki_v = 0.5, 10
                    Kp_i, Ki_i = 0.2, 5
                    self.control_state['integral_error_v'] += error_v * self.time_step
                    self.control_state['integral_error_i'] += error_i * self.time_step
                    V_out[j] = data['voltage'][i][j] + Kp_v * error_v + Ki_v * self.control_state['integral_error_v']
                    I_out[j] = data['current'][i][j] + Kp_i * error_i + Ki_i * self.control_state['integral_error_i']
                
                elif self.control == "PR":
                    Kp_v, Kr_v, w0 = 0.5, 50, 2*np.pi*self.frequency
                    Kp_i, Kr_i = 0.2, 20
                    resonant_v = Kr_v * np.sin(data['time'][j] * 2 * np.pi * self.frequency + phase_angle + phases[i]) * error_v
                    resonant_i = Kr_i * np.sin(data['time'][j] * 2 * np.pi * self.frequency + phase_angle + phases[i]) * error_i
                    V_out[j] = data['voltage'][i][j] + Kp_v * error_v + resonant_v
                    I_out[j] = data['current'][i][j] + Kp_i * error_i + resonant_i
                
                elif self.control == "Sliding Mode":
                    lambda_v, lambda_i = 100, 50
                    K_v, K_i = 10, 5
                    s_v = error_v + lambda_v * (error_v - self.control_state['prev_error_v'])
                    s_i = error_i + lambda_i * (error_i - self.control_state['prev_error_i'])
                    V_out[j] = data['voltage'][i][j] + K_v * np.sign(s_v)
                    I_out[j] = data['current'][i][j] + K_i * np.sign(s_i)
                    self.control_state['prev_error_v'] = error_v
                    self.control_state['prev_error_i'] = error_i
                
                elif self.control == "MPC":
                    R = 0.1
                    L = 0.01
                    V_pred = data['voltage'][i][j] + (self.time_step / L) * (V_ref[j] - data['voltage'][i][j] - R * data['current'][i][j])
                    I_pred = data['current'][i][j] + (self.time_step / L) * (V_pred - V_ref[j])
                    cost = (V_ref[j] - V_pred)**2 + (I_ref_i[j] - I_pred)**2
                    V_out[j] = V_pred if cost < 2 else data['voltage'][i][j]
                    I_out[j] = I_pred if cost < 2 else data['current'][i][j]
            
            output['voltage'].append(V_out)
            output['current'].append(I_out)
        
        return output
    
    def generate_waveforms(self, grid_voltage=None):
        if self.islanding_enabled:
            if self.islanding_detector.detect(grid_voltage, self.time_step):
                num_phases = 3 if isinstance(self.phase_topology, ThreePhaseTopology) else 1
                return {
                    'time': np.linspace(self.current_time, self.current_time + self.time_window, self.samples),
                    'voltage': [np.zeros(self.samples) for _ in range(num_phases)],
                    'current': [np.zeros(self.samples) for _ in range(num_phases)]
                }
        
        # Update DC voltage from DC source
        self.dc_voltage = self.dc_source.update({
            'irradiance': self.mppt_state.get('irradiance', 1000),
            'temperature': self.mppt_state.get('temperature', 25),
            'SOC': self.mppt_state.get('SOC', 0.8),
            'load_current': self.mppt_state.get('load_current', 10)
        }, self.time_step, self.current_time)
        
        if self.mppt:
            self.dc_voltage = self.mppt.update(self.mppt_state, self.time_step, self.current_time)
            self.mppt_state['voltage'] = self.dc_voltage
            self.phase_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
            if self.multilevel_topology:
                self.multilevel_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
        
        grid_voltage_sample = grid_voltage[0] if grid_voltage is not None else 230 * np.sqrt(2) * np.sin(2 * np.pi * self.frequency * self.current_time)
        phase_angle = self.pll.update(grid_voltage_sample, self.time_step)
        
        if self.multilevel_topology:
            data = self.multilevel_topology.generate_waveforms(self.current_time, self.phase_topology, self.pwm_technique)
        else:
            data = self.phase_topology.generate_waveforms(self.current_time)
        
        data = self.apply_control(data, phase_angle)
        
        data = self.design.apply_design(data, self.dc_voltage, self.frequency, self.time_step)
        
        self.current_time += self.time_window / 2
        return data
    
    def reset(self):
        self.current_time = 0
        self.dc_source.reset()
        self.dc_voltage = self.dc_source.voltage
        self.mppt_state = {'voltage': self.dc_voltage, 'power': 0, 'current': 0}
        self.control_state = {
            'integral_error_i': 0,
            'prev_error_i': 0,
            'integral_error_v': 0,
            'prev_error_v': 0,
            'sliding_surface': 0,
            'prev_sliding_surface': 0,
            'mpc_horizon': 10
        }
        self.pll.reset()
        self.islanding_detector.reset()
        self.phase_topology.reset()
        if self.multilevel_topology:
            self.multilevel_topology.reset()