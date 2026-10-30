"""Consolidação editorial de acontecimentos, artefatos e cronologia."""
from pathlib import Path
import hashlib
import json
import re
from enciclopedia_comum import ROOT, CONTEUDO, FONTES, escrever, pendencia, fonte, link

REG = json.loads((ROOT/'docs/enciclopedia/registro-entidades.json').read_text(encoding='utf-8'))['entidades']
DEST = {r['destino'].split('/')[-1]:r['destino'] for r in REG}


def expand(s):
    def sub(m):
        key, _, label = m[1].partition('|')
        return link(DEST[key], label or key)
    return re.sub(r'@\{([^}]+)\}',sub,s)


def ref(code, label=None, sec=None):
    return fonte(code,label,sec)


H = ref('H','Síntese do handoff')
J = ref('J','Esclarecimentos do jogador, 23/10')
B = ref('B','Background de Glim')
F = ref('F','Diário de Fash')
QUESTIONS = []
QP = {}


def q(code,title,category,ask,context,sources,entities,priority='media',nature='lacuna'):
    shared = {'EV-001','EV-002','EV-003','EV-006','EV-007','IT-002','IT-007','CR-001'}
    path = pendencia(code,title,category,['fash','glim'] if code in shared else ['glim'],
                      ask,expand(context),sources,[DEST.get(x,x) for x in entities],priority,nature)
    QP[code]=path
    QUESTIONS.append(path+'.md')


q('EV-001','Sequência da transição entre as duas campanhas','Eventos',
  'Em que ordem ocorreram a fuga de Fash, as mortes de Kael e Timo, a fundação das facções e a Noite Eterna, e quais intervalos são conhecidos?',
  'A continuidade de Fash/Glim e o intervalo de 70 anos estão estabelecidos. A ordem fina dos acontecimentos entre as mesas não está reconstruída. O handoff apresenta uma sequência geral, não um calendário completo. Não é necessário confirmar novamente Kael/Okay ou Ébano/Sociedade das Sombras.',
  ['H','J','T25'],['Morte de Kael','Duelo e entrega de Firael','Noite Eterna'],'alta','cronologia')
q('EV-002','Desfecho da epidemia das criaturas de luz','Eventos',
  'O que aconteceu aos atingidos pela destruição da esfera de Elena e até onde a transformação em criaturas de luz se espalhou?',
  'O diário registra o líder do Forte, cavalos, clérigo e animais atingidos. Em T25, 01:05:44, o mestre corrige a versão pública: destruir o artefato provocou a epidemia. O desfecho dos atingidos e a extensão final não foram recuperados.',
  ['F','H','T25'],['Destruicao da esfera de Elena','Esfera de Elena'],'alta','consequencia')
q('EV-003','Propósito e correspondências do sonho antigo','Eventos',
  'Qual era o propósito das camadas e provas do sonho e quais pessoas, instituições ou lugares nele apresentados correspondiam ao mundo material?',
  'O despertar de 25/10 muda a interpretação de toda a etapa de Lazathar. O diário preserva testes, investigações e personagens dessa experiência. A autorização para tratar o trecho como sonho não resolve suas correspondências ou a intenção das provas.',
  ['F','J','H'],['Cativeiro e sonho de Fash','Plano dos sonhos','Mascara dos testes'],'alta','continuidade')
q('EV-004','Resgatados e consequências da crise dos reféns','Eventos',
  'Qual foi o destino dos humanos libertados e qual é o balanço final do resgate nas cavernas, distinguindo os grupos salvos dos quinze reféns mortos?',
  'Os registros falam em cerca de 42 humanos libertados e a recapitulação de S23 fixa quinze reféns mortos nos setores não salvos. Esses números se referem a momentos e conjuntos distintos; não devem ser somados como um único censo sem confirmação.',
  ['H','T22','T23'],['Crise dos refens','Assentamento goblinoide'],'alta','consequencia')
q('EV-005','Sobreviventes da aldeia na neve','Eventos',
  'Quantos fugitivos sobreviveram ao ataque dos yetis e qual foi o destino posterior da criança salva por Okay e do sacerdote retirado pela figura do prelúdio?',
  'T23 confirma que Okay foge com a criança, que nem todos morreram e que a figura retira o sacerdote vivo. Não fornece um total final. A identidade da figura e o resultado posterior da tarefa de Tariun são questões relacionadas, mas não tornam conhecido esse balanço.',
  ['H','T23','T24'],['Provacoes de Kord','Aldeia ocupada na neve'],'alta','consequencia')
q('EV-006','Início e encerramento da Noite Eterna','Eventos',
  'Que ato desencadeou a Noite Eterna e como a crise foi encerrada, além do que os personagens presenciaram e do papel atribuído à Lua Sangrenta?',
  'Os esclarecimentos ligam a crise à bruxa e à continuação da campanha antiga. O background registra mortos levantando, destruição do circo e a morte do pai de Glim. Ainda falta uma descrição do desencadeamento e do encerramento; o nome Doze Dias Rubros sozinho não fixa todas as fases.',
  ['J','B','H','T24'],['Noite Eterna','Queda da Roda de Estopa'],'alta','causalidade')
q('EV-007','Identidade e cronologia das revoadas','Eventos',
  'A Revoada Branca e a revoada ligada à morte de Hourian/Haurim foram o mesmo acontecimento ou eventos diferentes, e quais datas e participantes são conhecidos?',
  'T23 menciona uma Revoada Branca em off, como informação de outra mesa. O handoff também preserva uma revoada ligada a Hourian/Haurim. Não há base para fundir automaticamente essas referências, muito menos identificá-las com a Noite Eterna.',
  ['H','T23'],['Revoada Branca','Hourian Haurim','Regiao gelada'],'media','identidade')
q('EV-008','Conclusão do caso da água envenenada','Eventos',
  'A origem do envenenamento da água de Eral foi descoberta e o problema chegou a ser resolvido?',
  'Os diários e investigações levantam suspeitas sobre a região dos Crepúsculos Venenosos, mas a escala da contaminação põe essa hipótese em dúvida. A resolução do caso não está registrada no recorte consolidado.',
  ['H','G'],['Caso das criancas','Eral','Crepusculos Venenosos'],'media','missao_aberta')
q('IT-001','Entidade e selo do grimório','Itens',
  'O que é a entidade ou presença do grimório, qual a função do selo rompido na infância e qual era sua relação com a sombra que matou Lilo e Piche?',
  'O background apresenta a ruptura e as mortes sob a perspectiva de Glim. As análises mostram energia excepcional e o livro produz mensagens; nenhuma dessas observações identifica sua natureza última ou torna todas as visões confiáveis.',
  ['B','H','J','T17','T24'],['Grimorio de Glim','Infancia e ruptura de Glim'],'alta','identidade')
q('IT-002','Diferenças entre os livros das bruxas','Itens',
  'Quais são os nomes, conteúdos, autores e relações entre o livro recuperado ou compilado na campanha antiga, sua cópia nos pergaminhos e o volume mais poderoso do dragão negro?',
  'T25, 00:12:11–00:13:06, distingue a cópia em papiros do livro que permanece com o dragão. O diário e o handoff também mencionam material de Morvessh e das três irmãs. A relação documental precisa de confirmação antes de fundir volumes.',
  ['F','H','T25'],['Livro das tres bruxas','Livro do dragao negro','Mapas e pergaminhos de Firael'],'alta','identidade')
q('IT-003','Natureza e funcionamento do amuleto de Kord','Itens',
  'Como se relacionam a origem do amuleto, a tradição de avatar relatada por Tólomon e a experiência planar de Okay, e quais poderes adicionais foram efetivamente liberados?',
  'A entrega por Rudiger, o uso por Crave e o ganho de Força estão registrados. A história do avatar é relato de Tólomon; a sequência vivida por Okay foi validada em mesa como realidade, mas a ligação completa com o objeto continua aberta.',
  ['H','T17','T23'],['Amuleto de Kord','Experiencia de Okay no amuleto'],'alta','mecanismo')
q('IT-004','Estado e regras restantes do cinto de Kord','Itens',
  'Quem ficou com o cinto depois do rito e quais condições seriam necessárias para recuperá-lo ou concluir a obrigação associada a ele?',
  'O rito começa com dez campeões e Crave retorna do torneio sem o cinto. O handoff distingue o resultado pessoal do torneio da recuperação do artefato. Não há localização posterior confirmada do item.',
  ['H','T23','T24'],['Cinto de Kord','Provacoes de Kord'],'media','posse')
q('IT-005','Fechar e reabrir as portas planares','Itens',
  'Em quais condições uma porta de Arkhavel pode ser fechada e reaberta, e quando deixá-la aberta é necessário para garantir o retorno?',
  'S14 admite fechar e reabrir uma porta ativa; S19 mostra uma porta que desaparece ao fechar e pode ser reaberta por quem conhece sua posição; S25 orienta mantê-la aberta. Podem existir condições diferentes, mas elas não foram conciliadas. Redirecionar uma porta e deslocar o interior da torre são mecanismos distintos.',
  ['H','T14','T19','T25','T26'],['Portas de Arkhavel','Torre de Arkhavel'],'alta','contradicao')
