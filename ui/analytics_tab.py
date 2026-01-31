from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd


class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setSpacing(16)
        self._layout.setContentsMargins(16, 16, 16, 16)
        scroll.setWidget(self._container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._placeholder = QLabel("Run distribution first to see analytics.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color: gray; font-size: 14px;")
        self._layout.addWidget(self._placeholder)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151; margin-top: 4px;")
        return lbl

    def _separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e5e7eb;")
        return line

    def set_data(self, df: pd.DataFrame, raw_facilities: pd.DataFrame):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        assigned = df[df['Assigned Health Facility'].notna()]
        total = len(df)
        assigned_count = len(assigned)
        unassigned_count = total - assigned_count

        # Quick stats row
        stats_text = (
            f"<b>Total:</b> {total} &nbsp;&nbsp; "
            f"<b>Assigned:</b> {assigned_count} &nbsp;&nbsp; "
            f"<b>Unassigned:</b> {unassigned_count}"
        )
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 13px; padding: 8px; background: #f3f4f6; border-radius: 4px;")
        self._layout.addWidget(stats_label)

        # Summary crosstab
        self._layout.addWidget(self._section_label("Facility x Qualification"))
        self._add_summary_table(assigned, raw_facilities)
        self._layout.addWidget(self._separator())

        # Row 1: Qualification pie + Gender bar side by side
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        row1.addWidget(self._chart_qualification(assigned), 1)
        row1.addWidget(self._chart_gender(assigned), 1)
        row1_widget = QWidget()
        row1_widget.setLayout(row1)
        self._layout.addWidget(row1_widget)
        self._layout.addWidget(self._separator())

        # University chart (full width)
        self._layout.addWidget(self._chart_university(assigned))
        self._layout.addWidget(self._separator())

        # Fill rate chart (full width)
        self._layout.addWidget(self._chart_fill_rate(assigned, raw_facilities))
        self._layout.addWidget(self._separator())

        # Facility chart (full width)
        self._layout.addWidget(self._section_label("Interns per Facility"))
        self._layout.addWidget(self._chart_facility(assigned))

        self._layout.addStretch()

    def _add_summary_table(self, df: pd.DataFrame, raw_fac: pd.DataFrame):
        if df.empty:
            return

        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setStyleSheet("QTableWidget { font-size: 11px; }")

        cross = pd.crosstab(df['Assigned Health Facility'], df['Qualification'], margins=True)
        table.setRowCount(len(cross))
        table.setColumnCount(len(cross.columns))
        table.setHorizontalHeaderLabels([str(c) for c in cross.columns])
        table.setVerticalHeaderLabels([str(i) for i in cross.index])

        for r, idx in enumerate(cross.index):
            for c, col in enumerate(cross.columns):
                item = QTableWidgetItem(str(cross.loc[idx, col]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(r, c, item)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        row_height = 26
        header_height = 30
        table.setMinimumHeight(min(600, row_height * len(cross) + header_height))
        self._layout.addWidget(table)

    def _make_figure(self, width=6, height=4) -> tuple[Figure, any, FigureCanvasQTAgg]:
        fig = Figure(figsize=(width, height), dpi=100, layout='constrained')
        ax = fig.add_subplot(111)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setFixedHeight(int(height * 100))
        return fig, ax, canvas

    def _chart_qualification(self, df: pd.DataFrame) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._section_label("By Qualification"))
        counts = df['Qualification'].value_counts()
        fig, ax, canvas = self._make_figure(5, 4)
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        wedges, texts, autotexts = ax.pie(
            counts.values, labels=counts.index, autopct='%1.0f%%',
            colors=colors[:len(counts)], pctdistance=0.75,
            textprops={'fontsize': 9}
        )
        for t in autotexts:
            t.set_fontsize(8)
        ax.set_ylabel("")
        layout.addWidget(canvas)
        return container

    def _chart_gender(self, df: pd.DataFrame) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._section_label("By Gender"))
        counts = df['Sex'].value_counts()
        fig, ax, canvas = self._make_figure(5, 4)
        colors = ['#3b82f6', '#ec4899'] + ['#6b7280'] * 5
        bars = ax.bar(range(len(counts)), counts.values, color=colors[:len(counts)])
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.index, fontsize=10)
        ax.set_ylabel("Count", fontsize=10)
        # Add value labels on bars
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(val), ha='center', va='bottom', fontsize=9)
        layout.addWidget(canvas)
        return container

    def _chart_university(self, df: pd.DataFrame) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._section_label("By University"))
        counts = df['University'].value_counts()
        h = max(3, len(counts) * 0.45)
        fig, ax, canvas = self._make_figure(10, min(h, 8))
        bars = ax.barh(range(len(counts)), counts.values, color='#3b82f6')
        ax.set_yticks(range(len(counts)))
        ax.set_yticklabels(counts.index, fontsize=9)
        ax.set_xlabel("Number of Interns", fontsize=9)
        ax.invert_yaxis()
        # Add value labels
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(val), ha='left', va='center', fontsize=8)
        layout.addWidget(canvas)
        return container

    def _chart_fill_rate(self, df: pd.DataFrame, raw_fac: pd.DataFrame) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._section_label("Fill Rate per Facility"))
        qual_cols = [c for c in raw_fac.columns if c != 'Internship Training Centre']
        capacity = raw_fac.set_index('Internship Training Centre')[qual_cols].sum(axis=1)
        assigned_counts = df['Assigned Health Facility'].value_counts()
        fill = (assigned_counts / capacity * 100).dropna().sort_index()
        h = max(3, len(fill) * 0.45)
        fig, ax, canvas = self._make_figure(10, min(h, 8))
        colors = ['#10b981' if v <= 100 else '#ef4444' for v in fill.values]
        bars = ax.barh(range(len(fill)), fill.values, color=colors)
        ax.set_yticks(range(len(fill)))
        ax.set_yticklabels(fill.index, fontsize=9)
        ax.set_xlabel("Fill Rate (%)", fontsize=9)
        ax.axvline(100, color='red', linestyle='--', alpha=0.5, linewidth=1)
        ax.invert_yaxis()
        # Add percentage labels
        for bar, val in zip(bars, fill.values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:.0f}%", ha='left', va='center', fontsize=8)
        layout.addWidget(canvas)
        return container

    def _chart_facility(self, df: pd.DataFrame) -> QWidget:
        counts = df['Assigned Health Facility'].value_counts().sort_index()
        h = max(3, len(counts) * 0.45)
        fig, ax, canvas = self._make_figure(10, min(h, 10))
        bars = ax.barh(range(len(counts)), counts.values, color='#6366f1')
        ax.set_yticks(range(len(counts)))
        ax.set_yticklabels(counts.index, fontsize=9)
        ax.set_xlabel("Number of Interns", fontsize=9)
        ax.invert_yaxis()
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(val), ha='left', va='center', fontsize=8)
        return canvas
