from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSpinBox, QGroupBox
)
from PySide6.QtCore import Signal


class InputTab(QWidget):
    distribute_requested = Signal(str, str, int)  # interns_path, facilities_path, seed

    def __init__(self):
        super().__init__()
        self._interns_path = ''
        self._facilities_path = ''
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Interns file
        interns_group = QGroupBox("Interns File")
        ig_layout = QHBoxLayout(interns_group)
        self._interns_label = QLabel("No file selected")
        self._interns_label.setStyleSheet("color: gray;")
        btn_interns = QPushButton("Browse...")
        btn_interns.clicked.connect(self._pick_interns)
        ig_layout.addWidget(self._interns_label, 1)
        ig_layout.addWidget(btn_interns)
        layout.addWidget(interns_group)

        # Facilities file
        fac_group = QGroupBox("Carrying Capacity File")
        fg_layout = QHBoxLayout(fac_group)
        self._fac_label = QLabel("No file selected")
        self._fac_label.setStyleSheet("color: gray;")
        btn_fac = QPushButton("Browse...")
        btn_fac.clicked.connect(self._pick_facilities)
        fg_layout.addWidget(self._fac_label, 1)
        fg_layout.addWidget(btn_fac)
        layout.addWidget(fac_group)

        # Seed
        seed_group = QGroupBox("Random Seed")
        sg_layout = QHBoxLayout(seed_group)
        sg_layout.addWidget(QLabel("Seed:"))
        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(0, 999999)
        self._seed_spin.setValue(42)
        sg_layout.addWidget(self._seed_spin)
        sg_layout.addStretch()
        layout.addWidget(seed_group)

        # Distribute button
        self._btn_distribute = QPushButton("Distribute Interns")
        self._btn_distribute.setMinimumHeight(40)
        self._btn_distribute.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-size: 14px; "
            "font-weight: bold; border-radius: 6px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:disabled { background-color: #94a3b8; }"
        )
        self._btn_distribute.clicked.connect(self._on_distribute)
        layout.addWidget(self._btn_distribute)

        layout.addStretch()

    def _pick_interns(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Interns File", "", "Excel Files (*.xlsx *.xls *.xlsm *.xlsb *.ods)")
        if path:
            self._interns_path = path
            self._interns_label.setText(path.split('/')[-1])
            self._interns_label.setStyleSheet("")

    def _pick_facilities(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Carrying Capacity File", "", "Excel Files (*.xlsx *.xls *.xlsm *.xlsb *.ods)")
        if path:
            self._facilities_path = path
            self._fac_label.setText(path.split('/')[-1])
            self._fac_label.setStyleSheet("")

    def _on_distribute(self):
        if self._interns_path and self._facilities_path:
            self.distribute_requested.emit(
                self._interns_path, self._facilities_path, self._seed_spin.value()
            )

    def seed(self) -> int:
        return self._seed_spin.value()
