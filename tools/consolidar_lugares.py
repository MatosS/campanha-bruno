"""Consolidação documentada de lugares; não escreve nas fontes nem nos índices."""
from pathlib import Path
import json
import re
from enciclopedia_comum import escrever, pendencia, fonte, link, ROOT, FONTES

XI = 'Fontes/Planilhas/Fash Paleskin - INTERESSES'
XA = 'Fontes/Planilhas/Fash Paleskin - ADMINISTRAÇÃO CIDADE DROW'
FA = 'Fontes/Vault/Vault - Fash Paleskin'

def T(n):
    datas = {13:'2026-05-27',14:'2026-06-17',17:'2026-08-17',19:'2026-09-01',20:'2026-09-02',23:'2026-09-27',24:'2026-09-30',25:'2026-10-05',26:'2026-10-20'}
    return f'Fontes/Transcricoes/Glim - Sessao {n:02} - {datas[n]}'

def f(c, label): return fonte(c, label)
def l(p, label=None): return link(p, label)

def referencias_oniricas():
    """Três referências de busca; validade material permanece aberta."""
    pc = l('Pendencias/Personagens/PC-002 - Continuidade de Tinkar e passado de Fash')
    return [
        dict(slug='Eldrosia',titulo='Eldrosia',texto=f'''## Referência do background

O background inicial de Fash diz que Tinkar Daergel nasceu num bairro modesto da **capital de Eldrosia**. Seus pais negociavam minerais e metais de {l('Lugares/Thal Karak')}. A formulação apresenta uma referência política ligada à capital, sem definir de maneira segura se Eldrosia nomeia reino, região ou outra unidade do cenário material. {f('F','Fash — BACKGROUND')}

## Continuidade e limites

A nota de Fash no vault resume que Tinkar nasceu em Eldrosia, mas está expressamente marcada **revisar_continuidade**. O handoff conserva Eldrosia entre referências do background/sonho, e o jogador não soube informar nomes oficiais do mundo, reino ou continentes. Portanto esta nota não adota Eldrosia como nome do mundo nem como reino material confirmado. {f(FA,'Vault — Fash Paleskin, em revisão de continuidade')}; {f('H','Handoff — Instituições e pessoas do sonho')}; {f('J','Esclarecimentos — Sonho e geografia')}

Não há fronteiras, população, coordenadas ou rotas materiais verificadas para Eldrosia. A capital real confirmada é {l('Lugares/Carruan')}; a cidade aparente de {l('Lugares/Lazathar')} pertence à experiência onírica. A reconciliação com a cidade natal narrada de {l('Lugares/Teladelion')} continua aberta. {f('F','Fash — 25/10')}; {f('J','Esclarecimentos — errata da capital')}

## Pendências existentes

{P[14]} · {pc}''',fontes=['F',FA,'H','J']),
        dict(slug='Thal Karak',titulo='Montanhas de Thal Karak',texto=f'''## Referência do background

Montanhas citadas no background inicial de Tinkar Daergel: Mendrik e Felbira negociavam minerais e metais vindos de **Thal Karak**. Essa é a função geográfica e econômica recuperável do nome. A fonte não identifica cidades, minas específicas, povos residentes, caminho comercial ou distância até a capital de {l('Lugares/Eldrosia')}. {f('F','Fash — BACKGROUND')}

## Continuidade e estado

A nota histórica de Fash no vault repete a relação comercial, porém exige revisão de continuidade. O handoff conserva Thal Karak entre as referências do background/sonho, cuja validade material não foi estabelecida individualmente pelo jogador. Não identificar essas montanhas com os covis de Hourian, a região nevada da prova de Kord ou a montanha das memórias sem evidência adicional. {f(FA,'Vault — Fash Paleskin, em revisão de continuidade')}; {f('H','Handoff — Instituições e pessoas do sonho')}; {f('J','Esclarecimentos — Sonho e geografia')}

Não há localização cartográfica ou atualização contemporânea de Glim. O comércio é parte da biografia inicial narrada de Fash, não prova de uma rota material ainda em operação. {f('F','Fash — BACKGROUND')}

## Pendências existentes

{P[14]} · {pc}''',fontes=['F',FA,'H','J']),
        dict(slug='Teladelion',titulo='Teladelion',texto=f'''## Cidade narrada no sonho

Na entrada de **11/09**, datada internamente em 18/7/536, Fash consulta um mapa mágico interativo numa grande taverna de {l('Lugares/Lazathar')}. Chama de **Teladelion (KHARTELADELIONRINZITH)** a cidade em que sempre viveu. A variante **Kharteladelionrinzith** é preservada como forma apresentada entre parênteses nessa fonte; não prova nome oficial ou identidade de uma cidade material fora do sonho. {f('F','Fash — 11/09')}

## Rota e ocupação relatadas

O mapa indica cerca de **um mês e meio de viagem a pé da capital**, dentro desse contexto onírico. Fash percebe aparente redução da cidade. Roger, o anão da taverna, relata embate contra uma guilda crescente e retomada do crescimento depois da chegada do Circo. Depois, um informante do Circo atribui a eliminação da guilda ao rompimento com o Mercado Negro e diz que a nova facção dominante responde a ele. São informações recebidas de interlocutores no sonho, não fatos políticos materiais verificados. {f('F','Fash — 11/09, mapa e notícias do Circo')}

## Continuidade e estado

O handoff a chama de cidade natal narrada de Fash, com situação material posterior não verificada. A revelação de 25/10 e a confirmação do jogador mantêm o trecho inicial como sonho. A relação entre a origem de Tinkar na capital de {l('Lugares/Eldrosia')} e sua afirmação de ter vivido em Teladelion permanece uma questão de continuidade, sem fusão automática das cidades. {f('H','Handoff — Instituições e pessoas do sonho')}; {f('F','Fash — 25/10 e BACKGROUND')}; {f('J','Esclarecimentos — Sonho e geografia')}

Não há coordenadas, censo ou estado material atual confirmado. A distância onírica não deve ser usada para traçar rota desde Carruan. {f('H','Handoff — O sonho da campanha de Fash')}

## Pendências existentes

{P[14]} · {pc}''',fontes=['F','H','J']),
    ]

notas = []
perguntas = []
def nota(slug, titulo, campanhas, texto, fontes, aliases=None, extra=False, **meta):
    path = escrever('Lugares/'+slug,titulo,'lugar',campanhas,texto,fontes,aliases,**meta)
    notas.append(dict(nome=titulo,caminho=path,fontes=[FONTES.get(x,x) for x in fontes],extra=extra))

def p(n,titulo,pergunta,contexto,fontes,entidades,prioridade='media',natureza='lacuna',campanhas=None):
    dest = pendencia(f'LG-{n:03}',titulo,'Lugares',campanhas or ['fash','glim'],pergunta,contexto,fontes,entidades,prioridade,natureza)
    perguntas.append(dict(id=f'LG-{n:03}',caminho=dest+'.md',prioridade=prioridade,fontes=[FONTES.get(x,x) for x in fontes],entidades=entidades))
    return l(dest)

