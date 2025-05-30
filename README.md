# Grid-Tie Inverter Simulation Software

This desktop software simulates a Grid-Tie Inverter and is second version of a similar desktop app which I wrote in C language. I wrote this version from scratch in Python and added a few more features and improved some features that exist in first version.

## 1. Functioning Logic

The Grid-Tie Inverter Simulation is a desktop software to simulate a grid-connected inverter under various configurations, including single-phase or three-phase topologies, multilevel inverter designs, DC source types (Fixed, PV Panel, Battery, Fuel Cell, Hybrid), control strategies, maximum power point tracking (MPPT) algorithms, and grid conditions. 

- **Inverter Simulation Core (`InverterSimulation.py`)**: Orchestrates the simulation by integrating DC sources, phase topologies, multilevel inverters, control algorithms, MPPT, phase-locked loop (PLL), and islanding detection to generate realistic voltage and current waveforms.
- **DC Sources (`DCSource.py`)**: Models DC inputs with distinct physical characteristics for different source types, providing voltage to the inverter.
- **Phase Topologies (`Wechselrichtertopologie.py`)**: Generates single-phase or three-phase waveforms based on inverter configuration.
- **Multilevel Inverters (`MehrstufigeWechselrichter.py`)**: Produces multilevel output voltages for advanced inverter designs like Neutral Point Clamped (NPC) or Modular Multilevel Converter (MMC).
- **Control Strategies (`InverterSimulation.py`, `AdaptiveKontrollstrategien.py`)**: Implements control methods (PI, PR, Sliding Mode, MPC, Q-learning) to regulate inverter output for grid synchronization and performance.
- **MPPT Algorithms (`MaximaleLeistungspunktverfolgung.py`, `Welligkeitskorrelationssteuerung.py`)**: Optimizes power extraction from PV or hybrid sources using algorithms like Perturb & Observe or Ripple Correlation Control.
- **Grid Simulation (`GridSimulation.py`)**: Simulates grid voltage with configurable faults (sag, swell, harmonics, frequency shift) and weak grid conditions.
- **Islanding Detection (`IslandingDetection.py`)**: Detects grid disconnection using passive and active methods.
- **Phase-Locked Loop (`Phasenregelkreis.py`)**: Synchronizes inverter output with the grid phase.
- **Time-Domain Simulation (`Zeitbereichssimulation.py`)**: Analyzes transient behavior with configurable time steps.
- **Frequency-Domain Analysis (`FrequenzbereichsUndKleinsignalanalyse.py`)**: Performs small-signal analysis to evaluate system stability via Bode plots.

## 2. Simulation Logic

The simulation operates in a time-stepped manner, updating system states and generating waveforms based on user inputs and dynamic conditions.

### Simulation Loop
- **Initialization**: The `MainWindow` class creates an `InverterSimulation` object with default parameters: DC voltage = 400V, frequency = 50Hz, modulation index = 0.8, time window = 0.04s, time step = 0.001s. It initializes DC source, phase topology, PLL, and islanding detector.
- **Parameter Updates**: User inputs from the control panel (e.g., DC source type, topology, control method) are sent via signals (`parameters_changed`, `topology_changed`, etc.) to `InverterSimulation.update_simulation_parameters`, which updates:
  - Frequency, modulation index, and DC voltage (if Fixed source).
  - MPPT state (irradiance, temperature, SOC, load current).
  - PLL and islanding detector parameters.
- **Waveform Generation (`InverterSimulation.generate_waveforms`)**:
  1. **Islanding Check**: Calls `IslandingDetector.detect` with grid voltage (from `GridSimulation.py` or default 230V RMS sine wave). If islanding is detected, returns zero voltage/current arrays.
  2. **DC Voltage Update**: Calls `DCSource.update` with MPPT state parameters (irradiance = 1000 W/m², temperature = 25°C, SOC = 0.8, load current = 10A by default) to compute the DC voltage.
  3. **MPPT Application**: If enabled, calls `MPPTAlgorithm.update` to adjust DC voltage for maximum power.
  4. **Waveform Generation**:
     - Uses `SinglePhaseTopology` or `ThreePhaseTopology` to generate base sinusoidal waveforms (230V RMS, scaled by modulation index).
     - If a multilevel inverter is selected, calls `MultilevelInverter.generate_waveforms` with the chosen PWM technique (Multicarrier or Space Vector).
  5. **Grid Synchronization**: Calls `PLL.update` with a grid voltage sample to compute phase angle for waveform alignment.
  6. **Control Application**: Calls `InverterSimulation.apply_control` to regulate voltage and current using the selected control method (PI, PR, Sliding Mode, MPC).
  7. **Design Adjustment**: Applies `TransformerlessDesign` or `TransformerBasedDesign` to modify waveforms (e.g., DC offset or efficiency loss).
  8. **Time Advance**: Increments current time by time_window / 2 (0.02s) for continuous simulation.
