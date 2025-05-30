import numpy as np

class DCSource:
    def __init__(self):
        self.voltage = 400  # Default voltage (V)
    
    def update(self, params, time_step, current_time):
        return self.voltage
    
    def reset(self):
        pass

class PVPanel(DCSource):
    def __init__(self):
        super().__init__()
        self.V_oc_STC = 500  # Open-circuit voltage at STC (V)
        self.I_sc_STC = 10   # Short-circuit current at STC (A)
        self.T_STC = 25      # Standard test condition temperature (°C)
        self.G_STC = 1000    # Standard test condition irradiance (W/m²)
        self.alpha = 0.0005  # Current temperature coefficient (1/°C)
        self.beta = -0.003   # Voltage temperature coefficient (1/°C)
        self.k = 0.05        # Empirical loss factor
    
    def update(self, params, time_step, current_time):
        irradiance = params.get('irradiance', 1000)  # W/m²
        temperature = params.get('temperature', 25)  # °C
        
        # Adjust I_sc and V_oc for irradiance and temperature
        I_sc = self.I_sc_STC * (irradiance / self.G_STC) * (1 + self.alpha * (temperature - self.T_STC))
        V_oc = self.V_oc_STC * (1 + self.beta * (temperature - self.T_STC))
        
        # Simplified PV model: I = I_sc * (1 - (V/V_oc)^2)
        V = self.voltage
        I = I_sc * (1 - (V / V_oc) ** 2)
        V_new = V  # Initial guess
        for _ in range(5):  # Simple iteration to find operating voltage
            I = I_sc * (1 - (V_new / V_oc) ** 2)
            P = V_new * I
            V_new = V + self.k * (P - V * I)  # Adjust voltage towards MPP
        self.voltage = np.clip(V_new, 100, 800)
        return self.voltage
    
    def reset(self):
        self.voltage = 400

class Battery(DCSource):
    def __init__(self):
        super().__init__()
        self.V_nom = 400     # Nominal voltage (V)
        self.SOC = 0.8       # State of Charge (0 to 1)
        self.C_nom = 100     # Nominal capacity (Ah)
        self.discharge_rate = 0.1  # C-rate (fraction of capacity per hour)
    
    def update(self, params, time_step, current_time):
        SOC = params.get('SOC', self.SOC)  # State of Charge from control panel
        self.SOC = np.clip(SOC, 0.1, 1.0)
        
        # Simple battery model: Voltage depends on SOC
        V_min = 0.9 * self.V_nom
        V_max = 1.1 * self.V_nom
        self.voltage = V_min + (V_max - V_min) * self.SOC
        
        # Simulate discharge
        discharge_current = self.discharge_rate * self.C_nom
        self.SOC -= (discharge_current * time_step / 3600) / self.C_nom
        self.SOC = np.clip(self.SOC, 0.1, 1.0)
        
        self.voltage = np.clip(self.voltage, 100, 800)
        return self.voltage
    
    def reset(self):
        self.voltage = 400
        self.SOC = 0.8

class FuelCell(DCSource):
    def __init__(self):
        super().__init__()
        self.V_nom = 400     # Nominal voltage (V)
        self.I_max = 20      # Maximum current (A)
        self.efficiency = 0.6  # Fuel cell efficiency
    
    def update(self, params, time_step, current_time):
        load_current = params.get('load_current', 10)  # A
        load_current = np.clip(load_current, 0, self.I_max)
        
        # Simple fuel cell model: Voltage drops with current
        V_drop = 0.05 * load_current  # Linear voltage drop
        self.voltage = self.V_nom * self.efficiency - V_drop
        self.voltage = np.clip(self.voltage, 100, 800)
        return self.voltage
    
    def reset(self):
        self.voltage = 400

class HybridSource(DCSource):
    def __init__(self):
        super().__init__()
        self.pv = PVPanel()
        self.battery = Battery()
        self.fuel_cell = FuelCell()
        self.weights = {'pv': 0.5, 'battery': 0.3, 'fuel_cell': 0.2}
    
    def update(self, params, time_step, current_time):
        pv_voltage = self.pv.update(params, time_step, current_time)
        battery_voltage = self.battery.update(params, time_step, current_time)
        fuel_cell_voltage = self.fuel_cell.update(params, time_step, current_time)
        
        # Weighted average of voltages
        self.voltage = (
            self.weights['pv'] * pv_voltage +
            self.weights['battery'] * battery_voltage +
            self.weights['fuel_cell'] * fuel_cell_voltage
        )
        self.voltage = np.clip(self.voltage, 100, 800)
        return self.voltage
    
    def reset(self):
        self.pv.reset()
        self.battery.reset()
        self.fuel_cell.reset()
        self.voltage = 400