P={}
P[1]=p(1,'Nomes oficiais e lei de Carruan','Quais são os nomes oficiais do mundo, dos continentes e dos domínios humanos, e a proibição de elfos registrada em Carruan ainda vigora?','Carruan substitui Lazathar após a revelação do sonho e a errata de 23/10. O jogador não conhece os nomes oficiais de mundo, reino e continente. A lei contra elfos só está documentada na campanha antiga. Eldrosia e Auria não bastam para nomear o cenário.', ['F','J','H'],['Lugares/Carruan','Lugares/Lazathar'], 'alta')
P[2]=p(2,'Ocupação de Eral e destino dos refugiados','Que bairros de Eral voltaram a ser ocupados e para onde foram os cerca de sete mil refugiados após o ataque? Há contagem posterior de moradores ou mortos?','A correção do mestre em S19 fixa aproximadamente 10 mil antes, 2 mil mortos, mil presentes e 7 mil em marcha. As mortes previstas na viagem não foram contabilizadas. A reconstrução por bairro foi observada, mas não há censo posterior.', [T(19),'H'],['Lugares/Eral','Lugares/Torre de Arkhavel','Lugares/Casa de Carlos','Lugares/Igreja de Kord em Eral'], 'alta',campanhas=['glim'])
P[3]=p(3,'Assentamentos goblinoides e rotas de Eral','A aldeia ligada à arena, o acampamento próximo e as cavernas de reféns são o mesmo complexo? Como se relacionam as referências a quatro dias e a um ou dois dias de viagem?','A síntese registra distâncias divergentes e admite locais diferentes. As campanhas contra o assentamento e as cavernas não autorizam fundir todos os pontos goblinoides num único endereço.', ['H','G'],['Lugares/Assentamento goblinoide','Lugares/Eral','Eventos/Crise dos refens'], 'alta',natureza='divergencia',campanhas=['glim'])
P[4]=p(4,'Ocupantes de P22 Q23 e U27','Quem ocupa hoje P22, Throden Q23 e a vila U27? Que população humana e anã permaneceu no subterrâneo após a fuga de Fash e Kael?','O diário registra humanos reassentados, anões libertos e meio-dragões assumindo o Forte. A administração da planilha lista 15 anões e 80 humanos; a estimativa inicial do Forte era 2 mil. São registros de contextos diferentes, sem censo reconciliado. Os mapas atuais descrevem dragão e trolls na antiga cidade drow.', ['F',XI,XA,'G',T(25)],['Lugares/Cidade drow','Lugares/Throden','Lugares/Vila dos meio-dragoes'], 'alta')
P[5]=p(5,'Cartografia e destinos antigos da cidade drow','Qual é o significado e a época dos dois rótulos riscados da planilha, como os três nomes sem rasura correspondem aos três portais do diário e como se resolvem W23 e K28/L28?','Diário 29/01: três portais — Abismo, associação com família e destino incerto. O XLSX original de INTERESSES contém cinco rótulos, dos quais três estão sem rasura (C48 Abismo, C49 Mundo Espelhado, C50 Ilha dos Elfos da Noite) e dois riscados (C51 Cabeça de Gigante, C52 4 Costelas Grandes; font.strike=true, confirmado diretamente nos estilos OOXML). A conversão Markdown inicial não mostrava o risco; isso não constitui contradição automática de cinco contra três. A rasura tampouco prova eliminação física de portais. Continuam abertas sua data, significado e correspondência com o diário. C79 diz Floresta do Timo W23, legenda diz Ruína 2 W23; C34 diz Furion K28, legenda indica Loraeth L28. Pergunta cartográfica; mecanismos das portas de Arkhavel pertencem ao domínio Itens.', ['F',XI],['Lugares/Cidade drow','Lugares/Floresta de Timo','Lugares/Loraeth','Lugares/Ruinas do mapa de Fash'], 'alta',natureza='divergencia',campanhas=['fash'])
P[6]=p(6,'Localização e guarda atual do nodo','O nodo sob os ossos nos mapas atuais é exatamente o fosso escavado por Fash? Quem ocupa ou guarda hoje a passagem e qual é sua relação geográfica com o nodo das bruxas?','O fosso antigo ficava na parte da caverna anterior a P22; Lídia perdeu vínculo junto de uma passagem. S25 descreve nodo funcional sob ossos e rocha, protegido por criatura e desconhecido do dragão. Isso não demonstra identidade com o nodo descrito no livro das bruxas nem explica a causa da perda de vínculo.', ['F',T(25),'H'],['Lugares/Fosso de ossos e nodo','Lugares/Cabana das bruxas','Lugares/Cidade drow'], 'alta')
P[7]=p(7,'Necrópole e área de mortos-vivos','A necrópole H20 e a cordilheira dos mortos-vivos imóveis são locais diferentes? Qual é a ocupação atual de cada uma?','O Necromante aponta necrópole junto ao rio e abaixo dos Equiceps. O relato atual de arquivista descreve 100–200 esqueletos e zumbis parados numa cordilheira enegrecida. A tomada da necrópole pelo Cavaleiro da Morte é hipótese condicional do jogador; a ligação da cordilheira ao Cavaleiro é suspeita do informante.', ['F',XI,'J',T(25)],['Lugares/Necropole','Lugares/Area dos mortos-vivos imoveis','Personagens/Cavaleiro da Morte'], 'alta')
P[8]=p(8,'Covis de Hourian Haurim','Quais são os nomes, a localização e a ocupação atual dos covis chamados de Hourian ou Haurim? Como identificar as duas montanhas ao sul registradas na planilha?','O diário considera a viagem longa demais para voltar antes dos trolls. A planilha só diz duas montanhas ao sul. Firael relata a morte de Hourian numa revoada, sem coordenadas ou equivalência com a Revoada Branca.', ['F',XI,'H'],['Lugares/Covis de Hourian Haurim','Personagens/Hourian Haurim'], 'media',campanhas=['fash'])
P[9]=p(9,'Região gelada e aldeia após os yetis','Qual é o nome da cidade de gelo e da região mostrada no mapa? Quem ocupa a aldeia da prova de Kord depois da fuga e da tarefa final de Tariun?','S23 confirma que a região está no plano natal e diferencia a cidade distante da aldeia ocupada. Houve ataque de yetis, resgate parcial e saída do sacerdote vivo; S25 não registra o resultado da tarefa de Tariun. Não há total final de sobreviventes nem nome geográfico seguro.', [T(23),'H','G'],['Lugares/Regiao gelada','Lugares/Aldeia ocupada na neve','Personagens/Tariun'], 'media',campanhas=['glim'])
P[10]=p(10,'Floresta de Timo e santuário atual','A floresta antiga de Timo, as ruínas W23, os santuários onde ele brotou e o santuário da portadora do cajado ocupam o mesmo lugar ou regiões distintas?','A identidade Timo/planta/cajado foi confirmada. S25 reconhece a região onde ele brotou e santuários em volta, mas isso não fornece coordenada ou equivalência com a floresta de infância/território antigo de Timo. W23 é descrito de duas maneiras na própria planilha.', ['F',XI,'G',T(25),'J'],['Lugares/Floresta de Timo','Lugares/Santuario da driade','Lugares/Ruinas do mapa de Fash'], 'media')
P[11]=p(11,'Rota marítima dos arquivistas','Qual é o nome do litoral, ilha ou continente do covil das expedições e qual rota segura chega à abertura sob o penhasco? Há informação posterior sobre a ocupação do local?','Tahen mostra um atlas e descreve travessia pela água a partir da região élfica, mas o TXT não conserva o apontamento visual. A primeira e a segunda expedições, inclusive barcos, desapareceram. O dragão desse covil não foi identificado como o dragão negro de P22.', [T(24),'H'],['Lugares/Covil maritimo','Faccoes/Arquivistas','Personagens/Elrohir'], 'alta',campanhas=['glim'])
P[12]=p(12,'Nome e rota da montanha das memórias','Qual é a montanha da mulher das memórias, e que estrada ou paradas ligam Carruan a ela? Um mês a cavalo continua sendo a estimativa adequada?','S25 estabelece a capital como acesso de porta mais próximo e um mês aproximado de viagem a cavalo. Há estrada perto segundo o diário. A viagem ainda não ocorreu no corte de S26; não confundir essa montanha com a aldeia nevada da prova de Kord.', [T(25),'G','J'],['Lugares/Montanha das memorias','Lugares/Carruan','Personagens/Mulher das memorias'], 'media',campanhas=['glim'])
P[13]=p(13,'Nome e localização da aldeia de Glim','Qual é o nome e a localização da aldeia natal de Glim, e qual é a condição mais recente de sua ocupação e de sua antiga casa?','O background canônico a situa no limite da mata e descreve retorno antes da campanha, com casas reconstruídas e a residência familiar abandonada por dentro. Não fornece coordenadas ou distância até Carruan.', ['B','J'],['Lugares/Aldeia natal de Glim','Personagens/Glim Sombrasselva'], 'media',campanhas=['glim'])
P[14]=p(14,'Referentes materiais dos lugares do sonho','Quais lugares do sonho antigo possuem correspondentes materiais, especialmente Teladelion, Thal Karak e as instituições urbanas de Lazathar?','O jogador autorizou preservar o trecho como sonho e não conhece o propósito do mestre. O sonho fornece cidades, distâncias e instituições que não podem ser transferidas automaticamente para o mundo material.', ['F','H','J'],['Lugares/Lazathar','Lugares/Plano dos sonhos','Lugares/Cabana das bruxas'], 'media',campanhas=['fash'])
P[15]=p(15,'Mercadia acessos e regras locais','Em que plano ou domínio fica Mercadia, qual é o endereço de sua casa de Arkhavel e qual o alcance da proibição de magia na cidade?','S20 descreve ilha envolta por cristal e Laoum a três quadras da saída utilizada. A proibição de usar magia é citada em S23, mas exceções, autoridades e sanções não foram estabelecidas. A pergunta trata de localização e normas, não do mecanismo das portas.', [T(20),'H'],['Lugares/Mercadia','Lugares/Laoum','Lugares/Torre de Arkhavel'], 'baixa',campanhas=['glim'])
P[16]=p(16,'Localização da comunidade de Eral','Onde fica a comunidade da floresta em relação a Eral e qual sua ocupação após o ataque? Há ligação geográfica comprovada com o Conclave da Raiz Ancestral T23?','A comunidade de rangers próxima de Eral tem leis próprias e cerca de 50–60 integrantes segundo síntese. O mapa antigo nomeia outro Conclave em T23. Sem confirmação não unir comunidades ou organizações por função ou nome semelhante.', ['H',T(13),XI],['Lugares/Comunidade da floresta','Lugares/Conclave da Raiz Ancestral'], 'media')

nota('Carruan','Carruan',['fash','glim'],f'''## Identidade e época

Capital humana real. A entrada de Fash de 25/10, situada internamente em 23/7/530, corrige a experiência anterior: Carruan é uma cidade bárbara de rocha bruta e estética rústica; os bairros lhe parecem semelhantes, sem a divisão entre área nobre e favela vista no sonho. São observações do diário antigo, não descrição atualizada da capital. {f('F','Fash — 25/10')}

O jogador confirmou em 23/10/2026 que chamar a capital de {l('Lugares/Lazathar')} no diário de Glim foi erro de registro. A capital visitada por Glim ao buscar trabalho deve ser lida como Carruan. Eldrosia, do background antigo, e Auria não foram confirmados como nomes oficiais de mundo ou reino. {f('J','Esclarecimentos — Sonho e geografia')}

## Ocupação e circulação

Fash anota uma lei que proibia elfos de entrar na região da cidade; sua vigência na campanha atual está aberta. Glim chega à capital procurando trabalho e segue para {l('Lugares/Eral')} numa caravana organizada pelo {l('Personagens/Teodoron Talent','duque Teodoron Talent')}, com mais de duzentos soldados. O diário diz que Eral não fica muito longe e registra notícia de estradas mais perigosas ao norte, mas não fornece distância absoluta ou coordenada. {f('F','Fash — 25/10')}; {f('G','Glim — S1, aplicando a errata J')}

## Estado mais recente e acesso planejado

Na S25, a capital é o ponto de chegada por porta mais próximo da {l('Lugares/Montanha das memorias')}; dali o mestre estima cerca de um mês a cavalo. Isso descreve uma rota planejada, ainda não realizada ao fim de S26. {f(T(25),'T25 — 01:57:28–01:58:39')}

## Lacunas

{P[1]} · {P[12]}''',['F','J','G',T(25)],aliases=['Capital real'])

nota('Lazathar','Lazathar',['fash','glim'],f'''## Natureza do registro

Capital aparente da experiência onírica de {l('Personagens/Fash Paleskin')}. Em 23/08 o grupo acredita ter escapado por um portal e chega à cidade. Fash recebe datas e intervalos de desaparecimento contraditórios; em 17/10 e 25/10 descobre que nunca saíra do cativeiro. O jogador confirmou que a cronologia e os lugares desse trecho podem ser tratados como sonho. {f('F','Fash — 23/08, 17/10 e 25/10')}; {f('J','Esclarecimentos — Sonho e geografia')}

## Cidade vivida no sonho

A cidade apresenta infraestrutura grandiosa e divisão urbana que contrasta, no relato posterior de Fash, com {l('Lugares/Carruan')}. Circo, Taverna, Quartel, Coliseu, Conclave e Torre dos Magos oferecem contatos, trabalhos e transporte. A investigação passa por corpos com runas, igreja, guarda, favela e uma câmara ritual. Esta organização de lugares e instituições é recuperada aqui como **síntese do handoff**, não como história material confirmada. {f('H','Handoff — O sonho da campanha de Fash')}

As notícias sobre Teladelion/Kharteladelionrinzith, sua distância de um mês e meio, refugiados bárbaros e política élfica pertencem a esse contexto. Não transportar suas rotas, população ou instituições para Carruan sem validação. {f('H','Handoff — Instituições e pessoas do sonho')}

## Errata e estado

Lazathar não é uma segunda capital real demonstrada: o jogador corrigiu a menção do diário de Glim. O destino material de possíveis referentes da cidade continua desconhecido. Ver {l('Lugares/Plano dos sonhos')} e {l('Eventos/Cativeiro e sonho de Fash')}. {f('J','Esclarecimentos — Sonho e geografia')}

## Lacunas

{P[14]}''',['F','H','J'],natureza='sonho')

nota('Eral','Eral',['glim'],f'''## Identidade e chegada

Cidade humana onde {l('Personagens/Glim Sombrasselva')}, {l('Personagens/Okay dBoa')}, {l('Personagens/Ryld')} e {l('Personagens/Crave')} começam a trabalhar para {l('Personagens/Arkhavel')}. Glim parte de Carruan numa caravana do duque Teodoron Talent; considera que Eral faz parte de seu domínio, mas escreve isso como impressão pessoal. A capital aparece com nome errado no diário e foi corrigida pelo jogador. {f('G','Glim — S1')}; {f('J','Esclarecimentos — errata Carruan/Lazathar')}

## Lugares e relações

A {l('Lugares/Torre de Arkhavel')} serve como base. A {l('Lugares/Igreja de Kord em Eral')} e a guarda atuam nas investigações e na defesa; a {l('Lugares/Arena de Eral')} integra o sistema criminoso ligado a Silthan, financiadores, falso prefeito e Mercado Negro. Os kenku inicialmente dão informações ao grupo e depois participam do saque. Essa leitura política é **síntese do handoff**. {f('H','Handoff — Facções e relações de poder; Eral, floresta e contatos atuais')}

O diário distingue a {l('Lugares/Casa de Carlos','casa do carpinteiro em frente à torre')} da {l('Lugares/Casa em quarentena')}, e documenta poço com água novamente envenenada. O assentamento dos rangers fica fora da cidade, próximo, com leis próprias. Não há coordenadas de bairro ou mapa de rotas seguro nesta nota. {f('G','Glim — S4, S8–S10 e S19')}; {f(T(13),'T13 — 01:12:10–01:12:47')}

## Ataque, população e estado mais recente

Após {l('Eventos/Ataque a Eral')}, há incêndios, mortes e êxodo. O mestre corrige os números improvisados durante S19: **cerca de 10 mil habitantes antes, 2 mil mortos, mil ainda na cidade e 7 mil em marcha**. Cerca de 60% dos mortos não morreram em combate. As baixas previstas entre refugiados são risco futuro, não número contabilizado. Os moradores presentes trabalham em mutirões por bairro. {f(T(19),'T19 — 00:23:55–00:26:59')}

Até S26 o grupo continua usando a torre, limpa e com a entrada desviada; isso não prova reconstrução concluída, retorno dos refugiados ou restauração do governo. A morte da taverneira é confirmada em S25. {f('G','Glim — S26')}; {f(T(25),'T25 — 00:14:11')}

## Lacunas

{P[2]} · {P[3]} · {P[16]}''',['G','J','H',T(13),T(19),T(25)])