- **Periodic Updates**: A QTimer in `Main.py` triggers `update_waveforms` every 100ms, generating new waveforms and updating plots.
### Time-Domain Simulation
- **Parameters**:
  - Base time step: 0.01–10ms (converted to seconds).
  - Variation factor: 0–1 (for sinusoidal time step variation).
  - Duration: 0.1–10s.
  - Adaptive stepping: Optional, adjusts time step based on voltage gradients.
- **Time Steps**: Generates `num_steps = duration / base_time_step` steps, with variation: `time_steps = base_time_step * (1 + variation_factor * sin(0 to 2π))`.
- **Adaptive Stepping**: If enabled, computes voltage gradient (`|V(t) - V(t-1)| / dt`). If gradient > 1000 V/s, reduces time step by 0.5x; if < 100 V/s, increases by 1.5x, clipped to [0.1 * base_time_step, 2 * base_time_step].
- **Simulation**:
  - Iterates `num_steps` times, overriding `InverterSimulation.time_step` and `time_window` (set to 10 * time_step).
  - Calls `generate_waveforms` to produce voltage/current for each phase.
  - Stores single-point data (first sample of each waveform) for efficiency.
  - Updates progress bar: `progress = (i + 1) / num_steps * 100`.
- **Output**: Stores time, voltages, and currents as NumPy arrays for plotting and CSV export.
### Frequency-Domain Analysis 
- **Parameters**:
  - Start frequency: 0.1–1000Hz.
  - End frequency: 10–100kHz.
  - Analysis type: Open-Loop or Closed-Loop.
  - Perturbation amplitude: 0.1–10% (scaled to 0.001–0.1).
- **Frequency Points**: Generates 100 logarithmically spaced frequencies using `np.logspace(log10(f_start), log10(f_end), 100)`.
- **Model**: Simplified PI controller + LC filter:
  - PI: `G_pi = Kp + Ki / s`, with Kp = 0.1, Ki = 10.
  - LC Filter: `G_filter = 1 / (L * C * s^2 + 1)`, with L = 0.001H, C = 100e-6F.
  - Transfer Function:
    - Open-Loop: `G = G_pi * G_filter`.
    - Closed-Loop: `G = (G_pi * G_filter) / (1 + G_pi * G_filter)`.
  - Applies perturbation: `G *= (1 + perturbation)`.
- **Calculation**:
  - For each frequency f, computes `s = 2j * π * f`.
  - Gain: `20 * log10(|G|)`.
  - Phase: `angle(G, deg=True)`.
- **Output**: Stores frequencies, gains, and phases for Bode plots and CSV export.
### Adaptive Control
- **Q-Learning Controller**:
  - State: Tracking error (V_grid - max(|V_inverter|)) discretized into 10 bins from -50V to 50V.
  - Action: Modulation index adjustment in 5 steps: [-0.1, -0.05, 0, 0.05, 0.1].
  - Parameters: Learning rate (α = 0.01–1), discount factor (γ = 0–1), exploration rate (ε = 0–1).
- **Training Mode**:
  - Chooses action: Random with probability ε, else `argmax(Q[state, :])`.
  - Applies action: `mod_index = clip(mod_index + action, 0, 1)`.
  - Computes reward: `-|V_grid - max(|V_inverter|)|`, with V_grid = 230 * sqrt(2).
  - Updates Q-table: `Q[state, action] += α * (reward + γ * max(Q[next_state, :]) - Q[state, action])`.
- **Apply Mode**: Uses trained Q-table to select actions without updates.
- **Simulation**:
  - Runs for 100–10,000 steps.
  - Tracks cumulative rewards and average Q-values.
  - Restores original modulation index after training.
- **Output**: Stores rewards and Q-values for plotting and CSV export.

## Physics Models and Equations

### DC Source Models 
- **Fixed Source**:
  - Model: Constant voltage output.
  - Equation: V = user_defined (default 400V, range 100–800V).
