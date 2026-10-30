"""Integração editorial das fontes recebidas em 30/10; execução única."""
from pathlib import Path
import json,re,difflib

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'conteudo'
F='Fontes/Documentos/Diario de Firael - versao completa'
R='Fontes/Documentos/Preludio de Ryld'
V1='Fontes/Documentos/Diario de Firael - variante 1'
V2='Fontes/Documentos/Diario de Firael - variante 2'
def ref(src,where):return '[['+src+'|'+where+']]'
def split(p):
 s=p.read_text(encoding='utf-8');_,meta,body=s.split('---',2)
 return {k:json.loads(v) for k,v in (l.split(': ',1) for l in meta.strip().splitlines())},body
def write(p,m,body):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text('---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in m.items())+'\n---\n'+body,encoding='utf-8')
def add(rel,src,heading,body,replace=None):
 p=B/(rel+'.md');m,s=split(p)
 assert '\n## '+heading+'\n' not in s, 'Integração já aplicada: '+rel
 for old,new in (replace or {}).items():
  assert old in s,(rel,old)
  s=s.replace(old,new)
 m['origens']=list(dict.fromkeys(m['origens']+[src]));m['atualizado']='2026-10-30'
 s+='\n## '+heading+'\n\n'+body+'\n';write(p,m,s)
def new(rel,title,kind,src,body,aliases=None,campaigns=None):
 p=B/(rel+'.md');assert not p.exists(),rel
 m={'tipo':kind,'titulo':title,'campanhas':campaigns or ['glim'],'publico':True,'status':'documentado_com_perspectiva','origens':[src],'aliases':aliases or [],'atualizado':'2026-10-30'}
 write(p,m,'\n# '+title+'\n\n'+body+'\n')
def pending(code,src,body,remaining=None):
 p=next((B/'Pendencias').rglob(code+'*.md'));m,s=split(p)
 if m['status']=='aberta':m['status']='parcialmente_respondida'
 m['atualizado']='2026-10-30';m['origens']=list(dict.fromkeys(m['origens']+[src]))
 if remaining:m['pergunta_restante']=remaining
 s=s.replace('Ainda não respondida. Registrar quem confirmou, a data e o alcance da resposta antes de atualizar as notas relacionadas.','A fonte adicional e seus limites estão registrados abaixo; a questão permanece parcialmente respondida.')
 s+='\n## Nova fonte documental — 30/10/2026\n\n'+body+'\n';write(p,m,s)

# A cronologia e as certezas da campanha atual não são substituídas por relatos antigos.
add('Personagens/Firael',F,'Perspectiva do próprio diário',
 'Nas entradas de 04/01 a 08/02, Firael admite voltar aos jogos, quebrar a promessa aos companheiros, omitir o limite de derrotas que calculava e, depois, perder deliberadamente para romper o selo. Relata um pacto de não agressão a ele, Timo, Fash e Kael, planeja levar o Cérebro ao covil do norte e admite mentir ao grupo sobre seu paradeiro. Isso acrescenta intenção e decisões narradas pelo próprio personagem; não prova ausência de influência mental. '+ref(F,'04/01, 15/01, 18/01 e 08/02; parágrafos 46–175, 274–339 e 364–395')+'\n\nNa entrada solo de 12/02, narra cinco dias de reclusão e quarenta de pregação, dá ao Cérebro o nome Kharzûn, a Mente-Registro, organiza arquivos secretos entre anões e humanos e recebe um primeiro fragmento de poder psíquico ilitídeo. Diz que Kharzûn o mandou ajudar Timo e transmitir informações, combinando proteção, dívida pela morte de Rake e cálculo estratégico. O diário chama a doutrina de [[Itens/Dogma do Saber Imortal|Dogma do Saber Imortal]]. Esses acontecimentos pertencem à campanha antiga; não datam a situação atual. '+ref(F,'12/02 solo e continuação; parágrafos 1–44'))
add('Personagens/Cerebro Anciao',F,'Nome e libertação relatados por Firael',
 'Firael escreve que deu ao Cérebro o nome **Kharzûn, a Mente-Registro**. A entrada de 08/02 descreve expressamente o rompimento do selo e das correntes após derrotas propositais, com acordo de seguir ao covil do norte de [[Personagens/Hourian Haurim|Hourian]]. A narrativa fornece testemunho explícito de libertação na época antiga; não demonstra que o corpo esteja nesse covil setenta anos depois. '+ref(F,'12/02 e 08/02; parágrafos 7–9, 71–86 e 137–175')+'\n\nAs afirmações sobre colônia devastada, capacidade sem rede, história dos povos e funcionamento dos portais são falas atribuídas ao Cérebro dentro do diário. A interpretação de que não representava ameaça global naquele momento é condicional à falta de estrutura, não garantia de inocuidade. '+ref(F,'08/02; parágrafos 81–133'),{
 'Não foram adotados nomes próprios ou títulos adicionais do documento Personagens e Heróis, marcado para revisão de continuidade.':'A documentação anterior não adotava nomes próprios de Personagens e Heróis; o diário de Firael agora fornece diretamente o nome Kharzûn, a Mente-Registro, como nome dado por ele ao Cérebro.',
 'Autoridade superior atual confirmada; condição material da prisão, corpo e eventual libertação não são descritos inequivocamente. Não se conclui a libertação apenas contando derrotas sem conhecer os efeitos exatos do selo.':'Autoridade superior atual confirmada. A condição física e a localização atuais permanecem desconhecidas; a libertação antiga é descrita explicitamente no diário de Firael acrescentado à base, distinguindo-se de uma conclusão por contagem de derrotas.'})
p=B/'Personagens/Cerebro Anciao.md';m,s=split(p);m['aliases']=list(dict.fromkeys(m['aliases']+['Kharzûn','Kharzun','Mente-Registro']));write(p,m,s)
add('Faccoes/Organizacao de Firael',F,'Fundação e doutrina na campanha antiga',
 'O diário de 08/02 apresenta o [[Itens/Dogma do Saber Imortal|Dogma do Saber Imortal]] e um convite aos companheiros para o séquito e a tatuagem psiônica. Em 12/02, Firael relata a nomeação de Kharzûn, cinco dias de penitência, quarenta de pregação secreta e a aproximação de influentes anões e humanos. Dois espaços guardariam relatos tidos como bons e ruins, transmitidos ao Cérebro como arquivo vivo. Isso documenta a presença de participantes não ilitídeos na fase de fundação, sem dar cadastro ou hierarquia completa da organização atual. '+ref(F,'08/02 e 12/02; parágrafos 1–44 e 137–175')+'\n\nAs rezas usam “Conclave”, mas isso é vocabulário litúrgico nesta fonte; não torna todas as organizações chamadas Conclave uma só. A alegação de que a pregação preserva saber deve ser distinguida da obtenção de conhecimento por cérebros descrita nas fontes atuais. A filiação dos companheiros convidados não é confirmada pelo convite. '+ref(F,'12/02; As Três Rezas'))
new('Itens/Dogma do Saber Imortal','Dogma do Saber Imortal','item',F,
 'Doutrina escrita por [[Personagens/Firael|Firael]] ao se ligar ao [[Personagens/Cerebro Anciao|Cérebro Ancião / Kharzûn]], na fundação do [[Faccoes/Organizacao de Firael|Séquito de Kharzun]]. Não é identificado como um artefato mágico físico. '+ref(F,'08/02; parágrafos 145–157')+'\n\n## Princípios registrados\n\nO saber é apresentado como imortalidade, acima da carne; toda mente é tratada como livro; ignorância é o pecado; o coletivo deve preservar conhecimento; evolução exige superar limites biológicos. São preceitos e autojustificativas do narrador, sem validar suas promessas de preservação ou seus métodos.\n\n## Rezas e prática\n\nEm 12/02 há três rezas: pública, juramento reservado aos influentes e íntima. Associam Kharzûn à Mente-Registro, disciplina, lei, império, ascensão e continuidade. O texto completo das rezas e dos mandamentos está na fonte integral. '+ref(F,'12/02; parágrafos 11–23'),campaigns=['fash'])
add('Personagens/Furion',F,'Cena recuperada no diário de Firael',
 'Na entrada de 08/02, o povo da floresta chega reverenciando Timo como escolhido de Silvanus. Firael segue com Furion, descrito como profeta humanoide de traços arbóreos, até um assentamento de casas integradas às árvores para investigar animais luminosos. Firael narra observar um leopardo que, transformado, continua sem fala e agressivo; ao final são eliminados o leopardo e dois pássaros afetados. A fonte dá cena, função e missão a Furion, superando a existência apenas no documento de continuidade. Não identifica automaticamente o ente sem nome do diário de Fash, não situa a vila em Loraeth e não informa destino posterior de Furion. '+ref(F,'08/02; parágrafos 178–211'),{
 'Essa fonte está marcada revisar_continuidade; a menção é preservada como proveniência, sem atestar automaticamente presença na campanha material.':'Essa fonte estava marcada revisar_continuidade; a cena acrescentada do diário de Firael agora documenta sua participação na campanha antiga.',
 'Continuidade e destino pessoal não verificados. A nota registra a evidência existente e a pergunta necessária, sem completar uma biografia por invenção.':'Participação na missão dos animais de luz documentada no diário de Firael; destino posterior desconhecido.'})
add('Eventos/Destruicao da esfera de Elena',F,'Animais de luz investigados por Firael',
 'A entrada de 01/12 descreve a explosão da esfera, a catatonia do líder e a propagação após o golpe no cavalo, atingindo o clérigo. Em 04/01, Firael atribui ao Cérebro a informação de transformação em seres iluminados. Em 08/02, já no povo da floresta com [[Personagens/Furion|Furion]], narra a eliminação de um leopardo e dois pássaros transformados, após tentativas de observação e comunicação. Esse é um desfecho local; não determina a extensão total da epidemia, o destino final dos líderes ou a cura de outros atingidos. '+ref(F,'01/12, 04/01 e 08/02; parágrafos 178–211, 364–395 e 434–467'))
add('Eventos/Aprisionamento do Cerebro',F,'Rompimento do selo narrado pelo participante',
 'No diário de 08/02, Firael diz que perdeu partidas deliberadamente e pediu magias para acelerar o enfraquecimento: as correntes cederam e o selo se rompeu. Relata pacto de não agressão e plano de deslocamento ao covil do norte de Hourian; depois assume ter mentido aos companheiros sobre o paradeiro do Cérebro. O testemunho expresso acrescenta a libertação antiga, sem determinar a posição física atual. '+ref(F,'08/02; parágrafos 71–86 e 137–175'))
add('Lugares/Covis de Hourian Haurim',F,'Estatueta, mapa e covil do norte',
 'O diário de Firael relata que o Cérebro pronunciou **Pyrotharxaziondrakulmorthvyrion**, apresentado como nome verdadeiro de Hourian/Haurim. A estatueta teria reagido, revelando um mapa e três localizações. Firael combina que o Cérebro liberto siga ao covil do norte e depois admite conhecer esse destino enquanto o omite ao grupo. O relato acrescenta três locais e a função planejada do covil setentrional; não fornece coordenadas nem resolve as duas montanhas ao sul da planilha. A ocupação no presente continua desconhecida. '+ref(F,'08/02; parágrafos 71–86 e 175'))
add('Personagens/Hourian Haurim',F,'Nome verdadeiro atribuído e estatueta',
 'No relato de Firael, o Cérebro revela **Pyrotharxaziondrakulmorthvyrion** como nome verdadeiro do dragão chamado Haurim nessa entrada. A estatueta reage e revela um mapa de três covis. A grafia canônica Hourian, confirmada pelo jogador, permanece; o nome extenso é registrado como revelação atribuída ao Cérebro nesta fonte. Isso não confirma que o dragão esteja vivo nem identifica a revoada que o matou como a Revoada Branca. '+ref(F,'08/02; parágrafos 71–79'))
add('Faccoes/Zodiacos',F,'Relato antigo recebido por Firael',
 'O Cérebro, segundo o diário de 08/02, descreve um líder venerado como divindade e supostamente renascente, doze generais com um artefato cada e perda de poder após o extravio dos artefatos. Firael registra símbolos na construção mais alta da cidade drow. Sua suspeita de que Kael fosse o líder ou integrasse o Zodíaco é conjectura pessoal motivada por reincarnação, não identificação confirmada. O quadro é da campanha antiga e não completa os ritos ou a estrutura da época de Okay. '+ref(F,'08/02; parágrafos 88–96'))
add('Itens/Livro das tres bruxas',F,'Conteúdo descrito pelo leitor Firael',
 'Na entrada de 06/11, Firael descreve um compilado de rituais e registros compartilhados por Morvessh, Selara e Lyvessa, com Lua, Mar e Grama, o Nó e referências a Elena como Serethyn. Considera que os rituais alimentam o Nó e que a biografia de Elena pode ter sido construída; sua natureza superior permanece hipótese derivada dos escritos. O diário não demonstra identidade desse compilado com o volume mais poderoso do dragão negro ou todas as cópias posteriores. '+ref(F,'06/11; parágrafos 519–539'))
add('Lugares/Cidade drow',F,'Reorganização e portais no diário adicional',
 'Após a queda do Druida Sangrento, Firael narra a libertação dos anões, a aceitação de humanos no assentamento e obras de Timo para reforçar acessos. A entrega da cidade humana a uma comunidade miscigenada e o pagamento mensal de 100 peças de ouro são propostas discutidas, não tratados comprovadamente executados. O Clã da Carne Negra é nomeado como ameaça de trolls ainda sem contato direto em 29/01. '+ref(F,'25/01 e 29/01; parágrafos 213–238')+'\n\nEm 08/02, atribui ao Cérebro três descrições: Portal do Espelho para mundo invertido ligado às bruxas; Portal do Abismo facilitador de invocação, dependente de conjurador e acordo; Portal da Noite para a ilha dos Elfos da Noite. As descrições ajudam a relacionar os três rótulos não riscados da planilha, sem resolver rótulos riscados ou as coordenadas K28/L28. Não se confundem com as portas de Arkhavel na campanha de Glim. '+ref(F,'08/02; parágrafos 117–133'))

# Prelúdio de Ryld: biografia narrada, sem promover devoção da família a origem de seus poderes.
add('Personagens/Ryld',R,'Prelúdio fornecido pelo jogador',
 'O documento recebido como **Préludio Ryld** tem o narrador chamado Ryldan por seus pais e descreve a família Velkyn. Sua origem passa a ser documentada por fonte diretamente fornecida, preservando os limites de perspectiva. [[Faccoes/Casa Velkyn|Casa Velkyn]] vive numa caverna próxima à costa oriental e conserva uma [[Lugares/Biblioteca da Casa Velkyn|biblioteca]]; seu pai é [[Personagens/Zaerith Velkyn|Zaerith]], guardião dos registros, e sua mãe [[Personagens/Lythrana Velkyn|Lythrana]], clériga de [[Personagens/Eilistraee|Eilistraee]]. Tem um irmão mais velho, [[Personagens/Vaerion Velkyn|Vaerion]], e uma irmã mais nova, [[Personagens/Sylra Velkyn|Sylra]]. '+ref(R,'capítulos 1 e 10')+'\n\n## Formação e primeira jornada\n\nCresce estudando e catalogando registros, aprende armas com Vaerion, prefere bestas menores e recebe cinco anos de treinamento com patrulheiros: furtividade, rastreamento, lâminas curtas, armadilhas e fechaduras. Mantém contato com um [[Lugares/Vilarejo costeiro do preludio de Ryld|vilarejo humano costeiro]]. Busca pistas do irmão desaparecido e encontra uma [[Lugares/Passagem colapsada de Vaerion|passagem colapsada por magia]], atribuindo ao grupo dele uma defesa sacrificial. Não encontra os corpos; essa reconstituição permanece inferência do narrador. '+ref(R,'capítulos 2–6')+'\n\n## Fé familiar e limites\n\nA mãe lhe entrega um símbolo de prata de Eilistraee; Sylra também segue seus ensinamentos. Isso documenta vínculo familiar e objeto devocional, sem identificar a origem da luz de Ryld ou confirmar Pelor. O capítulo 10 termina na véspera das Doze Noites Rubras com preparativos da mãe após uma resposta divina que ela relata. O texto não descreve o destino posterior de Ryld ou da família na campanha atual. '+ref(R,'capítulos 5, 8 e 10')+'\n\n## Divergências editoriais preservadas\n\nO capítulo 5 diz que partiu aos 85 anos; o capítulo 6 situa a primeira saída após o treinamento aos 86. O capítulo 6 aparece duas vezes integralmente, seguido do capítulo 8, sem capítulo 7 identificado. A fonte conserva tudo; não se fixou uma idade pela escolha silenciosa de uma versão. '+ref(R,'capítulos 5–8'),{
 'O documento Personagens e Heróis traz uma família de Ryldan Velkyn, mas está marcado para revisão; essa biografia não foi integrada a Ryld por semelhança do nome.':'A família de Ryldan Velkyn aparecia em Personagens e Heróis sob revisão; o novo Préludio Ryld agora fornece diretamente uma biografia narrada dessa família, sem validar por extensão outros detalhes do documento antigo.',
 'O nome do novo personagem e o destino de Ryld na ficção não foram informados.':'O novo personagem foi posteriormente identificado como Aelion; o destino de Ryld na ficção continua sem informação.'})
p=B/'Personagens/Ryld.md';m,s=split(p);m['aliases']=list(dict.fromkeys(m['aliases']+['Ryldan','Ryldan Velkyn']));write(p,m,s)
family=[
 ('Zaerith Velkyn','Pai de [[Personagens/Ryld|Ryldan/Ryld]], [[Personagens/Vaerion Velkyn|Vaerion]] e [[Personagens/Sylra Velkyn|Sylra]], esposo de [[Personagens/Lythrana Velkyn|Lythrana]]. É o principal guardião da [[Lugares/Biblioteca da Casa Velkyn|biblioteca]], sem ser apresentado como governante ou comandante militar. Ensina respeito pelos registros, recebe os relatos do filho e mostra um livro sobre antigos acordos humano-drow. A história do livro é relato documental interno, não verdade global independente. Seu destino após a véspera das Doze Noites Rubras não é informado.','capítulos 1, 6, 9 e 10'),
 ('Lythrana Velkyn','Mãe de [[Personagens/Ryld|Ryldan/Ryld]], [[Personagens/Vaerion Velkyn|Vaerion]] e [[Personagens/Sylra Velkyn|Sylra]], esposa de [[Personagens/Zaerith Velkyn|Zaerith]]. Clériga de [[Personagens/Eilistraee|Eilistraee]], conduz cantos, danças e preces sob a luz lunar na [[Faccoes/Casa Velkyn|Casa Velkyn]]. Dá ao filho um símbolo de prata. Na véspera das Doze Noites Rubras afirma ter recebido instrução da deusa para preparar o povo e organiza famílias, mantimentos e reforço de passagens. A resposta divina é relatada por ela; seu destino posterior não consta.','capítulos 1, 5 e 10'),
 ('Vaerion Velkyn','Irmão mais velho de [[Personagens/Ryld|Ryldan/Ryld]] e [[Personagens/Sylra Velkyn|Sylra]], filho de [[Personagens/Zaerith Velkyn|Zaerith]] e [[Personagens/Lythrana Velkyn|Lythrana]]. Tem noventa anos quando Ryldan tem dez. Treina o irmão e lidera patrulha das fronteiras profundas da [[Faccoes/Casa Velkyn|Casa Velkyn]]. Desaparece com os guerreiros; mais tarde Ryldan encontra barricada, restos de batalha e [[Lugares/Passagem colapsada de Vaerion|túnel colapsado por magia]]. Interpreta que resistiram para bloquear a invasão. Nenhum corpo é encontrado e o texto não confirma sua morte.','capítulos 1, 2 e 6'),
 ('Sylra Velkyn','Irmã mais nova de [[Personagens/Ryld|Ryldan/Ryld]] e [[Personagens/Vaerion Velkyn|Vaerion]], filha de [[Personagens/Zaerith Velkyn|Zaerith]] e [[Personagens/Lythrana Velkyn|Lythrana]]. Nasce quando Ryldan tem 21 anos. Cresce entre biblioteca e histórias; acompanha visitas à superfície e segue [[Personagens/Eilistraee|Eilistraee]]. Seis meses antes das Doze Noites Rubras aproxima-se de uma família de agricultores com um menino e uma menina, compartilhando histórias, canções e danças. Não há confirmação do destino posterior dessa família ou dela. Não identificar as crianças com personagens conhecidos por mera semelhança.','capítulos 1, 3 e 8'),
]
for name,body,where in family:new('Personagens/'+name,name,'personagem',R,body+' '+ref(R,where))
new('Personagens/Eilistraee','Eilistraee','personagem',R,
 'Divindade venerada por [[Personagens/Lythrana Velkyn|Lythrana]] e [[Personagens/Sylra Velkyn|Sylra]], apresentada no prelúdio como guia para drows que procuram uma vida além da crueldade das profundezas. Os rituais da comunidade incluem canto, dança e prece sob luz da lua. Lythrana relata um aviso divino na véspera das Doze Noites Rubras. A nota registra a representação na campanha, sem importar atributos externos ou confirmar que a luz de Ryld deriva dela. '+ref(R,'capítulos 1, 5, 8 e 10'))
new('Faccoes/Casa Velkyn','Casa Velkyn','faccao',R,
 'Comunidade drow ligada à família de [[Personagens/Ryld|Ryldan/Ryld]], numa caverna próxima à costa oriental do continente, com abertura para a luz da superfície. Sua força é apresentada como preservação de memória, não domínio militar. [[Personagens/Zaerith Velkyn|Zaerith]] guarda a [[Lugares/Biblioteca da Casa Velkyn|biblioteca]]; [[Personagens/Lythrana Velkyn|Lythrana]] conduz rituais de Eilistraee; [[Personagens/Vaerion Velkyn|Vaerion]] patrulha as fronteiras. O desaparecimento da patrulha e a passagem colapsada são descritos antes das Doze Noites Rubras. Destino posterior e localização cartográfica exata não constam. '+ref(R,'capítulos 1, 2, 6 e 10'))
new('Lugares/Biblioteca da Casa Velkyn','Biblioteca da Casa Velkyn','lugar',R,
 'Acervo de manuscritos, mapas de cavernas e relatos de viajantes, guardado por [[Personagens/Zaerith Velkyn|Zaerith]] na [[Faccoes/Casa Velkyn|Casa Velkyn]], próximo à costa oriental. [[Personagens/Ryld|Ryldan/Ryld]] cresce entre os livros, depois cataloga e restaura registros. O pai mostra um volume antigo sobre proteção indireta de comunidades humanas por casas drow em troca de metade da produção agrícola e pecuária; a alegação está mediada pelo livro e pela memória do narrador. Não se confunde com a [[Lugares/Biblioteca do beholder|biblioteca do beholder]]. '+ref(R,'capítulos 1 e 9'))
new('Lugares/Vilarejo costeiro do preludio de Ryld','Vilarejo costeiro do prelúdio de Ryld','lugar',R,
 'Povoado humano sem nome, próximo ao mar e às entradas de cavernas da [[Faccoes/Casa Velkyn|Casa Velkyn]]. Tem casas de madeira, barcos, pesca, campos cultivados e floresta próxima. [[Personagens/Ryld|Ryldan/Ryld]] mantém contatos locais e observa jovens humanos crescerem e partirem; [[Personagens/Sylra Velkyn|Sylra]] participa das visitas e se aproxima de uma família de agricultores. Não há base para identificá-lo como Eral ou a aldeia de Glim. A história termina na véspera das Doze Noites Rubras, sem mostrar o destino do povoado. '+ref(R,'capítulos 3, 4, 8 e 10'))
new('Lugares/Passagem colapsada de Vaerion','Passagem colapsada de Vaerion','lugar',R,
 'Rota subterrânea antiga entre territórios de casas drow hostis e a região da [[Faccoes/Casa Velkyn|Casa Velkyn]]. [[Personagens/Ryld|Ryldan/Ryld]] encontra barricada, armas, armaduras fragmentadas e runas queimadas indicativas de colapso provocado por magia. Deduz que [[Personagens/Vaerion Velkyn|Vaerion]] e sua patrulha sustentaram uma defesa até selar a passagem. Sem corpos encontrados, a atribuição e o sacrifício são reconstrução do narrador, não prova da morte de cada integrante. Não há coordenadas ou equivalência com túneis de Eral. '+ref(R,'capítulo 6, preservado em duas ocorrências'))

pending('PC-008',F,'A entrada de 08/02 descreve explicitamente Firael provocando derrotas até romper selo e correntes, com plano de levar o Cérebro ao covil do norte. A de 12/02 o nomeia Kharzûn e relata comunicação e poder psíquico. A libertação antiga passa a ter testemunho expresso; a localização física no presente permanece sem fonte. '+ref(F,'08/02 e 12/02'),'Onde está e em que condição física se encontra o Cérebro no presente da campanha de Glim? A libertação antiga já está explicitamente narrada por Firael.')
pending('FC-002',F,'A fundação é detalhada: pregação secreta entre anões e humanos, duas áreas de relatos e rezas diferenciadas para público, influentes e intimidade. O Cérebro recebe de Firael o nome Kharzûn, a Mente-Registro. Isso descreve a fase antiga e não um cadastro atual completo. '+ref(F,'12/02; parágrafos 1–44'),'Como evoluíram a composição e a hierarquia do Séquito até o presente? Nome e práticas de fundação já estão documentados.')
pending('PC-039',F,'Há agora uma cena expressa: Furion acompanha Firael ao assentamento do povo da floresta para investigar animais luminosos, no contexto da comitiva que reverencia Timo. Isso documenta função e participação antiga; não confirma identidade com o ente sem nome, Loraeth ou destino posterior. '+ref(F,'08/02; parágrafos 178–211'),'Qual foi o destino posterior de Furion? A participação na investigação dos animais de luz já está documentada.')
pending('LG-005',F,'A nova fonte descreve três portais: Espelho, Abismo e Noite, com os destinos e condições registrados na nota da cidade drow. Há correspondência nominal com os três rótulos sem rasura da planilha. Permanecem os significados dos dois riscados e as coordenadas K28/L28; não fundir mapas e eras. '+ref(F,'08/02; parágrafos 117–133'))
pending('LG-008',F,'A estatueta revela três localizações, com plano de o Cérebro ocupar o covil do norte. Não há coordenadas, nomes de montanhas ou ocupação no presente, e o sul da planilha não foi transformado em norte. '+ref(F,'08/02; parágrafos 71–86 e 175'))
pending('FC-015',F,'Firael recebe do Cérebro relato de doze generais, artefatos perdidos e líder renascente, e especula sobre Kael. Isso documenta tradição e conjectura antigas, não os ritos atuais ou identificação de Kael como líder. '+ref(F,'08/02; parágrafos 88–96'))
pending('EV-002',F,'Há desfecho local: leopardo e dois pássaros luminosos são eliminados durante a investigação com Furion. Isso não encerra a epidemia nem determina o destino do líder e do clérigo. '+ref(F,'08/02; parágrafos 178–211'))
pending('IT-002',F,'O compilado das três bruxas tem conteúdo descrito em 06/11: rituais, Nó, Elena/Serethyn e a tradição comum. Isso não iguala o tomo à cópia em papiros ou ao volume do dragão. '+ref(F,'06/11; parágrafos 519–539'))
pending('PC-014',R,'O prelúdio documenta família, formação e o símbolo de Eilistraee entregue pela mãe. Não identifica a origem da luz, não confirma Pelor e não narra a inspeção dos Mind Shredders nem o destino após a saída do grupo. '+ref(R,'capítulos 1–10'))

# Comparação reprodutível entre fontes, sem votação de versões nem deleção de repetições.
out=ROOT/'docs/importacoes/2026-10-30-firael-ryld'
load=lambda name:json.loads((out/(name+' - paragrafos.json')).read_text(encoding='utf-8'))
a=load('Diario de Firael - versao completa');v1=load('Diario de Firael - variante 1');v2=load('Diario de Firael - variante 2');ry=load('Preludio de Ryld')
norm=lambda text:re.sub(r'\s+',' ',re.sub(r'\s*[–-]\s*CONTABILIZADO PELO MESTRE','',text)).strip()
diffs=[]
sm=difflib.SequenceMatcher(None,[norm(x['texto']) for x in v1[227:]],[norm(x['texto']) for x in v2],autojunk=False)
for tag,i,j,k,l in sm.get_opcodes():
 if tag!='equal':diffs.append({'tipo':tag,'variante_1':[{'paragrafo':x['paragrafo'],'texto':x['texto']} for x in v1[227:][i:j]],'variante_2':[{'paragrafo':x['paragrafo'],'texto':x['texto']} for x in v2[k:l]]})
comparison={'completa_vs_variante_1_texto_integral_compartilhado_identico':[x['texto'] for x in a[45:]]==[x['texto'] for x in v1], 'completa_paragrafos_adicionais':45,'variantes_1_2_normalizacao':'Remove apenas rótulo CONTABILIZADO PELO MESTRE e normaliza espaços para comparar narrativa. Fontes integrais preservam esses rótulos.','diferencas_narrativas':diffs,'ryld_capitulo_6_repetido_identico':[x['texto'] for x in ry[615:773]]==[x['texto'] for x in ry[773:931]],'ryld_ocorrencias_paragrafos':[[616,773],[774,931]],'ryld_idade_primeira_jornada':{'capitulo_5':85,'capitulo_6':86},'decisao':'Nenhuma variante apagada ou escolhida como verdade única; datas dos cabeçalhos não viram anos do cenário.'}
(out/'comparacao.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(diffs)==3

table='\n'.join('| '+x['texto'].replace('|','\\|')+' | '+str(x['paragrafo'])+' |' for x in a if x['texto'].startswith('Diário de Firael'))
view='''Quatro DOCX recebidos em 30/10/2026, com originais preservados, conversão integral e auditoria por parágrafo. Esta visão liga as fontes às notas; não substitui a leitura dos narradores.

## Fontes e repetição

- '''+ref(F,'Diário de Firael — versão mais abrangente recebida')+''': 17 entradas, de 30/10/2025 a 12/02/2026, em ordem inversa na fonte.
- '''+ref(V1,'Diário de Firael — variante 1')+''': 15 entradas; seu trecho coincide textualmente com a parte compartilhada da versão mais abrangente. Essa última acrescenta 45 parágrafos, incluindo duas entradas de 12/02.
- '''+ref(V2,'Diário de Firael — variante 2')+''': 11 entradas; além de rótulos editoriais diferentes, contém três diferenças narrativas verificadas.
- '''+ref(R,'Prelúdio de Ryld')+''': capítulos 1–6, repetição integral do capítulo 6 e capítulos 8–10; não há capítulo 7 identificado.

As datas são rótulos dos documentos, sem equivalência demonstrada com o calendário do mundo. A campanha de Fash e a de Glim permanecem separadas por cerca de setenta anos. Informações íntimas de Firael e lembranças de Ryld não são conhecimento automático de Glim.

## Entradas de Firael e localizadores

| Cabeçalho preservado | Parágrafo inicial no DOCX mais abrangente |
| --- | --- |
'''+table+'''

## Divergências que exigem cuidado

| Cena | Versão mais abrangente e variante 1 | Variante 2 |
| --- | --- | --- |
| Silêncio contra a serpente, 15/12 | Fash conjura | Timo conjura |
| Avistamento nas copas, 30/10 | Fash avista | Timo avista |
| Árvore corrompida, 30/10 | Firael intervém; Fash conclui com óleo e fogo | Firael dá o golpe final |

As ações incompatíveis permanecem atribuídas às respectivas fontes. A marca “CONTABILIZADO PELO MESTRE” foi preservada como anotação, sem ser tratada como confirmação independente de cada frase.

No prelúdio, a primeira jornada é aos 85 anos no capítulo 5 e aos 86 no capítulo 6. As duas idades foram preservadas sem fixar uma delas. A grafia “Doze Noites Rubras” está mantida na fonte; não redefine sozinha o evento denominado Doze Dias Rubros / Noite Eterna na base.

## Novas informações integradas

- [[Personagens/Firael]], [[Personagens/Cerebro Anciao]] e [[Faccoes/Organizacao de Firael]]: intenção declarada, libertação antiga, nome Kharzûn, fundação, rezas e [[Itens/Dogma do Saber Imortal]].
- [[Personagens/Furion]] e [[Eventos/Destruicao da esfera de Elena]]: investigação e desfecho local de três animais luminosos.
- [[Personagens/Hourian Haurim]] e [[Lugares/Covis de Hourian Haurim]]: nome verdadeiro atribuído, estatueta, três covis e acordo sobre o covil do norte.
- [[Lugares/Cidade drow]], [[Faccoes/Zodiacos]] e [[Itens/Livro das tres bruxas]]: portais, assentamento, tradição e leitura dos livros com perspectiva identificada.
- [[Personagens/Ryld]], [[Faccoes/Casa Velkyn]], [[Personagens/Zaerith Velkyn]], [[Personagens/Lythrana Velkyn]], [[Personagens/Vaerion Velkyn]], [[Personagens/Sylra Velkyn]] e [[Personagens/Eilistraee]]: origem e família.
- [[Lugares/Biblioteca da Casa Velkyn]], [[Lugares/Vilarejo costeiro do preludio de Ryld]] e [[Lugares/Passagem colapsada de Vaerion]]: lugares sem equivalência inventada com Eral ou a aldeia de Glim.

## Pendências com novas fontes

PC-008, FC-002, PC-039, LG-005, LG-008, FC-015, EV-002, IT-002 e PC-014 foram complementadas. As partes ainda desconhecidas ficam explícitas. Nenhuma dessas consultas foi declarada totalmente resolvida apenas pela importação; fatos antigos não preenchem automaticamente o presente.
'''
new('Visoes/Novas fontes - Firael e Ryld','Novas fontes — Firael e Ryld','visao',F,view,campaigns=['fash','glim'])
p=B/'Visoes/Novas fontes - Firael e Ryld.md';m,s=split(p);m['origens']=[F,V1,V2,R];write(p,m,s)
for rel,src,body in [
 ('Campanhas/Fash',F,'Novas entradas de [[Personagens/Firael|Firael]] detalham o pacto e a libertação antiga do Cérebro, a fundação do culto, os portais e a missão de Furion. Ver [[Visoes/Novas fontes - Firael e Ryld|visão das fontes e divergências]]. '+ref(F,'Diário integral')),
 ('Campanhas/Glim',R,'O [[Fontes/Documentos/Preludio de Ryld|prelúdio de Ryld]] documenta a Casa Velkyn, sua família e a formação anterior às Doze Noites Rubras. Não informa o destino do personagem depois de se afastar dos Magníficos. Ver [[Visoes/Novas fontes - Firael e Ryld|fontes e limites]].'),
]:add(rel,src,'Fontes adicionais recebidas em 30/10/2026',body)
p=B/'Fontes/Indice.md';p.write_text(p.read_text(encoding='utf-8')+'\n## DOCX recebidos em 30/10/2026 — Firael e Ryld\n\n'+ '\n'.join('- '+ref(src,label) for src,label in [(F,'Diário de Firael — versão mais abrangente'),(V1,'Diário de Firael — variante 1'),(V2,'Diário de Firael — variante 2'),(R,'Prelúdio de Ryld')])+'\n\n[[Visoes/Novas fontes - Firael e Ryld|Integração, localizadores e divergências entre versões]].\n',encoding='utf-8')
print(json.dumps({'novas_notas':10,'fontes':4,'pendencias_complementadas':9,'diferencas_narrativas':len(diffs),'capitulo_repetido':comparison['ryld_capitulo_6_repetido_identico']},ensure_ascii=False))
