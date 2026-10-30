# Prévia local com Quartz

O usuário escolheu Quartz e autorizou uma prévia local em 30/10/2026. O código oficial está em `site/`, baseado em Quartz 5, revisão `97a2d05f80c4c50534959b1d0d41cc4b3895625e`, sob a licença MIT preservada nessa pasta.

A pasta `conteudo/` continua sendo a base editável. `tools/preparar-site.mjs` gera uma apresentação em `site/content/`, mapeando `titulo` para `title`, sem editar notas ou fontes. Os anexos e arquivos locais referenciados são incluídos, com links ajustados apenas na apresentação gerada. O manifesto registra hashes das notas originais.

A página de entrada é um atlas interativo. Os nós e arestas vêm das notas processadas pelo Quartz, sem inventar relações. O grafo principal destaca personagens, lugares, facções, acontecimentos, itens e criaturas, com filtros por categoria e época; fontes, sessões e revisão podem ser incluídas. As épocas vêm dos metadados existentes: não representam datas exatas nem presença simultânea de todos os personagens.

Direção visual: fundo azul de tinta, linhas discretas de constelação, títulos Spectral, corpo Source Sans 3 e cores por categoria. A leitura usa navegação lateral, busca do Quartz, referências de entrada e grafo local. A lista de notas permite navegar sem manipular o desenho. Tema claro, telas pequenas e preferência por movimento reduzido devem funcionar.

Esta etapa entrega somente a prévia local. A publicação pública continua para uma etapa posterior.

## Executar

Na pasta `site/`, `node scripts/preview.mjs` prepara a apresentação, executa o build do Quartz e serve `http://127.0.0.1:8080`. A porta pode ser trocada com a variável `PORT`. O servidor observa `conteudo/` e os arquivos da apresentação; após uma atualização, recarregue o navegador. `node scripts/build.mjs` gera somente os arquivos estáticos. Em uma máquina nova, instale as dependências com `npm ci` (npm >=10.9.2; Node >=22).

A prévia iniciada pelo agente roda em processo oculto e registra PID e URL em `site/.preview.json`, com saída em `site/preview.log` e erros em `site/preview-error.log`. Ela escuta apenas no próprio computador. Um endereço público depende de uma futura publicação.

## Verificar

Na raiz, `node tools/verificar_site.mjs` verifica destinos locais do HTML usando nomes exatos, cobertura no índice de busca e hashes das notas originais. Resultado em `docs/site/verificacao.json`. Os verificadores de migração e enciclopédia continuam válidos e independentes.