nota('Torre de Arkhavel','Torre de Arkhavel',['glim'],f'''## Função e ocupantes

Residência e oficina de {l('Personagens/Arkhavel')} em {l('Lugares/Eral')}, utilizada como base pelos {l('Faccoes/Magnificos','Magníficos')}. Na S1 o grupo encontra sala de visitas, laboratório no andar superior e biblioteca oferecida a Glim como contrapartida do trabalho contínuo. A porta do laboratório leva à ilha do {l('Lugares/Plano Elemental do Ar')}. {f('G','Glim — S1')}

## Espaços e infraestrutura documentados

Há biblioteca, mesa de análise e espaços cujo interior não corresponde aos andares externos. Em S14 uma mesa desce, revelando escada em espiral para corpos preservados iguais a Arkhavel. O mestre explica que servem de receptáculos para sua alma caso morra; a leitura é de clones, não parentes adormecidos. Crave inicialmente os chama de família por não compreender a função. {f(T(14),'T14 — parte 1, 01:16:26–01:18:35')}

Carlos carpinteiro e sua família, moradores em frente, ajudam a organizar abrigo/curral e cuidados com animais. A construção mobiliza outros moradores e familiares das crianças do caso da Fada Órfã. {f('G','Glim — S14')}

## Acesso e deslocamento

As {l('Itens/Portas de Arkhavel')} alcançam cidades e planos. É preciso separar portas de viagem do deslocamento do **interior** da torre entre cascas externas preexistentes. S26 confirma cinco destinos conhecidos para esse segundo recurso: mundo atual, {l('Lugares/Plano das Sombras')}, Greyhawk, Forgotten Realms e Dark Sun. Nomes das cidades externas não foram fixados. A ida ao {l('Lugares/Plano Etereo')} ocorre por uma porta e não o acrescenta como sexta casca. Custos, runas e divergências de retorno devem ser consultados na nota do item. {f(T(26),'T26 — 00:51:02–00:55:39; 02:43:10–02:44:06')}

## Estado no corte de S26

Durante o ataque a Eral, invasores entraram e Tauro defendeu a torre, conforme síntese do handoff. Na S26, a retirada do medalhão revela fuligem e sangue antigo. O grupo contrata limpeza; Vesperal participa, depois ataca Crave. O combate danifica uma parede e deixa o corpo de Carlos carpinteiro. A torre é limpa, e Glim ativa desvio na entrada principal. A eficácia é limitada pela possibilidade de um intruso suficientemente habilidoso desfazer marcas. A ida etérea encerra a sessão; retorno e resultados dos estudos permanecem futuros. {f('H','Handoff — Lugares e regiões; Aurel Vesperal')}; {f('G','Glim — S26')}; {f('J','Esclarecimentos — Carlos carpinteiro')}; {f(T(26),'T26 — 00:52:13; 02:50:01–02:50:12')}

## Relações

{l('Lugares/Casa de Carlos')} · {l('Eventos/Preparativos da torre')} · {l('Itens/Mesa de analise')} · {l('Itens/Medalhao de limpeza')}
''',['G','H','J',T(14),T(26)])

nota('Igreja de Kord em Eral','Igreja de Kord em Eral',['glim'],f'''## Identidade e papel

Templo da {l('Faccoes/Igreja de Kord')} em {l('Lugares/Eral')}, associado a {l('Personagens/Tolomon','Tólomon')}. A síntese do handoff o descreve erguido sobre grandes ruínas e como força política e militar na cidade. Não há coordenadas, planta ou população residente documentadas nas passagens consultadas. {f('H','Handoff — Lugares e regiões; Igreja de Kord')}

## Acontecimentos

O diário registra o fechamento da igreja durante a investigação do desaparecimento do corpo de {l('Personagens/Carlos guarda','Carlos, o guarda')}, levado para autópsia. A suspeita era de que o responsável permanecesse lá dentro. Na S13 Glim recorda que o corpo falou na igreja e acusou o prefeito. A menção a igreja de “Thorn” no diário deve ser lida com cautela nominal; não identifica automaticamente o clérigo do sonho antigo. {f('G','Glim — S9 e S13')}

## Estado e lacunas

O ataque a Eral atinge seus defensores religiosos; o handoff deixa sucessão e estado institucional abertos. Não há documentação de reconstrução concluída do prédio. {f('H','Handoff — Consequências que merecem atenção; Pontos para validação')}

{P[2]}''',['H','G'])

nota('Arena de Eral','Arena de Eral',['glim'],f'''## Lugar e operação

Arena de lutas de {l('Lugares/Eral')}, centro do {l('Faccoes/Arena de Silthan','negócio de Silthan')}. Comprava criaturas e mantinha prisioneiros para combates. A rede envolvia financiadores, guarda infiltrada, falso prefeito, kenku e rangers; pagava ao {l('Faccoes/Mercado Negro')} e usava essa proteção para intimidar adversários. É informação recuperada do relato dos kenku no diário e da síntese do handoff, não uma planta ou cadastro imobiliário. {f('G','Glim — S13')}; {f('H','Handoff — Arena, falso prefeito e filhos de Arkhavel')}

## Queda e consequências

{l('Eventos/Queda da arena')} inclui combate, prisioneiros, chefes e cartas que expõem a rede. O grupo recupera tesouros de famílias e enfrenta disfarces por anéis de aparência; Silthan sobrevive inicialmente ao ataque da floresta por invocar a proteção do Mercado. Esses detalhes são **síntese do handoff**. {f('H','Handoff — Arena; Conclave; sequência S15–S16')}

## Distinção e estado

A arena dos trolls na {l('Lugares/Cidade ana dos trolls')} pertence à campanha antiga e é outro local. Não há localização cartográfica ou descrição do reaproveitamento da arena de Eral após sua queda e o ataque à cidade. A continuidade do prédio não pode ser inferida da continuidade do antigo negócio. {f('H','Handoff — Lugares e regiões; Duelo, traição e fim da campanha')}

{P[2]}''',['H','G'])

nota('Casa de Carlos','Casa de Carlos carpinteiro',['glim'],f'''## Localização e moradores

Casa **logo em frente à {l('Lugares/Torre de Arkhavel')}**, em {l('Lugares/Eral')}. Na S4, {l('Personagens/Carlos carpinteiro','Carlos')} mora com esposa e dois filhos. A família dorme sem descansar, e relatos dos vizinhos cessam quando eles ficam fora por algum tempo. {f('G','Glim — S4')}

## Magia viva e colaboração

O caso é ligado a um experimento de Arkhavel. Glim e Crave fazem vigília após o churrasco e encontram uma gosma esbranquiçada e translúcida sobre a cama do casal. A criatura é combatida; a família está viva e agradecida, apesar da cama quebrada. Na S14 o casal ajuda a erguer o abrigo de animais junto à torre; a esposa pode trabalhar perto dos filhos. {f('G','Glim — S9–S10 e S14')}; ver {l('Eventos/Caso Carlos e magia viva')}.

## Distinções e última informação

Esta casa não é a {l('Lugares/Casa em quarentena')} dos Mind Shredders. O Carlos guarda é outro homem, distinção explícita já na S8. Em S26 Vesperal usa o corpo do **carpinteiro**, confirmado pelo jogador em 23/10; o momento de sua morte e o destino posterior da esposa, filhos e residência não foram esclarecidos. {f('G','Glim — S8 e S26')}; {f('J','Esclarecimentos — Carlos carpinteiro')}

{P[2]}''',['G','J'],aliases=['Casa do carpinteiro'])

nota('Casa em quarentena','Casa em quarentena',['glim'],f'''## Identidade e localização relativa

Residência de {l('Lugares/Eral')} isolada após ataque de criatura larval com tentáculos, queimaduras redondas e buraco pequeno no chão. Seu endereço e os nomes da família não estão estabelecidos nas fontes consultadas. É distinta da {l('Lugares/Casa de Carlos')}, afetada pela magia viva do sono. {f('G','Glim — S19')}; {f('H','Handoff — Lugares e regiões')}

## Inspeção e acesso subterrâneo

Após o ataque à cidade, a casa está sem porta, revirada e com um cômodo principal que dá aos quartos. No fundo da sala há um buraco antes descrito como suficiente para um cachorro; S19 especifica agora **2,6 a 3 metros**, com escavação animal. Os moradores procuram outros acessos nos arredores e ajudam a preparar bloqueio e tocaia. {f(T(19),'T19 — 00:32:13–00:36:25; 00:42:35')}

## Ocupantes e estado mais recente

O grupo enfrenta três {l('Criaturas/Mind Shredders')} vistos saindo do posto. O conhecimento apresentado em S19 explica postos de alimentação separados de colônias principais ocultas; portanto a casa não é demonstrada como sede da colônia ou morada do Zhental. O diário de S20 ainda registra o buraco e a decisão de avisar Ryld. A inspeção posterior de Ryld não tem resultado confirmado. {f('G','Glim — S19–S20')}; {f(T(19),'T19 — 00:58:47')}; {f('H','Handoff — Mind Shredders')}

{l('Eventos/Posto dos Mind Shredders')} · {P[2]}''',['G','H',T(19)])

nota('Comunidade da floresta','Comunidade da floresta',['glim'],f'''## Identidade e ocupação

Comunidade próxima de {l('Lugares/Eral')}, fora de seus limites urbanos, ligada ao {l('Faccoes/Conclave da floresta')}. O mestre distingue suas leis das leis da cidade e menciona rangers, fadas e centauros. A síntese do handoff acrescenta druidas e simpatizantes, com estimativas de cerca de **50 a 60**, contando aspirantes; são aproximações, não censo. {f(T(13),'T13 — 01:12:10–01:12:47')}; {f('H','Handoff — Conclave e comunidade da floresta')}

## Relações e deslocamentos

{l('Personagens/Folha-Seca')} e {l('Personagens/Hanta')} pertencem à rede de contatos da floresta. Membros participam dos conflitos da arena, e a comunidade negocia imunidade para nomes envolvidos. Contatos com {l('Personagens/Vyrix')} aparecem na busca dos rangers. Este parágrafo é **síntese do handoff**; não prova que toda a comunidade tenha cometido os mesmos crimes. {f('H','Handoff — Conclave e comunidade da floresta; Eral, floresta e contatos atuais')}

## Estado e limites geográficos

O paradeiro da expedição de Folha-Seca e Hanta continua incerto. O diário registra a busca fracassada, o abandono da busca e o retorno por referência ao rio; isso não estabelece coordenadas do assentamento. Não identificar esta comunidade com o {l('Lugares/Conclave da Raiz Ancestral')} T23 do mapa antigo, nem com o Círculo Vetrilus das bruxas. {f('G','Glim — S18')}; {f('H','Handoff — Conclave e correções')}; {f(XI,'INTERESSES — B29 e legenda')}

{P[16]}''',['H','G',T(13),XI])

nota('Assentamento goblinoide','Assentamento goblinoide',['glim'],f'''## Alcance do nome

Nome de trabalho para a aldeia/acampamento goblinoide e o complexo de cavernas associados aos crimes e ao saque de {l('Lugares/Eral')}. Não afirma que todas as referências sejam o mesmo sítio. O diário relata que a célula da aldeia se aproximara de Eral por considerar a proteção da organização do prefeito mais segura que seu território anterior. {f('G','Glim — S13')}

## Ocupação e acontecimentos

Há guerreiros, famílias, escravos humanos, crianças acorrentadas, ferros cravados e restos de canibalismo. O chefe produz inversões de acertos e erros numa condição chamada doença, sem poder irrestrito de alterar a realidade. A tenda contém rabiscos; outra caverna tem símbolos perfeitos no teto. Esses dois locais de inscrições não são uma única marca demonstrada. O relato aqui é **síntese do handoff**, fundamentada ali nas S21–S23. {f('H','Handoff — Chefe goblin; Consequências que merecem atenção')}

{l('Eventos/Crise dos refens')} inclui libertação de humanos e reféns divididos em setores; a recapitulação da S23 fixa quinze humanos mortos nos quatro setores não salvos. O massacre nas cavernas também atinge indefesos goblinoides. Sobrevivência de alguns reféns e vitória em combate não significam esvaziamento completo da região. {f('H','Handoff — Consequências; sequência S22–S23')}

## Acesso e estado

A síntese preserva referências a quatro dias de Eral e a um ou dois dias para um acampamento próximo, talvez locais diferentes. Não há coordenada segura ou nome formal. O estado posterior de cada caverna, ocupantes remanescentes e relação exata dos trajetos permanecem abertos. {f('H','Handoff — Lugares e regiões')}

{P[3]}''',['G','H'])

