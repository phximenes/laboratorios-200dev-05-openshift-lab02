$ErrorActionPreference = 'Stop'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.9+ real deve estar no PATH.' }
& python (Join-Path $PSScriptRoot 'check.py') @args
exit $LASTEXITCODE
