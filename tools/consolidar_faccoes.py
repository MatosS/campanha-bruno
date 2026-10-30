"""Consolidação documentada de facções e criaturas; não modifica fontes ou índices."""
from pathlib import Path
import hashlib
import json
import re

from enciclopedia_comum import ROOT, CONTEUDO, FONTES, escrever, pendencia, fonte, link

SRC = dict(FONTES)
DATAS = {13:'2026-05-27', 14:'2026-06-17', 16:'2026-08-05', 17:'2026-08-17',
         18:'2026-08-25', 19:'2026-09-01', 20:'2026-09-02', 21:'2026-09-13',
         24:'2026-09-30', 25:'2026-10-05'}
for n, data in DATAS.items():
    SRC[f'T{n}'] = f'Fontes/Transcricoes/Glim - Sessao {n} - {data}'


def cite(codigo, detalhe):
    return fonte(SRC[codigo], detalhe)


NOTAS = []
PERGUNTAS = []


def nota(destino, titulo, tipo, campanhas, fontes, texto, aliases=None, perguntas=None):
    NOTAS.append(dict(destino=destino, titulo=titulo, tipo=tipo, campanhas=campanhas,
                      fontes=fontes, texto=texto, aliases=aliases or [], perguntas=perguntas or []))


def pergunta(numero, titulo, pergunta_texto, contexto, fontes, entidades, prioridade='media', natureza='lacuna'):
    PERGUNTAS.append(dict(id=f'FC-{numero:03}', titulo=titulo, pergunta=pergunta_texto,
                         contexto=contexto, fontes=fontes, entidades=entidades,
                         prioridade=prioridade, natureza=natureza))


pergunta(1, 'Estrutura e alcance atual do Ébano',
         'Como se organiza hoje o Ébano, quais territórios e guildas controla e como distribui comando e filiação?',
         'A fundação por Fash e a identidade Sociedade das Sombras foram confirmadas. As cartas descrevem destruição e adesão de guildas e posterior equilíbrio com o Mercado, mas não apresentam organograma ou fronteiras atuais. Esta pergunta trata da instituição; a sobrevivência individual de Fash pertence às pendências de personagens. ' + cite('J','Esclarecimentos — organizações') + ' ' + cite('T16','T16 01:24:01–01:25:49'),
         ['J','T16'], ['Faccoes/Ebano','Faccoes/Mercado Negro'])
pergunta(2, 'Nome e composição da organização de Firael',
         'Qual é o nome oficial da organização de Firael, quem pode integrá-la e como Firael e o Cérebro exercem autoridade sobre seus membros?',
         'A confirmação em off fixa Firael no comando e o Cérebro acima dele. O nome foi esquecido e a mesa fala em religião e organização de devoradores de mente sem fornecer um cadastro de espécies, adeptos ou cargos. Não basta uma variante automática para batizar a facção. ' + cite('T25','T25 01:10:49–01:15:05; 01:35:35; 01:40:05') + ' ' + cite('J','Esclarecimentos — organizações'),
         ['T25','J'], ['Faccoes/Organizacao de Firael','Criaturas/Devoradores de mente','Personagens/Cerebro Anciao'], 'alta')
pergunta(3, 'Aliança de Firael com o Mercado e operação em Eral',
         'Que objetivo explica a organização de Firael ajudar a conduzir os Magníficos contra o Mercado em Eral apesar da aliança entre as duas facções?',
         'O mestre explicita a aliança contra o Ébano e depois chama atenção para a contradição da operação local. As possibilidades de obter cérebros, atacar o dragão ou testar os Magníficos são especulações, não resposta estabelecida. ' + cite('T25','T25 01:44:37–01:45:56; 01:49:34–01:55:22'),
         ['T25'], ['Faccoes/Organizacao de Firael','Faccoes/Mercado Negro','Faccoes/Ebano','Faccoes/Magnificos'], 'alta', 'motivacao')
pergunta(4, 'Estrutura e rotas do Mercado Negro',
         'Quem dirige o Mercado Negro e quais vínculos formais unem suas guildas, os fornecedores goblinoides e as rotas usadas por Eral?',
         'As cartas distinguem guildas da rede, Silthan como pagador e comprador, e goblinoides apresentados pelo Mercado sem patente demonstrada. O destino dos pagamentos não prova localização da sede; compartilhar a rota halfling não prova autoria do transporte. ' + cite('T16','T16 00:52:17–01:00:04; 01:07:49–01:10:05'),
         ['T16'], ['Faccoes/Mercado Negro','Faccoes/Arena de Silthan','Lugares/Assentamento goblinoide'])
pergunta(5, 'Informante investigado pelo Mercado',
         'Quem enviou as cartas clandestinas sobre Eral e quem, se alguém, manipulava os Magníficos em nome de uma facção?',
         'As cartas interceptadas e a mudança de rotas são relatadas, mas a lista de suspeitos é uma investigação do Mercado. Ela não confirma que taverneira, Carlos, Arkhavel, Tork, rangers, igreja ou Kenku fossem agentes infiltrados. ' + cite('T16','T16 01:06:32–01:10:05; 01:20:09–01:23:14'),
         ['T16'], ['Faccoes/Mercado Negro','Faccoes/Magnificos','Faccoes/Conclave da floresta','Faccoes/Igreja de Kord'], 'alta', 'identidade')
pergunta(6, 'Propriedade e liquidação do negócio da arena',
         'Como se dividia a propriedade entre Silthan, conde, condessa e demais financiadores, e o que restou da rede depois da queda da arena?',
         'Os Kenku listam doze participantes financeiros e um casal de proprietários. As cartas chamam Silthan de dono e mostram a associação imposta pelo falso prefeito; não esclarecem contratos ou liquidação dos bens e interesses após a derrota. ' + cite('T13','T13 00:54:32–00:55:18') + ' ' + cite('T16','T16 00:58:17–01:00:46; 01:10:36–01:11:09'),
         ['T13','T16'], ['Faccoes/Arena de Silthan','Faccoes/Mercado Negro','Lugares/Arena de Eral'])
pergunta(7, 'Decisão e vínculos dos Kenku no saque',
         'O grupo Kenku planejou a traição com os atacantes, foi contratado por alguém ou decidiu agir durante a oportunidade, e qual foi o destino coletivo de seu núcleo familiar?',
         'A auditoria do Mercado terminou antes da contratação por Silthan. O ataque pelas costas e a mensagem do saque são evidência da traição; a coordenação prévia e o mandante não foram estabelecidos. Há cerca de 32 pessoas com famílias na contagem anterior, não 32 agressores confirmados. ' + cite('T13','T13 00:58:24') + ' ' + cite('T16','T16 01:11:36–01:16:21') + ' ' + cite('T18','T18 01:08:18–01:10:19; 01:16:04'),
         ['T13','T16','T18'], ['Faccoes/Kenku de Eral','Faccoes/Mercado Negro','Faccoes/Guarda de Eral'], 'alta', 'relacao')
pergunta(8, 'Responsabilidade e governo do Conclave da floresta',
         'Quem decide pelo Conclave da floresta e como o acordo de imunidade dos seis envolvidos na arena e a expedição desaparecida afetaram sua comunidade?',
         'Folha-Seca negocia em nome da comunidade sem informar seu cargo formal. As cartas revelam participação e ciência coletivas, enquanto a negociação exige apagar seis nomes. Esta pergunta é sobre responsabilidade e continuidade institucional, não o destino individual de Folha-Seca ou Hanta. ' + cite('T14','T14 01:35:56–01:36:40; 01:44:00–01:49:02') + ' ' + cite('T16','T16 01:02:02–01:03:56') + ' ' + cite('T18','T18 01:11:11'),
         ['T14','T16','T18'], ['Faccoes/Conclave da floresta','Faccoes/Arena de Silthan'])
pergunta(9, 'Círculo Vetrilus e nome Conclave das Bruxas',
         'O símbolo do Conclave das Bruxas e o Círculo Vetrilus designam a mesma convenção, uma rede de vassalos ou grupos distintos?',
         'O diário nomeia Morvessh, Selara e Lyvessa como Círculo Vetrilus no livro das bruxas, mas chama a marca da armadura enviada a Cogu de Conclave das Bruxas. Nenhuma dessas expressões demonstra identidade com o Conclave dos rangers de Eral. ' + cite('F','Fash — 07/11 e Dia 45'),
         ['F'], ['Faccoes/Circulo Vetrilus','Faccoes/Conclave das Bruxas','Faccoes/Conclave da floresta'], 'alta', 'nomenclatura')
pergunta(10, 'Rede de vassalos e continuidade das bruxas',
         'Como a rede de vassalos se relacionava com as três bruxas, e o que permaneceu dessa rede depois da campanha antiga e da Noite Eterna?',
         'O diário relata regiões de busca, um mestre dissidente e hipóteses de Elena sobre sacrifício entre bruxas. O jogador atribui a Noite Eterna à bruxa, mas não conhece o desenvolvimento posterior conduzido pelo mestre. Isso não determina quais membros, cargos ou territórios persistiram. ' + cite('F','Fash — 28/11–02/12') + ' ' + cite('J','Esclarecimentos — continuidade'),
         ['F','J'], ['Faccoes/Circulo Vetrilus','Faccoes/Conclave das Bruxas','Faccoes/Organizacao do Necromante','Eventos/Noite Eterna'])
pergunta(11, 'Igreja de Kord após o ataque a Eral',
         'Quem assumiu a igreja de Kord em Eral após a perda dos clérigos combatentes e qual é sua relação institucional com Tariun e outros templos?',
         'A transcrição distingue clérigos mortos dos padres sobreviventes. A presença de Tariun em Mercadia e a tradição de artefatos mostram contatos religiosos, mas não estabelecem uma hierarquia única ou reposição do templo local. ' + cite('T18','T18 01:08:18–01:14:24') + ' ' + cite('H','Handoff, síntese — Igreja de Kord e forças rivais'),
         ['T18','H'], ['Faccoes/Igreja de Kord','Lugares/Igreja de Kord em Eral'])
pergunta(12, 'Nome e subdivisões dos arquivistas',
         'Qual é o nome formal da organização dos arquivistas e de sua subdivisão de milagres, e como se relacionam escolas, anciões e representantes?',
         'Okay descreve uma organização mãe, escola compartilhada com Tahen e subdivisão acadêmica. Há anciões e outros visitantes, mas os cargos e fronteiras das instituições não estão definidos. A tradição milenar não a identifica com os Zodíacos. ' + cite('T24','T24 02:20:24–02:21:44') + ' ' + cite('T25','T25 00:01:41–00:04:18; 01:13:38–01:14:15'),
         ['T24','T25'], ['Faccoes/Arquivistas','Faccoes/Zodiacos'])
