"""Integra a navegação enciclopédica e o banco de pendências, sem tocar fontes."""
from pathlib import Path
import argparse
import json
import re
from fila_revisao import separate, index_body, script_body
from enciclopedia_comum import ROOT, CONTEUDO, escrever as escrever_nota, fonte, link

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--somente-indices', action='store_true',
                    help='Atualiza navegação e manifesto sem reescrever campanhas ou visões curadas.')
args = parser.parse_args()
CONFIRMACAO_SABATINA = 'Fontes/Confirmacoes/2026-10-29 - Sabatina de continuidade - Fash e Timo'
CONFIRMACAO_GRIMORIO = 'Fontes/Confirmacoes/2026-10-29 - Grimorio de Glim e Shar'
CONFIRMACAO_FAMILIAR = 'Fontes/Confirmacoes/2026-10-29 - Identidade do familiar de Lilo'
CONFIRMACAO_PICHE = 'Fontes/Confirmacoes/2026-10-29 - Valor afetivo de Piche'
CONFIRMACAO_RUNA = 'Fontes/Confirmacoes/2026-10-29 - Reconhecimento da runa por estudo'
CONFIRMACAO_DIVINDADES = 'Fontes/Confirmacoes/2026-10-29 - Vinculos divinos e Mystra'
CONFIRMACAO_LACUNA = 'Fontes/Confirmacoes/2026-10-29 - Ryld e sessao recente sem gravacao'
CONFIRMACAO_ALDEIA = 'Fontes/Confirmacoes/2026-10-29 - Nome da aldeia de Glim nao definido'
CONFIRMACAO_CRAVE = 'Fontes/Confirmacoes/2026-10-29 - Redencao de Crave e recuperacao do amuleto'
CONFIRMACAO_CINTO = 'Fontes/Confirmacoes/2026-10-29 - Cinto de Kord nao recuperado'
CONFIRMACAO_PRIORIDADES = 'Fontes/Confirmacoes/2026-10-29 - Tariun sem noticias e prioridade para contradicoes'
CONFIRMACAO_PORTAS = 'Fontes/Confirmacoes/2026-10-29 - Invisibilidade das portas no destino'
CONFIRMACAO_RETORNO = 'Fontes/Confirmacoes/2026-10-29 - Porta mantida aberta para retorno'
CONFIRMACAO_COORDENADAS = 'Fontes/Confirmacoes/2026-10-29 - Coordenadas K28 L28 sem confirmacao'
CONFIRMACAO_HOURIAN = 'Fontes/Confirmacoes/2026-10-29 - Grafia confirmada de Hourian'


def escrever(caminho, titulo, tipo, *positional, **kwargs):
    if args.somente_indices and tipo != 'indice':
        return None
    return escrever_nota(caminho, titulo, tipo, *positional, **kwargs)


def meta(path):
    raw=path.read_text(encoding='utf-8')
    front=raw.split('---',2)[1]
    out={}
    for line in front.splitlines():
        if ': ' not in line:
            continue
        k,v=line.split(': ',1)
        try: out[k]=json.loads(v)
        except json.JSONDecodeError: out[k]=v.strip('"\'')
    return out


def dest(path):
    return path.relative_to(CONTEUDO).as_posix().removesuffix('.md')


def listing(paths):
    return '\n'.join('- '+link(dest(p),meta(p).get('titulo',p.stem)) for p in paths)


OUTPUTS=[]
categories=[('Personagens','Personagens'),('Lugares','Lugares'),('Faccoes','Facções e grupos'),
            ('Criaturas','Criaturas'),('Eventos','Acontecimentos'),('Itens','Itens, poderes e mecanismos'),
            ('Cronologia','Cronologia'),('Campanhas','Campanhas')]
counts={}
for folder,title in categories:
    pages=sorted((CONTEUDO/folder).glob('*.md'))
    pages=[p for p in pages if p.name!='Indice.md']
    counts[folder]=len(pages)
    intro=('Notas com informação documentada, relações e pendências. As citações distinguem a fonte consultada; relatos, sonhos e hipóteses conservam essa condição.\n\n'
           +listing(pages)+'\n\n'+link('Pendencias/Indice','Revisão de contradições e sequência')+' · '+link('Inicio','Início'))
    OUTPUTS.append(escrever(folder+'/Indice',title,'indice',['fash','glim'],intro,[],status='organizado'))

