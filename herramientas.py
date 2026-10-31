#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
herramientas.py - un solo archivo para COMPILAR, INSTALAR y preparar las LIBRERIAS de cualquier .py de esta carpeta.

    python herramientas.py                 abre la interfaz (doble clic también vale)
    python herramientas.py info            estado: portable o instalado, rutas, autoarranque
    python herramientas.py deps            librerías que necesita el .py y cuales faltan  (--install las instala)
    python herramientas.py build           compila un ejecutable en esta carpeta           (--dry-run solo muestra el comando)
    python herramientas.py install         instala (programa + datos + cache + accesos + autoarranque)
    python herramientas.py portable        vuelve a modo portable (datos junto al programa)
    python herramientas.py uninstall       quita accesos, autoarranque y programa (los datos solo si se pide)
    python herramientas.py autostart on|off
    python herramientas.py launchers       crea herramientas.bat / .command / .sh (solo si quieres doble clic sin asociar .py)

Cada subcomando acepta el nombre del .py como primer argumento (por defecto widget_arena.py, o el único .py de la carpeta).
La configuración de cada .py se guarda en herramientas.json (se crea sola; solo guarda lo que cambias).
Ayuda completa: pestaña "Ayuda" de la interfaz o  python herramientas.py help
"""
import argparse
import ast
import datetime
import json
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import sysconfig
import threading
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, "herramientas.json")
MANIFEST_NAME = "install_manifest.json"
IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
IS_LINUX = not IS_WIN and not IS_MAC
DEFAULT_SCRIPT = "widget_arena.py"
CANCEL = threading.Event()
_PROCS = []


# ====================================================================== utilidades
def say(log, msg=""):
    (log or print)(msg)


def home():
    return os.path.expanduser("~")


def user_dirs(app_name):
    """Sitios habituales de cada sistema (solo para este usuario, sin permisos de administrador)."""
    if IS_WIN:
        local = os.environ.get("LOCALAPPDATA") or os.path.join(home(), "AppData", "Local")
        roam = os.environ.get("APPDATA") or os.path.join(home(), "AppData", "Roaming")
        return {"program": os.path.join(local, "Programs", app_name), "data": os.path.join(roam, app_name, "data"),
                "cache": os.path.join(local, app_name, "cache")}
    if IS_MAC:
        return {"program": os.path.join(home(), "Applications", app_name),
                "data": os.path.join(home(), "Library", "Application Support", app_name, "data"),
                "cache": os.path.join(home(), "Library", "Caches", app_name)}
    share = os.environ.get("XDG_DATA_HOME") or os.path.join(home(), ".local", "share")
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.join(home(), ".cache")
    return {"program": os.path.join(share, app_name, "app"), "data": os.path.join(share, app_name, "data"),
            "cache": os.path.join(cache, app_name)}


def run_cmd(cmd, log=None, cwd=None, env=None):
    """Ejecuta un comando mostrando su salida linea a linea. Devuelve el codigo de salida (se puede cancelar)."""
    say(log, "    $ " + " ".join('"%s"' % c if " " in str(c) else str(c) for c in cmd))
    flags = 0x08000000 if IS_WIN else 0
    try:
        p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             bufsize=1, errors="replace", creationflags=flags)
    except OSError as e:
        say(log, "    ERROR: no se pudo ejecutar: %s" % e)
        return 127
    _PROCS.append(p)
    try:
        for line in p.stdout:
            say(log, "    " + line.rstrip())
            if CANCEL.is_set():
                p.terminate()
                break
        p.wait()
    finally:
        if p in _PROCS:
            _PROCS.remove(p)
    return p.returncode


def cancel_all():
    CANCEL.set()
    for p in list(_PROCS):
        try:
            p.terminate()
        except Exception:
            pass


def now_stamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def file_count_size(path):
    n = s = 0
    for r, _d, fs in os.walk(path):
        for f in fs:
            n += 1
            try:
                s += os.path.getsize(os.path.join(r, f))
            except OSError:
                pass
    return n, s


def merge_copy(src, dst, overwrite=False, skip=(), log=None):
    """Copia el contenido de src en dst sin borrar nada. Por defecto NO sobrescribe lo que ya exista. Devuelve (copiados, saltados)."""
    copied = skipped = 0
    for r, dirs, fs in os.walk(src):
        rel = os.path.relpath(r, src)
        if rel == "." and skip:
            dirs[:] = [d for d in dirs if d not in skip]
        out = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(out, exist_ok=True)
        for f in fs:
            d = os.path.join(out, f)
            if os.path.exists(d) and not overwrite:
                skipped += 1
                continue
            shutil.copy2(os.path.join(r, f), d)
            copied += 1
    return copied, skipped


# ====================================================================== configuración por .py
def py_files():
    return sorted(f for f in os.listdir(APP_DIR) if f.endswith(".py") and os.path.isfile(os.path.join(APP_DIR, f))
                  and f != os.path.basename(__file__))


def pick_script(name=None):
    if name:
        return os.path.basename(name)
    fs = py_files()
    return DEFAULT_SCRIPT if DEFAULT_SCRIPT in fs else (fs[0] if fs else DEFAULT_SCRIPT)


def _load_cfg():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def default_project(script):
    stem = os.path.splitext(os.path.basename(script))[0]
    words = [w for w in re.split(r"[^A-Za-z0-9]+", stem) if w]
    app_name = "".join(w[:1].upper() + w[1:] for w in words) or "App"
    full = script if os.path.isabs(script) else os.path.join(APP_DIR, script)
    imps = scan_imports(full) if os.path.isfile(full) else set()
    tops = {i.split(".")[0] for i in imps}
    gui = bool(tops & {"PySide6", "PyQt5", "PyQt6", "tkinter", "wx", "kivy"})
    data = stem + "_data"
    seed = []
    for rel, dst in (("templates", "templates"), ("data/default.json", "data"), ("data/default_set.json", "data")):
        if os.path.exists(os.path.join(APP_DIR, data, rel.replace("/", os.sep))):
            seed.append([data + "/" + rel, dst])
    if os.path.isdir(os.path.join(APP_DIR, "defaults")):
        seed.append(["defaults", "."])
    return {
        "script": os.path.basename(script), "app_name": app_name, "data_dirname": data, "loc_file": stem + "_location.json",
        "env_data": stem.upper() + "_DATA", "env_cache": stem.upper() + "_CACHE_DIR",
        "extra_files": sorted(f for f in (os.listdir(APP_DIR) if os.path.isdir(APP_DIR) else [])
                              if f.endswith(".py") and f.startswith(stem + "_") and f != os.path.basename(script)),
        "windowed": gui, "onefile": IS_WIN, "icon": "", "collect_all": ["PySide6"] if "PySide6" in tops else [],
        "pip_extra": [], "extra_args": "", "seed": seed,
    }


def get_project(script=None):
    script = pick_script(script)
    p = default_project(script)
    p.update(_load_cfg().get(os.path.basename(script), {}))
    p["script"] = os.path.basename(script)
    return p


def save_project(p):
    cfg = _load_cfg()
    base = default_project(p["script"])
    mine = {k: v for k, v in p.items() if base.get(k) != v}
    if not p.get("seed_custom"):              # la semilla solo se guarda si la has editado (si no, se calcula sola cada vez)
        mine.pop("seed", None)
        mine.pop("seed_custom", None)
    cfg[p["script"]] = mine
    if not cfg[p["script"]]:
        cfg.pop(p["script"], None)
    if not cfg:                              # sin nada que recordar no se deja archivo
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        return
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def script_path(p):
    return p["script"] if os.path.isabs(p["script"]) else os.path.join(APP_DIR, p["script"])


# ====================================================================== dependencias
try:
    STDLIB = set(sys.stdlib_module_names)
except AttributeError:
    STDLIB = {"os", "sys", "json", "re", "time", "math", "random", "copy", "shutil", "ctypes", "hashlib", "datetime",
              "urllib", "subprocess", "threading", "queue", "tempfile", "zipfile", "base64", "io", "itertools", "functools",
              "collections", "traceback", "logging", "typing", "pathlib", "argparse", "tkinter", "sqlite3", "struct"}
PIP_NAMES = {"PIL": "Pillow", "cv2": "opencv-python", "yaml": "PyYAML", "bs4": "beautifulsoup4", "sklearn": "scikit-learn",
             "dateutil": "python-dateutil", "serial": "pyserial", "docx": "python-docx", "fitz": "PyMuPDF", "win32com": "pywin32",
             "win32api": "pywin32", "win32gui": "pywin32", "win32con": "pywin32", "pythoncom": "pywin32", "pywintypes": "pywin32",
             "OpenGL": "PyOpenGL", "Xlib": "python-xlib", "gi": "PyGObject", "attr": "attrs", "magic": "python-magic"}
ONLY_WIN = {"win32com", "win32api", "win32gui", "win32con", "pythoncom", "pywintypes", "winreg", "msvcrt", "_winapi", "comtypes", "wmi", "winsound"}
ONLY_MAC = {"objc", "AppKit", "Foundation", "Quartz", "Cocoa"}
ONLY_LINUX = {"Xlib", "gi", "dbus"}


def scan_imports(path, _seen=None):
    """Nombres importados (con puntos) por un .py y por los módulos locales de su carpeta que importa."""
    _seen = _seen if _seen is not None else set()
    path = os.path.abspath(path)
    if path in _seen or not os.path.isfile(path):
        return set()
    _seen.add(path)
    out = set()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        for n in names:
            top = n.split(".")[0]
            if top == "__future__":
                continue
            local = os.path.join(os.path.dirname(path), top + ".py")
            if os.path.isfile(local):
                out |= scan_imports(local, _seen)
            elif top not in STDLIB:
                out.add(n)
    return out


def needed_modules(p):
    """[(import, paquete pip, nota)] que necesita el .py, agrupadas por modulo de primer nivel (las de PySide6 con sus submodulos)."""
    imps = scan_imports(script_path(p))
    tops = sorted({i.split(".")[0] for i in imps})
    res = []
    for t in tops:
        if t in ONLY_WIN and not IS_WIN or t in ONLY_MAC and not IS_MAC or t in ONLY_LINUX and not IS_LINUX:
            res.append((t, PIP_NAMES.get(t, t), "no aplica en este sistema"))
        else:
            res.append((t, PIP_NAMES.get(t, t), ""))
    for extra in p.get("pip_extra", []):
        res.append((extra, extra, "extra"))
    return res


def check_modules(py_exe, mods, subs=()):
    """Pregunta al Python elegido que módulos hay: {nombre: version|True|False}. 'subs' = submodulos con punto a comprobar también."""
    code = ("import importlib.util as u, importlib.metadata as m, json, sys\n"
            "req=json.loads(sys.argv[1]); out={}\n"
            "for n,pip in req:\n"
            "    try: ok=u.find_spec(n) is not None\n"
            "    except Exception: ok=False\n"
            "    v=None\n"
            "    if ok:\n"
            "        try: v=m.version(pip)\n"
            "        except Exception: v=True\n"
            "    out[n]=v if ok else False\n"
            "print(json.dumps(out))\n")
    req = [[n, pip] for n, pip, _ in mods] + [[s, s.split(".")[0]] for s in subs]
    try:
        r = subprocess.run([py_exe, "-c", code, json.dumps(req)], capture_output=True, text=True, timeout=120,
                           creationflags=0x08000000 if IS_WIN else 0)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return {n: False for n, _p, _x in mods}


def qt_submodules(p):
    return sorted(i for i in scan_imports(script_path(p)) if i.startswith("PySide6."))


def python_candidates():
    found = []

    def add(path):
        if path and os.path.isfile(path) and path not in found:
            found.append(path)
    add(sys.executable)
    if IS_WIN:
        try:
            out = subprocess.run(["py", "-0p"], capture_output=True, text=True, creationflags=0x08000000).stdout
            for line in out.splitlines():
                add(line.split()[-1] if line.strip() else None)
        except OSError:
            pass
    for n in ("python3", "python"):
        add(shutil.which(n))
    return found


def externally_managed(py_exe=None):
    """PEP 668: en Debian, Ubuntu o Linux Mint pip no deja instalar en el Python del sistema (hace falta un entorno aislado)."""
    if py_exe and os.path.abspath(py_exe) != os.path.abspath(sys.executable):
        try:
            r = subprocess.run([py_exe, "-c", "import sysconfig,os;print(os.path.exists(os.path.join(sysconfig.get_path('stdlib'),'EXTERNALLY-MANAGED')))"],
                               capture_output=True, text=True)
            return r.stdout.strip() == "True" and sys.prefix == getattr(sys, "base_prefix", sys.prefix)
        except OSError:
            return False
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    return (not in_venv) and os.path.exists(os.path.join(sysconfig.get_path("stdlib"), "EXTERNALLY-MANAGED"))


def venv_python(venv_dir):
    return os.path.join(venv_dir, "Scripts", "python.exe") if IS_WIN else os.path.join(venv_dir, "bin", "python")


def venv_ok(venv_dir):
    """Un entorno es utilizable si tiene su python.exe, su pyvenv.cfg y el python arranca. Un entorno a medias (por ejemplo de una
    instalacion que fallo) tiene python.exe pero no pyvenv.cfg: 'No pyvenv.cfg file' al usarlo."""
    py = venv_python(venv_dir)
    if not (os.path.isfile(py) and os.path.isfile(os.path.join(venv_dir, "pyvenv.cfg"))):
        return False
    try:
        r = subprocess.run([py, "-c", "import sys"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90,
                           creationflags=(0x08000000 if IS_WIN else 0))
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def ensure_venv(venv_dir, log=None):
    py = venv_python(venv_dir)
    if venv_ok(venv_dir):
        return py
    if os.path.isdir(venv_dir):
        say(log, "==> El entorno aislado anterior esta incompleto o roto: se rehace (%s)" % venv_dir)
        import shutil
        shutil.rmtree(venv_dir, ignore_errors=True)
    say(log, "==> Creando entorno aislado en %s" % venv_dir)
    code = run_cmd([sys.executable, "-m", "venv", venv_dir], log)
    if code != 0 or not venv_ok(venv_dir):
        hint = "  (en Linux Mint/Ubuntu:  sudo apt install python3-venv)" if IS_LINUX else ""
        raise RuntimeError("no se pudo crear el entorno aislado%s" % hint)
    return py


def pip_install(py_exe, pkgs, log=None):
    if not pkgs:
        return True
    say(log, "==> pip install %s" % " ".join(pkgs))
    return run_cmd([py_exe, "-m", "pip", "install", "--upgrade"] + list(pkgs), log) == 0


def install_missing(p, py_exe, log=None):
    """Instala en py_exe lo que falte. Devuelve (ok, lista de paquetes que siguen sin estar)."""
    mods = [m for m in needed_modules(p) if not m[2].startswith("no aplica")]
    st = check_modules(py_exe, mods)
    pkgs = sorted({pip for n, pip, _x in mods if not st.get(n)})
    if pkgs and not pip_install(py_exe, pkgs, log):
        say(log, "    AVISO: pip no pudo instalar todo")
    st = check_modules(py_exe, mods)
    subs = qt_submodules(p)
    if subs and st.get("PySide6"):
        ss = check_modules(py_exe, [], subs)
        bad = [s for s in subs if not ss.get(s)]
        if bad:
            ver = st.get("PySide6") if isinstance(st.get("PySide6"), str) else None
            say(log, "==> Faltan módulos de Qt (%s): se prueba el paquete aparte con la misma version" % ", ".join(bad))
            if any("WebEngine" in b for b in bad):
                pip_install(py_exe, ["PySide6-WebEngine==%s" % ver] if ver else ["PySide6-WebEngine"], log)
            ss = check_modules(py_exe, [], subs)
            bad = [s for s in subs if not ss.get(s)]
            if bad:
                say(log, "    AVISO: siguen sin estar: %s" % ", ".join(bad))
    left = [pip for n, pip, _x in mods if not check_modules(py_exe, [(n, pip, "")]).get(n)]
    return (not left), sorted(set(left))


# ====================================================================== compilar
def artifact(p):
    """(tipo, ruta) del ejecutable compilado si existe: ('file'|'dir'|'app', ruta) o (None, ruta_esperada)."""
    name = os.path.splitext(p["script"])[0]
    exe = os.path.join(APP_DIR, name + (".exe" if IS_WIN else ""))
    app = os.path.join(APP_DIR, name + ".app")
    folder = os.path.join(APP_DIR, name)
    if IS_MAC and os.path.isdir(app):
        return "app", app
    if os.path.isfile(exe):
        return "file", exe
    if os.path.isfile(os.path.join(folder, name + (".exe" if IS_WIN else ""))):
        return "dir", folder
    return None, exe


def seed_args(p, log=None):
    out = []
    for src_rel, dst_rel in p.get("seed", []):
        src = src_rel if os.path.isabs(src_rel) else os.path.join(APP_DIR, src_rel.replace("/", os.sep))
        if not os.path.exists(src):
            say(log, "    AVISO: semilla omitida (no existe): %s" % src)
            continue
        dst = "/".join(x for x in (p["data_dirname"], str(dst_rel).replace("\\", "/").strip("/")) if x and x != ".")
        out += ["--add-data", "%s%s%s" % (src, os.pathsep, dst)]
    return out


def build_command(p, builder, log=None):
    name = os.path.splitext(p["script"])[0]
    onefile = p.get("onefile", IS_WIN) and not IS_MAC          # macOS: QtWebEngine no funciona en un solo fichero (se usa carpeta/.app)
    cmd = [builder, "-m", "PyInstaller", "--noconfirm", "--clean"]
    if onefile:
        cmd.append("--onefile")
    if p.get("windowed", True):
        cmd.append("--windowed")
    cmd += ["--name", name]
    if p.get("icon"):
        cmd += ["--icon", p["icon"]]
    for pk in p.get("collect_all", []):
        cmd += ["--collect-all", pk]
    cmd += seed_args(p, log)
    cmd += (p.get("extra_args") or "").split()
    cmd += ["--paths", APP_DIR, "--specpath", APP_DIR, "--workpath", os.path.join(APP_DIR, "build"), "--distpath", APP_DIR,
            script_path(p)]
    return cmd


def find_builder(p, log=None):
    """Un Python con PyInstaller y las librerías del .py (para que PyInstaller las encuentre). Si ninguno las tiene, las instala
    (en un entorno aislado .venv_build si el sistema no deja instalar en el Python global)."""
    need = [("PyInstaller", "pyinstaller", "")] + [(x, x, "") for x in p.get("collect_all", [])]
    for exe in python_candidates():
        st = check_modules(exe, need)
        if all(st.get(n) for n, _a, _b in need):
            return exe
    exe = sys.executable
    if externally_managed():
        exe = ensure_venv(os.path.join(APP_DIR, ".venv_build"), log)
    say(log, "==> Preparando entorno de compilación en %s" % exe)
    if not pip_install(exe, ["pyinstaller"], log):
        raise RuntimeError("no se pudo instalar PyInstaller")
    install_missing(p, exe, log)
    return exe


def remove_path(path, log=None):
    if not os.path.exists(path):
        return
    try:
        shutil.rmtree(path) if os.path.isdir(path) and not os.path.islink(path) else os.remove(path)
        say(log, "    borrado: " + os.path.basename(path))
    except PermissionError:
        raise RuntimeError("no se puede borrar '%s': cierra el programa (administrador de tareas) y vuelve a compilar" % path)


def build(p, log=None, dry_run=False):
    """Compila el .py en esta carpeta. Devuelve la ruta del resultado (o la orden en dry_run)."""
    CANCEL.clear()
    src = script_path(p)
    if not os.path.isfile(src):
        raise RuntimeError("no existe " + src)
    t0 = time.time()
    name = os.path.splitext(p["script"])[0]
    say(log, "==> Plataforma: %s | Python %s" % (platform.platform(), platform.python_version()))
    if dry_run:
        cmd = build_command(p, sys.executable, log)
        say(log, "    " + " ".join(cmd))
        return cmd
    builder = find_builder(p, log)
    say(log, "==> Compilador: %s" % builder)
    say(log, "==> Limpieza: .spec desactualizado y compilación anterior")
    kind, old = artifact(p)
    remove_path(os.path.join(APP_DIR, name + ".spec"), log)
    remove_path(os.path.join(APP_DIR, "build"), log)
    if kind:
        remove_path(old, log)
    remove_path(os.path.join(APP_DIR, name + ".app"), log)
    cmd = build_command(p, builder, log)
    say(log, "==> Ejecutando PyInstaller (tarda unos minutos)")
    code = run_cmd(cmd, log, cwd=APP_DIR)
    if CANCEL.is_set():
        raise RuntimeError("cancelado")
    if code != 0:
        raise RuntimeError("PyInstaller ha fallado (codigo %d)" % code)
    kind, out = artifact(p)
    if not kind:
        raise RuntimeError("no se ha generado el ejecutable")
    remove_path(os.path.join(APP_DIR, name + ".spec"), log)           # temporales de PyInstaller: ya no hacen falta
    remove_path(os.path.join(APP_DIR, "build"), log)
    n, size = file_count_size(out) if os.path.isdir(out) else (1, os.path.getsize(out))
    say(log, "==> LISTO en %.1f s -> %s (%.0f MB)" % (time.time() - t0, out, size / 1048576.0))
    return out


# ====================================================================== instalación
def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _abs_from(base, v):
    if not v:
        return None
    v = os.path.expanduser(os.path.expandvars(str(v)))
    return os.path.abspath(v if os.path.isabs(v) else os.path.join(base, v))


def status(p, program_dir=None):
    """Estado de este .py: portable o instalado. Mira la carpeta donde esta herramientas.py y la instalación habitual."""
    d = {"mode": "portable", "program_dir": APP_DIR, "data_dir": os.path.join(APP_DIR, p["data_dirname"]), "cache_dir": None,
         "installed_elsewhere": None, "autostart": False}
    loc = read_json(os.path.join(APP_DIR, p["loc_file"]))
    if loc.get("data_dir"):
        d.update(mode="instalado", data_dir=_abs_from(APP_DIR, loc["data_dir"]), cache_dir=_abs_from(APP_DIR, loc.get("cache_dir")))
    else:
        for cand in filter(None, [program_dir, p.get("install_dir"), user_dirs(p["app_name"])["program"]]):
            if read_json(os.path.join(cand, MANIFEST_NAME)).get("installed"):
                d["installed_elsewhere"] = cand
                break
    d["autostart"] = is_autostart(p)
    return d


LAUNCHER_SRC = r'''# Lanzador de __APP__ (lo crea herramientas.py; no hace falta tocarlo).
# Arranca el programa SIN ventana de consola y deja todo lo que escriba en "arranque.log" (junto a este archivo).
# Si el programa no llega a abrirse, avisa con una ventana que dice por que y donde esta el registro.
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "__SCRIPT__")
LOG = os.path.join(HERE, "arranque.log")
TITLE = "__APP__"
WAIT = 20.0          # segundos que se vigila el arranque


def log(msg):
    try:
        with open(LOG, "ab") as f:
            f.write(("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)).encode("utf-8", "replace"))
    except OSError:
        pass


def rotate():
    try:
        if os.path.getsize(LOG) > 400000:
            with open(LOG, "rb") as f:
                f.seek(-150000, 2)
                tail = f.read()
            with open(LOG, "wb") as f:
                f.write(b"(...registro anterior recortado...)\n" + tail)
    except OSError:
        pass


def tail(n=12):
    try:
        with open(LOG, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 6000))
            lines = f.read().decode("utf-8", "replace").splitlines()
        return "\n".join(l[:160] for l in lines[-n:])
    except OSError:
        return ""


def alert(text):
    try:
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, TITLE, 0x10)
        elif sys.platform == "darwin":
            q = text.replace("\\", "\\\\").replace('"', '\\"')
            subprocess.run(["osascript", "-e", 'display dialog "%s" with title "%s" buttons {"OK"} with icon stop' % (q, TITLE)], timeout=600)
        else:
            import shutil
            for cmd in (["zenity", "--error", "--no-markup", "--title", TITLE, "--text", text],
                        ["kdialog", "--error", text, "--title", TITLE]):
                if shutil.which(cmd[0]) and subprocess.run(cmd, timeout=600).returncode in (0, 1):
                    return
            try:
                import tkinter
                from tkinter import messagebox
                r = tkinter.Tk()
                r.withdraw()
                messagebox.showerror(TITLE, text, parent=r)
                r.destroy()
            except Exception:
                if shutil.which("notify-send"):
                    subprocess.run(["notify-send", TITLE, text[:300]])
    except Exception:
        pass


def hint_for(txt):
    low = txt.lower()
    if "dll load failed" in low:
        return ("\n\nPosible causa: falta el componente 'Microsoft Visual C++ Redistributable' de Windows. "
                "Instalalo desde https://aka.ms/vs/17/release/vc_redist.x64.exe y vuelve a abrir el programa.")
    if "no module named" in low:
        return "\n\nPosible causa: faltan librerias. Vuelve a ejecutar el instalador: las repone."
    if "libxcb" in low or "could not load the qt platform plugin" in low:
        return "\n\nPosible causa: faltan librerias del sistema que usa Qt (en Linux, libxcb-cursor0 y similares). Vuelve a ejecutar el instalador."
    return ""


def fail(why):
    t = tail()
    alert("%s no ha podido abrirse.\n\n%s\n\nUltimas lineas del registro:\n%s\n\nRegistro completo:\n%s%s" % (TITLE, why, t, LOG, hint_for(t)))


def main():
    rotate()
    log("=== arranque === python %s (%s) en %s" % (sys.version.split()[0], sys.executable, sys.platform))
    if not os.path.isfile(SCRIPT):
        log("ERROR: no existe %s" % SCRIPT)
        fail("No se encuentra el programa (%s)." % SCRIPT)
        return
    py = sys.executable
    if os.name == "nt" and os.path.basename(py).lower() == "pythonw.exe":
        cand = os.path.join(os.path.dirname(py), "python.exe")      # el programa corre con python.exe (sin ventana) para tener salida de errores
        if os.path.isfile(cand):
            py = cand
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000 | 0x00000200              # sin ventana + grupo propio
    else:
        kw["start_new_session"] = True
    t0 = time.time()
    with open(LOG, "ab") as out:
        p = subprocess.Popen([py, "-u", SCRIPT], cwd=HERE, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, env=env, **kw)
    log("lanzado con %s (pid %d)" % (py, p.pid))
    rc = None
    while time.time() - t0 < WAIT:
        rc = p.poll()
        if rc is not None:
            break
        time.sleep(0.25)
    if rc is None:
        log("sigue abierto a los %d s: arranque correcto" % WAIT)
        return
    dur = time.time() - t0
    log("TERMINO a los %.1f s con codigo %s" % (dur, rc))
    if rc != 0 or dur < 3:
        fail("El programa se cerro a los %.0f segundos (codigo %s)." % (dur, rc))


try:
    main()
except Exception:
    import traceback
    log("ERROR en el lanzador:\n" + traceback.format_exc())
    fail("Fallo el lanzador.")
'''


def launcher_name(p):
    return os.path.splitext(p["script"])[0] + "_lanzador.pyw"


def write_launcher(p, program_dir):
    """Crea junto al programa el lanzador que deja el registro de arranque (arranque.log) y avisa si no se abre."""
    path = os.path.join(program_dir, launcher_name(p))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(LAUNCHER_SRC.replace("__APP__", p["app_name"]).replace("__SCRIPT__", p["script"]))
    return path


def launch_command(p, program_dir, mode, py_exe=None):
    """Orden que arranca la aplicación instalada."""
    if mode == "exe":
        name = os.path.splitext(p["script"])[0]
        app = os.path.join(program_dir, name + ".app")
        if os.path.isdir(app):
            return ["open", app]
        return [os.path.join(program_dir, name + (".exe" if IS_WIN else ""))]
    py = py_exe or sys.executable
    if IS_WIN and os.path.basename(py).lower() == "python.exe":
        pw = os.path.join(os.path.dirname(py), "pythonw.exe")
        if os.path.isfile(pw):
            py = pw
    lanz = os.path.join(program_dir, launcher_name(p))
    return [py, lanz if os.path.isfile(lanz) else os.path.join(program_dir, p["script"])]


def _q(args):
    return " ".join('"%s"' % a if (" " in a or not a) else a for a in args)


def _desktop_entry(p, cmd, program_dir, autostart=False):
    ex = " ".join('"%s"' % a.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") for a in cmd)
    return ("[Desktop Entry]\nType=Application\nName=%s\nComment=%s\nExec=%s\nPath=%s\nTerminal=false\nCategories=Utility;\n%s"
            % (p["app_name"], p["app_name"], ex, program_dir, "X-GNOME-Autostart-enabled=true\n" if autostart else ""))


def _win_shortcut(path, cmd, workdir, log=None):
    q = lambda s: str(s).replace("'", "''")
    ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%s');$s.TargetPath='%s';$s.Arguments='%s';"
          "$s.WorkingDirectory='%s';$s.Save()" % (q(path), q(cmd[0]), q(_q(cmd[1:])), q(workdir)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return run_cmd(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], log) == 0


def _win_folder(kind):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('%s')" % kind],
                             capture_output=True, text=True, creationflags=0x08000000).stdout.strip()
        if out:
            return out
    except OSError:
        pass
    if kind == "Desktop":
        return os.path.join(home(), "Desktop")
    return os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")


def _linux_desktop_dir():
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True).stdout.strip()
        if out and os.path.isdir(out):
            return out
    except OSError:
        pass
    d = os.path.join(home(), "Desktop")
    return d if os.path.isdir(d) else None


def create_shortcuts(p, cmd, program_dir, desktop, menu, man, log=None):
    name = p["app_name"]
    made = []
    if IS_WIN:
        targets = []
        if desktop:
            targets.append(os.path.join(_win_folder("Desktop"), name + ".lnk"))
        if menu:
            targets.append(os.path.join(_win_folder("Programs"), name + ".lnk"))
        for t in targets:
            if _win_shortcut(t, cmd, program_dir, log):
                made.append(t)
    elif IS_MAC:
        if desktop or menu:
            t = os.path.join(program_dir, name + ".command")
            with open(t, "w", encoding="utf-8") as f:
                f.write("#!/bin/bash\ncd \"$(dirname \"$0\")\"\nexec %s\n" % _q(cmd))
            os.chmod(t, 0o755)
            made.append(t)
    else:
        entry = _desktop_entry(p, cmd, program_dir)
        dests = []
        if menu:
            dests.append(os.path.join(os.environ.get("XDG_DATA_HOME") or os.path.join(home(), ".local", "share"), "applications", name + ".desktop"))
        if desktop and _linux_desktop_dir():
            dests.append(os.path.join(_linux_desktop_dir(), name + ".desktop"))
        for t in dests:
            os.makedirs(os.path.dirname(t), exist_ok=True)
            with open(t, "w", encoding="utf-8") as f:
                f.write(entry)
            os.chmod(t, 0o755)
            try:
                subprocess.run(["gio", "set", t, "metadata::trusted", "true"], capture_output=True)   # Cinnamon/GNOME: lanzador de confianza
            except OSError:
                pass
            made.append(t)
    for t in made:
        man.setdefault("shortcuts", []).append(t)
        say(log, "    acceso directo: %s" % t)
    return made


def autostart_path(p):
    if IS_LINUX:
        return os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(home(), ".config"), "autostart", p["app_name"] + ".desktop")
    if IS_MAC:
        return os.path.join(home(), "Library", "LaunchAgents", "com.user.%s.plist" % p["app_name"].lower())
    return r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run\%s" % p["app_name"]


def set_autostart(p, cmd, program_dir, on, man=None, log=None):
    path = autostart_path(p)
    try:
        if IS_WIN:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            try:
                if on:
                    winreg.SetValueEx(key, p["app_name"], 0, winreg.REG_SZ, _q(cmd))
                else:
                    try:
                        winreg.DeleteValue(key, p["app_name"])
                    except FileNotFoundError:
                        pass
            finally:
                winreg.CloseKey(key)
        elif on:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if IS_MAC:
                args = "".join("    <string>%s</string>\n" % a for a in cmd)
                txt = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<plist version=\"1.0\"><dict>\n<key>Label</key><string>com.user.%s</string>\n"
                       "<key>ProgramArguments</key><array>\n%s</array>\n<key>RunAtLoad</key><true/>\n<key>WorkingDirectory</key><string>%s</string>\n"
                       "</dict></plist>\n" % (p["app_name"].lower(), args, program_dir))
            else:
                txt = _desktop_entry(p, cmd, program_dir, autostart=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
        elif os.path.exists(path):
            os.remove(path)
    except Exception as e:
        say(log, "    AVISO: arranque automático: %s" % e)
        return False
    say(log, "    arranque automático %s: %s" % ("activado" if on else "quitado", path))
    if man is not None:
        man["autostart"] = bool(on)
        man["autostart_path"] = path
    return True


def is_autostart(p):
    if IS_WIN:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
            winreg.QueryValueEx(key, p["app_name"])
            return True
        except Exception:
            return False
    return os.path.exists(autostart_path(p))


def plan_defaults(p, mode="script"):
    d = user_dirs(p["app_name"])
    return {"mode": mode, "program_dir": d["program"], "data_dir": d["data"], "cache_dir": d["cache"], "move_data": False,
            "desktop": True, "menu": True, "autostart": False, "deps": True, "venv": "auto",
            "source_data": os.path.join(APP_DIR, p["data_dirname"])}


def install(p, plan, log=None):
    """Instala para este usuario: programa, datos, caché, ubicación, librerías, accesos y arranque automático.
    Nada se borra: con 'mover datos' los originales se renombran a <carpeta>.migrado_FECHA."""
    CANCEL.clear()
    pd, dd, cd = [os.path.abspath(plan[k]) for k in ("program_dir", "data_dir", "cache_dir")]
    if pd == APP_DIR:
        raise RuntimeError("la carpeta del programa no puede ser la misma de origen (elige otra)")
    if not os.path.isfile(script_path(p)):
        raise RuntimeError("no existe " + script_path(p))
    mode = plan.get("mode", "script")
    if mode == "exe" and not artifact(p)[0]:
        raise RuntimeError("no hay ejecutable compilado: compila primero (pestaña Compilar)")
    man = read_json(os.path.join(pd, MANIFEST_NAME))
    man.update(installed=True, app=p["app_name"], script=p["script"], mode=mode, program_dir=pd, data_dir=dd, cache_dir=cd,
               installed_at=datetime.datetime.now().isoformat(timespec="seconds"), shortcuts=[])
    man.pop("portable", None)
    say(log, "==> Programa en %s" % pd)
    os.makedirs(pd, exist_ok=True)
    # 1) programa
    if mode == "exe":
        kind, art = artifact(p)
        if kind == "file":
            shutil.copy2(art, os.path.join(pd, os.path.basename(art)))
        elif kind == "dir":
            merge_copy(art, pd, overwrite=True)
        else:
            shutil.copytree(art, os.path.join(pd, os.path.basename(art)), dirs_exist_ok=True)
    else:
        for f in [p["script"]] + list(p.get("extra_files", [])):
            src = os.path.join(APP_DIR, f)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(pd, f))
        if os.path.isdir(os.path.join(APP_DIR, "defaults")):
            merge_copy(os.path.join(APP_DIR, "defaults"), os.path.join(pd, "defaults"), overwrite=True)
    for f in (os.path.basename(__file__), "herramientas.json"):          # el instalador viaja con el programa (desinstalar / volver a portable)
        if os.path.isfile(os.path.join(APP_DIR, f)):
            shutil.copy2(os.path.join(APP_DIR, f), os.path.join(pd, f))
    # 2) datos
    src_data = plan.get("source_data") or os.path.join(APP_DIR, p["data_dirname"])
    os.makedirs(dd, exist_ok=True)
    os.makedirs(cd, exist_ok=True)
    if os.path.isdir(src_data) and os.path.abspath(src_data) != dd:
        say(log, "==> Datos: %s -> %s" % (src_data, dd))
        c, s = merge_copy(src_data, dd, overwrite=bool(plan.get("overwrite_data")), skip=("cache",), log=log)
        say(log, "    copiados %d archivos (%d ya estaban y no se tocan); la caché no se copia (se regenera)" % (c, s))
        if plan.get("move_data"):
            miss = []
            for r, _d, fs in os.walk(src_data):
                rel0 = os.path.relpath(r, src_data).split(os.sep)[0]
                if rel0 == "cache":
                    continue
                for f in fs:
                    if not os.path.exists(os.path.join(dd, os.path.relpath(os.path.join(r, f), src_data))):
                        miss.append(f)
            if miss:
                raise RuntimeError("la copia de datos no esta completa (%d archivos faltan); no se mueve nada" % len(miss))
            moved = src_data + ".migrado_" + now_stamp()
            os.rename(src_data, moved)
            man["data_migrated_from"] = moved
            say(log, "    originales apartados en %s (borralos tu cuando compruebes que todo va bien)" % moved)
    # 3) ubicación que lee la aplicación
    loc = os.path.join(pd, p["loc_file"])
    write_json(loc, {"installed": True, "app": p["app_name"], "data_dir": dd, "cache_dir": cd})
    man["location_file"] = loc
    say(log, "==> Ubicación guardada en %s" % loc)
    # 4) librerías
    py = None
    if mode == "script":
        py = sys.executable
        use_venv = plan.get("venv", "auto")
        if use_venv == "auto":
            use_venv = externally_managed()
        if use_venv:
            py = ensure_venv(os.path.join(pd, ".venv"), log)
            man["venv"] = os.path.join(pd, ".venv")
        if plan.get("deps", True):
            ok, left = install_missing(p, py, log)
            say(log, "==> Librerías: " + ("todo instalado" if ok else "faltan: %s" % ", ".join(left)))
    if mode == "script":
        man["launcher"] = write_launcher(p, pd)
        say(log, "==> Lanzador (deja el registro en %s)" % os.path.join(pd, "arranque.log"))
    cmd = launch_command(p, pd, mode, py)
    man["command"] = cmd
    # 5) accesos directos y arranque automático
    if plan.get("desktop") or plan.get("menu"):
        create_shortcuts(p, cmd, pd, plan.get("desktop"), plan.get("menu"), man, log)
    man["autostart"] = False
    man.pop("autostart_path", None)
    if plan.get("autostart"):
        set_autostart(p, cmd, pd, True, man, log)
    elif is_autostart(p):                                      # lo marcado es lo que queda: sin la casilla se quita el arranque anterior
        set_autostart(p, cmd, pd, False, man, log)
    write_json(os.path.join(pd, MANIFEST_NAME), man)
    p["install_dir"] = pd                                      # se recuerda para encontrar la instalación desde la carpeta de origen
    save_project(p)
    say(log, "==> LISTO. Instalado en %s" % pd)
    return man


def uninstall(p, program_dir, remove_data=False, remove_cache=True, log=None):
    pd = os.path.abspath(program_dir)
    man = read_json(os.path.join(pd, MANIFEST_NAME))
    if not man.get("installed"):
        raise RuntimeError("no hay una instalación en %s" % pd)
    say(log, "==> Desinstalando %s" % pd)
    if is_autostart(p):
        set_autostart(p, man.get("command") or [], pd, False, None, log)
    for t in man.get("shortcuts", []):
        try:
            os.remove(t)
            say(log, "    quitado: %s" % t)
        except OSError:
            pass
    dd, cd = man.get("data_dir"), man.get("cache_dir")
    if remove_cache and cd and os.path.isdir(cd):
        shutil.rmtree(cd, ignore_errors=True)
        say(log, "    caché borrada: %s" % cd)
    if remove_data and dd and os.path.isdir(dd):
        shutil.rmtree(dd, ignore_errors=True)
        say(log, "    datos borrados: %s" % dd)
    elif dd:
        say(log, "    los datos se conservan en %s" % dd)
    keep = os.path.abspath(dd) if (dd and not remove_data and os.path.abspath(dd).startswith(pd + os.sep)) else None
    os.chdir(os.path.dirname(pd) or home())
    for entry in os.listdir(pd):
        full = os.path.join(pd, entry)
        if keep and (full == keep or keep.startswith(full + os.sep)):
            continue
        shutil.rmtree(full, ignore_errors=True) if os.path.isdir(full) else os.remove(full)
    if not keep:
        try:
            os.rmdir(pd)
        except OSError:
            pass
    if p.get("install_dir") and os.path.abspath(p["install_dir"]) == pd:
        p.pop("install_dir", None)
        save_project(p)
    say(log, "==> LISTO")


def to_portable(p, program_dir, move=False, log=None):
    """Datos junto al programa (<programa>/<nombre>_data) y sin archivo de ubicación: la aplicación vuelve a ser portable."""
    pd = os.path.abspath(program_dir)
    loc_path = os.path.join(pd, p["loc_file"])
    dd = read_json(loc_path).get("data_dir")
    if not dd:
        raise RuntimeError("esa carpeta ya es portable (no hay archivo de ubicación)")
    dst = os.path.join(pd, p["data_dirname"])
    if os.path.abspath(dd) != dst:
        say(log, "==> Datos: %s -> %s" % (dd, dst))
        c, s = merge_copy(dd, dst)
        say(log, "    copiados %d archivos (%d ya estaban)" % (c, s))
        if move:
            os.rename(dd, dd + ".migrado_" + now_stamp())
            say(log, "    originales apartados en %s.migrado_..." % dd)
    os.remove(loc_path)
    man = read_json(os.path.join(pd, MANIFEST_NAME))
    man.update(installed=False, portable=True, data_dir=dst)
    write_json(os.path.join(pd, MANIFEST_NAME), man)
    say(log, "==> LISTO. %s es ahora portable: datos en %s" % (pd, dst))


def make_launchers(log=None):
    made = []
    me = os.path.basename(__file__)
    spec = (("herramientas.bat", '@echo off\r\ncd /d "%%~dp0"\r\npy %s 2>nul || python %s\r\n' % (me, me), IS_WIN, False),
            ("herramientas.command", '#!/bin/bash\ncd "$(dirname "$0")"\npython3 %s\n' % me, IS_MAC, True),
            ("herramientas.sh", '#!/bin/sh\ncd "$(dirname "$0")"\nexec python3 %s "$@"\n' % me, not IS_WIN, True))
    for fname, body, applies, ex in spec:
        if not applies:
            continue
        with open(os.path.join(APP_DIR, fname), "w", encoding="utf-8", newline="") as f:
            f.write(body)
        if ex:
            os.chmod(os.path.join(APP_DIR, fname), 0o755)
        made.append(fname)
        say(log, "    creado: " + fname)
    return made


# ====================================================================== ayuda
HELP = """\
QUE HACE ESTA HERRAMIENTA
Un solo archivo para cualquier .py de su carpeta: lo compila en un ejecutable, lo instala en el sitio que le corresponde al
sistema (o lo deja portable), activa el arranque automático y prepara las librerías que necesita.
Funciona con doble clic en herramientas.py (interfaz) o por línea de comandos (python herramientas.py ayuda).
Solo usa la librería estandar de Python. En Linux la interfaz necesita Tkinter:  sudo apt install python3-tk