pergunta(13, 'Relatórios e resposta às expedições perdidas',
         'Que relatórios a organização conserva das duas expedições ao covil marítimo e que decisão institucional tomou sobre resgate, quarentena ou nova missão?',
         'Tahen relata desaparecimento dos dois grupos e barcos; o segundo tinha mais recursos e o mestre de Okay. Os anciões tendem a considerá-los mortos, mas isso é avaliação e não observação do desfecho. Okay se oferece para investigar. ' + cite('T24','T24 02:08:41–02:13:37'),
         ['T24'], ['Faccoes/Arquivistas','Lugares/Covil maritimo'], 'alta')
pergunta(14, 'Identidade e atividade da Lua Sangrenta',
         'Quem compôs a Lua Sangrenta, como a organização se manteve depois da Noite Eterna e qual é sua atuação atual?',
         'O mestre confirma que Lua Sangrenta é o grupo dos que enfrentaram a crise, e Okay recorda uma mulher desse grupo que alertou sobre corpos roubados. Não há lista de membros, estrutura ou mandato atual recuperados nestes trechos. ' + cite('T24','T24 01:20:08–01:21:53') + ' ' + cite('T25','T25 01:43:16–01:43:25'),
         ['T24','T25'], ['Faccoes/Lua Sangrenta','Eventos/Noite Eterna'])
pergunta(15, 'Estrutura e legado dos Zodíacos',
         'Como funciona a casta dos Zodíacos e a transmissão de seus artefatos, e quais ritos ou vínculos ainda existem na época de Okay?',
         'O pesquisador conhece apenas uma tradição de milênios e artefatos herdados. O mestre identifica em off os Zodíacos e a conexão com o personagem que renascia; flashes de ritos não são cadastro completo nem memória de todas as encarnações. ' + cite('T25','T25 00:01:41–00:04:18; 01:38:10'),
         ['T25'], ['Faccoes/Zodiacos','Personagens/Okay dBoa','Itens/Artefatos investigados pelos arquivistas'])
pergunta(16, 'Nome e continuidade da organização do Necromante',
         'Qual era o nome da organização do Necromante, quem eram os três julgadores e o que restou dela e de sua relação com o Ébano?',
         'Fash foi iniciado numa organização horizontal, majoritariamente conjuradora, ligada à necrópole. O jogador esqueceu o nome e não confirmou que ela fosse antecessora do Ébano. A possível tomada pelo Cavaleiro é hipótese condicional, tratada separadamente do fato da iniciação. ' + cite('F','Fash — sessão solo dos 45 dias') + ' ' + cite('J','Esclarecimentos — organizações'),
         ['F','J'], ['Faccoes/Organizacao do Necromante','Faccoes/Ebano','Lugares/Necropole'])
pergunta(17, 'Continuidade coletiva da Roda de Estopa',
         'A Roda de Estopa deixou registros, remanescentes organizados ou alguma continuidade depois de ser dispersa nos Doze Dias Rubros?',
         'O background canônico descreve a pequena trupe em fuga e fragmentação na crise. Não fornece uma reconstituição institucional posterior nem permite declarar a morte de todos os integrantes. Os destinos pessoais cabem às notas de personagens. ' + cite('B','Background — atos 2–3') + ' ' + cite('J','Esclarecimentos — background canônico'),
         ['B','J'], ['Faccoes/Roda de Estopa','Eventos/Queda da Roda de Estopa'], 'baixa')
pergunta(18, 'Reconstituição da Guarda de Eral',
         'A ajuda pedida após o saque chegou, e quem recebeu a responsabilidade de reconstruir a Guarda e o governo de Eral?',
         'Após a purga dos corruptos e a defesa da cidade, o relato do ataque mostra guarda desfeita, Tork morto e ausência de comando. Os sobreviventes dizem aguardar auxílio e novo prefeito, sem conclusão recuperada nesta pesquisa. ' + cite('T18','T18 01:08:18–01:14:24') + ' ' + cite('H','Handoff, síntese — consequências'),
         ['T18','H'], ['Faccoes/Guarda de Eral','Lugares/Eral'])
pergunta(19, 'Identidade da organização de traficantes de almas',
         'Qual é o nome e alcance da organização das máscaras com anzol, e como ela se relaciona com os compradores e autoridades do leilão?',
         'Okay presencia recolha e venda de almas por humanoides encobertos. O símbolo, idioma e trajeto não revelam espécie, dirigentes, filiação ou equivalência com outros captores encontrados na experiência. ' + cite('T17','T17 00:47:07–00:48:41; 00:52:44–01:01:08; 02:00:15–02:02:03'),
         ['T17'], ['Faccoes/Traficantes planares de almas','Eventos/Experiencia de Okay no amuleto','Lugares/Muro das Lamentacoes'])
pergunta(20, 'Pacto e governo das comunidades reassentadas',
         'Como ficaram a autonomia dos anões libertos e o pacto de proteção e ocupação de Throden pelos meio-dragões, inclusive na época atual?',
         'Kael rompe as coleiras, mas Fash percebe que os anões assumem de imediato que devem trabalhar para os libertadores. O reassentamento e a proteção remunerada por meio-dragões são planos e ações da época antiga; não definem governo, consentimento contínuo ou estado atual. ' + cite('F','Fash — 22/01–25/01 e solo dos 45 dias'),
         ['F'], ['Faccoes/Anoes libertos','Faccoes/Meio-dragoes de Throden','Lugares/Throden','Eventos/Reassentamento em Throden'])
pergunta(21, 'Correspondentes materiais das instituições do sonho',
         'Alguma instituição ou relação política vivida em Lazathar possui correspondente material confirmado, ou deve permanecer apenas no registro do sonho?',
         'A revelação de 25/10 desfaz a capital aparente e o jogador autoriza separar a cronologia onírica. Guildas, Circo, Torre e notícias de reinos não devem ser transplantados sem confirmação; tampouco o Circo equivale à Roda de Estopa. ' + cite('F','Fash — trecho de Lazathar e 25/10') + ' ' + cite('J','Esclarecimentos — sonho e geografia'),
         ['F','J'], ['Faccoes/Instituicoes de Lazathar','Lugares/Lazathar'], 'baixa', 'continuidade')
pergunta(22, 'Colônia dos Mind Shredders',
         'O que a inspeção de Ryld encontrou no posto e onde está a colônia principal, com seu estágio inteligente, na região de Eral?',
         'A mesa explica postos descartáveis e colônia oculta; duas larvas e um guerreiro são abatidos no posto. Ryld é encarregado de verificá-lo, mas o resultado e a eliminação da ameaça maior não aparecem nos trechos consultados. A reprodução pelo estágio superior é crença, não observação. ' + cite('T19','T19 00:56:58–01:05:58') + ' ' + cite('T20','T20 00:00:50–00:03:28') + ' ' + cite('H','Handoff, síntese — Mind Shredders'),
         ['T19','T20','H'], ['Criaturas/Mind Shredders','Lugares/Casa em quarentena','Eventos/Posto dos Mind Shredders'], 'alta')
pergunta(23, 'Destino e reprodução da magia viva',
         'O que ocorreu com o exemplar pequeno entregue a Arkhavel, e houve confirmação do mecanismo que produziu esse segundo exemplar?',
         'O diário descreve um pequeno ser semelhante à magia viva e registra surpresa de Okay e Arkhavel, pois reprodução não era esperada. Chamá-lo filhote relata a cena; não demonstra biologicamente uma nova espécie ou o mecanismo de reprodução. ' + cite('G','Diário de Glim — S10'),
         ['G'], ['Criaturas/Magia viva do sono','Personagens/Arkhavel','Eventos/Caso Carlos e magia viva'])
pergunta(24, 'Envenenamento e Crepúsculos Venenosos',
         'A tribo dos Crepúsculos Venenosos foi confirmada como responsável pelo veneno de Eral, e qual é sua relação política atual com a cidade?',
         'Okay identifica reptilianos especialistas em venenos pela descrição de Folha-Seca. A guerra anterior torna a suspeita plausível para Glim, mas Folha-Seca contesta a quantidade necessária para contaminar o lençol d’água e nenhuma autoria é provada nesse relato. ' + cite('G','Diário de Glim — S4–S5'),
         ['G'], ['Criaturas/Crepusculos Venenosos','Lugares/Eral','Faccoes/Guarda de Eral'], 'media', 'responsabilidade')


nota('Faccoes/Ebano', 'Ébano', 'faccao', ['fash','glim'], ['J','T16','T25','B'], f"""
## Identidade e origem

Ébano e Sociedade das Sombras são a mesma organização, fundada por {link('Personagens/Fash Paleskin','Fash')} depois da fuga dos acontecimentos finais de sua campanha. Essa identidade e a fundação são confirmações do jogador, que informa confirmação do mestre; não demonstram, por si, um cargo atual do fundador. {cite('J','Esclarecimentos de 23/10 — organizações')}

## Expansão e guerra

Na época de Glim, a organização cresceu tomando territórios do {link('Faccoes/Mercado Negro')}, destruindo guildas inteiras e incorporando outras. A exposição do mestre na leitura das cartas dá três versões para adesões: medo de destruição, reconhecimento de força e ganhos maiores. Não fixa uma motivação comum a todas as guildas. {cite('T16','T16 01:05:48–01:06:32; 01:24:01–01:25:49')}

O Ébano chegou a ter superioridade ampla, mas ataques da religião de {link('Personagens/Firael')} contribuíram para um equilíbrio com o Mercado. Na sessão 25, o mestre volta a apresentar a {link('Faccoes/Organizacao de Firael')} e o Mercado como aliados contra os assassinos das sombras. Isso descreve o conflito conhecido, sem mapear todas as regiões ou sua duração. {cite('T16','T16 01:24:41–01:25:49')} {cite('T25','T25 01:49:34')}

## Contatos e limites

{link('Personagens/Glim Sombrasselva','Glim')} fez serviços avulsos para {link('Personagens/Varo','Varo Cinzafrio')} no submundo ligado ao Ébano: distrações, facilitação e tarefas cuja violência ele preferia não encarar. A morte de {link('Personagens/Tom do Cesto')} motivou sua investigação da rede. A afinidade que percebe entre as sombras da organização e seu grimório é interpretação de Glim; não comprova origem mágica comum nem sua filiação formal. {cite('B','Background canônico — atos 4–6')}

As fontes consultadas não fixam organograma, dirigentes atuais ou fronteiras. A possível sobrevivência de Fash é hipótese do jogador e também aparece como chute do mestre; a continuidade institucional do Ébano não resolve esse destino pessoal. {cite('J','Esclarecimentos — organizações')} {cite('T25','T25 01:49:34')}
""", ['Ebano','Sociedade das Sombras'], [1,3,5])

