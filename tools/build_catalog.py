"""Rebuild the bundled, offline catalogue from explicit reviewed facts."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sources = {
 "drs": {"title": "DXVK-NVAPI · Passing driver settings",
         "url": "https://github.com/jp7677/dxvk-nvapi/wiki/Passing-driver-settings"},
 "sr": {"title": "NVIDIA · DLSS Programming Guide",
        "url": "https://github.com/NVIDIA/DLSS/blob/main/doc/DLSS_Programming_Guide_Release.pdf"},
 "sr45": {"title": "NVIDIA · DLSS 4.5 Super Resolution",
          "url": "https://www.nvidia.com/en-us/geforce/news/dlss-4-5-super-resolution-available-now/"},
 "dlss4": {"title": "NVIDIA · DLSS 4 y modelos transformer",
           "url": "https://www.nvidia.com/en-us/geforce/news/dlss4-multi-frame-generation-ai-innovations/"},
 "rr": {"title": "NVIDIA Streamline · presets de Ray Reconstruction",
        "url": "https://github.com/NVIDIAGameWorks/Streamline/blob/main/include/sl_dlss_d.h"},
 "rrguide": {"title": "NVIDIA · Guía de integración RR",
             "url": "https://github.com/NVIDIAGameWorks/Streamline/blob/main/docs/ProgrammingGuideDLSS_RR.md"},
 "fg": {"title": "NVIDIA · Guía Frame Generation",
        "url": "https://github.com/NVIDIAGameWorks/Streamline/blob/main/docs/ProgrammingGuideDLSS_G.md"},
 "hardware": {"title": "NVIDIA · Tecnologías y compatibilidad DLSS",
              "url": "https://www.nvidia.com/en-us/geforce/technologies/dlss/"},
}
def entry(key, title, generation, description, recommendation, cost, refs,
          status="Documentado", advanced=False, generatable=True):
    return dict(id=key, title=title, generation=generation, description=description,
                recommendation=recommendation, cost=cost, sources=refs,
                status=status, advanced=advanced, generatable=generatable)

def base(tech):
    return [
        entry("game", "Controlado por el juego", "Sin override",
              "No solicita un modelo distinto. El juego y sus componentes deciden el preset.",
              "Para comparar con el comportamiento original. No borra variables de tu comando previo.",
              "El del modelo que elija el juego.", ["drs"]),
        entry("latest", "Recomendado por NVIDIA · automático", "Depende del componente NGX",
              "Delega la elección al controlador y a NGX; no fija una letra. En SR, desde DLSS 4.5, "
              "«latest» significa recomendado: K para DLAA/Calidad/Equilibrado, M para Rendimiento y "
              "L para Ultra rendimiento. No asumas esa misma correspondencia en RR/FG.",
              "Si prefieres seguir la política automática compatible de NVIDIA.",
              "Variable: puede seleccionar un modelo más costoso.", ["drs", "sr45"])
    ]

sr = base("sr")
sr += [
 entry("K", "K · Transformer", "DLSS 4 · Super Resolution",
       "Modelo transformer de primera generación. La guía lo recomienda generalmente frente a J "
       "y lo usa como predeterminado para DLAA, Calidad y Equilibrado.",
       "Buen punto de partida en RTX 20/30 y referencia para comparar con L/M.",
       "Menor coste que L; mide FPS y estabilidad temporal en tu juego.", ["sr", "sr45"]),
 entry("L", "L · Transformer de 2.ª generación", "DLSS 4.5 · Super Resolution",
       "Modelo destinado a Ultra rendimiento, especialmente a salida 4K. Busca una imagen más "
       "nítida y estable y menos ghosting que J/K.",
       "Ultra rendimiento a 4K, si compensa su mayor coste. No es una mejora gratuita en una RTX 2060.",
       "Alto, especialmente en RTX 20/30 sin FP8 nativo.", ["sr", "sr45"]),
 entry("M", "M · Transformer de 2.ª generación", "DLSS 4.5 · Super Resolution",
       "Modelo optimizado para Rendimiento. La guía describe mejoras de imagen similares a L "
       "con una velocidad más cercana a J/K.",
       "Modo Rendimiento. En RTX 20/30 compara siempre con K antes de mantenerlo.",
       "Mayor impacto en RTX 20/30; no garantiza más FPS.", ["sr", "sr45"]),
 entry("J", "J · Transformer alternativo", "DLSS 4 · Super Resolution",
       "Similar a K: puede mostrar algo menos de ghosting a cambio de más parpadeo. NVIDIA "
       "recomienda generalmente K.",
       "Comparaciones específicas de estelas y parpadeo, no como opción universal.",
       "Depende del juego y del componente NGX.", ["sr"]),
]
for letter in "ABCDEF":
    sr.append(entry(letter, f"{letter} · modelo histórico", "Familia CNN · anterior a DLSS 4",
        "Preset histórico de Super Resolution. En la documentación actual A–D ya no están "
        "disponibles y E/F figuran como heredados con soporte deprecado. La letra no equivale "
        "a una versión comercial exacta de DLSS.",
        "Consulta histórica; no se recomienda para una configuración moderna.",
        "No se compara sin probar una versión concreta de la DLL.", ["sr"],
        status="Retirado" if letter in "ABCD" else "Heredado / deprecado",
        advanced=True, generatable=letter in "EF"))
for letter in "GHINO":
    sr.append(entry(letter, f"{letter} · reservado / sin modelo documentado", "Sin correspondencia fiable",
        "DXVK-NVAPI reconoce esta letra, pero eso no acredita un modelo utilizable. G/H/I "
        "revierten al comportamiento predeterminado en la guía; N/O no tienen una descripción "
        "de modelo revisada en este catálogo.",
        "No forzarlo. Usa K, L, M, J o la selección automática.",
        "No documentado.", ["sr", "drs"], status="Reservado / no documentado",
        advanced=True, generatable=False))

rr = base("rr")
for letter, desc in [("D", "Modelo transformer documentado."),
                     ("E", "Modelo transformer documentado; el encabezado no detalla ventajas frente a D."),
                     ("F", "Modelo transformer señalado como el más reciente y predeterminado en el encabezado revisado.")]:
    rr.append(entry(letter, f"{letter} · Transformer RR", "Ray Reconstruction · familia transformer",
        desc + " Las letras de RR son independientes de las de SR. No se atribuye una "
        "generación comercial exacta por letra sin documentación explícita.",
        "Juegos con RR integrado y trazado de rayos activado. Compara en reflejos, iluminación "
        "en movimiento y detalles finos.",
        "Depende mucho del trazado de rayos; en RTX 2060 puede ser considerable.", ["rr", "rrguide"]))
for letter in "ABCGHIJKLMNO":
    rr.append(entry(letter, f"{letter} · retirado / vuelve al predeterminado",
        "Sin modelo seleccionable recomendado",
        "A/B/C están retirados. El encabezado de NVIDIA indica que G–O revierten al "
        "modelo predeterminado; no corresponden a los presets SR de la misma letra.",
        "Usa D/E/F o automático.", "No procede.", ["rr", "rrguide"],
        status="Retirado" if letter in "ABC" else "Vuelve al predeterminado",
        advanced=True, generatable=False))
fg = base("fg")
fg.append(entry("B", "B · override documentado en DXVK-NVAPI",
    "Frame Generation · generación exacta no atribuida",
    "La wiki usa B como ejemplo válido de preset FG. No describe su ventaja visual ni permite "
    "asignarle una versión comercial exacta. No confundir con B de SR/RR.",
    "Pruebas avanzadas en RTX 40/50. Para uso normal, automático y el modo del juego.",
    "Depende del juego; los fotogramas generados no reducen por sí solos la latencia base.",
    ["drs", "fg"], status="Sintaxis documentada; comportamiento no detallado", advanced=True))
for letter in "ACDEFGHIJKLMNOPQRSTUVWXYZ":
    fg.append(entry(letter, f"{letter} · sin descripción pública revisada",
        "Generación no atribuida",
        "DXVK-NVAPI admite el identificador, pero el catálogo no tiene una descripción fiable "
        "de su comportamiento. No se inventan recomendaciones ni equivalencias.",
        "No forzarlo. Usa automático o controlado por el juego.", "No documentado.",
        ["drs", "fg"], status="Sin descripción verificada", advanced=True, generatable=False))

# Marketing generation, not a DLL version. Do not infer an exact release from
# a reserved letter or from another technology's preset alphabet.
for tech, models in (("sr", sr), ("rr", rr), ("fg", fg)):
    for model in models:
        key = model["id"]
        if key == "game":
            model["generation_label"] = "Generación del juego · sin fijar"
        elif key == "latest":
            model["generation_label"] = "Automático · generación variable"
        elif tech == "sr" and key in "JK":
            model["generation_label"] = "DLSS 4.0"
            model["generation"] = "DLSS 4.0 · Super Resolution / DLAA · Transformer"
        elif tech == "sr" and key in "LM":
            model["generation_label"] = "DLSS 4.5"
        elif tech == "sr" and key in "ABCDEF":
            model["generation_label"] = "DLSS 2.x / 3.x · CNN heredado"
            model["generation"] = "DLSS 2.x / 3.x · familia CNN; la letra no fija una versión exacta"
        elif tech == "rr" and key in "DEF":
            model["generation_label"] = "DLSS 4+ · Transformer RR"
            model["generation"] = ("Familia transformer de DLSS 4.0 o posterior · "
                                   "versión exacta de D/E/F no publicada")
            model["sources"].append("dlss4")
        elif tech == "fg" and key == "B":
            model["generation_label"] = "FG · versión exacta no publicada"
        else:
            model["generation_label"] = "Sin generación atribuible"

catalog = dict(version=2, reviewed="2026-10-29", sources=sources, technologies={
 "sr": dict(title="Super Resolution / DLAA", minimum="GeForce RTX 20 o superior", presets=sr),
 "rr": dict(title="Ray Reconstruction", minimum="GeForce RTX 20 o superior · juego con RR", presets=rr),
 "fg": dict(title="Frame Generation", minimum="RTX 40: FG 2× · RTX 50: MFG hasta 6× y dinámico", presets=fg),
})
(BASE / "nvidia_commands/data").mkdir(exist_ok=True)
(BASE / "nvidia_commands/data/catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
print("Catálogo generado:", sum(len(t["presets"]) for t in catalog["technologies"].values()), "entradas")
