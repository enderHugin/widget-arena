#!/usr/bin/env bash
# ---------------------------------------------------------------------------------------------
# Widget Arena - instalador para Linux y macOS (el mismo archivo sirve para los dos).
# Todo va a carpetas de tu usuario (sin sudo, salvo las librerias de sistema que Qt necesita en algunas distribuciones de Linux):
# consigue un Python propio con "uv", prepara el programa y deja un acceso en el menu de aplicaciones.
# Volver a ejecutarlo actualiza. Para desinstalar:  bash <carpeta de datos>/WidgetArena/uninstall.sh
#
# Variables opcionales:  WA_NO_LAUNCH=1 (no abrir al terminar)   WA_UV=/ruta/a/uv (usar ese uv)   WA_PYTHON=/ruta/a/python3.12 (usar ese Python)
#                        WA_NO_DEPS=1 (no instalar librerias)
# ---------------------------------------------------------------------------------------------
set -euo pipefail

BASE="${WA_BASE_URL:-__BASE_URL__}"

say()  { printf '      %s\n' "$*"; }
step() { printf '\n\033[36m[%s/5] %s\033[0m\n' "$1" "$2"; }
die()  { printf '\n\033[31m  ERROR: %s\033[0m\n  Registro: %s\n' "$*" "${LOG:-}" >&2; exit 1; }
trap 'die "El instalador se detuvo (linea $LINENO). Puedes volver a ejecutarlo: continua donde lo dejo."' ERR

OS="$(uname -s)"; ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)  UVARCH=x86_64 ;;
  aarch64|arm64) UVARCH=aarch64 ;;
  *) die "Arquitectura no soportada: $ARCH" ;;
esac
case "$OS" in
  Linux)  KIND=linux; TRIPLE="$UVARCH-unknown-linux-gnu"
          ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/WidgetArena" ;;
  Darwin) KIND=mac;   TRIPLE="$UVARCH-apple-darwin"
          ROOT="$HOME/Library/Application Support/WidgetArena" ;;
  *) die "Sistema no soportado: $OS (este instalador es para Linux y macOS)" ;;
esac
if [ "$KIND" = linux ] && { ldd --version 2>&1 | grep -qi musl; }; then
  die "Esta distribucion usa musl (por ejemplo Alpine): Qt no tiene paquetes para ella."
fi

BIN="$ROOT/bin"; RT="$ROOT/runtime"; STAGE="$ROOT/stage"
if [ "$KIND" = linux ]; then PROG="$ROOT/app"; else PROG="$HOME/Applications/WidgetArena"; fi

fetch() {   # fetch URL DESTINO (con reintentos)
  local url="$1" dest="$2" n
  for n in 1 2 3; do
    if command -v curl >/dev/null 2>&1; then curl -fsSL --retry 2 -o "$dest" "$url" && [ -s "$dest" ] && return 0
    elif command -v wget >/dev/null 2>&1; then wget -q -O "$dest" "$url" && [ -s "$dest" ] && return 0
    else die "Hace falta curl o wget para descargar."; fi
    sleep $((2 * n))
  done
  die "No se pudo descargar $url. Comprueba tu conexion a internet."
}

printf '\n\033[33m  ==============================\n        Widget Arena\n  ==============================\033[0m\n'
echo "  Se instala solo para tu usuario. No hace falta tener Python ni ser administrador."
echo "  La primera vez descarga unos cientos de MB (las librerias de Qt); puede tardar unos minutos."

mkdir -p "$ROOT" "$BIN" "$RT" "$STAGE" "$ROOT/logs"
LOG="$ROOT/logs/instalacion.log"
exec > >(tee -a "$LOG") 2>&1            # todo lo que sale por pantalla queda tambien en el registro
echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="; echo "$(uname -srm) | $(command -v bash) $BASH_VERSION | usuario $(id -un)"
say "registro de esta instalacion: $LOG"
pkill -f "$PROG/widget_arena.py" 2>/dev/null || true

# --- 1) uv ---------------------------------------------------------------------------------------------------------
step 1 "Preparando el gestor de Python (uv)"
if [ -n "${WA_UV:-}" ] && [ -x "${WA_UV}" ]; then
  UV="$WA_UV"; say "usando $UV"
else
  UV="$BIN/uv"
  if [ -x "$UV" ] && "$UV" --version >/dev/null 2>&1; then
    say "ya estaba instalado"
  else
    T="$(mktemp -d)"
    fetch "https://github.com/astral-sh/uv/releases/latest/download/uv-$TRIPLE.tar.gz" "$T/uv.tgz"
    tar -xzf "$T/uv.tgz" -C "$T"
    F="$(find "$T" -type f -name uv -perm -u+x | head -n 1)"
    [ -n "$F" ] || die "El archivo descargado de uv no contiene el programa."
    cp "$F" "$UV"; chmod +x "$UV"; rm -rf "$T"
    say "listo"
  fi