q('IT-006','Origem e limites ainda abertos do Fogo Primordial','Itens',
  'Quem concedeu ou produziu o Fogo Primordial de Okay e quais condições limitam sua evolução além das funções já explicadas na sessão 24?',
  'A mesa chama o fogo de habilidade extraordinária, compara-o a exemplos de outro plano e sugere que Arkhavel sabe criá-lo. A analogia com Mystra não identifica uma patrona. As regras já explicadas de preparação, absorção e impossibilidade de absorver a própria magia devem permanecer registradas, sem perguntar de novo o que a fonte já responde.',
  ['H','T24'],['Fogo Primordial','Despertar do Fogo Primordial'],'alta','origem')
q('IT-007','Consciência e poderes do cajado de girassol','Itens',
  'Que consciência de Timo permanece no cajado de girassol e quais poderes e limites do artefato foram confirmados, além de estimular a vegetação e reverter a corrupção?',
  'J confirma Timo/planta/cajado e distingue a dríade portadora. Os relatos dos arquivistas descrevem a transformação ambiental. O processo de morte e transformação pertence também à história de Timo; esta pergunta se concentra no estado e nas capacidades atuais do artefato.',
  ['J','H','T25'],['Cajado de girassol','Santuario da driade'],'media','mecanismo')
q('IT-008','Dados dos artefatos investigados pelos arquivistas','Itens',
  'Quais nomes, localidades e desfechos foram confirmados para o totem roubado e o caso de transformação coletiva associado a um possível artefato?',
  'As informações chegam como relatos de pesquisadores, sem apresentação direta dos objetos. O catálogo deve distinguir o totem mencionado como objeto de um artefato apenas hipotético para explicar a transformação coletiva.',
  ['H','T25'],['Artefatos investigados pelos arquivistas','Arquivistas'],'media','investigacao')
q('CR-001','Calendário material do cenário','Cronologia',
  'Qual é o calendário material e o ano atual do cenário, e quais datas antigas de Fash pertencem ao mundo desperto?',
  'O intervalo de 70 anos é referência de continuidade. O diário antigo contém datas de sonho e referências conflitantes; somar 70 a uma data onírica não determina o presente. Os esclarecimentos autorizam manter esse trecho como sonho.',
  ['F','H','J'],['Cronologia/Fash e Glim','Cativeiro e sonho de Fash'],'alta','calendario')
q('CR-002','Dias transcorridos nas sessões vinte a vinte e seis','Cronologia',
  'Quais descansos, deslocamentos e intervalos planares das sessões 20–26 permitem atualizar a contagem de dias desde a caravana?',
  'A cronologia herdada estima cerca de 55 dias até a sessão 19. S26 acrescenta aproximadamente três dias de preparação, mas não preenche os intervalos anteriores. Meses subjetivos em provações e o mês de viagem ainda planejado não são automaticamente tempo transcorrido no Material.',
  ['C','H','T24','T25','T26'],['Cronologia/Glim Sombrasselva','Preparativos da torre'],'media','cronologia')

