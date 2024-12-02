from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QCheckBox
from modelo.datos import RequisitosContenedor, Paquete

class BPGAVista(QMainWindow):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Herramienta de Optimización de Empaquetado Multi-Contenedor")
        self.setGeometry(100, 100, 1000, 800)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tabs = {
            '1D': TabPaquete(1),
            '2D': TabPaquete(2),
            '3D': TabPaquete(3)
        }

        for name, tab in self.tabs.items():
            self.tab_widget.addTab(tab, name)

        button_layout = QHBoxLayout()
        optimize_btn = QPushButton("Optimizar")
        optimize_btn.clicked.connect(self.enviar_datos)
        button_layout.addWidget(optimize_btn)

        clear_btn = QPushButton("Limpiar Todo")
        clear_btn.clicked.connect(self.limpiar_todo)
        button_layout.addWidget(clear_btn)

        main_layout.addLayout(button_layout)

    def enviar_datos(self):
        p_actual = self.tabs[self.tab_widget.tabText(self.tab_widget.currentIndex())]


        containers = p_actual.get_contenedores()
        packages = p_actual.get_paquetes()
        rotation_permissions = p_actual.get_rotaciones_permitidas()

        self.controlador.solicitud(containers,packages,rotation_permissions)


    def limpiar_todo(self):
        current_tab = self.tabs[self.tab_widget.tabText(self.tab_widget.currentIndex())]
        current_tab.limpiar_entradas()

