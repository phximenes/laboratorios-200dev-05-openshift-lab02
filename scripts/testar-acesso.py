"""Executar por stdin dentro do container; nao exibe credenciais."""
import os
import sys
import urllib.error
import urllib.request

url = "http://127.0.0.1:8080/admin"


def status(headers):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


try:
    denied = status({})
    allowed = status({"Authorization": "Bearer " + os.environ.get("API_TOKEN", "")})
    print("Sem credencial:", denied, "| Com credencial:", allowed)
    sys.exit(0 if (denied, allowed) == (401, 200) else 1)
except (OSError, ValueError):
    print("Falha de conexao ou configuracao; conferir pod e endpoint.")
    sys.exit(2)
