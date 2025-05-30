import numpy as np

class IslandingDetector:
    def __init__(self, frequency):
        self.frequency = frequency
        self.V_nom = 230 * np.sqrt(2)  # Nominal voltage (peak)
        self.f_nom = frequency
        self.V_min, self.V_max = 0.88 * self.V_nom, 1.1 * self.V_nom
        self.f_min, self.f_max = self.f_nom - 1, self.f_nom + 1
        self.active_freq_shift = 0.5  # Hz
        self.active_q = 0.05  # Reactive power injection
        self.last_voltage = 0
        self.last_freq = self.f_nom
        self.time_since_last = 0
    
    def update_parameters(self, frequency):
        self.frequency = frequency
        self.f_nom = frequency
        self.V_min, self.V_max = 0.88 * self.V_nom, 1.1 * self.V_nom
        self.f_min, self.f_max = self.f_nom - 1, self.f_nom + 1
    
    def detect(self, grid_voltage, time_step):
        if grid_voltage is None:
            return False
        
        # Passive: Over/Under voltage and frequency
        V_peak = np.max(np.abs(grid_voltage))
        if V_peak < self.V_min or V_peak > self.V_max:
            return True
        
        # Estimate frequency (simplified)
        zero_crossings = np.where(np.diff(np.sign(grid_voltage)))[0]
        if len(zero_crossings) >= 2:
            period = (zero_crossings[1] - zero_crossings[0]) * time_step
            freq = 1 / (2 * period)
        else:
            freq = self.last_freq
        
        if freq < self.f_min or freq > self.f_max:
            return True
        
        # Active: Frequency shift
        if self.time_since_last >= 0.1:  # Apply every 100ms
            self.last_freq = freq + self.active_freq_shift * np.sign(freq - self.f_nom)
            self.time_since_last = 0
        
        # Active: Reactive power variation (simulated effect)
        Q_inject = self.active_q * V_peak
        if abs(Q_inject - self.last_voltage) > 0.1 * self.V_nom:
            return True
        
        self.last_voltage = V_peak
        self.last_freq = freq
        self.time_since_last += time_step
        return False
    
    def reset(self):
        self.last_voltage = 0
        self.last_freq = self.f_nom
        self.time_since_last = 0