# Organização enciclopédica — critérios

Execução autorizada pelo jogador em 2026-10-29. A etapa detalha personagens, lugares, facções, acontecimentos e objetos, conecta notas e reúne lacunas para uma sabatina posterior. As fontes, transcrições, diários e originais permanecem preservados.

## Evidência e redação

- Cada afirmação deve remeter a uma fonte local identificável, junto do parágrafo ou em nota de rodapé.
- Diferenciar observação em cena, relato de NPC, confirmação do jogador/mestre, memória, sonho/visão, hipótese e contradição de fontes. Informação documentada não significa verdade onisciente do mundo.
- O handoff é uma síntese útil. Quando só ele foi consultado, citar o handoff e declarar esse nível de evidência; não alegar leitura direta da transcrição apenas porque a síntese cita um timestamp.
- Consultar diretamente as fontes primárias para identidades, mortes, relações, mecanismos e divergências de maior impacto. Preservar as limitações quando a origem continua ambígua.
- Conhecimento público da base não implica conhecimento de todos os personagens na ficção.
- As notas devem conter os detalhes recuperáveis, sem estender por invenção um nome ou uma menção breve a uma biografia completa.
- Não fundir homônimos, transcrições incertas, lugares com função parecida, organizações ou artefatos por semelhança. Variantes recebem aliases somente quando há evidência de identidade.

## Estrutura das notas

Manter o frontmatter já adotado e usar `status: documentado_parcial`. Acrescentar `atualizado: 2026-10-29`. `origens` contém caminhos desde `conteudo/`, sem extensão opcional. Links usam caminhos completos desde essa raiz.

Uma nota deve apresentar, na medida sustentada pelas fontes: identidade ou função; história/ações; relações; estado mais recente; e dúvidas com links para pendências. Para lugares, registrar época, ocupantes, rotas e coordenadas somente se documentados. Para organizações, distinguir membros, dirigentes, aliados, inimigos e versões de sua agenda. Para eventos, separar participantes, sequência e consequências confirmadas das explicações propostas.

O cadastro `registro-entidades.json` coordena nomes e destinos entre os domínios. Novos nomes podem ser propostos nos manifestos dos domínios, com fonte e justificativa, evitando alterações concorrentes no cadastro comum.

## Pendências

Uma pendência é uma pergunta respondível, com identificador estável, categoria, prioridade, contexto, fontes e entidades afetadas. Não criar pergunta para toda frase incompleta: agrupar lacunas que dependem da mesma resposta, mantendo perguntas diferentes quando uma resposta não resolve a outra.

Prefixos: `PC` personagens, `LG` lugares, `FC` facções, `EV` acontecimentos, `IT` itens, `CR` cronologia e `FT` fontes/continuidade. As perguntas ficam em `Pendencias/<Categoria>/` e os índices permitem preparar a futura sabatina. Nesta etapa não se pede ao jogador que responda.

## Preservação e verificação

Nenhuma escrita em `Fontes/`, `Anexos/`, `Sessoes/`, `arquivo/`, `BASE INICIAL` ou no `vault-42`, exceto índices de navegação expressamente atualizados pelo integrador. Comparar o estado das fontes com o snapshot desta etapa, verificar destinos, aliases, perguntas e a integridade anterior da migração. Relatórios registram cobertura e limites sem afirmar pesquisa de arquivos não consultados.

Correções posteriores de apresentação em uma fonte convertida exigem evidência no original, cópia anterior e registro explícito dos hashes antes/depois em `correcoes-fontes.json`. Essa exceção permite recuperar marcações da fonte que a conversão não tornou visíveis; não permite reescrever dados ou alterar os arquivos originais. O snapshot histórico não é refeito silenciosamente.

## Sabatina em andamento — preferência do usuário em 29/10/2026

Priorizar questões que resolvam contradições entre fontes. Antes de perguntar, consultar os trechos comparados, conferir se tratam do mesmo objeto, lugar, momento e condição, e procurar esclarecimentos posteriores. Apresentar as versões e a incompatibilidade concreta; não pedir ao jogador que reconstrua um contexto que a própria base pode fornecer.

Diferença de grafia pode justificar uma confirmação de identidade. Ausência de notícia, motivação desconhecida, mistério ainda não revelado ou detalhe sem nome não constitui contradição documental por si só. Esses registros permanecem preservados, mas não orientam a fila imediata. Respeitar os adiamentos e as respostas já recebidas.

