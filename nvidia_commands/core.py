"""Pure command composition. Never executes launch options or modifies game files."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

RESOURCES = Path(__file__).resolve().parent
CATALOG = json.loads((RESOURCES / 'data/catalog.json').read_text(encoding='utf-8'))
MODES = {'game': 'Controlado por el juego', 'dlaa': 'DLAA · resolución nativa',
         'quality': 'Calidad', 'balanced': 'Equilibrado', 'performance': 'Rendimiento',
         'ultra_performance': 'Ultra rendimiento', 'custom': 'Escala personalizada'}
FAMILIES = ('rtx20', 'rtx30', 'rtx40', 'rtx50')

@dataclass
class Hardware:
    name: str = 'GPU sin identificar'
    family: str = 'unknown'
    driver: str = 'Sin detectar'
    memory: str = ''
    notes: list[str] = field(default_factory=list)
    smooth_layer: bool | None = None
    reflex_layer: bool | None = None

@dataclass
class Selection:
    preset: str = 'game'
    mode: str = 'game'
    scale: int = 67

@dataclass
class Config:
    gpu: str = 'rtx20'
    sr: Selection = field(default_factory=lambda: Selection('K'))
    rr: Selection = field(default_factory=Selection)
    fg: Selection = field(default_factory=Selection)
    fg_mode: str = 'game'
    multiplier: int = 2
    target_fps: int = 144
    updater: bool = True
    existing: str = ''
    launcher: str = 'steam'
    epic_path: str = ''
    epic_uri: str = ''
    api: str = 'dxvk'
    driver: str = ''
    smooth_layer: bool | None = None
    reflex_layer: bool | None = None
    smooth: str = 'game'
    smooth_queue: bool = False
    reflex: bool = False
    low_latency: str = 'game'
    fps: int = 0
    vsync: str = 'game'
    anisotropy: int = -1
    lod_bias: str = 'game'
    hdr: bool = False
    hud: str = 'game'
    indicator: str = 'game'
    prime: bool = False
    gl_threaded: str = 'game'
    gl_fxaa: str = 'game'
    gamescope: str = 'game'
    scaling_size: str = '720-1080'
    gl_vrr: str = 'game'
    gl_cache: str = 'game'
    sharpen: str = 'game'
    sharpen_value: int = 50
    film_grain: int = 17
    api_osd: bool = False

@dataclass
class Result:
    command: str = ''
    settings: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    game_arguments: str = ''


def preset(tech, key):
    return next(p for p in CATALOG['technologies'][tech]['presets'] if p['id'] == key)


def family_for(name):
    match = re.search(r'\bGeForce\s+RTX\s*([2345])\d{2}[0-9]\b', name, re.I)
    return 'rtx' + match[1] + '0' if match else 'unknown'


def compatible(tech, family):
    return family in (('rtx40', 'rtx50') if tech in ('fg', 'smooth') else FAMILIES)


def smooth_driver_supported(family, driver):
    if not driver:
        return True  # Unknown is reported, not presented as a verified runtime.
    try:
        parts = tuple(int(v) for v in driver.split('.')[:3])
    except ValueError:
        return False
    version = parts + (0,) * (3-len(parts))
    baseline = (580,95,5) if family == 'rtx40' else (580,65,6)
    return version >= baseline


def layer_present(name):
    dirs = [Path('/usr/share/vulkan/implicit_layer.d'), Path('/etc/vulkan/implicit_layer.d'),
            Path('/usr/share/vulkan/explicit_layer.d'), Path('/etc/vulkan/explicit_layer.d'),
            Path.home() / '.local/share/vulkan/implicit_layer.d',
            Path.home() / '.local/share/vulkan/explicit_layer.d']
    for directory in dirs:
        for path in directory.glob('*.json'):
            try:
                data = json.loads(path.read_text())
                layers = data.get('layers', [data.get('layer', {})])
                if any(layer.get('name') == name for layer in layers):
                    return True
            except (OSError, ValueError, TypeError, AttributeError):
                continue
    return False


def detect_hardware():
    env = os.environ.copy()
    if getattr(sys, 'frozen', False):
        original = env.get('LD_LIBRARY_PATH_ORIG')
        if original is None:
            env.pop('LD_LIBRARY_PATH', None)
        else:
            env['LD_LIBRARY_PATH'] = original
    try:
        reply = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,memory.total',
                                '--format=csv,noheader'], capture_output=True, text=True,
                               timeout=5, env=env, check=False)
        cards = [line.split(',', 2) for line in reply.stdout.strip().splitlines() if line.count(',') >= 2]
        if reply.returncode or not cards:
            return Hardware(notes=['nvidia-smi no ha devuelto una GPU. Comprueba el controlador propietario.'])
        cards.sort(key=lambda card: FAMILIES.index(family_for(card[0])) if family_for(card[0]) in FAMILIES else -1,
                   reverse=True)
        name, driver, memory = (x.strip() for x in cards[0])
        notes = ['Hay varias GPU NVIDIA; se muestra la RTX de generación más reciente. Elige esa GPU en el juego.'] if len(cards) > 1 else []
        return Hardware(name, family_for(name), driver, memory, notes,
                        layer_present('VK_LAYER_NV_present'), layer_present('VK_LAYER_DXVK_NVAPI_reflex'))
    except (OSError, subprocess.SubprocessError):
        return Hardware(notes=['No se pudo consultar nvidia-smi. Instala o revisa el controlador NVIDIA del sistema.'])


def detect_protons():
    roots = [Path.home() / '.local/share/Steam', Path.home() / '.steam/steam',
             Path.home() / '.var/app/com.valvesoftware.Steam/data/Steam']
    names = set()
    for root in roots:
        for parent in (root / 'steamapps/common', root / 'compatibilitytools.d'):
            if parent.is_dir():
                for path in parent.iterdir():
                    if (path / 'proton').is_file() or (path / 'compatibilitytool.vdf').is_file():
                        names.add(path.name)
    return sorted(names)


class ProfileStore:
    """Compatibility reader for old saved profiles; never deletes the old store."""
    def __init__(self, path=None):
        self.path = Path(path) if path else Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'dlss-studio/profiles.json'
    def load(self):
        if not self.path.exists():
            return {}
        try:
            result = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(result, dict):
                raise ValueError('El almacén de perfiles no es un objeto JSON')
            return result
        except (ValueError, OSError) as error:
            raise ValueError('No se puede leer el almacén de perfiles; no se sobrescribe.') from error
    def save(self, name, state):
        data = self.load()
        data[name] = state
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        temp.chmod(0o600)
        temp.replace(self.path)


def parse_existing(value):
    if any(c in value for c in ('\n', '\r', '\x00', '`', '$')):
        raise ValueError('No se admiten operadores de shell, sustituciones ni varias líneas.')
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars=';&|<>')
        lexer.whitespace_split = True
        lexer.commenters = ''
        tokens = list(lexer)
        if any(t and all(ch in ';&|<>' for ch in t) for t in tokens):
            raise ValueError('No se admiten operadores de shell en los parámetros actuales.')
    except ValueError as error:
        raise ValueError('Comillas sin cerrar en los parámetros actuales.') from error
    if tokens and tokens[0] == 'env':
        tokens.pop(0)
    env = {}
    while tokens and re.match(r'^[A-Za-z_][A-Za-z_0-9]*=', tokens[0]):
        key, val = tokens.pop(0).split('=', 1)
        env[key] = val
    if any(re.match(r'^(?:DXVK_NVAPI_DRS_|PROTON_ENABLE_NGX_UPDATER=|NVPRESENT_)', t) for t in tokens):
        raise ValueError('Las variables gestionadas deben ir antes de los wrappers, no después.')
    if any('%command%' in t and t != '%command%' for t in tokens) or tokens.count('%command%') > 1:
        raise ValueError('Utiliza un único %command%, como palabra independiente.')
    if '%command%' not in tokens:
        tokens.append('%command%')
    return env, tokens


def parse_drs(value):
    result = {}
    if not value:
        return result
    for entry in value.split(','):
        if '=' not in entry:
            raise ValueError('DXVK_NVAPI_DRS_SETTINGS contiene un ajuste sin valor.')
        key, val = entry.split('=', 1)
        if not key.strip() or not val.strip():
            raise ValueError('DXVK_NVAPI_DRS_SETTINGS contiene un ajuste vacío.')
        result[key.strip().upper()] = val.strip()
    return result


def merge_dxvk(value, changes):
    items = {}
    for item in value.split(';'):
        if not item.strip():
            continue
        if '=' not in item:
            raise ValueError('DXVK_CONFIG no se puede combinar: usa pares clave=valor separados por punto y coma.')
        key, val = item.split('=', 1)
        items[key.strip()] = val.strip()
    items.update(changes)
    return '; '.join(f'{k} = {v}' for k, v in items.items())


def generate(cfg):
    r = Result()
    s = r.settings
    try:
        env, tokens = parse_existing(cfg.existing)
        old_drs = parse_drs(env.get('DXVK_NVAPI_DRS_SETTINGS', ''))
        for key in list(env):
            if key.startswith('DXVK_NVAPI_DRS_') and key != 'DXVK_NVAPI_DRS_SETTINGS':
                old_drs[key[len('DXVK_NVAPI_DRS_'):].upper()] = env.pop(key)
        if cfg.launcher not in ('steam', 'epic') or cfg.api not in ('dxvk', 'dx12', 'vulkan', 'native_vulkan', 'opengl'):
            raise ValueError('Destino o API gráfica desconocidos.')
        for tech in ('sr', 'rr', 'fg'):
            choice = getattr(cfg, tech)
            try:
                model = preset(tech, choice.preset)
            except StopIteration:
                raise ValueError('Preset desconocido: ' + choice.preset)
            if not model['generatable']:
                raise ValueError('Reservado o retirado: este preset no tiene un modelo utilizable documentado.')
            active = choice.preset != 'game' or choice.mode != 'game'
            if active and not compatible(tech, cfg.gpu):
                raise ValueError(f'{tech.upper()} no es compatible con la GPU detectada.')
            if active and cfg.api in ('opengl', 'native_vulkan'):
                raise ValueError('Los overrides DLSS de DXVK-NVAPI son para Wine/Proton, no para juegos nativos de Linux. Elige controlado por el juego.')
            stem = f'NGX_DLSS_{tech.upper()}'
            if choice.preset != 'game':
                s[stem + '_OVERRIDE'] = 'on'
                s[stem + '_OVERRIDE_RENDER_PRESET_SELECTION'] = 'render_preset_' + choice.preset.lower()
            if choice.mode not in MODES:
                raise ValueError('Modo de calidad desconocido.')
            if tech in ('sr', 'rr') and choice.mode != 'game':
                s[stem + '_OVERRIDE'] = 'on'
                s[stem + '_MODE'] = choice.mode
                if choice.mode == 'custom':
                    if not isinstance(choice.scale, int) or not 33 <= choice.scale <= 100:
                        raise ValueError('La escala personalizada DLSS debe estar entre 33 y 100 %.')
                    s[stem + '_OVERRIDE_SCALING_RATIO'] = str(choice.scale)
            if tech == 'sr' and choice.preset in ('L', 'M') and cfg.gpu in ('rtx20', 'rtx30'):
                r.warnings.append('L/M requieren más trabajo en RTX 20/30 sin FP8 nativo. Compara el coste con K.')
        if cfg.sr.mode != cfg.rr.mode and 'game' not in (cfg.sr.mode, cfg.rr.mode):
            r.warnings.append('SR y RR solicitan modos distintos; su aplicación depende de la integración del juego.')
        if cfg.fg_mode not in ('game', 'on', 'off', 'dynamic'):
            raise ValueError('Modo de generación de fotogramas desconocido.')
        if cfg.fg_mode != 'game':
            if not compatible('fg', cfg.gpu) or cfg.api in ('opengl', 'native_vulkan'):
                raise ValueError('Frame Generation necesita RTX 40/50 y una integración compatible, no OpenGL nativo.')
            s['NGX_DLSS_FG_OVERRIDE'] = 'on'
            s['NGX_DLSSG_MODE'] = cfg.fg_mode
            if cfg.fg_mode in ('on', 'dynamic'):
                if not isinstance(cfg.multiplier, int) or not 2 <= cfg.multiplier <= 6:
                    raise ValueError('El multiplicador debe estar entre 2× y 6×.')
                if cfg.gpu != 'rtx50' and (cfg.multiplier > 2 or cfg.fg_mode == 'dynamic'):
                    raise ValueError('MFG y el modo dinámico requieren RTX 50.')
                if cfg.fg_mode == 'dynamic':
                    if not isinstance(cfg.target_fps, int) or not 30 <= cfg.target_fps <= 1000:
                        raise ValueError('Objetivo dinámico fuera de rango (30–1000 FPS).')
                    s['NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX'] = str(cfg.multiplier - 1)
                    s['NGX_DLSSG_DYNAMIC_TARGET_FRAME_RATE'] = str(cfg.target_fps)
                else:
                    s['NGX_DLSSG_MULTI_FRAME_COUNT'] = str(cfg.multiplier - 1)
        if s:
            r.warnings.append('Requiere DXVK-NVAPI/Proton reciente y funciones integradas en el juego. El comando solicita ajustes; no verifica su aplicación.')
            if cfg.updater:
                env['PROTON_ENABLE_NGX_UPDATER'] = '1'
        overwritten = set(old_drs) & set(s)
        if overwritten:
            r.warnings.append('Se sustituye el valor anterior de los ajustes seleccionados; se conservan los demás.')
        unmanaged = set(old_drs) - set(s)
        if unmanaged:
            r.warnings.append('Se conservan overrides previos no controlados por esta selección. Revisa su compatibilidad.')
        if cfg.fg_mode != 'game':
            stale = ['NGX_DLSSG_MULTI_FRAME_COUNT', 'NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX', 'NGX_DLSSG_DYNAMIC_TARGET_FRAME_RATE']
            for key in stale:
                if key not in s:old_drs.pop(key, None)
        old_drs.update(s)
        if old_drs:
            env['DXVK_NVAPI_DRS_SETTINGS'] = ','.join(f'{k}={v}' for k, v in old_drs.items())
        else:
            env.pop('DXVK_NVAPI_DRS_SETTINGS', None)
        apply_features(cfg, r, env, tokens, old_drs)
        if cfg.fg_mode in ('on', 'dynamic') and env.get('NVPRESENT_ENABLE_SMOOTH_MOTION') == '1':
            raise ValueError('No combines Smooth Motion previo con DLSS FG.')
        if cfg.launcher == 'steam':
            r.command = ' '.join([*(f'{k}={shlex.quote(v)}' for k, v in env.items()), *map(shlex.quote, tokens)])
        else:
            compose_epic(cfg, r, env, tokens)
        r.environment = env
    except (ValueError, TypeError) as error:
        r.errors.append(str(error))
        r.command = ''
    return r


def apply_features(c, r, env, tokens, drs):
    dx = {}
    def state(value):
        if value not in ('game', 'on', 'off'):
            raise ValueError('Valor de activación desconocido.')
        return {'on': '1', 'off': '0'}.get(value)
    for value in (c.smooth, c.vsync, c.low_latency, c.gl_threaded, c.gl_fxaa, c.gl_vrr, c.gl_cache, c.sharpen):
        state(value)
    if c.smooth != 'game':
        if c.smooth == 'on':
            if not compatible('smooth', c.gpu) or c.api == 'opengl':
                raise ValueError('Smooth Motion requiere RTX 40/50 y Vulkan (incluido DirectX traducido por Proton).')
            if not smooth_driver_supported(c.gpu, c.driver):
                raise ValueError('Smooth Motion: base documentada RTX 50 con 580.65.06+ y RTX 40 con 580.95.05+. Revisa el controlador.')
            if c.smooth_layer is False:
                raise ValueError('No se detecta VK_LAYER_NV_present. Revisa la instalación del controlador.')
            if c.smooth_layer is None:
                r.warnings.append('Smooth Motion: comprueba que el controlador incluye VK_LAYER_NV_present. La base documentada R580 soporta juegos Vulkan x86_64.')
            if c.fg_mode in ('on', 'dynamic') or drs.get('NGX_DLSSG_MODE', '').lower() in ('on', 'dynamic', 'auto', '2', '3', '4', '0x2', '0x3', '0x4') or (drs.get('NGX_DLSS_FG_OVERRIDE', '').lower() == 'on' and c.fg_mode != 'off'):
                raise ValueError('No combines Smooth Motion con DLSS Frame Generation. Desactiva FG en el juego y en los overrides.')
            r.warnings.append('Smooth Motion: desactiva FG dentro del juego; el generador no puede leer ese ajuste. Algunas superposiciones pueden interferir.')
        env['NVPRESENT_ENABLE_SMOOTH_MOTION'] = state(c.smooth)
    if c.smooth_queue:
        if env.get('NVPRESENT_ENABLE_SMOOTH_MOTION') != '1':
            raise ValueError('La compatibilidad de superposiciones requiere activar Smooth Motion.')
        env['NVPRESENT_QUEUE_FAMILY'] = '1'
    if env.get('NVPRESENT_ENABLE_SMOOTH_MOTION') == '1' and (c.fg_mode in ('on', 'dynamic') or drs.get('NGX_DLSSG_MODE', '').lower() in ('on', 'dynamic', 'auto', '2', '3', '4', '0x2', '0x3', '0x4') or (drs.get('NGX_DLSS_FG_OVERRIDE', '').lower() == 'on' and c.fg_mode != 'off')):
        raise ValueError('Los parámetros actuales combinan Smooth Motion y DLSS FG. Resuelve el conflicto antes de copiar.')
    if c.reflex:
        if c.gpu not in FAMILIES or c.api != 'vulkan':
            raise ValueError('El puente Reflex Vulkan se usa en juegos Windows/Vulkan con GPU RTX; DirectX ya lo enruta por DXVK-NVAPI.')
        if c.reflex_layer is False:
            raise ValueError('No se detecta VK_LAYER_DXVK_NVAPI_reflex; instala la capa compatible o usa winevulkan moderno compatible.')
        env['DXVK_NVAPI_VKREFLEX'] = '1'
        r.warnings.append('Activa Reflex en el juego. Este puente requiere la capa DXVK-NVAPI Reflex; no fuerza Reflex en títulos sin integración.')
    if c.low_latency != 'game':
        if c.api != 'dxvk':raise ValueError('La reducción de latencia DXVK solo se aplica a DirectX 9–11 con DXVK reciente.')
        dx['dxvk.latencySleep'] = 'True' if c.low_latency == 'on' else 'False'
        r.warnings.append('Latencia DXVK: no equivale a Reflex de NVIDIA App; puede interferir con limitadores o empeorar el pacing.')
    if not isinstance(c.fps, int) or not 0 <= c.fps <= 1000:
        raise ValueError('Límite de FPS fuera de rango (0 = sin override; 1–1000).')
    if c.fps:
        if c.api == 'dxvk':
            dx.update({'dxgi.maxFrameRate': str(c.fps), 'd3d9.maxFrameRate': str(c.fps)})
        elif c.api == 'dx12':env['VKD3D_FRAME_RATE'] = str(c.fps)
        else:raise ValueError('Este limitador solo se aplica a DXVK/VKD3D-Proton; usa el del juego en Vulkan/OpenGL.')
        r.warnings.append('Límite de FPS renderizados, no un objetivo de MFG. El limitador del juego, MangoHud o Gamescope puede ofrecer mejor pacing.')
    if c.vsync != 'game':
        if c.api == 'dxvk':
            dx.update({'dxgi.syncInterval': '1' if c.vsync == 'on' else '0', 'd3d9.presentInterval': '1' if c.vsync == 'on' else '0'})
        elif c.api == 'opengl':env['__GL_SYNC_TO_VBLANK'] = state(c.vsync)
        else:raise ValueError('Este override VSync se limita a DXVK u OpenGL; usa el juego/compositor para esta API.')
    if c.anisotropy not in (-1, 0, 2, 4, 8, 16):raise ValueError('Filtrado anisotrópico no válido.')
    if c.anisotropy >= 0:
        if c.api == 'dxvk':dx.update({'d3d11.samplerAnisotropy': str(c.anisotropy), 'd3d9.samplerAnisotropy': str(c.anisotropy)})
        elif c.api == 'opengl':env['__GL_LOG_MAX_ANISO'] = str({0:0,2:1,4:2,8:3,16:4}[c.anisotropy])
        else:raise ValueError('El override de anisotropía no se aplica a DirectX 12/Vulkan; ajústalo dentro del juego.')
        r.warnings.append('Forzar anisotropía puede romper pases que necesitan filtrado bilineal.')
    if c.lod_bias != 'game':
        if c.api != 'dxvk' or c.lod_bias not in ('-2.0', '-1.0', '-0.5', '0.0', '0.5', '1.0'):
            raise ValueError('LOD bias requiere DXVK y un valor entre −2 y +1.')
        dx.update({'d3d11.samplerLodBias': c.lod_bias, 'd3d9.samplerLodBias': c.lod_bias})
        r.warnings.append('LOD negativo aumenta detalle y puede producir parpadeo; no es RTX Dynamic Vibrance ni un filtro Freestyle.')
    if c.hdr:
        if c.api != 'dxvk':raise ValueError('La señalización DXVK_HDR se aplica a DXVK; no convierte SDR en HDR.')
        env['DXVK_HDR'] = '1'
        r.warnings.append('HDR nativo: necesita juego, pantalla y compositor HDR configurados. No es RTX HDR ni transforma juegos SDR.')
    if c.hud not in ('game', 'dxvk', 'mangohud'):raise ValueError('Superposición desconocida.')
    if c.hud == 'dxvk':
        if c.api != 'dxvk':raise ValueError('DXVK HUD solo se aplica a juegos DXVK.')
        old = env.get('DXVK_HUD', '').split(',')
        env['DXVK_HUD'] = ','.join(dict.fromkeys([x for x in old if x] + ['fps','frametimes','gpuload','memory']))
    elif c.hud == 'mangohud':
        if c.api == 'opengl':
            if 'mangohud' not in tokens:tokens[:0] = ['mangohud','--dlsym']
        else:env['MANGOHUD'] = '1'
        r.warnings.append('MangoHud debe estar instalado para la arquitectura y el entorno del juego (también Flatpak si corresponde).')
    if c.indicator not in ('game', 'on', 'off'):raise ValueError('Indicador DLSS desconocido.')
    if c.indicator != 'game':
        if c.api == 'opengl' or c.gpu not in FAMILIES:raise ValueError('Los indicadores NGX requieren una GPU RTX y un juego compatible con NGX.')
        if c.api == 'native_vulkan':
            env['__NGX_SHOW_INDICATOR'] = '1024' if c.indicator == 'on' else '0'
        else:
            apply_wine_indicators(c, r, env)
    if c.prime:
        if c.gpu not in FAMILIES:raise ValueError('PRIME necesita una GPU NVIDIA detectada.')
        env.update({'__NV_PRIME_RENDER_OFFLOAD':'1','__GLX_VENDOR_LIBRARY_NAME':'nvidia','__VK_LAYER_NV_optimus':'NVIDIA_only'})
        r.warnings.append('PRIME: para equipos híbridos con la GPU NVIDIA configurada; no instala ni configura el controlador.')
    for key,value in [('__GL_THREADED_OPTIMIZATIONS',c.gl_threaded),('__GL_ALLOW_FXAA_USAGE',c.gl_fxaa),('__GL_VRR_ALLOWED',c.gl_vrr),('__GL_SHADER_DISK_CACHE',c.gl_cache)]:
        if value == 'game':continue
        if c.api != 'opengl':raise ValueError('Este ajuste del controlador NVIDIA solo se aplica a OpenGL, no a Vulkan/Proton DirectX.')
        if c.gpu not in FAMILIES:raise ValueError('El ajuste OpenGL requiere una GPU NVIDIA RTX detectada.')
        env[key] = state(value)
    if c.gl_fxaa != 'game':r.warnings.append('__GL_ALLOW_FXAA_USAGE solo permite o impide FXAA del driver; no lo activa sin un perfil FXAA configurado.')
    if c.sharpen != 'game':
        if c.gpu not in FAMILIES:raise ValueError('La nitidez del driver requiere una GPU NVIDIA RTX detectada.')
        if c.driver and c.sharpen == 'on':
            try:version = int(c.driver.split('.')[0])
            except ValueError:raise ValueError('No se pudo comprobar el controlador para el filtro de nitidez.')
            if version < 595:raise ValueError('La nitidez OpenGL/Vulkan está verificada con R595 o posterior en esta versión.')
        if not all(isinstance(x, int) and 0 <= x <= 100 for x in (c.sharpen_value, c.film_grain)):
            raise ValueError('Nitidez y reducción de grano deben estar entre 0 y 100.')
        env['__GL_SHARPEN_ENABLE'] = state(c.sharpen)
        if c.sharpen == 'on':
            env.update({'__GL_SHARPEN_VALUE':str(c.sharpen_value), '__GL_SHARPEN_IGNORE_FILM_GRAIN':str(c.film_grain)})
        r.warnings.append('Nitidez del controlador NVIDIA: soporte documentado con R595 para OpenGL/Vulkan. No activa escalado NIS ni sustituye DLSS.')
    if c.api_osd:
        if c.gpu not in FAMILIES:raise ValueError('El indicador gráfico requiere una GPU NVIDIA RTX detectada.')
        env['__GL_SHOW_GRAPHICS_OSD'] = '1'
    if c.gamescope != 'game':
        sizes = {'720-1080': (1280,720,1920,1080), '1080-1440': (1920,1080,2560,1440),
                 '1080-4k': (1920,1080,3840,2160), '1440-4k': (2560,1440,3840,2160),
                 '4k-1080': (3840,2160,1920,1080), '4k-1440': (3840,2160,2560,1440)}
        if c.gamescope not in ('nis','fsr','supersample') or c.scaling_size not in sizes:
            raise ValueError('Modo o resoluciones de Gamescope desconocidos.')
        if c.launcher != 'steam':raise ValueError('El wrapper Gamescope requiere el comando del juego. No se envuelve el launcher de Epic como si fuera un juego.')
        if env.get('NVPRESENT_ENABLE_SMOOTH_MOTION') == '1':raise ValueError('No se combina automáticamente Smooth Motion con Gamescope: la capa puede afectar al compositor y al juego. Usa una sola ruta de interpolación/escalado.')
        if 'gamescope' in tokens:raise ValueError('Ya existe un wrapper Gamescope. Configúralo en un único lugar para evitar anidarlo.')
        w,h,ow,oh = sizes[c.scaling_size]
        if (c.gamescope == 'supersample') != (w > ow):
            raise ValueError('Supersampling requiere renderizar por encima de la salida; NIS/FSR requieren renderizar por debajo.')
        wrap = ['gamescope','-w',str(w),'-h',str(h),'-W',str(ow),'-H',str(oh)]
        if c.gamescope in ('nis','fsr'):wrap.extend(['-F',c.gamescope])
        tokens[:0] = wrap + ['--']
        r.warnings.append('Gamescope debe estar instalado. NVIDIA requiere driver 515.43.04+ y nvidia-drm.modeset=1. El juego debe usar la resolución interna; no es DSR/DLDSR del driver ni escalado temporal DLSS.')
    if dx:env['DXVK_CONFIG'] = merge_dxvk(env.get('DXVK_CONFIG',''), dx)



def apply_wine_indicators(c, r, env):
    updates = {'DLSSIndicator': '1024' if c.indicator == 'on' else '0', 'DLSSGIndicator': '2' if c.indicator == 'on' else '0'}
    indicators = {}
    for item in env.get('DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS', '').split(','):
        if not item:continue
        if '=' not in item:raise ValueError('Los indicadores NGX anteriores contienen una entrada inválida.')
        key, value = item.split('=',1)
        key = {'DLSSINDICATOR':'DLSSIndicator','DLSSGINDICATOR':'DLSSGIndicator'}.get(key.upper(),key)
        indicators[key] = value
    indicators.update(updates)
    env['DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS'] = ','.join(f'{k}={v}' for k,v in indicators.items())
    r.warnings.append('El indicador escribe en el registro del prefijo Wine y persiste. Para quitarlo, ejecuta una vez el comando con «Desactivar indicador».')

def compose_epic(c, r, env, tokens):
    if not c.epic_path or not Path(c.epic_path).is_absolute() or '\x00' in c.epic_path:
        raise ValueError('Selecciona la ruta absoluta al AppImage/binario oficial de Epic Games Launcher.')
    if c.epic_uri and not re.fullmatch(r'com\.epicgames\.launcher://apps/[A-Za-z0-9_.:%?=&+\-]+', c.epic_uri):
        raise ValueError('Usa un enlace oficial com.epicgames.launcher://apps/… sin espacios ni instrucciones de shell.')
    index = tokens.index('%command%')
    if index:
        raise ValueError('Los wrappers de Steam no son argumentos de Epic. Retíralos y configura el runtime de Epic por separado.')
    args = tokens[index+1:]
    r.game_arguments = shlex.join(args)
    launch = [c.epic_path] + ([c.epic_uri] if c.epic_uri else [])
    r.command = shlex.join(['env', *(f'{k}={v}' for k,v in env.items()), *launch])
    r.warnings.append('Epic Preview: cierra completamente el launcher antes de ejecutar este comando en una terminal. Las variables pertenecen a toda esa sesión, no a un perfil por juego; salen de efecto al cerrar Epic.')
    if args:r.warnings.append('Copia los argumentos del juego por separado en sus ajustes de Epic. Las variables de entorno NO van en ese campo.')
    r.warnings.append('La herencia hasta el runtime/juego de Epic está sin verificar en una sesión con cuenta. No se presupone que Epic use Proton de Steam ni que acepte %command%.')


def epic_arguments(existing):
    """Extract only game arguments; never disguise environment as Epic arguments."""
    _, tokens = parse_existing(existing)
    index = tokens.index('%command%')
    if index:
        raise ValueError('Los wrappers de Steam no son argumentos Epic. No se convierten automáticamente.')
    return shlex.join(tokens[index + 1:])