nota('Faccoes/Organizacao de Firael', 'Organização de Firael', 'faccao', ['fash','glim'], ['J','T24','T25'], f"""
## Identidade e comando

Organização também descrita na mesa como religião e como organização de devoradores de mente, fundada e atualmente comandada por {link('Personagens/Firael')}. O mestre confirma em off que Firael nunca morreu no episódio do dragão e que o {link('Personagens/Cerebro Anciao','Cérebro')} é a autoridade acima dele. O nome formal não foi recuperado; as expressões descritivas não são nomes oficiais nem comprovam que todos os adeptos sejam da mesma espécie. {cite('T25','T25 01:35:35; 01:40:05')} {cite('J','Esclarecimentos — organizações')}

## Agenda e métodos

O jogador confirma que a organização rouba corpos e obtém conhecimento consumindo cérebros. Antes da explicação de Okay, os {link('Faccoes/Arquivistas','arquivistas')} relatavam corpos desaparecidos de pessoas com segredos, conhecimento ou influência e suspeitavam de vampirismo, necromancia ou comunicação com os mortos. Essas eram hipóteses sobre o mecanismo, não mecanismos simultaneamente confirmados. A recomendação deles era cremar e consagrar corpos. {cite('J','Esclarecimentos — organizações')} {cite('T25','T25 01:11:05–01:15:05')}

Os arquivistas dizem ter membros capturados e avaliam que o alvo são informações, não simplesmente fama ou poder. O caso de um mago morto, seu corpo roubado e o golem retirando o tesouro é contado por eles como evidência da apropriação de segredos; não é uma observação direta do consumo de seu cérebro. {cite('T24','T24 02:15:21–02:17:27')} {cite('T25','T25 01:11:05–01:15:05')}

## Conflitos e operação de Eral

A organização alia-se ao {link('Faccoes/Mercado Negro')} contra o {link('Faccoes/Ebano','Ébano')}. Porém, o material associado a ela ajudou a conduzir os {link('Faccoes/Magnificos','Magníficos')} contra a rede local do Mercado. O mestre salienta a contradição, sem fechá-la. Okay reconhece a letra de Firael nos pergaminhos e mapas; a informação sobre o nodo vem de conhecimentos antigos ligados ao Cérebro. {cite('T25','T25 01:35:18–01:40:05; 01:49:34–01:55:22')}

Matar o dragão, recolher cérebros de dragão e beholder ou explorar a ligação divina do grupo são possibilidades aventadas pelo mestre em linguagem especulativa. Não estão confirmados um plano completo, o conhecimento de que Okay é Kael reencarnado ou a posição física atual do Cérebro. A organização, a espécie {link('Criaturas/Devoradores de mente')} e os {link('Criaturas/Mind Shredders')} recebem entradas distintas. {cite('T25','T25 01:35:35–01:45:56')} {cite('H','Handoff, síntese — correções e Mind Shredders')}
""", [], [2,3,5])

nota('Faccoes/Mercado Negro', 'Mercado Negro', 'faccao', ['glim'], ['T13','T16','T25'], f"""
## Rede e domínio

Rede formada por várias guildas que reivindica controle de atividades ilícitas em sua região. As cartas exigiram tributo da arena de Eral sob ameaça de ataque. O mestre distingue explicitamente {link('Personagens/Silthan')} como comprador e pagador para poder existir, sem torná-lo membro de uma guilda formal do Mercado. {cite('T16','T16 00:52:17–01:00:04; 01:24:01')}

## Cativos, fornecedores e rotas

O Mercado vendia escravos à arena, incluindo devedores, inimigos e pessoas descartadas por autoridades, como mendigos de outras cidades. Como a oferta não supria as lutas, apresentou fornecedores goblinoides que capturavam humanos e outros povos. O grau formal de filiação desses grupos não foi demonstrado; a exposição não lhes atribui patentes ou autoridade sobre Silthan. {cite('T16','T16 00:53:44–01:00:04')}

No arranjo anterior, pagamentos saíam pela região goblinoide e mercadorias chegavam pela rota inferior também usada pelos halflings. Após interceptar cartas clandestinas para a capital, o Mercado unificou as viagens numa rota conhecida de poucos, a mesma da falsa viagem do prefeito. Compartilhar a rota não prova que halflings transportassem os cativos; o destino dos pagamentos não estabelece a sede central. {cite('T16','T16 00:53:44; 01:06:32–01:10:05')}

## Proteção, auditoria e rivais

O Mercado enviou os {link('Faccoes/Kenku de Eral','Kenku')} por cinco meses para verificar a flutuação do faturamento, com ordem de matar os responsáveis se a fraude se revelasse. Encerrada a auditoria sem essa conclusão, deixou de pagá-los, e Silthan contratou-os diretamente. O Mercado também matou o irmão de Silthan na capital como punição pelo uso não autorizado de seu nome para impedir o ataque do {link('Faccoes/Conclave da floresta')}. {cite('T16','T16 01:02:02–01:03:56; 01:11:36–01:16:21')}

Perdeu territórios e guildas para o {link('Faccoes/Ebano','Ébano')}; os ataques da {link('Faccoes/Organizacao de Firael')} ao rival equilibraram as forças. Essa aliança não explica por que a operação ligada a Firael prejudicou o Mercado em Eral. {cite('T16','T16 01:24:01–01:25:49')} {cite('T25','T25 01:49:34–01:55:22')}

## Investigação de infiltrados

As cartas suspeitam de taverneira, Carlos, Arkhavel, Tork, dois rangers, igreja de Kord, um Kenku e dos Magníficos como instrumentos de alguém. Trata-se da lista investigativa do Mercado, não de agentes identificados. A hipótese de uma guilda rival era uma entre várias. {cite('T16','T16 01:20:09–01:23:14')}
""", [], [3,4,5,6])

nota('Faccoes/Arena de Silthan', 'Negócio da arena de Silthan', 'grupo', ['glim'], ['T13','T16','H'], f"""
## Negócio e participantes

Estrutura de lutas, aprisionamento e finanças em {link('Lugares/Arena de Eral','Eral')}, dirigida por {link('Personagens/Silthan')}, que o mestre chama de dono da arena. A lista fornecida pelos Kenku inclui doze pessoas ligadas às finanças e caravanas, entre elas um conde e uma condessa apresentados como proprietários. A relação contratual entre Silthan, casal e demais financiadores permanece incompleta. {cite('T13','T13 00:54:32–00:55:18')} {cite('T16','T16 00:58:17–00:58:57')}

A guarda sustentava o funcionamento armado. Os prisioneiros incluíam escravos, criminosos e pessoas usadas como descarte pelo Mercado e por autoridades. A falta de crianças na arena é informação atribuída a um informante na síntese, sem permitir concluir que toda a cadeia de fornecedores não escravizasse crianças. {cite('T13','T13 00:55:18')} {cite('T16','T16 00:55:45–01:00:04')} {cite('H','Handoff, síntese — Arena, falso prefeito e filhos de Arkhavel')}

## Relações impostas e contratos

O empreendimento começou independente do {link('Faccoes/Mercado Negro')}, passou a comprar seus cativos e pagar tributo sob ameaça e recebeu por intermédio dele fornecedores goblinoides. O falso prefeito, na realidade um filho de Arkhavel controlando um humano, impôs sociedade. A soma dos pagamentos ao Mercado e a esse sócio retirou mais da metade do negócio de Silthan. O Aboleth era parceiro secreto do filho, desconhecido de Silthan e do Mercado. {cite('T16','T16 00:52:17–01:00:46; 01:10:36–01:11:09; 01:18:24–01:18:57')}

Depois de um ataque do Conclave, Silthan usou o nome do Mercado para negociar um acordo que incluía entrega de bestas mágicas. O Mercado o puniu pela alegação de proteção matando seu irmão. Também contratou diretamente os Kenku depois do fim da auditoria. Não há vínculo hierárquico único que transforme todos esses contratos na mesma facção. {cite('T16','T16 01:02:02–01:03:56; 01:11:36–01:16:21')}

## Queda e estado

A arena foi tomada pelos Magníficos; tesouro e cartas revelaram sua rede de pagamentos e acordos. A síntese registra a queda, mas não encerra o destino de todos os financiadores nem a liquidação de seus bens. {cite('H','Handoff, síntese — acontecimentos S16')}
""", ['Arena de Silthan'], [6,4])

nota('Faccoes/Kenku de Eral', 'Kenku de Eral', 'grupo', ['glim'], ['T13','T14','T16','T18'], f"""
## Grupo e famílias

Esta entrada descreve o grupo contratado em Eral, não todos os membros da espécie Kenku. Seus interlocutores declaravam doze combatentes e cerca de trinta e duas pessoas contando mulheres e crianças; desejavam viver na cidade mantendo os disfarces. O {link('Personagens/Kenku caolho')} foi um contato do grupo com os Magníficos, mas não há cargo de comando formal recuperado. {cite('T13','T13 00:58:24–00:59:24')} {cite('T14','T14 00:10:10')} {cite('H','Handoff, síntese — Kenku caolho')}

## Contratos e aliança oferecida

Foram enviados pelo Mercado para auditar cinco meses de caixa da arena e matar os responsáveis se a estabilidade demonstrasse fraude. A oscilação se confirmou; o Mercado encerrou seu contrato. Silthan então os contratou diretamente. A explicação do mestre é que trouxeram famílias de um lugar ruim e buscavam trabalho e residência, preservando o ocultamento diante da sociedade. O medo que Silthan teria do falso prefeito é uma interpretação possível para a contratação, não motivo provado por carta. {cite('T16','T16 01:11:36–01:16:21')}

Ofereceram nomes e apoio contra a arena e admitiam que o grupo verificasse suas informações. Ao mesmo tempo, recomendaram exterminar mulheres e crianças goblinoides para retirar a razão de permanência dos guerreiros. O mestre advertiu que isso poderia gerar retaliação. A proposta documenta sua disposição a violência contra indefesos e não deve ser apagada pela apresentação inicial de famílias buscando abrigo. {cite('T13','T13 00:54:32–00:59:24')}

## Traição e estado posterior

No ataque a Eral, os defensores relatam que Kenku atingiram primeiro os clérigos e depois a retaguarda da guarda, ajudando os goblinoides. O mestre confirma as mortes dos combatentes mais fortes pelos Kenku; o corpo de Tork tinha ferimentos nas costas. O grupo saqueou e partiu, deixando mensagem que agradecia aos Magníficos pelo saque. {cite('T18','T18 01:08:18–01:14:24; 01:16:04')}

A fala do mestre sugere que aproveitaram a oportunidade, mas o planejamento anterior, eventual mandante e paradeiro coletivo não são estabelecidos. A contagem de famílias não autoriza atribuir a cada pessoa participação no ataque. {cite('T18','T18 01:10:07–01:10:19; 01:12:31')} {cite('T13','T13 00:58:24')}
""", [], [7])

