from __future__ import annotations
from html import escape
import argparse
import sys
from pathlib import Path
from . import __version__
from .qt import *
from .core import (CATALOG, RESOURCES, MODES, Hardware, Config, Selection,
                   detect_hardware, compatible, generate, preset, smooth_driver_supported, epic_arguments)
from .explanations import explain_result

STYLE = """
* { font-family: 'Inter', 'Noto Sans', sans-serif; font-size: 13px; }
QMainWindow, QWidget#root { background: #101419; color: #e7edf3; }
QWidget { color: #e7edf3; }
QFrame#sidebar { background: #151c23; border-right: 1px solid #29323c; }
QFrame#card { background: #19212a; border: 1px solid #303c48; border-radius: 12px; }
QLabel#brand { font-size: 22px; font-weight: 800; letter-spacing: 1px; color: #a8edb1; }
QLabel#title { font-size: 26px; font-weight: 750; }
QLabel#subtitle, QLabel#muted { color: #9eafbd; }
QLabel#eyebrow { color: #89cba1; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#section { font-size: 15px; font-weight: 700; }
QLabel#badge { background: #203b32; color: #a7ebbf; border-radius: 7px; padding: 6px 10px; font-weight: 650; }
QLabel#amber { background: #3a3021; color: #f2c983; border-radius: 6px; padding: 7px; }
QPushButton { background: #273440; border: 1px solid #3b4c5b; border-radius: 7px; padding: 8px 14px; font-weight: 600; }
QPushButton:hover { background: #334656; border-color: #759c8b; }
QPushButton:pressed { background: #415b50; }
QPushButton:disabled { color: #73818b; background: #202932; border-color: #303a43; }
QPushButton#primary { background: #b5ed9b; color: #152017; border: 0; padding: 10px 20px; }
QPushButton#primary:hover { background: #cef8bb; }
QPushButton#primary:disabled { background: #34483b; color: #7a9382; }
QPushButton#nav { text-align: left; background: transparent; border: 0; padding: 12px; color: #a9b8c5; }
QPushButton#nav:checked { background: #263b32; color: #b6edba; border-radius: 8px; }
QComboBox, QLineEdit, QSpinBox { background: #11191f; border: 1px solid #3a4856; border-radius: 6px; padding: 7px; min-height: 20px; }
QComboBox:hover, QLineEdit:focus { border-color: #a0d890; }
QComboBox QAbstractItemView { background: #1d2933; selection-background-color: #365348; color: #e7edf3; padding: 6px; }
QComboBox::drop-down { border: 0; width: 22px; }
QPlainTextEdit, QTextBrowser { background: #11191f; border: 1px solid #303d49; border-radius: 8px; padding: 10px; color: #dce8ed; }
QPlainTextEdit#command { color: #c6f2aa; font-family: 'DejaVu Sans Mono', monospace; font-size: 12px; }
QTextBrowser#detail { background: #19212a; border: 0; padding: 4px; }
QTabWidget::pane { border: 1px solid #303c48; border-radius: 8px; background: #19212a; }
QTabBar::tab { background: #171f27; color: #95a8b8; padding: 11px 15px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #b8edac; border-bottom: 2px solid #b8edac; background: #1d2b2b; }
QCheckBox { spacing: 8px; color: #b0c0ca; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #536775; border-radius: 4px; background: #11191f; }
QCheckBox::indicator:checked { background: #a7dd99; border-color: #a7dd99; image: none; }
QScrollArea { border: 0; background: transparent; }
QScrollBar:vertical { background: #141b22; width: 9px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #41505c; min-height: 24px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip { background: #23333e; color: #ecf4f6; border: 1px solid #567266; padding: 6px; }
QStatusBar { color: #92a6b4; background: #111820; }
"""

def label(text="", name=None, wrap=False):
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    w.setWordWrap(wrap)
    return w

def combo(items):
    w = QComboBox()
    for key, text in items:
        w.addItem(text, key)
    w.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    w.setMinimumContentsLength(12)
    return w

def pick(w, key):
    # Compare Python values: QVariant may use identity for tuples.
    for idx in range(w.count()):
        if w.itemData(idx) == key:
            w.setCurrentIndex(idx)
            return

def html(body):
    return """<html><head><style>
    body { color: #d3dfe7; font-size: 13px; }
    h2 { font-size: 21px; color: #edf5f8; margin-top: 5px; }
    h3 { font-size: 14px; color: #b6e5aa; margin-bottom: 4px; margin-top: 15px; }
    p, li { line-height: 150%; } a { color: #a9d8b7; }
    .muted { color: #92a7b7; } code { color: #c0e5b0; }
    </style></head><body>""" + body + "</body></html>"

