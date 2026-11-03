"""Human-readable meaning of emitted values; no Qt or command execution."""
from .core import CATALOG, MODES, parse_drs

TECHNOLOGIES = {
    'SR': 'Super Resolution / DLAA: reconstrucción de la imagen a partir de una resolución interna menor, o antialiasing a resolución nativa',
    'RR': 'Ray Reconstruction: reconstrucción de la iluminación trazada por rayos, sustituyendo los denoisers compatibles del juego',
    'FG': 'Frame Generation: generación de fotogramas intermedios entre los renderizados por el juego',
}


def describe_drs(key, value):
    for tech, meaning in TECHNOLOGIES.items():
        stem = 'NGX_DLSS_' + tech
        if key == stem + '_OVERRIDE':
            return f'{value}: permite sustituir la configuración de {meaning}. No añade esta función a un juego que no la integra.'
        if key == stem + '_OVERRIDE_RENDER_PRESET_SELECTION':
            model_id = value.removeprefix('render_preset_').upper()
            model = next((p for p in CATALOG['technologies'][tech.lower()]['presets']
                          if p['id'].upper() == model_id), None)
            detail = f"{model['title']} ({model['generation_label']})" if model else value
            return f'Selecciona el modelo de {meaning}: {detail}. Cambia el algoritmo, no la resolución ni el modo de calidad.'
        if key == stem + '_MODE':
            modes = {
                'dlaa': 'antialiasing a resolución nativa, sin reescalado',
                'quality': 'prioriza detalle usando una resolución interna mayor que Equilibrado o Rendimiento',
                'balanced': 'equilibra calidad de imagen y coste de renderizado',
                'performance': 'reduce la resolución interna para priorizar FPS a costa de detalle',
                'ultra_performance': 'reduce aún más la resolución interna, con mayor pérdida potencial de detalle',
                'custom': 'usa el porcentaje de resolución interna indicado en SCALING_RATIO',
                'game': 'deja que el juego decida el modo',
            }
            return f'Modo de {tech}: {MODES.get(value, value)}; {modes.get(value, "valor importado, no interpretado por esta versión")}. No selecciona un preset de IA.'
        if key == stem + '_OVERRIDE_SCALING_RATIO':
            return f'Resolución interna solicitada para {tech}: {value} % de cada dimensión de salida. Menor porcentaje reduce el trabajo de renderizado y el detalle; 100 % usa resolución nativa.'
    if key == 'NGX_DLSSG_MODE':
        return {
            'on': 'Activa FG con multiplicador fijo: inserta fotogramas generados entre los renderizados. Necesita FG integrado y RTX 40/50.',
            'off': 'Solicita desactivar Frame Generation. No desactiva Super Resolution ni Ray Reconstruction.',
            'dynamic': 'Activa MFG dinámico en RTX 50: ajusta cuántos fotogramas se generan hasta el máximo seleccionado para aproximarse al objetivo FPS.',
        }.get(value, f'Modo FG importado ({value}); valor no interpretado por esta versión.')
    if key in ('NGX_DLSSG_MULTI_FRAME_COUNT', 'NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX'):
        try:
            n = int(value)
            return (f'Límite dinámico: hasta {n} fotograma(s) generado(s) por cada renderizado, equivalente a {n+1}× como máximo.'
                    if 'DYNAMIC' in key else
                    f'Multiplicador fijo: {n} fotograma(s) generado(s) por cada renderizado, equivalente a {n+1}× en total. No multiplica los FPS de simulación ni reduce la latencia en esa proporción.')
        except ValueError:
            return 'Conteo FG importado con formato no reconocido; no se puede deducir su multiplicador.'
    if key == 'NGX_DLSSG_DYNAMIC_TARGET_FRAME_RATE':
        return f'Objetivo del modo MFG dinámico: {value} FPS de salida, incluidos fotogramas generados. No es una medición ni una garantía, y no limita los FPS renderizados como un limitador convencional.'
    return 'Ajuste DRS conservado de tus parámetros actuales; su significado no está catalogado y no se atribuye a una función conocida.'