nota('Cidade drow','Cidade drow — P22',['fash','glim'],f'''## Identidade e estrutura

Antiga cidade subterrânea dos drow, identificada como **P22** no diário e na legenda do mapa de Fash. Ocupada pelo {l('Personagens/Druida Sangrento')} e por anões escravizados antes da vitória do grupo antigo. O complexo tem casas com defesas próprias, tesouros, minas, trechos inundados e passagens secretas. Não confundir a coordenada P22 com a grade de células da planilha: é referência do mapa desenhado. {f('F','Fash — Dia 45, 22/01 e 29/01')}; {f(XI,'INTERESSES — B47 e legenda visual')}

## Libertação e reassentamento

Após Kael matar o drow, recebe a autoridade das coleiras e liberta os anões. Fash descreve uma comunidade inteira nascida em escravidão. Humanos do Forte são transferidos para o subterrâneo; meio-dragões recebem pagamento para proteção e passam a assumir {l('Lugares/Throden')}. Timo molda rocha e o grupo sinaliza caminhos labirínticos para substituir a rota em que era necessário nadar. {f('F','Fash — 22/01, 25/01 e 29/01')}; {l('Eventos/Reassentamento em Throden')}.

A aba administrativa registra **15 anões e 80 humanos**, além de minas de mithral (2.000 PO/mês) e ouro (1.200 PO/mês), 2.500 armas e 6.500 armaduras. São anotações administrativas sem data reconciliada ou garantia de produção atual; não equivalem à população inicial estimada em dois mil no Forte. {f(XA,'ADMINISTRAÇÃO CIDADE DROW — B2:C17')}

## Rotas e portais

Uma passagem inferior segue sem bifurcação até a {l('Lugares/Cidade ana dos trolls')}; outra exploração desce a uma trifurcação, com populações aracnídeas e a {l('Lugares/Biblioteca do beholder')}. O {l('Lugares/Fosso de ossos e nodo')} fica na caverna antes da cidade. {f('F','Fash — 29/01 e solo dos 45 dias')}

O diário de 29/01 registra **três** portais: Abismo, outro relacionado a família e um não identificado. No XLSX original de INTERESSES há **cinco rótulos, três sem rasura e dois riscados**: C48 Abismo, C49 Mundo Espelhado e C50 Ilha dos Elfos da Noite estão sem risco; C51 ~~Cabeça de Gigante~~ e C52 ~~4 Costelas Grandes~~ têm `font.strike=true`. O estilo foi conferido diretamente no OOXML do original; a conversão Markdown inicial não o exibia. Portanto a lista não demonstra uma contradição automática de cinco contra três. A rasura também não prova que portas tenham sido fisicamente eliminadas: significado, datas e correspondência entre os três nomes sem rasura e os três portais do diário continuam abertos. {f('F','Fash — 29/01')}; {f(XI,'INTERESSES — C48:C52 e estilos do XLSX original')}

## Estado mais recente

Na S25, mapas entregues ao grupo atual descrevem a antiga cidade sob dragão negro e trolls, superfície devastada, minas e equilíbrio regional com beholder e outro dragão. O mestre confirma que os mapas contêm detalhes de caminhos e nodo; Okay reconhece a letra de Firael. É informação de mapas e memória, sem nova visita dos Magníficos a P22. A condição atual dos humanos e anões reassentados não é conhecida. {f('G','Glim — S25')}; {f(T(25),'T25 — 01:26:13–01:28:35; 01:36:35')}

{P[4]} · {P[5]}''',['F',XI,XA,'G',T(25)],aliases=['P22'])

nota('Cidade ana dos trolls','Antiga cidade anã dos trolls',['fash','glim'],f'''## Local e ocupação antiga

Cidade originalmente anã, ocupada por trolls na campanha de Fash. Fash a alcança seguindo a passagem inferior da {l('Lugares/Cidade drow')} sem encontrar bifurcações, concluindo que ali residiam os cobradores de tributos. Os anões libertos relatam pagamentos aproximadamente semestrais em utensílios fabricados por eles. {f('F','Fash — 25/01 e 29/01')}

## Arena e acordo

No Dia 45 um emissário troll com metade inferior de cobra conduz dois trolls em coleiras e recolhe utensílios de mithral e cem peças de ouro. Uma convocação exige um campeão para a arena; Fash pede sete dias, e Firael se prepara. Tambores ecoam da cidade. A planilha acrescenta arena e líder de três cabeças, sem fornecer coordenada ou relato de encontro direto com esse líder. {f('F','Fash — Dia 45')}; {f(XI,'INTERESSES — C63:D67')}

O jogador completa o desfecho ausente no diário: Firael foi gravemente ferido pelo troll. Depois foi entregue vivo ao dragão negro por Fash e Kael. Isso explica o {l('Eventos/Duelo e entrega de Firael')}, mas não documenta abandono ou conquista da cidade dos trolls. {f('J','Esclarecimentos — Desfecho não registrado')}

## Estado mais recente

Os mapas de S25 descrevem trolls, dragão negro e experimentos na região da antiga cidade drow. Não estabelecem o nome próprio da cidade anã, seu censo ou a distribuição atual dos trolls entre cidade, túneis e superfície. A arena daqui é distinta da {l('Lugares/Arena de Eral')}. {f('G','Glim — S25')}

{P[4]}''',['F',XI,'J','G'])

nota('Throden','Throden — Forte Q23',['fash','glim'],f'''## Identidade e coordenada

Forte humano da campanha de Fash, chamado **Throden** pelos meio-dragões quando passam a ocupá-lo. A planilha escreve “O Forte — Throden (Q23)”; a legenda incorporada escreve **Vytharix Throdenaar**, na mesma coordenada **Q23**. A equivalência de ponto é explícita no mapa; a forma extensa é conservada como nome da legenda, sem afirmar sua etimologia. {f('F','Fash — solo dos 45 dias')}; {f(XI,'INTERESSES — B2 e legenda visual')}

## Aspecto e população no primeiro encontro

Fash estima cerca de **duas mil pessoas**, maioria humana, aproximadamente um meio-dragão por dez moradores e poucos centauros e halflings. Descreve cidade compacta, muitos cavalos, muros de pedra de três metros, pequenas casas de madeira e construção central maior, de pedra. São estimativas e impressões do narrador. {f('F','Fash — 30/10, data interna 29/7/530')}

Seus líderes acreditam ser a última cidade humana livre: interpretam as cidades do norte como dependentes dos drow após antiga guerra. Fash e companheiros questionam isso. O contato comercial conhecido é por navios halflings, com intervalos que podem chegar a meses; a hipótese de isolamento deliberado é especulação do grupo. {f('F','Fash — 30/10')}

## Guerra e troca de ocupação

O regente oferece destruir a esfera de Elena caso o problema do drow seja resolvido; a destruição inicia o fenômeno de luz. Setenta guerreiros do Forte morrem no ataque à caverna segundo síntese do handoff. Após a vitória sobre o drow, o diário registra humanos transferidos para P22 e meio-dragões assumindo gradualmente fortificações e plantações. {f('F','Fash — 25/01 e 29/01')}; {f('H','Handoff — Forte, cidade drow e libertações')}

## Rotas e estado

A fuga da cabana leva o grupo através de floresta e rio; após quase cinco dias desde a travessia, alcançam os portões. O território de Timo é alcançado a cavalo em cerca de meio dia em outra entrada. A vila de origem dos meio-dragões fica em **U27**, outro ponto do mapa. Não transformar coordenadas em distâncias sem escala. A ocupação atual de Q23, muito depois de Fash, permanece sem atualização direta. {f('F','Fash — 30/10 e 31/10')}; {f(XI,'INTERESSES — legenda U27')}

{l('Lugares/Vila dos meio-dragoes')} · {l('Eventos/Reassentamento em Throden')} · {P[4]}''',['F',XI,'H'],aliases=['Forte Q23','Vytharix Throdenaar'])

nota('Vila dos meio-dragoes','Vila dos meio-dragões — U27',['fash','glim'],f'''## Identidade e coordenada

Vila de origem dos meio-dragões, marcada **U27** e nomeada **Darastrix Vurix** na legenda visual da planilha de Fash, conferida diretamente. É outro lugar que {l('Lugares/Throden','o Forte Q23')}; os moradores migram de um para o outro. Não há escala de distância ou rota formal entre ambos. {f(XI,'INTERESSES — legenda incorporada, U27')}; {f('F','Fash — 25/01 e solo dos 45 dias')}

## Relação com o grupo e migração

Depois da morte do Druida Sangrento, o grupo contrata proteção remunerada dos meio-dragões para humanos reassentados na cidade subterrânea. Eles podem assumir o antigo Forte, considerado melhor posicionado e mais fortificado. Fash também contrata trabalhadores dessa população para escavar o fosso de ossos; a mudança ao Forte ocorre aos poucos. {f('F','Fash — 25/01 e solo dos 45 dias')}

## Estado mais recente e limites

As fontes documentam a migração, não o abandono completo de U27. Não há população, chefia, ocupação remanescente ou atualização atual verificadas para a vila. O título “meio-dragões de Throden” designa a comunidade após o reassentamento e não transfere U27 para Q23. {f('F','Fash — solo dos 45 dias')}; {f(XI,'INTERESSES — legenda Q23 e U27')}

{P[4]}''',['F',XI],aliases=['Darastrix Vurix','U27'])

nota('Fosso de ossos e nodo','Fosso de ossos e nodo',['fash','glim'],f'''## Fosso na campanha antiga

Grande depósito de ossos na caverna anterior à {l('Lugares/Cidade drow','cidade drow P22')}, perto de onde o Cérebro Ancião esteve preso. Para entrar na {l('Faccoes/Organizacao do Necromante')}, Fash escava e envia ossos de dragão por saco mágico. Meio-dragões trabalham inicialmente; ele conclui sozinho. Lídia indica uma passagem subterrânea pouco abaixo do nível atingido. O Necromante diz ter perdido o vínculo com ela quando se aproximou dessa passagem e manda investigá-la. A causa não está demonstrada. {f('F','Fash — solo dos 45 dias')}

## Nodo nos mapas atuais

Na S25, o mestre confirma que mapas atuais descrevem um **nodo funcional**, oculto sob ossos e grande quantidade de rocha, guardado por criatura. O dragão não sabe que ele está ali; Firael soubera por informação do Cérebro. A hipótese de o nodo resultar dos mortos acumulados é apresentada como possibilidade. O grupo não o visita nessa sessão. {f(T(25),'T25 — 01:28:35; 01:39:15')}

## Distinções e acesso

O título reúne o fosso antigo e o nodo atual por contexto geográfico, **sem declarar identidade plenamente reconciliada**. Também não identifica automaticamente esse nodo ao descrito pelo livro das bruxas como origem do Círculo Vetrilus. A explicação geral de Elena sobre formação de nodos é relato dela, não demonstração da origem deste. {f('F','Fash — 07/11 e 02/12 solo')}

Não há coordenada própria do fosso, profundidade medida ou percurso seguro atualizado. O acesso antigo fica antes de P22; os mapas de S25 alertam para um guardião. {f('F','Fash — solo dos 45 dias')}; {f(T(25),'T25 — 01:28:35')}

{P[6]}''',['F',T(25)])