def browser():
    w = QTextBrowser()
    w.setOpenExternalLinks(True)
    w.setObjectName("detail")
    return w

def card():
    frame = QFrame()
    frame.setObjectName("card")
    return frame

class TechPanel(QWidget):
    def __init__(self, tech, changed):
        super().__init__()
        self.tech = tech
        self.changed = changed
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(22)
        controls = QWidget()
        controls.setMaximumWidth(410)
        controls.setMinimumWidth(310)
        form = QVBoxLayout(controls)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)
        form.addWidget(label("MODELO / PRESET", "eyebrow"))
        self.models = QComboBox()
        self.models.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.models.setMinimumContentsLength(15)
        self.models.setAccessibleName("Preset " + tech.upper())
        form.addWidget(self.models)
        self.generation = label("", "badge", True)
        self.generation.setAccessibleName("Generación DLSS del preset")
        form.addWidget(self.generation)
        self.mode = None
        if tech in ("sr", "rr"):
            form.addSpacing(6)
            form.addWidget(label("MODO DE CALIDAD · INDEPENDIENTE DEL PRESET", "eyebrow", True))
            self.mode = combo(MODES.items())
            self.mode.setAccessibleName("Modo de calidad " + tech.upper())
            form.addWidget(self.mode)
            self.custom_scale = QSpinBox()
            self.custom_scale.setRange(33, 100)
            self.custom_scale.setValue(67)
            self.custom_scale.setSuffix(" % · escala interna")
            self.custom_scale.setToolTip("Porcentaje de escala interna solicitado al runtime DLSS. No cambia la resolución de salida.")
            self.custom_scale.valueChanged.connect(changed)
            form.addWidget(self.custom_scale)
            self.scale = label("", "muted", True)
            form.addWidget(self.scale)
            self.mode.currentIndexChanged.connect(changed)
        else:
            form.addWidget(label("GENERACIÓN DE FOTOGRAMAS", "eyebrow"))
            self.fg_mode = combo([("game", "Controlado por el juego"), ("on", "Activar FG / MFG · multiplicador fijo"),
                                  ("dynamic", "DLSS 4.5 · MFG dinámico"), ("off", "Desactivar FG")])
            form.addWidget(self.fg_mode)
            row = QHBoxLayout()
            self.multiplier = combo([(i, f"{i}× · {i-1} generado(s)") for i in range(2, 7)])
            row.addWidget(self.multiplier)
            self.target = QSpinBox()
            self.target.setRange(30, 1000)
            self.target.setValue(144)
            self.target.setSuffix(" FPS")
            row.addWidget(self.target)
            form.addLayout(row)
            form.addWidget(label("En modo dinámico, el multiplicador es el límite máximo; "
                                 "el objetivo FPS no equivale a FPS medidos.", "muted", True))
            for w in (self.fg_mode, self.multiplier):
                w.currentIndexChanged.connect(changed)
            self.target.valueChanged.connect(changed)
        self.availability = label("", "muted", True)
        form.addSpacing(6)
        form.addWidget(self.availability)
        form.addStretch()
        self.description = browser()
        outer.addWidget(controls, 4)
        outer.addWidget(self.description, 6)
        self.models.currentIndexChanged.connect(changed)
        self.populate(False, "K" if tech == "sr" else "game")

    def populate(self, advanced, selected=None):
        key = selected or self.models.currentData() or "game"
        self.models.blockSignals(True)
        self.models.clear()
        for model in CATALOG["technologies"][self.tech]["presets"]:
            if model["advanced"] and not advanced:
                continue
            model_key = model["id"]
            title = (model["title"] if model_key in ("game", "latest") else
                     f'{model_key} · {model["generation_label"]}')
            self.models.addItem(title, model_key)
            self.models.setItemData(self.models.count() - 1, model["title"], Qt.ItemDataRole.ToolTipRole)
        pick(self.models, key)
        self.models.blockSignals(False)

    def update_info(self, gpu, api="dxvk"):
        item = preset(self.tech, self.models.currentData() or "game")
        generation = item["generation_label"]
        feature = ""
        if self.tech == "fg":
            mode = self.fg_mode.currentData()
            if mode == "dynamic":
                feature = "DLSS 4.5 · Multi Frame Generation dinámico"
            elif mode == "on":
                feature = ("DLSS 4+ · Multi Frame Generation" if self.multiplier.currentData() > 2
                           else "DLSS 3+ · Frame Generation 2×")
        self.generation.setText(feature or generation)
        self.generation.setToolTip(item["generation"])
        self.description.setHtml(html(
            f'<h2>{escape(item["title"])}</h2>'
            f'<p><b>{escape(item["generation"])}</b></p>'
            + (f'<p>{escape(feature)}. Es la generación de la función, no una versión exacta del preset.</p>'
               if feature else "") +
            f'<p>{escape(item["description"])}</p>'
            f'<h3>Cuándo utilizarlo</h3><p>{escape(item["recommendation"])}</p>'
            f'<h3>Impacto en rendimiento</h3><p>{escape(item["cost"])}</p>'))
        ok = compatible(self.tech, gpu) and api not in ("opengl", "native_vulkan")
        for idx in range(self.models.count()):
            self.models.model().item(idx).setEnabled(self.models.itemData(idx) == "game" or ok)
        if self.mode is not None:
            for idx in range(self.mode.count()):
                self.mode.model().item(idx).setEnabled(self.mode.itemData(idx) == "game" or ok)
        self.availability.setText(("Compatible con tu GPU. " if ok else "No compatible con tu GPU. ") +
                                  CATALOG["technologies"][self.tech]["minimum"])
        if self.tech == "fg":
            for idx in range(self.fg_mode.count()):
                mode = self.fg_mode.itemData(idx)
                enabled = mode == "game" or (ok and (mode != "dynamic" or gpu == "rtx50"))
                self.fg_mode.model().item(idx).setEnabled(enabled)
            mode = self.fg_mode.currentData()
            self.multiplier.setEnabled(ok and mode in ("on", "dynamic"))
            for idx in range(self.multiplier.count()):
                self.multiplier.model().item(idx).setEnabled(gpu == "rtx50" or self.multiplier.itemData(idx) == 2)
            self.target.setEnabled(ok and mode == "dynamic")
        else:
            self.custom_scale.setVisible(self.mode.currentData() == "custom")
            self.scale.setText("Calidad prioriza detalle; Rendimiento prioriza FPS. "
                               "El preset cambia el modelo, no la resolución del juego.")