nota('Faccoes/Conclave da floresta', 'Conclave da floresta', 'grupo', ['glim'], ['T13','T14','T16','T18','H'], f"""
## Comunidade e representação

Comunidade fora dos muros de Eral com leis próprias, formada por rangers, druidas, fadas, centauros e simpatizantes. As estimativas do mestre variam de quase cinquenta a cerca de sessenta com aspirantes; não são censos idênticos de combatentes. {link('Personagens/Folha-Seca','Darian Folha-Seca Valek')} negocia pela comunidade; {link('Personagens/Hanta')} é um guia ranger, sem que os trechos fixem títulos ou hierarquia. {cite('T13','T13 01:11:44–01:13:22')} {cite('T14','T14 00:29:54')} {cite('H','Handoff, síntese — Eral, floresta e contatos')}

## Arena e responsabilidade coletiva

Folha-Seca corrige a versão de que os envolvidos entraram no negócio para salvar animais: a motivação original era outra, e a comunidade, quando soube, exigiu que ao menos conseguissem proibir animais nas lutas sob pena de exclusão. O motivo inicial não foi explicitado nessa conversa. {cite('T14','T14 01:35:56–01:36:40')}

As cartas mostram outra camada: o Conclave inteiro atacou a arena; Silthan evitou a morte invocando a proteção do Mercado. O acordo posterior incluía fornecer bestas mágicas. Poucos se responsabilizaram pelas entregas, mas o conjunto sabia da situação. Assim, envolvimento coletivo e execução individual das entregas são distinções necessárias. {cite('T16','T16 01:02:02–01:03:56')}

Folha-Seca ofereceu eliminar os guardas viajantes em troca de esquecer seis nomes e negar o vínculo com os crimes. Disse não saber nem querer saber o que esses membros fizeram fora de sua comunidade. O acordo foi aceito por Tork, segundo a síntese. Trata-se de imunidade negociada, não absolvição por investigação. {cite('T14','T14 01:44:00–01:49:02')} {cite('H','Handoff, síntese — Conclave e comunidade da floresta')}

## Alcance e incertezas

Depois da busca, os rangers e druidas não retornaram e não foram vistos nos dias anteriores ao relato do ataque. Isso não confirma a extinção de toda a comunidade nem a morte de cada integrante. O grupo de Eral não foi demonstrado como o {link('Faccoes/Circulo Vetrilus','Círculo Vetrilus')} ou o {link('Faccoes/Conclave das Bruxas')}; a semelhança do termo não basta. {cite('T18','T18 01:11:11')} {cite('H','Handoff, síntese — correções e Conclave')}
""", [], [8,9])

nota('Faccoes/Circulo Vetrilus', 'Círculo Vetrilus', 'faccao', ['fash','glim'], ['F','J','H'], f"""
## Convenção e origem relatada

Convenção de três bruxas: {link('Personagens/Morvessh')}, Lua; {link('Personagens/Selara')}, Mar; e {link('Personagens/Lyvessa')}, Grama. A leitura do livro levado da bruxa, registrada por Fash em 07/11, atribui a origem do Círculo à descoberta de um nó ou nodo de grande poder. É história do próprio livro, mediada pelo diário, não uma origem narrada por observador onisciente. {cite('F','Fash — 07/11')}

## Atividades e vítimas

O diário relaciona os sequestros, o demônio e o artefato que escraviza {link('Personagens/Elena','Elena / Serethyn')} a alimentar o nodo e receber poder. O livro questiona a biografia contada por Elena e sugere natureza mais poderosa; a hipótese divina é do narrador. Os mundos de sonho e a escravidão no artefato são parte central dessa perseguição, sem reduzir Elena a integrante voluntária da organização. {cite('F','Fash — 07/11')} {cite('H','Handoff, síntese — Bruxas, nodo e Elena')}

Vassalos foram distribuídos por regiões para procurar os fugitivos. Um mestre dissidente ofereceu proteção e aliança contra as bruxas. Elena aventou que Morvessh tivesse obrigado outra bruxa a um sacrifício para criar o ente corrompido e conservar controle dos vassalos; a morte de uma das três nesse ritual não é confirmada. {cite('F','Fash — 28/11–02/12')} {cite('H','Handoff, síntese — Bruxas, nodo e Elena')}

## Épocas e limites de identificação

O jogador atribui a {link('Eventos/Noite Eterna')} à bruxa na continuação conduzida pelo mestre depois da campanha antiga, mas não reconstitui suas etapas nem o estado das três membros. O nome {link('Faccoes/Conclave das Bruxas')} aparece separadamente numa marca de armadura, e a equivalência não foi demonstrada. O {link('Faccoes/Conclave da floresta')} de Eral também permanece separado. {cite('J','Esclarecimentos — continuidade e organizações')} {cite('F','Fash — Dia 45')} {cite('H','Handoff, síntese — correções')}
""", [], [9,10])

nota('Faccoes/Igreja de Kord', 'Igreja de Kord', 'faccao', ['glim'], ['G','T18','H'], f"""
## Presença e contatos

Instituição religiosa presente em Eral, aliada dos Magníficos em conflitos da cidade. A vigília de moradores com velas e oração a Kord ocorre após o caso das crianças; o diário a interpreta como resposta ao que o grupo fez. {link('Personagens/Tolomon','Tólomon')} é o responsável religioso que negocia ajuda de Arkhavel e comenta o amuleto de Crave. A síntese reúne esse papel, sem definir uma hierarquia universal da igreja. {cite('G','Diário de Glim — S6')} {cite('H','Handoff, síntese — Igreja de Kord e forças rivais')}

{link('Personagens/Tariun')}, sacerdote troglodita em Mercadia, ensina que força deve proteger e ser celebrada em desafios e competição, e que matar indefesos por medo do que farão é covardia. Oferece prisão e justiça como alternativas. Esses são ensinamentos dele registrados na síntese da sessão 23; não permitem deduzir uniformidade de todos os templos. {cite('H','Handoff, síntese de T23 — Igreja de Kord e forças rivais')}

## Defesa e perdas em Eral

A guarda e a igreja tomaram a frente contra os goblinoides. Os Kenku atacaram por trás, primeiro os clérigos, depois os guerreiros. O mestre confirma a morte dos clérigos combatentes mais fortes, restando padres que não lutaram. O relato também afirma que a defesa salvou muitas vidas; o resultado não estabelece quem recompôs o templo depois. {cite('T18','T18 01:08:18–01:14:24')}

## Tradição e oposição

O amuleto entregue por {link('Personagens/Rudiger')} a {link('Personagens/Crave')} e a provação do cinto são tradições religiosas relacionadas, com objetos distintos. Tólomon cogita manifestação de Kord na história de Rudiger; isso é hipótese de sacerdote. A síntese registra {link('Personagens/Hextor')} como inimigo de Kord e um emissário tentando recrutar Crave com promessa de força: sua fala é propaganda de rival, não diagnóstico imparcial da igreja. {cite('H','Handoff, síntese — Igreja de Kord, contatos religiosos e objetos')}
""", [], [11,18])

nota('Faccoes/Arquivistas', 'Arquivistas da sociedade élfica', 'faccao', ['glim'], ['T24','T25'], f"""
## Organização e pesquisa

Organização milenar ligada à sociedade élfica, com escola de arquivistas e subdivisões. {link('Personagens/Okay dBoa','Okay')} descreve sua atuação numa subparte dedicada a estudar milagres de forma acadêmica: causas, padrões e relação entre intervenções arcanas e divinas. {link('Personagens/Tahen')} estudou com ele e integra a mesma organização mãe. O nome formal e os cargos exatos não foram recuperados. {cite('T24','T24 02:20:24–02:21:44')} {cite('T25','T25 01:13:38–01:14:15')}

## Rede de apoio

Após notícias do ataque a Eral e ausência de notícias de Okay, Tahen e outros membros vieram verificar sua segurança. {link('Personagens/Elrohir')} chega com outros elfos na sequência registrada no Handoff; a pesquisa associada à ausência de avatares é uma investigação e hipótese, não prova de impedimento de todos os deuses. {cite('T24','T24 01:57:35–01:58:34; 02:13:19')} {cite('H','Handoff, síntese — Arquivistas e forças dos Magníficos')}

## Expedições desaparecidas

Tahen relata duas expedições a um possível covil de dragão acessível pelo mar sob um penhasco perto da região élfica. O primeiro grupo comunicou indícios de uma seita que cultuava e nutria o dragão e desapareceu; o segundo, mais experiente e armado, também sumiu com suas embarcações. O antigo mestre de Okay estava na segunda leva. {cite('T24','T24 02:08:41–02:11:41')}

A organização discute a resposta e mantém o lugar em quarentena. Os anciões tendem a julgar os desaparecidos mortos, mas o relato conserva preocupação com possíveis sobreviventes. Okay se oferece para investigar; isso não confirma que a missão já ocorreu. {cite('T24','T24 02:08:41; 02:11:41–02:13:37')}

## Segredos e adversários

Membros relatam capturas pela organização depois identificada como de Firael, que busca pessoas com segredos. Antes de saber do consumo de cérebros, suspeitavam de vampiros ou uso necromântico dos cadáveres; recomendavam cremação e consagração. O caráter milenar e as pesquisas sobre artefatos não tornam os arquivistas os {link('Faccoes/Zodiacos','Zodíacos')}: o mestre identifica esses últimos como o objeto de uma pesquisa de um colega. {cite('T24','T24 02:15:21–02:17:27')} {cite('T25','T25 00:01:41–00:04:18; 01:11:05–01:15:05')}
""", [], [12,13,2])

nota('Faccoes/Lua Sangrenta', 'Lua Sangrenta', 'faccao', ['fash','glim'], ['T24','T25','J'], f"""
## Identidade histórica

Organização dos que enfrentaram a {link('Eventos/Noite Eterna','Noite Eterna / Doze Dias Rubros')}. O mestre corrige explicitamente a expressão durante a sessão 24: a bruxa fez a Noite Eterna; Lua Sangrenta é o nome do grupo dos que salvaram a situação. O jogador situa a crise aproximadamente setenta anos antes de Glim. {cite('T24','T24 01:20:08–01:21:53')} {cite('J','Esclarecimentos — continuidade')}

## Contatos na época atual

Okay recorda uma mulher da Lua Sangrenta que alertara o grupo sobre corpos roubados e conhecimentos extraídos. Na conversa com os arquivistas, a organização é reconhecida como famosa. Esses trechos não fornecem nome da mulher, relação completa de membros, sede, dirigente ou alcance atual. {cite('T25','T25 01:10:24–01:10:43; 01:43:16–01:43:25')}

## Limites de evidência

A visão de Glim em que Lilo parecia querer “fazer a Lua Sangrenta” é problematizada pelo mestre: ilusões podem recombinar memórias e talvez enganar. Ela não prova participação histórica de Lilo na fundação ou na crise, nem altera a distinção entre grupo e acontecimento. {cite('T24','T24 01:20:08–01:21:53')}
""", [], [14])

