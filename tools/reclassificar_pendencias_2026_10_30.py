"""Triagem editorial única; preserva fontes, respostas e perguntas como histórico."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'conteudo'
SOURCE='Fontes/Confirmacoes/2026-10-30 - Criterio de revisao contradicoes e fluxo'
def parse(p):
    raw=p.read_text(encoding='utf-8');_,front,body=raw.split('---',2)
    return {k:json.loads(v) for k,v in (l.split(': ',1) for l in front.strip().splitlines())},body,raw
def write(p,m,body):
    p.write_text('---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in m.items())+'\n---\n'+body,encoding='utf-8')

OPEN={
'EV-002':'Extensão e fim da epidemia ainda não foram revelados; um desfecho desconhecido não contradiz o desfecho local já documentado.',
'EV-003':'Propósito do sonho e correspondências ocultas pertencem à intenção ainda não revelada do mestre; preservar a camada onírica basta.',
'EV-005':'Destino posterior dos sobreviventes e contagem não interrompem a sequência da fuga já registrada.',
'EV-006':'Causas e resolução fora de cena são história ainda não conhecida. A ordem dos acontecimentos já narrados é tratada apenas em EV-001.',
'EV-007':'Não foi demonstrado que as duas revoadas sejam o mesmo fato. O jogador já considera provável serem distintas; não insistir na hipótese.',
'FC-010':'Estado futuro da rede das bruxas é informação não revelada, sem duas versões incompatíveis identificadas.',
'FC-011':'Sucessão institucional desconhecida após o ataque; não há contradição sobre um dirigente identificado.',
'FC-013':'Novos relatórios e decisões de resgate seriam revelações ou ações futuras, não correção da sequência conhecida.',
'FC-015':'Ritos, artefatos e vínculo atual dos Zodíacos são mistérios. O diário de Firael fornece um relato antigo, sem contradição demonstrada com o presente.',
'FC-019':'Alcance e identidade da rede de almas ainda não foram revelados. Não exigir organograma para narrar o leilão.',
'FC-020':'Governo e permanência atual dos reassentados não são conhecidos; os acontecimentos antigos já podem ser narrados sem censo ou organograma.',
'FC-022':'A incursão ainda não ocorreu nos relatos. Colônia e resultado da missão devem permanecer abertos, sem pergunta antecipada.',
'IT-001':'O jogador já declarou incertos entidade, voz e selo do grimório. Mistério preservado, sem nova consulta.',
'IT-002':'As fontes distinguem tomo, cópia e volume do dragão. Não há dois relatos incompatíveis demonstrados; nomes e relações adicionais podem continuar desconhecidos.',
'IT-003':'Origem e novos poderes do amuleto são mistérios. Entrega, recuperação e experiência de Okay estão registradas, sem conflito factual apresentado.',
'IT-004':'O cinto não foi recuperado. Sua localização e eventual obtenção são possibilidades de jogo, não lacunas a preencher por entrevista.',
'IT-006':'Causas e condições dos poderes ainda não foram reveladas a ninguém; preservar esse limite já esclarecido.',
'IT-007':'Consciência e poderes adicionais de Timo no cajado não são conhecidos. A identidade confirmada e o salto histórico ficam separados.',
'IT-008':'Nomes, ocupação e desfechos dos artefatos investigados são informação adicional não revelada, sem contradição identificada.',
'LG-004':'Ocupantes atuais, setenta anos depois, não são dedutíveis dos moradores antigos; desconhecimento não é erro de continuidade.',
'LG-006':'Identidade do fosso e distinção dos nodos já foram resolvidas; guardião e mecanismos atuais são revelações futuras.',
'LG-007':'A distinção dos locais já foi confirmada. Ocupação atual e vínculo com o Cavaleiro continuam desconhecidos, sem nova contradição.',
'LG-008':'Nomes, coordenadas e ocupação atual dos covis não foram estabelecidos; os três locais e o acordo antigo estão documentados.',
'LG-010':'A equivalência geográfica não foi confirmada e o jogador não sabe. Manter lugares distintos não impede narrar os eventos.',
'LG-011':'Localização exata, rota segura e ocupação do covil dependem de exploração ou informação ainda não recebida.',
'PC-004':'Memórias não recuperadas e vínculos das encarnações são mistérios da campanha, sem versões incompatíveis apontadas.',
'PC-007':'Reconhecimento de Okay por Firael não foi revelado. A motivação da operação de Eral já foi encerrada em FC-003 como desconhecida.',
'PC-008':'A libertação antiga já está narrada por Firael; o corpo e o paradeiro no presente são informação ainda não revelada.',
'PC-012':'Redenção, recuperação do amuleto e ausência da sombra foram esclarecidas. Efeitos adicionais continuam abertos por decisão de jogo.',
'PC-013':'A manifestação de Kord é crença do grupo; identidade definitiva e outros atos não foram revelados. Não exigir confirmação do mistério.',
'PC-014':'A inspeção foi esclarecida: Ryld não encontrou nada. Origem da luz e destino posterior permanecem desconhecidos, não contraditórios.',
'PC-015':'Busca dos filhos e retorno de Arkhavel ainda estão em aberto; não antecipar o resultado de uma ação do personagem.',
'PC-017':'Donovan já foi distinguido do outro filho. Função, natureza e paradeiro adicionais podem permanecer desconhecidos.',
'PC-018':'Almas de Tauro, resultado da consulta do Lamassu e recuperação não foram revelados; não há desfechos incompatíveis demonstrados.',
'PC-019':'Nome, origem da mulher e destino da alma são mistérios; não são necessários para preservar os fatos observados.',
'PC-020':'O jogador não recebeu notícias. Identidade e tratamento desconhecidos permanecem assim, sem nova pergunta.',
'PC-022':'Autor e destino do cadáver roubado são o próprio mistério investigado. Não há versões incompatíveis de um desfecho conhecido.',
'PC-023':'Natureza de Vesperal, sobrevivência e nova encomenda são ganchos ainda não resolvidos, não erros de registro.',
'PC-025':'A morte de Tólomon é crença declarada. Falta de confirmação não justifica repetir uma pergunta já respondida com incerteza.',
'PC-026':'Folha-Seca e sucesso da missão foram esclarecidos; Hanta segue sem notícia. Não converter medo de perguntar em obrigação de obter uma resposta.',
'PC-027':'O desaparecimento da amiga é informação ainda não solucionada pela campanha.',
'PC-028':'O jogador pediu manter o destino de Silthan desconhecido; prisão coletiva sem nomes não permite completar seu destino individual.',
'PC-029':'Destino e participação individual do Kenku não foram revelados; fuga coletiva e oportunismo já estão registrados.',
'PC-030':'Já foi respondido que não houve notícias de Tariun. Missão e advertência continuam abertas, sem contradição.',
'PC-031':'Identidade do mestre desaparecido e novos relatos são informação ainda não conhecida; o jogador já declarou esse limite.',
'PC-032':'O jogador registrou crença na versão da bruxa. Natureza e paradeiros não revelados não se tornam contradições a resolver por insistência.',
'PC-033':'Existência material e destino de Grixxian não foram revelados. Preservar a camada do sonho evita fusão indevida.',
'PC-036':'Vida, território e acordo atuais do dragão dependem de informação nova; relatos antigos não obrigam a definir o presente.',
'PC-037':'A grafia Hourian já foi confirmada. Biografia e revoada não reveladas permanecem sem exigir preenchimento.',
'PC-038':'Destino da matilha e legado adicional de Rake não foram narrados, sem conflito com os fatos conhecidos.',
'PC-039':'A missão de Furion já foi recuperada no diário de Firael. Só o destino posterior continua desconhecido.',
'PC-043':'Acordo e paradeiro do dragão de cristal são informação adicional não revelada; não há conflito demonstrado sobre seus atos.',
'PC-044':'Disposição e vínculos atuais do beholder dependem de exploração ou revelação futura.',
'PC-045':'Origem da condição do chefe goblin e vínculos com entidades são mistério; os efeitos observados já estão documentados.',
'PC-046':'Vínculos específicos e mecanismos dos poderes ainda não foram revelados. Mystra e Shar já foram registrados no alcance confirmado.',
'PC-047':'Conhecimento do duque e nomeação de substituto não foram informados. A presença do exército já foi confirmada sem definir o governo futuro.',
}
DETAIL={
'CR-001':'Não é preciso fixar calendário absoluto ou ano atual para preservar a ordem relativa já conhecida; datas do sonho não são datas materiais.',
'CR-002':'Não foi demonstrado conflito de ordem causado pelos dias ausentes. Contagem exata por completude sai da fila; o prazo do ranger pode continuar relativo.',
'FC-012':'Nome da Ordem confirmado e orientação para seguir o dossiê de Okay já recebida. Completar nomes e organograma de subdivisões não corrige um acontecimento.',
'FC-021':'Instituições oníricas não precisam ganhar equivalentes materiais. Mantê-las na camada do sonho evita invenção.',
'LG-001':'Nomes do mundo e continentes não são necessários à sequência. Carruan e o caráter onírico da proibição já foram esclarecidos.',
'LG-003':'As distâncias são informação de Tork e estimativa de Glim para trajetos não demonstrados como iguais; não há contradição comparável a cobrar do jogador.',
'LG-005':'K28/L28 é divergência cartográfica preservada, mas sem efeito demonstrado no fluxo de um evento. O jogador já não se recorda; não insistir em coordenadas.',
'LG-009':'Nome da região e ocupação posterior da aldeia não resolvem contradição ou etapa ausente do resgate já narrado.',
'LG-012':'Nome e paradas de estrada não são necessários para registrar a viagem planejada. Não pedir itinerário sem problema concreto no relato.',
'LG-013':'O jogador declarou a aldeia próxima à capital e sem relevância; não solicitar nome, endereço ou ocupação da casa.',
'LG-014':'Correspondentes materiais dos lugares do sonho não precisam existir. Origem real de Fash e capital Carruan já foram distinguidas.',
'LG-015':'Endereço da casa de Arkhavel em Mercadia não altera a história. Plano e regras adicionais sem conflito demonstrado também não geram uma consulta de preenchimento.',
'LG-016':'As regiões de Eral e de Fash já foram separadas. Coordenadas e ocupação posterior não apresentam contradição restante.',
'PC-006':'Timo/Fash e erro Fesh já foram esclarecidos. Datas 530/536 não estão ancoradas a um calendário material comparável; manter a ressalva, sem repetir o que o jogador não sabe.',
'PC-016':'Identidade do falso mordomo e sobrevivência para o interrogatório já foram resolvidas. Nome e grafia adicionais não reabrem essas contradições; paradeiro posterior permanece desconhecido.',
'PC-035':'Não há afirmação conflitante que exija fundir o anão material ao onírico. Seu nome e destino posterior não são necessários para registrar sua função já conhecida.',
}
FOCUS={
'EV-001':dict(group='lacuna_de_sequencia',action='perguntar',priority='alta',
 reason='Falta a ligação entre acontecimentos já afirmados do fim da campanha antiga e o cenário setenta anos depois; a revisão precisa de ordem, não de novas revelações.',
 impact='Evitar que morte de Kael, separação de Fash, continuidade de Timo e crise sejam narradas numa ordem inventada.',
 question='Entre os acontecimentos que a mesa já narrou, em que ordem ficaram a separação de Fash e Kael, a morte de Kael, a passagem de Timo a planta e a Noite Eterna? Basta a ordem conhecida; o que aconteceu fora de cena continua desconhecido.'),
'PC-021':dict(group='lacuna_de_sequencia',action='conferir_fontes',priority='media',
 reason='Carlos aparece vivo trabalhando e, mais tarde, seu cadáver é usado na S26. É preciso conferir se existe uma notícia intermediária, sem investigar um assassino não revelado.',
 impact='Distinguir uma passagem omitida na wiki de uma morte fora de cena que a campanha deliberadamente não explicou.',
 question='Existe alguma cena ou notícia já registrada entre Carlos trabalhando e seu cadáver na S26? Se não houver, registrar morte fora de cena, sem perguntar autor, método ou destino da família.'),
'FT-001':dict(group='lacuna_de_sequencia',action='aguardar_fonte',priority='media',
 reason='A gravação ausente deixou um trecho concreto da sequência sem fonte; o usuário já decidiu aguardar outra gravação e parte dos acontecimentos foi recuperada.',
 impact='Preservar o ponto de retomada antes da entrada no túnel sem criar número de sessão, fatos ou resultados.',
 question='Recuperar somente a sequência restante da sessão sem gravação quando chegar a recapitulação ou fonte já combinada; não perguntar novamente o background de Aelion.'),
'PC-005':dict(group='lacuna_de_sequencia',action='consolidada',priority='media',
 reason='A transição já afirmada Timo → planta → cajado integra o salto histórico de EV-001; não justifica outra bateria sobre consciência, poderes ou identidade da dríade.',
 impact='Uma única revisão da transição entre campanhas, sem repetir perguntas sobre a mesma passagem.',
 question='Tratar apenas a posição dos acontecimentos já narrados dentro de EV-001; consciência e mecanismo não revelados permanecem em aberto.',parent='EV-001'),
}

def main():
    auditpath=ROOT/'docs/enciclopedia/triagem-pendencias-2026-10-30.json'
    assert not auditpath.exists(),'Triagem única já aplicada; revisar em vez de reexecutar.'
    source=B/(SOURCE+'.md')
    assert not source.exists()
    source.write_text('''---
tipo: "fonte"
titulo: "Critério do jogador — contradições e gaps no fluxo"
campanhas: ["fash", "glim"]
publico: true
status: "orientacao_registrada"
origens: ["Conversa com o jogador em 2026-10-30 — revisão da lista inteira de pendências"]
aliases: []
atualizado: "2026-10-30"
---

# Critério do jogador — contradições e gaps no fluxo

## Orientação literal

> Precisamos priorizar as duvidas, você faz muitas perguntas sem nenhum nível de relevancia.
>
> "Qual o endereço da casa do Arkhavel em Mercadia?" Sério isso? Qual a relevância disso?
>
> Eu não quero dúvidas do que está em aberto, o que está em aberto está em aberto e pronto, as dúvidas devem focar no que está contraditório, em gaps dentro de um fluxo de acontecimentos.
>
> Revisa a lista de pendências e separa elas por esse critério.

## Aplicação

Revisar versões incompatíveis de um mesmo acontecimento e elos ausentes entre acontecimentos já narrados. Exigir fontes e explicar o efeito da dúvida na leitura. Mistérios sem revelação, missões futuras, paradeiros desconhecidos e detalhes sem impacto ficam fora da fila. Preservar perguntas antigas como histórico, sem fingir que suas respostas foram descobertas. Não voltar a perguntar o que o jogador já disse não saber. Atualizar somente o projeto, sem editar o Google Doc.
''',encoding='utf-8')
    originals=[];paths={}
    for p in sorted((B/'Pendencias').rglob('*.md')):
        m,body,raw=parse(p)
        if m.get('tipo')!='pendencia':continue
        paths[m['id']]=p
        originals.append(dict(id=m['id'],caminho=p.relative_to(ROOT).as_posix(),sha256_antes=hashlib.sha256(raw.encode()).hexdigest(),texto_antes=raw))
    live={code for code,p in paths.items() if parse(p)[0]['status']!='respondida'}
    assert live==set(OPEN)|set(DETAIL)|set(FOCUS),('Sem classificação',live-(set(OPEN)|set(DETAIL)|set(FOCUS)), 'Entradas extras',(set(OPEN)|set(DETAIL)|set(FOCUS))-live)
    labels={'em_aberto':'Fato ainda em aberto — fora da fila','detalhe_sem_impacto':'Detalhe sem impacto na sequência — fora da fila','encerrada':'Histórico encerrado','contradicao':'Contradição documental','lacuna_de_sequencia':'Lacuna de sequência'}
    for code,p in paths.items():
        m,body,raw=parse(p);closed=m['status']=='respondida'
        if closed:
            group='encerrada';action='nao_perguntar';reason='A consulta já foi respondida ou encerrada pelo jogador. Preservar a resposta e seus limites sem reabri-la.';priority='baixa';impact='';question=''
        elif code in FOCUS:
            f=FOCUS[code];group=f['group'];action=f['action'];reason=f['reason'];priority=f['priority'];impact=f['impact'];question=f['question']
        else:
            group='em_aberto' if code in OPEN else 'detalhe_sem_impacto';action='nao_perguntar';reason=(OPEN|DETAIL)[code];priority='baixa';impact='';question=''
        m['prioridade_anterior']=m['prioridade'];m['prioridade']=priority
        m.update(classificacao_revisao=group,acao_revisao=action,justificativa_revisao=reason,retomar_na_sabatina=action=='perguntar',atualizado='2026-10-30')
        m['origens']=list(dict.fromkeys(m['origens']+[SOURCE]))
        if impact:m['impacto_revisao']=impact
        if question:m['pergunta_revisada']=question
        if code=='PC-005':m['consolidada_em']='EV-001'
        body=body.replace('## Pergunta para a sabatina','## Pergunta original — preservada como histórico')
        if action=='nao_perguntar':body=body.replace('## Restante para a sabatina','## Escopo anterior — fora da fila')
        block='\n## Triagem de relevância — 30/10/2026\n\n**'+labels[group]+'.** '+reason
        if question:block+='\n\n**Escopo revisado:** '+question
        block+='\n\n[[Pendencias/Indice|Consultar a lista revisada por critério]]. [[%s|Orientação do jogador]].\n'%SOURCE
        # A triagem atual aparece antes da pergunta antiga, não escondida no fim.
        body=re.sub(r'(^\s*# [^\n]+\n)',lambda x:x[1]+block,body,count=1)
        write(p,m,body)
    # Um conflito efetivamente demonstrado, reunido numa única consulta sobre versões.
    p=B/'Pendencias/Eventos/EV-009 - Versoes divergentes do diario de Firael.md'
    assert not p.exists()
    m=dict(tipo='pendencia',titulo='EV-009 — Versões divergentes do diário de Firael',campanhas=['fash'],publico=True,status='aberta',origens=[SOURCE,'Fontes/Documentos/Diario de Firael - versao completa','Fontes/Documentos/Diario de Firael - variante 1','Fontes/Documentos/Diario de Firael - variante 2'],aliases=[],atualizado='2026-10-30',id='EV-009',categoria='Eventos',prioridade='media',natureza='divergencia_de_versoes',pergunta='Qual versão do diário de Firael deve orientar a atribuição dos atos nas três passagens divergentes?',entidades=['Personagens/Firael','Personagens/Fash Paleskin','Personagens/Timo'],classificacao_revisao='contradicao',acao_revisao='perguntar',retomar_na_sabatina=True,
        justificativa_revisao='Os mesmos episódios têm ações atribuídas a personagens diferentes nas três versões recebidas; a comparação dos parágrafos confirmou as diferenças.',
        impacto_revisao='Evitar que a wiki atribua o mesmo ato a autores incompatíveis ou some versões alternativas como acontecimentos diferentes.',
        pergunta_revisada='A variante 2 foi substituída pelas versões mais abrangentes? Qual versão deve orientar a autoria das ações nas três passagens divergentes, mantendo todas como fontes?')
    body='''
# EV-009 — Versões divergentes do diário de Firael

## Contradição demonstrada

| Cena | Versão mais abrangente e variante 1 | Variante 2 |
| --- | --- | --- |
| Silêncio contra a serpente, 15/12 | Fash conjura | Timo conjura |
| Avistamento nas copas, 30/10 | Fash avista | Timo avista |
| Árvore corrompida, 30/10 | Firael intervém; Fash conclui com óleo e fogo | Firael dá o golpe final |

As três divergências são uma única revisão de versões: não perguntar três vezes pelo mesmo problema de precedência documental. A sequência pode ser narrada até a decisão sobre autoria; não apagar nenhuma versão.

## Fontes e localizadores

- [[Fontes/Documentos/Diario de Firael - versao completa|Versão mais abrangente]]: parágrafos 408, 547 e 551.
- [[Fontes/Documentos/Diario de Firael - variante 1|Variante 1]]: parágrafos 363, 502 e 506.
- [[Fontes/Documentos/Diario de Firael - variante 2|Variante 2]]: parágrafos 136, 275 e 279.

Comparação reproduzível em `docs/importacoes/2026-10-30-firael-ryld/comparacao.json`. As três versões foram preservadas integralmente.

## Pergunta focada

A variante 2 foi substituída pelas versões mais abrangentes? Qual versão deve orientar a autoria das ações nas três passagens divergentes, mantendo todas como fontes?

## Impacto e limite

Atribuição de atos e escolha de fonte na reconstituição dos eventos. Não perguntar nomes, endereços ou desfechos ainda desconhecidos para resolver este conflito. Até a resposta, mostrar as versões com atribuição, sem escolher uma por extensão do arquivo ou pelo sufixo do nome.

[[Fontes/Confirmacoes/2026-10-30 - Criterio de revisao contradicoes e fluxo|Critério de relevância do jogador]]. [[Pendencias/Indice|Lista revisada]].
''';write(p,m,body);paths['EV-009']=p
    new={'id':'EV-009','caminho':p.relative_to(ROOT).as_posix(),'novo':True}
    records=[]
    for rec in originals+[new]:
        m,_,_=parse(paths[rec['id']]);records.append({**rec,'classificacao':m['classificacao_revisao'],'acao':m['acao_revisao'],'justificativa':m['justificativa_revisao'],'prioridade_atual':m['prioridade'],'consolidada_em':m.get('consolidada_em')})
    counts={key:sum(r['classificacao']==key for r in records) for key in labels}
    auditpath.write_text(json.dumps(dict(data='2026-10-30',criterio=SOURCE,originais_revisados=len(originals),registros_atuais=len(records),classificacoes=counts,registros=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # A referência narrativa usa a revisão, sem transformar cada informação ausente em pergunta.
    for rel in ['Personagens/Firael.md','Visoes/Novas fontes - Firael e Ryld.md']:
        p=B/rel;m,body,_=parse(p)
        body+='\n## Revisão das versões do diário\n\n[[Pendencias/Eventos/EV-009 - Versoes divergentes do diario de Firael|EV-009]] reúne as três atribuições incompatíveis entre as versões recebidas. Preservar as alternativas até definir qual versão orienta o relato. [[%s|Critério de revisão]].\n'%SOURCE
        m['origens']=list(dict.fromkeys(m['origens']+[SOURCE]));write(p,m,body)
    p=B/'Fontes/Indice.md';p.write_text(p.read_text(encoding='utf-8')+'\n- [[%s|Critério de revisão: contradições e gaps no fluxo — 30/10/2026]].\n'%SOURCE,encoding='utf-8')
    print(json.dumps(dict(revisados=len(originals),novo_conflito='EV-009',classificacoes=counts),ensure_ascii=False))

if __name__=='__main__':main()
