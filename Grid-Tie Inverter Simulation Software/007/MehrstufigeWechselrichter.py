import numpy as np
from Wechselrichtertopologie import SinglePhaseTopology, ThreePhaseTopology

class MultilevelInverter:
    def __init__(self, dc_voltage, frequency, mod_index, time_window, time_step):
        self.dc_voltage = dc_voltage
        self.frequency = frequency
        self.mod_index = mod_index
        self.time_window = time_window
        self.time_step = time_step
        self.samples = int(time_window / time_step)
        self.levels = 5  # Default 5-level
    
    def update_parameters(self, dc_voltage, frequency, mod_index):
        self.dc_voltage = dc_voltage
        self.frequency = frequency
        self.mod_index = mod_index
    
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        pass
    
    def reset(self):
        pass

    def apply_pwm(self, ref, levels, pwm_technique):
        v_out = np.zeros_like(ref)
        if pwm_technique == "Multicarrier":
            thresholds = np.linspace(-1, 1, len(levels)-1)
            for i in range(len(ref)):
                for j in range(len(thresholds)):
                    if ref[i] > thresholds[j]:
                        v_out[i] = levels[j+1]
                    else:
                        v_out[i] = levels[j]
                        break
        else:  # Space Vector
            # Simplified SVPWM: Discretize to nearest level with slight offset
            for i in range(len(ref)):
                normalized = ref[i] * 1.1  # Adjust for SVPWM
                v_out[i] = levels[np.argmin(np.abs(levels - normalized * self.dc_voltage/2))]
        return v_out

class NPCInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        levels = np.array([-self.dc_voltage/2, -self.dc_voltage/4, 0, self.dc_voltage/4, self.dc_voltage/2])
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}

class FlyingCapacitorInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        levels = np.array([-self.dc_voltage/2, -self.dc_voltage/4, 0, self.dc_voltage/4, self.dc_voltage/2])
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}

class CascadedHBridgeInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        levels = np.array([-self.dc_voltage, -self.dc_voltage/2, 0, self.dc_voltage/2, self.dc_voltage])
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}

class MMCInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        # MMC: More levels for smoother output
        levels = np.array([-self.dc_voltage/2, -self.dc_voltage*3/8, -self.dc_voltage/4, -self.dc_voltage/8, 0, 
                          self.dc_voltage/8, self.dc_voltage/4, self.dc_voltage*3/8, self.dc_voltage/2])
        self.levels = 9  # 9-level for MMC
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}

class ReducedSwitchCountInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        # Fewer switches, optimized 5-level
        levels = np.array([-self.dc_voltage/2, -self.dc_voltage/4, 0, self.dc_voltage/4, self.dc_voltage/2])
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}

class HybridCHBPlusNPCInverter(MultilevelInverter):
    def generate_waveforms(self, current_time, phase_topology, pwm_technique):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        num_phases = 1 if isinstance(phase_topology, SinglePhaseTopology) else 3
        phase_angles = [0] if num_phases == 1 else [0, -2 * np.pi / 3, 2 * np.pi / 3]
        
        # Hybrid: 7-level output
        levels = np.array([-self.dc_voltage*3/4, -self.dc_voltage/2, -self.dc_voltage/4, 0, 
                          self.dc_voltage/4, self.dc_voltage/2, self.dc_voltage*3/4])
        self.levels = 7
        voltage = []
        current = []
        for angle in phase_angles:
            ref = self.mod_index * np.sin(2 * np.pi * self.frequency * time + angle)
            v_out = self.apply_pwm(ref, levels, pwm_technique)
            voltage.append(v_out)
            current.append(v_out * (self.mod_index / 230))
        return {'time': time, 'voltage': voltage, 'current': current}