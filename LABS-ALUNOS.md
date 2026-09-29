# Lab 02 — Roteiro do aluno

## Cenário

Você assumiu o plantão da aplicação `atendimento`. A equipe anterior deixou chamados de configuração, conectividade e recursos. Depois de resolvê-los, publique a versão green e demonstre que consegue retornar à blue.

Trabalhe na raiz do pacote, em Bash, com `LAB_NS` definido conforme PREREQUISITOS.md. Use somente o projeto exclusivo da aula. Não abra `gabarito/`. Cada chamado deve ser documentado em uma cópia de EVIDENCIAS.md com sintoma, evidência, causa, correção e teste final.

## 0 — Conferência de acesso • 15 min

1. Autentique e crie/selecione o projeto `lab-plantao-SEU_IDENTIFICADOR` com label `training.200dev.com/lab=plantao02`.
2. Execute `bash scripts/preflight.sh "$LAB_NS"`. Resolva os bloqueios com o instrutor.
3. Abra o console e localize Deployments, Services, Routes, ConfigMaps, Secrets e Quotas do projeto. Nomes de menus dependem da versão.
4. Registre a versão do servidor e permissões indisponíveis. Não registre token nem endereço privado do cluster.

**Aceite:** projeto dedicado e permissões básicas verificadas. **Pergunta:** por que não reutilizar um namespace com aplicações de outras equipes para testar quotas?

## 1 — Receber a aplicação blue • 20 min

A base está pronta. Leia `starter/base.yaml` e identifique os relacionamentos entre Deployment, ConfigMap, Secret, Service e Route antes de aplicar.

```bash
oc create configmap plantao-code -n "$LAB_NS" --from-file=server.py=starter/app/server.py
oc create configmap plantao-config -n "$LAB_NS" --from-literal=APP_MESSAGE='Equipe A'
# Credencial PUBLICA e FICTICIA desta aula; nunca usar em sistemas reais.
oc create secret generic plantao-credencial -n "$LAB_NS" --from-literal=API_TOKEN=treino-sem-valor-real
oc apply --dry-run=server -n "$LAB_NS" -f starter/base.yaml
oc apply -n "$LAB_NS" -f starter/base.yaml
oc rollout status deployment/atendimento-blue -n "$LAB_NS" --timeout=180s
ROUTE_HOST=$(oc get route atendimento -n "$LAB_NS" -o jsonpath='{.spec.host}')
curl --fail "https://$ROUTE_HOST/"
```

**Aceite:** resposta com `release: blue`, `message: Equipe A` e `credential_configured: true`. A aplicação nunca devolve o valor da credencial. `/healthz` e `/readyz` retornam 200; `/admin` exige autenticação de aplicação, independente do login `oc`.

## 2 — Chamado: a mensagem continua antiga • 25 min

O novo turno solicita mensagem `Equipe B`. Atualize o ConfigMap sem alterar a imagem nem o código:

```bash
oc create configmap plantao-config -n "$LAB_NS" --from-literal=APP_MESSAGE='Equipe B' --dry-run=client -o yaml | oc apply -n "$LAB_NS" -f -
curl --fail "https://$ROUTE_HOST/"
```

1. Compare o valor armazenado no ConfigMap com a resposta HTTP do processo existente.
2. Explique por que o processo ainda pode responder `Equipe A`.
3. Faça a aplicação consumir o novo valor, mantendo a referência ao ConfigMap e acompanhando o rollout. Não substitua a referência por um valor literal no Deployment.
4. Registre os UIDs dos pods antes/depois e a resposta final `Equipe B`.

**Aceite:** blue responde Equipe B; a variável ainda vem de `configMapKeyRef`. **Pergunta:** `oc rollout undo` reverte o conteúdo de um ConfigMap independente?

## 3 — Chamado: Service sem destino • 25 min

```bash
oc apply -n "$LAB_NS" -f starter/chamados/01-service.yaml
oc get service chamado-service -n "$LAB_NS" -o yaml
oc get pods -n "$LAB_NS" --show-labels
oc get endpointslices -n "$LAB_NS" -l kubernetes.io/service-name=chamado-service
oc exec -n "$LAB_NS" deployment/atendimento-blue -- python3 -c 'import urllib.request; print(urllib.request.urlopen("http://chamado-service:8080/", timeout=5).read().decode())'
```

1. Localize a inconsistência sem reiniciar pods saudáveis.
2. Corrija o arquivo do chamado para o Service selecionar somente a versão blue. Reaplique.
3. Confirme endpoints Ready e HTTP 200 pelo mesmo endereço interno.
4. Exclua apenas `service/chamado-service` depois de registrar o diagnóstico.

**Aceite:** correção restrita à seleção de pods. **Pergunta:** DNS resolver um Service comprova que há endpoints prontos atrás dele?

## 4 — Chamado: Deployment existe, mas não cria pod • 25 min

1. Complete `starter/orcamento.yaml`: orçamento agregado de requests de CPU = **1 CPU**. Mantenha os demais valores: requests de memória 1Gi, limits CPU 2, limits memória 2Gi e até 10 pods. O LimitRange fornece defaults de 50m/64Mi e limits de 200m/128Mi por container.
2. Valide e aplique o arquivo. Aplique `starter/chamados/02-quota.yaml`.
3. Consulte Deployment, ReplicaSet, eventos e quota. Não procure apenas um pod Pending: a admissão pode impedir que ele seja criado.