question_paths=sorted((CONTEUDO/'Pendencias').rglob('*.md'))
questions=[]
for p in question_paths:
    m=meta(p)
    if m.get('tipo')=='pendencia':
        questions.append(dict(m,caminho=dest(p)))
Q={q['id']:q for q in questions}
statuses=['aberta','parcialmente_respondida','respondida']
for q in questions:
    if q.get('status') not in statuses:
        raise ValueError('Status de pendência não reconhecido: '+q['id']+' '+str(q.get('status')))
review_groups,active_questions,fila_sabatina,waiting_questions,consolidated_questions=separate(questions)
unanswered_questions=[q for q in questions if q['status']!='respondida']
answered_questions=[q for q in questions if q['status']=='respondida']
status_counts={status:sum(q['status']==status for q in questions) for status in statuses}


def qlink(code,label=None):
    q=Q[code]
    if label is None and q['status']=='parcialmente_respondida':
        label=q['titulo']+' — parcialmente respondida; consultar o restante registrado'
    return link(q['caminho'],label or q['titulo'])


def qtable(rows):
    lines=['| ID | Tema registrado | Prioridade | Estado |','| --- | --- | --- | --- |']
    for q in rows:
        label=q['titulo'].split(' — ',1)[-1].replace('|','/')
        state=q['status'].replace('_',' ')
        lines.append('| '+qlink(q['id'],q['id'])+' | '+label+' | '+q['prioridade']+' | '+state+' |')
    return '\n'.join(lines)


priority_counts={p:sum(q['prioridade']==p for q in active_questions) for p in ['alta','media','baixa']}
intro=index_body(review_groups,active_questions,fila_sabatina,waiting_questions,consolidated_questions,qlink,link)
OUTPUTS.append(escrever('Pendencias/Indice','Revisão de contradições e sequência','indice',['fash','glim'],intro,['Fontes/Confirmacoes/2026-10-30 - Criterio de revisao contradicoes e fluxo'],status='organizado',atualizado='2026-10-30'))
body=script_body(active_questions,fila_sabatina,waiting_questions,consolidated_questions,qlink,link)
OUTPUTS.append(escrever('Pendencias/Roteiro da sabatina','Roteiro de revisão — contradições e sequência','indice',['fash','glim'],body,['Fontes/Confirmacoes/2026-10-30 - Criterio de revisao contradicoes e fluxo'],status='organizado',atualizado='2026-10-30'))