nota('Faccoes/Zodiacos', 'Zodíacos', 'faccao', ['fash','glim'], ['T25','H'], f"""
## Tradição e artefatos

Organização antiga ligada a uma casta e a artefatos transmitidos entre gerações. Um pesquisador conta ter encontrado indícios de existência milenar, mas diz desconhecer o nome e considerar a história próxima de mito. O mestre identifica em off o assunto como os Zodíacos; a identificação do mestre e o conhecimento limitado do NPC devem permanecer distintos. {cite('T25','T25 00:01:41–00:02:59')}

## Kael e Okay

O mestre relaciona a organização ao antigo personagem que renascia, com a tradição chamada na conversa de Jade Phoenix Mage. Okay tem flashes de ritos e de um grupo diante de um artefato, sem possuir naquele momento uma memória contínua dessas experiências. Ao recuperar Kael, não recupera automaticamente lembranças que Kael já obtivera de vidas anteriores. Isso não estabelece cargos, lista de encarnações ou regras completas da organização. {cite('T25','T25 00:02:38–00:04:18; 01:38:10')}

## Outras aparições e distinções

A síntese do diário antigo registra figura encapuzada com símbolos do zodíaco na destruição da esfera de Elena; identidade e finalidade da intervenção permanecem abertas. Os atuais {link('Faccoes/Arquivistas','arquivistas')} pesquisam a tradição, mas não foram equiparados aos Zodíacos. O cajado novo ligado a Timo tampouco foi classificado como um artefato herdado deles. {cite('H','Handoff, síntese — Destruição do artefato e criaturas de luz')} {cite('T25','T25 00:02:38–00:02:59; 01:02:01–01:04:00')}
""", [], [15,12])

nota('Faccoes/Organizacao do Necromante', 'Organização do Necromante', 'faccao', ['fash','glim'], ['F','J','H'], f"""
## Identidade e ingresso

Organização sem nome recuperado, associada ao {link('Personagens/Necromante','Necromante')} e a uma {link('Lugares/Necropole','necrópole')}. Era composta majoritariamente por conjuradores, mas convidou Fash pelas outras habilidades que poderia oferecer. A iniciação exigiu enviar ossos de dragão do fosso por um saco mágico; Fash empregou trabalhadores meio-dragões e concluiu a tarefa sozinho. {cite('F','Fash — sessão solo dos 45 dias')} {cite('J','Esclarecimentos — organizações')}

## Regras e integrantes conhecidos

No acampamento com outros membros, o Necromante descreveu uma organização horizontal, sem líderes no sentido usual, mas com três pessoas em posição superior para julgamentos. Não havia obrigação geral de aceitar tarefas; a importância dependia de contribuição. Era proibido agir contra a existência do grupo, inclusive omitindo informação crítica. Fash fez o compromisso e passou por ritual. {cite('F','Fash — sessão solo dos 45 dias')}

{link('Personagens/Lidia','Lídia')}, fantasma, vigiava Fash desde o encontro inicial; após o ingresso, a vigilância seria encerrada. Ele recebeu pergaminhos de necromancia e um esqueleto guerreiro. As primeiras questões eram o risco representado por Firael, sem ordem de assassinato direto, e a passagem subterrânea onde se perdera a ligação com Lídia. {cite('F','Fash — sessão solo dos 45 dias')}

## Relações e continuidade

O Necromante aparece na síntese como mestre dissidente da rede de vassalos das bruxas, oferecendo aliança contra elas. Ele via o Cavaleiro da Morte adormecido como ameaça que mobilizaria mortos-vivos numa guerra caótica sem objetivo e indicou a necrópole junto ao rio, abaixo dos Equiceps. A avaliação do Cavaleiro é fala do Necromante. {cite('H','Handoff, síntese — Bruxas, nodo e Elena')} {cite('F','Fash — sessão solo dos 45 dias')}

O jogador não recorda o nome do grupo e só considera condicionalmente que o Cavaleiro possa ter tomado a necrópole. Não confirmou essa conquista nem que a organização tenha se transformado no Ébano; o vínculo conhecido entre as duas é Fash, em momentos diferentes. {cite('J','Esclarecimentos — organizações')}
""", [], [16,10])

nota('Faccoes/Roda de Estopa', 'Roda de Estopa', 'grupo', ['glim'], ['B','J'], f"""
## Trupe e acolhimento

Pequeno circo itinerante do background canônico de Glim, com duas carroças, lona remendada e apresentações breves nas povoações. O ato 2, narrado na perspectiva de {link('Personagens/Brakka Pedramansa')}, apresenta {link('Personagens/Dornal','Dornal Três Dedos')} como mestre de pista. Brakka assume responsabilidade pelo recém-chegado Glim e garante sua entrada; os juízos afetivos da narradora são perspectiva dela. {cite('B','Background — ato 2')} {cite('J','Esclarecimentos — background canônico')}

Glim começa fazendo trabalho de manutenção e depois oferece ilusões e sombras em palco, reforçando sua persona “O Magnífico”. O mago {link('Personagens/Harlom Vinte-E-Dois')}, {link('Personagens/Rumo')} com sua música e {link('Personagens/Miri')} com suas piadas estão entre os integrantes nomeados. Harlom reage com medo a uma página do grimório e aconselha Glim a não mexer nisso; sua reação não identifica a origem do livro. {cite('B','Background — ato 2')}

## Doze Dias Rubros e dispersão

O ato 3 mostra a trupe sem defesas preparadas diante da noite vermelha e dos mortos que se levantam: tenta reunir pessoas, foge com carroças e perde a coesão sob medo, frio e ataques. Brakka desaparece do lado de Glim em seu relato fragmentado; não há contagem segura de sobreviventes ou prova de morte de cada integrante. {cite('B','Background — ato 3')}

O grupo pertence à vida de Glim e não deve ser fundido ao Circo de Lazathar vivido por Fash em sonho. A destruição e dispersão são parte da crise identificada pelo jogador como Noite Eterna, aproximadamente setenta anos antes da campanha atual; não há reconstituição posterior da Roda nas fontes consultadas. {cite('B','Background — atos 2–3')} {cite('J','Esclarecimentos — continuidade e sonho')}
""", [], [17])

nota('Faccoes/Guarda de Eral', 'Guarda de Eral', 'grupo', ['glim'], ['G','T13','T14','T16','T18','H'], f"""
## Instituição e corrupção

Força de segurança de Eral com setores comprometidos com apostas, arena e proteção de interesses privados. O diário registra acusações de Folha-Seca de que guardas deixavam de investigar por interesse ou dinheiro; a lista depois fornecida pelos Kenku nomeia quarenta soldados envolvidos. A lista é documento informativo do caso, não prova de que todo guarda da cidade estivesse no mesmo esquema. {cite('G','Diário de Glim — S5')} {cite('T13','T13 00:54:32–00:55:18')}

{link('Personagens/Tork')} tentava agir, mas retaliações contra civis limitavam suas investigações. O mestre explica a possibilidade de executar corruptos um a um por emboscada usando a autoridade para convocá-los, em vez de vitória aberta sobre todos. A síntese registra a purga e a relutância em aceitar o apagamento dos nomes do Conclave em troca de ajuda contra guardas viajantes. {cite('T13','T13 01:13:41–01:14:48')} {cite('H','Handoff, síntese — consequências e Conclave')}

## Defesa da cidade e colapso

Após a derrubada do esquema, a guarda e os clérigos de Kord enfrentaram o ataque goblinoide. Kenku os atingiram por trás. Tork foi encontrado morto com ferimentos nas costas; o mestre atribui claramente aos Kenku a morte dos defensores mais fortes. A conversa conta seis guardas com Tork na defesa, e não recompõe um efetivo completo da cidade. {cite('T18','T18 01:08:18–01:14:24')}

Os sobreviventes dizem não haver ninguém comandando a cidade e que haviam pedido ajuda e novo prefeito. Na sessão 20, Glim comenta que já não existe uma guarda capaz de verificar o posto de Mind Shredders; a inspeção acaba ligada a Ryld, segundo a síntese. A restauração institucional não é demonstrada nos trechos consultados. {cite('T18','T18 01:10:39–01:11:11')} {cite('T20','T20 00:04:07')} {cite('H','Handoff, síntese — Mind Shredders')}
""", [], [18,5])

nota('Faccoes/Traficantes planares de almas', 'Traficantes planares de almas', 'grupo', ['glim'], ['T17'], f"""
## Identificação observada

Grupo encontrado por Okay durante a experiência ligada ao amuleto de Crave. Cerca de cinco humanoides de estatura aparentemente humana, falando comum, vestiam roxo e preto, cobriam o rosto e portavam no lado direito da máscara um anzol. “Humanos” é impressão de aparência, não espécie identificada. Não há nome oficial ou dirigente revelado. {cite('T17','T17 00:47:07–00:48:41')}

## Captura e comércio

O grupo reconhece Okay como alma recém-chegada no Muro das Lamentações e o retira para vendê-lo. Leva almas por um trajeto próximo à guerra de demônios e diabos até uma cidade com habitantes e compradores diversos; ali realiza leilão público. O relato estabelece tráfico e escravização de almas, sem demonstrar afiliação de todos os moradores da cidade à mesma organização. {cite('T17','T17 00:47:07–00:48:41; 00:52:44–00:55:38')}

Okay é comprado por mulher aparentemente humana, cuja possível natureza de súcubo é inferência da cena; mais tarde ela o engole. Essa compradora não foi identificada como dirigente dos vendedores. Tampouco a descrição demonstra que os captores anteriores que o levaram a tortura no Abismo pertenciam ao mesmo grupo das máscaras com anzol. {cite('T17','T17 00:22:03; 00:56:15–01:01:08')}

## Natureza da experiência e alcance

Depois, pesquisas de Okay encontram nos livros correspondências de criaturas e detalhes que antes desconhecia. O mestre afirma que a vivência é realidade. Isso valida a experiência no alcance declarado pela mesa; o mecanismo de conexão com o amuleto, as passagens e a morte e retorno não fica explicado, nem revela o alcance político da organização. {cite('T17','T17 02:00:15–02:02:03')}
""", [], [19])

nota('Faccoes/Conclave das Bruxas', 'Conclave das Bruxas nos registros antigos', 'grupo', ['fash'], ['F','H'], f"""
## Nome documental

Designação encontrada no diário de Fash no Dia 45: uma armadura animada trazia no peito o símbolo do Conclave das Bruxas e se aproximava da entrada da cidade drow. Esta é uma entrada para o nome e sua marca, sem completar uma organização por semelhança de palavras. {cite('F','Fash — Dia 45')}

## Ação conhecida

O relato associa o construto à procura por Cogu; a síntese registra sua destruição por Kael e Timo. A marca aponta vínculo com as bruxas no registro, mas não fornece rol de membros, dirigentes, sede ou tratados. {cite('F','Fash — Dia 45')} {cite('H','Handoff, síntese — Duelo, traição e fim da campanha')}

## Identidades ainda abertas

O livro das três bruxas chama a convenção de Morvessh, Selara e Lyvessa de {link('Faccoes/Circulo Vetrilus','Círculo Vetrilus')}; não há equivalência explicitada entre os dois nomes nos trechos consultados. O {link('Faccoes/Conclave da floresta')} de Eral é outra comunidade documentada, sem identidade comprovada com qualquer dessas designações antigas. {cite('F','Fash — 07/11 e Dia 45')} {cite('H','Handoff, síntese — correções')}
""", [], [9,10])