EVENTS = [
('Aprisionamento do Cerebro', ['fash','glim'],
 'Antiga crise regional que explica a prisão do @{Cerebro Anciao|Cérebro Ancião} e a condição do @{Druida Sangrento}. A narrativa é recuperada por documentos e relatos da campanha de Fash, não por uma cena presenciada do passado remoto.',
 'Quatro povos — humanos, anões, drow e uma raça extraplanar não identificada — aprisionaram o Cérebro. O acordo de jogos oferecia conhecimento em troca do risco de enfraquecer o selo quando se perdia. O diário atribui à exploração desse saber uma parte da decadência que antecedeu a guerra.\n\nOs humanos foram derrotados; drow à beira da derrota pactuaram com @{Lolth}. As civilizações anã e drow foram destruídas e o Druida Sangrento permaneceu como guardião amaldiçoado. O anão que o acompanhava era coagido pela escravização de sua família, em vez de ser um guardião contínuo equivalente.',
 'O mecanismo dos jogos dá contexto às decisões de @{Firael}, mas sua relação presente com o Cérebro não demonstra quando ou se a prisão material foi rompida. A identidade da quarta raça e a data da guerra permanecem desconhecidas.',
 ['Cerebro Anciao','Druida Sangrento','Cidade drow','Anoes libertos'], ['H'], ['CR-001']),
('Cativeiro e sonho de Fash',['fash'],
 'A campanha antiga registra uma experiência em camadas de cativeiro, provas e investigação. A revelação de 25/10 muda a interpretação do trecho de @{Lazathar}: os personagens ainda estavam num mundo de sonho.',
 'Os testes envolvem paredes móveis, espelho de ossos, três corações e uma máscara. Há registro de portas ligadas a ira, amor, mentira, medo, orgulho e sangue/omissão; Fome aparece como rótulo sem prova correspondente descrita nessa sequência. As recompensas e mudanças da máscara fazem parte da experiência vivida, sem comprovar efeitos permanentes no Material.\n\nA aparente saída leva a Lazathar, investigação de corpos com runas e confronto entre instituições. @{Elena} revela que o grupo nunca saíra do cativeiro. Seu artefato é associado à criação desses mundos. Os esclarecimentos do jogador autorizam manter todo esse trecho como sonho, preservando pistas e símbolos.',
 'Nomes, datas e instituições oníricas não são automaticamente transferidos para a história material. A experiência é real como vivência dos personagens; suas correspondências com pessoas e lugares externos ainda dependem de esclarecimento.',
 ['Fash Paleskin','Timo','Firael','Elena','Plano dos sonhos','Mascara dos testes'], ['H','J'], ['EV-003','CR-001']),
('Destruicao da esfera de Elena',['fash','glim'],
 'Destruição do artefato de sonhos associado a @{Elena}, seguida por um fenômeno luminoso que o mundo atual recorda como epidemia.',
 'Na síntese dos diários antigos, o líder do @{Throden|Forte} se oferece para destruir a esfera perto da caverna drow. Surgem pilar de luz, forma translúcida de dragão e figura encapuzada com símbolos zodiacais. Líder e cavalo ficam imóveis, de olhos brancos. Matar o cavalo provoca outra explosão, atingindo o clérigo e o cavalo de Firael; animais semelhantes aparecem depois na região.\n\nEm T25, 01:05:44, o mestre corrige a história relatada pelos pesquisadores: a destruição do artefato **criou** a epidemia; a versão corrente dizia que o artefato fora destruído para encerrá-la.',
 'Registrar a versão pública e a correção em off preserva uma divergência interna do mundo. A figura zodiacal não recebeu identidade confirmada; o desfecho dos atingidos não foi recuperado. Não há confirmação de que essa epidemia seja a @{Noite Eterna}.',
 ['Esfera de Elena','Elena','Zodiacos','Throden'], ['H','T25'], ['EV-002']),
('Queda do Druida Sangrento',['fash'],
 'A derrota do carcereiro drow rompe o domínio imediato sobre os anões e permite ao grupo antigo ocupar a cidade subterrânea.',
 'O handoff reúne a campanha contra defesas com zumbis venenosos, aranhas balistas, golems e disfarces. Setenta guerreiros do Forte avançam pela entrada principal enquanto o grupo procura outra passagem, mas todos morrem no cerco de zumbis enterrados. Em outro confronto, @{Rake} morre quando chega com @{Timo}, enquanto Firael estava fechado com o Cérebro.\n\n@{Kael} desfere o golpe fatal no @{Druida Sangrento}; Firael o decapita. A autoridade das @{Coleiras drow} passa ao assassino após 24 horas, e Kael a utiliza para libertar os anões.',
 'A libertação e o reassentamento são consequências documentadas. A morte do drow não equivale a uma descrição do rompimento da prisão do Cérebro; esses fatos devem continuar separados.',
 ['Kael','Firael','Timo','Rake','Cidade drow','Reassentamento em Throden'], ['H'], []),
('Reassentamento em Throden',['fash'],
 'Reorganização das populações humanas, anãs e meio-dragônicas após a queda do Druida Sangrento.',
 'Os humanos do Forte passam a planejar e executar a migração para a @{Cidade drow}. Os anões libertos, todos descritos como nascidos em escravidão, preservavam sua cultura apesar dessa condição. Meio-dragões assumem proteção remunerada e gradualmente ocupam o antigo Forte, chamado de @{Throden}.\n\nA organização do novo assentamento inclui defesa, casas, passagens e acordos regionais. A cobrança dos trolls e a presença do dragão negro continuam condicionando a segurança: tomar a cidade não elimina essas dependências.',
 'As coordenadas Q23 e U27 distinguem o Forte da vila de origem dos meio-dragões. A situação setenta anos depois não pode ser inferida apenas desse acordo antigo.',
 ['Throden','Cidade drow','Vila dos meio-dragoes','Meio-dragoes de Throden','Anoes libertos'], ['H','XF'], []),
('Duelo e entrega de Firael',['fash','glim'],
 'Ruptura final do grupo antigo em torno da convocação dos trolls, do vínculo de Firael com o Cérebro e de sua entrega ao dragão negro.',
 'O diário termina na preparação: um emissário troll exige campeão e Fash consegue sete dias. O desfecho é complementado pelos esclarecimentos do jogador: @{Firael} fica gravemente ferido no duelo; @{Fash Paleskin|Fash} e @{Kael} o entregam vivo ao @{Dragao negro|dragão negro}.\n\nT25 confirma em off que Firael sobrevive, negocia e mantém sua relação com o Cérebro. O medo do dragão diante dessa influência favorece o acordo. A tentativa de roubar seu livro também é explicada na mesa; não foi uma execução bem-sucedida de Firael.',
 'Fash e Kael tentam fugir separados, abrindo caminho para a morte de Kael e as organizações do presente. O desfecho não deve ser atribuído ao diário antigo como se estivesse escrito nele: as fontes complementares são essenciais.',
 ['Fash Paleskin','Kael','Firael','Dragao negro','Cidade ana dos trolls','Livro do dragao negro'], ['J','H','T25'], ['EV-001']),
('Morte de Kael',['fash','glim'],
 'A morte de Kael pelo dragão negro conecta o encerramento da campanha antiga às memórias recuperadas por Okay.',
 'Em T25, 01:34:26–01:39:15, o mestre explica que Fash e Kael se separam na fuga, Kael é capturado, torturado e morto pelo dragão. A hipótese de Firael ter consumido seu cérebro é negada na mesa.\n\nOs esclarecimentos do jogador confirmam que @{Okay dBoa|Okay} é a reencarnação de @{Kael}. A recuperação não devolve automaticamente todas as vidas anteriores, nem todo o conhecimento que Kael já recuperara numa outra vida.',
 'A identidade entre as encarnações é confirmação existente. O caminho intermediário de reencarnação, a sequência fina com os demais eventos antigos e as memórias ainda inacessíveis permanecem abertos.',
 ['Kael','Okay dBoa','Fash Paleskin','Dragao negro','Memorias de Kael'], ['J','T25','H'], ['EV-001']),
('Noite Eterna',['fash','glim'],
 'Noite Eterna e Doze Dias Rubros são nomes do mesmo acontecimento, conforme confirmação do jogador. A crise está ligada à continuação da campanha de Fash e antecede a campanha atual.',
 'Os esclarecimentos atribuem a crise à bruxa e aos acontecimentos da campanha antiga, sem recuperar a continuação completa conduzida pelo mestre. O background de Glim registra mortos se levantando, a destruição da @{Roda de Estopa} e a perda de seu pai.\n\n@{Lua Sangrenta} é a organização dos que enfrentaram essa crise, não um terceiro nome confirmado do fenômeno lunar. O intervalo de 70 anos entre as épocas é uma referência do jogador; não permite fixar o ano atual a partir de datas do sonho.',
 'O relato de um pesquisador sobre ausência de avatares desde a crise permanece relato e hipótese cosmológica. Não demonstra sozinho que manifestações privadas ou sonhos de divindades sejam impossíveis.',
 ['Lua Sangrenta','Queda da Roda de Estopa','Glim Sombrasselva','Fash Paleskin'], ['J','H','B'], ['EV-001','EV-006','CR-001']),
('Infancia e ruptura de Glim',['glim'],
 'Origem da ligação de Glim com o grimório e da perda de seu irmão e do corvo. O background foi aprovado sob a perspectiva de Glim.',
 'Glim e @{Lilo Sombrasselva|Lilo} encontram o livro na mata próxima à aldeia humana. Lilo o incentiva com a frase “Se você acredita, é real”. Ao tentar um efeito maior, Glim rompe algo semelhante a um selo; uma sombra mata Lilo e @{Piche}.\n\nGlim retorna sozinho, sofre rejeição e foge levando o grimório e o corpo do corvo. O texto preserva culpa, memória e interpretação do personagem; não identifica por isso a intenção última da presença do livro.',
 'O vínculo com Lilo reaparece nas provações e na manifestação do familiar. Esses acontecimentos posteriores não comprovam uma ressurreição completa ou que todas as visões reconstituam a história com fidelidade.',
 ['Glim Sombrasselva','Lilo Sombrasselva','Piche','Grimorio de Glim','Aldeia natal de Glim'], ['B','J','H'], ['IT-001']),
('Queda da Roda de Estopa',['glim'],
 'Destruição do circo que acolheu Glim, vivida por ele no contexto dos Doze Dias Rubros.',
 'A Roda de Estopa oferece trabalho e convivência com @{Brakka Pedramansa}, @{Dornal}, @{Harlom Vinte-E-Dois}, @{Rumo} e @{Miri}. O background os apresenta como vínculos de uma vida anterior à campanha atual.\n\nNa crise dos mortos, Glim perde o circo e Brakka. A narrativa não descreve um destino individual seguro para cada membro da trupe; a destruição do lugar não é prova de morte de todos.',
 'O pingente de Brakka passa a integrar os memoriais pessoais de Glim. A identidade deste circo não deve ser confundida com a instituição chamada Circo na experiência de Lazathar da campanha de Fash.',
 ['Roda de Estopa','Brakka Pedramansa','Noite Eterna','Memorias materiais de Glim'], ['B','H'], ['EV-006']),
('Trabalho de Glim para Varo',['glim'],
 'Fase em que Glim emprega seus talentos em serviços criminosos e chega ao rompimento moral provocado pela morte de Tom.',
 '@{Varo} o utiliza como distração e conhece os limites que o gnomo procura impor a si mesmo. O percurso aproxima Glim de informações sobre o Ébano, sem tornar todas as conexões uma cadeia de comando comprovada.\n\nDurante um serviço, @{Tom do Cesto|Tomas Rell, o Tom do Cesto}, que acolhia Glim, o reconhece. O homem que acompanha Glim mata Tom. A cena rompe a possibilidade de fingir desconhecimento sobre os efeitos do trabalho; a autoria material não deve ser transferida automaticamente a Varo.',
 'Glim guarda uma moeda de Tom, investiga ligações do submundo e retorna à aldeia. O arco prepara sua tentativa posterior de se afastar desse meio ao procurar trabalho em Eral.',
 ['Varo','Tom do Cesto','Ebano','Glim Sombrasselva','Memorias materiais de Glim'], ['B','H'], []),
('Chegada a Eral',['glim'],
 'Formação do grupo na caravana Talent e início da relação de trabalho com Arkhavel, registrada nas primeiras sessões.',
 'A síntese dos diários apresenta Glim buscando trabalho e viajando para @{Eral} na caravana organizada por @{Teodoron Talent}. Ali conhece Okay, Ryld, Crave, Tauro e a mulher que o acompanha. Poderes dos quatro futuros Magníficos reagem entre si.\n\nA mulher possuída transportada pela caravana é levada a Arkhavel e não é a mulher originada do braço de Tauro. O primeiro serviço leva o grupo ao @{Plano Elemental do Ar} para obter um elemental de tempestade, usado por uma invenção de limpeza.',
 'O perdão obtido após as mortes dos gnolls estabelece um ano de serviço e percentual dos contratos, segundo a síntese. A capital do início do diário foi corrigida pelo jogador para Carruan; a narrativa original continua preservada.',
 ['Glim Sombrasselva','Okay dBoa','Ryld','Crave','Teodoron Talent','Arkhavel','Eral'], ['H','J'], []),
('Caso das criancas',['glim'],
 'Investigação das crianças desaparecidas e dos arbustos, distinta da apuração ainda incompleta da água envenenada.',
 'O grupo descobre sete crianças desaparecidas e indícios associados a arbustos. A @{Fada Orfa|Fada Órfã} é identificada no caso e morta depois de quase matar Glim. O agradecimento popular, presentes e a vigília de Kord diante da torre mudam o vínculo do grupo com os moradores.\n\nAs investigações também tratam de água imprópria e de uma região venenosa associada aos Crepúsculos Venenosos. Essa associação começa como suspeita e a quantidade de veneno necessária a põe em dúvida; resolver o caso das crianças não encerra automaticamente o caso da água.',
 'As informações desta entrada são a sequência reunida no handoff a partir das sessões 4–6. A responsabilidade individual de outros agentes e o estado final da água não foram confirmados por essa sequência.',
 ['Fada Orfa','Glim Sombrasselva','Eral','Igreja de Kord','Crepusculos Venenosos'], ['H'], ['EV-008']),
('Caca ao Vasuthant',['glim'],
 'Busca prolongada de uma criatura ligada aos experimentos de Arkhavel, com orientação de Hanta e a primeira mensagem prática do grimório.',
 'A síntese do diário registra a contratação de @{Hanta}, tentativas frustradas e quase quinze dias de procura. Na entrada solo de 22/04, o livro aconselha mudar a estratégia: deixar de caçar como presa e empregar iscas.\n\nO grupo mata o @{Vasuthant} com iscas vivas, volta com animais e presentes e vê Hanta recusar pagamento. Na volta, o desaparecimento de Ryld e a morte do guarda Carlos abrem outros problemas em Eral.',
 'A duração da caça é aproximada. A mensagem confirma atividade comunicativa do livro, sem responder quem fala por ele. O paradeiro posterior de Hanta pertence à expedição dos rangers, não a uma morte demonstrada aqui.',
 ['Vasuthant','Hanta','Grimorio de Glim','Ryld','Eral'], ['H'], ['IT-001']),
('Caso Carlos e magia viva',['glim'],
 'Ataques à família do carpinteiro em frente à torre, paralelos à morte e ao roubo do cadáver de um guarda também chamado Carlos.',
 'Glim prepara um alarme para a casa da família do @{Carlos carpinteiro}. O grupo enfrenta a @{Magia viva do sono} adulta e recolhe um filhote inteligente; Arkhavel interpreta o resultado como criação de uma raça.\n\nSeparadamente, o cadáver de @{Carlos guarda|Carlos, o guarda}, foi levado à igreja e roubado. A chantagem pela libertação de Ryld exige tirar da igreja um infiltrado que matou um religioso para substituí-lo. A coincidência de nome não faz dos dois Carlos a mesma pessoa.',
 'A confirmação posterior identifica o corpo usado por Vesperal como o do carpinteiro. A morte do guarda no arco anterior não explica a morte do carpinteiro, cujas circunstâncias continuam abertas na nota pessoal.',
 ['Carlos carpinteiro','Carlos guarda','Magia viva do sono','Ryld','Casa de Carlos','Igreja de Kord em Eral'], ['H','J'], []),
('Crise do prefeito',['glim'],
 'Confronto que expõe a dominação do prefeito e a presença do Aboleth, antes da operação final contra a arena.',
 'O grupo chega à recepção do prefeito com ajuda negociada de Arkhavel. Na síntese da sessão 12, Crave mata o prefeito dominado; @{Kuat}, o mordomo transformado em abominação, derruba quase todos até ser neutralizado por Glim. Arkhavel intervém e mata o Aboleth no lago da mansão, ficando com o tesouro.\n\nAs cartas posteriores ligam um filho de Arkhavel ao controle do prefeito e à parceria secreta com o Aboleth. @{Donovan} é apresentado como outro filho: a identidade e as funções dos dois não devem ser fundidas.',
 'A queda dessa estrutura não prova o fim da rede de cativos ou do Mercado Negro. As relações são esclarecidas parcialmente na queda da arena e continuam com lacunas pessoais e políticas.',
 ['Prefeito humano de Eral','Filho de Arkhavel ligado ao prefeito','Kuat','Arkhavel','Mercado Negro','Queda da arena'], ['H'], []),
('Queda da arena',['glim'],
 'Operação dos Magníficos e aliados contra a arena de Eral, seguida de investigação do tesouro e das cartas de seus responsáveis.',
 'Os preparativos envolvem Kenku, igreja, Tork e o Conclave. A negociação apaga seis nomes ligados à comunidade da floresta em troca de ajuda contra guardas. A sessão 15 contém combate contra guardas, gnolls e chefes; seu começo não está integralmente gravado.\n\nNa sessão 16, a queda da arena e a leitura das cartas revelam tributos, cativos, financiadores e pressões entre @{Silthan}, @{Mercado Negro}, o filho de Arkhavel, @{Kenku de Eral} e @{Conclave da floresta}. A classificação de cada aliado ou suspeito deve seguir o papel descrito, e não uma culpa coletiva inferida.',
 'Tork realiza uma purga por emboscadas individuais e recebe o título de Primeiro Magnífico Honorário. A ruptura local não neutraliza os agentes que depois traem a cidade. A estrutura de propriedade da arena e os propósitos de alguns participantes permanecem em suas notas.',
 ['Arena de Eral','Arena de Silthan','Tork','Kenku de Eral','Conclave da floresta','Mercado Negro'], ['H'], []),
('Busca dos rangers',['glim'],
 'Expedição frustrada em busca dos rangers, cuja ausência coincide com a vulnerabilidade de Eral.',
 'A correção preservada na cronologia estabelece que o grupo desistiu doze dias depois de sair de Eral e então iniciou a volta. O retorno também é descrito em cerca de doze dias; a ausência total não foi de apenas doze.\n\nA síntese registra encontro com @{Vyrix}, orientações e, na volta, um lirista espectral que fascina e drena Carisma. O grupo chega a Eral depois do saque. Folha-Seca, Hanta e os demais desaparecidos não ganham um destino confirmado com o encerramento da busca.',
 'A amiga de Folha-Seca desaparecera antes dessa missão e é outra ocorrência. A duração corrigida deve orientar a cronologia sem fabricar itinerário ou resultado do resgate.',
 ['Folha-Seca','Hanta','Vyrix','Ataque a Eral','Eral'], ['H','C'], []),
('Ataque a Eral',['glim'],
 'Ataque e saque de Eral durante a ausência dos Magníficos, agravados pela traição dos Kenku.',
 'A síntese da sessão 18 registra Kenku golpeando defensores e clérigos pelas costas, a morte de Tork, o saque e a mensagem agradecendo pelo “saque magnífico”. A torre é invadida, Tauro fica gravemente ferido e a jovem por ele protegida morre. A coordenação exata entre traidores e atacantes não está recuperada.\n\nT19, 00:25:36–00:26:59, corrige estimativas improvisadas: cerca de dez mil habitantes antes, dois mil mortos, aproximadamente mil ainda na cidade e sete mil em marcha. Cerca de sessenta por cento dos mortos não morreram em combate. Mortes futuras dos refugiados são previstas, não contadas.',
 'A cidade perde comando efetivo e aguarda ajuda e novo prefeito. Os números são estimativas da mesa, não um censo preciso de cada indivíduo, e não autorizam declarar os sete mil refugiados mortos.',
 ['Eral','Tork','Kenku de Eral','Guarda de Eral','Igreja de Kord','Tauro','Torre de Arkhavel'], ['H','T19'], []),
('Experiencia de Okay no amuleto',['glim'],
 'Sequência planar vivida por Okay durante o fenômeno do amuleto de Kord, com tempo subjetivo distinto do que passa fora.',
 'O handoff reúne a passagem pelo @{Muro das Lamentacoes}, almas sem patrono aceito, figura angélica colossal, planos inferiores e guerra entre demônios e diabos. Uma organização de encapuzados com símbolo de anzol recolhe almas para leilão. Okay é comprado por figura aparentemente humana, tida como possível súcubo, sem espécie confirmada.\n\nDepois, correspondências pesquisadas e a validação do mestre dão à experiência estatuto de realidade da mesa; isso não completa a ligação entre amuleto, morte e renascimento. Seres encontrados passam a poder ser invocados por ele de modo específico.',
 'A sequência parece longa para Okay enquanto cerca de meia hora passa fora, segundo a síntese. Sua duração não deve ser somada ao calendário Material nem usada para importar a cosmologia de outro cenário.',
 ['Okay dBoa','Amuleto de Kord','Traficantes planares de almas','Muro das Lamentacoes'], ['H'], ['IT-003']),
('Posto dos Mind Shredders',['glim'],
 'Combate na casa em quarentena que revela um posto de alimentação de Mind Shredders, sem resolver a localização de toda a colônia.',
 'A síntese de S19 registra duas larvas e um guerreiro mortos. As explicações de S19–S20 descrevem estágios que passam por casulos, formas maiores e estágio inteligente/mágico menor. A ideia de reprodução por larvas do estágio superior é apresentada como crença.\n\nNa sessão 20, Ryld assume a inspeção da toca. Não há resultado posterior confirmado dessa verificação. A @{Casa em quarentena} não foi identificada como a casa do carpinteiro Carlos.',
 'O esvaziamento de um posto não prova a destruição da colônia ou morte de sua forma dirigente. @{Mind Shredders} e @{Devoradores de mente} ligados à organização de Firael são ameaças distintas.',
 ['Mind Shredders','Casa em quarentena','Ryld','Devoradores de mente'], ['H'], []),
('Crise dos refens',['glim'],
 'Escalada do confronto com os goblinoides, envolvendo humanos escravizados, negociação de reféns e morte de indefesos.',
 'Após a morte do chefe cuja condição distorcia resultados, o grupo encontra humanos cativos, incluindo crianças, em condições de escravidão. A sessão 22 registra libertações e o confronto com o gnoll sobrevivente. Glim mata uma adulta inconsciente; Crave mata outros indefesos, incluindo um intérprete jovem.\n\nA recapitulação de S23 fixa quinze humanos mortos nos setores em que goblins recuam e matam reféns, enquanto Glim salva pessoas em outros setores. Cerca de 42 libertados aparece em outro momento do relato e não deve ser tratado como o mesmo total sem reconciliação.',
 'Os crimes dos captores não eliminam a distinção entre combatentes e pessoas indefesas. O massacre fundamenta a busca de redenção de Crave e a orientação de Tariun; a base registra atos e consequências, sem transformar interpretação moral de um personagem em absolvição factual.',
 ['Assentamento goblinoide','Chefe goblin','Glim Sombrasselva','Crave','Gnoll sobrevivente','Tariun','Provacoes de Kord'], ['H'], ['EV-004']),
('Provacoes de Kord',['glim'],
 'Busca de redenção de Crave depois da crise dos reféns, que passa pela orientação de Tariun, tentação de Hextor e escolhas na aldeia gelada.',
 'Tariun apresenta a força como proteção e condena matar indefesos por medo do futuro. Crave recusa a oferta de Hextor. Na neve, encontra o cinto de Kord preso em gelo azul e um rito de dez campeões; escolhe tocar o gelo enquanto Glim e Okay tentam atrasar yetis e salvar fugitivos.\n\nT23, 02:12:17–02:13:36, explica em off o propósito da escolha e identifica o sacerdote ferido como a pessoa não vilã da situação. Em 03:46:30–03:48:25, a figura do prelúdio o retira vivo, Crave fica congelado e vai ao torneio. O torneio inclui provas de força e atletismo com pontuação, em vez de ser somente um combate mortal.',
 'Crave retorna exausto, com três pontos cumulativos de Força, sem recuperar o cinto segundo a síntese de S24. O total de fugitivos mortos não foi registrado. Sua participação no torneio não demonstra redenção final nem recuperação automática do artefato.',
 ['Crave','Kord','Hextor','Tariun','Aldeia ocupada na neve','Cinto de Kord','Disco de Tariun'], ['H','T23'], ['EV-005','IT-004']),
('Despertar do Fogo Primordial',['glim'],
 'Provação que envolve o sacrifício permanente de uma magia de Glim e o despertar do fogo branco/prateado de Okay.',
 'Durante a prova do beholder flamejante, distinto do beholder da biblioteca, Glim entrega uma magia de círculo zero identificada no handoff como Caltrops. T24, 00:59:32–01:00:09, explica que a proibição de conjurá-la é permanente, inclusive por outros meios ou classes.\n\nOkay passa a manifestar chama branca/prateada. Em 01:05:31–01:07:10, o mestre a identifica como Fogo Primordial, habilidade extraordinária rara e tida como presente, não uma magia comum. A comparação com figuras de Forgotten Realms é uma analogia de conhecimento, não identificação da patrona de Okay.',
 'Os estudos posteriores apresentam preparação e absorção, com impossibilidade de absorver a própria magia. A relação entre provação, origem do poder e o conhecimento de Arkhavel ainda não foi totalmente explicada.',
 ['Glim Sombrasselva','Okay dBoa','Fogo Primordial','Arkhavel','Grimorio de Glim'], ['H','T24'], ['IT-006']),
('Manifestacao da sombra de Lilo',['glim'],
 'Criação do familiar de sombra com a forma de Lilo, mediante a renúncia de Crave à própria sombra.',
 'T24, 03:03:17–03:04:20, descreve Crave retornando sem projetar sombra e a sombra saindo inteira do livro, com a aparência do irmão de Glim. A mesa atribui capacidades associadas a Glim e natureza de sombra, com comunicação limitada.\n\nUma atualização posterior permite manipular objetos. A manifestação acontece depois de visões e disputas em torno do grimório e do fogo, mas essas visões não são por si mesmas depoimentos históricos confiáveis de Lilo.',
 'O familiar existir e ter a forma de Lilo não comprova que contenha sua alma original ou que tenha ocorrido ressurreição completa. A nota pessoal de Lilo preserva essa questão; o evento não a resolve por escolha de vocabulário.',
 ['Lilo Sombrasselva','Crave','Glim Sombrasselva','Grimorio de Glim'], ['H','T24'], ['IT-001']),
('Memorias de Kael',['glim','fash'],
 'Revelações da sessão 25 ligadas aos pergaminhos e mapas, que permitem a Okay reconhecer a própria vida como Kael.',
 'O mestre descreve morte, fuga e memória da vida anterior. Okay reconhece a letra de Firael nos documentos e descobre sua posição de comando no presente, com o Cérebro acima dele. Os esclarecimentos posteriores confirmam a identificação @{Kael}/@{Okay dBoa|Okay}.\n\nA gravação distingue o que é narrado a Okay, o que ele compartilha e o que decide guardar. Conhecer a antiga identidade da planta/cajado de Timo não vira conhecimento automático de Glim quando Okay escolhe manter esse segredo.',
 'A memória recuperada não é acesso universal a todas as encarnações. O desejo de procurar a mulher das memórias na montanha é plano de investigação, não uma viagem já realizada no recorte até S26.',
 ['Okay dBoa','Kael','Firael','Mapas e pergaminhos de Firael','Mulher das memorias','Montanha das memorias'], ['H','J','T25'], ['EV-001']),
('Confronto com Vesperal',['glim'],
 'Encontro com o visitante de aparência idêntica a Carlos, que tenta obter o amuleto de Crave e é derrotado na torre.',
 'Aurel Vesperal apresenta fala arcaica, interesse por limpeza e pelo amuleto, percebe a fuligem apesar do medalhão e integra o serviço de limpeza. Ao tocar Crave, drena Constituição e fortalece o próprio corpo. Voo, teleporte e resistência dificultam o combate; Proteção contra o Mal bloqueia o contato com Crave e o agressor drena invocações e Okay.\n\nEm T26, 02:39:48–02:42:04, o corpo cortado não sangra e a mesa o identifica como Carlos. A lembrança dos anjos caçando um possessor e de sobrenome semelhante leva à suspeita de demônio. J confirma que o cadáver é do carpinteiro, não do guarda.',
 'A destruição do corpo não comprova a morte do possessor. A encomenda de hidromel por uma mulher não vista sustenta suspeita de continuidade, não identidade confirmada da mandante. O pergaminho do anjo permanece disponível segundo a síntese.',
 ['Aurel Vesperal','Carlos carpinteiro','Amuleto de Kord','Medalhao de limpeza','Torre de Arkhavel','Pergaminho do anjo'], ['H','J','T26'], []),
('Preparativos da torre',['glim'],
 'Estudo dos mecanismos da torre, limpeza e organização da saída, no período em que Arkhavel continua ausente.',
 'T26, 00:51:02–00:55:39, distingue redirecionar portas por dez peças de ouro e mover o interior da torre por cem, com ritual de uma hora. O exterior permanece no lugar e o interior se encaixa numa casca existente no destino. Apagar runas pode provocar retorno em cerca de uma hora.\n\nOs registros descrevem cinco destinos conhecidos das cascas, limpeza após a revelação da sujeira e proteção da entrada por desvio. A ida ao Etéreo é registrada no encerramento e no diário; não é o deslocamento de toda a torre nem confirma um sexto destino de casca.',
 'A síntese estima aproximadamente três dias de preparação em S26, sem reconciliar todos os dias de S20–S24. A próxima cena é prevista para o retorno; duração efetiva da estada e lista final de magias copiadas não foram registradas.',
 ['Torre de Arkhavel','Portas de Arkhavel','Plano Etereo','Glim Sombrasselva','Okay dBoa','Crave'], ['H','T26','C'], ['IT-005','CR-002']),
('Revoada Branca',['fash','glim'],
 'Registro que reúne referências a revoadas sem transformá-las automaticamente num único evento.',
 'O handoff aponta a fala em off de T23, 01:08:44: uma Revoada Branca ocorreu na região gelada e a informação pertencia a outra mesa, não aos personagens atuais. Data, dragões participantes e campanha de origem não foram recuperados.\n\nTambém existe referência a revoada ligada à morte de Hourian/Haurim, cuja grafia e localização precisam de revisão. A semelhança de tema não demonstra identidade entre essa revoada, a Revoada Branca e a Noite Eterna.',
 'O registro está disponível aos leitores da base pública, preservando a diferença entre conhecimento em off e conhecimento dos personagens. Comparar os eventos continua sendo uma pergunta de sabatina, não uma equivalência adotada.',
 ['Hourian Haurim','Regiao gelada','Noite Eterna'], ['H'], ['EV-007']),
]