body='''A base preserva a fonte e a diferença entre uma afirmação nela registrada e uma confirmação do cenário. O quadro evita resolver divergências por semelhança de nomes ou pela mera data de uma nota.

| Tema | Tratamento atual | Registro |
| --- | --- | --- |
| Capital Carruan/Lazathar | Errata já confirmada; sonho e capital real separados. | [[Lugares/Carruan]], [[Lugares/Lazathar]] e esclarecimentos. |
| Okay: elfo cinza/meio-elfo | Meio-elfo, filho de humano e elfa cinzenta, confirmado pelo jogador em 29/10. “Elfo cinza” permanece no diário como percepção histórica retificada. | '''+qlink('PC-003','PC-003 — respondida')+'; '+fonte(CONFIRMACAO_SABATINA,'resposta literal')+''' |
| Tinkar/Eldrosia | Background confirmado como passado real de Fash em 29/10. Interpretações de Tinkar continuam perspectivas; correspondências exclusivas do sonho e geografia restante continuam abertas. | '''+qlink('PC-002','PC-002 — respondida')+'; '+fonte(CONFIRMACAO_SABATINA,'confirmação literal')+''' |
| Timo Pé-de-Musgo/Fesh | Timo pertence à campanha de Fash; Fesh é erro de grafia de Fash. Datas 530/536 não validadas: jogador declarou desconhecê-las; aguardar fontes ou mestre sem repetir a pergunta. | '''+qlink('PC-006','PC-006 — parcialmente respondida')+'; '+fonte(CONFIRMACAO_SABATINA,'confirmação literal')+''' |
| Dois Carlos de Eral | Pessoas distintas; o carpinteiro morreu no ataque a Eral e um demônio possuiu seu corpo já morto, usado na S26. | [[Personagens/Carlos carpinteiro]], [[Personagens/Carlos guarda]], [[Fontes/Confirmacoes/2026-10-30 - Morte de Carlos no ataque e possessao do cadaver|confirmação de 30/10]] e '''+qlink('PC-021','PC-021 — encerrada')+''' |
| Causa da epidemia de luz | Versão pública e correção em off separadas; desfecho ainda aberto. | [[Eventos/Destruicao da esfera de Elena]] e '''+qlink('EV-002','EV-002')+''' |
| Portais drow e rasuras | Cinco rótulos na planilha, dos quais dois estão riscados; restam três sem rasura. O significado e a correspondência com o diário permanecem abertos. | '''+qlink('LG-005','LG-005')+''' |
| Coordenadas K28/L28 e contexto de W23 | Divergência K28/L28 preservada; jogador não se recorda e a consulta aguarda fonte adicional. W23 está sob Ruínas, sem contradição automática floresta/ruína. | '''+qlink('LG-005','LG-005 — em espera')+'; '+fonte(CONFIRMACAO_COORDENADAS,'limite registrado')+''' |
| Distâncias goblinoides de Eral | S13 atribui quatro dias à informação de Tork; S14 registra estimativa de Glim de um dia, sem confirmação explícita no trecho. Não tratar como duas definições equivalentes antes de comparar trajetos. | '''+qlink('LG-003','LG-003 — conferência de contexto')+''' |
| Fechar portas de Arkhavel | Regra confirmada pelo jogador: invisível do lado do destino e mantida aberta para retorno. As formulações antigas foram preservadas como histórico. | '''+qlink('IT-005','IT-005 — respondida')+'; '+fonte(CONFIRMACAO_RETORNO,'regra confirmada')+''' |
| Conclaves e Círculo Vetrilus | Organizações e pontos geográficos mantidos distintos sem prova de identidade. | '''+qlink('FC-009','FC-009')+' e '+qlink('LG-016','LG-016')+''' |
| Livros das bruxas/dragão | Cópia e volume mais poderoso distinguidos; cadeia documental a completar. | '''+qlink('IT-002','IT-002')+''' |
| Noite Eterna/Lua Sangrenta | Evento e organização distintos; Doze Dias Rubros é nome confirmado do evento. | [[Eventos/Noite Eterna]] e [[Faccoes/Lua Sangrenta]] |
| Lilo e familiar | Aparência de Lilo e função de familiar de Glim confirmadas. Alma e memórias continuam sem confirmação; item encerrado pelo jogador e retirado das pendências, sem resolver o mistério. | '''+qlink('PC-010','PC-010 — encerrada; identidade incerta')+'; '+fonte(CONFIRMACAO_FAMILIAR,'resposta literal')+''' |
| Corpo de Piche | Glim o guarda pelo valor afetivo, confirmado pelo jogador. A resposta não atribui efeito mágico ao corpo. | '''+qlink('PC-011','PC-011 — respondida no escopo registrado')+'; '+fonte(CONFIRMACAO_PICHE,'resposta literal')+''' |
| Reconhecimento da runa | Glim reconheceu por estudo. A pergunta que pressupunha experiência pessoal anterior foi corrigida. | '''+qlink('PC-011','PC-011 — respondida')+'; '+fonte(CONFIRMACAO_RUNA,'correção literal')+''' |
| Okay, Mystra e Fogo Primordial | Okay obteve a habilidade por sua ligação com Mystra. A identificação está confirmada; causas e condições das manifestações permanecem desconhecidas para todos. | '''+qlink('IT-006','IT-006 — aguardando revelação')+'; '+fonte(CONFIRMACAO_DIVINDADES,'confirmação literal')+''' |
| Vínculos divinos do grupo | O jogador confirmou uma ligação com divindades específicas para cada personagem do grupo. A resposta não nomeia os vínculos de todos; Pelor/Ryld continua hipótese nos registros. | '''+qlink('PC-046','PC-046 — identificações restantes')+'; '+fonte(CONFIRMACAO_DIVINDADES,'confirmação literal')+''' |
| Ryld e sessão sem gravação | Ryld/Pelor não confirmado. O jogador voltou com outro personagem, introduzido na sessão não gravada; nome e destino ficcional de Ryld não informados. Reconstrução adiada até outra gravação. | '''+qlink('FT-001','FT-001 — em espera')+'; '+fonte(CONFIRMACAO_LACUNA,'resposta literal')+''' |
| Nome da aldeia natal de Glim | Não definido; sem importância por agora segundo o usuário. Manter a designação descritiva e adiar essa definição até ganhar relevância. A PC-042 foi posteriormente respondida: ambos os pais morreram e Glim não tem notícias de Nina desde a última saída da vila. Os detalhes geográficos continuam separados. | '''+qlink('PC-042','PC-042 — respondida')+'; '+qlink('LG-013','LG-013 — resposta parcial')+'; '+fonte(CONFIRMACAO_ALDEIA,'resposta literal')+''' |
| Crave, redenção e amuleto | Redenção perante Kord concluída; amuleto recuperado. Efeitos da perda da sombra, funcionamento do amuleto e posse do cinto permanecem assuntos separados. | '''+qlink('PC-012','PC-012 — resposta parcial')+'; '+fonte(CONFIRMACAO_CRAVE,'respostas literais')+''' |
| Cinto de Kord | Não foi recuperado. Detentor, localização atual e condições de obtenção não esclarecidos; não se presume permanência no gelo. | '''+qlink('IT-004','IT-004 — resposta parcial')+'; '+fonte(CONFIRMACAO_CINTO,'resposta literal')+''' |
| Grimório, mortes e Shar | Grimório causou as mortes de Lilo e Piche; artefato divino relacionado a Shar. Glim ainda não entende bem. PC-009 encerrada pelo jogador; não há novas perguntas sobre intenção ou terceiros. Selo e origem da voz continuam incertos em IT-001; nenhuma ordem direta da deusa foi confirmada. | '''+qlink('PC-009','PC-009 — encerrada')+'; '+qlink('IT-001','IT-001 — resposta parcial')+'; '+fonte(CONFIRMACAO_GRIMORIO,'confirmação literal')+''' |
| Hourian/Haurim | Adotar Hourian como nome canônico; Haurim é variante de anotação e alias. Não confirma biografia expandida ou a revoada. | '''+qlink('PC-037','PC-037 — grafia esclarecida')+'; '+fonte(CONFIRMACAO_HOURIAN,'resposta literal')+''' |
| Firael e consumo do cérebro de Kael | A hipótese de que Firael o consumiu foi negada pelo mestre. | [[Eventos/Morte de Kael]], T25 e esclarecimentos. |
| Amuleto, cinto e medalhão | Objetos separados; efeitos, posse e escolhas não intercambiáveis. | [[Itens/Amuleto de Kord]], [[Itens/Cinto de Kord]], [[Itens/Medalhao de limpeza]] |
| Datas das primeiras sessões | Dia/mês preservados; ano 2026 explicitamente inferido em 1–12/solo. | [[Sessoes/Indice]] |
| Tariun — notícias posteriores | Jogador confirmou que não houve notícias após a despedida. PC-030 fica em espera; ausência de notícia não constitui contradição. | '''+qlink('PC-030','PC-030 — em espera')+'; '+fonte(CONFIRMACAO_PRIORIDADES,'resposta literal')+''' |

## Base documental

- '''+fonte('J','Esclarecimentos de 23/10')+'''
- '''+fonte(CONFIRMACAO_SABATINA,'Sabatina de continuidade — confirmações de 29/10')+'''
- '''+fonte(CONFIRMACAO_GRIMORIO,'Sabatina — grimório de Glim e Shar')+'''
- '''+fonte(CONFIRMACAO_FAMILIAR,'Sabatina — limites da identidade do familiar')+'''
- '''+fonte(CONFIRMACAO_PICHE,'Sabatina — valor afetivo de Piche')+'''
- '''+fonte(CONFIRMACAO_RUNA,'Sabatina — reconhecimento da runa por estudo')+'''
- '''+fonte(CONFIRMACAO_DIVINDADES,'Sabatina — vínculos divinos e Mystra')+'''
- '''+fonte(CONFIRMACAO_LACUNA,'Sabatina — Ryld e sessão sem gravação')+'''
- '''+fonte(CONFIRMACAO_ALDEIA,'Sabatina — nome da aldeia não definido')+'''
- '''+fonte(CONFIRMACAO_CRAVE,'Sabatina — redenção de Crave e recuperação do amuleto')+'''
- '''+fonte(CONFIRMACAO_CINTO,'Sabatina — cinto de Kord não recuperado')+'''
- '''+fonte(CONFIRMACAO_PRIORIDADES,'Sabatina — Tariun sem notícias e prioridade para contradições')+'''
- '''+fonte(CONFIRMACAO_PORTAS,'Sabatina — invisibilidade das portas no destino')+'''
- '''+fonte(CONFIRMACAO_RETORNO,'Sabatina — porta mantida aberta para retorno')+'''
- '''+fonte(CONFIRMACAO_COORDENADAS,'Sabatina — limite de memória sobre K28/L28')+'''
- '''+fonte(CONFIRMACAO_HOURIAN,'Sabatina — grafia confirmada de Hourian')+'''
- '''+fonte('H','Handoff e seus limites')+'''
- [[Fontes/Indice|Fontes integrais e variantes]]

## Como resolver depois

Uma confirmação deve dizer qual versão foi esclarecida e até onde vale. Resolver o nome de uma pessoa não resolve automaticamente sua biografia; confirmar um vínculo não transforma uma hipótese de plano ou intenção em fato ocorrido.
'''
OUTPUTS.append(escrever('Pendencias/Conflitos e confirmacoes','Conflitos de fontes e confirmações existentes','indice',['fash','glim'],body,['J','H',CONFIRMACAO_SABATINA,CONFIRMACAO_GRIMORIO,CONFIRMACAO_FAMILIAR,CONFIRMACAO_PICHE,CONFIRMACAO_RUNA,CONFIRMACAO_DIVINDADES,CONFIRMACAO_LACUNA,CONFIRMACAO_ALDEIA,CONFIRMACAO_CRAVE,CONFIRMACAO_CINTO,CONFIRMACAO_PRIORIDADES,CONFIRMACAO_PORTAS,CONFIRMACAO_RETORNO,CONFIRMACAO_COORDENADAS,CONFIRMACAO_HOURIAN],status='organizado'))