Orientação registrada em `conteudo/Fontes/Confirmacoes/2026-10-29 - Tariun sem noticias e prioridade para contradicoes.md`. Esta instrução atualiza a condução da sabatina, sem encerrar por suposição as demais pendências.


Orientação do jogador em 29/10/2026: após registrar cada resposta da sabatina, apresentar a próxima pergunta na mesma resposta, priorizando contradições documentais e evitando repetir questões adiadas ou já respondidas.


Geografia confirmada em 30/10/2026: a região do mapa de Fash e Eral são locais totalmente diferentes e distantes. Não propor identidades entre seus lugares ou grupos apenas por nomes e funções semelhantes. Exigir evidência positiva antes de levantar nova comparação. Isso não impede que documentos atuais, como os mapas de Firael, descrevam locais da região antiga. Fonte: conteudo/Fontes/Confirmacoes/2026-10-30 - Regiao de Fash distante de Eral.md.


Referência temporal confirmada em 30/10/2026: o mapa de Fash retrata a região há cerca de 70 anos, com muitas mudanças desde então. Distinguir geografia histórica de ocupação e condições atuais. O caso da água de Eral foi resolvido após a chegada do exército; a maioria dos problemas locais foi resolvida, sem lista exaustiva. Não presumir que toda lacuna do acervo represente missão ativa, nem encerrar individualmente todos os casos sem identificação. Fonte: conteudo/Fontes/Confirmacoes/2026-10-30 - Mapa antigo e resolucao dos problemas de Eral.md.


Voz de Glim — orientação do jogador em 30/10/2026: “Se você acredita é real” exprime também negação e negação plausível. Distinguir desconhecimento, suspeita, confirmação recebida e recusa de encarar algo. No caso da taverneira, ele considera provável a morte e evita buscar bolo para não lidar com a possibilidade; não foi informada comunicação explícita. Não atribuir essa motivação automaticamente a outras lacunas, nem converter o lema em regra mecânica dos poderes. Fonte: conteudo/Fontes/Confirmacoes/2026-10-30 - Negacao de Glim e morte da taverneira.md.


Grimório e negação — complemento de 30/10/2026: Glim vê a relação entre o livro e as mortes de Lilo e Piche; evita encará-la e acredita que o grimório é o que o torna Magnífico. Não retratá-lo como incapaz de perceber a ligação, nem transformar a crença em dependência comprovada de todos os seus poderes. Isso não revela a ele a ligação com Shar. Fonte: conteudo/Fontes/Confirmacoes/2026-10-30 - Grimorio negacao e identidade de Glim.md.


Lei sobre elfos — revisão de 30/10/2026: a anotação aparece antes do despertar definitivo. O jogador não recorda menção fora do sonho e acredita que era só onírica. Não atribuir a proibição como lei histórica ou atual da Carruan material; preservar a incerteza da lembrança. Carruan como capital real é confirmação independente, sem validar automaticamente o conteúdo político do trecho. Fonte: conteudo/Fontes/Confirmacoes/2026-10-30 - Proibicao de elfos lembrada como onirica.md.

## Critério atual de revisão — 30/10/2026

Esta orientação do jogador substitui a antiga ideia de completar toda informação desconhecida. Uma pergunta só entra se houver versões incompatíveis do mesmo acontecimento com impacto na narrativa ou um elo ausente entre fatos já narrados. Antes de perguntar, identificar fontes, comparar contexto e explicar qual erro de leitura a resposta evita. Diferenças de época, perspectiva ou camada onírica não são contradições por si sós.

Os metadados `classificacao_revisao` e `acao_revisao` governam a fila, independentemente do status histórico. Grupos: `contradicao`, `lacuna_de_sequencia`, `em_aberto`, `detalhe_sem_impacto` e `encerrada`. Ações: `perguntar`, `conferir_fontes`, `aguardar_fonte`, `consolidada` e `nao_perguntar`. Só as duas primeiras ações nos dois primeiros grupos geram tópicos prioritários. A entrevista exige ainda `retomar_na_sabatina: true`, pergunta focada, fontes, justificativa e impacto. Sem classificação, uma nova nota fica fora da fila por padrão.

Não inventar respostas, marcar mistérios como solucionados ou apagar perguntas antigas: o status original e o texto anterior estão preservados na auditoria `triagem-pendencias-2026-10-30.json`. O resumo da nota mostra primeiro a triagem atual. Não perguntar endereços, nomes, censos, organogramas ou resultados futuros apenas para preencher campos. Se não foi narrado, registrar o salto ou a incerteza sem exigir revelação. Toda atualização ocorre somente neste projeto; o Google Doc não deve ser alterado.
