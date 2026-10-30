# Levantamento inicial — campanha de Fash e Glim

> Registro histórico do levantamento inicial. Em 2026-10-29, a remoção autorizada das duplicatas foi concluída; os links abaixo agora consultam as cópias preservadas. Veja o [registro da limpeza](limpeza/relatorio.md).

Data: 2026-10-29.

> Registro histórico anterior à execução. A transferência autorizada posteriormente está documentada no [relatório da migração](migracao/relatorio.md).

Pergunta deste levantamento: quais materiais de Fash e Glim existentes no `vault-42` devem ser considerados para uma base pública independente, sem incorporar o restante do segundo cérebro?

Este documento registra a pesquisa e as recomendações. A importação e a construção da wiki ainda não foram executadas. O `vault-42` e a `BASE INICIAL` foram usados apenas para leitura.

## Decisões informadas pelo jogador nesta conversa

- A base inteira será pública, incluindo o material da campanha que antes tinha classificação de segredo ou bastidor.
- Fash é o personagem da campanha antiga; Glim é o personagem da campanha em andamento.
- As campanhas pertencem à mesma continuidade, com 70 anos de separação entre suas épocas. Isso não fornece datas absolutas para cada acontecimento.
- O `vault-42` é um segundo cérebro pessoal e pode ser consultado para recuperar o material pertinente ao RPG.

## Material localizado

O [inventário em JSON](inventario-fontes.json) registra caminhos, classificação, tamanhos, hashes e verificações. A seleção preliminar contém **52 arquivos do vault**: 36 notas Markdown, 14 transcrições e dois arquivos de suporte. Os 12 arquivos da `BASE INICIAL` foram catalogados separadamente; há sobreposição entre os conjuntos.

| Conjunto | Quantidade | Utilidade |
| --- | ---: | --- |
| Projeto `Glim Sombrasselva` | 29 notas | Painel, diários, background, ficha resumida, cronologia, threads e sete notas de entidades. Inclui 14 notas de preparação dos diários das sessões 13–26. |
| Handoff do cenário | 1 nota | Síntese que conecta as campanhas, apresenta entidades, acontecimentos, fontes e divergências. |
| Esclarecimentos do jogador de 23/10 | 1 nota | Correções e confirmações que não estão integralmente nos diários. |
| Arquivo histórico de Fash | 1 nota | Índice de documentos e materiais antigos; não substitui o diário completo da `BASE INICIAL`. |
| Registros de fontes do Drive | 4 notas | Proveniência do background, diário, ficha de Glim e tesouro do grupo; alguns dados são snapshots antigos. |
| Transcrições de Glim | 14 arquivos TXT | Sessões 13–25 no pacote de exportação e sessão 26 em arquivo separado. |
| Suporte das transcrições | 2 arquivos | `LEIA-ME.txt` e `proveniencia.json`, com cobertura, lacunas, partes e hashes. |

Os caminhos completos de cada candidato constam no inventário. Localizações centrais:

- [Projeto Glim](../arquivo/originais/vault-42/20%20Projects/Glim%20Sombrasselva/Glim%20Sombrasselva.md).
- [Handoff do cenário](../arquivo/originais/vault-42/70%20Research/RPG%20-%20Handoff%20do%20cenario%20para%20o%20mestre.md).
- [Esclarecimentos de Fash e Glim](../arquivo/originais/vault-42/40%20Sources/RPG/2026-10-23%20-%20Esclarecimentos%20do%20jogador%20sobre%20Fash%20e%20Glim.md).
- [Índice histórico de Fash](../arquivo/originais/vault-42/90%20Archive/RPG/Fash%20Paleskin%20-%20Old%20Archive.md).
- [Cobertura e limites das transcrições](../arquivo/originais/vault-42/98%20Attachments/GLIM%20-%20Transcricoes%20por%20Sessao%20-%202026-10-20/LEIA-ME.txt).

## Sobreposições verificadas