body='''Relações de poder documentadas, com foco nas cartas e revelações do arco da arena. O diagrama é um resumo dessas relações em seus momentos registrados; não declara que todos os contratos sobreviveram à queda da arena ou ao saque de Eral.

```mermaid
flowchart LR
    Fash[Fash] -->|fundou| Ebano[Ébano]
    Firael[Firael] -->|comanda| Org[Organização de Firael]
    Cerebro[Cérebro Ancião] -->|autoridade superior| Org
    Org ---|aliança contra Ébano| Mercado[Mercado Negro]
    Org -->|rivalidade| Ebano
    Mercado -->|disputa territorial| Ebano
    Arena[Arena de Silthan] -->|tributo e compras| Mercado
    Filho[Filho de Arkhavel] -->|pressão e participação| Arena
    Kenku[Kenku] -->|auditoria anterior| Mercado
    Kenku -->|contrato posterior| Arena
    Conclave[Conclave da floresta] ---|acordo sobre bestas| Arena
```

| Relação | Natureza e limite | Fontes |
| --- | --- | --- |
| [[Personagens/Fash Paleskin]] → [[Faccoes/Ebano]] | Fundação confirmada; comando atual de Fash aberto. | '''+fonte('J')+''' |
| [[Personagens/Firael]] e [[Personagens/Cerebro Anciao]] → [[Faccoes/Organizacao de Firael]] | Liderança com Cérebro acima de Firael, explicada em T25. | '''+fonte('H')+'; '+fonte('J')+''' |
| [[Faccoes/Organizacao de Firael]] + [[Faccoes/Mercado Negro]] | Aliança contra Ébano; objetivo dos mapas de Eral contraditório. | '''+fonte('H')+''' |
| [[Faccoes/Arena de Silthan]] → [[Faccoes/Mercado Negro]] | Tributo e compra de cativos, não identidade automática das organizações. | '''+fonte('H')+''' |
| [[Personagens/Filho de Arkhavel ligado ao prefeito]] + Aboleth | Parceria secreta, desconhecida de Mercado e Silthan, segundo cartas. | '''+fonte('H')+''' |
| [[Faccoes/Kenku de Eral]] → Mercado, depois Silthan | Auditoria encerrada e contratação direta posterior; traição a Eral é outro momento. | '''+fonte('H')+''' |
| [[Faccoes/Conclave da floresta]] e arena | Responsabilidade e acordo revelados; não confundir com Círculo Vetrilus. | '''+fonte('H')+''' |

As descrições do diagrama são uma síntese do handoff; as notas temáticas indicam os trechos primários examinados e as pendências específicas. Veja '''+qlink('FC-003','FC-003 — consulta encerrada, motivação desconhecida')+' e '+qlink('FC-005','FC-005 — consulta encerrada, suspeita não confirmada')+'.'
OUTPUTS.append(escrever('Visoes/Relacoes de poder','Relações de poder','visao',['fash','glim'],body,['H','J'],status='documentado_parcial'))

