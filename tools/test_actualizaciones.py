# test_actualizaciones.py
"""Prueba del sistema de actualizaciones de widget-arena contra un servidor local que hace de
«enderhugin.github.io/widget-arena/dl/»: comprobar, aplicar (widget_arena.py + herramientas.py),
volver atras, rechazar huellas malas / pack que no coincide / Python invalido / redirecciones
fuera, conservar 5 copias. Sin red real ni ventanas.
Uso (con PySide6 instalado):  QT_QPA_PLATFORM=offscreen python tools/test_actualizaciones.py"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = tempfile.mkdtemp(prefix='wa_update_test_')
os.environ['WIDGET_ARENA_DATA'] = os.path.join(WORK, 'datos')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, REPO)
sys.argv = [os.path.join(REPO, 'widget_arena.py')]
import widget_arena as w      # noqa: E402

DL = os.path.join(WORK, 'dl')
PROG = os.path.join(WORK, 'prog')
os.makedirs(DL)
os.makedirs(PROG)
REDIRECT = {'on': False}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/dl/fuera' and REDIRECT['on']:
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:%d/otro' % OTHER)
            self.end_headers()
            return
        p = os.path.join(WORK, path.lstrip('/'))
        if path.startswith('/dl/') and os.path.isfile(p):
            data = open(p, 'rb').read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(404)
        self.end_headers()


srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
oth = ThreadingHTTPServer(('127.0.0.1', 0), H)
OTHER = oth.server_address[1]
for s in (srv, oth):
    threading.Thread(target=s.serve_forever, daemon=True).start()

w.UPDATE_BASE = 'http://127.0.0.1:%d/dl/' % srv.server_address[1]
w.APP_FILE = os.path.join(PROG, 'widget_arena.py')
w.APP_DIR = PROG
w.UPDATE_STATE = os.path.join(WORK, 'actualizacion.json')
w.UPDATE_BACKUPS = os.path.join(WORK, 'backups_programa')
w._UPDATE_ST = {}
sha = lambda d: hashlib.sha256(d).hexdigest()


def publish(pack, tools=b'# herramientas v1\n', extra=None):
    main = ('APP_PACK = %d\n' % pack).encode()
    files = {'widget_arena.py': main, 'herramientas.py': tools}
    files.update(extra or {})
    for n, d in files.items():
        open(os.path.join(DL, n), 'wb').write(d)
    json.dump({'pack': pack, 'version': 'v%d' % pack, 'notes': 'n',
               'files': {n: {'sha256': sha(d), 'size': len(d)} for n, d in files.items()}},
              open(os.path.join(DL, 'update.json'), 'w'))
    return main


def set_local(pack, main, tools=b'# herramientas v1\n'):
    w.APP_PACK = pack
    open(w.APP_FILE, 'wb').write(main)
    open(os.path.join(PROG, 'herramientas.py'), 'wb').write(tools)
    w._UPDATE_ST = {}


def ok(c, m):
    assert c, m
    print('ok -', m)


base = publish(1)
set_local(1, base)
new = publish(2, tools=b'# herramientas v2\n')
r = w.update_check()
ok(r['ok'] and r['state'] == 'newer', 'detecta version nueva')
res = w.update_apply(r['info'])
ok(open(w.APP_FILE, 'rb').read() == new, 'instala widget_arena.py nuevo')
ok(open(os.path.join(PROG, 'herramientas.py'), 'rb').read() == b'# herramientas v2\n', 'instala herramientas.py nuevo')
ok(open(res['backup'], 'rb').read() == base, 'la copia es la version anterior')
ok(w.update_backup_available(), 'hay copia para volver')
w.update_rollback()
ok(open(w.APP_FILE, 'rb').read() == base, 'volver atras restaura widget_arena.py')
ok(open(os.path.join(PROG, 'herramientas.py'), 'rb').read() == b'# herramientas v1\n', 'volver atras restaura herramientas.py')

set_local(2, new, b'# herramientas v2\n')
ok(w.update_check()['state'] == 'same', 'misma version -> same')
set_local(2, new + b'# local\n', b'# herramientas v2\n')
ok(w.update_check()['state'] == 'diverged', 'cambios locales -> diverged')
set_local(3, new)
ok(w.update_check()['state'] == 'older', 'local mas nueva -> older')

set_local(1, base)
publish(2)
u = json.load(open(os.path.join(DL, 'update.json')))
u['files']['widget_arena.py']['sha256'] = '0' * 64
json.dump(u, open(os.path.join(DL, 'update.json'), 'w'))
r = w.update_check()
try:
    w.update_apply(r['info'])
    ok(False, 'huella mala')
except ValueError as e:
    ok('huella' in str(e) and open(w.APP_FILE, 'rb').read() == base, 'huella que no coincide -> rechazo sin tocar nada')

bad = b'APP_PACK = 999\n'
open(os.path.join(DL, 'widget_arena.py'), 'wb').write(bad)
u['files']['widget_arena.py'] = {'sha256': sha(bad), 'size': len(bad)}
json.dump(u, open(os.path.join(DL, 'update.json'), 'w'))
try:
    w.update_apply(w.update_check()['info'])
    ok(False, 'pack')
except ValueError as e:
    ok('anunciada' in str(e) and open(w.APP_FILE, 'rb').read() == base, 'pack que no coincide -> rechazo sin tocar nada')

bad = b'APP_PACK = 2\ndef mal(:\n'
open(os.path.join(DL, 'widget_arena.py'), 'wb').write(bad)
u['files']['widget_arena.py'] = {'sha256': sha(bad), 'size': len(bad)}
json.dump(u, open(os.path.join(DL, 'update.json'), 'w'))
try:
    w.update_apply(w.update_check()['info'])
    ok(False, 'python invalido')
except SyntaxError:
    ok(open(w.APP_FILE, 'rb').read() == base, 'Python invalido -> rechazo sin tocar nada')

REDIRECT['on'] = True
try:
    w._update_get(w.UPDATE_BASE + 'fuera', 1024)
    ok(False, 'redireccion')
except ValueError as e:
    ok('redirec' in str(e), 'rechaza redirecciones a otro sitio')

shutil.rmtree(w.UPDATE_BACKUPS, ignore_errors=True)
for i in range(7):
    publish(2 + i)
    w.update_apply(w.update_check()['info'])
    set_local(1, base)
    time.sleep(0.02)
kept = [f for f in os.listdir(w.UPDATE_BACKUPS) if f.startswith('widget_arena.pack')]
ok(len(kept) == 5, 'se conservan 5 copias (%d)' % len(kept))

w._UPDATE_ST = {'auto': False}
w.update_state_save()
srv.shutdown()
shutil.rmtree(WORK, ignore_errors=True)
print('TODO OK')
