# Validação da entrega — 29/09/2026

## Confirmado localmente

- Sintaxe dos arquivos Python analisada; wrappers PowerShell e Bash verificados.
- 25 objetos YAML carregados pelo parser; relações entre selectors/labels e soluções dos chamados conferidas. Os TODO nos starters são intencionais.
- Aplicação executada em HTTP local: saúde, readiness, configuração/release, 404, acesso negado 401 e autorizado 200. Credencial vazia não autoriza acesso e respostas não expõem seu valor.
- Avaliador testado com respostas simuladas construídas a partir dos manifestos: 60/60 no estado final; 55/60 para quota incorreta, Role ampliado e chave de Secret incorreta, cada falha isoladamente; label de projeto ausente bloqueia com saída 2.
- Links dos documentos verificados; dois ZIPs separados gerados e integridade conferida. Pacote do aluno exclui gabarito e guia do instrutor.

## Ensaio em cluster ainda necessário

Não foram aplicados recursos em um cluster durante a criação desta entrega. Antes da turma, validar pull da imagem, SCC/UID, dry-run do servidor, DNS/Services/endpoints, Route/TLS, quotas e respectivos eventos, referência de Secret, permissões efetivas, blue/green e avaliador contra o ambiente real.

A tentativa de consultar a ajuda da CLI local foi bloqueada pelo Controle de Aplicativo do Windows. A estação usada na aula precisa de uma instalação de `oc` permitida pela política do ambiente. Não foi tentado contornar esse bloqueio; os testes do avaliador utilizaram respostas simuladas.

Os resultados simulados não comprovam execução real. A imagem usa tag flutuante; o instrutor pode fixar um digest após ensaiar. Interferências de políticas ou quotas existentes precisam ser registradas, especialmente no chamado de admissão.

## Distribuição

- `distribuicao/200DEV-lab02-aluno.zip`: roteiro, pré-requisitos, evidências, cobertura, aplicação, starters, preflight e avaliador.
- `distribuicao/200DEV-lab02-instrutor.zip`: todos os itens acima, guia do instrutor, gabarito e manifestos resolvidos.

Nenhum ZIP inclui arquivos do primeiro lab, caches, kubeconfig ou credenciais reais. A string usada para autenticação da aplicação é um exemplo público fictício definido no enunciado.
