@echo off
rem Widget Arena - instalador para Windows (no necesita permisos de administrador ni Python).
rem Este archivo es un .cmd con un script de PowerShell dentro: lo extrae y lo ejecuta.
title Widget Arena - instalador
set "WA_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$t=[IO.File]::ReadAllText($env:WA_SELF); $i=$t.IndexOf('#'+'#PS##'); $p=Join-Path $env:TEMP 'widget-arena-setup.ps1'; [IO.File]::WriteAllText($p,$t.Substring($i),(New-Object Text.UTF8Encoding $true)); & powershell -NoProfile -ExecutionPolicy Bypass -File $p; exit $LASTEXITCODE"
set "WA_RC=%ERRORLEVEL%"
if not "%WA_RC%"=="0" pause
exit /b %WA_RC%
##PS##
# ---------------------------------------------------------------------------------------------
# Widget Arena - instalador de Windows.
# Todo va a carpetas del usuario (sin administrador): consigue un Python propio con "uv", lo prepara y deja el programa
# instalado con sus accesos directos, su icono y su entrada en "Aplicaciones instaladas". Volver a ejecutarlo actualiza.
# ---------------------------------------------------------------------------------------------
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

$Base  = '__BASE_URL__'
$Root  = Join-Path $env:LOCALAPPDATA 'WidgetArena'
$Bin   = Join-Path $Root 'bin'
$Rt    = Join-Path $Root 'runtime'
$Stage = Join-Path $Root 'stage'
$Prog  = Join-Path $env:LOCALAPPDATA 'Programs\WidgetArena'
$RegKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\WidgetArena'
$Total = 5
$LogDir  = Join-Path $Root 'logs'
$LogFile = Join-Path $LogDir 'instalacion.log'
try { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null; Start-Transcript -Path $LogFile -Append -Force | Out-Null } catch { }

function Step([int]$n, [string]$text) {
    Write-Host ''
    Write-Host ("[{0}/{1}] {2}" -f $n, $Total, $text) -ForegroundColor Cyan
}
function Say([string]$text) { Write-Host ('      ' + $text) }

function Get-File([string]$url, [string]$dest) {
    $last = $null
    for ($try = 1; $try -le 3; $try++) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dest
            if ((Get-Item $dest).Length -gt 0) { return }
        } catch { $last = $_ }
        Start-Sleep -Seconds (2 * $try)
    }
    throw ("No se pudo descargar " + $url + " (" + $last + "). Comprueba tu conexion a internet.")
}

function Invoke-Native([string]$exe, [string[]]$argList) {
    & $exe @argList
    if ($LASTEXITCODE -ne 0) { throw ("Fallo: " + (Split-Path $exe -Leaf) + " " + ($argList -join ' ') + " (codigo " + $LASTEXITCODE + ")") }
}

function Stop-Running {
    try {
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -and $_.Name -like 'python*' -and $_.CommandLine -like '*Programs\WidgetArena*widget_arena.py*' -and $_.ProcessId -ne $PID } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    } catch { }
}

function Show-Box([string]$text, [string]$icon) {
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [void][Windows.Forms.MessageBox]::Show($text, 'Widget Arena', 'OK', $icon)
    } catch { }
}

