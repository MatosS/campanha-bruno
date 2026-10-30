# Relatório da primeira migração

> Este relatório descreve a etapa anterior à exclusão. A limpeza autorizada foi concluída em 2026-10-29, preservando originais, fontes e anexos. Estado atual: [relatório da limpeza](../limpeza/relatorio.md).

Data: 2026-10-29.

> Registro da etapa de migração. A organização enciclopédica posterior e suas contagens atuais estão no [relatório da enciclopédia](../enciclopedia/relatorio.md).

A base está disponível a partir de [Inicio.md](../../conteudo/Inicio.md). O `vault-42` e a `BASE INICIAL` permanecem intactos; nenhuma exclusão, movimentação, publicação ou operação Git foi realizada nas origens.

## Cobertura

- **12 de 12 arquivos da BASE INICIAL** têm conversão em Markdown, incluindo os dois PDFs, o DOCX e as duas planilhas.
- **53 arquivos do vault-42** foram copiados: os 52 selecionados no levantamento e o background adicional de Fash, preservado com indicação de continuidade a revisar.
- **65 originais** estão guardados com igualdade de bytes em `arquivo/originais/`.
- **143 notas Markdown** compõem a entrada, índices, campanhas, sessões, entidades e fontes. Todas são alcançáveis a partir da página inicial.
- **27 entradas do diário de Glim** foram separadas em notas de sessão, preservando integralmente o texto de cada entrada.
- **14 transcrições** das sessões 13–26 foram mantidas integralmente, com seus timestamps, erros e lacunas.

O [manifesto de textos](textos.json) relaciona cada origem e destino. A [verificação global](verificacao.json) inclui a cobertura individual dos 12 arquivos iniciais.

## Conversões dos formatos binários

| Fonte | Conteúdo preservado | Conferência |
| --- | --- | --- |
| Nota1.pdf e Nota2.pdf | Texto integral, marcadores, imagens e 80 páginas completas em PNG. Uma página está em branco na própria fonte. | Dois extratores independentes e comparação do texto do Markdown por página; inspeção visual; hashes dos arquivos. |
| FASH PALESKIN.xlsx | Seis abas, 398 células com conteúdo, 40 fórmulas, comentários, hyperlinks e imagens. | Conferência de coordenadas, fórmulas e caches com leitor independente e XML original. |
| GLIM SOMBRASSELVA.xlsx | Onze abas, 2.470 células com conteúdo, 160 fórmulas, comentários, hyperlinks e imagens. | Mesma conferência; todas as abas foram incluídas. |
| Resumo detalhado.docx | 306 blocos, 337 parágrafos incluindo células, uma tabela 16×2 e 64 itens de lista. | Reconstrução integral dos textos a partir do Markdown, com hash igual ao XML e leitura independente. |

As duas planilhas somam 20 comentários, 346 hyperlinks, 1.271 mesclagens e sete imagens. Todas as abas são visíveis. Fórmulas, valores em cache e valores originais foram mantidos separadamente; nenhum recálculo foi executado. Três caches vazios continuam identificados como vazios.

O pacote XML das planilhas e os dados por coordenada acompanham a conversão para preservar detalhes que uma tabela Markdown não representa. Fontes, estilos, paginação, posicionamento e interatividade originais também continuam disponíveis nos binários arquivados. Não foi encontrado um renderizador Word no runtime; a conversão do DOCX teve verificação estrutural e textual, sem alegação de comparação visual do layout.

Manifestos: [PDF](pdf.json), [planilhas](planilhas.json) e [DOCX](docx.json).

## Variantes e incertezas preservadas

- O handoff, o background e os diários presentes nos dois acervos mantêm sua proveniência. Apresentações derivadas não foram usadas para apagar variantes originais.
- Os PDFs são variantes dos TXT do dossiê de Okay e de Personagens e Heróis. As pequenas diferenças de pontuação e formatação foram registradas no manifesto de PDF; os textos não foram substituídos uns pelos outros.
- `Resumo detalhado.docx` mantém Timo Pé-de-Musgo e Fesh como escritos. A ligação com os outros nomes e campanhas continua a revisar.
- O background de Tinkar Daergel/Eldrosia e o documento Personagens e Heróis têm indicação de revisão, sem promoção automática de suas afirmações a cânone.
- Nas sessões 1–12 e na solo, a fonte informa dia/mês. O ano 2026 usado para organização está explicitamente marcado como inferido; nas sessões 13–26, é documentado nas transcrições.
- As estimativas de tempo ficcional, relatos de NPCs, sonhos, hipóteses e confirmações posteriores continuam diferenciados. A migração de formato não resolve divergências narrativas.

## Verificações executadas

A conferência global verifica hashes dos originais e de 227 saídas de conversão, corpos dos 60 documentos textuais importados, integridade dos 27 diários, estrutura dos metadados, 463 wikilinks e 354 links locais. A validação dos metadados cobre explicitamente o subconjunto YAML emitido pelos conversores, com escalares e listas.

Uma revisão independente conferiu a preservação textual e as fronteiras de continuidade. Sua observação sobre os anos das primeiras sessões foi incorporada aos metadados e ao índice.

Os scripts em `tools/` documentam a reprodução e a conferência. O comando de verificação é de leitura das fontes; os importadores e conversores sobrescrevem suas próprias saídas e precisam de revisão antes de qualquer reexecução após edição manual das notas.

## Próximas etapas

O acervo já pode ser consultado e serve como base para detalhar as notas de personagens, lugares, facções e eventos. Essas notas têm uma camada inicial de navegação; a consolidação enciclopédica completa e a interface de busca/grafo ainda são etapas seguintes.

Imagens que existiam apenas como links do Drive continuam referenciadas nas fontes. Não foram baixadas nem declaradas preservadas localmente. Novas gravações posteriores às cópias disponíveis também não foram conferidas. Essas limitações não substituem nem removem nenhum dos 12 arquivos iniciais.

A remoção futura do `vault-42` e da `BASE INICIAL` deve usar os manifestos para selecionar exatamente o material já preservado. Nenhuma dessas remoções foi executada nesta etapa.
