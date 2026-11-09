$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:USE_SQLITE = '1'
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw 'Static file preparation failed.' }
python -m PyInstaller --noconfirm --clean --onedir --name TechBridgeCRM --collect-all django --collect-submodules crm --collect-submodules config --collect-submodules whitenoise --collect-data tzdata --hidden-import waitress --add-data 'templates;templates' --add-data 'staticfiles;staticfiles' --add-data 'static;static' desktop.py
if ($LASTEXITCODE -ne 0) { throw 'Windows build failed.' }
Write-Host 'Package the entire dist\TechBridgeCRM folder, including _internal.'
