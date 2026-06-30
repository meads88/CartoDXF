# -*- coding: utf-8 -*-
"""
cartodxf_dialog.py  —  Diálogo principal del plugin CartoDXF
"""
import traceback

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFileDialog, QListWidget,
    QListWidgetItem, QGroupBox, QComboBox, QCheckBox,
    QDoubleSpinBox, QProgressBar, QMessageBox, QLineEdit,
    QAbstractItemView, QWidget,
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QUrl, QSettings
from qgis.PyQt.QtGui import QDesktopServices

from qgis.core import QgsProject, QgsMapLayerType


# ─────────────────────────────────────────────────────────────────────────────
#  Tema claro / oscuro (mismo sistema que ProfileMaster, para mantener una
#  identidad visual unificada entre los plugins de este autor)
# ─────────────────────────────────────────────────────────────────────────────

_THEMES = {
    'dark': dict(
        bg='#22232e', panel='#2b2d3a', border='#454860', fg='#e8e9f0',
        fg_disabled='#6b6e80',
        field_bg='#1b1c25', field_fg='#f0f1f6',
        field_bg_disabled='#262833', field_fg_disabled='#6b6e80',
        tab_bg='#262834', accent='#2471A3', muted='#a4a7bd', warn='#ff7a6b',
        button_bg='#343750', button_bg_hover='#3d4060', theme_btn_bg='#343750',
        check_border='#8489a8', header_bg='#262834',
    ),
    'light': dict(
        bg='#f4f4f8', panel='#ffffff', border='#c7c9d6', fg='#1c1d27',
        fg_disabled='#9a9cab',
        field_bg='#ffffff', field_fg='#1c1d27',
        field_bg_disabled='#ececf2', field_fg_disabled='#9a9cab',
        tab_bg='#e7e8ef', accent='#1A5276', muted='#5b5d6c', warn='#c0392b',
        button_bg='#e9e9f0', button_bg_hover='#dadce6', theme_btn_bg='#e9e9f0',
        check_border='#6b6e80', header_bg='#e7e8ef',
    ),
}

_QSS_TEMPLATE = """
QWidget {{
    background: {bg};
    color: {fg};
    font-size: 9pt;
}}
QDialog {{ background: {bg}; }}
QGroupBox {{
    font-weight: bold;
    border: 1px solid {border};
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 6px;
    background: {panel};
    color: {fg};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {fg};
}}
QGroupBox:disabled {{ color: {fg_disabled}; }}
QLabel {{ background: transparent; color: {fg}; }}
QCheckBox {{ background: transparent; color: {fg}; spacing: 6px; }}
QCheckBox:disabled {{ color: {fg_disabled}; }}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1.5px solid {check_border};
    border-radius: 3px;
    background: {field_bg};
}}
QCheckBox::indicator:hover {{
    border: 1.5px solid {accent};
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border: 1.5px solid {accent};
}}
QCheckBox::indicator:checked:hover {{
    background: {accent};
    border: 1.5px solid {check_border};
}}
QCheckBox::indicator:disabled {{
    background: {field_bg_disabled};
    border: 1.5px solid {border};
}}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    padding: 2px 4px;
    border: 1px solid {border};
    border-radius: 3px;
    background: {field_bg};
    color: {field_fg};
}}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
    background: {field_bg_disabled};
    color: {field_fg_disabled};
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}
QComboBox::drop-down {{
    border: none;
    width: 18px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {fg};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background: {field_bg};
    color: {field_fg};
    border: 1px solid {border};
    selection-background-color: {accent};
    selection-color: white;
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid {border};
    border-bottom: 1px solid {border};
    border-top-right-radius: 3px;
    background: {button_bg};
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid {border};
    border-top: 1px solid {border};
    border-bottom-right-radius: 3px;
    background: {button_bg};
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {button_bg_hover};
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {fg};
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {fg};
}}
QSpinBox::up-arrow:disabled, QDoubleSpinBox::up-arrow:disabled,
QSpinBox::down-arrow:disabled, QDoubleSpinBox::down-arrow:disabled {{
    border-bottom-color: {fg_disabled};
    border-top-color: {fg_disabled};
}}
QPushButton {{
    background: {button_bg};
    color: {fg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 5px 12px;
}}
QPushButton:hover {{ background: {button_bg_hover}; }}
QPushButton:disabled {{ background: {border}; color: {fg_disabled}; }}
QPushButton#btn_run {{
    background: #1A5276;
    color: white;
    font-weight: bold;
    padding: 8px 22px;
    border-radius: 5px;
    font-size: 10pt;
    border: none;
}}
QPushButton#btn_run:hover {{ background: #2471A3; }}
QPushButton#btn_run:disabled {{ background: {border}; color: {fg_disabled}; }}
QPushButton#btn_donate {{
    background: #E67E22;
    color: white;
    font-weight: bold;
    padding: 8px 14px;
    border-radius: 5px;
    font-size: 9pt;
    border: none;
}}
QPushButton#btn_donate:hover {{ background: #CA6F1E; }}
QPushButton#btn_close {{
    padding: 8px 16px;
    border-radius: 5px;
    font-size: 10pt;
}}
QPushButton#btn_theme {{
    padding: 5px 12px;
    border-radius: 14px;
    font-size: 9pt;
    background: {theme_btn_bg};
    border: 1px solid {border};
    color: {fg};
}}
QPushButton#btn_theme:hover {{ background: {button_bg_hover}; }}
QProgressBar {{
    border: 1px solid {border};
    border-radius: 4px;
    text-align: center;
    height: 18px;
    background: {field_bg};
    color: {fg};
}}
QProgressBar::chunk {{ background: #2471A3; border-radius: 3px; }}
QLabel#lbl_title {{
    font-size: 13pt;
    font-weight: bold;
    padding: 4px 0;
    color: {fg};
}}
QLabel#lbl_info {{
    font-size: 8pt;
    color: {muted};
}}
QLabel#lbl_header {{
    font-size: 8pt;
    font-weight: bold;
    color: {muted};
    background: {header_bg};
    padding: 4px;
}}
QListWidget {{
    background: {panel};
    border: 1px solid {border};
    border-radius: 3px;
}}
QListWidget::item {{
    border-bottom: 1px solid {border};
}}
"""


