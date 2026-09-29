"""Consultas limitadas; nunca imprime credenciais ou saidas brutas da API."""
import json
import shutil
import subprocess


def oc(*args):
    if not shutil.which("oc"):
        raise RuntimeError("oc nao encontrado no PATH")
    try:
        result = subprocess.run(["oc", "--request-timeout=15s", *args],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("tempo limite; verificar conectividade ou saude do recurso") from None
    if result.returncode:
        error = result.stderr.lower()
        if "forbidden" in error:
            reason = "sem permissao (Forbidden)"
        elif "notfound" in error or "not found" in error:
            reason = "recurso ausente"
        elif "unauthorized" in error or "logged in" in error:
            reason = "login necessario ou expirado"
        else:
            reason = "consulta falhou; execute o comando correspondente do roteiro para diagnosticar"
        raise RuntimeError(reason)
    return result.stdout.strip()


def get(kind, name=None, namespace=None, selector=None):
    args = ["get", kind]
    if name:
        args.append(name)
    if namespace:
        args += ["-n", namespace]
    if selector:
        args += ["-l", selector]
    return json.loads(oc(*args, "-o", "json"))
