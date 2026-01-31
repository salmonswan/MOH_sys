from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QLabel, QHeaderView, QComboBox, QCheckBox
)
from PySide6.QtCore import Signal, Qt
import pandas as pd


DISPLAY_COLUMNS = [
    'Name', 'Sex', 'Qualification', 'University',
    'Year of Completion', 'National Identification Number',
    'Nationality', 'Assigned Health Facility'
]


class ResultsTab(QWidget):
    redistribute_requested = Signal()  # emitted when user clicks "Re-distribute Unlocked"

    def __init__(self):
        super().__init__()
        self._df: pd.DataFrame | None = None
        self._facilities_by_qual: dict[str, list[str]] = {}
        self._lock_checks: list[QCheckBox] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Status
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        # Table
        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        self._btn_redistribute = QPushButton("Re-distribute Unlocked")
        self._btn_redistribute.clicked.connect(self.redistribute_requested.emit)
        self._btn_redistribute.setEnabled(False)
        btn_layout.addWidget(self._btn_redistribute)

        btn_layout.addStretch()

        self._btn_export = QPushButton("Export to Excel")
        self._btn_export.clicked.connect(self._export)
        self._btn_export.setEnabled(False)
        btn_layout.addWidget(self._btn_export)

        layout.addLayout(btn_layout)

    def set_facilities_by_qual(self, facilities_df: pd.DataFrame):
        """Store facility lists grouped by qualification for dropdown filtering."""
        self._facilities_by_qual = {}
        for _, row in facilities_df.iterrows():
            qual = row['Qualification']
            centre = row['Internship Training Centre']
            self._facilities_by_qual.setdefault(qual, [])
            if centre not in self._facilities_by_qual[qual]:
                self._facilities_by_qual[qual].append(centre)

    def set_data(self, df: pd.DataFrame, warnings: list[str]):
        self._df = df.copy()
        self._populate_table()
        self._btn_export.setEnabled(True)
        self._btn_redistribute.setEnabled(True)

        if warnings:
            self._status_label.setText("⚠ " + "; ".join(warnings))
            self._status_label.setStyleSheet("color: #b45309; font-weight: bold;")
        else:
            assigned = df['Assigned Health Facility'].notna().sum()
            self._status_label.setText(f"All {assigned} intern(s) assigned successfully.")
            self._status_label.setStyleSheet("color: #16a34a; font-weight: bold;")

    def _populate_table(self):
        df = self._df
        cols = ['Lock'] + [c for c in DISPLAY_COLUMNS if c in df.columns]
        self._table.setRowCount(len(df))
        self._table.setColumnCount(len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._lock_checks = []

        for row_idx in range(len(df)):
            # Lock checkbox
            cb = QCheckBox()
            self._lock_checks.append(cb)
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(cb)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            self._table.setCellWidget(row_idx, 0, cb_widget)

            for col_idx, col_name in enumerate(cols[1:], start=1):
                value = df.iloc[row_idx].get(col_name, '')
                if col_name == 'Assigned Health Facility':
                    qual = df.iloc[row_idx].get('Qualification', '')
                    combo = QComboBox()
                    options = sorted(self._facilities_by_qual.get(qual, []))
                    combo.addItems(options)
                    current = str(value) if pd.notna(value) else ''
                    if current in options:
                        combo.setCurrentText(current)
                    combo.currentTextChanged.connect(
                        lambda text, r=row_idx: self._on_facility_changed(r, text)
                    )
                    self._table.setCellWidget(row_idx, col_idx, combo)
                else:
                    item = QTableWidgetItem(str(value) if pd.notna(value) else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self._table.setItem(row_idx, col_idx, item)

        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setStretchLastSection(True)

    def _on_facility_changed(self, row_idx: int, text: str):
        if self._df is not None:
            self._df.iloc[row_idx, self._df.columns.get_loc('Assigned Health Facility')] = text

    def get_locked_df(self) -> pd.DataFrame:
        """Return a DataFrame with only the locked rows (with their facility assignments)."""
        if self._df is None:
            return pd.DataFrame()

        locked_indices = []
        for i, cb in enumerate(self._lock_checks):
            if cb.isChecked():
                locked_indices.append(i)

        if not locked_indices:
            return pd.DataFrame()

        return self._df.iloc[locked_indices].copy()

    def get_current_df(self) -> pd.DataFrame | None:
        return self._df

    def _export(self):
        if self._df is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedule", "intern_schedule.xlsx", "Excel Files (*.xlsx)")
        if path:
            from core.exporter import export_to_excel
            export_to_excel(self._df, path)
            self._status_label.setText(f"Exported to {path}")
            self._status_label.setStyleSheet("color: #16a34a;")