nota('Biblioteca do beholder','Biblioteca do beholder',['fash','glim'],f'''## Localização e descoberta

Biblioteca gigantesca num ramo de uma trifurcação que Fash alcança descendo a partir da {l('Lugares/Cidade drow')}. Os outros dois caminhos parecem levar a populações aracnídeas, uma inteligente e outra não; são impressões de reconhecimento. Fash vê o {l('Personagens/Beholder da biblioteca')}, acredita não ter sido visto e recua. {f('F','Fash — solo dos 45 dias')}

## Mapas e posição atual

A planilha associa o caminho triplo a Chitine, um destino “?” e Beholder; também o lista como presença subterrânea. Isso não fornece nome próprio da biblioteca ou número de volumes. Nos mapas atuais, o beholder tem seguidores, sua biblioteca está detalhada e há tratado ou equilíbrio regional com dragões e trolls. A descrição política do tratado é de mapas no diário, sem visita atual. {f(XI,'INTERESSES — C53:E57 e C77')}; {f('G','Glim — S25')}; {f(T(25),'T25 — 01:28:35')}

## Acesso e estado

Nenhuma coordenada própria, regra de admissão, identidade dos seguidores ou acesso seguro foi confirmada. As informações recentes tornam a biblioteca um alvo possível de investigação, não uma aliada disponível do grupo. O suposto interesse de Firael no cérebro do beholder é conjectura discutida pelo mestre, não ataque consumado. {f(T(25),'T25 — 01:45:03')}

{P[4]}''',['F',XI,'G',T(25)])

nota('Floresta de Timo','Floresta de Timo',['fash','glim'],f'''## Identidade e ocupação antiga

Território florestal reconhecido por {l('Personagens/Timo')}, associado a sua matilha e a {l('Personagens/Cogu')}. O diário registra acesso a cavalo desde o Forte em aproximadamente meio dia. Houve reconhecimento de hipogrifos e criaturas extraplanares na região; não há fronteiras medidas. {f('F','Fash — 31/10 e 24/11')}

## Perseguição das bruxas

O grupo percebe ausência de pássaros e acompanha seis Marrash rumo ao mar. Encontra clareira com plantas mortas, rubi suspenso e árvore corrompida em formação. Fash a incendeia, a degradação para e o rubi cai. A associação do ritual aos pelos de Cogu e ao rastreamento pelas bruxas é teoria construída pelo grupo a partir do livro. Mais tarde uma armadura animada com símbolo das bruxas passa da entrada de P22 rumo à floresta e é destruída por Kael e Timo ao proteger Cogu. {f('F','Fash — 31/10 e Dia 45')}

## Coordenada e continuidade

A célula C79 de INTERESSES associa “Floresta do Timo” a **W23**, sob a seção Ruínas. A legenda visual identifica W23 como **Ruína 2**. Isso pode indicar uma ruína dentro da área, mas não foi confirmado; conservar ambas as formulações. A identidade posterior de Timo como planta e cajado foi confirmada pelo jogador, porém não estabelece que o {l('Lugares/Santuario da driade')} esteja exatamente neste território antigo. {f(XI,'INTERESSES — B78:C81 e legenda')}; {f('J','Esclarecimentos — Timo')}

Ocupação atual da floresta, destino de sua matilha e posição precisa do santuário permanecem abertos. {P[10]} · {P[5]}''',['F',XI,'J'],aliases=['Floresta do Timo'])

nota('Necropole','Necrópole',['fash','glim'],f'''## Localização documentada

O {l('Personagens/Necromante')} informa a Fash uma necrópole não muito distante da cidade drow, **próxima do rio e logo abaixo dos Equiceps**. A planilha a marca em **H20**, imediatamente após a referência aos Equicep em H19. Não há escala ou distância de viagem; “abaixo” conserva a descrição da fonte. {f('F','Fash — solo dos 45 dias')}; {f(XI,'INTERESSES — C5 e C26')}

## Organização e ameaça

O jogador associa a {l('Faccoes/Organizacao do Necromante')} à necrópole, mas não recorda seu nome. Na campanha antiga, o Necromante considera um Cavaleiro da Morte selado ameaça à organização, por mobilizar mortos-vivos para guerra caótica. Não há relato de visita de Fash à necrópole nas passagens consultadas. {f('F','Fash — solo dos 45 dias')}; {f('J','Esclarecimentos — Organizações e personagens sobreviventes')}

## Estado atual e hipóteses

A ideia de que o {l('Personagens/Cavaleiro da Morte')} possa ter despertado e tomado a necrópole é lembrança hipotética e condicional do jogador, não acontecimento confirmado. A {l('Lugares/Area dos mortos-vivos imoveis')} da campanha atual não recebeu coordenada que permita identificá-la como H20. {f('J','Esclarecimentos — hipótese da necrópole')}; {f(T(25),'T25 — 00:46:15–00:47:55')}

{P[7]}''',['F',XI,'J',T(25)],aliases=['Necrópole H20'])

nota('Covis de Hourian Haurim','Covis de Hourian / Haurim',['fash'],f'''## Identidade e interesse

Conjunto de covis que o grupo antigo considera explorar em busca de recursos. O diário de 08/02 escreve **Haurim**; entradas anteriores mencionam o dragão vermelho **Hourian** e uma estatueta ligada a ele. A variação é preservada, sem corrigir a grafia por conhecimento externo. {f('F','Fash — 08/02, 01/12 e 02/12 solo')}

## Localização e rota

INTERESSES B82:C83 registra apenas “Covis de Haurim” e “Duas montanhas ao sul”. O diário considera a viagem distante e longa demais para voltar antes da visita dos trolls, razão para adiar a exploração. Não fornece nome das montanhas, coordenada, caminho ou duração absoluta. {f(XI,'INTERESSES — B82:C83')}; {f('F','Fash — 08/02')}

## História atribuída e estado

Firael relata que Hourian favorecia o progresso das raças e morreu contra uma grande revoada de dragões. É relato do personagem, não inspeção dos covis ou confirmação de seus tesouros. A revoada não deve ser identificada automaticamente com a Revoada Branca da região gelada. O estado dos covis, sua ocupação e qualquer visita posterior permanecem sem desfecho. {f('F','Fash — 01/12')}; {f('H','Handoff — História regional adicional')}

{P[8]}''',['F',XI,'H'])

nota('Regiao gelada','Região gelada e cidade sem nome',['glim'],f'''## Localização e meio

Região nevada do **plano natal do grupo**, confirmada pelo mestre durante a prova de Kord. Há uma cidade de gelo indicada no mapa, sem nome transcrito, e montanhas abaixo dela. Okay reconhece a região pelas silhuetas quando a neblina se desfaz. A {l('Lugares/Aldeia ocupada na neve')} é outro ponto dentro dessa região montanhosa. Não há coordenada recuperável do apontamento do mapa. {f(T(23),'T23 — 01:07:13–01:08:44')}

## História e ocupação

O mestre descreve expansão humana abandonada há muito tempo e ruínas de antigas cidades; a hostilidade do clima, alimentação e água torna rara a visita de humanos, elfos e anões. Acredita-se que gigantes da tempestade, gigantes de gelo e trolls do gelo predominem. Isso é conhecimento regional com incerteza explícita, não censo ou ausência absoluta de outras raças. A presença da tribo humana surpreende Okay. {f(T(23),'T23 — 01:08:44')}

Na mesma passagem, o mestre revela em off uma **Revoada Branca**, ressalvando que essa informação pertencia a outra mesa e não aos personagens atuais. Data e participantes permanecem indefinidos; não equiparar a outras revoadas ou à Noite Eterna. {f(T(23),'T23 — 01:08:44')}

## Estado e acesso

O grupo chega por transporte de Tariun para a missão religiosa, não por rota terrestre medida. Depois regressa, e Tariun pretende concluir a tarefa na montanha. Não há exploração documentada das ruínas nem notícia posterior sobre a cidade de gelo. Esta região não é a {l('Lugares/Montanha das memorias')}. {f('H','Handoff — Consequências que merecem atenção; Lugares e regiões')}

{P[9]}''',[T(23),'H'])

nota('Aldeia ocupada na neve','Aldeia ocupada na neve',['glim'],f'''## Lugar e ocupação

Aldeia em área relativamente plana de uma montanha da {l('Lugares/Regiao gelada')}, palco das {l('Eventos/Provacoes de Kord')}. A síntese do handoff registra cerca de cem mulheres e crianças entre os ocupantes quando o grupo chega. O local fora tomado de seguidores de Kord, e o sobrevivente original era um sacerdote com pernas quebradas. Os atuais ocupantes praticavam canibalismo; o mestre identifica em off o sacerdote como a única pessoa não vilã da situação. Essa caracterização não torna todo ocupante combatente apto. {f('H','Handoff — Consequências que merecem atenção')}; {f(T(23),'T23 — 02:12:17–02:13:36')}

## Acesso e terreno tático

A neve dificulta a caminhada, sobretudo de crianças que precisam ser carregadas. O mestre descreve uma extensão plana equivalente a cerca de cinco horas de deslocamento nas condições locais, acesso íngreme de melhor escalada e outro afunilamento de trilha que favoreceria defesa de poucos contra muitos. São tempos de cena dependentes da neve, não escala cartográfica geral. Os moradores removem neve do interior da aldeia. {f(T(23),'T23 — 01:47:37')}

## Rito, ataque e estado

Crave escolhe o rito do cinto enquanto Glim e Okay tentam proteger fugitivos dos yetis. Os ocupantes dizem poder voltar a outra região, pois apenas haviam tomado aquela vila. O resgate não salva todos: Okay consegue levar a criança do casaco, mas não há total final de mortos. A figura do prelúdio leva o sacerdote vivo. Tariun depois parte para concluir a tarefa, sem resultado registrado. A ocupação final da aldeia não é conhecida. {f(T(23),'T23 — 02:12:17; 03:44:38–03:48:25')}; {f('H','Handoff — Consequências que merecem atenção')}

O disco de retorno não transportava quem não participara da ida. Não confundir esta montanha com a rota futura de um mês desde Carruan. {f('H','Handoff — Consequências')}; {l('Lugares/Montanha das memorias')}.

{P[9]}''',['H',T(23)])

nota('Santuario da driade','Santuário da dríade',['glim','fash'],f'''## Identidade e transformação

Área conhecida por Okay, anteriormente cercada de corrupção. Uma planta ainda em botão ajudava a manter o local em equilíbrio. Na S25 os relatos recebidos pelos arquivistas descrevem agora floresta saudável e uma fada parecida com centaura carregando cajado como grande girassol, capaz de crescimento vegetal muito rápido. A descrição está no diário, sob perspectiva de Glim e dos relatos trazidos; não é uma nova visita do grupo inteiro. {f('G','Glim — S25')}

## Timo e os santuários

Ao reconhecer a região, o mestre lembra que foi onde o personagem antigo de César brotou e foram feitos santuários em volta. A identificação **Timo → planta → cajado de girassol** foi confirmada pelo jogador. Isso não identifica a portadora como reencarnação de Timo. Okay decide não contar a Glim a identidade anterior da planta, segundo síntese do handoff. {f(T(25),'T25 — 01:25:51')}; {f('J','Esclarecimentos — Timo')}; {f('H','Handoff — Correções; Timo e dríade')}

## Geografia e estado

A melhora da floresta e a transformação da planta são as últimas informações documentadas. Não há coordenada, nome formal ou rota de visita nesta nota. A ligação exata com a {l('Lugares/Floresta de Timo')} antiga e com W23 não foi estabelecida. O mesmo vínculo pessoal de Timo não resolve a identidade geográfica dos locais. {f('G','Glim — S25')}; {f(XI,'INTERESSES — C79 e legenda')}

{l('Itens/Cajado de girassol')} · {P[10]}''',['G',T(25),'J','H',XI])

