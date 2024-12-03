from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QPushButton, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QCheckBox, QSpinBox, QFrame)
from modelo.datos import RequisitosContenedor, Paquete


class StyleSheet:
    MAIN = """
        QMainWindow {
            background-color: #ffffff;
        }

        QTabWidget::pane {
            border: none;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }

        QFrame {
            border: none;
            margin: 0;
            padding: 0;
        }

        QTabBar::tab {
            background-color: #f8f9fa;
            border: none;
            padding: 8px 16px;
            margin-right: 2px;
            color: #495057;
            font-weight: bold;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #1976D2;
            border-bottom: 2px solid #1976D2;
        }

        QPushButton {
            background-color: #1976D2;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 80px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1565C0;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }

        QTableWidget {
            border: none;
            background-color: #ffffff;
            gridline-color: transparent;
            selection-background-color: #e3f2fd;
            margin: 0;
            padding: 0;
        }

        QTableWidget::item {
            padding: 4px 6px;
            border-bottom: 1px solid #e0e0e0;
            color: #212529;
        }

        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #000000;
        }

        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 6px;
            border: none;
            border-bottom: 2px solid #e0e0e0;
            font-weight: bold;
            color: #212529;
        }

        QHeaderView {
            font-size: 13px;
        }

        QTableWidget QScrollBar:vertical {
            border: none;
            background-color: #f8f9fa;
            width: 6px;
            margin: 0px;
        }

        QTableWidget QScrollBar::handle:vertical {
            background-color: #90a4ae;
            border-radius: 3px;
        }

        QTableWidget QScrollBar::add-line:vertical,
        QTableWidget QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QSpinBox {
            padding: 3px 5px;
            border: 1px solid #bdbdbd;
            border-radius: 3px;
            background-color: #ffffff;
            color: #212529;
            min-width: 60px;
            margin: 0;
        }

        QSpinBox:hover {
            border-color: #1976D2;
        }

        QSpinBox:focus {
            border-color: #1976D2;
            background-color: #ffffff;
        }

        QSpinBox::up-button, QSpinBox::down-button {
            width: 0px;
            border: none;
        }

        QSpinBox::up-arrow, QSpinBox::down-arrow {
            width: 0px;
            height: 0px;
            border: none;
        }

        QCheckBox {
            spacing: 4px;
            color: #212529;
        }

        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border: 2px solid #757575;
            border-radius: 3px;
        }

        QCheckBox::indicator:checked {
            background-color: #1976D2;
            border-color: #1976D2;
        }

        QCheckBox::indicator:hover {
            border-color: #1976D2;
        }

        QLabel {
            color: #212529;
            font-size: 13px;
            font-weight: bold;
            margin: 0;
            padding: 0;
        }

        QLabel[class="title"] {
            font-size: 14px;
            font-weight: bold;
            color: #1976D2;
            margin: 0;
            padding: 0;
        }

        QTabWidget {
            font-size: 13px;
        }
    """

class ModernFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ModernFrame {
                background-color: white;
                border: 0;
                border-radius: 4px;
                padding: 16px;
                margin: 0;
            }
        """)

class BPGAVista(QMainWindow):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setup_ui()
        self.setStyleSheet(StyleSheet.MAIN)

    def setup_ui(self):
        self.setWindowTitle("Optimización de Empaquetado Multi-Contenedor")
        self.setGeometry(100, 100, 1200, 900)

        widget_principal = QWidget()
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        widget_principal.setLayout(layout_principal)
        self.setCentralWidget(widget_principal)

        # Parámetros del algoritmo en un marco moderno
        frame_parametros = ModernFrame()
        layout_parametros = QHBoxLayout()
        layout_parametros.setContentsMargins(0, 0, 0, 0)
        layout_parametros.setSpacing(100)
        frame_parametros.setLayout(layout_parametros)

        for label_text, spinbox_attr, default_value in [
            ("Tamaño de Población:", "selector_poblacion", 100),
            ("Número de Generaciones:", "selector_generaciones", 10)
        ]:
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            label = QLabel(label_text)
            spinbox = QSpinBox()
            spinbox.setRange(1, 99999)
            spinbox.setValue(default_value)
            container_layout.addWidget(label)
            container_layout.addWidget(spinbox)
            container.setLayout(container_layout)
            layout_parametros.addWidget(container)
            setattr(self, spinbox_attr, spinbox)

        layout_principal.addWidget(frame_parametros)

        # Pestañas
        self.widget_pestanas = QTabWidget()
        self.pestanas = {
            '1D': PestanaPaquete(1),
            '2D': PestanaPaquete(2),
            '3D': PestanaPaquete(3)
        }

        for nombre, pestana in self.pestanas.items():
            self.widget_pestanas.addTab(pestana, nombre)

        layout_principal.addWidget(self.widget_pestanas)

        # Botones de acción
        frame_botones = ModernFrame()
        layout_botones = QHBoxLayout()
        layout_botones.setContentsMargins(0, 0, 0, 0)
        layout_botones.setSpacing(100)
        frame_botones.setLayout(layout_botones)

        for button_text, slot, primary in [
            ("Optimizar", self.enviar_datos, True),
            ("Limpiar Todo", self.limpiar_todo, False)
        ]:
            btn = QPushButton(button_text)
            btn.clicked.connect(slot)
            if not primary:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
            layout_botones.addWidget(btn)

        layout_principal.addWidget(frame_botones)

    def enviar_datos(self):
        pestana_actual = self.pestanas[self.widget_pestanas.tabText(self.widget_pestanas.currentIndex())]

        contenedores = pestana_actual.obtener_contenedores()
        paquetes = pestana_actual.obtener_paquetes()
        permisos_rotacion = pestana_actual.obtener_rotaciones_permitidas()
        poblacion = self.selector_poblacion.value()
        generaciones = self.selector_generaciones.value()

        self.controlador.solicitud(
            contenedores,
            paquetes,
            permisos_rotacion,
            poblacion,
            generaciones
        )

    def limpiar_todo(self):
        pestana_actual = self.pestanas[self.widget_pestanas.tabText(self.widget_pestanas.currentIndex())]
        pestana_actual.limpiar_entradas()


class PestanaPaquete(QWidget):
    def __init__(self, dimensiones):
        super().__init__()
        self.dimensiones = dimensiones
        self.contador_contenedor = {}
        self.setup_ui()
        self.setStyleSheet(StyleSheet.MAIN)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Sección Contenedores
        frame_contenedores = ModernFrame()
        layout_contenedores = QVBoxLayout()
        layout_contenedores.setContentsMargins(0, 0, 0, 0)
        layout_contenedores.setSpacing(0)
        frame_contenedores.setLayout(layout_contenedores)

        titulo_contenedores = QLabel("Contenedores")
        titulo_contenedores.setStyleSheet("font-size: 16px; margin-bottom: 8px;")
        layout_contenedores.addWidget(titulo_contenedores)

        self.tabla_contenedores = self.crear_tabla_contenedores()
        layout_contenedores.addWidget(self.tabla_contenedores)

        btn_agregar_contenedor = QPushButton("+ Agregar Contenedor")
        btn_agregar_contenedor.clicked.connect(self.agregar_contenedor)
        layout_contenedores.addWidget(btn_agregar_contenedor)

        layout.addWidget(frame_contenedores)

        # Sección Paquetes
        frame_paquetes = ModernFrame()
        layout_paquetes = QVBoxLayout()
        layout_paquetes.setContentsMargins(0, 0, 0, 0)
        layout_paquetes.setSpacing(0)
        frame_paquetes.setLayout(layout_paquetes)

        titulo_paquetes = QLabel("Paquetes")
        titulo_paquetes.setStyleSheet("font-size: 16px; margin-bottom: 8px;")
        layout_paquetes.addWidget(titulo_paquetes)

        self.tabla_paquetes = self.crear_tabla_paquetes()
        layout_paquetes.addWidget(self.tabla_paquetes)

        btn_agregar_paquete = QPushButton("+ Agregar Paquete")
        btn_agregar_paquete.clicked.connect(self.agregar_paquete)
        layout_paquetes.addWidget(btn_agregar_paquete)

        layout.addWidget(frame_paquetes)

    def crear_tabla_contenedores(self):
        tabla = QTableWidget()
        tabla.setColumnCount(self.dimensiones + 3)
        encabezados = ([f"Dimensión {i + 1}" for i in range(self.dimensiones)] +
                      ["Cantidad", "Opcional", "ID"])
        tabla.setHorizontalHeaderLabels(encabezados)

        return tabla

    def crear_tabla_paquetes(self):
        tabla = QTableWidget()
        self.columnas_rotacion = []
        if self.dimensiones == 2:
            self.columnas_rotacion = ["R-XY"]
        elif self.dimensiones == 3:
            self.columnas_rotacion = [
                "R-XY", "R-XZ", "R-YZ",
                "R-XY-XZ", "R-XY-YZ"
            ]

        total_columnas = self.dimensiones + 2 + len(self.columnas_rotacion) + 1
        tabla.setColumnCount(total_columnas)

        encabezados = ([f"Dimensión {i + 1}" for i in range(self.dimensiones)] +
                      ["Cant. Mín", "Cant. Máx"] +
                      self.columnas_rotacion +
                      ["ID"])
        tabla.setHorizontalHeaderLabels(encabezados)

        return tabla

    def agregar_contenedor(self):
        fila = self.tabla_contenedores.rowCount()
        self.tabla_contenedores.insertRow(fila)

        for columna in range(self.dimensiones):
            selector = QSpinBox()
            selector.setRange(1, 999999)
            selector.setValue(1)
            self.tabla_contenedores.setCellWidget(fila, columna, selector)

        selector_cantidad = QSpinBox()
        selector_cantidad.setRange(1, 999999)
        selector_cantidad.setValue(1)
        self.tabla_contenedores.setCellWidget(fila, self.dimensiones, selector_cantidad)

        casilla_opcional = QCheckBox()
        self.tabla_contenedores.setCellWidget(fila, self.dimensiones + 1, casilla_opcional)

        item_id = QTableWidgetItem(f"Contenedor-{fila + 1}")
        self.tabla_contenedores.setItem(fila, self.dimensiones + 2, item_id)

    def agregar_paquete(self):
        fila = self.tabla_paquetes.rowCount()
        self.tabla_paquetes.insertRow(fila)

        for columna in range(self.dimensiones):
            selector = QSpinBox()
            selector.setRange(1, 999999)
            selector.setValue(1)
            self.tabla_paquetes.setCellWidget(fila, columna, selector)

        columna_min = self.dimensiones
        columna_max = self.dimensiones + 1

        selector_min = QSpinBox()
        selector_min.setRange(1, 999999)
        selector_min.setValue(1)
        self.tabla_paquetes.setCellWidget(fila, columna_min, selector_min)

        selector_max = QSpinBox()
        selector_max.setRange(1, 999999)
        selector_max.setValue(1)
        self.tabla_paquetes.setCellWidget(fila, columna_max, selector_max)

        columna_actual = self.dimensiones + 2
        for _ in self.columnas_rotacion:
            casilla = QCheckBox()
            casilla.setChecked(False)
            self.tabla_paquetes.setCellWidget(fila, columna_actual, casilla)
            columna_actual += 1

        item_id = QTableWidgetItem(f"Paquete-{fila + 1}")
        self.tabla_paquetes.setItem(fila, columna_actual, item_id)

    def obtener_contenedores(self) -> list[RequisitosContenedor]:
        contenedores = []
        self.contador_contenedor.clear()

        for fila in range(self.tabla_contenedores.rowCount()):
            dimensiones_cont = []
            for columna in range(self.dimensiones):
                selector = self.tabla_contenedores.cellWidget(fila, columna)
                dimensiones_cont.append(selector.value())

            selector_cantidad = self.tabla_contenedores.cellWidget(fila, self.dimensiones)
            cantidad = selector_cantidad.value()

            casilla_opcional = self.tabla_contenedores.cellWidget(fila, self.dimensiones + 1)
            es_opcional = casilla_opcional.isChecked()

            tupla_dim = tuple(dimensiones_cont)
            if tupla_dim not in self.contador_contenedor:
                self.contador_contenedor[tupla_dim] = 0

            for i in range(cantidad):
                self.contador_contenedor[tupla_dim] += 1
                id_contenedor = f"Contenedor-{fila + 1}-{self.contador_contenedor[tupla_dim]}"
                contenedor = RequisitosContenedor(
                    dimensiones=tupla_dim,
                    id=id_contenedor,
                    uso_opcional=es_opcional)
                contenedores.append(contenedor)

        return contenedores

    def obtener_paquetes(self) -> list[Paquete]:
        paquetes = []
        for fila in range(self.tabla_paquetes.rowCount()):
            dimensiones_paq = []
            for columna in range(self.dimensiones):
                selector = self.tabla_paquetes.cellWidget(fila, columna)
                dimensiones_paq.append(selector.value())

            columna_min = self.dimensiones
            columna_max = self.dimensiones + 1

            selector_min = self.tabla_paquetes.cellWidget(fila, columna_min)
            selector_max = self.tabla_paquetes.cellWidget(fila, columna_max)

            cantidad_min = selector_min.value()
            cantidad_max = selector_max.value()

            columna_id = self.tabla_paquetes.columnCount() - 1
            item_id = self.tabla_paquetes.item(fila, columna_id)
            id_paquete = item_id.text() if item_id else f"Paquete-{fila + 1}"

            paquete = Paquete(
                nombre=id_paquete,
                dimensiones=tuple(dimensiones_paq),
                cantidad_minima=cantidad_min,
                cantidad_maxima=cantidad_max
            )
            paquetes.append(paquete)

        return paquetes

    def obtener_rotaciones_permitidas(self) -> list[tuple]:
        if self.dimensiones == 1:
            return []

        rotaciones_permitidas = []

        for fila in range(self.tabla_paquetes.rowCount()):
            rotaciones_paquete = []
            columna_rot_inicial = self.dimensiones + 2

            for columna in range(columna_rot_inicial, columna_rot_inicial + len(self.columnas_rotacion)):
                casilla = self.tabla_paquetes.cellWidget(fila, columna)
                rotaciones_paquete.append(casilla.isChecked())

            rotaciones_permitidas.append(tuple(rotaciones_paquete))

        return rotaciones_permitidas

    def limpiar_entradas(self):
        while self.tabla_contenedores.rowCount() > 0:
            self.tabla_contenedores.removeRow(0)
        while self.tabla_paquetes.rowCount() > 0:
            self.tabla_paquetes.removeRow(0)