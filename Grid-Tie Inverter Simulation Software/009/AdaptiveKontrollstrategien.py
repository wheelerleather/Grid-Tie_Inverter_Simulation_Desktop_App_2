from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDoubleSpinBox, QLabel, QPushButton, QComboBox, QApplication, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np
import csv
import os

class QLearningController:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        # State: Discretized tracking error (-50V to 50V, 10 bins)
        self.error_bins = np.linspace(-50, 50, 11)
        # Action: Modulation index adjustment (-0.1 to 0.1, 5 steps)
        self.action_bins = np.linspace(-0.1, 0.1, 5)
        # Q-table: [states, actions]
        self.q_table = np.zeros((len(self.error_bins)-1, len(self.action_bins)))
        self.current_state = 0

    def get_state(self, error):
        state = np.digitize(error, self.error_bins) - 1
        return np.clip(state, 0, len(self.error_bins)-2)

    def choose_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.choice(len(self.action_bins))
        return np.argmax(self.q_table[self.current_state])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (
            reward + self.gamma * self.q_table[next_state, best_next_action] - self.q_table[state, action]
        )

    def get_action_value(self, action_idx):
        return self.action_bins[action_idx]

class AdaptiveControlWindow(QWidget):
    def __init__(self, inverter_simulation):
        super().__init__()
        self.inverter_simulation = inverter_simulation
        self.controller = QLearningController()
        self.setWindowTitle("Adaptive Control Strategies")
        self.setMinimumSize(800, 600)
        self.training_data = {'rewards': [], 'avg_q_values': []}
        self.is_training = False
        self.current_step = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #C0C0C0;
                font-family: 'Consolas';
                font-size: 12pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 3px inset #808080;
                border-radius: 6px;
                margin-top: 15px;
                padding: 10px;
                background-color: #C0C0C0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
            }
            QDoubleSpinBox, QPushButton, QComboBox {
                background-color: #FFFFFF;
                border: 2px inset #808080;
                padding: 5px;
                min-height: 30px;
                font-family: 'Consolas';
                font-size: 12pt;
            }
            QPushButton:pressed {
                background-color: #A0A0A0;
                border: 2px inset #808080;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        # Control Group
        control_group = QGroupBox("RL Parameters")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        control_group.setLayout(control_layout)

        # Learning Rate
        self.lr_label = QLabel("Learning Rate:")
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.01, 1.0)
        self.lr_spin.setValue(0.1)
        self.lr_spin.setSingleStep(0.01)
        self.lr_spin.setFixedHeight(40)

        # Discount Factor
        self.df_label = QLabel("Discount Factor:")
        self.df_spin = QDoubleSpinBox()
        self.df_spin.setRange(0.0, 1.0)
        self.df_spin.setValue(0.9)
        self.df_spin.setSingleStep(0.01)
        self.df_spin.setFixedHeight(40)

        # Exploration Rate
        self.er_label = QLabel("Exploration Rate:")
        self.er_spin = QDoubleSpinBox()
        self.er_spin.setRange(0.0, 1.0)
        self.er_spin.setValue(0.1)
        self.er_spin.setSingleStep(0.01)
        self.er_spin.setFixedHeight(40)

        # Training Steps
        self.steps_label = QLabel("Training Steps:")
        self.steps_spin = QDoubleSpinBox()
        self.steps_spin.setRange(100, 10000)
        self.steps_spin.setValue(1000)
        self.steps_spin.setSingleStep(100)
        self.steps_spin.setFixedHeight(40)

        # Control Mode
        self.mode_label = QLabel("Control Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Train", "Apply"])
        self.mode_combo.setCurrentText("Train")

        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_control)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_control)
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.export_button)

        control_layout.addWidget(self.lr_label)
        control_layout.addWidget(self.lr_spin)
        control_layout.addWidget(self.df_label)
        control_layout.addWidget(self.df_spin)
        control_layout.addWidget(self.er_label)
        control_layout.addWidget(self.er_spin)
        control_layout.addWidget(self.steps_label)
        control_layout.addWidget(self.steps_spin)
        control_layout.addWidget(self.mode_label)
        control_layout.addWidget(self.mode_combo)
        control_layout.addLayout(button_layout)
        control_layout.addStretch()

        # Plot Group
        plot_group = QGroupBox("Learning Progress")
        plot_layout = QVBoxLayout()
        plot_group.setLayout(plot_layout)

        # Reward Plot
        self.reward_plot = pg.PlotWidget()
        self.reward_plot.setBackground('k')
        self.reward_plot.showGrid(x=True, y=True, alpha=1.0)
        self.reward_plot.setLabel('left', 'Cumulative Reward', color='white')
        self.reward_plot.setLabel('bottom', 'Step', color='white')
        self.reward_plot.getAxis('left').setPen('w')
        self.reward_plot.getAxis('bottom').setPen('w')
        self.reward_plot.getAxis('left').setTextPen('w')
        self.reward_plot.getAxis('bottom').setTextPen('w')

        # Q-Value Plot
        self.qvalue_plot = pg.PlotWidget()
        self.qvalue_plot.setBackground('k')
        self.qvalue_plot.showGrid(x=True, y=True, alpha=1.0)
        self.qvalue_plot.setLabel('left', 'Average Q-Value', color='white')
        self.qvalue_plot.setLabel('bottom', 'Step', color='white')
        self.qvalue_plot.getAxis('left').setPen('w')
        self.qvalue_plot.getAxis('bottom').setPen('w')
        self.qvalue_plot.getAxis('left').setTextPen('w')
        self.qvalue_plot.getAxis('bottom').setTextPen('w')

        plot_layout.addWidget(self.reward_plot)
        plot_layout.addWidget(self.qvalue_plot)

        layout.addWidget(control_group)
        layout.addWidget(plot_group)

    def run_control(self):
        if self.is_training:
            return

        self.is_training = True
        self.controller = QLearningController(
            self.lr_spin.value(),
            self.df_spin.value(),
            self.er_spin.value()
        )
        self.training_data = {'rewards': [], 'avg_q_values': []}
        self.current_step = 0
        max_steps = int(self.steps_spin.value())
        mode = self.mode_combo.currentText()

        V_grid = 230 * np.sqrt(2)
        original_mod_index = self.inverter_simulation.mod_index

        while self.is_training and self.current_step < max_steps:
            # Get current state (tracking error)
            data = self.inverter_simulation.generate_waveforms()
            error = V_grid - np.max(np.abs(data['voltage'][0]))
            state = self.controller.get_state(error)

            # Choose and apply action
            action_idx = self.controller.choose_action()
            action = self.controller.get_action_value(action_idx)
            if mode == "Train":
                self.inverter_simulation.mod_index = np.clip(
                    self.inverter_simulation.mod_index + action, 0.0, 1.0
                )

            # Get next state and reward
            data = self.inverter_simulation.generate_waveforms()
            next_error = V_grid - np.max(np.abs(data['voltage'][0]))
            next_state = self.controller.get_state(next_error)
            reward = -abs(next_error)  # Negative of error magnitude

            if mode == "Train":
                self.controller.update_q_table(state, action_idx, reward, next_state)

            self.controller.current_state = next_state
            self.training_data['rewards'].append(reward)
            self.training_data['avg_q_values'].append(np.mean(self.controller.q_table))

            # Update plots
            self.reward_plot.clear()
            self.reward_plot.plot(range(len(self.training_data['rewards'])),
                                np.cumsum(self.training_data['rewards']),
                                pen=pg.mkPen('b', width=2))
            self.qvalue_plot.clear()
            self.qvalue_plot.plot(range(len(self.training_data['avg_q_values'])),
                                self.training_data['avg_q_values'],
                                pen=pg.mkPen('r', width=2))

            self.current_step += 1
            QApplication.processEvents()

        if mode == "Train":
            self.inverter_simulation.mod_index = original_mod_index
        self.is_training = False

    def stop_control(self):
        self.is_training = False

    def export_data(self):
        if not self.training_data['rewards']:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save RL Data", os.path.expanduser("~"), "CSV Files (*.csv);;All Files (*)"
        )
        if not filename:
            return
        if not filename.endswith('.csv'):
            filename += '.csv'

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Step', 'Cumulative Reward', 'Average Q-Value'])
            for i in range(len(self.training_data['rewards'])):
                writer.writerow([
                    i,
                    np.cumsum(self.training_data['rewards'])[i],
                    self.training_data['avg_q_values'][i]
                ])