"""Lab 02: 12 verificacoes de 5 pontos; nao aplica alteracoes no cluster."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import get, oc


def quantity(value):
    value = str(value)
    for suffix, multiplier in (("Gi", 1024**3), ("Mi", 1024**2), ("Ki", 1024), ("m", Decimal("0.001"))):
        if value.endswith(suffix):
            return Decimal(value[:-len(suffix)]) * multiplier
    return Decimal(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("namespace")
    ns = parser.parse_args().namespace
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", ns) or len(ns) > 63:
        parser.error("informe um projeto <identificador>")
    score = 0

    def check(title, fn):
        nonlocal score
        try:
            passed = bool(fn())
            detail = "" if passed else "estado esperado nao encontrado"
        except RuntimeError as error:
            passed, detail = False, str(error)
        except Exception:
            passed, detail = False, "resposta invalida ou teste HTTP/TLS indisponivel"
        if passed:
            score += 5
        print(("OK +5: " if passed else "PENDENTE +0: ") + title + (" — " + detail if detail else ""))

    def obj(kind, name):
        return get(kind, name, ns)

    def deployment(color, count):
        d = obj("deployment", "atendimento-" + color)
        s = d.get("status", {})
        return d["spec"]["replicas"] == count and s.get("observedGeneration", 0) >= d["metadata"]["generation"] and all(
            s.get(k) == count for k in ("replicas", "updatedReplicas", "readyReplicas", "availableReplicas"))

    def response(color):
        code = 'import urllib.request; print(urllib.request.urlopen(' + repr("http://atendimento-" + color + ":8080/") + ', timeout=5).read().decode())'
        return json.loads(oc("exec", "-n", ns, "deployment/atendimento-" + color, "--", "python3", "-c", code))

    def configuration():
        if obj("configmap", "plantao-config")["data"].get("APP_MESSAGE") != "Equipe B":
            return False
        for color in ("blue", "green"):
            d = obj("deployment", "atendimento-" + color)
            env = d["spec"]["template"]["spec"]["containers"][0]["env"]
            if not any(e["name"] == "APP_MESSAGE" and e.get("valueFrom", {}).get("configMapKeyRef") == {
                    "name": "plantao-config", "key": "APP_MESSAGE"} for e in env):
                return False
            r = response(color)
            if r.get("message") != "Equipe B" or r.get("release") != color:
                return False
        return True

    def service(color, expected):
        s = obj("service", "atendimento-" + color)
        slices = get("endpointslices.discovery.k8s.io", namespace=ns,
                     selector="kubernetes.io/service-name=atendimento-" + color)["items"]
        ready = {e.get("targetRef", {}).get("uid", str(e.get("addresses"))) for x in slices for e in x.get("endpoints", [])
                 if e.get("conditions", {}).get("ready") is True}
        return (s["spec"]["selector"] == {"app": "atendimento", "release": color} and len(ready) == expected
                and any(p["name"] == "http" and p["port"] == 8080 and p["targetPort"] == "http" for p in s["spec"]["ports"]))

    def route():
        r = obj("route", "atendimento")
        spec = r["spec"]
        if spec["to"]["name"] != "atendimento-green" or spec.get("alternateBackends"):
            return False
        if spec.get("tls", {}).get("termination") != "edge" or spec["tls"].get("insecureEdgeTerminationPolicy") != "Redirect":
            return False
        if not any(c["type"] == "Admitted" and c["status"] == "True" for i in r.get("status", {}).get("ingress", []) for c in i.get("conditions", [])):
            return False
        with urllib.request.urlopen("https://" + spec["host"] + "/", timeout=10) as result:
            data = json.load(result)
            return result.status == 200 and data.get("release") == "green" and data.get("message") == "Equipe B"

    def secret_refs():
        for color in ("blue", "green"):
            env = obj("deployment", "atendimento-" + color)["spec"]["template"]["spec"]["containers"][0]["env"]
            if not any(e["name"] == "API_TOKEN" and e.get("valueFrom", {}).get("secretKeyRef") == {
                    "name": "plantao-credencial", "key": "API_TOKEN"} for e in env):
                return False
            if response(color).get("credential_configured") is not True:
                return False
        return True

    def budget():
        hard = obj("resourcequota", "orcamento-plantao")["spec"]["hard"]
        expected = {"requests.cpu": "1", "requests.memory": "1Gi", "limits.cpu": "2", "limits.memory": "2Gi", "pods": "10"}
        return all(quantity(hard.get(k, -1)) == quantity(v) for k, v in expected.items())

    def defaults():
        entries = obj("limitrange", "padroes-plantao")["spec"]["limits"]
        return any(x.get("type") == "Container" and all(quantity(x.get(field, {}).get(k, -1)) == quantity(v)
            for field, pairs in (("defaultRequest", {"cpu": "50m", "memory": "64Mi"}), ("default", {"cpu": "200m", "memory": "128Mi"}))
            for k, v in pairs.items()) for x in entries)

    def rbac():
        obj("serviceaccount", "observador")
        role = obj("role", "leitor-pods")
        # Sem wildcards, resourceNames, URLs ou regras extras; o Role deve ser exatamente o enunciado.
        normalized = {(tuple(sorted(x.get("apiGroups", []))), tuple(sorted(x.get("resources", []))), tuple(sorted(x.get("verbs", [])))) for x in role["rules"]}
        expected = {(('',), ('pods',), ('get', 'list', 'watch')), (('',), ('pods/log',), ('get',))}
        if normalized != expected or any(set(x) - {"apiGroups", "resources", "verbs"} for x in role["rules"]):
            return False
        b = obj("rolebinding", "observador-pods")
        return (b["roleRef"] == {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role", "name": "leitor-pods"}
                and any(s.get("kind") == "ServiceAccount" and s.get("name") == "observador" and s.get("namespace", ns) == ns for s in b.get("subjects", [])))

    def security():
        pods = get("pods", namespace=ns, selector="app=atendimento")["items"]
        if len(pods) != 3:
            return False
        for pod in pods:
            spec = pod["spec"]
            sc = spec["containers"][0].get("securityContext", {})
            if spec.get("automountServiceAccountToken") is not False or sc.get("allowPrivilegeEscalation") is not False or "ALL" not in sc.get("capabilities", {}).get("drop", []):
                return False
            uid = oc("exec", "-n", ns, pod["metadata"]["name"], "--", "id", "-u")
            if not uid.isdigit() or int(uid) == 0:
                return False
        return True

    def cleanup():
        return all(not x["metadata"]["name"].startswith("chamado-") for kind in ("deployments", "pods", "services")
                   for x in get(kind, namespace=ns).get("items", []))

    check("Blue com uma replica convergida", lambda: deployment("blue", 1))
    check("Green com duas replicas convergidas", lambda: deployment("green", 2))
    check("ConfigMap e respostas Equipe B", configuration)
    check("Service blue e endpoint", lambda: service("blue", 1))
    check("Service green e endpoints", lambda: service("green", 2))
    check("Route HTTPS publica green", route)
    check("Referencia ao Secret e configuracao carregada", secret_refs)
    check("Orcamento preservado", budget)
    check("Defaults do LimitRange", defaults)
    check("Role minimo e binding", rbac)
    check("Tres pods sem root e sem token de API montado", security)
    check("Chamados temporarios removidos", cleanup)
    print(f"\nResultado automatico: {score}/60. Evidencias manuais: ate 40 pontos.")
    print("O avaliador nao le valores de Secrets nem comprova historico de troca/retorno ou permissoes efetivas completas.")
    return 0 if score == 60 else 1


if __name__ == "__main__":
    sys.exit(main())