nota('Area dos mortos-vivos imoveis','Área dos mortos-vivos imóveis',['glim'],f'''## Descrição e evidência

Região descrita por um informante dos {l('Faccoes/Arquivistas')} na S25: pequena cordilheira com passagens entre rochas, terra corrompida e pedras enegrecidas. O explorador vê esqueletos e zumbis aglomerados, imóveis, que não reagem enquanto ele não se aproxima ou ataca. Estima mais de cem, talvez duzentos, e recua por não poder enfrentá-los. É relato de reconhecimento de NPC, não observação direta dos Magníficos ou censo. {f(T(25),'T25 — 00:46:15–00:47:55')}

## Hipótese de ocupação

O informante relaciona a anomalia ao {l('Personagens/Cavaleiro da Morte')}, desaparecido desde a época da Noite Eterna, porque duvida que um necromante manteria tantos mortos-vivos estáticos. Ele diz explicitamente que está supondo. Não há encontro com o Cavaleiro, prova de domínio ou origem da corrupção. {f(T(25),'T25 — 00:47:05–00:47:55')}

## Estado e acesso

As fontes consultadas não oferecem nome, coordenada ou duração de viagem. O local é apontado como opção de investigação e permanece sem visita posterior no corte da S26. Não fundir com a {l('Lugares/Necropole')} H20, cuja tomada pelo Cavaleiro é outra hipótese, do jogador. {f('G','Glim — S25–S26')}; {f('J','Esclarecimentos — necrópole')}

{P[7]}''',[T(25),'G','J'])

nota('Covil maritimo','Covil marítimo das expedições',['glim'],f'''## Localização e acesso

Localidade investigada pelos {l('Faccoes/Arquivistas')} perto da região élfica. {l('Personagens/Tahen')} mostra atlas a Okay e descreve travessia pela água até uma ilha/continente indicado à esquerda do mapa. A entrada é uma cratera na base de **penhasco**, acessível pelo mar e suficientemente grande para embarcação. O apontamento visual não está preservado no TXT, portanto não há coordenada segura ou nome de litoral. {f(T(24),'T24 — 02:10:17–02:10:45')}

## Expedições e ocupantes presumidos

O primeiro grupo reporta provável covil de dragão e seita que o cultuava ou nutria; depois deixa de enviar notícias, e o barco desaparece. Uma segunda leva, mais experiente e armada, também some com suas embarcações. O mestre/professor de Okay, {l('Personagens/Elrohir')}, participava dessa segunda expedição. O dragão **não foi identificado**. A possibilidade de guardiões ou descendentes no local motivou o reforço, sem confirmar sua existência atual. {f(T(24),'T24 — 02:08:41–02:11:41')}; {f('H','Handoff — Arquivistas e contatos atuais')}

## Estado mais recente e distinções

A organização mantém o lugar em espécie de quarentena e debate como agir. Há preocupação com sobreviventes, enquanto anciões suspeitam que já tenham morrido; nenhuma dessas opiniões confirma destino final. Okay promete investigar, mas a viagem não ocorreu ao fim de S26. {f(T(24),'T24 — 02:08:41; 02:11:41–02:13:37')}; {f('G','Glim — S26')}

Este covil marítimo não é o covil do dragão negro da região de {l('Lugares/Cidade drow','P22')}; não há evidência de equivalência entre os locais ou dragões. {f('H','Handoff — Lugares e regiões')}

{P[11]}''',[T(24),'H','G'])

nota('Montanha das memorias','Montanha das memórias',['glim'],f'''## Identidade e objetivo

Montanha onde Okay acredita poder encontrar uma {l('Personagens/Mulher das memorias','mulher capaz de ajudá-lo a recuperar mais memórias')}, após lembrar sua vida como Kael. É um destino planejado; nome próprio, identidade da mulher e endereço exato não foram fixados nas passagens consultadas. {f('G','Glim — S25')}

## Rota documentada

O mestre confirma a **capital** como ponto de chegada mais próximo entre as portas de Arkhavel. A capital é {l('Lugares/Carruan')}, aplicando a errata do jogador. A partir dela, o mestre estima aproximadamente **um mês a cavalo**; a avaliação é feita sobre o mapa, sem distância em quilômetros. O diário registra estrada perto da montanha. Não há roteiro detalhado, paradas ou coordenada. {f(T(25),'T25 — 01:57:28–01:58:39')}; {f('J','Esclarecimentos — Carruan/Lazathar')}; {f('G','Glim — S25')}

## Estado da viagem

O grupo decide estudar e proteger a torre antes de ficar tanto tempo fora. S26 encerra com ida ao Etéreo para estudos; o próprio diário ressalta que ainda não estavam a caminho da montanha. Portanto nenhum encontro, recuperação adicional de memórias ou resultado da viagem está consumado. {f('G','Glim — S25–S26')}

A montanha é distinta da {l('Lugares/Aldeia ocupada na neve','montanha nevada da prova de Kord')}. Sem confirmação não associar as duas por sua forma de relevo. {f('H','Handoff — Lugares e regiões')}

{P[12]}''',['G',T(25),'J','H'])

nota('Mercadia','Mercadia',['glim'],f'''## Aspecto e natureza do lugar

Cidade de circulação planar visitada a partir de uma casa de Arkhavel. Na S20 o céu parece aurora boreal, e além dele há uma cobertura cristalina que fecha a cidade, semelhante a ilha dentro de globo de neve. A arquitetura é de pedra naturalmente prateada, extremamente detalhada; há casas de dois ou três andares, torres e galpões comerciais de até dez andares. Essas são observações narradas em cena, sem nome confirmado do plano ou coordenadas materiais. {f(T(20),'T20 — 00:22:41–00:25:02')}

## Circulação e ocupação

Ruas muito cheias, liches sem disfarce, seres poderosos, dragões que mudam de forma ao pousar e embarcações flutuantes. A impressão inicial de ausência de raças mais básicas não é proibição absoluta: a síntese do handoff registra depois o grupo heterogêneo de Tariun. Não há censo ou governo identificado. {f(T(20),'T20 — 00:25:02')}; {f('H','Handoff — Mercadia e circulação planar')}

## Casa de Arkhavel e comércio

A casa de madeira da qual saem os Magníficos é considerada boa para seu mundo, mas simples e mal-acabada diante do restante da cidade. Um contato indica o comerciante Tareksin e a loja {l('Lugares/Laoum')} **três quadras abaixo** da saída utilizada. O comércio oferece grande variedade de bens mágicos, com preços negociados e risco de pagar mais caro. {f(T(20),'T20 — 00:21:54–00:25:02; 00:36:05–00:36:25')}

{l('Personagens/Tariun')} é encontrado na cidade e se torna contato de Crave nas questões de Kord. A mesa cita proibição de usar magia na cidade, mas alcance, exceções e sanções não foram detalhados nas passagens consultadas; essa regra é recuperada como **síntese do handoff**, sem importar legislação externa de outros cenários. {f('H','Handoff — Mercadia e circulação planar; Igreja de Kord')}

## Estado e acesso

Continua sendo destino de compras e contato religioso nas sessões seguintes. A casa de Mercadia não deve ser automaticamente identificada como uma das cinco cascas conhecidas do interior da torre, cujas cidades não foram nomeadas. {f('G','Glim — S25')}; {f(T(26),'T26 — 02:43:10–02:44:06')}

{P[15]}''',[T(20),'H','G',T(26)])

nota('Laoum','Laoum',['glim'],f'''## Identidade e acesso

Loja em {l('Lugares/Mercadia')}, indicada por contato de Arkhavel como estabelecimento de Tareksin, a três quadras abaixo da saída usada pelo grupo. O nome do atendente aparece com variações de transcrição; o nome da loja é explicitamente informado como Laoum. Não há endereço além dessa referência relativa. {f(T(20),'T20 — 00:21:54–00:22:27')}

## Interior e proteção

A loja está cheia de itens e bugigangas presumivelmente mágicos. Na porta há guardião semelhante a inevitável, considerado pelo mestre muito mais forte e de patamar épico; isso é comparação de aparência e força, não identidade de espécie confirmada. Atrás do atendente ficam três figuras: encapuzado com facas, guerreiro de armadura completa com espada bastarda e escudo, e figura em manto de lava com mãos femininas. A aparência do atendente foi mostrada por imagem ausente do TXT, portanto não é reconstruída aqui. {f(T(20),'T20 — 00:28:51–00:33:08')}

## Comércio e estado

O atendente fala dracônico antigo, compreensível com palavras desconhecidas para os personagens que sabem dracônico. O grupo negocia compras; o mestre explica variação de preços pela negociação. Não há ataque, troca de proprietários ou fechamento documentados. Regras de inevitáveis de outros livros não foram usadas para corrigir o guardião desta mesa. {f(T(20),'T20 — 00:32:54–00:36:25')}

{P[15]}''',[T(20)])

nota('Plano Elemental do Ar','Plano Elemental do Ar',['glim'],f'''## Lugar visitado

Destino da primeira missão para Arkhavel. Pela porta preparada no laboratório, o grupo chega a uma grande ilha flutuante com campina; outras ilhas aparecem num céu aparentemente infinito e tempestades/furacões, alguns parecendo rostos ou corpos, são vistos ao longe. Esta nota descreve somente a área visitada, não uma geografia universal do plano. {f('G','Glim — S1')}

## Acesso e missão

Arkhavel busca um pequeno elemental da tempestade e fornece garrafa rúnica. Uma primeira abertura produz rajada que o lança contra a parede; ele recalibra a porta. Na ilha, o grupo caminha por dias e encontra o elemental no segundo dia; Crave é derrubado por raios, Glim atordoa a criatura e a recolhe na garrafa. Todos retornam pela mesma porta. {f('G','Glim — S1')}; {l('Eventos/Chegada a Eral')}.

## Estado e limites

Não há população, cidade, nome da ilha ou coordenada documentados. A missão é concluída, e o elemental passa a alimentar o dispositivo de limpeza de Arkhavel. A possibilidade de voltar depende das {l('Itens/Portas de Arkhavel')}; a lista de cinco cascas móveis da torre é outro recurso e não inclui automaticamente este plano. {f('G','Glim — S1')}; {f(T(26),'T26 — 02:43:10–02:44:06')}''',['G',T(26)])

nota('Plano Etereo','Plano Etéreo',['glim'],f'''## Função na campanha

Destino planejado para os estudos de Okay, pois o mestre informa relação de **um dia no Etéreo para uma hora no Material**. A mesma explicação menciona encontros possíveis como aranhas planares e fantasmas. Este parágrafo é **síntese do handoff**, que remete à S24; não representa experiência efetivamente registrada pelo grupo. {f('H','Handoff — Torre e portas de Arkhavel')}

## Acesso confirmado e corte

O fim da S26 confirma que o grupo fez a ida por uma porta, e a próxima sessão começaria com o retorno. A transcrição usa formulação oral confusa perto de 02:50; o diário esclarece “O Plano Etéreo ficou para a porta, não para a torre inteira”. Não há duração vivida, encontros realizados ou lista final de magias copiadas documentados no corte. {f(T(26),'T26 — 02:50:01–02:50:12')}; {f('G','Glim — encerramento S26')}

## Distinções geográficas

Etéreo não é sexta casca conhecida da {l('Lugares/Torre de Arkhavel')}. Os cinco destinos do interior são mundo atual, Sombras, Greyhawk, Forgotten Realms e Dark Sun. A ida também não representa partida para a {l('Lugares/Montanha das memorias')}. {f(T(26),'T26 — 02:43:10–02:44:06')}; {f('G','Glim — S26')}

{l('Eventos/Preparativos da torre')} · {l('Itens/Portas de Arkhavel')}''',['H',T(26),'G'],aliases=['Etéreo'])

nota('Plano das Sombras','Plano das Sombras',['fash','glim'],f'''## Registro material atual

Uma das cinco localizações conhecidas em que o **interior** da torre de Arkhavel pode se encaixar numa casca externa preexistente. O mestre confirma a lista em S26; fala de cidades, mas não nomeia a cidade ou descreve seus habitantes, ruas ou posição. A capacidade descoberta não demonstra que o grupo tenha feito essa transferência. {f(T(26),'T26 — 00:53:03; 02:43:10–02:44:06')}

## Cuidado com o sonho antigo

No início de Fash, a sala de paredes móveis é comparada por Firael ao Plano das Sombras. A revelação posterior a situa dentro da experiência de cativeiro e sonho. A comparação de aparência não prova visita material ao plano. {f('F','Fash — 08/08 e 25/10')}; {f('J','Esclarecimentos — Sonho e geografia')}

## Estado e relações

Sem exploração, rota urbana ou ocupação confirmada no corte. A origem da magia de sombras de Fash, Glim ou do Ébano não pode ser deduzida apenas da existência deste destino da torre. {l('Lugares/Plano dos sonhos')} · {l('Itens/Portas de Arkhavel')} · {l('Lugares/Torre de Arkhavel')}.''',[T(26),'F','J'])

