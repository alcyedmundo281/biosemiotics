# Activa Python y salida Unicode para esta consola de PowerShell.
. (Join-Path $PSScriptRoot '.venv/Scripts/Activate.ps1')
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$global:OutputEncoding = [Console]::OutputEncoding