try {
    Write-Host ''
    Write-Host '  ==============================' -ForegroundColor Yellow
    Write-Host '        Widget Arena'              -ForegroundColor Yellow
    Write-Host '  ==============================' -ForegroundColor Yellow
    Write-Host '  Se instala solo para tu usuario. No hace falta nada mas: ni Python ni permisos de administrador.'
    Write-Host '  La primera vez descarga unos cientos de MB (las librerias de Qt); puede tardar unos minutos.'

    Say ('registro de esta instalacion: ' + $LogFile)
    Say ('Windows ' + [Environment]::OSVersion.Version + ' | PowerShell ' + $PSVersionTable.PSVersion + ' | procesador ' + $env:PROCESSOR_ARCHITECTURE + ' | usuario ' + $env:USERNAME)
    Say ('programa en ' + $Prog)
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Widget Arena necesita un Windows de 64 bits.' }
    New-Item -ItemType Directory -Force -Path $Root, $Bin, $Rt, $Stage | Out-Null
    Stop-Running

    # --- 1) uv: una herramienta de un solo archivo que descarga y gestiona Python -----------------------------------
    Step 1 'Preparando el gestor de Python (uv)'
    $uv = Join-Path $Bin 'uv.exe'
    $uvOk = $false
    if (Test-Path $uv) { try { & $uv --version | Out-Null; $uvOk = ($LASTEXITCODE -eq 0) } catch { $uvOk = $false } }
    if ($uvOk) {
        Say 'ya estaba instalado'
    } else {
        $zip = Join-Path $Root 'uv.zip'
        # Siempre la version de 64 bits Intel/AMD: en Windows ARM funciona (emulada) y evita librerias que aun no existen para ARM.
        Get-File 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' $zip
        $tmp = Join-Path $Root 'uv-tmp'
        if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
        Expand-Archive -Path $zip -DestinationPath $tmp -Force
        $found = Get-ChildItem -Path $tmp -Recurse -Filter 'uv.exe' | Select-Object -First 1
        if (-not $found) { throw 'El archivo descargado de uv no contiene uv.exe.' }
        Copy-Item $found.FullName $uv -Force
        Remove-Item -Recurse -Force $tmp, $zip
        Say 'listo'
    }

    # --- 2) Python 3.12 propio (no toca el Python que tengas instalado) ---------------------------------------------
    Step 2 'Preparando Python 3.12'
    $env:UV_PYTHON_INSTALL_DIR = $Rt
    $env:UV_CACHE_DIR = Join-Path $Root 'cache'
    $env:UV_PYTHON_PREFERENCE = 'only-managed'
    $env:UV_PYTHON_DOWNLOADS = 'automatic'
    $env:UV_NO_PROGRESS = '1'
    Invoke-Native $uv @('python', 'install', '3.12')
    $found = & $uv python find 3.12
    if ($LASTEXITCODE -ne 0 -or -not $found) { throw 'No se encontro el Python 3.12 recien instalado.' }
    $py = ([string]@($found)[0]).Trim()
    if (-not (Test-Path $py)) { throw ('No existe ' + $py) }
    Say $py

    # --- 3) el programa --------------------------------------------------------------------------------------------
    Step 3 'Descargando Widget Arena'
    foreach ($f in @('widget_arena.py', 'herramientas.py', 'VERSION')) { Get-File ($Base + '/dl/' + $f) (Join-Path $Stage $f) }
    Get-File ($Base + '/dl/icon.ico') (Join-Path $Stage 'icon.ico')
    # notas de bienvenida (opcional: si no se pueden bajar, el programa arranca igual, solo que vacio)
    try {
        $dz = Join-Path $Stage 'defaults.zip'
        Get-File ($Base + '/dl/defaults.zip') $dz
        Expand-Archive -LiteralPath $dz -DestinationPath $Stage -Force
    } catch { Say 'no se pudieron bajar las notas de bienvenida (se omiten)' }
    $version = (Get-Content (Join-Path $Stage 'VERSION') -Raw).Trim()
    Say ('version ' + $version)

    # --- 4) instalacion (carpeta del programa, datos, entorno con sus librerias y accesos directos) -------------------
    Step 4 'Instalando el programa y sus librerias (la parte lenta)'
    Invoke-Native $py @('-u', (Join-Path $Stage 'herramientas.py'), 'install', 'widget_arena.py', '--mode', 'script', '--desktop', '--menu', '--venv', 'yes')

    # --- 5) icono, "Aplicaciones instaladas" y desinstalador -------------------------------------------------------
    Step 5 'Terminando: icono y desinstalador'
    Copy-Item (Join-Path $Stage 'icon.ico') (Join-Path $Prog 'widget_arena.ico') -Force
    $manFile = Join-Path $Prog 'install_manifest.json'
    if (-not (Test-Path $manFile)) { throw 'La instalacion no termino (no hay manifiesto).' }
    $man = Get-Content $manFile -Raw | ConvertFrom-Json
    $vpy = Join-Path $Prog '.venv\Scripts\python.exe'
    $sh = New-Object -ComObject WScript.Shell
    foreach ($lnk in @($man.shortcuts)) {
        if ($lnk -and (Test-Path $lnk)) {
            $s = $sh.CreateShortcut($lnk)
            $s.IconLocation = (Join-Path $Prog 'widget_arena.ico') + ',0'
            $s.Description = 'Widget Arena'
            $s.Save()
        }
    }

    $un = @'
Add-Type -AssemblyName System.Windows.Forms
$r = [Windows.Forms.MessageBox]::Show('¿Desinstalar Widget Arena?', 'Widget Arena', 'YesNo', 'Question')
if ($r -ne 'Yes') { exit 0 }
$d = [Windows.Forms.MessageBox]::Show("¿Borrar también tus notas y ajustes?`n`nSi dices que no, se conservan por si vuelves a instalarlo.", 'Widget Arena', 'YesNo', 'Question')
try {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.Name -like 'python*' -and $_.CommandLine -like '*Programs\WidgetArena*widget_arena.py*' -and $_.ProcessId -ne $PID } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
} catch { }
Start-Sleep -Milliseconds 800
$a = @('-u', '__PROG__\herramientas.py', 'uninstall', 'widget_arena.py', '--program-dir', '__PROG__')
if ($d -eq 'Yes') { $a += '--remove-data' }
try { & '__PY__' @a } catch { }
Remove-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\WidgetArena' -Recurse -Force -ErrorAction SilentlyContinue
Start-Process -WindowStyle Hidden -FilePath cmd.exe -ArgumentList '/c ping -n 4 127.0.0.1 >nul & rmdir /s /q "__ROOT__"'
[void][Windows.Forms.MessageBox]::Show('Widget Arena se ha desinstalado.', 'Widget Arena', 'OK', 'Information')
'@
    $un = $un.Replace('__PROG__', $Prog).Replace('__PY__', $py).Replace('__ROOT__', $Root)
    [IO.File]::WriteAllText((Join-Path $Root 'uninstall.ps1'), $un, (New-Object Text.UTF8Encoding $true))

    New-Item -Path $RegKey -Force | Out-Null
    $vals = @{
        DisplayName     = 'Widget Arena'
        DisplayVersion  = $version
        Publisher       = 'Widget Arena'
        InstallLocation = $Prog
        DisplayIcon     = (Join-Path $Prog 'widget_arena.ico')
        UninstallString = ('powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $Root 'uninstall.ps1') + '"')
        URLInfoAbout    = $Base
    }
    foreach ($k in $vals.Keys) { New-ItemProperty -Path $RegKey -Name $k -Value $vals[$k] -PropertyType String -Force | Out-Null }
    New-ItemProperty -Path $RegKey -Name NoModify -Value 1 -PropertyType DWord -Force | Out-Null
    New-ItemProperty -Path $RegKey -Name NoRepair -Value 1 -PropertyType DWord -Force | Out-Null

    Remove-Item -Recurse -Force $Stage -ErrorAction SilentlyContinue

    # Comprobacion: ¿cargan de verdad las librerias? (si no, se dice aqui y no con un programa que "no hace nada")
    Say 'comprobando que las librerias cargan...'
    $smoke = ''; $smokeRc = 1
    $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
        $env:QT_QPA_PLATFORM = 'offscreen'
        $smoke = (& $vpy -c "import numpy; from PySide6 import QtWidgets, QtWebEngineWidgets; print('QT_OK')" 2>&1 | Out-String)
        $smokeRc = $LASTEXITCODE
    } catch { $smoke = [string]$_ }
    $ErrorActionPreference = $old
    Remove-Item Env:\QT_QPA_PLATFORM -ErrorAction SilentlyContinue
    if ($smokeRc -ne 0 -or $smoke -notmatch 'QT_OK') {
        Write-Host $smoke -ForegroundColor Yellow
        $hint = ''
        if ($smoke -match 'DLL load failed') { $hint = "`n`nFalta el componente 'Microsoft Visual C++ Redistributable'. Instalalo desde https://aka.ms/vs/17/release/vc_redist.x64.exe y abre Widget Arena desde el menu Inicio." }
        $tl = ($smoke -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 6) -join "`n"
        try { Stop-Transcript | Out-Null } catch { }
        Show-Box ("Widget Arena se ha instalado, pero sus librerias no cargan en este equipo, asi que no se abrira todavia.`n`n" + $tl + $hint + "`n`nRegistro: " + $LogFile) 'Warning'
        exit 2
    }
    Say 'librerias correctas'

    Write-Host ''
    Write-Host '  Listo. Widget Arena esta instalado.' -ForegroundColor Green
    Write-Host '  Lo encuentras en el menu Inicio y en el escritorio. Se abre ahora; busca su icono junto al reloj.'
    $cmd = @($man.command)
    Start-Process -FilePath $cmd[0] -ArgumentList ('"' + $cmd[1] + '"') -WorkingDirectory $Prog
    Start-Sleep -Seconds 2
    Show-Box ("Widget Arena esta instalado y se esta abriendo.`n`nBusca su icono junto al reloj (si no lo ves, en las flechas de iconos ocultos). Tambien lo tienes en el menu Inicio y en el escritorio.`n`nSi alguna vez no se abre, mira su registro: " + (Join-Path $Prog 'arranque.log')) 'Information'
    try { Stop-Transcript | Out-Null } catch { }
    exit 0
}
catch {
    Write-Host ''
    Write-Host ('  ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host ('  ' + $_.ScriptStackTrace) -ForegroundColor DarkGray
    Show-Box ("No se pudo completar la instalacion:`n`n" + $_.Exception.Message + "`n`nPuedes volver a ejecutar el instalador: continuara donde lo dejo.`n`nRegistro: " + $LogFile) 'Error'
    try { Stop-Transcript | Out-Null } catch { }
    exit 1
}
