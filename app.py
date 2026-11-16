from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QHBoxLayout,
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


class GradesWindow(QMainWindow):
    MAX_ROWS = 50
    VISIBLE_ROWS = 10

    def __init__(self) -> None:
        super().__init__()

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = 'grades.csv'

        self.setWindowTitle("Grades")

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        controls_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Grades")
        self.load_button.clicked.connect(self.load_grades)
        controls_layout.addWidget(self.load_button, alignment=Qt.AlignmentFlag.AlignTop)

        controls_layout.addStretch()

        actions_layout = QVBoxLayout()
        actions_layout.addWidget(QLabel("Amount of grade to be added:"))

        self.amount_input = QSpinBox()
        actions_layout.addWidget(self.amount_input)

        self.update_button = QPushButton("Update File")
        self.update_button.clicked.connect(self.update_file)
        actions_layout.addWidget(self.update_button)

        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.about)
        actions_layout.addWidget(self.about_button)

        controls_layout.addLayout(actions_layout)
        main_layout.addLayout(controls_layout)

        self.grades_table = QTableWidget(self.MAX_ROWS, 3)
        self.grades_table.setHorizontalHeaderLabels(
            ["ID", "Original Grades", "Corrected Grades"]
        )
        self.grades_table.verticalHeader().hide()
        self.grades_table.verticalHeader().setDefaultSectionSize(28)
        self.grades_table.setFixedHeight(
            self.grades_table.horizontalHeader().sizeHint().height()
            + self.VISIBLE_ROWS * self.grades_table.verticalHeader().defaultSectionSize()
            + 2
        )

        for row in range(self.MAX_ROWS):
            self.grades_table.setItem(row, 0, QTableWidgetItem())
            self.grades_table.setItem(row, 1, QTableWidgetItem())
            self.grades_table.setItem(row, 2, QTableWidgetItem())

        self.grades_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.grades_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.grades_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        main_layout.addWidget(self.grades_table)

        self.setCentralWidget(central_widget)

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
        self.set_grades(self.student_ids, self.original_grades)


    def set_grades(
        self, ids: Sequence[int | float], original_grades: Sequence[int | float]
    ) -> None:
        if len(ids) != len(original_grades):
            raise ValueError("IDs and original grades must have the same number of entries.")
        if len(ids) > self.MAX_ROWS:
            raise ValueError(f"At most {self.MAX_ROWS} grade entries can be displayed.")

        for row in range(self.MAX_ROWS):
            self.grades_table.item(row, 0).setText("")
            self.grades_table.item(row, 1).setText("")
            self.grades_table.item(row, 2).setText("")

        for row, (student_id, grade) in enumerate(zip(ids, original_grades)):
            self.grades_table.item(row, 0).setText(str(student_id))
            self.grades_table.item(row, 1).setText(str(grade))
            self.grades_table.item(row, 2).setText(str(grade))

    def update_file(self) -> None:
        pass

    def about(self) -> None:
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = GradesWindow()
    window.show()
    app.exec()