- **PV Panel**:
  - Model: Simplified I-V curve adjusted for irradiance (G) and temperature (T).
  - Parameters: V_oc_STC = 500V, I_sc_STC = 10A, T_STC = 25°C, G_STC = 1000 W/m², α = 0.0005/°C, β = -0.003/°C, k = 0.05.
  - Equations:
    - Short-circuit current: `I_sc = I_sc_STC * (G / G_STC) * (1 + α * (T - T_STC))`.
    - Open-circuit voltage: `V_oc = V_oc_STC * (1 + β * (T - T_STC))`.
    - Current: `I = I_sc * (1 - (V / V_oc)^2)`.
    - Power: `P = V * I`.
    - Voltage update: `V_new = V + k * (P - V * I)` (iterated 5 times).
  - Constraints: V clipped to 100–800V.
- **Battery**:
  - Model: Voltage varies with state of charge (SOC).
  - Parameters: V_nom = 400V, C_nom = 100Ah, discharge_rate = 0.1C, SOC = 0.1–1.0.
  - Equations:
    - Voltage: `V = V_min + (V_max - V_min) * SOC`, where V_min = 0.9 * V_nom, V_max = 1.1 * V_nom.
    - Discharge: `SOC -= (discharge_current * time_step / 3600) / C_nom`, where discharge_current = discharge_rate * C_nom.
  - Constraints: V clipped to 100–800V, SOC to 0.1–1.0.
- **Fuel Cell**:
  - Model: Voltage decreases with load current.
  - Parameters: V_nom = 400V, I_max = 20A, efficiency = 0.6.
  - Equations:
    - Voltage drop: `V_drop = 0.05 * load_current`.
    - Voltage: `V = V_nom * efficiency - V_drop`.
  - Constraints: V clipped to 100–800V.
- **Hybrid Source**:
  - Model: Weighted average of PV, Battery, and Fuel Cell voltages.
  - Weights: PV = 0.5, Battery = 0.3, Fuel Cell = 0.2.
  - Equation: `V = 0.5 * V_pv + 0.3 * V_battery + 0.2 * V_fuel_cell`.
  - Constraints: V clipped to 100–800V.
### Inverter Topologies 
- **Single-Phase Topology**:
  - Equations:
    - Voltage: `V = 230 * sqrt(2) * sin(2 * π * f * t)`.
    - Current: `I = (V_dc * mod_index / 230) * sqrt(2) * sin(2 * π * f * t)`.
- **Three-Phase Topology**:
  - Equations:
    - Voltage (per phase i): `V_i = 230 * sqrt(2) * sin(2 * π * f * t + θ_i)`, where θ_i = [0, -2π/3, 2π/3].
    - Current: `I_i = (V_dc * mod_index / 230) * sqrt(2) * sin(2 * π * f * t + θ_i)`.
- **Multilevel Inverters**:
  - Topologies: NPC, Flying Capacitor, Cascaded H-Bridge, MMC, Reduced Switch Count, Hybrid CHB+NPC.
  - Voltage Levels:
    - NPC, Flying Capacitor, Reduced Switch Count: [-V_dc/2, -V_dc/4, 0, V_dc/4, V_dc/2].
    - Cascaded H-Bridge: [-V_dc, -V_dc/2, 0, V_dc/2, V_dc].
    - MMC: [-V_dc/2, -3V_dc/8, -V_dc/4, -V_dc/8, 0, V_dc/8, V_dc/4, 3V_dc/8, V_dc/2].
    - Hybrid CHB+NPC: [-3V_dc/4, -V_dc/2, -V_dc/4, 0, V_dc/4, V_dc/2, 3V_dc/4].
  - PWM:
    - Multicarrier: Compares reference `ref = mod_index * sin(2 * π * f * t)` to thresholds `[-1, 1] / (levels-1)` to select output voltage.
    - Space Vector: Selects nearest level to `ref * 1.1 * V_dc/2`.
  - Equations:
    - Voltage: `V_out = level_j` where `ref > threshold_j`.
    - Current: `I = V_out * (mod_index / 230)`.
### Grid Model 
- **Nominal Voltage**:
  - Equation: `V = 230 * sqrt(2) * sin(2 * π * f * t)`.
- **Impedance**:
  - Parameters: R = 0.1Ω (1.0Ω weak), L = 0.001H (0.01H weak), I_load = 10A.
  - Equation: `V_drop = R * I_load + L * 2 * π * f * I_load`.
  - Output: `V = V_nominal - V_drop`.