fi

# --- 2) Python 3.12 propio -----------------------------------------------------------------------------------------
step 2 "Preparando Python 3.12"
if [ -n "${WA_PYTHON:-}" ] && [ -x "${WA_PYTHON}" ]; then
  PY="$WA_PYTHON"; say "usando $PY"
else
  export UV_PYTHON_INSTALL_DIR="$RT" UV_CACHE_DIR="$ROOT/cache" UV_PYTHON_PREFERENCE=only-managed UV_PYTHON_DOWNLOADS=automatic UV_NO_PROGRESS=1
  "$UV" python install 3.12
  PY="$("$UV" python find 3.12 | head -n 1)"
  [ -x "$PY" ] || die "No se encontro el Python 3.12 recien instalado."
  say "$PY"
fi

# --- 3) el programa ------------------------------------------------------------------------------------------------
step 3 "Descargando Widget Arena"
for f in widget_arena.py herramientas.py VERSION icon.png; do fetch "$BASE/dl/$f" "$STAGE/$f"; done
[ "$KIND" = mac ] && fetch "$BASE/dl/icon.icns" "$STAGE/icon.icns"
# notas de bienvenida (opcional: si no se pueden bajar, el programa arranca igual, solo que vacio)
if curl -fsSL --retry 2 -o "$STAGE/defaults.zip" "$BASE/dl/defaults.zip" 2>/dev/null || wget -q -O "$STAGE/defaults.zip" "$BASE/dl/defaults.zip" 2>/dev/null; then
  "$PY" -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$STAGE/defaults.zip" "$STAGE" || rm -rf "$STAGE/defaults"
fi
VERSION="$(tr -d '[:space:]' < "$STAGE/VERSION")"
# fuente predeterminada: el programa la pregunta, con muestras, la primera vez que se abre. Solo si defines WA_FONT (instalacion desatendida) se fija aqui.
if [ -n "${WA_FONT:-}" ] && [ -d "$STAGE/defaults" ]; then
  mkdir -p "$STAGE/defaults/data"
  printf '{"default_font": "%s", "asked": true}\n' "$(printf '%s' "$WA_FONT" | tr -d '"\\')" > "$STAGE/defaults/data/fuentes.json"
  say "fuente predeterminada: $WA_FONT"
fi
say "version $VERSION"

# --- 4) instalacion ------------------------------------------------------------------------------------------------
step 4 "Instalando el programa y sus librerias (la parte lenta)"
EXTRA=""; [ -n "${WA_NO_DEPS:-}" ] && EXTRA="--no-deps"
"$PY" -u "$STAGE/herramientas.py" install widget_arena.py --mode script --desktop --menu --venv yes $EXTRA

# --- 5) icono, acceso y desinstalador ------------------------------------------------------------------------------
step 5 "Terminando: icono y desinstalador"
cp "$STAGE/icon.png" "$PROG/widget_arena.png"
VPY="$PROG/.venv/bin/python"

if [ "$KIND" = linux ]; then
  ICONDIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/512x512/apps"
  mkdir -p "$ICONDIR"; cp "$STAGE/icon.png" "$ICONDIR/widget-arena.png"
  "$PY" - "$PROG/install_manifest.json" <<'PYEOF'
