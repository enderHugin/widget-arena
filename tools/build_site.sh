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
cp assets/icon.png assets/icon.ico assets/icon.icns "$OUT/dl/"
# notas de bienvenida y perfil de ejemplo (se copian en el primer arranque): defaults.zip con carpeta "defaults/" en la raiz
zip -qrX "$OUT/dl/defaults.zip" defaults
cp defaults/packs/*.wapack "$OUT/dl/" 2>/dev/null || true       # packs de ejemplo para descargar
sub installers/install-windows.cmd | sed -e 's/\r$//' -e 's/$/\r/' > "$OUT/dl/install-windows.cmd"
sub installers/install-unix.sh > "$OUT/dl/install-linux.sh"
sub installers/install-unix.sh > "$OUT/dl/Widget Arena.command"
chmod +x "$OUT/dl/install-linux.sh" "$OUT/dl/Widget Arena.command"
( cd "$OUT/dl" && zip -qX install-macos.zip "Widget Arena.command" && rm "Widget Arena.command" )
echo "Sitio montado en $OUT (base $BASE, version $VER)"