threads=[
 ('Vesperal e Carlos','Eventos/Confronto com Vesperal',['PC-023','PC-021']),
 ('Grimório e familiar','Itens/Grimorio de Glim',['IT-001']),
 ('Objetivo de Firael e mapas','Itens/Mapas e pergaminhos de Firael',['PC-007']),
 ('Eral após o saque','Eventos/Ataque a Eral',['PC-025','FC-011']),
 ('Rangers desaparecidos','Eventos/Busca dos rangers',['PC-026','PC-027']),
 ('Posto e colônia Mind Shredder','Eventos/Posto dos Mind Shredders',['FC-022','PC-014']),
 ('Almas de Tauro e investigação do Lamassu','Personagens/Tauro',['PC-018','PC-019']),
 ('Expedições dos arquivistas','Lugares/Covil maritimo',['PC-031','LG-011']),
 ('Busca de memórias de Okay','Lugares/Montanha das memorias',['PC-004','LG-012']),
 ('Crave após a redenção e tarefa de Tariun','Eventos/Provacoes de Kord',['PC-012','PC-030','EV-005','IT-004']),
 ('Região antiga e necrópole','Lugares/Necropole',['LG-007']),
 ('Retorno do Etéreo e contagem do tempo','Eventos/Preparativos da torre',['CR-002']),
]
body='Este quadro reúne investigações e consequências sem registrar planos como feitos consumados. O corte atual do acervo é a sessão 26 de Glim. Cada pergunta aponta para evidências e limites, não para um desfecho inventado.\n\n| Fio | Consultar | A confirmar |\n| --- | --- | --- |\n'
for title,path,codes in threads:
    body+='| '+title+' | '+link(path)+' | '+'; '.join(qlink(c,c) for c in codes)+' |\n'
