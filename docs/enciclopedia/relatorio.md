# Organização enciclopédica da campanha

> Este relatório descreve a etapa anterior à exclusão. A limpeza autorizada foi concluída em 2026-10-29, preservando originais, fontes e anexos. Estado atual: [relatório da limpeza](../limpeza/relatorio.md).

Data: 2026-10-29.

> Auditoria posterior: seis rasuras de uma planilha foram tornadas visíveis numa fonte Markdown e a pendência cartográfica foi qualificada. Os originais permaneceram intactos; a única correção de apresentação de fonte está registrada com hashes antes/depois em `correcoes-fontes.json`. Ver o [parecer de remoção](../auditoria-exclusao/parecer.md).

O ponto de entrada continua sendo [Inicio.md](../../conteudo/Inicio.md). Esta etapa transforma as entradas iniciais de navegação em notas detalhadas, com referências, relações e lacunas. Não altera o vault-42, a BASE INICIAL ou os registros importados.

## Conteúdo organizado

| Categoria | Entradas |
| --- | ---: |
| Personagens | 86 |
| Lugares e referências cartográficas | 47 |
| Facções e grupos | 20 |
| Criaturas | 8 |
| Acontecimentos | 29 |
| Itens, poderes e mecanismos | 22 |
| Total de entradas enciclopédicas | 212 |

Há também duas notas de cronologia, apresentações das duas campanhas, índices e visões de relações de poder e investigações. A base inteira contém 452 arquivos Markdown, contando fontes, diários e pendências; eles não são 452 entidades distintas do cenário.

As 181 entradas do cadastro inicial foram cobertas. Foram acrescentadas 31 entradas sustentadas pelas fontes, incluindo pontos do mapa, referências geográficas do sonho, personagens oníricos, pais de Glim e contatos ou criaturas individuais relevantes.

## Banco de informações a completar

Foram registrados **105 itens de pendência**, com identificadores estáveis, contexto, fontes e entidades afetadas: 53 de prioridade alta, 48 média e quatro baixa. A prioridade indica o impacto do esclarecimento, não pressupõe que o jogador saiba a resposta.

- [Banco completo por assunto](../../conteudo/Pendencias/Indice.md).
- [Roteiro da futura sabatina em nove blocos](../../conteudo/Pendencias/Roteiro%20da%20sabatina.md).
- [Conflitos de fontes e confirmações existentes](../../conteudo/Pendencias/Conflitos%20e%20confirmacoes.md).
- [Missões e fios abertos](../../conteudo/Visoes/Missoes%20e%20fios%20abertos.md).

Os registros são perguntas preparadas, não uma solicitação para responder todas de uma vez. O roteiro agrupa questões complementares e indica o que uma única resposta pode esclarecer em várias notas. As identidades Kael/Okay, Ébano/Sociedade das Sombras e outras confirmações de 23/10 não foram reabertas como se desconhecidas.

## Critérios aplicados

As notas distinguem acontecimentos, relatos de NPCs, informações em off, memórias, sonhos, visões e hipóteses. A base ser pública não atribui a todos os personagens conhecimento de cenas privadas.

O handoff foi usado como síntese, com essa condição declarada. Os pesquisadores abriram fontes primárias seletivamente para confirmar pontos de maior impacto. Os manifestos de cada domínio discriminam o que foi consultado e seus limites; esta entrega não alega uma nova leitura contínua de todas as falas das gravações.

Foram mantidas separadas pessoas e referências que poderiam ser fundidas por nome ou semelhança: os Carlos, os Rogers do sonho, filhos de Arkhavel, dois beholders, Conclaves, Mind Shredders/devoradores de mente, livros das bruxas e do dragão, amuleto/cinto/medalhão e as duas epidemias ou crises possíveis. O nome material do mundo não foi deduzido de Eldrosia ou de outro cenário pessoal do vault.

## Divergências recuperadas

- A planilha antiga lista cinco rótulos de portais onde o diário descreve três; a diferença foi preservada com referência a células e contexto.
- Na auditoria posterior de remoção, verificou-se que dois desses cinco rótulos estavam riscados no Excel. A apresentação Markdown foi corrigida e LG-005 passou a tratar a correspondência e o significado das marcações, em vez de presumir uma contradição de contagem. Ver `docs/auditoria-exclusao/parecer.md`.
- A legenda de W23 e a célula que a associa à floresta de Timo divergem; K28/L28 também requer reconciliação cartográfica.
- O dossiê descreve Okay como meio-elfo, enquanto outras fontes o apresentam como elfo cinza; a base registra a discrepância.
- O resumo de Timo Pé-de-Musgo/Fesh permanece com continuidade a confirmar.
- Fechar e reabrir portas recebe orientações diferentes entre S14, S19 e S25; a regra não foi resolvida por preferência editorial.
- A espécie de Tom não foi acrescentada onde a passagem consultada não a confirmava.

## Preservação e verificações

O snapshot desta etapa conferiu **315 arquivos protegidos** em Fontes, Anexos e Sessões. Nenhum foi alterado. A verificação anterior também conferiu os 65 originais arquivados, as origens consultadas e os corpos integrais dos 27 diários.

As conferências estruturais verificaram metadados, fontes locais, IDs únicos, aliases, remissões e destinos dos links. Ao final, 4.042 wikilinks e 354 links locais resolveram seus destinos, sem notas órfãs a partir da entrada. Esses controles não substituem a avaliação de cada interpretação narrativa.

Uma revisão independente amostrou os pontos de maior impacto e identificou seis parágrafos em que os esclarecimentos do jogador sustentavam só parte do texto. As citações próximas foram completadas com a síntese efetivamente usada, sem alegar uma consulta primária inexistente. A revisão e as verificações foram realizadas antes da entrega.

Manifestos e evidências: `personagens.json`, `lugares.json`, `faccoes.json`, `eventos-itens.json`, `integracao.json`, `verificacao.json` e `estado-fontes.json`, nesta pasta.

## Atualização posterior

Na sabatina, registrar quem confirmou cada resposta e seu alcance. Atualizar as pendências e as notas afetadas, mantendo a voz e o conteúdo das fontes. Confirmação parcial não encerra questões restantes nem valida toda a narrativa de um documento.

A interface estática com busca e grafo continua para etapa posterior. O acervo atual pode ser usado como vault e já fornece notas, fontes e relações para essa interface.
