from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QComboBox,
    QLabel, QProgressBar, QLineEdit, QDateEdit
)
from qgis.PyQt.QtCore import QDate


class ClassificadorDialog(QDialog):
    def __init__(self, layers):
        super().__init__()

        self.setWindowTitle("Classificador Cana")

        layout = QVBoxLayout()

        # Seleção de camada
        layout.addWidget(QLabel("Selecione a camada:"))
        self.combo = QComboBox()
        for layer in layers:
            self.combo.addItem(layer.name(), layer)
        layout.addWidget(self.combo)

        # OBS_IMG
        layout.addWidget(QLabel("Nome da imagem (OBS_IMG):"))
        self.obs_input = QLineEdit()
        layout.addWidget(self.obs_input)

        # DATA_IMG
        layout.addWidget(QLabel("Data da imagem (DATA_IMG):"))
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        layout.addWidget(self.data_input)

        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Botão
        self.btn_run = QPushButton("Executar")
        layout.addWidget(self.btn_run)

        self.setLayout(layout)