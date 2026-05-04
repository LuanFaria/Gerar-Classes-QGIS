from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsField, edit
from qgis.PyQt.QtCore import QVariant
from .classificador_dialog import ClassificadorDialog
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
import os


class classes_luan:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        plugin_dir = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_dir, "icon.png")
        self.action = QAction(QIcon(icon_path), "Classe Luan", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Cana", self.action)
    

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Cana", self.action)


    def meses_entre(self, d1, d2):
        try:
            if hasattr(d1, "toPyDate"):
                d1 = d1.toPyDate()
            if hasattr(d2, "toPyDate"):
                d2 = d2.toPyDate()

            if not d1 or not d2:
                return 0

            return (d1.year - d2.year) * 12 + (d1.month - d2.month)

        except:
            return 0
        

    def run(self):
        layers = self.iface.mapCanvas().layers()
        self.dlg = ClassificadorDialog(layers)

        self.dlg.btn_run.clicked.connect(self.processar)
        self.dlg.exec_()

    def processar(self):
        obs_input = self.dlg.obs_input.text()
        data_input = self.dlg.data_input.date()  # QDate
        layer = self.dlg.combo.currentData()

        if not layer:
            return

        total = max(layer.featureCount(), 1)

        # =========================
        # CRIAR CAMPOS
        # =========================
        with edit(layer):
            if layer.fields().indexFromName("OBS_IMG") == -1:
                layer.addAttribute(QgsField("OBS_IMG", QVariant.String, len=50))

            if layer.fields().indexFromName("DATA_IMG") == -1:
                layer.addAttribute(QgsField("DATA_IMG", QVariant.Date))

            if layer.fields().indexFromName("IDADE_IMG") == -1:
                layer.addAttribute(QgsField("IDADE_IMG", QVariant.Int))

            if layer.fields().indexFromName("CLASSE") == -1:
                layer.addAttribute(QgsField("CLASSE", QVariant.String, len=70))

        layer.updateFields()

        idades_validas = []

        # =========================
        # CALCULAR IDADE
        # =========================
        with edit(layer):
            for i, feat in enumerate(layer.getFeatures()):
                dt_plantio = feat["DT_PLANTIO"]
                dt_ult_cor = feat["DT_ULT_COR"]
                corte = feat["NMRO_CORTE"]

                idade = 0

                if corte == 1:
                    idade = self.meses_entre(data_input, dt_plantio)

                elif str(dt_ult_cor) == '1900-01-01' and corte > 1:
                    idade = 0

                else:
                    idade = self.meses_entre(data_input, dt_ult_cor)

                if idade < 30:
                    idades_validas.append(idade)

                # ✅ SALVA TUDO
                feat["OBS_IMG"] = obs_input
                feat["DATA_IMG"] = data_input
                feat["IDADE_IMG"] = idade

                layer.updateFeature(feat)

                self.dlg.progress.setValue(int((i / total) * 50))

        media = int(sum(idades_validas) / len(idades_validas)) if idades_validas else 0

        # =========================
        # CORRIGIR IDADE
        # =========================
        with edit(layer):
            for i, feat in enumerate(layer.getFeatures()):
                if feat["IDADE_IMG"] > 30:
                    feat["IDADE_IMG"] = media
                    layer.updateFeature(feat)

                self.dlg.progress.setValue(50 + int((i / total) * 25))

        # =========================
        # MÉDIA SOQUEIRA
        # =========================
        idades_soq = [
            f["IDADE_IMG"] for f in layer.getFeatures()
            if f["DESC_CANA"] == 'SOQUEIRA' and f["IDADE_IMG"] > 0
        ]

        media_soq = int(sum(idades_soq) / len(idades_soq)) if idades_soq else 0

        # =========================
        # CLASSE
        # =========================
        with edit(layer):
            for i, feat in enumerate(layer.getFeatures()):
                idade = feat["IDADE_IMG"]
                tipo = feat["DESC_CANA"]

                if tipo == 'SOQUEIRA' and idade <= media_soq:
                    classe = f"{obs_input}_SOQ_MEI{media_soq}"

                elif tipo == 'SOQUEIRA' and idade > media_soq:
                    classe = f"{obs_input}_SOQ_MA{media_soq}"

                elif tipo == 'CANA PLANTA':
                    classe = f"{obs_input}_CP"

                else:
                    classe = f"{obs_input}_BIS"

                feat["CLASSE"] = classe
                layer.updateFeature(feat)

                self.dlg.progress.setValue(75 + int((i / total) * 25))

        self.dlg.progress.setValue(100)

        QMessageBox.information(
            None,
            "Sucesso",
            "Processamento finalizado com sucesso!"
        )

        self.dlg.close()