- **Faults** (duration 100ms):
  - Sag: `V *= 0.8`.
  - Swell: `V *= 1.2`.
  - Harmonics: `V += 0.05 * 230 * sqrt(2) * (sin(10 * π * f * t) + sin(14 * π * f * t))`.
  - Frequency Shift: `f += 2`, `V = 230 * sqrt(2) * sin(2 * π * (f+2) * t)`.
### Transformer Designs
- **Transformerless**:
  - DC Offset: `V += 0.01 * V_dc`.
  - High-Pass Filter: `V[j] = α * (V[j] - V[j-1]) + V[j-1]`, α = 0.99.
  - Current: `I *= V_new / V_old` (V_old = 1.0 if V_old < 1e-6).
- **Transformer-Based**:
  - Efficiency: `V *= 0.95`.
  - Phase Shift: `V(t) = V(t - 0.01)` (interpolated).
  - Current: `I *= V_new / V_old` (V_old = 1.0 if V_old < 1e-6).

## 4. Algorithms and Equations
### MPPT Algorithms 
- **Perturb and Observe**:
  - Parameters: Step = 5V, V_oc = 500V, I_sc = 10A.
  - Equations:
    - Current: `I = I_sc * (1 - (V / V_oc)^2)`.
    - Power: `P = V * I`.
    - Update: If `P > P_prev`, `V += direction * step`; else `direction *= -1`, `V += direction * step`.
  - Constraints: V clipped to 100–800V.
- **Incremental Conductance**:
  - Parameters: Step = 5V, V_oc = 500V, I_sc = 10A.
  - Equations:
    - Current: `I = I_sc * (1 - (V / V_oc)^2)`.
    - Power: `P = V * I`.
    - Derivatives: `dV = V - V_prev`, `dI = I - I_prev`.
    - Conductance: `inc_conductance = dI / dV`, `conductance = I / V` (0 if V = 0).
    - Update:
      - If `dV != 0`:
        - If `inc_conductance > -conductance`, `V += step`.
        - If `inc_conductance < -conductance`, `V -= step`.
      - Else:
        - If `dI > 0`, `V += step`.
        - If `dI < 0`, `V -= step`.
  - Constraints: V clipped to 100–800V.
- **Constant Voltage**:
  - Equation: `V = 0.8 * V_oc = 0.8 * 500 = 400V`.
  - Constraints: V clipped to 100–800V.
- **Constant Current**:
  - Parameters: I_sc = 10A, V_oc = 500V.
  - Equations:
    - Target: `I_target = 0.9 * I_sc = 9A`.
    - Current: `I = I_sc * (1 - (V / V_oc)^2)`.
    - Update: `V *= I_target / I` (if I != 0).
  - Constraints: V clipped to 100–800V.
- **Ripple Correlation Control**:
  - Parameters: Gain = 0.1, ripple_freq = 100Hz, V_oc = 500V, I_sc = 10A.
  - Equations:
    - Ripple: `V_ripple = 0.01 * V * sin(2 * π * 100 * t)`.
    - Voltage: `V_total = V + V_ripple`.
    - Current: `I = I_sc * (1 - (V_total / V_oc)^2)`.
    - Power: `P = V_total * I`.
    - Derivatives: `dV_dt = (V_total - V_prev) / dt`, `dP_dt = (P - P_prev) / dt`.
    - Correlation: `correlation = dP_dt * dV_dt`.
    - Update: `V_new = V - gain * correlation`.
  - Constraints: V clipped to 100–800V.
### Control Algorithms
- **PI Control**:
  - Parameters: Kp_v = 0.5, Ki_v = 10, Kp_i = 0.2, Ki_i = 5.
  - Equations:
    - Errors: `error_v = V_ref - V`, `error_i = I_ref - I`, where V_ref = 230 * sqrt(2) * sin(2 * π * f * t + φ), I_ref = 10 * sin(2 * π * f * t + φ).
    - Integral: `integral_error_v += error_v * time_step`, `integral_error_i += error_i * time_step`.
    - Output: `V_out = V + Kp_v * error_v + Ki_v * integral_error_v`, `I_out = I + Kp_i * error_i + Ki_i * integral_error_i`.