body+='\n\nA situação atual é sintetizada em '+fonte('H')+' e na '+fonte('C','cronologia herdada')+'. As atualizações confirmadas podem ser incorporadas posteriormente sem reescrever as falas e diários de origem.'
body+='\n\nA redenção de Crave perante Kord foi concluída e o amuleto foi recuperado, conforme confirmação do jogador. Efeitos da perda da sombra, questões do amuleto, tarefa de Tariun e cinto permanecem assuntos separados. '+fonte(CONFIRMACAO_CRAVE,'Confirmação do jogador — redenção e amuleto')+'.'
body+='\n\nO cinto de Kord não foi recuperado; sua localização e condições para eventual obtenção continuam em aberto em '+qlink('IT-004','IT-004')+'. '+fonte(CONFIRMACAO_CINTO,'Confirmação do jogador — cinto não recuperado')+'.'
body+='\n\nA regra das portas foi esclarecida em '+qlink('IT-005','IT-005')+': manter a porta aberta para o retorno; ela é invisível do lado do destino. '+fonte(CONFIRMACAO_RETORNO,'Confirmação do jogador — regra de retorno')+'.'
OUTPUTS.append(escrever('Visoes/Missoes e fios abertos','Missões e fios abertos','visao',['fash','glim'],body,['H','C',CONFIRMACAO_CRAVE,CONFIRMACAO_CINTO,CONFIRMACAO_PRIORIDADES,CONFIRMACAO_RETORNO],status='documentado_parcial'))
OUTPUTS.append(escrever('Visoes/Indice','Visões gerais','indice',['fash','glim'],listing(sorted(p for p in (CONTEUDO/'Visoes').glob('*.md') if p.name!='Indice.md'))+'\n\n'+link('Inicio'),[],status='organizado'))