```bash
oc get deployment,replicaset,pods -n "$LAB_NS" -l app=atendimento
oc describe resourcequota orcamento-plantao -n "$LAB_NS"
oc get events -n "$LAB_NS" --sort-by=.metadata.creationTimestamp
```

4. Corrija os recursos solicitados pelo chamado para requests CPU 50m/memória 64Mi e limits CPU 200m/memória 128Mi. Preserve a quota, reaplique e espere o rollout.
5. Confirme HTTP em `/healthz` via `oc exec` no Deployment corrigido. Depois exclua `deployment/chamado-quota`.

**Aceite:** evento de rejeição registrado e workload recuperado sem ampliar o orçamento. **Pergunta:** qual a diferença entre quota excedida e `Insufficient cpu` do scheduler? Alterar LimitRange reescreve pods existentes?

## 5 — Chamado: credencial não encontrada • 20 min

```bash
oc apply -n "$LAB_NS" -f starter/chamados/03-credencial.yaml
oc get pods -n "$LAB_NS" -l release=diagnostico-credencial
```

1. Use `describe pod` e eventos para investigar. Compare **nome do Secret e nome da chave referenciada** sem imprimir valores de Secret.
2. Corrija a referência no arquivo do chamado. Não torne a referência opcional nem crie outra credencial para esconder o erro.
3. Aguarde rollout; confirme `/` com `credential_configured: true`.
4. Verifique que `/admin` retorna 401 sem credencial e 200 com a credencial demonstrativa usando o teste fornecido:

```bash
oc exec -i -n "$LAB_NS" deployment/chamado-credencial -- python3 - < scripts/testar-acesso.py
```

O teste lê a variável dentro do container, mas mostra apenas os resultados HTTP. Exclua `deployment/chamado-credencial` após registrar.

**Aceite:** referência corrigida e teste 401/200. **Pergunta:** guardar uma string em Secret significa que o etcd está necessariamente criptografado? Por que não salvar `oc get secret -o yaml` no relatório?

## 6 — Acesso mínimo para suporte • 25 min

Complete `starter/rbac.yaml` para a ServiceAccount `observador` poder:

- `get`, `list`, `watch` em pods;
- `get` em pods/log;
- nenhuma permissão adicional concedida por este Role.

Use Role `leitor-pods` e RoleBinding `observador-pods`. Não conceda `view`, `edit` ou `admin`; o objetivo é construir um papel específico.

Aplique o arquivo e acompanhe a demonstração do instrutor de permissões efetivas. Esperado: listar pods e ler logs = permitido; criar pods, ler Secrets e excluir Deployments = negado. A conta do aluno não precisa ter impersonação. Se não houver demonstração, registre a lacuna, sem afirmar que o teste efetivo passou.

**Aceite:** Role restrito, binding para a conta correta e análise dos resultados. **Pergunta:** outro binding poderia ampliar os direitos dessa mesma conta?

## 7 — Publicação blue/green e retorno • 30 min

1. Complete `starter/green.yaml`: duas réplicas, `RELEASE=green` e Service com selector `release: green`. Preserve labels, ConfigMap e Secret.
2. Valide com dry-run do servidor, aplique e espere o rollout.
3. Teste `http://atendimento-green:8080/` de dentro de um pod: espera-se green, Equipe B e credencial configurada. A Route ainda deve responder blue.
4. Publique a green aplicando `starter/route-green.yaml`; confirme novas requisições HTTPS à **mesma Route** retornando green.
5. Simule o retorno aplicando `starter/route-blue.yaml`. Confirme blue. Não exclua green nem altere DNS.
6. Publique green novamente e deixe esse estado final. Mantenha blue com uma réplica e green com duas.

```bash
oc get deployment,service,route -n "$LAB_NS"
curl --fail "https://$ROUTE_HOST/"
```

**Aceite:** evidências blue → green → blue → green na mesma URL; todos os pods finais Ready. Teste com novas conexões; troca de backend não garante migração de conexões já estabelecidas. **Pergunta:** o que esta estratégia não resolve em uma migração incompatível de banco de dados?

## 8 — Entrega do plantão • 15 min

```bash
bash avaliacao/check.sh "$LAB_NS"
```

Entregue o resultado e EVIDENCIAS.md preenchido. Produza uma passagem de plantão de até dez linhas: versão ativa, versão de retorno, chamados resolvidos, limitações e próximo passo operacional.

Estado final: blue com uma réplica, green com duas; Route apontando apenas para green; mensagem Equipe B; quota e LimitRange mantidos; Role/RoleBinding de observador; sem recursos `chamado-*`. O avaliador não atribui os 40 pontos históricos/manuais.

## Limpeza após a avaliação

Excluir o projeto remove todos os recursos do lab. Execute somente depois da correção, confirmando que é o projeto exclusivo desta aula:

```bash
oc get namespace "$LAB_NS" --show-labels
oc delete project "$LAB_NS"
```

Não reaplique `starter/base.yaml` no encerramento: ele aponta a Route para blue.