nota('Faccoes/Magnificos', 'Os Magníficos', 'grupo', ['glim'], ['G','T16','T18','H'], f"""
## Identidade do grupo

Nome usado pelo grupo de {link('Personagens/Glim Sombrasselva','Glim')}, {link('Personagens/Okay dBoa','Okay')}, {link('Personagens/Crave')} e {link('Personagens/Ryld')}, reunido no percurso até Eral e no trabalho para {link('Personagens/Arkhavel')}. A manifestação privada de fogo, sombra, luz e pressão invisível na caravana é relatada na síntese; a cooperação não significa que o grupo já soubesse a origem de cada poder. {cite('H','Handoff, síntese — personagens centrais, forças e S1')}

“Magnífico” nasce também da apresentação de palco e autoconstrução de Glim. Títulos como Soberano das Sombras e chefe de assistentes são usados por ele como performance ou brincadeira; não estabelecem hierarquia objetiva, nível de poder ou domínio sobre os companheiros. {cite('B','Background — ato 2')} {cite('G','Diário de Glim — S4–S6')}

## Atuação e alianças

O grupo soluciona os casos da Fada Órfã, Vasuthant e magia viva e atua contra o esquema do prefeito e da arena, obtendo cartas que expõem suas relações. Negocia com guardas, igreja, Kenku e Conclave, com compromissos e graus de informação diferentes. Tork recebe o título de Primeiro Magnífico Honorário depois da purga; o título honra a relação, sem demonstrar uma patente permanente. {cite('G','Diário de Glim — S5, S8 e S10')} {cite('T16','T16 00:51:56–01:25:49')} {cite('H','Handoff, síntese — S16 e Tork')}

## Reputação, perdas e riscos

O grupo retorna a Eral atacada e descobre a traição Kenku, mortes dos aliados e a cidade sem comando. A mensagem de saque explora ironicamente o nome Magníficos. As cartas do Mercado os tratavam como possíveis instrumentos de um infiltrado; depois o mestre salienta a operação ligada a Firael. Essas avaliações adversárias não retiram a agência do grupo nem demonstram uma aliança consciente com Firael. {cite('T18','T18 01:08:18–01:16:04')} {cite('T16','T16 01:17:32–01:23:14')} {cite('H','Handoff, síntese — Organização ou religião de Firael')}

Na fase posterior, a síntese registra escravos resgatados e também massacre de indefesos nas cavernas e quinze reféns humanos mortos nos setores não salvos. São consequências concretas da atuação; a marca Magníficos não é juízo moral do narrador. A torre segue como base e preparativo para novas viagens ao corte da sessão 26. {cite('H','Handoff, síntese — consequências e acontecimentos S21–S26')}
""", ['Magníficos'], [3,5])

nota('Faccoes/Meio-dragoes de Throden', 'Meio-dragões de Throden', 'grupo', ['fash','glim'], ['F','H'], f"""
## Comunidade e reassentamento

Comunidade de meio-dragões da campanha antiga, ligada à vila que os registros situam em U27 e ao antigo Forte humano, Q23, posteriormente chamado {link('Lugares/Throden','Throden')}. As coordenadas são recuperadas da síntese da versão PRONTO, não de nova conferência cartográfica. No diário, a migração para o Forte acontece gradualmente. {cite('H','Handoff, síntese — Forte, cidade drow e lugares')} {cite('F','Fash — sessão solo dos 45 dias')}

Após a morte do Druida Sangrento, o acordo previsto transferia humanos para a cidade subterrânea e meio-dragões para o Forte, com proteção remunerada. Isso descreve um arranjo de ocupação e serviço, sem tornar os meio-dragões propriedade do grupo ou membros da organização do Necromante. {cite('H','Handoff, síntese — Forte, cidade drow e libertações')} {cite('F','Fash — 22/01–25/01')}

## Trabalhos e segurança

Fash contratou trabalhadores para escavar o fosso de ossos e depois concluiu sozinho o envio ao Necromante. Patrulhas de meio-dragões avisaram da armadura animada que se aproximava; um Nyth invisível ameaçava a região e Fash o eliminou durante a espera pelos trolls. Essas tarefas registram relações concretas com o grupo antigo, sem um chefe comunitário nomeado. {cite('F','Fash — Dia 45 e sessão solo dos 45 dias')}

## Estado e limites

O diário termina sem estabelecer o destino coletivo após o acordo com os trolls e o dragão. Os mapas atuais na síntese descrevem a antiga região em termos de trolls e dragão negro, mas isso não prova extermínio ou condição atual dos reassentados. Não há governo, efetivo ou permanência do contrato de proteção confirmados para a época de Glim. {cite('H','Handoff, síntese — Duelo, traição, lugares e pergaminhos')} {cite('F','Fash — abertura e sessão solo')}
""", [], [20])

nota('Faccoes/Anoes libertos', 'Anões libertos', 'grupo', ['fash','glim'], ['F','H'], f"""
## Escravidão e comunidade

Anões mantidos escravizados pelo {link('Personagens/Druida Sangrento')} na cidade drow, sob coleiras mágicas. Fash registra que todos haviam nascido nessa condição e transmitiam dentro dela a cultura anã; eram forçados a produzir, inclusive estátuas de Lolth e itens usados no tributo aos trolls. A comunidade documentada não é automaticamente toda a antiga civilização anã. {cite('F','Fash — 25/01')}

## Libertação

Depois do golpe fatal de Kael no Druida Sangrento e da transferência da autoridade das coleiras ao assassino após 24 horas, Kael usou a palavra de comando para libertá-los. Fash incentivou crianças a quebrar as estátuas e compartilhou comida. O relato descreve libertação real das coleiras e a comoção do encontro. {cite('F','Fash — 22/01–25/01')}

Fash também percebeu que os libertos assumiram imediatamente que deveriam trabalhar para os libertadores e questionou o alcance dessa liberdade. Sua reflexão é parte da fonte: não deve apagar a ruptura do mecanismo mágico nem declarar autonomia social e consentimento plenamente resolvidos. {cite('F','Fash — 25/01')}

## Trabalho, relações e estado

Os anões explicaram o pagamento aproximadamente semestral aos trolls e continuaram a preparar utensílios. Alguns falavam gigante, mas o grupo hesitou em deixá-los negociar sem supervisão por medo da descoberta da mudança de ocupantes. Passagens foram adaptadas para circulação de anões e humanos. Isso documenta participação na reconstrução, sem dirigente, constituição ou desfecho coletivo atual conhecidos. {cite('F','Fash — 25/01, 08/02 e sessão solo')} {cite('H','Handoff, síntese — Forte, cidade drow e libertações')}
""", [], [20])

nota('Faccoes/Instituicoes de Lazathar', 'Instituições do sonho de Lazathar', 'grupo', ['fash'], ['F','H','J'], f"""
## Condição do registro

Conjunto de instituições vivido por Fash no trecho de Lazathar, depois revelado como sonho ou camada do cativeiro. A revelação de 25/10 e os esclarecimentos do jogador impedem usar sua capital e política como história material sem confirmação. Carruan é a capital real; a ocorrência de Lazathar no diário de Glim foi corrigida como erro do jogador. {cite('F','Fash — 25/10')} {cite('J','Esclarecimentos — sonho e geografia')}

## Guildas, serviços e autoridades do sonho

Filipe Vander, da Torre dos Magos, menciona Conclave, Taverna, Quartel, Coliseu e Circo, além de guildas do submundo que desconhece. Timo recebe do Conclave fora dos muros um serviço para eliminar um tipo de lobo de gelo. A síntese registra o Circo oferecendo rede de transporte e exigindo encerrar assassinatos da favela sem investigação profunda. Esses serviços pertencem à experiência onírica registrada, sem identidade comprovada com o Conclave de Eral ou com a Roda de Estopa. {cite('F','Fash — trecho de Lazathar, conversa com Filipe e Timo')} {cite('H','Handoff, síntese — Instituições e pessoas do sonho')}

A Lâmina da Meia-Noite aparece como guilda infiltrada por Fash; na prova da ira, Roger Cangles, chefe da guarda, é citado como contato dos assassinatos. Billy investiga cadáveres e chantagens; a igreja e a guarda entram em conflito na investigação de Thorn. São relações narradas no sonho, não condenações confirmadas de pessoas materiais. {cite('H','Handoff, síntese — Provas iniciais e Instituições e pessoas do sonho')}

## Notícias políticas e incertezas

O sonho apresenta família real élfica, tratado humano-anão, refugiados bárbaros e Taruk como unificador goblinoide em notícias ou rumores. Sua presença registra pistas e temas do cativeiro, sem estabelecer nomes oficiais de reino, governantes materiais ou continuidade dessas instituições na época de Glim. O propósito das camadas de sonho permanece desconhecido do jogador. {cite('H','Handoff, síntese — Instituições e pessoas do sonho')} {cite('J','Esclarecimentos — sonho e geografia')}
""", [], [21])


nota('Criaturas/Mind Shredders', 'Mind Shredders', 'criatura', ['glim'], ['T19','T20','H'], f"""
## Espécie e desenvolvimento explicado na mesa

Criaturas de organização semelhante a colmeia ou formigueiro, identificadas na sessão 19. Segundo o conhecimento dado pelo mestre, larvas consomem Sabedoria, formam casulo e evoluem para guerreiro grande chamado Walker, também grafado Horror na síntese. Com mais alimentação, outro casulo produz forma menor, mais inteligente e mágica, transcrita Zhental ou Zental. As grafias automáticas oscilam; não representam espécies adicionais confirmadas. {cite('T19','T19 00:56:58–00:59:11')} {cite('H','Handoff, síntese — Mind Shredders')}

## Capacidades e alimentação

As larvas atacam com dois tentáculos: podem causar ferimento e drenar Sabedoria, ou usar toque para apenas drená-la. A drenagem concede pontos de vida temporários. A explicação dá visão no escuro de 60 pés e sentido de mentes a 20 pés para larvas; o guerreiro detecta a 40 pés e possui salto extraordinário, com exemplo médio de 45 pés. São capacidades explicadas nesta mesa, não uma ficha externa completa. {cite('T19','T19 01:00:25–01:05:58')}

A mesa afirma que vivem bastante sem alimentar-se e que o consumo serve sobretudo à evolução. Não acumulam tesouros como objetivo. A produção das larvas pelo estágio superior é apresentada como crença de conhecimento incompleto, não observação de reprodução. {cite('T20','T20 00:01:27–00:03:28')}

## Colônia e posto de Eral

O estágio inteligente mantém colônia oculta, com postos distantes e descartáveis para incursões e alimentação. Isso preserva a colônia se um posto for descoberto. A construção interna é descrita como alienígena, dura e resistente, além do trecho inicial de terra instável. A casa em quarentena é interpretada como um desses postos, sem localização da colônia principal. {cite('T19','T19 00:58:47–00:59:11')} {cite('T20','T20 00:00:50–00:03:28')}

Duas larvas e um guerreiro foram mortos; a síntese registra que Ryld ficou encarregado de inspecionar o local, mas o resultado não foi recuperado. Eliminar os três indivíduos vistos não resolve automaticamente a colônia. Os Mind Shredders são distintos dos {link('Criaturas/Devoradores de mente')} e da {link('Faccoes/Organizacao de Firael')}, mesmo quando a transcrição mistura termos na leitura de habilidades. {cite('H','Handoff, síntese — Mind Shredders e correções')} {cite('T19','T19 01:02:26')}
""", [], [22])