nota('Plano dos sonhos','Experiência e mundo dos sonhos',['fash'],f'''## Alcance do nome

Nome de navegação para a experiência onírica de cativeiro de Fash, Firael, Timo e companheiros. Não define um plano cosmológico formal ou todas as regras dos sonhos do cenário. Na suposta saída inicial, uma criatura afirma que entraram pelo plano dos sonhos; em 17/10 e 25/10 Elena revela que nunca haviam saído do cativeiro. O jogador autorizou classificar esse trecho e suas datas como sonho. {f('F','Fash — 23/08, 17/10 e 25/10')}; {f('J','Esclarecimentos — Sonho e geografia')}

## Espaços vividos

Sala escura de paredes móveis, corredor aberto por sangue, espelho emoldurado de restos mortais, altar de três corações e sala de sete portas. Os corações geram combates e itens; o de pedra move o altar para a sala inferior. As provas apresentam contextos de ira, amor, mentira, medo, orgulho e sangue/omissão, enquanto a frase sobre fome não tem prova correspondente descrita. A experiência depois inclui portais, demônio de cinzas, Elena e {l('Lugares/Lazathar')}. {f('F','Fash — 08/08, 16/08, 18/08 e 23/08')}

A investigação urbana, câmara ritual, Caminhante das Sombras e instituições da capital aparente integram as camadas do sonho. Elena cria ainda um espaço de treino antes de acordá-los. Não há mapa com fronteiras estáveis, tempo material correspondente a cada cena ou confirmação dos referentes físicos. {f('H','Handoff — O sonho da campanha de Fash')}; {f('F','Fash — 25/10')}

## Saída e estado

Os personagens despertam na {l('Lugares/Cabana das bruxas')}, levam esfera e livro e fogem pela floresta. Fash afirma que não houve o salto temporal anteriormente acreditado. O propósito dos testes e a quantidade de camadas não são conhecidos. A experiência pode ter efeitos e pistas reais, mas não valida a existência material de suas cidades ou condena pessoas reais por cenas de prova. {f('F','Fash — 25/10')}; {f('J','Esclarecimentos — Sonho e geografia')}

{l('Eventos/Cativeiro e sonho de Fash')} · {P[14]}''',['F','H','J'],natureza='sonho')

nota('Cabana das bruxas','Cabana das bruxas',['fash'],f'''## Identidade e localização

Cabana numa floresta onde o grupo de Fash desperta do cativeiro. A primeira descrição se refere à cabana da bruxa da noite que os sequestrou; o título plural funciona como agrupamento do contexto do {l('Faccoes/Circulo Vetrilus')}, sem provar residência simultânea das três irmãs. Não há coordenada ou nome de floresta. {f('F','Fash — 25/10 e 07/11')}

## Interior e fuga

Elena prepara as crianças para ver corpos de animais e experimentos. Ao acordar, Fash descreve cheiro podre, caos e a esfera amarelada associada a Elena. Leva a esfera, enquanto Firael recolhe o livro de feitiços. A bruxa havia se ausentado; Cogu sente seu cheiro e guia a fuga na direção oposta. Depois de alguns dias, Timo reconhece a região e conduz o grupo ao Forte. {f('F','Fash — 25/10')}

## Relações e estado

O livro posteriormente descreve Morvessh, Selara, Lyvessa e a origem de seu círculo num nodo. Isso não fornece localização do nodo na cabana, nem prova de que seja o mesmo nodo sob ossos dos mapas atuais. O estado da construção, eventual retorno da bruxa e ocupantes posteriores não estão documentados. {f('F','Fash — 07/11')}; {l('Lugares/Fosso de ossos e nodo')}.

{l('Lugares/Plano dos sonhos')} · {l('Itens/Esfera de Elena')} · {l('Itens/Livro das tres bruxas')} · {P[6]}''',['F'])

nota('Aldeia natal de Glim','Aldeia natal de Glim',['glim'],f'''## Lugar e infância

Aldeia de maioria humana no limite da mata, onde Glim e Lilo crescem com os pais. O background a descreve sob perspectiva dos irmãos: trabalho braçal, casas simples e pouco espaço para suas aspirações. A floresta próxima é o lugar de descoberta do grimório e da morte de Lilo; essa proximidade não a identifica como a floresta de Timo ou a comunidade dos rangers de Eral. {f('B','Background — ato 1')}; {f('J','Esclarecimentos — cânone do background sob ponto de vista de Glim')}

## Retorno e ocupação posterior

Glim retorna antes de procurar trabalho na capital. Vê casas reconstruídas às pressas e aldeia mais fechada após os Doze Dias Rubros. Nina informa que o pai dele morreu ao ir ao cemitério e que a mãe continua viva, dependente de cuidados e sem responder. Sua antiga casa está abandonada por dentro, com pertences remanescentes; ele recupera um pente quebrado e fivela de cinto. São lembranças narradas e notícias de Nina no background, não uma visita posterior à campanha atual. {f('B','Background — ato 6')}

## Rotas e estado mais recente

Glim chega pela estrada e sai antes do sol; não há nome formal, coordenada, duração até Carruan ou censo. A aldeia permanece habitada na última visita, e não há atualização posterior confirmada do prédio da família. {f('B','Background — ato 6')}

{l('Eventos/Infancia e ruptura de Glim')} · {l('Itens/Memorias materiais de Glim')} · {P[13]}''',['B','J'])

nota('Muro das Lamentacoes','Muro das Lamentações',['glim'],f'''## Lugar vivido por Okay

Okay encontra-se incorporado a um muro durante {l('Eventos/Experiencia de Okay no amuleto')}. O mestre explica, a partir de conhecimento de religião/planos, que almas sem patrono aceito podem parar ali, inclusive as de quem cultua apenas por conveniência. O muro é feito de almas, presas por fungo que as consome lentamente; um anjo colossal de quatro asas o protege de ladrões de almas. São a cosmologia e a descrição desta mesa, sem complementação de geografia de D&D externa. {f(T(17),'T17 — 00:11:29–00:13:27')}

## Passagem e acontecimentos

Dois barbados tentam retirar uma alma vizinha já consumida demais, devolvem-na e escolhem Okay. Ele não consegue reagir com suas capacidades habituais e aceita ser levado. Saem por um buraco no muro para região associada à Guerra Infinita e descem ao Abismo, atravessando castelos. A narração chama os sequestradores de demônios; não corrigir a taxonomia pela aparência dos barbados. {f(T(17),'T17 — 00:13:27–00:22:03')}

## Natureza e limites

A síntese do handoff registra que pesquisas posteriores corroboram a experiência e o mestre afirma que aquilo é realidade. Ainda assim, o modo de acesso pelo amuleto, morte/renascimento e diferença entre tempo percebido e externo permanece aberto. Não há coordenada ou caminho utilizável a partir de Eral, nem prova de que outras pessoas possam repetir a passagem. {f('H','Handoff — Experiência de Okay no amuleto e planos inferiores')}

{l('Itens/Amuleto de Kord')} · {l('Faccoes/Traficantes planares de almas')}''',[T(17),'H'])

# Extras cartográficos: notas curtas proporcionais à legenda/células.
extras = [
('Kranklefang Lunhollow','Kranklefang Lunhollow — vila dos gnomos','K18','Vila dos Gnomos — Kranklefang Lunhollow','A célula C30 diz Gnomos (K18). O mapa não autoriza identificar todos esses moradores aos “gnomos (pequenos lobos)” mencionados no diário, sem confirmação.',['Kranklefang Lunhollow']),
('Loraeth','Loraeth — vila dos Furion','L28','Vila dos Furion — Loraeth','Há divergência: a célula C34 escreve Furion (K28), mas a legenda visual escreve L28. Preservar L28 como referência da legenda e K28 como referência da célula, sem escolher uma por semelhança.',['Loraeth']),
('Thornaeva','Thornaeva — vila das fadas espinho','M13','Vila das Fadas Espinho — Thornaeva','A célula C36 repete Fadas Espinho (M13). Não há notícia de visita, fronteira ou ocupação atual da vila.',['Thornaeva']),
('Thael V oren','Thael`Voren — vila das fadas','R20','Vila das Fadas — Thael`Voren','C38:C41 associa Fadas Pixie (R20), Cavaleiro da Morte selado, selo enfraquecendo/corrompendo a terra e Trent Ancião Corrompido como possível informante. A lista é pista de interesse, não relato de desfecho.',['Thael`Voren']),
('Vael Tharion','Vael`Tharion — vila dos centauros','X12','Vila dos Centauros — Vael`Tharion','C42:D44 registra Centauros (X12), Dragonetes da Fúria e Esmagador Encouraçado. Não estabelece que esses seres residam todos na vila ou que sejam adversários dela.',['Vael`Tharion']),
('Syltha Vaelor','Syltha Vaelor — vila das dríades','AC10','Vila das Dríades — Syltha Vaelor','C45 também registra Dríades (AC10). Não identificar com o santuário da portadora do cajado apenas pela espécie.',['Syltha Vaelor']),
('Conclave da Raiz Ancestral','Conclave da Raiz Ancestral — T23','T23','Conclave da Raiz Ancestral','B29 e a legenda confirmam o nome e a coordenada. Não há prova de equivalência ao Conclave dos rangers de Eral ou ao Círculo Vetrilus.',['Conclave da Raiz Ancestral']),
]
for slug,titulo,coord,legenda,obs,aliases in extras:
    nota(slug,titulo,['fash'],f'''## Registro cartográfico

Ponto **{coord}** na legenda visual incorporada à aba INTERESSES da planilha de Fash: “{legenda}”. A imagem e a transcrição foram conferidas diretamente. {f(XI,'INTERESSES — legenda incorporada')}

{obs} {f(XI,'INTERESSES — células e legenda')}

## Limites e estado

Nome e ocupação nominal são os dados recuperáveis. Não há censo, dirigente, duração de viagem, escala de mapa ou atualização contemporânea de Glim. Coordenadas indicam quadrícula do mapa; não são latitude/longitude. Ver {l('Lugares/Cartografia regional de Fash')} e {P[5] if slug=='Loraeth' else P[16] if slug=='Conclave da Raiz Ancestral' else P[10] if slug=='Syltha Vaelor' else P[4]}.
''',[XI],aliases=aliases,extra=True)

nota('Ruinas do mapa de Fash','Ruínas do mapa de Fash',['fash'],f'''## Pontos documentados

A legenda visual de INTERESSES identifica **Ruína 1 — Q27**, **Ruína 2 — W23** e **Ruína 3 — J25**. As células são menos específicas: C81 marca “? (Q27)”, C79 “Floresta do Timo (W23)” e C80 “Embaixo do Rio (J25)”. A imagem cartográfica mostra o rio na região de J25, mas não fornece planta subterrânea. {f(XI,'INTERESSES — B78:C81, mapa e legenda')}

## Limites de interpretação

Conservar a possibilidade de ruínas inseridas nas áreas citadas, sem tratar isso como identidade resolvida. Não se conhece origem, data, construtores, ocupantes atuais ou ligação entre as três ruínas. A árvore negra AC34 é outro marcador e não quarta ruína demonstrada. Não há escala para calcular distância ou tempo de deslocamento. {f(XI,'INTERESSES — células e legenda')}

{l('Lugares/Floresta de Timo')} · {l('Lugares/Cartografia regional de Fash')} · {P[5]}''',[XI],extra=True)