ITEMS = [
('Grimorio de Glim',['glim'],'item',
 'Livro encontrado por Glim e Lilo, centro de sua relação com sombras e de eventos que ultrapassam o que ele entende de magia.',
 'O background descreve escrita e aparência que mudam com a iluminação, páginas antes invisíveis e a ruptura de um selo. O livro passa a produzir mensagens, incluindo o conselho de caçar o Vasuthant com iscas. O handoff reúne a análise inicial que o data em pelo menos cinco mil anos e lhe atribui matéria externa ao Material.\n\nT17, 00:33:07–00:36:02, descreve energia tão densa que a mesa racha; a comparação com um planeta comunica escala de energia, sem provar um planeta literal dentro do volume. A mesa continua funcionando. O mestre o descreve como maior que um artefato maior e único.\n\nNas provações surgem imagens de Lilo e mensagens de amizade, acompanhadas de advertência do mestre sobre engano. O familiar posterior não resolve a identidade espiritual de Lilo nem a vontade do livro.',
 ['Glim Sombrasselva','Lilo Sombrasselva','Infancia e ruptura de Glim','Manifestacao da sombra de Lilo','Mesa de analise'], ['B','H','T17','T24'], ['IT-001']),
('Amuleto de Kord',['glim'],'item',
 'Objeto de Crave, entregue por Rudiger, que pode ser apresentado como amuleto, corrente ou anel nos registros. É distinto do medalhão de limpeza e do cinto no gelo.',
 'Tólomon o associa a um antigo avatar de Kord: essa é a tradição relatada pelo sacerdote. O handoff registra a correção de mesa de que o objeto não tem símbolo e o ganho de +6 de Força para Crave, enquanto o usa, após o golem vencido por Okay.\n\nA experiência planar de Okay no objeto e seu resultado são eventos próprios. Vesperal insiste em obtê-lo e toca Crave ao fingir examiná-lo; o interesse do agressor não revela sozinho a função secreta do amuleto.',
 ['Crave','Rudiger','Tolomon','Kord','Experiencia de Okay no amuleto','Confronto com Vesperal'], ['H'], ['IT-003']),
('Cinto de Kord',['glim'],'item',
 'Artefato feito de couro de dragão vermelho, preso em gelo azul com runas na aldeia da montanha.',
 'A síntese de S23–S24 descreve o rito que depende de dez campeões aceitos. Crave escolhe tocar o gelo e participa do torneio, ao mesmo tempo que Glim e Okay tentam salvar fugitivos. A proteção dos já congelados e as provas de força/atletismo são explicadas pelo mestre em T23.\n\nCrave volta com um resultado pessoal de Força, mas sem o cinto. A participação no rito e a recuperação do objeto são fatos diferentes; não registrar o artefato como parte de seu inventário atual.',
 ['Kord','Crave','Provacoes de Kord','Aldeia ocupada na neve'], ['H','T23'], ['IT-004']),
('Livro de Hextor',['glim'],'item',
 'Oferta recusada no arco de tentação de Crave. A descrição de seu efeito é informação revelada pelo mestre em off, não um benefício recebido.',
 'T23, 03:49:20–03:49:44, explica que o conteúdo do baú seria um livro de Força +5 permanente. A leitura aumentaria a musculatura e produziria veias salientes em desenho circular. O formato da marca é parte da explicação de uma escolha que não ocorreu.\n\nCrave não leu ou adquiriu o livro nesse registro e não recebeu esse bônus. A promessa de força que a entidade não retiraria deve permanecer como discurso da oferta, sem lhe conferir alcance universal demonstrado.',
 ['Hextor','Crave','Provacoes de Kord'], ['H','T23'], []),
('Esfera de Elena',['fash','glim'],'item',
 'Artefato de cristal amarelado associado à escravidão de Elena e aos mundos de sonho da campanha antiga.',
 'Segundo a síntese do diário, o grupo o leva da cabana ao despertar, junto de material da bruxa. Elena pede sua destruição para cessar o cativeiro. O líder do Forte o destrói perto da caverna drow, desencadeando o fenômeno das criaturas de luz.\n\nT25, 01:05:44, distingue a versão pública — destruição como cura da epidemia — da correção do mestre: a destruição a provocou. O pedido de Elena e a consequência observada não são suficientes para reconstruir todo o projeto original do artefato.',
 ['Elena','Plano dos sonhos','Destruicao da esfera de Elena','Cabana das bruxas'], ['H','T25'], ['EV-002','EV-003']),
('Livro das tres bruxas',['fash','glim'],'item',
 'Entrada documental para o material das três bruxas recuperado, lido ou compilado durante a campanha antiga e reapresentado em cópias na campanha atual.',
 'O diário, conforme reunido no handoff, utiliza um livro de Morvessh para explicar o Círculo Vetrilus, o nodo e a identidade Serethyn. A atribuição de uma biografia falsa ou incompleta a Elena é afirmação desse livro, não comprovação automática de cada detalhe.\n\nT25, 00:12:11–00:13:06, descreve cópia do livro em vários papiros entre os documentos entregues, e distingue outro volume mais poderoso com o dragão. A denominação desta nota reúne uma cadeia documental; os títulos e a identidade exata de cada volume ainda precisam ser conciliados.',
 ['Circulo Vetrilus','Morvessh','Elena','Livro do dragao negro','Mapas e pergaminhos de Firael'], ['H','T25'], ['IT-002']),
('Livro do dragao negro',['fash','glim'],'item',
 'Volume especialmente poderoso em poder do dragão negro, distinto da cópia em papiros apresentada aos Magníficos.',
 'T25, 00:12:11–00:13:06, ressalta que o dragão tem um livro da bruxa e que esse outro é muito mais poderoso que o material copiado. Os nomes das irmãs aparecem nos documentos, embora a fala da mesa oscile ao recordá-los.\n\nA tentativa de roubo de Firael depois de ser entregue vivo ao dragão é complementada por J e pelo handoff. O acordo que lhe permite sobreviver não demonstra que tenha saído com o livro, nem que o volume seja o grimório de Glim.',
 ['Dragao negro','Firael','Livro das tres bruxas','Duelo e entrega de Firael'], ['H','J','T25'], ['IT-002']),
('Cajado de girassol',['fash','glim'],'item',
 'Artefato maior novo, originado da planta que era Timo, atualmente referido com uma dríade portadora.',
 'J confirma Timo/planta/cajado e ressalta que isso não identifica a dríade como reencarnação do druida. O handoff reúne os relatos do cajado que faz a vegetação crescer e de uma região antes corrompida que voltou a apresentar floresta saudável.\n\nO caráter novo do artefato o distingue da antiguidade atribuída aos artefatos dos Zodíacos. A consciência de Timo, o modo da transformação e a extensão de seus poderes não ficam resolvidos pela classificação de artefato maior.',
 ['Timo','Driade do cajado de girassol','Santuario da driade','Zodiacos'], ['J','H'], ['IT-007']),
('Mesa de analise',['glim'],'item',
 'Instrumento do laboratório de Arkhavel usado para estudar objetos, corpos e criaturas, com instruções em celestial.',
 'A síntese dos diários registra análises de Tauro, da mulher com coração de warforged e do grimório. O que o aparelho revela deve ser descrito conforme cada leitura, em vez de pressupor uma identificação perfeita e ilimitada de tudo.\n\nNa análise do livro em T17, 00:33:07–00:36:02, a mesa racha sob a energia, mas continua utilizável. Em T26, 02:40:38, seu experimento permite reconhecer o cadáver como Carlos; a identificação como carpinteiro é complementada por J.',
 ['Arkhavel','Torre de Arkhavel','Tauro','Mulher originada do braco','Grimorio de Glim','Carlos carpinteiro'], ['H','J','T17','T26'], []),
('Medalhao de limpeza',['glim'],'item',
 'Objeto da torre que mascara a sujeira e impede que ela suje os ocupantes, sem remover a matéria acumulada.',
 'Vesperal percebe ou toca fuligem apesar de o medalhão estar ativo. Sua retirada revela sangue seco, fuligem e sujeira; a limpeza feita por pessoas é uma operação posterior real. A aparência de limpeza não provava que a torre estivesse materialmente limpa.\n\nO handoff o distingue expressamente do amuleto de Kord cobiçado pelo visitante. Retirar o medalhão não significa entregar, destruir ou desativar o objeto de Crave.',
 ['Torre de Arkhavel','Aurel Vesperal','Amuleto de Kord','Confronto com Vesperal'], ['H'], []),
('Corneta da arena',['glim'],'item',
 'Corneta obtida no arco da arena e usada para chamar Ryld após o ataque a Eral.',
 'A explicação reunida no handoff para T19, 00:01:51–00:06:08, diz que a voz alcança quem poderia ver o portador, ainda que não esteja olhando; a direção é percebida e não há filtro de destinatários. Essa regra impede tratá-la como telepatia discreta com uma pessoa escolhida.\n\nO uso para chamar Ryld demonstra uma aplicação, mas não identifica por si só a origem ou todos os efeitos possíveis do objeto.',
 ['Arena de Eral','Ryld','Ataque a Eral'], ['H'], []),
('Coleiras drow',['fash'],'item',
 'Instrumentos de domínio dos escravizados na cidade drow, cuja sucessão de autoridade teve papel decisivo na libertação dos anões.',
 'Segundo a síntese do diário, a autoridade passa ao assassino do proprietário após 24 horas. Kael desfere o golpe fatal no Druida Sangrento e depois utiliza o domínio para libertar os anões. Firael o decapitar posteriormente não é registrado como transferência equivalente de autoridade.\n\nA regra observada nesse episódio não demonstra o funcionamento de toda coleira de escravos do mundo nem autoriza inferir condição atual de objetos não acompanhados.',
 ['Druida Sangrento','Kael','Anoes libertos','Queda do Druida Sangrento','Cidade drow'], ['H'], []),
('Mascara astral do drow',['fash'],'item',
 'Máscara associada ao drow que permite espiar o astral e verificar a presença de Lídia, conforme a síntese do diário solo.',
 'A observação se insere na vigilância do Necromante sobre Fash. A capacidade de ver a presença de Lídia não é comprovação de conhecimento universal do plano astral nem de todas as funções da máscara.\n\nÉ um objeto distinto da máscara que muda de aspecto nas provas oníricas. A coincidência de nome de tipo não estabelece identidade entre os dois artefatos.',
 ['Lidia','Necromante','Fash Paleskin','Mascara dos testes'], ['H'], []),
('Mascara dos testes',['fash'],'item',
 'Máscara das provas do sonho antigo, cujo aspecto se altera conforme as experiências narradas nas portas.',
 'A síntese descreve resultados angelicais ou demoníacos e, ao fim, uma máscara metade angelical/metade demoníaca. Uma criatura se forma e desaparece; anão e criança tornam-se portais dentro da experiência.\n\nOs episódios pertencem ao contexto posteriormente revelado como sonho. Não se conclui desses símbolos uma classificação moral objetiva de cada personagem, uma criatura material solta ou a permanência das recompensas fora do cativeiro.',
 ['Cativeiro e sonho de Fash','Plano dos sonhos','Mascara astral do drow'], ['H','J'], ['EV-003']),
('Colar de mortos-vivos',['fash'],'item',
 'Objeto ligado ao recolhimento dos zumbis do drow, referido na entrada de 08/02 resumida pelo handoff.',
 'O registro o coloca com pequenos gnomos ou criaturas também descritas como pequenos lobos; a taxonomia fica ambígua. É prudente registrar a ação e a divergência descritiva sem criar uma espécie ou trocar silenciosamente os portadores.\n\nEste colar não deve ser fundido com amuleto de Kord, objetos das provas ou coleiras de escravos apenas pela forma de adorno.',
 ['Druida Sangrento','Cidade drow','Coleiras drow'], ['H'], []),
('Disco de Tariun',['glim'],'item',
 'Disco de pedra com gemas vermelha e verde, entregue para a viagem da provação de Crave.',
 'T23, 00:17:48–00:18:48, explica: quebrar a pedra vermelha leva ao destino; quebrar a verde traz de volta. Todos os viajantes precisam tocar o disco e **só quem participou da ida pode voltar por ele**. Acrescentar outras pessoas no retorno não as transporta.\n\nA limitação é crucial para a tentativa de resgate na aldeia: o objeto não oferecia uma evacuação de todos os fugitivos. Sua utilidade naquela missão não prova novos usos ou recargas posteriores.',
 ['Tariun','Crave','Provacoes de Kord','Aldeia ocupada na neve'], ['T23','H'], []),
('Pergaminho do anjo',['glim'],'item',
 'Pergaminho de uso único para convocar um anjo específico, disponível como recurso na ameaça do possessor.',
 'A síntese de S26 registra que ele não foi consumido. A conversa considera a possibilidade de recorrer ao anjo se o inimigo puder ser localizado, ao mesmo tempo que ressalta seu teleporte e dificuldade de captura.\n\nDisponibilidade de um recurso e plano de usá-lo não equivalem a convocação realizada. O anjo, suas condições de intervenção e o resultado dessa opção não têm um novo episódio registrado no recorte.',
 ['Confronto com Vesperal','Aurel Vesperal','Preparativos da torre'], ['H'], []),
('Memorias materiais de Glim',['glim'],'conjunto_de_itens',
 'Objetos e restos preservados por Glim como vínculos afetivos de sua história, sem poderes mágicos específicos demonstrados.',
 'O background e o handoff enumeram Piche, o pingente de Brakka, a moeda de Tom, o pente quebrado da mãe e a fivela do pai. Cada lembrança corresponde a relação e perda distintas; o corpo do corvo não implica ressurreição.\n\nEsses elementos ligam a infância, o circo, o trabalho para Varo e a volta à aldeia. A memória emocional do personagem é parte do registro, sem transformar todos os objetos em artefatos.',
 ['Glim Sombrasselva','Piche','Brakka Pedramansa','Tom do Cesto','Infancia e ruptura de Glim','Queda da Roda de Estopa'], ['B','H'], []),
('Artefatos investigados pelos arquivistas',['glim'],'dossie_de_itens',
 'Casos transmitidos pelos pesquisadores de Okay, com graus diferentes de confirmação e sem apresentação direta de todos os objetos.',
 'O handoff reúne o totem guardado por um povo da montanha dizimado e depois roubado. Em outro caso, uma transformação coletiva de sexo numa cidade é associada a um possível artefato: a causa material continua hipótese.\n\nA história da epidemia e do artefato quebrado também chega aos pesquisadores como versão distorcida e é corrigida pelo mestre em T25. Esses casos servem como pistas e objetos de pesquisa, não como um inventário de artefatos já adquiridos pelo grupo.',
 ['Arquivistas','Okay dBoa','Destruicao da esfera de Elena','Zodiacos'], ['H','T25'], ['IT-008']),
('Mapas e pergaminhos de Firael',['fash','glim'],'conjunto_de_documentos',
 'Documentos entregues na campanha atual que descrevem a região antiga e desencadeiam a recuperação das memórias de Okay.',
 'O material descreve cidade drow, dragão negro, trolls, biblioteca do beholder, minas e nodo. T25, 01:35:18, explica que Okay reconhece a letra do personagem antigo identificado como Firael. A localização do nodo inclui informação recebida do Cérebro que os outros companheiros não conheciam.\n\nEntre os papiros há cópia de material das bruxas; outro livro mais poderoso permanece atribuído ao dragão. Um pergaminho que avalia os Magníficos como manipuláveis sugere uma agenda, mas não a revela por inteiro.',
 ['Firael','Cerebro Anciao','Memorias de Kael','Cidade drow','Livro das tres bruxas','Livro do dragao negro'], ['H','T25'], ['IT-002']),
('Portas de Arkhavel',['glim'],'mecanismo',
 'Rede de portas e mecanismos de desvio vinculados à torre. Redirecionar uma passagem é diferente de deslocar o interior da torre entre estruturas externas.',
 'T26, 00:51:02–00:55:39, fixa dez peças de ouro por configuração de porta. O desvio atua em ambos os sentidos e pode ser desfeito apagando os sinais; eles ficam magicamente escondidos, mas alguém suficientemente habilidoso pode detectá-los e removê-los.\n\nMover o interior da torre custa cem peças de ouro e exige ritual de uma hora. A casca externa fica no lugar, e o interior se encaixa em outra estrutura existente. O handoff reúne os cinco destinos identificados: mundo atual, Plano das Sombras, Greyhawk, Forgotten Realms e Dark Sun. A ida ao Etéreo por uma porta não é um sexto destino demonstrado desse mecanismo.\n\nHá orientações diferentes sobre fechar e reabrir portas em S14, S19 e S25. A base as preserva como divergência a esclarecer em vez de criar uma regra universal por escolha da versão mais recente.',
 ['Arkhavel','Torre de Arkhavel','Preparativos da torre','Plano Etereo','Plano das Sombras'], ['H','T26'], ['IT-005']),
('Fogo Primordial',['glim'],'poder',
 'Habilidade extraordinária de Okay, visualmente associada a chamas brancas/prateadas, cuja compreensão começa na sessão 24.',
 'T24, 01:03:38–01:07:10, distingue o fogo de uma magia comum e o apresenta como capacidade rara, normalmente tida como presente. O exemplo de Elminster e outras figuras de Forgotten Realms é analogia, não confirmação de que Mystra seja a fonte de poder de Okay.\n\nEm 01:38:19–01:42:05, os livros levam à conclusão de que Arkhavel sabe criá-lo. Okay aprende a fazer a chama aparecer e a preparar absorção de magia hostil que o atinja; a própria magia não serve para abastecê-lo. A chama pode ser exibida sem preparação e ilumina aproximadamente três metros de raio, conforme a explicação da mesa.\n\nO handoff também registra uso da energia para cura ou dano e possibilidade de sobrecarga. Não se infere imunidade universal à magia a partir da comparação histórica ou da aparência acesa.',
 ['Okay dBoa','Arkhavel','Despertar do Fogo Primordial','Grimorio de Glim'], ['H','T24'], ['IT-006']),
]