import json, sys, os
man = json.load(open(sys.argv[1], encoding='utf-8'))
for t in man.get('shortcuts', []):
    if not t.endswith('.desktop') or not os.path.exists(t):
        continue
    lines = [l for l in open(t, encoding='utf-8').read().splitlines() if not l.startswith(('Icon=', 'StartupWMClass=', 'Name=', 'Comment='))]
    lines[1:1] = ['Name=Widget Arena', 'Comment=Notas adhesivas y widgets enlazados', 'Icon=widget-arena']
    open(t, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
PYEOF
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" >/dev/null 2>&1 || true
  # Librerias del sistema que necesita Qt: el propio programa sabe cuales faltan y pide permiso para instalarlas (una sola vez).
  if [ -z "${WA_NO_DEPS:-}" ]; then
    cat > "$STAGE/syslibs.py" <<'PYEOF'
import sys
p = sys.argv[1]
src = open(p, encoding='utf-8').read()
head = src.split("\n_wa_bootstrap()\n")[0]
ns = {'__file__': p, '__name__': 'wa_boot'}
exec(compile(head, p, 'exec'), ns)
ns['_wa_bootstrap_system']()
PYEOF
    if { : < /dev/tty; } 2>/dev/null; then      # con "curl ... | bash" la entrada no es la terminal: se le devuelve para que pueda preguntar
      "$VPY" "$STAGE/syslibs.py" "$PROG/widget_arena.py" < /dev/tty || true
    else
      "$VPY" "$STAGE/syslibs.py" "$PROG/widget_arena.py" || true
    fi
  fi
else
  APP="$HOME/Applications/Widget Arena.app"
  rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cp "$STAGE/icon.icns" "$APP/Contents/Resources/icon.icns"
  cat > "$APP/Contents/Info.plist" <<PLEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Widget Arena</string>
<key>CFBundleDisplayName</key><string>Widget Arena</string>
<key>CFBundleIdentifier</key><string>app.widgetarena.widgetarena</string>
<key>CFBundleExecutable</key><string>WidgetArena</string>
<key>CFBundleIconFile</key><string>icon</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>$VERSION</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLEOF
  cat > "$APP/Contents/MacOS/WidgetArena" <<LAEOF
#!/bin/bash
cd "$PROG"
echo "[\$(date '+%F %T')] arranque desde Widget Arena.app" >> "$PROG/arranque.log"
exec "$VPY" -u "$PROG/widget_arena.py" >> "$PROG/arranque.log" 2>&1
LAEOF
  chmod +x "$APP/Contents/MacOS/WidgetArena"
fi

# desinstalador
cat > "$ROOT/uninstall.sh" <<UNEOF
#!/usr/bin/env bash
# Desinstala Widget Arena (accesos directos, programa y Python propio). Tus notas y ajustes se conservan salvo que lo pidas.
pkill -f "$PROG/widget_arena.py" 2>/dev/null || true
ARGS=()
read -r -p "¿Borrar tambien tus notas y ajustes? [s/N] " r
case "\$r" in s|S|y|Y) ARGS+=(--remove-data) ;; esac
"$PY" -u "$PROG/herramientas.py" uninstall widget_arena.py --program-dir "$PROG" "\${ARGS[@]}" || true
rm -rf "$HOME/Applications/Widget Arena.app" "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/512x512/apps/widget-arena.png"
rm -rf "$RT" "$BIN" "$ROOT/cache" "$ROOT/stage"
rm -f "\$0"
echo "Widget Arena se ha desinstalado."
UNEOF
chmod +x "$ROOT/uninstall.sh"

# comprobacion: ¿cargan de verdad las librerias?
SMOKE_OK=1
if [ -z "${WA_NO_DEPS:-}" ]; then
  say "comprobando que las librerias cargan..."
  if SM="$(QT_QPA_PLATFORM=offscreen "$VPY" -c "import numpy; from PySide6 import QtWidgets, QtWebEngineWidgets; print('QT_OK')" 2>&1)" && [ "${SM##*$'\n'}" = "QT_OK" ]; then
    say "librerias correctas"
  else
    SMOKE_OK=0
    printf '\n\033[33m  AVISO: las librerias no cargan en este equipo, asi que el programa no se abrira todavia:\033[0m\n%s\n' "$(printf '%s\n' "$SM" | tail -n 8)"
    if [ "$KIND" = linux ]; then echo "  Suele faltar alguna libreria del sistema (por ejemplo libxcb-cursor0, libegl1, libnss3). Vuelve a ejecutar el instalador y acepta instalarlas."; fi
    echo "  Registro: $LOG"
  fi
fi

rm -rf "$STAGE"
printf '\n\033[32m  Listo. Widget Arena esta instalado.\033[0m\n'
if [ "$KIND" = mac ]; then
  echo "  Lo encuentras en la carpeta Aplicaciones de tu usuario (Widget Arena). Si macOS avisa de que no puede verificarlo: clic derecho > Abrir."
else
  echo "  Lo encuentras en el menu de aplicaciones (Widget Arena) y en el escritorio. Busca su icono junto al reloj."
fi
echo "  Si alguna vez no se abre, mira su registro: $PROG/arranque.log"
if [ -z "${WA_NO_LAUNCH:-}" ] && [ "$SMOKE_OK" = 1 ]; then
  if [ "$KIND" = mac ]; then open "$HOME/Applications/Widget Arena.app" || true
  else nohup setsid "$VPY" "$PROG/widget_arena_lanzador.pyw" >/dev/null 2>&1 & fi
fi
sleep 0.5
exit 0