def _build_stylesheet(theme):
    colors = _THEMES.get(theme, _THEMES['dark'])
    return _QSS_TEMPLATE.format(**colors)


class ExportWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            from .dxf_exporter import DXFExporter

            p = self.params
            exporter = DXFExporter(
                output_path=p['output_path'],
                target_crs=p.get('target_crs'),
                progress_cb=lambda v, msg: self.progress.emit(v, msg),
            )

            layers = p['layers']
            for i, item in enumerate(layers):
                self.progress.emit(
                    int(i / len(layers) * 95),
                    f"Exportando capa {i + 1}/{len(layers)}: {item['layer'].name()}"
                )
                exporter.add_layer(
                    qgis_layer=item['layer'],
                    category_field=item.get('category_field'),
                    label_field=item.get('label_field'),
                    label_height=p.get('label_height', 2.0),
                    export_labels=p.get('export_labels', True),
                    export_hatch=p.get('export_hatch', True),
                    export_symbol_block=p.get('export_symbol_block', False),
                    symbol_size=p.get('symbol_size', 1.0),
                    outline_uses_fill_color=p.get('outline_uses_fill_color', True),
                )

            self.progress.emit(97, 'Guardando archivo DXF…')
            exporter.save()
            self.progress.emit(100, 'Exportación completada.')
            self.finished.emit(p['output_path'])

        except Exception as e:
            self.error.emit(f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}")


class LayerConfigWidget(QWidget):
    """Widget de configuración por capa."""

    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # Nombre de la capa
        lbl = QLabel(self.layer.name())
        lbl.setMinimumWidth(90)
        lbl.setMaximumWidth(180)
        lbl.setToolTip(self.layer.source())
        layout.addWidget(lbl)

        # Campo de categoría → define el NOMBRE DE LA CAPA DXF resultante.
        layout.addWidget(QLabel('Capa DXF:'))
        self.combo_cat = QComboBox()
        self.combo_cat.setMinimumWidth(120)
        self.combo_cat.setToolTip(
            'Determina el nombre de la capa DXF que se creará.\n'
            '"(nombre de capa)" usa el nombre de esta capa de QGIS tal cual.\n'
            'Si eliges un campo, cada valor distinto de ese campo genera\n'
            'su propia capa DXF (p.ej. una capa por cada tipo de vía).'
        )
        self.combo_cat.addItem('(nombre de capa)', None)
        for field in self.layer.fields():
            self.combo_cat.addItem(field.name(), field.name())
        # Autodetectar campo "layer" o "LAYER"
        for i in range(self.combo_cat.count()):
            if self.combo_cat.itemText(i).lower() == 'layer':
                self.combo_cat.setCurrentIndex(i)
                break
        layout.addWidget(self.combo_cat)

        # Campo de etiqueta → texto DXF que se escribe junto a cada entidad.
        layout.addWidget(QLabel('Texto/etiqueta:'))
        self.combo_lbl = QComboBox()
        self.combo_lbl.setMinimumWidth(120)
        self.combo_lbl.setToolTip(
            'Campo cuyo valor se escribe como texto (entidad TEXT) en el\n'
            'DXF, junto al centroide de cada elemento. Es independiente\n'
            'de "Capa DXF": puedes usar el mismo campo en ambos, campos\n'
            'distintos, o dejar esta opción en "(sin etiqueta)" si solo\n'
            'quieres organizar capas sin escribir ningún rótulo.'
        )
        self.combo_lbl.addItem('(sin etiqueta)', None)
        for field in self.layer.fields():
            self.combo_lbl.addItem(field.name(), field.name())
        # Autodetectar campo de etiqueta activo en QGIS
        if self.layer.labelsEnabled():
            lbl_field = self.layer.labeling().settings().fieldName if self.layer.labeling() else ''
            for i in range(self.combo_lbl.count()):
                if self.combo_lbl.itemText(i) == lbl_field:
                    self.combo_lbl.setCurrentIndex(i)
                    break
        layout.addWidget(self.combo_lbl)
        layout.addStretch()

    def category_field(self):
        return self.combo_cat.currentData()

    def label_field(self):
        return self.combo_lbl.currentData()


class CartoDXFDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface = iface
        self.worker = None
        self.layer_widgets = {}  # layer_id → LayerConfigWidget

        self._settings = QSettings()
        saved_theme = self._settings.value("CartoDXF/theme", None)
        if saved_theme in ('dark', 'light'):
            self._theme = saved_theme
        else:
            bg_lightness = self.palette().window().color().lightness()
            self._theme = 'dark' if bg_lightness < 128 else 'light'

        self.setWindowTitle('CartoDXF')
        self.setMinimumSize(780, 600)
        self._build_ui()
        self._load_layers()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setSpacing(8)
        main.setContentsMargins(12, 12, 12, 12)

        self.setStyleSheet(_build_stylesheet(self._theme))

        # ── Cabecera ──────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        title = QLabel('🗂️  CartoDXF')
        title.setObjectName('lbl_title')
        header_row.addWidget(title)
        header_row.addStretch()

        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName('btn_theme')
        self.btn_theme.clicked.connect(self._toggle_theme)
        header_row.addWidget(self.btn_theme)
        main.addLayout(header_row)

        sub = QLabel('Exporta capas de QGIS a DXF, una capa DXF por categoría')
        sub.setObjectName('lbl_info')
        main.addWidget(sub)

        # ── Grupo de capas ────────────────────────────────────────────────
        grp_layers = QGroupBox('Capas a exportar')
        grp_layout = QVBoxLayout(grp_layers)

        # Botones selección
        sel_row = QHBoxLayout()
        btn_all = QPushButton('Seleccionar todas')
        btn_all.clicked.connect(self._select_all)
        btn_none = QPushButton('Deseleccionar todas')
        btn_none.clicked.connect(self._select_none)
        sel_row.addWidget(btn_all)
        sel_row.addWidget(btn_none)
        sel_row.addStretch()
        grp_layout.addLayout(sel_row)

        # Cabecera
        hdr = QLabel('  ☑  Capa                                    '
                     'Capa DXF                       Texto/etiqueta')
        hdr.setObjectName('lbl_header')
        grp_layout.addWidget(hdr)

        # Lista de capas
        self.list_layers = QListWidget()
        self.list_layers.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_layers.setMinimumHeight(220)
        grp_layout.addWidget(self.list_layers)

        main.addWidget(grp_layers)

        # ── Opciones generales ────────────────────────────────────────────
        grp_opts = QGroupBox('Opciones')
        opts_grid = QGridLayout(grp_opts)
        opts_grid.setSpacing(6)

        self.chk_labels = QCheckBox('Exportar etiquetas como texto DXF')
        self.chk_labels.setChecked(True)
        opts_grid.addWidget(self.chk_labels, 0, 0, 1, 2)

        self.chk_hatch = QCheckBox('Exportar relleno de polígonos (hatch)')
        self.chk_hatch.setChecked(True)
        self.chk_hatch.setToolTip(
            'Activo: exporta relleno sólido (hatch) en áreas.\n'
            'Inactivo: exporta solo los contornos cerrados.'
        )
        opts_grid.addWidget(self.chk_hatch, 1, 0, 1, 2)

        self.chk_outline_fill = QCheckBox('Usar el color de relleno también en el contorno de los polígonos')
        self.chk_outline_fill.setChecked(True)
        self.chk_outline_fill.setToolTip(
            'En un renderer "Categorizado" con colores aleatorios, normalmente\n'
            'solo varía el RELLENO; el borde se queda en el gris por defecto\n'
            'de QGIS, igual en todas las categorías. En AutoCAD ese borde es\n'
            'lo que más se ve, así que esta opción (activa por defecto) hace\n'
            'que el contorno tome el mismo color que el relleno de su categoría.\n'
            'Desactívala si tu estilo usa un color de borde distinto a propósito.'
        )
        opts_grid.addWidget(self.chk_outline_fill, 2, 0, 1, 2)

        self.chk_symbol_block = QCheckBox('Exportar también el símbolo de QGIS como bloque DXF (en puntos)')
        self.chk_symbol_block.setChecked(False)
        self.chk_symbol_block.setToolTip(
            'Además del punto (entidad POINT), inserta un bloque (INSERT) con\n'
            'una aproximación del símbolo de QGIS: círculo, cuadrado, triángulo,\n'
            'diamante, cruz, X, estrella, pentágono o hexágono según la forma\n'
            'configurada en "Marcador simple". Si el símbolo es un icono SVG o\n'
            'una imagen, se usa un círculo como aproximación genérica, ya que\n'
            'no es posible convertir un icono arbitrario a geometría DXF.'
        )
        self.chk_symbol_block.toggled.connect(self._toggle_symbol_size)
        opts_grid.addWidget(self.chk_symbol_block, 3, 0, 1, 2)

        self.lbl_symbol_size = QLabel('Tamaño del bloque (unid. del mapa):')
        self.lbl_symbol_size.setEnabled(False)
        opts_grid.addWidget(self.lbl_symbol_size, 4, 0)
        self.spin_symbol_size = QDoubleSpinBox()
        self.spin_symbol_size.setRange(0.001, 100000.0)
        self.spin_symbol_size.setDecimals(3)
        self.spin_symbol_size.setValue(1.0)
        self.spin_symbol_size.setSingleStep(0.1)
        self.spin_symbol_size.setEnabled(False)
        self.spin_symbol_size.setToolTip(
            'El tamaño del símbolo en QGIS está en mm/px de pantalla y no\n'
            'corresponde a ninguna medida real sobre el terreno, así que aquí\n'
            'se indica directamente el tamaño (diámetro) que debe tener el\n'
            'bloque en las unidades del mapa (p.ej. metros).'
        )
        opts_grid.addWidget(self.spin_symbol_size, 4, 1)

        opts_grid.addWidget(QLabel('Altura texto (m):'), 5, 0)
        self.spin_lbl_h = QDoubleSpinBox()
        self.spin_lbl_h.setRange(0.1, 100.0)
        self.spin_lbl_h.setValue(2.0)
        self.spin_lbl_h.setSingleStep(0.5)
        opts_grid.addWidget(self.spin_lbl_h, 5, 1)

        self.chk_reproject = QCheckBox('Reproyectar al CRS del proyecto')
        self.chk_reproject.setChecked(True)
        opts_grid.addWidget(self.chk_reproject, 6, 0, 1, 2)

        main.addWidget(grp_opts)

        # ── Archivo de salida ─────────────────────────────────────────────
        grp_out = QGroupBox('Archivo de salida')
        out_row = QHBoxLayout(grp_out)
        self.edit_output = QLineEdit()
        self.edit_output.setPlaceholderText('Selecciona la ruta del archivo DXF…')
        btn_browse = QPushButton('…')
        btn_browse.setMaximumWidth(32)
        btn_browse.clicked.connect(self._browse_output)
        out_row.addWidget(self.edit_output)
        out_row.addWidget(btn_browse)
        main.addWidget(grp_out)

        # ── Progreso ──────────────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main.addWidget(self.progress)

        self.lbl_status = QLabel('Listo.')
        self.lbl_status.setObjectName('lbl_info')
        main.addWidget(self.lbl_status)

        # ── Botones ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()

        self.btn_export = QPushButton('▶  Exportar DXF')
        self.btn_export.setObjectName('btn_run')
        self.btn_export.clicked.connect(self._run_export)
        btn_row.addWidget(self.btn_export)

        btn_row.addStretch()

        btn_donate = QPushButton('☕  Invítame a un café')
        btn_donate.setObjectName('btn_donate')
        btn_donate.setToolTip('Si este plugin te resulta útil, apoya su desarrollo.')
        btn_donate.clicked.connect(self._open_donate)
        btn_row.addWidget(btn_donate)

        btn_close = QPushButton('Cerrar')
        btn_close.setObjectName('btn_close')
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        main.addLayout(btn_row)

        self._update_theme_button()

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._theme = 'light' if self._theme == 'dark' else 'dark'
        self.setStyleSheet(_build_stylesheet(self._theme))
        self._settings.setValue("CartoDXF/theme", self._theme)
        self._update_theme_button()

    def _update_theme_button(self):
        if self._theme == 'dark':
            self.btn_theme.setText("☀️  Modo claro")
            self.btn_theme.setToolTip("Cambiar a modo claro (fondos claros, textos oscuros)")
        else:
            self.btn_theme.setText("🌙  Modo oscuro")
            self.btn_theme.setToolTip("Cambiar a modo oscuro (fondos oscuros, textos claros)")

    # ── Carga de capas ────────────────────────────────────────────────────────

    def _load_layers(self):
        self.list_layers.clear()
        self.layer_widgets.clear()

        layers = QgsProject.instance().mapLayers().values()
        vector_layers = [lyr for lyr in layers if lyr.type() == QgsMapLayerType.VectorLayer]

        for layer in vector_layers:
            item = QListWidgetItem()
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, layer.id())

            widget = LayerConfigWidget(layer)
            self.layer_widgets[layer.id()] = widget

            item.setSizeHint(widget.sizeHint())
            self.list_layers.addItem(item)
            self.list_layers.setItemWidget(item, widget)

    # ── Selección de capas ────────────────────────────────────────────────────

    def _select_all(self):
        for i in range(self.list_layers.count()):
            self.list_layers.item(i).setCheckState(Qt.CheckState.Checked)

    def _select_none(self):
        for i in range(self.list_layers.count()):
            self.list_layers.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _toggle_symbol_size(self, checked):
        self.lbl_symbol_size.setEnabled(checked)
        self.spin_symbol_size.setEnabled(checked)

    # ── Archivo salida ────────────────────────────────────────────────────────

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Guardar DXF', '', 'Archivos DXF (*.dxf)'
        )
        if path:
            if not path.lower().endswith('.dxf'):
                path += '.dxf'
            self.edit_output.setText(path)

    # ── Exportación ───────────────────────────────────────────────────────────

    def _run_export(self):
        output_path = self.edit_output.text().strip()
        if not output_path:
            QMessageBox.warning(self, 'Aviso', 'Selecciona un archivo de salida.')
            return

        # Capas seleccionadas
        selected_layers = []
        for i in range(self.list_layers.count()):
            item = self.list_layers.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                layer_id = item.data(Qt.ItemDataRole.UserRole)
                layer = QgsProject.instance().mapLayer(layer_id)
                widget = self.layer_widgets.get(layer_id)
                if layer and widget:
                    selected_layers.append({
                        'layer': layer,
                        'category_field': widget.category_field(),
                        'label_field': widget.label_field(),
                    })

        if not selected_layers:
            QMessageBox.warning(self, 'Aviso', 'Selecciona al menos una capa.')
            return

        # CRS destino
        target_crs = None
        if self.chk_reproject.isChecked():
            target_crs = QgsProject.instance().crs()

        params = {
            'output_path': output_path,
            'layers': selected_layers,
            'target_crs': target_crs,
            'export_labels': self.chk_labels.isChecked(),
            'export_hatch': self.chk_hatch.isChecked(),
            'outline_uses_fill_color': self.chk_outline_fill.isChecked(),
            'export_symbol_block': self.chk_symbol_block.isChecked(),
            'symbol_size': self.spin_symbol_size.value(),
            'label_height': self.spin_lbl_h.value(),
        }

        self.btn_export.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        self.worker = ExportWorker(params)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, value, msg):
        self.progress.setValue(value)
        self.lbl_status.setText(msg)

    def _on_finished(self, path):
        self.btn_export.setEnabled(True)
        self.lbl_status.setText(f'✅ Exportado: {path}')
        QMessageBox.information(
            self, 'Exportación completada',
            f'Archivo DXF generado correctamente:\n{path}'
        )

    def _on_error(self, msg):
        self.btn_export.setEnabled(True)
        self.progress.setVisible(False)
        self.lbl_status.setText('❌ Error en la exportación')
        QMessageBox.critical(self, 'Error', msg)

    # ── Donativo ──────────────────────────────────────────────────────────────

    def _open_donate(self):
        QDesktopServices.openUrl(
            QUrl('https://www.paypal.com/donate/?hosted_button_id=UF9SYUY42GWTG')
        )