def describe_dxvk(key, value):
    scope = 'DirectX 9' if key.startswith('d3d9.') else 'DirectX 10/11' if key.startswith('d3d11.') else 'DirectX 10/11 mediante DXGI'
    if key.endswith('maxFrameRate'):
        return f'Limita a {value} FPS los fotogramas renderizados en {scope}; no cuenta los añadidos por FG o Smooth Motion.'
    if key.endswith(('syncInterval', 'presentInterval')):
        return f'{scope}: ' + ('solicita sincronizar la presentación con el refresco de la pantalla (VSync); puede añadir espera y latencia.' if value == '1' else 'solicita presentación sin espera de VSync; puede producir tearing según el compositor.')
    if key.endswith('samplerAnisotropy'):
        return f'{scope}: ' + ('desactiva el filtrado anisotrópico forzado.' if value == '0' else f'fuerza filtrado anisotrópico {value}× para mejorar texturas vistas en ángulo; puede alterar pases que necesitan filtrado bilineal.')
    if key.endswith('samplerLodBias'):
        return f'{scope}: sesgo de nivel de detalle de texturas {value}. Negativo favorece texturas más detalladas y posible parpadeo; positivo usa niveles menos detallados. No cambia la resolución del juego.'
    if key == 'dxvk.latencySleep':
        return ('Activa' if value.lower() == 'true' else 'Desactiva') + ' la espera de DXVK destinada a reducir la cola y la latencia. No fuerza NVIDIA Reflex; puede interferir con otros limitadores.'
    return 'Opción DXVK conservada de tus parámetros actuales; significado no catalogado en esta versión.'


def describe_environment(key, value):
    enabled = 'Activa' if value == '1' else 'Desactiva'
    descriptions = {
        'PROTON_ENABLE_NGX_UPDATER': 'Solicita a Proton la descarga/actualización de componentes NVIDIA NGX compatibles al iniciar el juego. No instala un controlador ni garantiza que el juego use el modelo elegido.',
        'NVPRESENT_ENABLE_SMOOTH_MOTION': f'{enabled} Smooth Motion: la capa NVIDIA Vulkan interpola fotogramas aunque el juego no integre DLSS FG. Necesita RTX 40/50, controlador compatible y VK_LAYER_NV_present. No combinar con FG.',
        'NVPRESENT_QUEUE_FAMILY': 'Selecciona la cola gráfica para la presentación de Smooth Motion (valor 1), como alternativa de compatibilidad con overlays. Puede reducir el rendimiento.',
        'DXVK_NVAPI_VKREFLEX': 'Habilita el puente de Reflex para juegos Windows/Vulkan mediante DXVK-NVAPI. Necesita integración Reflex en el juego y una capa compatible; no fuerza Reflex en juegos sin soporte.',
        'VKD3D_FRAME_RATE': f'Limita a {value} FPS el renderizado DirectX 12 traducido por VKD3D-Proton. No es el objetivo MFG ni cuenta fotogramas interpolados.',
        '__GL_SHARPEN_ENABLE': f'{enabled} el filtro de nitidez del controlador NVIDIA para OpenGL/Vulkan. Realza bordes; no reescala la imagen ni activa NIS. Base documentada R595+.',
        '__GL_SHARPEN_VALUE': f'Intensidad de nitidez: {value} sobre 100 (50 es el valor predeterminado). Aumentarla acentúa los bordes, pero puede producir halos; requiere nitidez activada.',
        '__GL_SHARPEN_IGNORE_FILM_GRAIN': f'Ajuste para ignorar grano al aplicar nitidez: {value} sobre 100 (17 es el valor predeterminado). Evita realzar ese ruido; no elimina por sí mismo el grano del juego.',
        '__GL_SYNC_TO_VBLANK': f'{enabled} la sincronización vertical OpenGL con el refresco de pantalla. VSync puede evitar tearing a cambio de espera y latencia; el compositor también interviene.',
        '__GL_THREADED_OPTIMIZATIONS': f'{enabled} las optimizaciones multihilo del controlador OpenGL. Pueden reducir carga en el hilo del juego o empeorar rendimiento según el título; no afectan a Vulkan.',
        '__GL_ALLOW_FXAA_USAGE': ('Permite' if value == '1' else 'Impide') + ' usar FXAA del controlador OpenGL si ya está habilitado en su perfil. Por sí sola esta variable no activa FXAA.',
        '__GL_VRR_ALLOWED': ('Permite' if value == '1' else 'Impide') + ' refresco variable (G-SYNC/VRR) para OpenGL. Requiere monitor y sesión configurados; no configura G-SYNC globalmente.',
        '__GL_SHADER_DISK_CACHE': f'{enabled} la caché en disco de shaders del controlador OpenGL, reutilizando compilaciones entre ejecuciones. No borra cachés ni modifica la precaché de Steam.',
        '__GL_SHOW_GRAPHICS_OSD': 'Muestra el indicador del controlador NVIDIA con API gráfica, FPS y presentación. No indica qué modelo de IA DLSS se está usando.',
        '__NGX_SHOW_INDICATOR': ('Muestra el indicador de Super Resolution NGX en Vulkan nativo (1024).' if value == '1024' else 'Oculta el indicador NGX de Vulkan nativo (0).') + ' Este ajuste es temporal para el proceso.',
        'DXVK_HDR': 'Expone la capacidad HDR al juego mediante DXVK. Requiere juego, monitor y cadena de presentación HDR; no convierte SDR en HDR ni equivale a RTX HDR.',
        'MANGOHUD': 'Activa MangoHud, superposición externa de métricas que debe estar instalada. Parámetro importado; no es una función del controlador NVIDIA.',
        'DXVK_HUD': f'Muestra métricas DXVK ({value}): fps = imágenes renderizadas por segundo; frametimes = tiempos de fotograma; gpuload = carga GPU; memory = memoria. No mide los fotogramas añadidos externamente.',
        '__NV_PRIME_RENDER_OFFLOAD': 'Solicita renderizado en la GPU NVIDIA de un equipo híbrido previamente configurado. No instala ni configura controladores.',
        '__GLX_VENDOR_LIBRARY_NAME': f'Selecciona la biblioteca GLX {value} para el contexto OpenGL del juego en equipos híbridos.',
        '__VK_LAYER_NV_optimus': f'Filtro de selección Vulkan {value}: NVIDIA_only expone solo GPU NVIDIA para favorecer su uso en un equipo híbrido.',
    }
    if key == '__GL_LOG_MAX_ANISO':
        try:
            factor = 2 ** int(value) if int(value) else 0
            return f'Filtrado anisotrópico OpenGL: valor logarítmico {value}, equivalente a {factor}× (0 = desactivado). Mejora texturas vistas en ángulo.'
        except ValueError:
            return 'Anisotropía OpenGL importada con valor no reconocido.'
    return descriptions.get(key, 'Variable conservada de tus parámetros actuales. No está catalogada; no se presupone su efecto ni su compatibilidad.')