COMPILAR
Elige el .py y pulsa Compilar. El resultado queda en esta misma carpeta (Windows: .exe en un solo fichero; Mac: .app; Linux: carpeta).
PyInstaller solo compila para el sistema donde se ejecuta: un .exe no se puede generar en Mac/Linux, ni al reves.
La "semilla" son datos mínimos que viajan dentro del ejecutable y se copian a la carpeta de datos en el primer arranque, sin
sobrescribir nada. Si existe una carpeta defaults/ junto al .py se incluye sola (es lo que se sube al repositorio).
No metas en la semilla datos del usuario ni carpetas que crecen (cache, copias, perfiles, logs...).

INSTALAR (como en un Linux live: portable o instalado)
PORTABLE: todo junto al programa (carpeta <nombre>_data al lado). Se puede llevar en un USB; no se toca nada del sistema.
INSTALADO (solo para tu usuario, sin permisos de administrador): el programa, los datos y la caché van a las carpetas habituales
del sistema y se guarda esa ubicación en <nombre>_location.json junto al programa; la aplicación la lee al arrancar.
  Windows: programa en %LOCALAPPDATA%\\Programs\\<App>   datos en %APPDATA%\\<App>\\data   cache en %LOCALAPPDATA%\\<App>\\cache
  Linux:   programa en ~/.local/share/<App>/app        datos en ~/.local/share/<App>/data  cache en ~/.cache/<App>
  Mac:     programa en ~/Applications/<App>            datos en ~/Library/Application Support/<App>/data
