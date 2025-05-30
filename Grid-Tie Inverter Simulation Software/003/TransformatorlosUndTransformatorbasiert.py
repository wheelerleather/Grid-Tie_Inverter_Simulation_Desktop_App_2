import numpy as np

class InverterDesign:
    def apply_design(self, data, dc_voltage, frequency, time_step):
        pass

class TransformerlessDesign(InverterDesign):
    def apply_design(self, data, dc_voltage, frequency, time_step):
        # Transformerless: Higher efficiency, add small DC offset
        output = data.copy()
        for i in range(len(output['voltage'])):
            # Add DC offset (1% of DC voltage)
            output['voltage'][i] = output['voltage'][i] + 0.01 * dc_voltage
            # Simulate high-pass filter to mitigate DC offset
            alpha = 0.99
            for j in range(1, len(output['voltage'][i])):
                output['voltage'][i][j] = alpha * (output['voltage'][i][j] - output['voltage'][i][j-1]) + output['voltage'][i][j-1]
            # Update current proportionally, avoid division by zero
            valid_voltage = np.where(np.abs(output['voltage'][i]) > 1e-6, output['voltage'][i], 1.0)
            scaling_factor = output['voltage'][i] / valid_voltage
            output['current'][i] = output['current'][i] * scaling_factor
        return output

class TransformerBasedDesign(InverterDesign):
    def apply_design(self, data, dc_voltage, frequency, time_step):
        # Transformer-Based: Galvanic isolation, slight efficiency loss
        output = data.copy()
        efficiency = 0.95  # Transformer efficiency
        phase_shift = 0.01  # Small phase shift due to inductance
        for i in range(len(output['voltage'])):
            # Scale voltage due to transformer losses
            output['voltage'][i] = output['voltage'][i] * efficiency
            # Apply phase shift
            time = output['time']
            shifted_voltage = np.zeros_like(output['voltage'][i])
            for j in range(len(time)):
                shifted_time = time[j] - phase_shift
                if shifted_time >= time[0]:
                    idx = np.searchsorted(time, shifted_time)
                    if idx < len(time):
                        shifted_voltage[j] = output['voltage'][i][idx]
            output['voltage'][i] = shifted_voltage
            # Update current proportionally, avoid division by zero
            valid_voltage = np.where(np.abs(data['voltage'][i]) > 1e-6, data['voltage'][i], 1.0)
            scaling_factor = output['voltage'][i] / valid_voltage
            output['current'][i] = output['current'][i] * scaling_factor
        return output