# Campanha de Fash e Glim

Base pública de conhecimento da campanha. O ponto de entrada é [conteudo/Inicio.md](conteudo/Inicio.md).

[Abrir o atlas da campanha](https://matoss.github.io/campanha-bruno/).

A pasta `conteudo/` reúne as notas Markdown e seus anexos. Ela pode ser aberta como um vault no Obsidian. Diários de Glim estão separados por sessão; documentos, transcrições e planilhas convertidas ficam em `Fontes/`.

A organização enciclopédica detalha personagens, lugares, facções, criaturas, acontecimentos e itens. Cada entrada conecta fontes, relações e questões em aberto. A [lista revisada](conteudo/Pendencias/Indice.md) separa contradições e gaps de sequência de fatos ainda em aberto, detalhes sem impacto e histórico encerrado. O [roteiro de revisão](conteudo/Pendencias/Roteiro%20da%20sabatina.md) contém só os tópicos relevantes; mistérios, missões futuras, nomes e endereços não viram perguntas por falta de informação.

Os arquivos originais foram preservados em `arquivo/originais/`, com hashes e destinos documentados. Essa pasta de preservação continua separada da apresentação. A prévia local inclui cópias para download dos arquivos referenciados pelas notas; seus links são ajustados apenas na apresentação gerada.

## Documentação

- [Formato da base](docs/formato-da-base.md)
- [Relatório da organização enciclopédica](docs/enciclopedia/relatorio.md)
- [Critérios de evidência e pendências](docs/enciclopedia/criterios.md)
- [Verificação da enciclopédia](docs/enciclopedia/verificacao.json)
- [Limpeza das origens e conferência de preservação](docs/limpeza/relatorio.md)
- [Auditoria para remoção das entradas duplicadas](docs/auditoria-exclusao/parecer.md)
- [Relatório da migração](docs/migracao/relatorio.md)
- [Verificação automática](docs/migracao/verificacao.json)
- [Levantamento anterior à migração](docs/levantamento-inicial.md)

A `BASE INICIAL` e os 53 arquivos auditados do `vault-42` foram removidos com autorização em 2026-10-29. As 65 cópias integrais continuam em `arquivo/originais/`; as fontes convertidas e os anexos foram preservados. Os links afetados do vault-42 apontam para uma nota de migração com os destinos nesta base. Fontes com interpretação incerta permanecem sinalizadas, e a sabatina já começou.

## Prévia local do site

O Quartz 5 está em `site/`, com atlas interativo, filtros por campanha e categoria, busca, grafo local e referências entre notas. A base editável continua em `conteudo/`; a apresentação é gerada sem alterar suas fontes. [Detalhes e verificação](docs/site/previa.md).

Para iniciar, com Node.js 22 ou superior e dependências já instaladas:

```powershell
cd C:\sources\campanha-bruno\site
node scripts/preview.mjs
```

Abra `http://127.0.0.1:8080`. Alterações na base ou na apresentação geram uma nova versão; recarregue a página após a mensagem de atualização. Encerre com `Ctrl+C` no terminal que iniciou a prévia. Para apenas gerar os arquivos estáticos, execute `node scripts/build.mjs` na pasta `site/`; a saída fica em `site/public/`.

A publicação pública usa GitHub Pages. Cada envio de um commit à branch `main` executa a geração, verifica os links e atualiza o site. Consulte [a configuração da publicação](docs/site/publicacao.md).

Em uma instalação nova, execute `npm ci` em `site/` antes de iniciar, usando npm 10.9.2 ou superior. A verificação de links e preservação pode ser repetida na raiz com `node tools/verificar_site.mjs`.

## Conferir novamente

`tools/verificar_migracao.py` é uma conferência de leitura: valida hashes, cobertura, estrutura dos metadados, destinos dos links e os corpos dos diários. Após a limpeza, usa as cópias arquivadas e só aceita a ausência de origens que constem no registro de exclusão autorizado. Execute com o Python do runtime de documentos.

`tools/verificar_enciclopedia.py` confere o snapshot das fontes, cobertura das entidades, metadados, proveniência, IDs de pendências e suas remissões. `tools/indexar_enciclopedia.py --somente-indices` atualiza a navegação e a fila conforme a classificação de relevância; mantém as contagens históricas de status separadas, preservando as notas já curadas. A execução sem essa opção também regenera campanhas e visões; revise antes de usá-la após a sabatina.

Os importadores, conversores e geradores editoriais sobrescrevem suas próprias saídas. Não os reexecute sobre notas que já tenham recebido edição manual sem revisar antes, especialmente depois de incorporar respostas da sabatina.

`tools/verificar_limpeza.py` confere as 65 remoções, as cópias integrais, o snapshot dos arquivos protegidos e os links redirecionados do vault-42. A lista exata e os hashes permanecem em `docs/auditoria-exclusao/candidatos.json` e `docs/limpeza/execucao.json`.
