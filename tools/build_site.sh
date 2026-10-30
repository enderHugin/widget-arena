#!/usr/bin/env bash
# Monta la carpeta que se publica en GitHub Pages:  tools/build_site.sh <URL base del sitio> [carpeta de salida]
# Sustituye __BASE_URL__ / __VERSION__ en la pagina y en los instaladores y copia el programa a /dl.
set -euo pipefail
BASE="${1:?Uso: build_site.sh https://usuario.github.io/repositorio [salida]}"; BASE="${BASE%/}"
OUT="${2:-_site}"
REPO="${3:-https://github.com/${GITHUB_REPOSITORY:-OWNER/REPO}}"
cd "$(dirname "$0")/.."
VER="$(tr -d '[:space:]' < VERSION)"
rm -rf "$OUT"; mkdir -p "$OUT/dl"
sub() { sed -e "s|__BASE_URL__|$BASE|g" -e "s|__VERSION__|$VER|g" -e "s|__REPO_URL__|$REPO|g" "$1"; }
sub site/index.html > "$OUT/index.html"
cp site/favicon.png "$OUT/favicon.png"
touch "$OUT/.nojekyll"
cp widget_arena.py herramientas.py VERSION "$OUT/dl/"
# update.json: lo que lee el boton "Buscar actualizaciones" (numero de pack, huellas sha256 y novedades)
python3 - "$OUT" "$VER" <<'PYEOF'
import hashlib, json, os, re, sys
out, ver = sys.argv[1], sys.argv[2]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
m = re.search(r'^APP_PACK\s*=\s*(\d+)', open('widget_arena.py', encoding='utf-8').read(), re.M)
if not m:
    sys.exit('widget_arena.py no define APP_PACK')
notes = open('NOVEDADES.md', encoding='utf-8').read()[:4000] if os.path.exists('NOVEDADES.md') else ''
files = {n: {'sha256': sha(n), 'size': os.path.getsize(n)} for n in ('widget_arena.py', 'herramientas.py')}
with open(os.path.join(out, 'dl', 'update.json'), 'w', encoding='utf-8') as f:
    json.dump({'pack': int(m.group(1)), 'version': ver, 'notes': notes, 'files': files}, f, ensure_ascii=False, indent=2)
PYEOF
cp assets/icon.png assets/icon.ico assets/icon.icns "$OUT/dl/"
# notas de bienvenida y perfil de ejemplo (se copian en el primer arranque): defaults.zip con carpeta "defaults/" en la raiz
zip -qrX "$OUT/dl/defaults.zip" defaults
cp defaults/packs/*.wapack "$OUT/dl/" 2>/dev/null || true       # packs de ejemplo para descargar
# fuentes libres (OFL): el programa las descarga solo desde aqui si no las encuentra (con su huella sha256 fijada en el codigo)
mkdir -p "$OUT/dl/fonts"; cp defaults/fonts/*.ttf defaults/fonts/OFL-*.txt "$OUT/dl/fonts/"
sub installers/install-windows.cmd | sed -e 's/\r$//' -e 's/$/\r/' > "$OUT/dl/install-windows.cmd"
sub installers/install-unix.sh > "$OUT/dl/install-linux.sh"
sub installers/install-unix.sh > "$OUT/dl/Widget Arena.command"
chmod +x "$OUT/dl/install-linux.sh" "$OUT/dl/Widget Arena.command"
( cd "$OUT/dl" && zip -qX install-macos.zip "Widget Arena.command" && rm "Widget Arena.command" )
echo "Sitio montado en $OUT (base $BASE, version $VER)"