**Verificação direta:** o handoff na `BASE INICIAL` tem o mesmo texto que a nota do vault, após normalizar quebras de linha e espaços externos.

**Verificação direta:** o background de Glim tem o mesmo corpo narrativo nos dois locais. A versão do vault acrescenta metadados e um cabeçalho documental.

**Verificação direta:** os dois diários Markdown de Glim têm as mesmas 27 entradas: sessões 1–26 e uma sessão solo. Os corpos coincidem ao desconsiderar marcação Markdown e diferenças de espaço. A `BASE INICIAL` organiza as entradas em ordem crescente; o consolidado do vault usa ordem inversa. Essa comparação não afirma identidade de bytes, títulos ou índice.

**Recomendação:** preservar essas versões como fontes identificadas e produzir uma única apresentação por sessão na wiki. Não duplicar acontecimentos ou nós do grafo por causa das diferentes exportações. A versão TXT do diário não foi comparada integralmente nesta etapa.

## Informações adicionais e correções úteis

**Documentado nos esclarecimentos do jogador:** Carruan é a capital real; a menção de Glim a Lazathar como capital foi identificada como erro do jogador. O trecho de Lazathar da campanha de Fash deve ser tratado no contexto onírico indicado pela fonte. Isso permite registrar uma errata sem alterar os diários originais.

**Documentado nos esclarecimentos do jogador:** Fash fundou o Ébano; Sociedade das Sombras é um nome da mesma organização. Okay é a reencarnação de Kael. A sobrevivência atual de Fash permanece incerta. Essas classificações não devem ser reduzidas a um único nível de certeza.

**Verificação direta:** a [nota curta de Ébano](../arquivo/originais/vault-42/20%20Projects/Glim%20Sombrasselva/%C3%89bano.md), de maio, ainda pergunta se o assunto corresponde a NPC, facção ou dívida pessoal. Os esclarecimentos posteriores já o identificam como organização. Portanto, copiar as notas curtas sem reconciliá-las preservaria dúvidas já respondidas.

**Documentado na cronologia:** a [cronologia de Glim](../arquivo/originais/vault-42/20%20Projects/Glim%20Sombrasselva/Glim%20Sombrasselva%20-%20Cronologia%20da%20Campanha.md) estima cerca de 55 dias até a sessão 19. As sessões 20–26 estão registradas como marcos posteriores, com intervalos ainda não reconciliados. Não há uma contagem atual exata pronta para publicar.

**Documentado nas notas de preparação:** arquivos chamados `Session NN Diary Draft` contêm análise da transcrição, distinção entre ON/OFF game, hipóteses e um diário canônico. O nome `Draft` não significa que todo o conteúdo seja descartável ou que o diário nele contido nunca tenha sido publicado. A análise pode fornecer fatos do cenário que Glim não presenciou.

**Verificação direta:** algumas fontes ainda mantêm metadados da captura de maio, embora tenham recebido atualizações posteriores. A data de captura inicial não deve ser usada isoladamente para decidir a versão atual de uma nota.

## Transcrições disponíveis e integridade

**Verificação direta:** os 13 consolidados das sessões 13–25 coincidem com seus hashes no manifest após normalizar CRLF para LF em memória. A sessão 26 também coincide com o SHA-256 registrado na nota de produção de 21/10. Nenhum arquivo foi normalizado no disco.

O pacote das sessões 13–25 registra 15 gravações e 14.971 entradas. A sessão 26 contém 1.831 entradas no arquivo local. Esses números descrevem o texto disponível e não garantem a fidelidade de cada fala ao áudio.

Limites documentados:

- O pacote não contém transcrições das sessões 1–12 ou da solo de 22/04.
- A sessão 13 começa depois do início da mesa.
- A sessão 14 reúne três partes com lacunas e timestamps que reiniciam.
- A sessão 15 tem gravação parcial.
- A sessão 21 registra cinco falhas de transcrição.
- A tentativa inicial de gravação da sessão 26 não tinha texto transcrito, segundo o registro local. O começo não deve ser reconstruído como se tivesse sido ouvido.
- O diretório em `G:` não ficou acessível nesta sessão. Gravações posteriores às cópias locais ainda precisam ser conferidas.