OUTPUTS = []


def cite_prose(body, sources):
    paragraphs=[]
    for paragraph in body.split('\n\n'):
        if paragraph.startswith('#') or not paragraph.strip():
            paragraphs.append(paragraph)
            continue
        codes=[]
        if 'H' in sources and any(x in paragraph.lower() for x in ['síntese','handoff']):
            codes=['H']
        else:
            codes=[x for x in re.findall(r'\bT(?:1[3-9]|2[0-6])\b',paragraph) if x in sources]
            if not codes and 'J' in sources and any(x in paragraph.lower() for x in ['jogador','esclarecimentos']):
                codes=['J']
            if not codes and 'B' in sources and 'background' in paragraph.lower():
                codes=['B']
            if not codes:
                codes=['H'] if 'H' in sources else sources
        if codes == ['J'] and 'H' in sources:
            # J confirms identities/errata but does not repeat every surrounding
            # scene. A mixed paragraph also cites the synthesis supporting it.
            codes.append('H')
        paragraphs.append(paragraph + ' ' + ' '.join(ref(c) for c in dict.fromkeys(codes)) + '.')
    return '\n\n'.join(paragraphs)


def record_notes(records,domain):
    by_path = {r['destino'].split('/')[-1]:r for r in REG if r['dominio']==domain}
    for entry in records:
        if domain=='eventos':
            key,campaigns,intro,sequence,aftermath,related,sources,questions = entry
            kind='evento'
            body = expand(intro) + '\n\n## Sequência documentada\n\n' + expand(sequence) + '\n\n## Consequências e limites\n\n' + expand(aftermath)
        else:
            key,campaigns,kind,intro,detail,related,sources,questions = entry
            body = expand(intro) + '\n\n## Registro e funcionamento\n\n' + expand(detail)
        body = cite_prose(body,sources)
        # Section-level citations state the actual evidence level, rather than
        # presenting source codes copied from a synthesis as newly checked speech.
        body += '\n\n## Evidências\n\n'
        if sources==['H']:
            body += 'Esta entrada organiza a síntese do handoff. As referências primárias indicadas por ele continuam disponíveis no acervo; esta nota não alega revisão integral de todas essas gravações.\n\n'
        body += '\n'.join('- ' + ref(s) for s in sources)
        body += '\n\n## Conexões\n\n' + '\n'.join('- ' + link(DEST[x]) for x in related)
        if questions:
            body += '\n\n## A confirmar ou completar\n\n' + '\n'.join('- ' + link(QP[x],x+' — pergunta preparada para a sabatina') for x in questions)
        else:
            body += '\n\n## A confirmar ou completar\n\nAs condições não demonstradas nesta entrada permanecem abertas. Consulte as pendências das entidades relacionadas; não foi criada uma resposta por dedução a partir do nome do objeto ou evento.'
        row=by_path[key]
        OUTPUTS.append(escrever(row['destino'],row['nome'],kind,campaigns,body,sources,
                                aliases=['Doze Dias Rubros'] if key=='Noite Eterna' else []))