class TabPaquete(QWidget):
    def __init__(self, dimensions):
        super().__init__()
        self.dimensions = dimensions
        self.container_counter = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Sección de Contenedores
        containers_group = QWidget()
        containers_layout = QVBoxLayout()
        containers_group.setLayout(containers_layout)

        containers_label = QLabel("Contenedores:")
        containers_layout.addWidget(containers_label)

        self.containers_table = QTableWidget()
        self.containers_table.setColumnCount(dimensions + 3)
        headers = ([f"Dimensión {i + 1}" for i in range(dimensions)] +
                   ["Cantidad", "Opcional", "ID"])
        self.containers_table.setHorizontalHeaderLabels(headers)
        containers_layout.addWidget(self.containers_table)

        add_container_btn = QPushButton("Agregar Contenedor")
        add_container_btn.clicked.connect(self.agregar_contenedor)
        containers_layout.addWidget(add_container_btn)

        layout.addWidget(containers_group)

        # Sección de Paquetes con columnas de rotación
        packages_group = QWidget()
        packages_layout = QVBoxLayout()
        packages_group.setLayout(packages_layout)

        packages_label = QLabel("Paquetes:")
        packages_layout.addWidget(packages_label)

        self.packages_table = QTableWidget()

        # Calcular número de columnas de rotación basado en dimensiones
        self.rotation_columns = []
        if dimensions == 2:
            self.rotation_columns = ["Rot XY"]
        elif dimensions == 3:
            self.rotation_columns = ["Rot XY", "Rot XZ", "Rot YZ", "Rot XY-XZ", "Rot XY-YZ"]

        total_columns = (dimensions +  # Dimensiones
                         2 +  # Cantidad Min/Max
                         1 +  # ID
                         len(self.rotation_columns))  # Columnas de rotación

        self.packages_table.setColumnCount(total_columns)

        headers = ([f"Dimensión {i + 1}" for i in range(dimensions)] +
                   ["Cant. Mín", "Cant. Máx"] +
                   self.rotation_columns +
                   ["ID"])

        self.packages_table.setHorizontalHeaderLabels(headers)
        packages_layout.addWidget(self.packages_table)

        add_package_btn = QPushButton("Agregar Paquete")
        add_package_btn.clicked.connect(self.agregar_paquete)
        packages_layout.addWidget(add_package_btn)

        layout.addWidget(packages_group)

    def agregar_contenedor(self):
        row = self.containers_table.rowCount()
        self.containers_table.insertRow(row)

        for col in range(self.dimensions):
            self.containers_table.setItem(row, col, QTableWidgetItem())

        self.containers_table.setItem(row, self.dimensions, QTableWidgetItem('1'))

        optional_check = QCheckBox()
        self.containers_table.setCellWidget(row, self.dimensions + 1, optional_check)

        id_item = QTableWidgetItem(f"Contenedor-{row + 1}")
        self.containers_table.setItem(row, self.dimensions + 2, id_item)

    def agregar_paquete(self):
        row = self.packages_table.rowCount()
        self.packages_table.insertRow(row)

        # Dimensiones
        for col in range(self.dimensions):
            self.packages_table.setItem(row, col, QTableWidgetItem())

        # Cantidades mínima y máxima
        min_qty_col = self.dimensions
        max_qty_col = self.dimensions + 1
        self.packages_table.setItem(row, min_qty_col, QTableWidgetItem('1'))
        self.packages_table.setItem(row, max_qty_col, QTableWidgetItem('1'))

        # Checkboxes de rotación
        current_col = self.dimensions + 2
        for _ in self.rotation_columns:
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.packages_table.setCellWidget(row, current_col, checkbox)
            current_col += 1

        # ID
        id_item = QTableWidgetItem(f"Paquete-{row + 1}")
        self.packages_table.setItem(row, current_col, id_item)

    def get_contenedores(self) -> list[RequisitosContenedor]:
        contenedores = []
        self.container_counter.clear()

        for row in range(self.containers_table.rowCount()):
            dimc = []
            for col in range(self.dimensions):
                item = self.containers_table.item(row, col)
                if not item or not item.text():
                    raise ValueError(f"Contenedor {row + 1} le falta la dimensión {col + 1}")
                dimc.append(int(item.text()))

            qty_item = self.containers_table.item(row, self.dimensions)
            if not qty_item or not qty_item.text():
                raise ValueError(f"Contenedor {row + 1} le falta la cantidad")
            quantity = int(qty_item.text())

            optional_check = self.containers_table.cellWidget(row, self.dimensions + 1)
            is_optional = optional_check.isChecked()

            dim_tuple = tuple(dimc)
            if dim_tuple not in self.container_counter:
                self.container_counter[dim_tuple] = 0

            for i in range(quantity):
                self.container_counter[dim_tuple] += 1
                container_id = f"Contenedor-{row + 1}-{self.container_counter[dim_tuple]}"
                contenedor = RequisitosContenedor(
                    dimensiones=dim_tuple,
                    id=container_id,
                    uso_opcional=is_optional)
                contenedores.append(contenedor)

        return contenedores

    def get_paquetes(self) -> list[Paquete]:
        packages = []
        for row in range(self.packages_table.rowCount()):
            dimc = []
            for col in range(self.dimensions):
                item = self.packages_table.item(row, col)
                if not item or not item.text():
                    raise ValueError(f"Paquete {row + 1} le falta la dimensión {col + 1}")
                dimc.append(int(item.text()))

            min_qty_col = self.dimensions
            max_qty_col = self.dimensions + 1
            min_qty_item = self.packages_table.item(row, min_qty_col)
            max_qty_item = self.packages_table.item(row, max_qty_col)

            if not min_qty_item or not max_qty_item:
                raise ValueError(f"Paquete {row + 1} le falta información de cantidad")

            min_qty = int(min_qty_item.text())
            max_qty = int(max_qty_item.text())

            id_col = self.packages_table.columnCount() - 1
            id_item = self.packages_table.item(row, id_col)
            package_id = id_item.text() if id_item else f"Paquete-{row + 1}"
            paquete = Paquete(
                nombre=package_id,
                dimensiones=tuple(dimc),
                cantidad_minima=min_qty,
                cantidad_maxima=max_qty
            )
            packages.append(paquete)

        return packages

    def get_rotaciones_permitidas(self) -> list[tuple]:
        if self.dimensions == 1:
            return []

        rotaciones_permitidas = []

        for row in range(self.packages_table.rowCount()):
            package_rotations = []
            rot_start_col = self.dimensions + 2

            for col in range(rot_start_col, rot_start_col + len(self.rotation_columns)):
                checkbox = self.packages_table.cellWidget(row, col)
                package_rotations.append(checkbox.isChecked())

            rotaciones_permitidas.append(tuple(package_rotations))

        return rotaciones_permitidas

    def limpiar_entradas(self):
        while self.containers_table.rowCount() > 0:
            self.containers_table.removeRow(0)
        while self.packages_table.rowCount() > 0:
            self.packages_table.removeRow(0)
