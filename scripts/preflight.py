import argparse
import re
import sys
from common import oc, get


def main():
    parser = argparse.ArgumentParser(description="Preflight somente leitura do Lab 02")
    parser.add_argument("namespace")
    ns = parser.parse_args().namespace
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", ns) or len(ns) > 63:
        parser.error("informe um projeto <identificador>")
    try:
        oc("whoami")
        n = get("namespace", ns)
    except RuntimeError as error:
        print("BLOQUEIO:", error)
        return 2
    failed = False
    for resource in ("deployments.apps", "pods", "services", "routes.route.openshift.io",
                     "configmaps", "secrets", "resourcequotas", "limitranges", "serviceaccounts",
                     "roles.rbac.authorization.k8s.io", "rolebindings.rbac.authorization.k8s.io", "pods/exec"):
        try:
            if oc("auth", "can-i", "create", resource, "-n", ns) != "yes":
                raise RuntimeError("criacao nao autorizada")
            print("OK:", resource)
        except RuntimeError as error:
            print("BLOQUEIO:", resource, "-", error)
            failed = True
    for kind in ("resourcequotas", "limitranges"):
        try:
            items = get(kind, namespace=ns).get("items", [])
            print("INFO:", kind, len(items), "objetos existentes; verificar conflitos antes da aula")
        except RuntimeError as error:
            print("LACUNA:", kind, "-", error)
    print("MANUAL: validar imagem, SCC, capacidade, DNS, Route/TLS e quota agregada do ambiente.")
    print("Preflight nao prova execucao funcional. Nenhum recurso foi criado.")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