record_notes(EVENTS,'eventos')
record_notes(ITEMS,'itens')

chronology = '''A base distingue três eixos: datas das sessões, tempo vivido no mundo material e experiências subjetivas em sonhos ou planos. O intervalo de **70 anos entre as épocas de Fash e Glim** foi informado pelo jogador; ele não cria um calendário absoluto para todas as ocorrências.

## Sequência de referência

| Fase | Registro e limite |
| --- | --- |
| Antiguidade regional | Aprisionamento do Cérebro por quatro povos, uso de jogos e guerra; data não fixada. |
| Cativeiro de Fash | Provas e Lazathar pertencem ao sonho revelado em 25/10; datas desse trecho não fixam o presente. |
| Campanha material antiga | Esfera de Elena, Forte, Druida Sangrento, libertações e cidade drow. |
| Fim da mesa antiga | Duelo, entrega de Firael e fuga; morte de Kael pelo dragão. |
| Transição posterior | Fundações das facções, destino de Timo e Noite Eterna; ordem e intervalos incompletos. |
| Vida de Glim antes da mesa | Infância e grimório, circo, crise dos mortos, Varo e retorno à aldeia, conforme seu background. |
| Campanha atual | Caravana, Eral, arena, expedição, saque, ameaças, provações e preparação da torre. |

O quadro é uma ordem de referência sintetizada a partir do handoff e dos esclarecimentos; a transição não foi convertida em datas precisas. Fonte: ''' + H + ' e ' + J + '''.

## Continuidade confirmada e fronteiras

- Kael reencarnou como Okay; a memória recuperada não é conhecimento de todas as vidas.
- Ébano e Sociedade das Sombras são nomes da mesma organização, fundada por Fash.
- Timo tornou-se planta e cajado; a dríade portadora não foi identificada como reencarnação dele.
- Noite Eterna e Doze Dias Rubros nomeiam o mesmo evento; Lua Sangrenta é uma organização.
- Carruan é a capital real; Lazathar como capital no diário de Glim é errata reconhecida.

Essas confirmações já constam em ''' + J + ''' e não precisam ser repetidas como perguntas abertas na sabatina.

## Conexões

- @{Cativeiro e sonho de Fash}
- @{Aprisionamento do Cerebro}
- @{Duelo e entrega de Firael}
- @{Noite Eterna}
- [[Cronologia/Glim Sombrasselva|Cronologia da campanha atual]]

## A confirmar

''' + '\n'.join('- '+link(QP[x],x) for x in ['EV-001','CR-001','EV-003'])
OUTPUTS.append(escrever('Cronologia/Fash e Glim','Fash e Glim — continuidade','cronologia',['fash','glim'],expand(chronology),['H','J']))

