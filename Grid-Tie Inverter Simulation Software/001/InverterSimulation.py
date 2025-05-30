from Wechselrichtertopologie import SinglePhaseTopology, ThreePhaseTopology
from MehrstufigeWechselrichter import NPCInverter, FlyingCapacitorInverter, CascadedHBridgeInverter, MMCInverter, ReducedSwitchCountInverter, HybridCHBPlusNPCInverter

class InverterSimulation:
    def __init__(self):
        self.dc_voltage = 400
        self.frequency = 50
        self.mod_index = 0.8
        self.time_window = 0.04
        self.time_step = 0.0001
        self.current_time = 0
        self.samples = int(self.time_window / self.time_step)
        self.phase_topology = SinglePhaseTopology(self.dc_voltage, self.frequency, self.mod_index, self.time_window, self.time_step)
        self.multilevel_topology = None
        self.pwm_technique = "Multicarrier"
    
    def update_parameters(self, params):
        self.dc_voltage = params['dc_voltage']
        self.frequency = params['frequency']
        self.mod_index = params['mod_index']
        self.phase_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
        if self.multilevel_topology:
            self.multilevel_topology.update_parameters(self.dc_voltage, self.frequency, self.mod_index)
    
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
    
    def generate_waveforms(self):
        if self.multilevel_topology:
            data = self.multilevel_topology.generate_waveforms(self.current_time, self.phase_topology, self.pwm_technique)
        else:
            data = self.phase_topology.generate_waveforms(self.current_time)
        self.current_time += self.time_window / 2
        return data
    
    def reset(self):
        self.current_time = 0
        self.phase_topology.reset()
        if self.multilevel_topology:
            self.multilevel_topology.reset()