Las tres rutas se pueden cambiar. Nada se borra: con "mover" los datos originales se renombran a <carpeta>.migrado_FECHA.
Tambien puede crear accesos directos (escritorio y menu) y activar el arranque automático (Windows: clave Run del usuario;
Linux: ~/.config/autostart; Mac: LaunchAgent). Se puede cambiar después sin reinstalar (boton "Arranque automático").
Volver a portable copia los datos junto al programa y borra el archivo de ubicación. Desinstalar quita accesos, arranque
automático y programa; los datos solo se borran si lo marcas.
Para variar la ubicación sin instalar: variables de entorno WIDGET_ARENA_DATA y WIDGET_ARENA_CACHE_DIR (tienen prioridad).

DEPENDENCIAS
Lee los import del .py (y de sus módulos locales), comprueba cuales faltan en el Python elegido y los instala con pip.
En Debian, Ubuntu y Linux Mint pip no deja instalar en el Python del sistema (PEP 668): se crea un entorno aislado (.venv) solo.
Si faltan módulos de Qt como WebEngine, prueba el paquete PySide6-WebEngine con la misma version de PySide6.
Para un entorno propio de cualquier .py nuevo no hace falta configurar nada: se detecta solo y lo que cambies se guarda en
herramientas.json.

OTROS .py
El selector muestra todos los .py de la carpeta. Para uno nuevo se proponen solos: nombre de la app (del nombre del archivo),
carpeta de datos <nombre>_data, archivo de ubicación <nombre>_location.json, variables <NOMBRE>_DATA y <NOMBRE>_CACHE_DIR,
si lleva ventana (PySide6, Tk...) y las librerías. Para que un .py respete esa ubicación debe leer el archivo/variables
(ver el bloque PACK88 de widget_arena.py: unas 40 lineas).
"""


# ====================================================================== línea de comandos
def _plan_from_args(p, a):
    pl = plan_defaults(p, a.mode)
    for k in ("program_dir", "data_dir", "cache_dir"):
        v = getattr(a, k, None)
        if v:
            pl[k] = os.path.abspath(os.path.expanduser(v))
    pl.update(move_data=a.move_data, desktop=a.desktop, menu=a.menu, autostart=a.autostart, deps=not a.no_deps,
              venv={"auto": "auto", "yes": True, "no": False}[a.venv])
    return pl


def main(argv=None):
    ap = argparse.ArgumentParser(prog="herramientas.py", description="Compilar, instalar y preparar librerías de un .py")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, hlp, script=True):
        sp = sub.add_parser(name, help=hlp)
        if script:
            sp.add_argument("script", nargs="?", help="archivo .py de esta carpeta (por defecto %s)" % DEFAULT_SCRIPT)
        return sp
    add("info", "estado: portable o instalado")
    s = add("deps", "librerías necesarias")
    s.add_argument("--install", action="store_true", help="instalar las que falten")
    s.add_argument("--venv", choices=("auto", "yes", "no"), default="auto")
    s = add("build", "compilar")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--onefile", dest="onefile", action="store_true", default=None)
    s.add_argument("--onedir", dest="onefile", action="store_false")
    s.add_argument("--console", action="store_true", help="con consola (por defecto sin ventana de consola si el .py es gráfico)")
    s = add("install", "instalar")
    s.add_argument("--mode", choices=("script", "exe"), default="script")
    for k in ("program-dir", "data-dir", "cache-dir"):
        s.add_argument("--" + k)
    s.add_argument("--move-data", action="store_true")
    s.add_argument("--desktop", action="store_true")
    s.add_argument("--menu", action="store_true")
    s.add_argument("--autostart", action="store_true")
    s.add_argument("--no-deps", action="store_true")
    s.add_argument("--venv", choices=("auto", "yes", "no"), default="auto")
    s = add("uninstall", "desinstalar")
    s.add_argument("--program-dir")
    s.add_argument("--remove-data", action="store_true")
    s.add_argument("--keep-cache", action="store_true")
    s = add("portable", "volver a portable")
    s.add_argument("--program-dir")
    s.add_argument("--move-data", action="store_true")
    s = add("autostart", "activar o desactivar el arranque automático")
    s.add_argument("state", choices=("on", "off"))
    add("launchers", "crear herramientas.bat/.command/.sh", script=False)
    add("help", "ayuda completa", script=False)
    add("ayuda", "ayuda completa", script=False)
    add("ui", "abrir la interfaz", script=False)
    a = ap.parse_args(argv)
    if a.cmd in (None, "ui"):
        return run_ui()
    if a.cmd in ("help", "ayuda"):
        print(HELP)
        return 0
    if a.cmd == "launchers":
        make_launchers()
        return 0
    p = get_project(getattr(a, "script", None))
    try:
        if a.cmd == "info":
            st = status(p)
            print("Aplicación : %s (%s)" % (p["app_name"], p["script"]))
            print("Modo       : %s" % st["mode"])
            print("Programa   : %s" % st["program_dir"])
            print("Datos      : %s" % st["data_dir"])
            print("Cache      : %s" % (st["cache_dir"] or "(dentro de los datos)"))
            print("Autoarranque: %s" % ("si" if st["autostart"] else "no"))
            if st["installed_elsewhere"]:
                print("Instalación existente en: %s" % st["installed_elsewhere"])
            kind, path = artifact(p)
            print("Ejecutable : %s" % (path if kind else "(sin compilar)"))
        elif a.cmd == "deps":
            mods = needed_modules(p)
            py = sys.executable
            st = check_modules(py, [m for m in mods if not m[2].startswith("no aplica")], qt_submodules(p))
            for n, pip, note in mods:
                state = note or ("OK %s" % (st.get(n) if isinstance(st.get(n), str) else "") if st.get(n) else "FALTA")
                print("%-22s %-22s %s" % (n, pip, state))
            for sname in qt_submodules(p):
                if not st.get(sname):
                    print("%-22s %-22s FALTA" % (sname, "PySide6-WebEngine" if "WebEngine" in sname else "PySide6"))
            if a.install:
                use = {"auto": externally_managed(), "yes": True, "no": False}[a.venv]
                if use:
                    py = ensure_venv(os.path.join(APP_DIR, ".venv_" + os.path.splitext(p["script"])[0]), print)
                ok, left = install_missing(p, py, print)
                print("Todo instalado en %s" % py if ok else "Faltan: %s" % ", ".join(left))
                return 0 if ok else 1
        elif a.cmd == "build":
            if a.onefile is not None:
                p["onefile"] = a.onefile
            if a.console:
                p["windowed"] = False
            build(p, print, a.dry_run)
        elif a.cmd == "install":
            install(p, _plan_from_args(p, a), print)
        elif a.cmd == "uninstall":
            pd = a.program_dir or (status(p)["installed_elsewhere"] if status(p)["mode"] == "portable" else APP_DIR)
            if not pd:
                print("No se encuentra ninguna instalación (usa --program-dir).")
                return 1
            uninstall(p, pd, a.remove_data, not a.keep_cache, print)
        elif a.cmd == "portable":
            pd = a.program_dir or (APP_DIR if status(p)["mode"] == "instalado" else status(p)["installed_elsewhere"])
            if not pd:
                print("No se encuentra ninguna instalación (usa --program-dir).")
                return 1
            to_portable(p, pd, a.move_data, print)
        elif a.cmd == "autostart":
            st = status(p)
            pd = APP_DIR if st["mode"] == "instalado" else st["installed_elsewhere"]
            if not pd:
                print("Primero instala la aplicación.")
                return 1
            man = read_json(os.path.join(pd, MANIFEST_NAME))
            ok = set_autostart(p, man.get("command") or launch_command(p, pd, man.get("mode", "script")), pd, a.state == "on", man, print)
            write_json(os.path.join(pd, MANIFEST_NAME), man)
            return 0 if ok else 1
    except RuntimeError as e:
        print("ERROR: %s" % e)
        return 1
    return 0


# ====================================================================== interfaz (Tkinter)
def run_ui(on_ready=None):
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, simpledialog, ttk
    except ImportError:
        print("No hay Tkinter en este Python, asi que no se puede abrir la interfaz.")
        if IS_LINUX:
            print("En Linux Mint/Ubuntu:  sudo apt install python3-tk")
        print("Mientras tanto todo funciona por línea de comandos:  python herramientas.py ayuda")
        return 1

    class UI:
        def __init__(self, root):
            self.root = root
            root.title("Herramientas: compilar, instalar y librerías")
            root.geometry("980x780")
            self.q = queue.Queue()
            self.busy = False
            self.p = get_project(None)
            self.vars = {}
            top = ttk.Frame(root, padding=(10, 8, 10, 0))
            top.pack(fill="x")
            ttk.Label(top, text="Archivo .py:").pack(side="left")
            self.var_script = tk.StringVar(value=self.p["script"])
            self.cb_script = ttk.Combobox(top, textvariable=self.var_script, values=py_files(), width=40)
            self.cb_script.pack(side="left", padx=6)
            self.cb_script.bind("<<ComboboxSelected>>", lambda e: self.change_script())
            self.cb_script.bind("<Return>", lambda e: self.change_script())
            ttk.Button(top, text="Examinar...", command=self.browse).pack(side="left")
            self.lbl_mode = ttk.Label(top, text="", font=("TkDefaultFont", 10, "bold"))
            self.lbl_mode.pack(side="right")
            self.nb = ttk.Notebook(root)
            self.nb.pack(fill="both", expand=True, padx=10, pady=8)
            self.tab_build, self.tab_inst, self.tab_deps, self.tab_help = (ttk.Frame(self.nb, padding=10) for _ in range(4))
            for t, txt in ((self.tab_build, "Compilar"), (self.tab_inst, "Instalar / Portable"), (self.tab_deps, "Dependencias"), (self.tab_help, "Ayuda")):
                self.nb.add(t, text=txt)
            self.build_tab_build()
            self.build_tab_install()
            self.build_tab_deps()
            self.build_tab_help()
            bot = ttk.Frame(root, padding=(10, 0, 10, 8))
            bot.pack(fill="both")
            row = ttk.Frame(bot)
            row.pack(fill="x")
            self.var_status = tk.StringVar(value="Listo.")
            ttk.Label(row, textvariable=self.var_status).pack(side="left")
            self.btn_cancel = ttk.Button(row, text="Cancelar", command=cancel_all, state="disabled")
            self.btn_cancel.pack(side="right")
            self.log = tk.Text(bot, height=11, state="disabled", bg="#111", fg="#ddd", font=("Consolas", 9))
            self.log.pack(fill="both", pady=(4, 0))
            self.refresh_all()
            root.after(80, self.poll)

        # ---------- comun
        def append(self, text):
            self.log.configure(state="normal")
            self.log.insert("end", text + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")

        def poll(self):
            try:
                while True:
                    item = self.q.get_nowait()
                    if isinstance(item, tuple):
                        item[0]()
                    else:
                        self.append(item)
            except queue.Empty:
                pass
            self.root.after(80, self.poll)

        def run_task(self, label, fn, after=None):
            if self.busy:
                return
            self.busy = True
            self.btn_cancel.configure(state="normal")
            self.var_status.set(label + "...")
            self.append("\n===== %s =====" % label)

            def worker():
                err = None
                try:
                    fn(self.q.put)
                except Exception as e:
                    err = str(e) or e.__class__.__name__
                    self.q.put("ERROR: %s" % err)

                def done():
                    self.busy = False
                    self.btn_cancel.configure(state="disabled")
                    self.var_status.set("ERROR: " + err if err else "Listo.")
                    self.refresh_all()
                    if after:
                        after(err)
                self.q.put((done,))
            threading.Thread(target=worker, daemon=True).start()

        def browse(self):
            path = filedialog.askopenfilename(initialdir=APP_DIR, filetypes=[("Python", "*.py"), ("Todos", "*.*")])
            if path:
                if os.path.dirname(os.path.abspath(path)) != APP_DIR:
                    messagebox.showinfo("Archivo", "El .py debe estar en la misma carpeta que herramientas.py:\n" + APP_DIR)
                    return
                self.var_script.set(os.path.basename(path))
                self.change_script()

        def change_script(self):
            self.p = get_project(self.var_script.get().strip())
            self.refresh_all()

        def refresh_all(self):
            self.cb_script.configure(values=py_files())
            self.load_build_fields()
            self.load_install_fields()
            self.refresh_deps()

        def pull(self):
            """Guarda en self.p lo escrito en las pestanas (y en herramientas.json)."""
            p = self.p
            p["app_name"] = self.vars["app_name"].get().strip() or p["app_name"]
            p["windowed"], p["onefile"] = self.vars["windowed"].get(), self.vars["onefile"].get()
            p["icon"], p["extra_args"] = self.vars["icon"].get().strip(), self.vars["extra_args"].get().strip()
            save_project(p)

        # ---------- compilar
        def build_tab_build(self):
            f = self.tab_build
            f.columnconfigure(1, weight=1)
            self.vars.update(app_name=tk.StringVar(), windowed=tk.BooleanVar(), onefile=tk.BooleanVar(), icon=tk.StringVar(), extra_args=tk.StringVar())
            ttk.Label(f, text="Nombre de la aplicación:").grid(row=0, column=0, sticky="w")
            ttk.Entry(f, textvariable=self.vars["app_name"]).grid(row=0, column=1, sticky="we", padx=6)
            ttk.Checkbutton(f, text="Sin ventana de consola (aplicación gráfica)", variable=self.vars["windowed"]).grid(row=1, column=0, columnspan=2, sticky="w")
            ttk.Checkbutton(f, text="Un solo fichero (solo Windows; Mac/Linux usan carpeta)", variable=self.vars["onefile"]).grid(row=2, column=0, columnspan=2, sticky="w")
            ttk.Label(f, text="Icono (opcional):").grid(row=3, column=0, sticky="w")
            ttk.Entry(f, textvariable=self.vars["icon"]).grid(row=3, column=1, sticky="we", padx=6)
            ttk.Label(f, text="Opciones extra de PyInstaller:").grid(row=4, column=0, sticky="w")
            ttk.Entry(f, textvariable=self.vars["extra_args"]).grid(row=4, column=1, sticky="we", padx=6)
            self.lbl_out = ttk.Label(f, text="", foreground="#0645ad", wraplength=880)
            self.lbl_out.grid(row=5, column=0, columnspan=3, sticky="w", pady=(6, 4))
            ttk.Label(f, text="Semilla: datos que viajan DENTRO del ejecutable y se copian a la carpeta de datos en el primer arranque (sin sobrescribir):"
                      ).grid(row=6, column=0, columnspan=3, sticky="w")
            self.tree = ttk.Treeview(f, columns=("o", "d", "t", "e"), show="headings", height=6, selectmode="extended")
            for c, t, w in (("o", "Origen", 380), ("d", "Destino (subcarpeta de los datos)", 200), ("t", "Tamaño", 70), ("e", "Estado", 70)):
                self.tree.heading(c, text=t)
                self.tree.column(c, width=w, anchor="w")
            self.tree.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(4, 0))
            f.rowconfigure(7, weight=1)
            self.tree.bind("<Double-1>", lambda e: self.edit_dest())
            b = ttk.Frame(f)
            b.grid(row=8, column=0, columnspan=3, sticky="w", pady=6)
            for text, cmd in (("Añadir carpeta...", self.add_folder), ("Añadir fichero...", self.add_file), ("Editar destino", self.edit_dest), ("Quitar", self.remove_seed)):
                ttk.Button(b, text=text, command=cmd).pack(side="left", padx=(0, 6))
            r = ttk.Frame(f)
            r.grid(row=9, column=0, columnspan=3, sticky="w")
            self.btn_build = ttk.Button(r, text="Compilar", command=self.do_build)
            self.btn_build.pack(side="left")
            ttk.Button(r, text="Ver la orden (sin compilar)", command=self.do_dry).pack(side="left", padx=6)

        def load_build_fields(self):
            p = self.p
            self.vars["app_name"].set(p["app_name"])
            self.vars["windowed"].set(bool(p["windowed"]))
            self.vars["onefile"].set(bool(p["onefile"]))
            self.vars["icon"].set(p.get("icon", ""))
            self.vars["extra_args"].set(p.get("extra_args", ""))
            kind, path = artifact(p)
            self.lbl_out.configure(text="Salida: %s%s" % (path, "" if kind else "  (se generará al compilar)"))
            self.tree.delete(*self.tree.get_children())
            for src, dst in p["seed"]:
                full = os.path.normpath(src if os.path.isabs(src) else os.path.join(APP_DIR, src.replace("/", os.sep)))
                ok = os.path.exists(full)
                size = "?"
                if ok:
                    n, s = file_count_size(full) if os.path.isdir(full) else (1, os.path.getsize(full))
                    size = "%.1f MB" % (s / 1048576.0) if s > 1048576 else "%d KB" % (s // 1024)
                self.tree.insert("", "end", values=(full, dst, size, "OK" if ok else "FALTA"))

        def _sel(self):
            return sorted(self.tree.index(i) for i in self.tree.selection())

        def _ask_dst(self, initial):
            v = simpledialog.askstring("Destino", "Subcarpeta de los datos donde se copiara ('.' = raiz).\nEj.: templates", initialvalue=initial, parent=self.root)
            return None if v is None else (v.replace("\\", "/").strip("/") or ".")

        def add_folder(self):
            d = filedialog.askdirectory(initialdir=APP_DIR)
            if d:
                dst = self._ask_dst(os.path.basename(d))
                if dst is not None:
                    self.p["seed"].append([os.path.normpath(d), dst])
                    self.p["seed_custom"] = True
                    self.load_build_fields()

        def add_file(self):
            f = filedialog.askopenfilename(initialdir=APP_DIR)
            if f:
                dst = self._ask_dst(".")
                if dst is not None:
                    self.p["seed"].append([os.path.normpath(f), dst])
                    self.p["seed_custom"] = True
                    self.load_build_fields()

        def edit_dest(self):
            idx = self._sel()
            if len(idx) == 1:
                dst = self._ask_dst(self.p["seed"][idx[0]][1])
                if dst is not None:
                    self.p["seed"][idx[0]][1] = dst
                    self.p["seed_custom"] = True
                    self.load_build_fields()

        def remove_seed(self):
            for i in reversed(self._sel()):
                del self.p["seed"][i]
                self.p["seed_custom"] = True
            self.load_build_fields()

        def do_build(self):
            self.pull()
            self.run_task("Compilando %s" % self.p["script"], lambda log: build(self.p, log))

        def do_dry(self):
            self.pull()
            self.run_task("Orden de compilación", lambda log: build(self.p, log, dry_run=True))

        # ---------- instalar
        def build_tab_install(self):
            f = self.tab_inst
            f.columnconfigure(1, weight=1)
            v = self.vars
            v.update(mode=tk.StringVar(value="script"), program=tk.StringVar(), data=tk.StringVar(), cache=tk.StringVar(), move=tk.BooleanVar(),
                     desktop=tk.BooleanVar(value=True), menu=tk.BooleanVar(value=True), autostart=tk.BooleanVar(), deps=tk.BooleanVar(value=True),
                     venv=tk.StringVar(value="auto"))
            self.lbl_state = ttk.Label(f, text="", wraplength=900, justify="left")
            self.lbl_state.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
            ttk.Label(f, text="Instalar como:").grid(row=1, column=0, sticky="w")
            r = ttk.Frame(f)
            r.grid(row=1, column=1, sticky="w")
            ttk.Radiobutton(r, text="Script .py (usa el Python de este equipo)", variable=v["mode"], value="script").pack(side="left")
            ttk.Radiobutton(r, text="Ejecutable compilado", variable=v["mode"], value="exe").pack(side="left", padx=10)
            for i, (key, text) in enumerate((("program", "Carpeta del programa:"), ("data", "Carpeta de datos:"), ("cache", "Carpeta de caché:")), start=2):
                ttk.Label(f, text=text).grid(row=i, column=0, sticky="w", pady=2)
                ttk.Entry(f, textvariable=v[key]).grid(row=i, column=1, sticky="we", padx=6)
                ttk.Button(f, text="Examinar...", command=lambda k=key: self.pick_dir(k)).grid(row=i, column=2)
            ttk.Checkbutton(f, text="MOVER los datos actuales (los originales se apartan como .migrado_FECHA; si no, se copian)", variable=v["move"]).grid(row=5, column=0, columnspan=3, sticky="w", pady=(8, 0))
            ttk.Checkbutton(f, text="Acceso directo en el escritorio", variable=v["desktop"]).grid(row=6, column=0, columnspan=3, sticky="w")
            ttk.Checkbutton(f, text="Acceso directo en el menú de aplicaciones", variable=v["menu"]).grid(row=7, column=0, columnspan=3, sticky="w")
            ttk.Checkbutton(f, text="Arrancar automáticamente al iniciar sesión", variable=v["autostart"]).grid(row=8, column=0, columnspan=3, sticky="w")
            d = ttk.Frame(f)
            d.grid(row=9, column=0, columnspan=3, sticky="w")
            ttk.Checkbutton(d, text="Instalar las librerías que falten", variable=v["deps"]).pack(side="left")
            ttk.Label(d, text="   Entorno aislado (.venv):").pack(side="left")
            ttk.Combobox(d, textvariable=v["venv"], values=("auto", "yes", "no"), width=6, state="readonly").pack(side="left", padx=4)
            ttk.Label(d, text="(auto = solo si el sistema lo exige, como Linux Mint)", foreground="#666").pack(side="left")
            b = ttk.Frame(f)
            b.grid(row=10, column=0, columnspan=3, sticky="w", pady=12)
            self.btn_install = ttk.Button(b, text="Instalar / Actualizar", command=self.do_install)
            self.btn_install.pack(side="left")
            ttk.Button(b, text="Volver a portable", command=self.do_portable).pack(side="left", padx=6)
            ttk.Button(b, text="Desinstalar...", command=self.do_uninstall).pack(side="left")
            ttk.Button(b, text="Alternar arranque automático", command=self.do_toggle_autostart).pack(side="left", padx=6)
            ttk.Button(b, text="Abrir carpeta de datos", command=self.open_data).pack(side="left")

        def load_install_fields(self):
            d = plan_defaults(self.p)
            st = status(self.p)
            cur = st["program_dir"] if st["mode"] == "instalado" else (st["installed_elsewhere"] or d["program_dir"])
            if st["mode"] == "instalado":
                d["data_dir"], d["cache_dir"] = st["data_dir"], st["cache_dir"] or d["cache_dir"]
            for k, key in (("program", "program_dir"), ("data", "data_dir"), ("cache", "cache_dir")):
                self.vars[k].set(cur if k == "program" else d[key])
            self.vars["autostart"].set(bool(st["autostart"]))
            txt = {"portable": "MODO PORTABLE: los datos viven junto al programa (%s).",
                   "instalado": "MODO INSTALADO: datos en %s."}[st["mode"]] % st["data_dir"]
            if st["installed_elsewhere"]:
                txt += "\nYa hay una instalación en %s (se actualizará si pulsas Instalar)." % st["installed_elsewhere"]
            self.lbl_state.configure(text=txt)
            self.lbl_mode.configure(text="Modo: " + st["mode"])

        def pick_dir(self, key):
            d = filedialog.askdirectory(initialdir=self.vars[key].get() or home())
            if d:
                self.vars[key].set(os.path.normpath(d))

        def plan(self):
            v = self.vars
            pl = plan_defaults(self.p, v["mode"].get())
            pl.update(program_dir=v["program"].get().strip(), data_dir=v["data"].get().strip(), cache_dir=v["cache"].get().strip(),
                      move_data=v["move"].get(), desktop=v["desktop"].get(), menu=v["menu"].get(), autostart=v["autostart"].get(),
                      deps=v["deps"].get(), venv={"auto": "auto", "yes": True, "no": False}[v["venv"].get()])
            return pl

        def do_install(self):
            self.pull()
            pl = self.plan()
            if not (pl["program_dir"] and pl["data_dir"] and pl["cache_dir"]):
                messagebox.showerror("Instalar", "Faltan carpetas.")
                return
            if not messagebox.askyesno("Instalar", "Se instalará %s para este usuario:\n\nPrograma: %s\nDatos: %s\nCache: %s\n\n%s\n\n¿Continuar?" % (
                    self.p["app_name"], pl["program_dir"], pl["data_dir"], pl["cache_dir"],
                    "Los datos actuales se MUEVEN (los originales quedan apartados)." if pl["move_data"] else "Los datos actuales se COPIAN (los originales no se tocan).")):
                return
            self.run_task("Instalando %s" % self.p["app_name"], lambda log: install(self.p, pl, log))

        def _inst_dir(self):
            st = status(self.p)
            return APP_DIR if st["mode"] == "instalado" else (st["installed_elsewhere"] or self.vars["program"].get().strip())

        def do_portable(self):
            pd = self._inst_dir()
            if not messagebox.askyesno("Volver a portable", "Los datos se copiarán junto al programa:\n%s\n\nLos datos instalados se conservan.\n¿Continuar?" % pd):
                return
            self.run_task("Volviendo a portable", lambda log: to_portable(self.p, pd, False, log))

        def do_uninstall(self):
            pd = self._inst_dir()
            if not messagebox.askyesno("Desinstalar", "Se quitarán accesos directos, arranque automático, cache y el programa de:\n%s\n\nLos DATOS se conservan.\n¿Continuar?" % pd):
                return
            rd = messagebox.askyesno("Datos", "¿Borrar TAMBIEN los datos (perfiles, templates, copias)? Esta acción no se puede deshacer.", default="no")
            self.run_task("Desinstalando", lambda log: uninstall(self.p, pd, rd, True, log))

        def do_toggle_autostart(self):
            def fn(log):
                st = status(self.p)
                pd = APP_DIR if st["mode"] == "instalado" else st["installed_elsewhere"]
                if not pd:
                    raise RuntimeError("primero instala la aplicación")
                man = read_json(os.path.join(pd, MANIFEST_NAME))
                on = not is_autostart(self.p)
                set_autostart(self.p, man.get("command") or launch_command(self.p, pd, man.get("mode", "script")), pd, on, man, log)
                write_json(os.path.join(pd, MANIFEST_NAME), man)
            self.run_task("Arranque automático", fn)

        def open_data(self):
            d = status(self.p)["data_dir"]
            if not os.path.isdir(d):
                messagebox.showinfo("Datos", "Todavia no existe:\n" + d)
                return
            if IS_WIN:
                os.startfile(d)
            else:
                subprocess.Popen(["open" if IS_MAC else "xdg-open", d])

        # ---------- dependencias
        def build_tab_deps(self):
            f = self.tab_deps
            f.columnconfigure(0, weight=1)
            f.rowconfigure(1, weight=1)
            ttk.Label(f, text="Librerías que importa el .py (y sus módulos locales), comprobadas en el Python de abajo:").grid(row=0, column=0, sticky="w")
            self.dtree = ttk.Treeview(f, columns=("m", "p", "e", "v"), show="headings", height=12)
            for c, t, w in (("m", "Módulo", 220), ("p", "Paquete pip", 220), ("e", "Estado", 200), ("v", "Versión", 120)):
                self.dtree.heading(c, text=t)
                self.dtree.column(c, width=w, anchor="w")
            self.dtree.grid(row=1, column=0, sticky="nsew", pady=6)
            r = ttk.Frame(f)
            r.grid(row=2, column=0, sticky="w")
            ttk.Label(r, text="Python:").pack(side="left")
            self.var_py = tk.StringVar(value=sys.executable)
            ttk.Combobox(r, textvariable=self.var_py, values=python_candidates(), width=60).pack(side="left", padx=6)
            ttk.Button(r, text="Comprobar", command=self.refresh_deps).pack(side="left")
            ttk.Button(r, text="Instalar las que faltan", command=self.do_deps).pack(side="left", padx=6)
            self.lbl_pep = ttk.Label(f, text="", foreground="#a60", wraplength=900)
            self.lbl_pep.grid(row=3, column=0, sticky="w", pady=(6, 0))

        def refresh_deps(self):
            if not hasattr(self, "dtree"):
                return
            self.dtree.delete(*self.dtree.get_children())
            mods = needed_modules(self.p)
            py = self.var_py.get().strip() or sys.executable
            real = [m for m in mods if not m[2].startswith("no aplica")]
            st = check_modules(py, real, qt_submodules(self.p)) if os.path.isfile(py) else {}
            for n, pip, note in mods:
                ok = st.get(n)
                self.dtree.insert("", "end", values=(n, pip, note or ("instalado" if ok else "FALTA"), ok if isinstance(ok, str) else ""))
            for s in qt_submodules(self.p):
                ok = st.get(s)
                self.dtree.insert("", "end", values=(s, "PySide6", "instalado" if ok else "FALTA", ""))
            self.lbl_pep.configure(text=("Este Python es 'externally managed' (PEP 668): pip no deja instalar aquí. Al instalar se creará un entorno aislado (.venv)."
                                         if externally_managed(py) else ""))

        def do_deps(self):
            py = self.var_py.get().strip() or sys.executable

            def fn(log):
                target = py
                if externally_managed(py):
                    target = ensure_venv(os.path.join(APP_DIR, ".venv_" + os.path.splitext(self.p["script"])[0]), log)
                ok, left = install_missing(self.p, target, log)
                say(log, "==> " + ("Todo instalado en %s" % target if ok else "Faltan: %s" % ", ".join(left)))
            self.run_task("Instalando librerías", fn, after=lambda e: self.refresh_deps())

        # ---------- ayuda
        def build_tab_help(self):
            f = self.tab_help
            f.columnconfigure(0, weight=1)
            f.rowconfigure(0, weight=1)
            t = tk.Text(f, wrap="word", font=("TkDefaultFont", 10))
            t.insert("1.0", HELP)
            t.configure(state="disabled")
            t.grid(row=0, column=0, sticky="nsew")
            ttk.Button(f, text="Crear lanzador de doble clic (.bat / .command / .sh)", command=lambda: self.run_task("Lanzadores", lambda log: make_launchers(log))).grid(row=1, column=0, sticky="w", pady=6)

    root = tk.Tk()
    ui = UI(root)
    if on_ready:                      # gancho para pruebas automaticas
        root.after(400, lambda: on_ready(ui, root))
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
