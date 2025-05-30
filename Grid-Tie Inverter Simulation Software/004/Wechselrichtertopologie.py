import numpy as np

class InverterTopology:
    def __init__(self, dc_voltage, frequency, mod_index, time_window, time_step):
        self.dc_voltage = dc_voltage
        self.frequency = frequency
        self.mod_index = mod_index
        self.time_window = time_window
        self.time_step = time_step
        self.samples = int(time_window / time_step)
    
    def update_parameters(self, dc_voltage, frequency, mod_index):
        self.dc_voltage = dc_voltage
        self.frequency = frequency
        self.mod_index = mod_index
    
    def generate_waveforms(self, current_time):
        pass
    
    def reset(self):
        pass

class SinglePhaseTopology(InverterTopology):
    def generate_waveforms(self, current_time):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        grid_voltage = [230 * np.sqrt(2) * np.sin(2 * np.pi * self.frequency * time)]
        inverter_current = [(self.dc_voltage * self.mod_index / 230) * np.sqrt(2) * np.sin(2 * np.pi * self.frequency * time)]
        return {
            'time': time,
            'voltage': grid_voltage,
            'current': inverter_current
        }
    
    def reset(self):
        pass

class ThreePhaseTopology(InverterTopology):
    def generate_waveforms(self, current_time):
        time = np.linspace(current_time, current_time + self.time_window, self.samples)
        phase_angles = [0, -2 * np.pi / 3, 2 * np.pi / 3]  # 0°, -120°, 120°
        grid_voltage = [
            230 * np.sqrt(2) * np.sin(2 * np.pi * self.frequency * time + angle)
            for angle in phase_angles
        ]
        inverter_current = [
            (self.dc_voltage * self.mod_index / 230) * np.sqrt(2) * np.sin(2 * np.pi * self.frequency * time + angle)
            for angle in phase_angles
        ]
        return {
            'time': time,
            'voltage': grid_voltage,
            'current': inverter_current
        }
    
    def reset(self):
        pass