- **PR Control**:
  - Parameters: Kp_v = 0.5, Kr_v = 50, Kp_i = 0.2, Kr_i = 20, ω_0 = 2 * π * f.
  - Equations:
    - Errors: `error_v = V_ref - V`, `error_i = I_ref - I`.
    - Resonant: `resonant_v = Kr_v * sin(ω_0 * t + φ) * error_v`, `resonant_i = Kr_i * sin(ω_0 * t + φ) * error_i`.
    - Output: `V_out = V + Kp_v * error_v + resonant_v`, `I_out = I + Kp_i * error_i + resonant_i`.
- **Sliding Mode**:
  - Parameters: λ_v = 100, λ_i = 50, K_v = 10, K_i = 5.
  - Equations:
    - Errors: `error_v = V_ref - V`, `error_i = I_ref - I`.
    - Surfaces: `s_v = error_v + λ_v * (error_v - prev_error_v)`, `s_i = error_i + λ_i * (error_i - prev_error_i)`.
    - Output: `V_out = V + K_v * sign(s_v)`, `I_out = I + K_i * sign(s_i)`.
    - Update: `prev_error_v = error_v`, `prev_error_i = error_i`.
- **MPC**:
  - Parameters: R = 0.1Ω, L = 0.01H.
  - Equations:
    - Predictions: `V_pred = V + (time_step / L) * (V_ref - V - R * I)`, `I_pred = I + (time_step / L) * (V_pred - V_ref)`.
    - Cost: `cost = (V_ref - V_pred)^2 + (I_ref - I_pred)^2`.
    - Output: If `cost < 2`, `V_out = V_pred`, `I_out = I_pred`; else `V_out = V`, `I_out = I`.

### Q-Learning
- **Parameters**:
  - Error bins: 10, from -50V to 50V.
  - Actions: [-0.1, -0.05, 0, 0.05, 0.1].
  - α = 0.01–1, γ = 0–1, ε = 0–1.
- **Equations**:
  - State: `state = digitize(error, bins) - 1`, error = 230 * sqrt(2) - max(|V_inverter|).
  - Action: Random if `rand() < ε`, else `argmax(Q[state, :])`.
  - Reward: `R = -|error|`.
  - Update: `Q[state, action] += α * (R + γ * max(Q[next_state, :]) - Q[state, action])`.
### PLL
- **Parameters**: k = 0.5, Kp = 2.0, Ki = 100.0, ω = 2 * π * f.
- **Equations**:
  - Error: `v_error = V_grid - v`.
  - SOGI: `v += time_step * (k * v_error * ω - q * ω^2)`, `q += time_step * v`.
  - Phase: `θ = arctan2(q, v)` (if v != 0, else previous phase).
  - Phase Error: `phase_error = sin(θ - phase)`.
  - Adjustment: `ω_adjust = Kp * phase_error + Ki * integral_error`, `integral_error += phase_error * time_step`.
  - Output: `phase += (ω + ω_adjust) * time_step`, `phase %= 2 * π`.
### Islanding Detection
- **Parameters**: V_nom = 230 * sqrt(2), f_nom = 50Hz, V_min = 0.88 * V_nom, V_max = 1.1 * V_nom, f_min = f_nom - 1, f_max = f_nom + 1, active_freq_shift = 0.5Hz, active_q = 0.05.
- **Passive Detection**:
  - Voltage: `V_peak = max(|V_grid|)`. Detect if `V_peak < V_min` or `V_peak > V_max`.
  - Frequency: `freq = 1 / (2 * period)`, where period is time between zero crossings. Detect if `freq < f_min` or `freq > f_max`.
- **Active Detection**:
  - Frequency Shift (every 100ms): `freq += active_freq_shift * sign(freq - f_nom)`.
  - Reactive Power: `Q_inject = active_q * V_peak`. Detect if `|Q_inject - last_voltage| > 0.1 * V_nom`.
## Integration and Data Flow
- **Input Processing**: User inputs update simulation parameters via signals in `Main.py`.
- **Waveform Pipeline**: `InverterSimulation.generate_waveforms` chains DC source → MPPT → topology → PWM → control → design to produce waveforms.
- **Grid Feedback**: Grid voltage from `GridSimulation.py` feeds into PLL and islanding detection.
- **Data Management**:
  - Time-domain: Stored in `Zeitbereichssimulation.py` and `Main.py` for plotting/export.
  - Frequency-domain: Stored in `FrequenzbereichsUndKleinsignalanalyse.py`.
  - Adaptive control: Stored in `AdaptiveKontrollstrategien.py`.
- **Reset**: All components reset to initial states (e.g., V = 400V, phase = 0) for consistent restarts.

