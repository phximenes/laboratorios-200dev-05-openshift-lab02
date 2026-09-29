# Lab 02 — Passagem de plantão e publicação blue/green

200DEV • Fundamentos da Administração do Red Hat OpenShift • Segunda prática

Você recebe uma aplicação de atendimento e precisa resolver chamados operacionais antes de publicar uma nova versão. Este lab é independente do anterior: não exige que os recursos da primeira aula existam e usa outros nomes/projetos.

**Duração:** 3h20, mais pausas. **Nível:** alunos que já conhecem Pod, Deployment, Service, Route e os comandos básicos de `oc`. **Avaliação:** 60 pontos automáticos + 40 de evidências.

## Material

- [Pré-requisitos](PREREQUISITOS.md): ambiente, permissões e conectividade.
- [Roteiro do aluno](LABS-ALUNOS.md): nove exercícios, do acesso à passagem de plantão.
- [Ficha de evidências](EVIDENCIAS.md): respostas e registros de diagnóstico.
- [Cobertura](COBERTURA.md): relação com o treinamento e fontes técnicas.
- `starter/`: aplicação, base funcional, manifestos para completar e incidentes.
- `scripts/`: preflight somente leitura.
- `avaliacao/`: verificador do estado final.
- No pacote do instrutor: `GUIA-INSTRUTOR.md` e `gabarito/`.

Trabalhe na raiz deste pacote. Os comandos do roteiro usam Bash; no Windows, use WSL/Git Bash com `oc` e login configurados no mesmo terminal. Os scripts também possuem entradas PowerShell. Python 3.9+ real é necessário para o preflight e avaliador; não há dependências Python externas.

```bash
bash scripts/preflight.sh lab-plantao-aluno01
# Depois dos exercicios:
bash avaliacao/check.sh lab-plantao-aluno01
```

```powershell
./scripts/preflight.ps1 lab-plantao-aluno01
./avaliacao/check.ps1 lab-plantao-aluno01
```

Consulte [VALIDACAO.md](VALIDACAO.md) antes da aula. A validação local não substitui o ensaio no cluster de treinamento. Este material é autoral e não é um exame oficial Red Hat.