nota('Covil do dragao negro','Covil do dragão negro da região de P22',['fash','glim'],f'''## Localidade e distinção

Presença subterrânea ligada à {l('Lugares/Cidade drow','região de P22')}, aos trolls e ao fim da campanha antiga. A planilha registra “Subterrâneo: Dragão Negro” e “100 peças de ouro por mês”, sem esclarecer completamente a obrigação ou localização do covil. Não há coordenada própria ou planta. {f(XI,'INTERESSES — C60:D61')}

## Acontecimentos e estado recente

O jogador confirma que Fash e Kael entregaram Firael vivo ao dragão. O mestre confirma depois que Kael foi capturado, torturado e comido e que Firael sobreviveu por acordo. Na S25, mapas atuais descrevem dragão negro, trolls, experimentos e devastação na antiga região drow. O livro da bruxa pertence ao dragão, mas o nodo oculto é desconhecido dele. {f('J','Esclarecimentos — Desfecho não registrado')}; {f(T(25),'T25 — 01:28:35; 01:34:26–01:39:15')}; {f('G','Glim — S25')}

Esta localidade não é o {l('Lugares/Covil maritimo')}, cujo dragão não foi identificado. A história material não fornece censo de trolls, fronteiras de domínio ou destino dos moradores reassentados por Fash. {l('Personagens/Dragao negro')} · {P[4]}''',[XI,'J',T(25),'G'],extra=True)

nota('Cartografia regional de Fash','Cartografia regional de Fash',['fash'],f'''## Fonte, leitura e alcance

Inventário dos pontos efetivamente presentes nas células e nas duas imagens incorporadas à aba INTERESSES de Fash. O mapa tem grade alfanumérica, rio, floresta e costa; a legenda é a referência nominal. Não fornece escala métrica nem tempo de viagem. A ordem de letras exibida deve ser preservada, sem reconstruir distâncias por uma planilha moderna. As coordenadas abaixo são quadrículas do desenho, não endereços de célula do XLSX. {f(XI,'INTERESSES — mapa image2.png e legenda image1.png')}

## Povoações e locais com nota própria

| Ponto | Registro |
| --- | --- |
| P22 | {l('Lugares/Cidade drow')} |
| Q23 | {l('Lugares/Throden','Forte — Vytharix Throdenaar')} |
| U27 | {l('Lugares/Vila dos meio-dragoes','Darastrix Vurix')} |
| K18 | {l('Lugares/Kranklefang Lunhollow')} |
| L28 / K28 | {l('Lugares/Loraeth')} — legenda / célula C34 divergentes |
| M13 | {l('Lugares/Thornaeva')} |
| R20 | {l('Lugares/Thael V oren','Thael`Voren')} |
| X12 | {l('Lugares/Vael Tharion','Vael`Tharion')} |
| AC10 | {l('Lugares/Syltha Vaelor')} |
| T23 | {l('Lugares/Conclave da Raiz Ancestral')} |
| H20 | {l('Lugares/Necropole')} — coordenada só da célula C26 |
| Q27, W23, J25 | {l('Lugares/Ruinas do mapa de Fash')} |

Fonte integral da tabela: {f(XI,'INTERESSES — células e legenda visual')}.

## Outros marcadores preservados

| Quadrícula | Conteúdo da fonte e limite |
| --- | --- |
| H19 | Equicep; células D6:D7 dizem que compram escravos e possuem alguns do povo lagarto. |
| Q31 | Povo Lagarto / Lagartos Negros; D9 registra pedido de ajuda contra ogros e Equiceps. |
| S18 | Vila Murgul, sem outro detalhe. |
| M22 | Criatura com símbolo da bruxa em direção a P22; é ocorrência de trajeto, não cidade. |
| O20 | Saída subterrânea — crias dracônicas; C70 especifica dragão das profundezas. |
| O24 | Pantera espectral, somente na legenda. |
| P25 | Nyth parecido com fogo-fátuo; a célula diz que os mestiços não conseguem eliminá-lo. |
| R27 | Periton, águia com cabeça de cervo. |
| Y31 | Bocarra. |
| AC34 | Árvore negra. |
| AD17 | Híbridos gorila/aranha; D17 anota quarenta indivíduos. |
| AN10 | Pterapovo na legenda / Pteropovo na célula C18; D19 diz não ter atuação na terra. |
| AN23 | Farol, só a legenda fornece nome. |
| AP29 | Criatura peluda/forte do olho verde; D21:D22 registra emboscada e roubo sem objetivo de matar e cinquenta indivíduos. |

Os dados são apontamentos antigos, sem atualização de ocupação atual ou autorização para atribuir todos os números a uma espécie definida. Fonte da tabela: {f(XI,'INTERESSES — C3:D22 e legenda')}.

## Subterrâneo e referências sem coordenada própria

A lista registra gnomos, trolls, orcs, duergars, quitina/“Quitiina” ladina criada por drow, aracnídeos de vários tamanhos com veneno variável e beholder. Os números de Knowledge/ND são mecânica anotada, não população. Caminhos do fosso e dos trolls aparecem sob P22, mas não constituem mapa completo de túneis. Os covis de Haurim são anotados como duas montanhas ao sul. {f(XI,'INTERESSES — C53:C83')}

## Divergências abertas

A planilha contém **cinco rótulos de portais, mas dois estão riscados**: C51 ~~Cabeça de Gigante~~ e C52 ~~4 Costelas Grandes~~. C48 Abismo, C49 Mundo Espelhado e C50 Ilha dos Elfos da Noite são os **três sem rasura**. A conferência direta dos estilos OOXML do XLSX original confirma `font.strike=true` apenas em C51:C52; a conversão Markdown inicial omitiu esse estilo. Assim, os três portais do diário e os cinco rótulos totais não constituem uma divergência automática de contagem. Rasura não comprova eliminação física: continuam abertas sua data e significado e a correspondência entre os três nomes sem risco e os três portais narrados. {f(XI,'INTERESSES — C48:C52 e estilos do XLSX original')}; {f('F','Fash — 29/01')}

Também permanecem W23 como floresta/ruína e K28/L28 para Furion/Loraeth. As notas preservam diferenças de documento e de época. Não foi usado mapa de outros cenários para preencher lacunas. {P[5]}''',[XI,'F'],extra=True)

for ref in referencias_oniricas():
    nota(ref['slug'],ref['titulo'],['fash'],ref['texto'],ref['fontes'],extra=True,natureza='referencia_background_sonho')

registro=json.loads((ROOT/'docs/enciclopedia/registro-entidades.json').read_text(encoding='utf-8'))
esperados=[e for e in registro['entidades'] if e['dominio']=='lugares']
paths={n['caminho'].removesuffix('.md') for n in notas}
faltantes=[e['destino'] for e in esperados if e['destino'] not in paths]
if faltantes: raise RuntimeError(f'Cobertura incompleta: {faltantes}')

manifesto={
    'dominio':'lugares','data':'2026-10-29','status':'congelado_aguardando_integracao',
    'cobertura':{'previstos':len(esperados),'cobertos':len(esperados)-len(faltantes),'faltantes':faltantes,'extras':sum(n['extra'] for n in notas)},
    'notas':notas,'pendencias':perguntas,
    'fontes_efetivamente_consultadas':[
        {'caminho':FONTES['H']+'.md','alcance':'seções completas de geografia, campanha antiga, portas, cosmologia e sonho; consultas adicionais a relações, consequências e mistérios'},
        {'caminho':FONTES['J']+'.md','alcance':'integral'},
        {'caminho':FONTES['F']+'.md','alcance':'entradas Dia 45 e solo dos 45 dias; 08/02; 29/01; 25/01; 22/01; 30/10; 31/10; 07/11; 24/11; 28/11; 01/12; 02/12 solo; 25/10 e saída; provas 08/08 a 23/08; confronto/retorno 17/10; 11/09, notícias de Teladelion e BACKGROUND'},
        {'caminho':FA+'.md','alcance':'integral; nota expressamente marcada revisar_continuidade, usada com ressalva para Eldrosia e Thal Karak'},
        {'caminho':FONTES['G']+'.md','alcance':'S1 integral; trechos pertinentes S4, S8–S10, S13–S14, S18–S20, S25–S26; buscas temáticas em restante'},
        {'caminho':FONTES['B']+'.md','alcance':'abertura/ato 1 e retorno à aldeia/ato 6; busca temática de localidade'},
        {'caminho':XI+'.md','alcance':'integral, incluindo transcrição de legenda; ambas imagens verificadas visualmente'},
        {'caminho':'arquivo/originais/BASE INICIAL/FASH PALESKIN.xlsx','raiz':'workspace','alcance':'auditoria posterior: leitura direta de sheet3.xml e styles.xml do XLSX; C48:C50 sem rasura, C51:C52 font.strike=true'},
        {'caminho':XA+'.md','alcance':'integral'},
        {'caminho':FONTES['XF']+'.md','alcance':'índice das abas e inventário de imagens'},
        {'caminho':FONTES['XG']+'.md','alcance':'índice das abas e inventário de imagens; sem mapa geográfico ali listado'},
        *[{'caminho':T(n)+'.md','alcance':a} for n,a in [
            (13,'01:12:10–01:12:47 e busca temática comunidade'),(14,'parte 1: 01:16:26–01:18:53, clones e espaços'),
            (17,'00:11:29–00:30:30, especialmente Muro e saída ao Abismo'),
            (19,'00:23:31–00:27:33 censo corrigido; trechos 00:32–00:43 buraco; 00:58:47 posto/colônia'),
            (20,'00:21:38–00:38:56 cidade, loja, negociação'),
            (23,'01:07:13–01:08:44 região; 01:47:37 terreno; 02:12:00–02:13:36 ocupação; buscas na sequência final'),
            (24,'02:08:41–02:13:37 covil e expedições'),
            (25,'00:46:15–00:47:55 mortos-vivos; 01:25:43–01:28:35 mapas e santuários; 01:34:26–01:45:03 memória; 01:57:28–01:59:24 rota; buscas adicionais'),
            (26,'00:51:02–00:55:39 mecanismos e cascas; 02:43:10–02:44:06 destinos; 02:50:01 encerramento')]],
        {'caminho':'Anexos/planilhas/fash-paleskin/ooxml/xl/media/image1.png','alcance':'visual integral; legenda nominal e coordenadas'},
        {'caminho':'Anexos/planilhas/fash-paleskin/ooxml/xl/media/image2.png','alcance':'visual integral; grade, rio, costa e símbolos; sem inferência métrica'},
    ],
    'ajustes_de_auditoria':[
        {'data':'2026-10-29','registro':'docs/auditoria-exclusao/ajuste-cartografia.json','assunto':'Rasura dos rótulos de portais em INTERESSES C51:C52','conclusao':'Cinco rótulos totais: três sem rasura e dois riscados. Não há contradição automática de contagem nem prova de eliminação física de portais; LG-005 conserva dúvidas de significado, época, correspondência e coordenadas.'}
    ],
    'limites':[
        'Nenhuma fonte, anexo, sessão, índice, arquivo original ou cadastro comum foi modificado por este script.',
        'Pesquisa seletiva; consultar transcrição em trecho não equivale a auditar integralmente toda a sessão.',
        'Diário PRONTO mencionado no handoff não está convertido como fonte própria consultada; coordenadas P22/Q23/U27 foram conferidas na planilha e imagens locais.',
        'Afirmações conhecidas apenas pelo handoff são marcadas como síntese e citam H, sem alegar consulta às transcrições ali referidas.',
        'As imagens da planilha Glim listadas são da aba de formas, não mapas geográficos; inventário consultado sem alegar inspeção visual dessas imagens.',
        'Nenhum nome oficial de mundo/reino é inferido de Eldrosia ou Auria; nenhuma geografia externa de D&D foi importada.',
        'Sem censo atual de Throden/P22/U27, escala métrica do mapa antigo ou identificação segura entre nodos, necrópole e cordilheira atual.',
        'LG-005 trata nomenclatura e cartografia de portais antigos; a divergência de funcionamento das portas de Arkhavel fica com o integrador/Itens.',
    ]
}
(ROOT/'docs/enciclopedia/lugares.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'notas':len(notas),'base':len(esperados),'extras':sum(n['extra'] for n in notas),'pendencias':len(perguntas),'faltantes':faltantes},ensure_ascii=False))
