# Parecer sobre remoção dos dados de entrada

> Este relatório descreve a etapa anterior à exclusão. A limpeza autorizada foi concluída em 2026-10-29, preservando originais, fontes e anexos. Estado atual: [relatório da limpeza](../limpeza/relatorio.md).

Data: 2026-10-29. Nenhuma exclusão foi executada.

## Conclusão

A auditoria aprova a remoção da pasta `BASE INICIAL` e dos **53 arquivos específicos do vault-42** registrados na lista de candidatos, **mantendo `conteudo/Fontes/`, `conteudo/Anexos/` e `arquivo/originais/`**. O parecer não abrange apagar todo o RPG do vault, seus outros projetos, o Google Drive ou gravações de áudio.

As 65 fontes do recorte possuem cópias locais byte a byte idênticas, somando 17.456.580 bytes, aproximadamente 17,5 MB. Nesse cenário, nenhuma informação dos arquivos removidos desaparece do projeto, inclusive aquela cuja apresentação original exige o formato binário ou o XML auxiliar.

[Lista exata de candidatos e cópias preservadas](candidatos.json).

## Verificação independente

| Conjunto | Resultado |
| --- | --- |
| 65 arquivos de origem | Igualdade de bytes com as cópias arquivadas. |
| 60 conversões textuais | Linhas, parágrafos e ordem preservados, salvo transformações de formato documentadas. |
| 38 front matters originais | Preservados literalmente nos detalhes das notas. |
| 14 transcrições e um JSON literal | Conteúdo integral conferido. |
| 27 entradas de diário | Corpo textual integral idêntico. |
| Dois PDFs | 80 páginas, 79 com texto; extrações, Markdown, recursos raster e imagens de página conferidos. Nenhum campo, anotação ou anexo embutido foi encontrado. |
| DOCX | 337 parágrafos/células, tabela 16×2, 64 itens de lista e 362 runs conferidos. Sem imagens, notas, comentários ou revisões ocultas nessa fonte. |
| Duas planilhas | 17 abas, 2.868 células com conteúdo, 200 fórmulas, 20 comentários, 346 hyperlinks, 1.271 mesclagens e sete imagens conferidos. |
| Pacotes de planilha | Todos os 88 membros OOXML são idênticos; um XLSX semanticamente equivalente foi reconstruído e lido em memória. O contêiner ZIP não fica byte a byte idêntico. |

Não foi detectada omissão narrativa ou de dados nas conversões auditadas. Isso não equivale a afirmar que apenas as notas enciclopédicas substituem os documentos integrais ou que todo o conteúdo pessoal de RPG foi transferido.

## Ressalva encontrada e corrigida

A auditoria identificou **seis textos riscados** em Fash `INTERESSES` que a primeira apresentação Markdown exibia sem rasura: `C3`, `D4`, `C24`, `C25`, `C51` e `C52`. A informação nunca deixou de existir no XLSX ou no XML arquivado, mas poderia ser interpretada incorretamente ao consultar somente a tabela Markdown.

A conversão passou a exibir as rasuras, sem inferir que uma célula riscada significa necessariamente morte, conclusão ou eliminação física. Duas dessas células são os rótulos dos portais Cabeça de Gigante e 4 Costelas Grandes. Portanto, a planilha contém cinco rótulos, dos quais três não estão riscados e dois estão: isso não demonstra por si só contradição com os três portais do diário. As notas cartográficas e LG-005 foram ajustadas para preservar essa diferença.

A versão anterior foi guardada em `antes-correcao/`. A mudança de apresentação tem hashes antes/depois e registro explícito; o snapshot histórico das fontes foi preservado, sem ser substituído silenciosamente.

O teste de regressão confirmou as seis rasuras e seus valores literais. Dos 397 arquivos monitorados pelo corretor, 396 permaneceram byte a byte idênticos; somente a apresentação de `Fash Paleskin - INTERESSES.md` mudou. A verificação enciclopédica confere 314 arquivos idênticos ao snapshot e essa única correção documentada; o controle dos 65 originais continua integralmente aprovado. Registros: [correção de rasuras](correcao-rasuras.json), [ajuste de cartografia](ajuste-cartografia.json) e [histórico de hashes](../enciclopedia/correcoes-fontes.json).

## O que acontece em cada cenário

| Remoção considerada | Parecer |
| --- | --- |
| Somente `BASE INICIAL` | Aprovada para os 12 arquivos auditados. As cópias exatas e os destinos convertidos permanecem aqui. |
| Somente os 53 arquivos copiados do vault-42 | Aprovada para a preservação neste projeto. Outros índices do vault podem precisar de ajuste de links após a retirada. Não abrange todo o vault nem todo o RPG nele existente. |
| Também `arquivo/originais/` | Não é a limpeza recomendada: elimina as cópias exatas, a restituição fiel de PDF/Word e afeta 101 links de consulta aos arquivos. Os dados de RPG auditados continuam em Markdown e anexos, mas a equivalência completa dos formatos originais deixa de ser garantida. |
| `conteudo/Fontes/` | Manter. É o acervo integral que sustenta citações, variantes e detalhes não repetidos na enciclopédia. |
| `conteudo/Anexos/` | Manter. Contém imagens, páginas, estrutura, dados exatos e estilos; a remoção afeta 252 links locais, além de eliminar informação que o Markdown não representa sozinho. |
| Google Drive ou diretório original de gravações | Fora do parecer. Há quatro imagens apenas catalogadas por URLs e nenhum pacote de áudio foi migrado. A transcrição não substitui o som original. |

A simulação de caminhos não encontrou dependência de consulta a `BASE INICIAL` ou aos 53 arquivos selecionados no vault: removê-los não quebra links de consulta deste conteúdo. Referências históricas nos metadados continuam documentando as origens, e alguns índices globais do vault foram intencionalmente deixados fora do recorte.

## Limites e manutenção

- Não houve nova renderização do Word. A conferência do DOCX é estrutural e textual; a dos PDFs usa extração fresca e inspeção dos PNGs já existentes.
- A reconstrução dos XLSX foi em memória, conferida por membros OOXML e leitor independente, sem abertura no Excel.
- Cores, estilos, células vazias formatadas e strings de texto rico continuam preservados no OOXML. Não se deve remover esse pacote supondo que a tabela Markdown seja uma reprodução completa da ficha.
- Os importadores e o verificador histórico ainda apontam para as pastas de entrada. Antes de executar a limpeza, convém adaptar a verificação para usar as cópias arquivadas quando a origem já tiver sido retirada. Isso é uma dependência de manutenção, não de leitura da wiki.
- O ZIP de transcrições não copiado como contêiner teve seus 15 membros conferidos com os arquivos arquivados, normalizando somente LF/CRLF. O TXT portátil do handoff difere do corpo arquivado apenas pela ausência da seção final de navegação.
- A conclusão vale para os arquivos e hashes auditados. Não significa autorização ou execução de exclusão.

Relatórios: [textos](textos.json), [documentos](documentos.json), [planilhas](planilhas.json), [dependências](dependencias.json) e [limites de escopo](limites.json).