current = '''A contagem estimada herdada chega a cerca de **55 dias desde a primeira cena da caravana até a sessão 19**, ou cerca de 51–52 desde a chegada a Eral. É estimativa explícita, com deslocamentos possíveis de um ou mais dias. Fonte: ''' + ref('C','Cronologia integral herdada') + '''.

## Marcos e intervalos

- A caça ao Vasuthant ocupa quase quinze dias segundo os diários, sem calendário diário completo.
- A correção do jogador para a expedição estabelece desistência doze dias após a saída de Eral e, em seguida, uma volta também descrita em cerca de doze dias. Não reduzir toda a ausência a doze.
- As sessões 20–24 têm deslocamentos, descansos e provações ainda sem conciliação da contagem absoluta.
- A sessão 25 ocorre na continuidade da fase da torre. Um mês a cavalo até a montanha é estimativa de viagem futura, não tempo já transcorrido.
- A preparação de S26 acrescenta aproximadamente três dias. A ida ao Etéreo acontece no encerramento, sem experiência ou duração detalhadas registradas.

Esses limites estão descritos em ''' + ref('C') + ' e ' + H + '''. Meses vividos subjetivamente nas provações não são somados automaticamente ao Plano Material.

## Datas da mesa

[[Sessoes/Indice|O índice de sessões]] mantém dias e meses originais. O ano de 1–12 e da solo está marcado como inferido; 13–26 têm ano documentado na proveniência. Essas datas organizam as gravações e diários, sem determinar datas ficcionais.

## Marcos conectados

- @{Chegada a Eral}
- @{Caca ao Vasuthant}
- @{Queda da arena}
- @{Busca dos rangers}
- @{Ataque a Eral}
- @{Crise dos refens}
- @{Provacoes de Kord}
- @{Preparativos da torre}

## A confirmar

''' + link(QP['CR-002'],'CR-002 — completar os intervalos das sessões 20–26')
OUTPUTS.append(escrever('Cronologia/Glim Sombrasselva','Glim — cronologia da campanha','cronologia',['glim'],expand(current),['C','H']))

manifest=dict(data='2026-10-29',dominios=['eventos','itens','cronologia'],notas=OUTPUTS,pendencias=QUESTIONS,
              cobertura=dict(eventos=len(EVENTS),itens=len(ITEMS),cronologias=2),
              fontes_consultadas=['H','J','B','F','C','T17','T19','T23','T24','T25','T26'],
              limites=['Handoff é fonte de síntese das entradas que o declaram; não foi refeita leitura contínua de todas as falas.',
                       'Fontes, diários, transcrições e originais não foram alterados.',
                       'Pendências individuais, geográficas e políticas são integradas a partir dos outros domínios.'])
(ROOT/'docs/enciclopedia/eventos-itens.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'notas':len(OUTPUTS),'pendencias':len(QUESTIONS),'eventos':len(EVENTS),'itens':len(ITEMS)},ensure_ascii=True))
