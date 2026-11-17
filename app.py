from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QLabel,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from About import AboutWindow


class EnterAwareSpinBox(QSpinBox):
    enterPressed = Signal()

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enterPressed.emit()


class GradesWindow(QMainWindow):
    MAX_ROWS = 50
    VISIBLE_ROWS = 10

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("gradesWindow")
        self.resize(550, 620)
        self.setMinimumHeight(520)

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ''
        self.about_window = AboutWindow()

        self.setWindowTitle("Grades")

        central_widget = QWidget(self)
        central_widget.setObjectName("mainContainer")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 14, 14, 14)
        controls_widget = QWidget(central_widget)
        controls_widget.setFixedWidth(240)
        controls_layout = QVBoxLayout(controls_widget)

        self.load_button = QPushButton("Load Grades")
        self.load_button.clicked.connect(self.load_grades)
        controls_layout.addWidget(self.load_button)

        actions_layout = QVBoxLayout()
        amount_label = QLabel("Amount of grade to be added:")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions_layout.addWidget(amount_label)

        self.amount_input = EnterAwareSpinBox()
        self.amount_input.setRange(0,100)
        self.amount_input.setFixedWidth(self.amount_input.sizeHint().width())
        actions_layout.addWidget(
            self.amount_input, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.amount_input.enterPressed.connect(self.amount_to_add_changed)

        self.update_button = QPushButton("Update File")
        self.update_button.clicked.connect(self.update_file)
        actions_layout.addWidget(self.update_button)

        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.about)
        actions_layout.addWidget(self.about_button)

        controls_layout.addLayout(actions_layout)
        main_layout.addWidget(
            controls_widget, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.grades_table = QTableWidget(self.MAX_ROWS, 3)
        self.grades_table.setHorizontalHeaderLabels(
            ["ID", "Original Grades", "Corrected Grades"]
        )
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.verticalHeader().hide()
        self.grades_table.verticalHeader().setDefaultSectionSize(32)
        self.grades_table.setFixedHeight(
            self.grades_table.horizontalHeader().sizeHint().height()
            + self.VISIBLE_ROWS * self.grades_table.verticalHeader().defaultSectionSize()
            + 2
        )

        for row in range(self.MAX_ROWS):
            for column in range(3):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grades_table.setItem(row, column, item)

        self.grades_table.setColumnWidth(0, 110)
        self.grades_table.setColumnWidth(1, 180)
        self.grades_table.setColumnWidth(2, 180)
        self.grades_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.grades_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.grades_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        self.grades_table.horizontalHeader().setStretchLastSection(False)
        table_width = sum(
            self.grades_table.columnWidth(column) for column in range(3)
        )
        table_width += (
            2 * self.grades_table.frameWidth()
            + self.grades_table.verticalScrollBar().sizeHint().width()
        )
        self.grades_table.setFixedWidth(table_width)
        main_layout.addWidget(self.grades_table, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setCentralWidget(central_widget)
        margins = main_layout.contentsMargins()
        self.setFixedWidth(table_width + margins.left() + margins.right())

    def amount_to_add_changed(self):
        for row in range(len(self.corrected_grades)):
            self.corrected_grades[row] = min(
                self.corrected_grades[row] + self.amount_input.value(), 100
            )
        self.set_grades()

    def load_grades(self):
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Grades File",
            "",
            "CSV files (*.csv);;All files (*)",
        )
        if not selected_file:
            return

        self.selected_file = selected_file
        with open(self.selected_file, 'r') as f:
            next(f) # מקדם בשורה אחת
            for line in f:
                parts = line.split(',')
                self.student_ids.append(int(parts[0]))
                self.original_grades.append(int(parts[1]))
                self.corrected_grades.append(int(parts[1]))
        self.set_grades()


    def set_grades(self) -> None:
        if len(self.student_ids) != len(self.original_grades):
            raise ValueError("IDs and original grades must have the same number of entries.")
        if len(self.student_ids) > self.MAX_ROWS:
            raise ValueError(f"At most {self.MAX_ROWS} grade entries can be displayed.")

        for row in range(self.MAX_ROWS):
            self.grades_table.item(row, 0).setText("")
            self.grades_table.item(row, 1).setText("")
            self.grades_table.item(row, 2).setText("")

        for row, (student_id, grade, corrected_grade) in enumerate(zip(self.student_ids, self.original_grades, self.corrected_grades)):
            self.grades_table.item(row, 0).setText(str(student_id))
            self.grades_table.item(row, 1).setText(str(grade))
            self.grades_table.item(row, 2).setText(str(corrected_grade))

    def update_file(self) -> None:
        if not self.selected_file:
            return

        with open(self.selected_file,'w') as f:
            f.write("ID,Grade\n")
            for i in range(len(self.student_ids)):
                f.write(f'{self.student_ids[i]},{self.corrected_grades[i]}\n')

        if not QDesktopServices.openUrl(QUrl.fromLocalFile(self.selected_file)):
            raise OSError(f"Could not open updated file: {self.selected_file}")

    def about(self) -> None:
        self.about_window.show()


def load_qss() -> str:
    qss_path = Path(__file__).resolve().parent / "styles.qss"
    return qss_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(load_qss())
    window = GradesWindow()
    window.show()
    app.exec()