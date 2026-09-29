# Pré-requisitos

## Ambiente

- Cluster OpenShift 4.x de treinamento com Route/ingress funcional; referência documental 4.18. Confira a versão efetiva e compatibilidade da CLI antes da turma.
- Projeto exclusivo `lab-plantao-<aluno>`, sem recursos de outras aulas, com papel admin no projeto. O instrutor cria/identifica o namespace se o aluno não tiver permissão.
- Permissões para Deployments, Pods/exec, Services, Routes, ConfigMaps, Secrets, ResourceQuota, LimitRange, ServiceAccount, Role e RoleBinding. Não é necessário cluster-admin no roteiro principal.
- Aproximadamente 1 CPU e 1 GiB de RAM em requests disponíveis por aluno, com margem no cluster para rollouts simultâneos. Sem PVC, build, monitoramento extra ou operadores adicionais.
- Python 3.9+, `oc`, Bash e `curl`. No PowerShell, use Python real no PATH; alias da Microsoft Store não comprova instalação. WSL pode exigir seu próprio login.
- Os nós precisam baixar `registry.access.redhat.com/ubi9/python-312:latest` ou equivalente espelhado. O instrutor deve ensaiar e pode congelar a imagem por digest em todos os YAMLs.
- Certificado da Route confiável na estação; `curl` e Python precisam confiar na CA corporativa quando aplicável. Não usar `-k` como solução de certificado.

## Conectividade

| Origem | Destino | Porta | Finalidade |
|---|---|---|---|
| Estação | API do cluster | TCP 6443 ou porta do provedor | CLI |
| Estação | Console/OAuth e aplicações | TCP 443 | Login, navegação e Route |
| Nós | Registro de imagens/espelho e seus endpoints de entrega | TCP 443 | Pull |
| Estação e nós | DNS autorizado | UDP/TCP 53 | Resolução |
| Pods de aula e ingress | Pods de atendimento | TCP 8080 | Service e aplicação |

Políticas de rede ou quotas preexistentes precisam ser conhecidas. A quota deste lab limita apenas seu projeto; outras quotas/limites também podem valer e alterar os incidentes.

## Criar o projeto da aula

Autentique pelo método fornecido pelo instrutor; não salve token em arquivo de evidências. Em Bash:

```bash
export LAB_NS=lab-plantao-aluno01
oc new-project "$LAB_NS"
oc label namespace "$LAB_NS" training.200dev.com/lab=plantao02
oc project "$LAB_NS"
bash scripts/preflight.sh "$LAB_NS"
```

Em PowerShell:
```powershell
$Env:LAB_NS = 'lab-plantao-aluno01'
oc new-project "$Env:LAB_NS"
oc label namespace "$Env:LAB_NS" training.200dev.com/lab=plantao02
oc project "$Env:LAB_NS"
.\scripts\preflight.ps1 "$Env:LAB_NS"
```

Se o instrutor já criou o projeto, apenas selecione-o. Ele deve aplicar a label em um namespace realmente reservado à aula. O avaliador exige o prefixo e a label para evitar confusão com outros projetos.

## Preparação do instrutor

Ensaie com uma conta equivalente à dos alunos. A demonstração de permissões efetivas por impersonação exige uma sessão administrativa autorizada, separada da sessão do aluno. Se isso não estiver disponível, avalie o manifesto RBAC e registre o teste efetivo como pendente; não distribua cluster-admin para executar a demonstração.
