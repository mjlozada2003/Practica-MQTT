$ErrorActionPreference = 'Stop'

$plantilla = Get-Content -LiteralPath 'include/ConfiguracionEjemplo.h' -Raw
if ($plantilla -notmatch '"TU_RED_WIFI"' -or
    $plantilla -notmatch '"TU_CLAVE_WIFI"') {
    Write-Error 'La plantilla WiFi fue modificada: restaurar los placeholders antes de publicar.'
}

$patron = '(?i)(password|passwd|clave|secret|token|api[_-]?key)\s*[:=]\s*["''][^"'']{4,}["'']'
$exclusiones = @(
    '--glob', '!include/ConfiguracionEjemplo.h',
    '--glob', '!mcp_server/.env.example',
    '--glob', '!scripts/auditar_secretos.ps1',
    '--glob', '!**/.pio/**',
    '--glob', '!**/.venv/**',
    '--glob', '!**/.git/**',
    '--glob', '!**/.python/**',
    '--glob', '!**/.uv-cache/**',
    '--glob', '!**/.pytest_cache/**'
)

& rg --line-number @exclusiones $patron .
if ($LASTEXITCODE -eq 0) {
    Write-Error 'Se encontraron posibles secretos. Revisar antes de publicar.'
}
if ($LASTEXITCODE -eq 1) {
    Write-Output 'Auditoria completada: no se detectaron posibles secretos.'
    exit 0
}
exit $LASTEXITCODE
