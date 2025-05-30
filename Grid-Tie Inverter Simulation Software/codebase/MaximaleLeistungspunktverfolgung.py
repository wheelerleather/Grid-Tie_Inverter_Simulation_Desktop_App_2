import numpy as np

class MPPTAlgorithm:
    def update(self, state, time_step, current_time):
        pass

class PerturbAndObserve(MPPTAlgorithm):
    def __init__(self):
        self.perturbation_step = 5.0  # Voltage step (V)
        self.prev_power = 0
        self.prev_voltage = 400
        self.direction = 1  # 1 for increase, -1 for decrease
    
    def update(self, state, time_step, current_time):
        # PV model
        V_oc = 500  # Open-circuit voltage
        I_sc = 10   # Short-circuit current
        voltage = state['voltage']
        current = I_sc * (1 - (voltage / V_oc) ** 2)
        power = voltage * current
        
        # P&O logic
        if power > self.prev_power:
            # Continue in same direction
            voltage += self.direction * self.perturbation_step
        else:
            # Reverse direction
            self.direction *= -1
            voltage += self.direction * self.perturbation_step
        
        # Update state
        self.prev_power = power
        self.prev_voltage = voltage
        # Constrain voltage
        voltage = np.clip(voltage, 100, 800)
        return voltage

class IncrementalConductance(MPPTAlgorithm):
    def __init__(self):
        self.step_size = 5.0  # Voltage step
    
    def update(self, state, time_step, current_time):
        # PV model
        V_oc = 500
        I_sc = 10
        voltage = state['voltage']
        current = I_sc * (1 - (voltage / V_oc) ** 2)
        power = voltage * current
        
        # Incremental conductance
        dV = voltage - state.get('prev_voltage', voltage)
        dI = current - state.get('prev_current', current)
        if dV != 0:
            inc_conductance = dI / dV
            conductance = current / voltage if voltage != 0 else 0
            if inc_conductance > -conductance:
                voltage += self.step_size
            elif inc_conductance < -conductance:
                voltage -= self.step_size
        else:
            if dI > 0:
                voltage += self.step_size
            elif dI < 0:
                voltage -= self.step_size
        
        # Update state
        state['prev_voltage'] = voltage
        state['prev_current'] = current
        # Constrain voltage
        voltage = np.clip(voltage, 100, 800)
        return voltage

class ConstantVoltage(MPPTAlgorithm):
    def update(self, state, time_step, current_time):
        # Maintain 80% of open-circuit voltage
        V_oc = 500
        target_voltage = 0.8 * V_oc
        return np.clip(target_voltage, 100, 800)

class ConstantCurrent(MPPTAlgorithm):
    def update(self, state, time_step, current_time):
        # Maintain 90% of short-circuit current
        V_oc = 500
        I_sc = 10
        target_current = 0.9 * I_sc
        # Estimate voltage to achieve target current
        voltage = state['voltage']
        current = I_sc * (1 - (voltage / V_oc) ** 2)
        if current != 0:
            voltage *= (target_current / current)
        # Constrain voltage
        return np.clip(voltage, 100, 800)