Os hashes foram verificados neste levantamento; não foi feita leitura contínua de todas as falas nem conferência com os áudios.

## Fronteiras que a importação precisa respeitar

**Mesmo nome não basta para unir fontes.** Há uma [nota de Fash com o background de Tinkar Daergel e Eldrosia](../arquivo/originais/vault-42/90%20Archive/RPG/Fash%20Paleskin.md). Os esclarecimentos não confirmam Eldrosia como nome oficial deste cenário. Esse background foi registrado como candidato que exige revisão de continuidade, fora dos 52 arquivos selecionados.

**Outras mesas são outro acervo.** Mundo de Auria, Index e outros personagens históricos têm material próprio no segundo cérebro. Não foram tratados como parte da campanha de Fash/Glim. Os índices globais de RPG também não devem ser copiados por encadeamento automático de links.

**Links para fora do recorte precisam de adaptação.** As notas apontam para painéis globais, índices e pastas do Drive. Na wiki independente, essas referências devem ser substituídas por destinos pertinentes à campanha ou mantidas como proveniência, conforme o caso.

**Há entidades sem nota própria.** A busca de destinos por nome de arquivo nas 36 notas selecionadas encontrou `Folha-Seca`, `Kenku` e `Tork` sem notas correspondentes. Esta é uma verificação de wikilinks por nome, não uma auditoria completa de aliases, links Markdown ou todas as entidades mencionadas em texto corrido.

**Imagens ainda são referências remotas.** A [nota de assets](../arquivo/originais/vault-42/20%20Projects/Glim%20Sombrasselva/Glim%20Sombrasselva%20-%20Assets.md) lista três imagens de Glim por links do Drive. O índice de Fash também aponta para uma imagem. Esses arquivos não foram recuperados nesta etapa.

## Recomendação para o próximo passo

**Proposta:** usar este projeto como base independente da campanha, com uma importação selecionada de cópias. Manter os originais no `vault-42` durante a transição e registrar a origem de cada arquivo. Isso aproveita a pesquisa existente sem trazer a estrutura inteira do segundo cérebro.

A preparação do conteúdo deverá:

1. Preservar documentos e transcrições como fontes identificadas, com suas lacunas.
2. Separar o texto do diário da análise usada para escrevê-lo.
3. Criar notas de sessão e de entidades com relações sustentadas pelas fontes.
4. Reconciliar notas antigas com confirmações explícitas posteriores, mantendo divergências quando não houver resolução.
5. Diferenciar fato em cena, relato de NPC, confirmação do mestre/jogador, sonho/visão e hipótese. A base ser pública não elimina essas diferenças.
6. Distinguir data da mesa, tempo dentro do mundo e época Fash/Glim, sem preencher datas desconhecidas.
7. Validar o recorte em uma amostra antes de processar todo o acervo.

Essa recomendação ainda não escolhe a tecnologia do site nem define o formato definitivo das notas.

## Pendências e registro desta etapa

- Confirmar se a produção dos próximos diários também passará para este projeto ou continuará no `vault-42`.
- Conferir gravações novas ou fontes ausentes quando o acervo original estiver acessível.
- Extrair e comparar o conteúdo dos PDFs, DOCX e XLSX da `BASE INICIAL`; nesta etapa, esses binários foram apenas catalogados.
- Revisar a continuidade do background de Fash antes de integrá-lo.
- Recuperar imagens e outras fontes remotas pertinentes na etapa de importação.

Arquivos criados nesta etapa: este levantamento e `inventario-fontes.json`. Não houve edição, movimentação, exclusão, commit ou push no `vault-42`. Os registros antigos de agentes foram consultados como histórico de proveniência, sem executar as ações neles descritas.