body='''Base pública das campanhas de Fash e Glim. As entradas enciclopédicas reúnem o que as fontes sustentam e ligam pessoas, lugares, grupos, objetos e acontecimentos. Os registros originais conservam a voz dos personagens e suas divergências.

## Explorar

- [[Personagens/Indice|Personagens]]
- [[Lugares/Indice|Lugares e cartografia]]
- [[Faccoes/Indice|Facções e grupos]]
- [[Criaturas/Indice|Criaturas]]
- [[Eventos/Indice|Acontecimentos]]
- [[Itens/Indice|Itens, poderes e mecanismos]]
- [[Cronologia/Indice|Cronologia]]
- [[Visoes/Indice|Visões gerais]]
- [[Visoes/Relacoes de poder|Relações de poder]]
- [[Visoes/Missoes e fios abertos|Missões e fios abertos]]

## As campanhas

- [[Campanhas/Indice|Índice de campanhas]]
- [[Campanhas/Fash|Fash — campanha antiga]]
- [[Campanhas/Glim|Glim — campanha atual]]
- [[Cronologia/Fash e Glim|Continuidade e intervalo de 70 anos]]

## Fontes e diários

- [[Sessoes/Indice|Diários de Glim por sessão]]
- [[Fontes/Transcricoes/Indice|Transcrições disponíveis]]
- [[Fontes/Indice|Acervo integral de fontes]]

## Completar a base

- [[Pendencias/Indice|Banco de pendências por assunto e prioridade]]
- [[Pendencias/Roteiro da sabatina|Sabatina — contradições primeiro]]
- [[Pendencias/Conflitos e confirmacoes|Conflitos de fontes e confirmações já existentes]]
- [[Pendencias/Acervo/FT-001 - Sessao recente sem gravacao e novo personagem|Sessão recente sem gravação — reconstrução parcial]]

**Como ler:** um relato de NPC, uma visão ou uma hipótese conserva essa condição. Uma confirmação pode esclarecer uma afirmação sem validar todas as interpretações da mesma fonte. Os diários e transcrições consolidados vão até a sessão 26. Relatos posteriores do jogador reconstituem parte da sessão recente sem gravação; a cobertura e as lacunas restantes estão em [[Pendencias/Acervo/FT-001 - Sessao recente sem gravacao e novo personagem|FT-001]]. Os planos só são registrados como realizados quando há confirmação.
'''
OUTPUTS.append(escrever('Inicio','Campanha de Fash e Glim','indice',['fash','glim'],body,[],status='organizado'))

