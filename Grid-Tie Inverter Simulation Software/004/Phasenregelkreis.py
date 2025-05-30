import numpy as np

class PLL:
    def __init__(self, frequency):
        self.frequency = frequency
        self.omega = 2 * np.pi * frequency
        self.k = 0.5  # SOGI gain
        self.Kp = 2.0  # PI proportional gain
        self.Ki = 100.0  # PI integral gain
        self.integral_error = 0
        self.phase = 0
        self.q = 0  # Quadrature signal
        self.v = 0  # In-phase signal
    
    def update_parameters(self, frequency):
        self.frequency = frequency
        self.omega = 2 * np.pi * frequency
    
    def update(self, grid_voltage, time_step):
        # SOGI for orthogonal signals (scalar input)
        v_error = grid_voltage - self.v
        self.v += time_step * (self.k * v_error * self.omega - self.q * self.omega**2)
        self.q += time_step * self.v
        
        # Phase detection
        theta = np.arctan2(self.q, self.v) if self.v != 0 else self.phase
        phase_error = np.sin(theta - self.phase)
        
        # PI controller
        self.integral_error += phase_error * time_step
        omega_adjust = self.Kp * phase_error + self.Ki * self.integral_error
        self.phase += (self.omega + omega_adjust) * time_step
        self.phase = self.phase % (2 * np.pi)
        
        return self.phase
    
    def reset(self):
        self.integral_error = 0
        self.phase = 0
        self.q = 0
        self.v = 0