nota('Criaturas/Devoradores de mente', 'Devoradores de mente', 'criatura', ['fash','glim'], ['G','T25','J','H'], f"""
## Uso do nome e indivíduos

Nome de criaturas distinguido pela mesa dos Mind Shredders. No diário da sessão 4, Glim encontra um devorador de mentes numa reunião cordial de Arkhavel com visitantes planares. O visitante pede um escaravelho vivo e fala diretamente na mente de Glim para fixar prazo de trinta dias. Essa cena observa comunicação mental e um contrato específico; não estabelece filiação desse indivíduo a Firael. {cite('G','Diário de Glim — S4')} {cite('H','Handoff, síntese — correções e amigos de Arkhavel')}

## Organização que consome cérebros

A {link('Faccoes/Organizacao de Firael')} é chamada de organização dos devoradores de mente na confirmação do mestre sobre seu fundador e líder atual. O jogador confirma roubo de corpos e aquisição de conhecimento pelo consumo dos cérebros. Isso descreve o método documentado dessa organização; não prova que todo indivíduo da espécie encontrado no cenário a integre ou tenha essa agenda. {cite('T25','T25 01:35:35; 01:40:05; 01:43:25')} {cite('J','Esclarecimentos — organizações')}

O {link('Personagens/Cerebro Anciao','Cérebro Ancião')} tem entrada de indivíduo e autoridade acima de Firael. A história de sua prisão e a ligação hierárquica não autorizam acrescentar aqui um ciclo biológico, população universal ou ecologia que a mesa não explicou. Os {link('Criaturas/Mind Shredders')} têm ciclo de larvas e casulos documentado separadamente. {cite('T25','T25 01:35:35')} {cite('H','Handoff, síntese — Povos antigos e Mind Shredders')}
""", [], [2])

nota('Criaturas/Vasuthant', 'Vasuthant', 'criatura', ['glim'], ['G'], f"""
## Natureza e origem relatadas

Criatura vista como nuvem negra voadora com tentáculos, escapada de um experimento de Arkhavel. Segundo a explicação dele registrada por Glim, vem do plano da energia negativa, alimenta-se de pequenas criaturas e pode crescer até tornar-se ameaça séria. A origem planar e a previsão de crescimento são relato de Arkhavel, não viagem dos personagens ao habitat de origem. {cite('G','Diário de Glim — S4')}

## Comportamento observado

A investigação segue uma região sem animais pequenos e encontra o Vasuthant num tronco a cerca de seis metros de altura. A ilusão de Glim não o atrai; ele foge dos ataques e retorna ao local no dia seguinte, como Hanta previra. A falha daquela isca não demonstra imunidade universal a ilusões. {cite('G','Diário de Glim — S7')}

## Caça e desfecho local

O grupo usa pássaros presos e outros animais vivos feridos como iscas. O Vasuthant se alimenta dos pássaros e desce para os animais no chão, onde Crave o atinge. A nuvem negra se desfaz e resta um tentáculo semelhante a uma lombriga grande, levado à guarda como prova; o diário registra retorno depois de quase quinze dias de expedição. Esse indivíduo foi abatido, sem que a cena defina a ecologia de toda a espécie. {cite('G','Diário de Glim — S8')}
""", [], [])

nota('Criaturas/Magia viva do sono', 'Magia viva do sono', 'criatura', ['glim'], ['G'], f"""
## Origem e caso de Carlos

Magia que ganhou vida num experimento de {link('Personagens/Arkhavel')}, segundo sua confirmação registrada no diário. Os relatos concentram-se na família de {link('Personagens/Carlos carpinteiro')}, cuja casa fica diante da torre: dormiam, mas não descansavam. Houve queixas de vizinhos que cessaram depois de uma ausência; o grupo investiga a concentração posterior sobre a família. {cite('G','Diário de Glim — S4')}

## Aparência e capacidades observadas

Na vigília da sessão 10, o grupo vê uma gosma translúcida e esbranquiçada cobrindo a cama dos pais, ainda adormecidos. Ela foge, esconde-se sob a cama, estica-se para tocar Crave e o faz dormir; um tapa o desperta. Depois atravessa frestas de madeira e tenta alcançar o fosso do banheiro externo. Esses são efeitos observados nesse encontro, sem regra externa de alcance ou duração. {cite('G','Diário de Glim — S10')}

## Segundo exemplar e estado

Crave destrói a criatura maior. A busca encontra um exemplar pequeno semelhante, descrito como filhote; Glim o guarda num recipiente e o leva a Arkhavel. Okay e Arkhavel dizem que a reprodução não deveria ocorrer; Arkhavel se entusiasma por ter criado uma “raça”, e o diário atribui inteligência incomum aos dois exemplares. A reação dele não explica o mecanismo de origem do pequeno nem confirma uma espécie estável. Não há destino posterior registrado na passagem consultada. {cite('G','Diário de Glim — S10')}
""", [], [23])

nota('Criaturas/Fada Orfa', 'Fada Órfã', 'criatura', ['glim'], ['G'], f"""
## Identificação e vítimas

No caso das sete crianças desaparecidas de Eral, Okay identifica como hipótese confiável uma fada que vive nos subúrbios e transforma os corpos das vítimas mortas em arbustos. O mapa registra os arbustos nas áreas periféricas e permite escolher possíveis esconderijos. “Fada Órfã” é a identificação usada no relato, sem nome pessoal recuperado para o indivíduo. {cite('G','Diário de Glim — S4–S5')}

## Encontro observado

Arkhavel adverte sobre sua capacidade extraordinária de esconder-se. As tentativas de Glim de atingi-la com Leque Cromático e a magia de gelo de Okay não a expõem de modo suficiente; o grupo segue seus passos por ruínas de uma casa. Ela fere pescoço e peito de Glim com garras, deixando-o quase morto. A cena mostra furtividade extrema e garras, sem demonstrar uma regra universal de invisibilidade ou imunidades. {cite('G','Diário de Glim — S5')}

## Desfecho e limite

Crave mata a fada, Okay cura Glim, e o grupo encontra moedas no esconderijo. O cadáver é entregue à guarda e a morte das crianças é comunicada, com os arbustos tratados como seus restos transformados. O caso encerra a ameaça desse indivíduo no relato; não há pesquisa adicional sobre reprodução, sociedade feérica ou outros exemplares. {cite('G','Diário de Glim — S5')}
""", ['Fada Orfã'], [])

nota('Criaturas/Goblins de Dekanter', 'Goblins de Dekanter', 'criatura', ['glim'], ['T21','H'], f"""
## Espécie explicada na mesa

Goblinoides robustos de pele vermelha alaranjada, espessa, com juba negra, garras e chifre semelhante ao de rinoceronte. A explicação do mestre lhes dá cerca de 1,20 a 1,50 metro de altura, grande largura de ombros e idiomas subterrâneo e goblin. Essa descrição é o conhecimento concedido no encontro, sem importar história externa sobre sua criação. {cite('T21','T21 01:03:01')}

## Capacidades de combate

O mestre explica resistência ao frio, cura acelerada de três pontos por rodada enquanto tiverem ao menos um ponto de vida e incapacidade de regenerar partes perdidas. Destacam-se em investidas com chifre e encontrões; ele interpreta que os fossos laterais favoreciam empurrar adversários. A menção genérica a obedecer ao criador na explicação não nomeia um criador desses indivíduos. {cite('T21','T21 01:03:01')}

## Grupo encontrado e fuga

No combate ao chefe goblin que invertia resultados, os goblins fogem quando ele se desfaz após ser morto por cura. Três fugitivos são abatidos e dois escapam na sequência narrada. Esse vínculo local não transforma a espécie inteira numa facção com a agenda do chefe, nem prova que todos os moradores e escravizadores da aldeia eram de Dekanter. {cite('T21','T21 01:05:56; 01:24:33')}

O assentamento continha humanos escravizados e crianças presas com ferros e pesos danosos. A síntese registra depois massacre de mulheres, crianças e intérprete jovem, além de reféns humanos mortos. Esses fatos exigem distinguir combatentes, escravizadores e indefesos; a identificação de espécie não substitui essa distinção. {cite('T21','T21 01:40:37')} {cite('H','Handoff, síntese — consequências nas cavernas')}
""", [], [])

nota('Criaturas/Crepusculos Venenosos', 'Crepúsculos Venenosos', 'criatura', ['glim'], ['G'], f"""
## Identificação por relato

Reptilianos que Okay identifica pela descrição de Folha-Seca como pertencentes à raça chamada Crepúsculo Venenoso, especializada em venenos e conhecida por envenenar comunidades inimigas. O trecho não mostra encontro direto com exemplares; a especialização é conhecimento relatado por Okay. {cite('G','Diário de Glim — S5')}

## Tribo próxima de Eral e suspeita

Folha-Seca aponta uma tribo na região de possível acesso subterrâneo ao lençol d’água de Eral e relata guerra da cidade com ela aproximadamente um ano antes. O envenenamento recorria havia cerca de dois anos, em intervalos aproximados de mês e meio. A amostra analisada por Glim lhe parecia fabricada, levando-o à suspeita de ação intencional. São relatos e interpretação da investigação, não autoria demonstrada. {cite('G','Diário de Glim — S4–S5')}

Glim vê a tribo como culpada óbvia, mas Folha-Seca contesta a escala de veneno necessária. Não se confirmou responsabilidade, comando tribal, aliados, situação posterior ou capacidades de exemplares individuais. O sumiço do ranger numa área corrosiva é outra pista; a fonte não demonstra que fosse obra dos mesmos reptilianos. {cite('G','Diário de Glim — S5')}
""", ['Crepúsculo Venenoso'], [24])

