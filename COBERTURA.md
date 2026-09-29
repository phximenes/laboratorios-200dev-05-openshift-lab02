# Cobertura e referências

Continuação prática do treinamento **200DEV — 05 — Fundamentos da Administração do Red Hat OpenShift**, usado no primeiro lab. O foco agora é operação de aplicações e diagnóstico, não repetir toda a apresentação.

| Tema do treinamento | Exercícios | Novidade desta prática |
|---|---|---|
| Console e CLI; inspeção da API (slides 7, 10 e 12) | 0–8 | Evidências para uma passagem de plantão |
| Namespaces e limites de recursos (slides 4 e 7) | 0 e 4 | ResourceQuota e LimitRange aplicados ao diagnóstico |
| Identidades e RBAC (slide 11) | 5 e 6 | Role mínimo para pods/logs e distinção de autenticação da aplicação |
| Ciclo de vida e workloads (slides 3, 4 e 14) | 1, 2 e 7 | Atualização de configuração e duas versões simultâneas |
| Segurança e UID (slide 15) | 1, 5 e avaliação | Referência de Secret e execução sem root |
| Deploy, Service/Route e troubleshooting (slide 17) | 2–7 | Quatro chamados e publicação blue/green |

ConfigMap/Secret, quotas e blue/green aprofundam os fundamentos do módulo; não implicam que o slide original descrevia estes mesmos exercícios. Persistência, MCO, S2I e monitoramento não são repetidos aqui.

## Referências consultadas em 29/09/2026

- [Kubernetes — atualização via ConfigMap](https://kubernetes.io/docs/tutorials/configuration/updating-configuration-via-a-configmap/): a prática diferencia o objeto atualizado das variáveis do processo já existente.
- [Kubernetes — ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/): orçamento agregado do namespace usado no chamado de admissão.
- [Kubernetes — LimitRange](https://kubernetes.io/docs/concepts/policy/limit-range/): defaults e restrições aplicados na admissão.
- [OpenShift 4.18 — Deployments e estratégias de publicação](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/building_applications/deployments): troca do Service de destino da Route.

Confirme os detalhes na versão do cluster de aula. O exemplo é didático: imagem flutuante, código em ConfigMap e credencial pública fictícia não constituem um padrão de implantação para produção.