def explain_result(result):
    if result.errors:
        return [('Comando no disponible', 'Corrige el conflicto indicado antes de copiar. No se genera un comando parcial.')]
    output = []
    for key, value in result.environment.items():
        token = f'{key}={value}'
        if key == 'DXVK_NVAPI_DRS_SETTINGS':
            output.append((key, 'Contiene los ajustes de perfil que DXVK-NVAPI entrega a NVIDIA NGX bajo Wine/Proton. Cada par nombre=valor separado por comas tiene el efecto indicado a continuación; no son argumentos del juego.'))
            for setting, val in parse_drs(value).items():
                output.append((f'{setting}={val}', describe_drs(setting, val)))
        elif key == 'DXVK_CONFIG':
            output.append((key, 'Configura la traducción de DirectX 9/10/11 a Vulkan mediante DXVK. Los pares separados por punto y coma son opciones independientes; no se aplican a DirectX 12.'))
            for item in value.split(';'):
                if '=' in item:
                    setting, val = (part.strip() for part in item.split('=', 1))
                    output.append((f'{setting}={val}', describe_dxvk(setting, val)))
        elif key == 'DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS':
            output.append((key, 'Configura indicadores NGX en el registro del prefijo Wine; persisten tras cerrar el juego. Reset solo limpia el generador: para ocultarlos, lanza una vez con Desactivar indicador.'))
            for item in value.split(','):
                if '=' in item:
                    setting, val = item.split('=', 1)
                    effect = 'el indicador DLSS Super Resolution' if setting == 'DLSSIndicator' else 'el indicador DLSS Frame Generation' if setting == 'DLSSGIndicator' else 'un indicador NGX importado no catalogado'
                    output.append((item, f'{"Oculta" if val == "0" else "Solicita mostrar"} {effect}; valor {val}, persistente en el prefijo Wine.'))
        else:
            output.append((token, describe_environment(key, value)))
    if result.command:
        output.append(('%command%', 'Steam sustituye este marcador por el ejecutable y los argumentos del juego. Las variables que lo preceden configuran ese proceso; no se pega este marcador en Epic.'))
    return output
