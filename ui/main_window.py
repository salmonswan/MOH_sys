import random
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QDialog, QVBoxLayout,
    QLabel, QDialogButtonBox, QComboBox, QHBoxLayout, QGroupBox
)
from ui.input_tab import InputTab
from ui.results_tab import ResultsTab
from ui.analytics_tab import AnalyticsTab
from ui.help_tab import HelpTab
from core.loader import load_interns, load_facilities
from core.distributor import distribute, apply_overflow_action
import pandas as pd


class OverflowDialog(QDialog):
    """Dialog that lets the user choose how to handle overflow for each qualification."""

    def __init__(self, overflow_info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capacity Overflow")
        self.setMinimumWidth(500)
        self._combos: dict[str, QComboBox] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Some qualifications have more interns than available positions.</b><br>"
            "Choose how to handle each:"
        ))

        for qual, info in overflow_info.items():
            group = QGroupBox(qual)
            g_layout = QVBoxLayout(group)
            g_layout.addWidget(QLabel(
                f"<b>{info['count']}</b> extra intern(s), "
                f"<b>{len(info['facilities'])}</b> facility/ies available"
            ))

            row = QHBoxLayout()
            row.addWidget(QLabel("Action:"))
            combo = QComboBox()
            combo.addItem("Spread evenly beyond capacity", "spread")
            combo.addItem("Leave unassigned", "leave_unassigned")
            row.addWidget(combo, 1)
            self._combos[qual] = combo

            g_layout.addLayout(row)
            layout.addWidget(group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_actions(self) -> dict[str, str]:
        return {qual: combo.currentData() for qual, combo in self._combos.items()}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOH Uganda - Intern Placement System")
        self.setMinimumSize(1000, 700)

        self._interns_df: pd.DataFrame | None = None
        self._facilities_df: pd.DataFrame | None = None
        self._raw_facilities: pd.DataFrame | None = None

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self._input_tab = InputTab()
        self._results_tab = ResultsTab()
        self._analytics_tab = AnalyticsTab()

        tabs.addTab(self._input_tab, "Input")
        tabs.addTab(self._results_tab, "Results")
        tabs.addTab(self._analytics_tab, "Analytics")
        tabs.addTab(HelpTab(), "Help")

        self._tabs = tabs

        self._input_tab.distribute_requested.connect(self._on_distribute)
        self._results_tab.redistribute_requested.connect(self._on_redistribute)

    def _run_distribution(self, seed: int, locked: pd.DataFrame | None = None):
        result, warnings, overflow_info, capacity = distribute(
            self._interns_df, self._facilities_df, seed=seed, locked=locked
        )

        if overflow_info:
            dialog = OverflowDialog(overflow_info, parent=self)
            if dialog.exec() == QDialog.Accepted:
                actions = dialog.get_actions()
                rng = random.Random(seed + 1)
                result, overflow_warnings = apply_overflow_action(
                    result, overflow_info, actions, rng
                )
                warnings.extend(overflow_warnings)
            else:
                # User cancelled — show partial results with unassigned
                for qual, info in overflow_info.items():
                    warnings.append(
                        f"{qual}: {info['count']} intern(s) left unassigned (user cancelled)"
                    )

        self._results_tab.set_data(result, warnings)
        self._analytics_tab.set_data(result, self._raw_facilities)

    def _on_distribute(self, interns_path: str, facilities_path: str, seed: int):
        try:
            self._interns_df = load_interns(interns_path)
            self._facilities_df, self._raw_facilities = load_facilities(facilities_path)
        except Exception as e:
            QMessageBox.critical(self, "File Error", str(e))
            return

        self._results_tab.set_facilities_by_qual(self._facilities_df)
        self._run_distribution(seed)
        self._tabs.setCurrentIndex(1)

    def _on_redistribute(self):
        if self._interns_df is None or self._facilities_df is None:
            return

        locked = self._results_tab.get_locked_df()
        seed = self._input_tab.seed()
        self._run_distribution(seed, locked)