body='''Campanha antiga do jogador, situada 70 anos antes da época de Glim. O diário inclui experiência onírica e acontecimentos materiais, que continuam distinguidos nas notas. A síntese de referência é '''+fonte('H')+' e as correções são '+fonte('J')+'''.

## Eixos da história

- [[Eventos/Cativeiro e sonho de Fash|Cativeiro e sonho]]
- [[Eventos/Destruicao da esfera de Elena|Esfera de Elena e epidemia de luz]]
- [[Eventos/Queda do Druida Sangrento|Cidade drow e libertações]]
- [[Eventos/Reassentamento em Throden|Reassentamento do Forte e da cidade]]
- [[Eventos/Duelo e entrega de Firael|Duelo, entrega de Firael e ruptura]]
- [[Eventos/Morte de Kael|Morte de Kael e continuidade em Okay]]
- [[Cronologia/Fash e Glim|Transição para a época de Glim]]

## Pessoas e forças

[[Personagens/Fash Paleskin]], [[Personagens/Kael]], [[Personagens/Timo]], [[Personagens/Firael]], [[Personagens/Elena]], [[Personagens/Cerebro Anciao]], [[Faccoes/Circulo Vetrilus]] e [[Faccoes/Organizacao do Necromante]].

## Fontes

- [[Fontes/Documentos/Diario - Fash Paleskin|Diário integral de Fash]]
- [[Fontes/Planilhas/Fash Paleskin|Ficha, registros e mapas]]
- [[Pendencias/Roteiro da sabatina|Lacunas preparadas para a sabatina]]
'''
OUTPUTS.append(escrever('Campanhas/Fash','Campanha de Fash','campanha',['fash'],body,['H','J'],status='documentado_parcial'))
body='''Campanha em andamento, com registros consolidados até a sessão 26, de 20/10/2026. O diário de Glim é uma perspectiva; as análises e transcrições também preservam cenas privadas e explicações em off sem atribuir esse conhecimento automaticamente a todos os personagens. Fontes: '''+fonte('H')+' e '+fonte('G')+'''.

## Personagens nos registros consolidados

[[Personagens/Glim Sombrasselva]], [[Personagens/Okay dBoa|Okay]], [[Personagens/Crave]], [[Personagens/Ryld]] e seus vínculos com [[Personagens/Arkhavel]].

## Arcos e consequências

- [[Eventos/Chegada a Eral|Caravana, Eral e contratos]]
- [[Eventos/Caso das criancas|Crianças e água envenenada]]
- [[Eventos/Caca ao Vasuthant|Caça ao Vasuthant]]
- [[Eventos/Crise do prefeito|Prefeito e Aboleth]]
- [[Eventos/Queda da arena|Queda da arena e cartas]]
- [[Eventos/Busca dos rangers|Expedição e retorno]]
- [[Eventos/Ataque a Eral|Saque e traição]]
- [[Eventos/Crise dos refens|Reféns e massacre]]
- [[Eventos/Provacoes de Kord|Provações de Crave]]
- [[Eventos/Despertar do Fogo Primordial|Poderes e provações]]
- [[Eventos/Memorias de Kael|Memórias da campanha antiga]]
- [[Eventos/Confronto com Vesperal|Vesperal e preparação da torre]]

## Sessão recente sem gravação

O usuário informou que a sessão mais recente não foi gravada. Nela foi introduzido outro personagem do jogador que antes interpretava Ryld e havia ficado um período sem jogar. Nome, data e número da sessão não foram fornecidos. A reconstrução foi adiada até haver outra gravação, em [[Pendencias/Acervo/FT-001 - Sessao recente sem gravacao e novo personagem|FT-001]]. Fonte: '''+fonte(CONFIRMACAO_LACUNA,'Esclarecimento do jogador')+'''.

## Consultar e atualizar

- [[Sessoes/Indice|Diários por sessão]]
- [[Fontes/Transcricoes/Indice|Transcrições]]
- [[Cronologia/Glim Sombrasselva|Cronologia e limites da contagem]]
- [[Visoes/Missoes e fios abertos|Fios ainda abertos]]
- [[Pendencias/Indice|Revisão de contradições e sequência]]
'''
OUTPUTS.append(escrever('Campanhas/Glim','Campanha de Glim','campanha',['glim'],body,['H','G',CONFIRMACAO_LACUNA],status='documentado_parcial'))

OUTPUTS=[path for path in OUTPUTS if path is not None]
manifest=dict(data='2026-10-30',contagens=counts,pendencias=len(questions),pendencias_ativas=len(active_questions),
              status_pendencias=status_counts,prioridades=priority_counts,
              foco_sabatina='contradicoes_e_lacunas_de_sequencia',fila_sabatina=fila_sabatina,
              registros_sem_resposta_completa=len(unanswered_questions),
              classificacoes_revisao={k:len(v) for k,v in review_groups.items()},
              ids_aguardando_fonte=[q['id'] for q in waiting_questions],
              ids_consolidados=[q['id'] for q in consolidated_questions],
              ids=[q['id'] for q in questions],ids_ativos=[q['id'] for q in active_questions],
              arquivos_de_navegacao=OUTPUTS,somente_indices=args.somente_indices)
(ROOT/'docs/enciclopedia/integracao.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'categorias':counts,'pendencias':len(questions),'pendencias_ativas':len(active_questions),
                  'status_pendencias':status_counts,'prioridades':priority_counts,'navegacao':len(OUTPUTS),
                  'somente_indices':args.somente_indices},ensure_ascii=True))
