# test_ventana_actualizaciones.py
"""[PACK217] Las actualizaciones de widget-arena las lleva el actualizador comun (pyi_update.qt_install):
se arranca el gestor de verdad (sin red) y se comprueba la ventana, el atajo secreto desde otra ventana,
las preferencias antiguas y la opcion del menu de la bandeja.
Uso (con PySide6 instalado):  QT_QPA_PLATFORM=offscreen python tools/test_ventana_actualizaciones.py
(como root en Linux, ademas QTWEBENGINE_DISABLE_SANDBOX=1)"""
import json
import os
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = tempfile.mkdtemp(prefix='wa_upd_ui_')
os.environ['WIDGET_ARENA_DATA'] = os.path.join(WORK, 'datos')
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
for k in ('WA_OFFLINE', 'WA_NO_FONT_PROMPT', 'WA_NO_PERF_PROMPT', 'WA_NO_MODE_PROMPT'):
    os.environ[k] = '1'
sys.path.insert(0, REPO)
sys.argv = [os.path.join(REPO, 'widget_arena.py')]
import widget_arena as w      # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QLineEdit, QLabel  # noqa: E402

fails = []


def ok(c, m):
    print(('ok - ' if c else 'FALLO - ') + m)
    if not c:
        fails.append(m)


def pump(ms):
    end = time.time() + ms / 1000.0
    while time.time() < end:
        app.processEvents()
        time.sleep(0.01)


# preferencias de antes (nombres antiguos de widget-arena)
os.makedirs(os.path.dirname(w.UPDATE_STATE), exist_ok=True)
json.dump({'watch': False, 'auto_install': True}, open(w.UPDATE_STATE, 'w'))
w._UPDATE_ST = {}
app = QApplication.instance() or QApplication([])
m = w.WidgetManager(app, None)
pump(900)
ctl = m._upd_ctl if getattr(m, '_upd_ctl', None) else m._updates_ctl()
import pyi_update  # noqa: E402
ok(ctl.u.state().get('auto_apply') is True, 'la preferencia antigua "actualizar al iniciar" se conserva')
ok(m.update_auto_install_on() is True, 'el menu de la bandeja la ve marcada')
m.set_update_auto_install(False)
ok(ctl.u.state().get('auto_apply') is False and json.load(open(w.UPDATE_STATE)).get('auto_apply') is False,
   'desmarcarla en la bandeja la apaga en el actualizador')
other = QLineEdit()
other.show()
pump(50)
M = Qt.KeyboardModifier
QTest.keyClick(other, Qt.Key.Key_F12, M.ControlModifier | M.ShiftModifier | M.AltModifier)
pump(200)
win = ctl.win
ok(win is not None and win.alive() and win.watch_visible(), 'Ctrl+Mayus+Alt+F12 desde otra ventana abre Actualizaciones con la casilla')
labels = [x.text() for x in win.top.findChildren(QLabel)]
ok(any(('py-installer ' + pyi_update.PYI_VERSION) in t for t in labels), 'se ve la version del actualizador')
ok(any(('pack %d' % w.APP_PACK) in t for t in labels), 'se ve el pack instalado')
win.c['watch'].setChecked(True)
ok(json.load(open(w.UPDATE_STATE)).get('silent_watch') is True, '"vigilar sola" se guarda')
win.c['watch'].setChecked(False)
win.top.close()
pump(50)
d = m.show_updates(check=False)
ok(d is not None and d.alive() and not d.watch_visible(), 'el menu "Buscar actualizaciones" abre la ventana (sin la casilla oculta)')
ok(ctl.watch_every_ms == w.UPDATE_WATCH_MS, 'vigila cada %d min' % (w.UPDATE_WATCH_MS // 60000))
print('TODO OK' if not fails else '%d FALLOS' % len(fails))
os._exit(1 if fails else 0)