nota('Criaturas/Inevitaveis', 'Inevitáveis na descrição da mesa', 'criatura', ['glim'], ['T20'], f"""
## Explicação recebida

Na chegada à loja Laoum, em Mercadia, o mestre explica inevitáveis como constructos feitos por uma raça para perseguir violações específicas. Descreve três tipos, mas só exemplifica dois alvos: quem burla a morte, incluindo liches, mortos-vivos ou quem obtém perpetuidade por magia; e assassinos. O terceiro alvo não é lembrado na fala. Essa é a cosmologia explicada nesta mesa, com suas lacunas preservadas. {cite('T20','T20 00:28:51–00:29:12')}

## Guardião comparado

O golem diante de Laoum lembra a forma dos inevitáveis, grandes e muito fortes, porém o mestre afirma que o guardião é ainda mais poderoso, de escala épica. A comparação não o identifica categoricamente como um inevitável de tipo conhecido nem como membro de organização nomeada. Não há combate para medir suas capacidades nessa passagem. {cite('T20','T20 00:28:51–00:29:12')}

## Limite da entrada

O encontro registra um guardião de loja e uma explicação de conhecimento dos personagens; não identifica a raça construtora, comando, base, agenda de cada indivíduo ou perseguição ativa aos Magníficos. A associação com Laoum não estabelece aliança dos inevitáveis como conjunto com o comerciante. {cite('T20','T20 00:28:51–00:33:08')}
""", [], [])


def executar():
    ids = {int(p['id'].split('-')[1]): p for p in PERGUNTAS}
    for p in PERGUNTAS:
        fontes = [SRC[x] for x in p['fontes']]
        campanhas = ['fash','glim'] if any(x in p['fontes'] for x in ['F','J']) else ['glim']
        p['destino'] = pendencia(p['id'],p['titulo'],'Faccoes',campanhas,p['pergunta'],p['contexto'],
                                fontes,p['entidades'],p['prioridade'],p['natureza'])
    for n in NOTAS:
        texto = n['texto'].strip()
        # Toda fonte citada deve constar também de origens; referências cruzadas
        # entre entidades não entram nessa relação de evidências.
        citadas = re.findall(r'\[\[(Fontes/[^\]|#]+)', texto)
        for codigo, caminho_fonte in SRC.items():
            if caminho_fonte in citadas and codigo not in n['fontes']:
                n['fontes'].append(codigo)
        if n['perguntas']:
            texto += '\n\n## Pendências relacionadas\n\n' + '\n'.join(
                '- ' + link(ids[x]['destino'],ids[x]['id'] + ' — ' + ids[x]['titulo']) for x in n['perguntas'])
        n['arquivo'] = escrever(n['destino'],n['titulo'],n['tipo'],n['campanhas'],texto,
                                [SRC[x] for x in n['fontes']],n['aliases'])
    cadastro = json.loads((ROOT/'docs/enciclopedia/registro-entidades.json').read_text(encoding='utf-8'))
    esperados = [x for x in cadastro['entidades'] if x['dominio'] in ['faccoes','criaturas']]
    cobertura = []
    for e in esperados:
        n = next(n for n in NOTAS if n['destino']==e['destino'])
        cobertura.append(dict(**e,arquivo=n['arquivo'],fontes=[SRC[x] for x in n['fontes']],
                              pendencias=[ids[x]['id'] for x in n['perguntas']]))
    escritos = [CONTEUDO/n['arquivo'] for n in NOTAS] + [CONTEUDO/(p['destino']+'.md') for p in PERGUNTAS]
    fontes_inexistentes = []
    destinos_cadastro = {x['destino'] for x in cadastro['entidades']}
    links_outros_dominios_pendentes = set()
    links_fora_cadastro = []
    paragrafos_sem_citacao = []
    for caminho in escritos:
        conteudo_nota = caminho.read_text(encoding='utf-8')
        frontmatter,corpo = conteudo_nota.split('---',2)[1:]
        meta = {k:json.loads(v) for k,v in (linha.split(':',1) for linha in frontmatter.strip().splitlines())}
        assert meta['atualizado']=='2026-10-29'
        assert meta['status'] in ['aberta','documentado_parcial']
        for alvo in re.findall(r'\[\[([^\]|#]+)',conteudo_nota):
            if alvo.startswith('Fontes/') and not (CONTEUDO/(alvo+'.md')).exists():
                fontes_inexistentes.append(dict(nota=str(caminho),alvo=alvo))
            elif not (CONTEUDO/(alvo+'.md')).exists():
                if alvo in destinos_cadastro:
                    links_outros_dominios_pendentes.add(alvo)
                else:
                    links_fora_cadastro.append(dict(nota=str(caminho),alvo=alvo))
        if meta['tipo']!='pendencia':
            for paragrafo in re.split(r'\n\s*\n',corpo):
                if paragrafo.strip() and not paragrafo.lstrip().startswith(('#','- ')) and '[[Fontes/' not in paragrafo:
                    paragrafos_sem_citacao.append(caminho.relative_to(CONTEUDO).as_posix())
    snapshot=json.loads((ROOT/'docs/enciclopedia/estado-fontes.json').read_text(encoding='utf-8'))
    mudancas=[]
    for e in snapshot['arquivos']:
        caminho=ROOT/e['path']
        if not caminho.exists() or hashlib.sha256(caminho.read_bytes()).hexdigest()!=e['sha256']:
            mudancas.append(e['path'])
    assert len(cobertura)==28
    assert len([n for n in NOTAS if n['destino'].startswith('Faccoes/')])==20
    assert len([n for n in NOTAS if n['destino'].startswith('Criaturas/')])==8
    assert not fontes_inexistentes, fontes_inexistentes
    assert not links_fora_cadastro, links_fora_cadastro
    assert not paragrafos_sem_citacao, paragrafos_sem_citacao
    assert not mudancas, mudancas
    manifesto=dict(
        dominio='faccoes_e_criaturas', atualizado='2026-10-29', estado='congelado_para_integracao',
        resumo={'faccoes':20,'criaturas':8,'notas':28,'pendencias':len(PERGUNTAS),'extras':0},
        cobertura=cobertura,
        notas=[dict(destino=n['destino'],arquivo=n['arquivo'],titulo=n['titulo'],tipo=n['tipo'],
                    campanhas=n['campanhas'],aliases=n['aliases']) for n in NOTAS],
        perguntas=[{k:v for k,v in p.items() if k not in ['contexto']} for p in PERGUNTAS],
        fontes_efetivamente_consultadas=[
            {'fonte':SRC['H'],'alcance':'Seções de correções, cronologia, campanha antiga, facções e quadro, pessoas, lugares, planos, ameaças, criaturas e instituições do sonho; síntese secundária identificada como tal nas notas.'},
            {'fonte':SRC['J'],'alcance':'Leitura integral do conteúdo dos esclarecimentos de 23/10/2026.'},
            {'fonte':SRC['F'],'alcance':'Trechos Dia 45/solo dos 45 dias, 22/01–25/01, 08/02, 07/11, 28/11–02/12, 25/10 e menções a guildas/Timo em Lazathar. Pesquisa textual e leitura de excertos, não releitura integral do diário.'},
            {'fonte':SRC['B'],'alcance':'Ato 2 de Brakka e trechos do ato 3 sobre dispersão nos Dias Rubros; ato 4 de Varo e excertos dos atos 5–6 com morte de Tom, trabalho avulso, investigação do Ébano e interpretação de afinidade das sombras. Não releitura integral do background.'},
            {'fonte':SRC['G'],'alcance':'Leitura de S4–S5, S7–S8 e S9–S10; começo S6 e menções pesquisadas sobre criaturas. Não releitura integral das 26 sessões.'},
            {'fonte':SRC['T13'],'alcance':'00:54:32–00:59:24 e 01:11:44–01:14:48: lista, arena, Kenku, comunidade e tática de Tork.'},
            {'fonte':SRC['T14'],'alcance':'00:10:10, 00:29:54, 01:35:56–01:36:40 e 01:41:18–01:49:02: Kenku, tamanho do Conclave e negociação.'},
            {'fonte':SRC['T16'],'alcance':'Excertos de 00:16 e leitura concentrada de 00:51:56–01:25:49: cartas, pagamentos, Conclave, Kenku e rivais. Não transcrição integral.'},
            {'fonte':SRC['T17'],'alcance':'00:22:03; 00:47:07–01:01:08 e 02:00:15–02:02:03: experiência planar, máscaras, leilão e validação da vivência.'},
            {'fonte':SRC['T18'],'alcance':'01:06:50–01:16:04: retorno, depoimento, guarda, clérigos, Kenku e mensagem.'},
            {'fonte':SRC['T19'],'alcance':'00:56:07–01:09:18: identificação e capacidades de Mind Shredders. Desfecho dos três no posto via Handoff.'},
            {'fonte':SRC['T20'],'alcance':'00:00:00–00:08:22; 00:28:51–00:33:08: posto, reprodução, alimentação e inevitáveis. Menções e excertos posteriores da loja sem uso de lore externo.'},
            {'fonte':SRC['T21'],'alcance':'01:03:01, 01:05:56, 01:24:33 e 01:40:37: Dekanter, fuga e escravidão. Consequências posteriores via Handoff.'},
            {'fonte':SRC['T24'],'alcance':'01:20:08–01:21:53; 01:57:35–01:58:34; 02:08:41–02:23:31: Lua Sangrenta, Tahen, organização e expedições.'},
            {'fonte':SRC['T25'],'alcance':'00:01:41–00:04:18; 01:10:24–01:15:05; 01:35:18–01:45:56; 01:49:34–01:55:22 e menções correlatas: Zodíacos, corpos, Firael, Cérebro e aliança. Demais fatos atribuídos explicitamente ao Handoff.'},
        ],
        limites=[
            'Não foram consultadas fontes externas de D&D nem completada taxonomia de criaturas por lore de publicação.',
            'As leituras de transcrições foram de excertos direcionados; uma citação ao Handoff permanece citação de síntese, ainda que esta informe timestamps de primárias.',
            'O background foi consultado diretamente em trechos dos atos 2–6; as perspectivas de Brakka, Varo, Tom e Glim conservam suas limitações.',
            'Índices e cadastro comum não foram alterados; destinos de outros domínios serão conferidos pelo integrador.',
            'Perguntas institucionais não pretendem resolver as pendências individuais de Fash, Timo, rangers ou demais personagens.',
            'Conhecimento público da base não significa que todos os personagens conheçam informações de bastidores.',
        ],
        verificacoes={'cobertura_cadastro':len(cobertura),'arquivos_gerados':len(escritos),
                      'citacoes_fontes_inexistentes':fontes_inexistentes,
                      'links_fora_cadastro':links_fora_cadastro,
                      'links_outros_dominios_pendentes':sorted(links_outros_dominios_pendentes),
                      'paragrafos_factuais_sem_citacao':paragrafos_sem_citacao,
                      'metadados_json_yaml_compativeis':True,
                      'fontes_modificadas_desde_snapshot':mudancas,
                      'fontes_no_snapshot_verificadas':len(snapshot['arquivos']),
                      'status_notas':'documentado_parcial','status_pendencias':'aberta',
                      'indices_alterados':False,'extras_propostos':[]})
    (ROOT/'docs/enciclopedia/faccoes.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifesto['resumo'],ensure_ascii=False))
    print(json.dumps(manifesto['verificacoes'],ensure_ascii=False))


if __name__=='__main__':
    executar()