class LinuxPanel(QWidget):
    """API-specific controls, kept separate from the DLSS model selectors."""
    def __init__(self, changed):
        super().__init__()
        layout = QGridLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setHorizontalSpacing(28)
        self.controls = {}
        self.rows = {}
        choices = [("game", "Controlado por el juego"), ("on", "Activar"), ("off", "Desactivar")]
        definitions = [
            ("smooth", "Smooth Motion · Vulkan · RTX 40/50", choices,
             "Interpolación del controlador. RTX 50: 580.65.06+; RTX 40: 580.95.05+. VK_LAYER_NV_present y juego Vulkan x86_64. No combinar con FG."),
            ("smooth_queue", "Smooth Motion · compatibilidad de overlays", None,
             "Presenta desde la cola gráfica; puede reducir el rendimiento. Solo con Smooth Motion activo."),
            ("sharpen", "Nitidez NVIDIA · OpenGL / Vulkan · R595+", choices,
             "Filtro del controlador; no activa NIS ni cambia la resolución. Soporte documentado con R595+."),
            ("sharpen_value", "Intensidad de nitidez · 0–100", (0, 100, 50), "50 = valor predeterminado del controlador."),
            ("film_grain", "Reducción de grano · 0–100", (0, 100, 17), "17 = valor predeterminado del controlador."),
            ("reflex", "Puente Reflex · Windows / Vulkan", None,
             "Requiere capa DXVK-NVAPI Reflex e integración en el juego. En DirectX no se necesita este puente."),
            ("low_latency", "Reducción de latencia · DXVK", choices,
             "Heurística de DXVK reciente, no equivale a forzar Reflex. Puede interferir con limitadores."),
            ("fps", "Límite FPS · DXVK / VKD3D-Proton", (0, 1000, 0),
             "0 = no añadir override. Limita FPS renderizados, no los fotogramas interpolados."),
            ("vsync", "Sincronización vertical · DXVK / OpenGL", choices,
             "No fuerza VSync en DirectX 12 ni en Vulkan nativo. El compositor también decide."),
            ("anisotropy", "Filtrado anisotrópico · DXVK / OpenGL", [(-1,"Controlado por el juego"),(0,"Desactivar"),(2,"2×"),(4,"4×"),(8,"8×"),(16,"16×")],
             "Puede afectar pases que requieren filtrado bilineal; no se aplica a DX12/Vulkan directo."),
            ("lod_bias", "Detalle de texturas (LOD bias) · DXVK", [("game","Controlado por el juego")]+[(x,x) for x in ("-2.0","-1.0","-0.5","0.0","0.5","1.0")],
             "Valores negativos aumentan detalle y parpadeo; positivos reducen detalle. No es un filtro Freestyle."),
            ("api_osd", "Indicador gráfico NVIDIA · OpenGL / Vulkan", None,
             "Muestra API, FPS y presentación. No es el indicador del modelo DLSS."),
            ("indicator", "Indicadores DLSS · Proton / Vulkan nativo", choices,
             "Proton: persisten en el registro Wine; ejecuta Desactivar una vez. Vulkan nativo: indicador temporal de SR."),
            ("gl_vrr", "Permitir G-SYNC / VRR · OpenGL", choices,
             "Necesita pantalla y sesión VRR configuradas. No activa G-SYNC en el compositor."),
            ("gl_threaded", "Optimizaciones multihilo · OpenGL", choices,
             "Puede beneficiar juegos limitados por CPU o empeorar su rendimiento. No afecta a Vulkan."),
            ("gl_cache", "Caché de shaders del driver · OpenGL", choices,
             "No borra ni cambia la caché global; no modifica la precaché de Steam."),
            ("gl_fxaa", "Permitir FXAA del perfil · OpenGL", choices,
             "Solo permite o impide FXAA previamente habilitado en un perfil del driver; no lo activa por sí solo."),
        ]
        for index, (key, title, items, tip) in enumerate(definitions):
            row = QWidget()
            form = QVBoxLayout(row)
            form.setContentsMargins(0, 2, 0, 6)
            form.setSpacing(4)
            caption = label(title, "muted", True)
            if items is None:
                widget = QCheckBox(title)
                form.addWidget(widget)
                widget.toggled.connect(changed)
            elif isinstance(items, tuple):
                form.addWidget(caption)
                widget = QSpinBox()
                widget.setRange(items[0], items[1])
                widget.setValue(items[2])
                if key == "fps":widget.setSpecialValueText("Sin override")
                form.addWidget(widget)
                widget.valueChanged.connect(changed)
            else:
                form.addWidget(caption)
                widget = combo(items)
                form.addWidget(widget)
                widget.currentIndexChanged.connect(changed)
            widget.setToolTip(tip)
            widget.setAccessibleName(title)
            self.controls[key] = widget
            self.rows[key] = row
            layout.addWidget(row, index // 2, index % 2)
        layout.setRowStretch(12, 1)

    def values(self):
        return {key: (w.isChecked() if isinstance(w, QCheckBox) else
                      w.value() if isinstance(w, QSpinBox) else w.currentData())
                for key, w in self.controls.items()}

    def update_support(self, cfg, show):
        scopes = {"smooth": cfg.gpu in ("rtx40", "rtx50") and cfg.api != "opengl",
                  "smooth_queue": cfg.gpu in ("rtx40", "rtx50") and cfg.api != "opengl",
                  "reflex": cfg.api == "vulkan", "low_latency": cfg.api == "dxvk",
                  "fps": cfg.api in ("dxvk", "dx12"), "vsync": cfg.api in ("dxvk", "opengl"),
                  "anisotropy": cfg.api in ("dxvk", "opengl"), "lod_bias": cfg.api == "dxvk",
                  "indicator": cfg.api != "opengl"}
        values = self.values()
        for key, row in self.rows.items():
            allowed = scopes.get(key, cfg.api == "opengl" if key.startswith("gl_") else True)
            allowed = allowed and compatible("sr", cfg.gpu)
            defaults = {"sharpen_value":50, "film_grain":17, "fps":0, "anisotropy":-1}
            default = defaults.get(key, False if isinstance(self.controls[key], QCheckBox) else "game")
            selected = values[key] != default
            row.setVisible(allowed or show or selected)
            # Keep an incompatible selected control operable so it can be reset.
            self.controls[key].setEnabled(allowed or selected)
        smooth = self.controls["smooth"]
        available = scopes["smooth"] and cfg.smooth_layer is not False
        available = available and smooth_driver_supported(cfg.gpu, cfg.driver)
        smooth.model().item(smooth.findData("on")).setEnabled(available)
        sharpening = self.controls["sharpen"]
        sharp_ok = compatible("sr", cfg.gpu)
        if cfg.driver:
            try:sharp_ok = sharp_ok and int(cfg.driver.split(".")[0]) >= 595
            except ValueError:sharp_ok = False
        sharpening.model().item(sharpening.findData("on")).setEnabled(sharp_ok)
        self.controls["sharpen_value"].setEnabled(cfg.sharpen == "on")
        self.controls["film_grain"].setEnabled(cfg.sharpen == "on")


class MainWindow(QMainWindow):
    def __init__(self, hardware=None):
        super().__init__()
        self.hw = hardware or detect_hardware()
        self._building = True
        self.setWindowTitle("NVIDIA Commands for Linux · Configurador para Linux")
        self.setWindowIcon(QIcon(str(RESOURCES / "assets/nvidia-commands-for-linux.png")))
        self.resize(1350, 900)
        self.setMinimumSize(1080, 760)
        self.setStyleSheet(STYLE)
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(18, 28, 18, 20)
        side.setSpacing(10)
        side.addWidget(label("◈  NVIDIA", "brand"))
        side.addWidget(label("COMMANDS FOR LINUX", "subtitle", True))
        side.addSpacing(30)
        selected = label("Configurador", "badge")
        side.addWidget(selected)
        side.addSpacing(18)
        side.addWidget(label("GPU DETECTADA", "eyebrow"))
        self.hardware_label = label(self.hw.name, "section", True)
        side.addWidget(self.hardware_label)
        self.hardware_support = label("", "muted", True)
        side.addWidget(self.hardware_support)
        self.retry_detection = QPushButton("Detectar de nuevo")
        self.retry_detection.clicked.connect(self.redetect_hardware)
        side.addWidget(self.retry_detection)
        side.addStretch()
        shell.addWidget(sidebar)
        self.stack = QStackedWidget()
        shell.addWidget(self.stack, 1)
        self.build_config()
        self._building = False
        self.refresh()
        self.statusBar().showMessage("Listo para configurar · No afiliado a NVIDIA")

    def redetect_hardware(self):
        self.hw = detect_hardware()
        self.refresh()

    def build_config(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 22, 24, 16)
        layout.setSpacing(14)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.addWidget(label("Tu GPU. Tus ajustes.", "title"))
        titles.addWidget(label("DLSS y ajustes NVIDIA para tus juegos en Linux.", "subtitle", True))
        header.addLayout(titles, 1)
        layout.addLayout(header)
        api_row = QHBoxLayout()
        api_row.addWidget(label("API DEL JUEGO", "eyebrow"))
        self.api = combo([("dxvk", "DirectX 9–11 · DXVK"), ("dx12", "DirectX 12 · VKD3D-Proton"),
                          ("vulkan", "Vulkan · Windows / Proton"), ("native_vulkan", "Vulkan nativo · Linux"), ("opengl", "OpenGL nativo")])
        self.api.setAccessibleName("API gráfica del juego")
        self.api.currentIndexChanged.connect(self.change_api)
        api_row.addWidget(self.api)
        api_row.addStretch()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Borra los parámetros y deja todos los ajustes controlados por el juego.")
        self.reset_button.clicked.connect(self.reset_config)
        api_row.addWidget(self.reset_button)
        layout.addLayout(api_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(0, 0, 8, 0)
        body.setSpacing(14)
        tech_header = QHBoxLayout()
        tech_header.addWidget(label("01 / ELIGE TECNOLOGÍA Y PRESET", "eyebrow"))
        tech_header.addStretch()
        self.advanced = QCheckBox("Mostrar históricos / reservados")
        self.advanced.setToolTip("Las letras sin un modelo documentado se pueden consultar, pero no generar.")
        self.advanced.toggled.connect(self.toggle_advanced)
        self.show_unsupported = QCheckBox("Mostrar tecnologías incompatibles")
        self.show_unsupported.toggled.connect(self.refresh)
        tech_header.addWidget(self.advanced)
        tech_header.addWidget(self.show_unsupported)
        body.addLayout(tech_header)
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(330)
        self.panels = {}
        for tech, title in (("sr", "Super Resolution / DLAA"), ("rr", "Ray Reconstruction"), ("fg", "Frame Generation")):
            panel = TechPanel(tech, self.refresh)
            self.panels[tech] = panel
            self.tabs.addTab(panel, title)
        self.linux_panel = LinuxPanel(self.refresh)
        linux_scroll = QScrollArea()
        linux_scroll.setWidgetResizable(True)
        linux_scroll.setWidget(self.linux_panel)
        self.tabs.addTab(linux_scroll, "Ajustes NVIDIA / Linux")
        self.tabs.setMaximumHeight(440)
        body.addWidget(self.tabs)
        advice_row = QHBoxLayout()
        self.advice = label("", "muted", True)
        advice_row.addWidget(self.advice, 1)
        body.addLayout(advice_row)

        self.options_toggle = QPushButton("▸ Más opciones · parámetros actuales y actualizador NGX")
        self.options_toggle.setCheckable(True)
        self.options_toggle.toggled.connect(self.toggle_options)
        body.addWidget(self.options_toggle)
        self.advanced_card = card()
        advanced_layout = QVBoxLayout(self.advanced_card)
        advanced_layout.setContentsMargins(15, 12, 15, 12)
        advanced_layout.addWidget(label("TUS PARÁMETROS ACTUALES · OPCIONAL", "eyebrow"))
        self.existing = QPlainTextEdit()
        self.existing.setPlaceholderText("Ejemplo: %command% -dx12")
        self.existing.setMaximumHeight(65)
        self.existing.setAccessibleName("Parámetros de lanzamiento existentes")
        self.existing.textChanged.connect(self.refresh)
        advanced_layout.addWidget(self.existing)
        advanced_layout.addWidget(label("Pega tus parámetros para conservarlos en el comando final.", "muted", True))
        self.updater = QCheckBox("Solicitar actualizador NGX de Proton")
        self.updater.setChecked(True)
        self.updater.toggled.connect(self.refresh)
        self.updater.setToolTip("Solicita componentes DLSS compatibles. Si el juego no arranca, prueba desactivándolo.")
        advanced_layout.addWidget(self.updater)
        self.advanced_card.setVisible(False)
        body.addWidget(self.advanced_card)
        body.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        output = card()
        output.setMinimumHeight(300)
        output.setMaximumHeight(360)
        output_layout = QVBoxLayout(output)
        output_layout.setContentsMargins(15, 12, 15, 12)
        output_layout.setSpacing(8)
        self.output_title = label("02 / COPIA EL RESULTADO", "eyebrow")
        output_layout.addWidget(self.output_title)
        self.output_tabs = QTabWidget()
        commands = QWidget()
        columns = QHBoxLayout(commands)
        columns.setContentsMargins(8, 8, 8, 8)
        self.command = QPlainTextEdit()
        self.command.setObjectName("command")
        self.command.setReadOnly(True)
        self.command.setAccessibleName("Comando generado para Steam")
        self.command.setPlaceholderText("Elige un ajuste para crear el comando Steam.")
        self.game_arguments = QPlainTextEdit()
        self.game_arguments.setObjectName("command")
        self.game_arguments.setReadOnly(True)
        self.game_arguments.setAccessibleName("Argumento Epic")
        self.game_arguments.setPlaceholderText("Sin argumentos del juego. Las variables NVIDIA no se pueden pegar como argumentos Epic.")
        self.copy_button = QPushButton("Copiar Steam")
        self.copy_button.setObjectName("primary")
        self.copy_button.clicked.connect(self.copy_command)
        self.copy_arguments_button = QPushButton("Copiar Epic")
        self.copy_arguments_button.clicked.connect(self.copy_epic_arguments)
        self.output_guide = label("Steam → Propiedades → Parámetros de lanzamiento.", "muted", True)
        self.epic_guide = label("Solo argumentos del juego. Epic no interpreta las variables NVIDIA de Steam en este campo.", "muted", True)
        for title, field, button, guide in (
                ("Comando Steam", self.command, self.copy_button, self.output_guide),
                ("Argumento Epic", self.game_arguments, self.copy_arguments_button, self.epic_guide)):
            column = QVBoxLayout()
            row = QHBoxLayout()
            row.addWidget(label(title, "section"))
            row.addStretch()
            row.addWidget(button)
            column.addLayout(row)
            column.addWidget(field, 1)
            column.addWidget(guide)
            columns.addLayout(column, 1)
        self.explanation = browser()
        self.explanation.setAccessibleName("Explicación de cada variable y de su valor")
        self.output_tabs.addTab(commands, "Comandos")
        self.output_tabs.addTab(self.explanation, "Qué hace cada variable")
        output_layout.addWidget(self.output_tabs, 1)
        self.notice = QTextBrowser()
        self.notice.setOpenExternalLinks(True)
        self.notice.setObjectName("detail")
        self.notice.setMinimumHeight(44)
        self.notice.setMaximumHeight(60)
        output_layout.addWidget(self.notice)
        layout.addWidget(output)
        self.stack.addWidget(page)

    def change_api(self):
        if not self._building and self.api.currentData() in ("opengl", "native_vulkan"):
            self._building = True
            for panel in self.panels.values():
                pick(panel.models, "game")
                if panel.mode is not None:pick(panel.mode, "game")
            pick(self.panels["fg"].fg_mode, "game")
            self._building = False
            self.tabs.setCurrentIndex(3)
            self.statusBar().showMessage("Juego nativo: los overrides DLSS de Proton no se aplican. Se deja DLSS controlado por el juego.", 10000)
        self.refresh()

    def reset_config(self):
        self._building = True
        try:
            self.existing.clear()
            self.updater.setChecked(False)
            self.advanced.setChecked(False)
            self.show_unsupported.setChecked(False)
            self.options_toggle.setChecked(False)
            pick(self.api, "dxvk")
            for panel in self.panels.values():
                panel.populate(False, "game")
                if panel.mode is not None:
                    pick(panel.mode, "game")
                    panel.custom_scale.setValue(67)
            fg = self.panels["fg"]
            pick(fg.fg_mode, "game")
            pick(fg.multiplier, 2)
            fg.target.setValue(144)
            defaults = Config()
            for key, widget in self.linux_panel.controls.items():
                value = getattr(defaults, key)
                if isinstance(widget, QCheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(value)
                else:
                    pick(widget, value)
            self.tabs.setCurrentIndex(0)
            self.output_tabs.setCurrentIndex(0)
        finally:
            self._building = False
        self.refresh()
        self.statusBar().showMessage("Configuración borrada. Elige nuevos ajustes para empezar de cero.", 6000)

    def toggle_options(self, checked):
        self.advanced_card.setVisible(checked)
        self.options_toggle.setText(("▾" if checked else "▸") +
                                   " Más opciones · parámetros actuales y actualizador NGX")

    def config(self):
        sr = self.panels["sr"]
        rr = self.panels["rr"]
        fg = self.panels["fg"]
        return Config(
            gpu=self.hw.family,
            sr=Selection(sr.models.currentData() or "game", sr.mode.currentData(), sr.custom_scale.value()),
            rr=Selection(rr.models.currentData() or "game", rr.mode.currentData(), rr.custom_scale.value()),
            fg=Selection(fg.models.currentData() or "game"),
            fg_mode=fg.fg_mode.currentData(), multiplier=fg.multiplier.currentData(),
            target_fps=fg.target.value(), updater=self.updater.isChecked(),
            existing=self.existing.toPlainText(), api=self.api.currentData(),
            driver=self.hw.driver if self.hw.driver != "Sin detectar" else "",
            smooth_layer=self.hw.smooth_layer, reflex_layer=self.hw.reflex_layer,
            **self.linux_panel.values())

    def refresh(self, *_):
        if self._building:
            return
        cfg = self.config()
        self.linux_panel.update_support(cfg, self.show_unsupported.isChecked())
        self.hardware_label.setText(self.hw.name)
        self.hardware_support.setText(
            "SR / DLAA · RR · FG / MFG" if cfg.gpu == "rtx50" else
            "SR / DLAA · RR · FG 2×" if cfg.gpu == "rtx40" else
            "SR / DLAA · RR\nFG requiere RTX 40/50" if compatible("sr", cfg.gpu) else
            "Compatibilidad sin identificar")
        self.retry_detection.setVisible(not compatible("sr", cfg.gpu))
        show = self.show_unsupported.isChecked()
        native = cfg.api in ("opengl", "native_vulkan")
        for index in (0, 1):self.tabs.setTabVisible(index, not native or show)
        self.tabs.setTabVisible(2, (compatible("fg", cfg.gpu) and not native) or show or
                                cfg.fg.preset != "game" or cfg.fg_mode != "game")
        for panel in self.panels.values():
            panel.update_info(cfg.gpu, cfg.api)
        self.result = generate(cfg)
        if self.result.command == "%command%":
            self.result.command = ""
        self.command.setPlainText(self.result.command)
        try:
            self.epic_arguments = epic_arguments(cfg.existing)
            self.epic_guide.setText("Solo argumentos del juego. Los ajustes NVIDIA necesitan variables de entorno; no se aplican pegándolos aquí.")
        except ValueError as error:
            self.epic_arguments = ""
            self.epic_guide.setText(str(error))
        self.game_arguments.setPlainText(self.epic_arguments)
        self.copy_arguments_button.setEnabled(bool(self.epic_arguments))
        self.copy_button.setEnabled(not self.result.errors and bool(self.result.command))
        messages = list(self.result.errors) + list(self.result.warnings) + list(self.hw.notes)
        active = bool(self.result.settings)
        if active and self.hw.driver not in ("Sin detectar", ""):
            try:
                if int(self.hw.driver.split(".")[0]) < 570:
                    messages.append("Controlador anterior a R570: la wiki documenta incidencias del actualizador NGX.")
            except ValueError:
                pass
        if not messages:
            messages = ["Sin overrides nuevos. Se respetan las decisiones del juego. Aplicación en juego: sin verificar."]
        self.notice.setHtml(html("".join(f'<p style="margin: 3px 0; color: {"#f4be8c" if i < len(self.result.errors) else "#aabac6"}">• '
                                         f'{escape(message)}</p>' for i, message in enumerate(messages))))
        explanations = explain_result(self.result)
        self.explanation.setHtml(html("".join(
            f"<p><code>{escape(token)}</code><br>{escape(meaning)}</p>"
            for token, meaning in explanations) or "<p>No hay variables activas. Elige un ajuste para ver qué hace y qué significa su valor.</p>"))
        if cfg.gpu in ("rtx20", "rtx30"):
            suggestion = "Para tu GPU: K · DLSS 4.0 es un buen punto de partida. L/M · DLSS 4.5 pueden costar más FPS."
        elif cfg.gpu in ("rtx40", "rtx50"):
            suggestion = "K · DLSS 4.0 para Calidad/DLAA; compara M · DLSS 4.5 en Rendimiento y L en Ultra rendimiento."
        else:
            suggestion = "No se ha identificado una GeForce RTX compatible. Comprueba la detección de la GPU."
        self.advice.setText(suggestion)

    def toggle_advanced(self, checked):
        for panel in self.panels.values():
            panel.populate(checked)
        self.refresh()

    def copy_epic_arguments(self):
        self.refresh()
        if self.epic_arguments:
            QApplication.clipboard().setText(self.epic_arguments)
            self.statusBar().showMessage("Argumentos copiados para los ajustes del juego en Epic. No contienen los ajustes NVIDIA.", 8000)

    def copy_command(self):
        self.refresh()
        if self.result.errors or not self.result.command:
            return
        QApplication.clipboard().setText(self.result.command)
        self.statusBar().showMessage("Comando copiado para Steam → Parámetros de lanzamiento del juego.", 8000)
        self.copy_button.setText("✓ Copiado")
        QTimer.singleShot(1800, lambda: self.copy_button.setText("Copiar Steam"))

def main():
    parser = argparse.ArgumentParser(description="NVIDIA Commands for Linux · Linux / Proton")
    parser.add_argument("--screenshot", type=Path, help="Guardar captura de la interfaz y salir (comprobación visual)")
    parser.add_argument("--version", action="version", version=f"NVIDIA Commands for Linux {__version__}")
    parser.add_argument("--self-test", action="store_true", help="Verificar recursos, interfaz y portapapeles y salir")
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName("NVIDIA Commands for Linux")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(RESOURCES / "assets/nvidia-commands-for-linux.png")))
    app.setOrganizationName("N3ruk")
    app.setDesktopFileName("nvidia-commands-for-linux")
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#101419"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e7edf3"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#11191f"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e7edf3"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#273440"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e7edf3"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#365348"))
    app.setPalette(palette)
    window = MainWindow(Hardware("NVIDIA GeForce RTX 2060", "rtx20")) if args.self_test else MainWindow()
    window.show()
    if args.self_test:
        def verify():
            try:
                assert not window.windowIcon().isNull(), "Icono ausente"
                assert window.panels["sr"].generation.text() == "DLSS 4.0", "Catálogo incorrecto"
                pick(window.panels["sr"].models, "M")
                pick(window.panels["sr"].mode, "performance")
                window.copy_command()
                command = app.clipboard().text()
                assert "render_preset_m" in command and command.count("%command%") == 1, "Copia incorrecta"
                smooth = generate(Config(gpu="rtx50", smooth="on", driver="595.99.02", smooth_layer=True))
                assert not smooth.errors and "NVPRESENT_ENABLE_SMOOTH_MOTION=1" in smooth.command, "Smooth Motion incorrecto"
                conflict = generate(Config(gpu="rtx50", smooth="on", fg_mode="dynamic"))
                assert conflict.errors and not conflict.command, "Conflicto FG no bloqueado"
                window.existing.setPlainText("%command% -dx12")
                window.copy_epic_arguments()
                assert app.clipboard().text() == "-dx12", "Argumentos Epic incorrectos"
                assert "DXVK_NVAPI_DRS_SETTINGS" in window.explanation.toPlainText(), "Explicaciones ausentes"
                window.reset_button.click()
                assert not window.command.toPlainText() and not window.game_arguments.toPlainText(), "Reset no vacía las salidas"
                assert not window.result.environment and not window.copy_button.isEnabled(), "Reset conserva ajustes"
                pick(window.panels["sr"].models, "M")
                assert "render_preset_m" in window.command.toPlainText(), "No se puede empezar tras Reset"
                print(f"NVIDIA Commands for Linux {__version__}: recursos, GPU simulada, presets, Steam/Argumento Epic, Reset, explicaciones, Smooth Motion, conflictos y portapapeles OK", flush=True)
                app.exit(0)
            except Exception as error:
                print(f"Autocomprobación fallida: {error}", file=sys.stderr, flush=True)
                app.exit(1)
        QTimer.singleShot(100, verify)
    if args.screenshot:
        def capture():
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            ok = window.grab().save(str(args.screenshot))
            app.exit(0 if ok else 1)
        QTimer.singleShot(600, capture)
    return app.exec()
