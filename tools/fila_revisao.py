"""Fila editorial: só contradições e elos de sequências já narradas."""
GROUPS={
    'contradicao':'Contradições documentais',
    'lacuna_de_sequencia':'Gaps no fluxo dos acontecimentos',
    'em_aberto':'Fatos em aberto — não são perguntas',
    'detalhe_sem_impacto':'Detalhes sem impacto — fora da fila',
    'encerrada':'Histórico encerrado',
    'sem_triagem':'Sem triagem — não entra automaticamente na fila',
}
REVIEW={'contradicao','lacuna_de_sequencia'}
ORDER={'alta':0,'media':1,'baixa':2}

def order(q):return (ORDER.get(q.get('prioridade'),3),q['id'])

def separate(questions):
    groups={name:[] for name in GROUPS}
    for q in questions:
        kind='encerrada' if q['status']=='respondida' else q.get('classificacao_revisao','sem_triagem')
        if kind not in groups:raise ValueError('Classificação desconhecida: '+q['id']+' '+kind)
        groups[kind].append(q)
    active=sorted([q for kind in REVIEW for q in groups[kind]
                   if q.get('acao_revisao') in {'perguntar','conferir_fontes'}],key=order)
    for q in active:
        if not all(q.get(field) for field in ['justificativa_revisao','impacto_revisao','pergunta_revisada','origens']):
            raise ValueError('Revisão sem fontes, justificativa, impacto ou escopo focado: '+q['id'])
    queue=[q['id'] for q in active if q.get('acao_revisao')=='perguntar' and q.get('retomar_na_sabatina',False)]
    waiting=sorted([q for kind in REVIEW for q in groups[kind] if q.get('acao_revisao')=='aguardar_fonte'],key=order)
    consolidated=sorted([q for kind in REVIEW for q in groups[kind] if q.get('acao_revisao')=='consolidada'],key=order)
    return groups,active,queue,waiting,consolidated

def clean(value):return str(value).replace('|','/').replace('\n',' ')
def short(q):return clean(q['titulo'].split(' — ',1)[-1])
def limits_table(rows,qlink):
    lines=['| Registro | Tema e limite |','| --- | --- |']
    for q in sorted(rows,key=lambda q:q['id']):
        lines.append('| '+qlink(q['id'],q['id'])+' | **'+short(q)+'** — '+clean(q.get('justificativa_revisao','Não classificado; não perguntar até demonstrar relevância.'))+' |')
    return '\n'.join(lines)

def index_body(groups,active,queue,waiting,consolidated,qlink,link):
    result=(f'**{len(active)} tópicos de revisão prioritária**, com **{len(queue)} consultas possíveis aos jogadores**. '
            'Só entram aqui versões incompatíveis do mesmo fato ou elos ausentes entre acontecimentos já narrados. '
            'Antes de perguntar, conferir as fontes e explicar o que a resposta muda na leitura.\n\n'
            'Mistérios ainda não revelados, missões futuras, falta de notícias, nomes, endereços e contagens sem efeito na sequência ficam fora da fila. '
            'Não saber uma resposta não cria uma obrigação de descobri-la. As perguntas antigas permanecem como histórico, não como questionário atual.\n\n'
            '- '+link('Pendencias/Roteiro da sabatina','Revisão prioritária e ordem de trabalho')+'\n'
            '- '+link('Visoes/Missoes e fios abertos','Estado dos fios da campanha — sem obrigação de responder')+'\n\n')
    for kind in ['contradicao','lacuna_de_sequencia']:
        rows=[q for q in active if q.get('classificacao_revisao')==kind]
        result+='## '+GROUPS[kind]+'\n\n'
        if not rows:result+='Nenhum tópico de revisão imediata neste grupo.\n\n';continue
        result+='| Registro | Problema e impacto | Próxima ação |\n| --- | --- | --- |\n'
        for q in rows:
            action='Pergunta focada' if q['acao_revisao']=='perguntar' else 'Conferir fontes'
            result+='| '+qlink(q['id'],q['id'])+' | **'+short(q)+'** — '+clean(q['justificativa_revisao'])+' '+clean(q.get('impacto_revisao',''))+' | '+action+' |\n'
        result+='\n'
    if waiting:
        result+='## Gaps aguardando a fonte já combinada\n\nNão repetir a consulta enquanto a fonte não chegar.\n\n'+limits_table(waiting,qlink)+'\n\n'
    if consolidated:
        result+='## Escopos consolidados — sem outra pergunta\n\n'
        for q in consolidated:
            result+='- '+qlink(q['id'],q['id'])+' tratado em '+qlink(q['consolidada_em'],q['consolidada_em'])+': '+q['justificativa_revisao']+'\n'
        result+='\n'
    for kind in ['em_aberto','detalhe_sem_impacto','encerrada','sem_triagem']:
        if groups[kind]:result+='## '+GROUPS[kind]+'\n\n'+limits_table(groups[kind],qlink)+'\n\n'
    result+='## Critério e auditoria\n\n[[Fontes/Confirmacoes/2026-10-30 - Criterio de revisao contradicoes e fluxo|Orientação do jogador]]. '
    result+='[Auditoria dos registros e classificação individual](../../docs/enciclopedia/triagem-pendencias-2026-10-30.json). '
    result+='Uma nova dúvida só entra com versões incompatíveis ou uma passagem concreta ausente, fontes e impacto explicado. '
    result+='Assuntos em aberto permanecem em aberto; não voltam à fila apenas por terem status parcial no arquivo.\n\n'+link('Inicio','Voltar ao início')
    return result

def script_body(active,queue,waiting,consolidated,qlink,link):
    result=('A fila contém revisão da consistência dos relatos, não perguntas para completar o mundo. '
            'Conferir a documentação antes de consultar jogadores. O que ainda não foi revelado pode continuar desconhecido.\n\n')
    for i,q in enumerate(active,1):
        action='Pergunta focada' if q['acao_revisao']=='perguntar' else 'Conferir fontes'
        result+=f'## {i}. '+qlink(q['id'],short(q))+'\n\n'
        result+='**Por que revisar:** '+q['justificativa_revisao']+'\n\n'
        result+='**Efeito na leitura:** '+q.get('impacto_revisao','')+'\n\n'
        result+='**'+action+':** '+q['pergunta_revisada']+'\n\n'
        if q.get('consolidada_em'):result+='Escopo consolidado em '+qlink(q['consolidada_em'])+'.\n\n'
    if not active:result+='Nenhuma revisão imediata demonstrada. Não criar perguntas para ocupar a fila.\n\n'
    if waiting:
        result+='## Aguardar fonte — sem nova entrevista\n\n'+limits_table(waiting,qlink)+'\n\n'
    if consolidated:
        result+='## Evitar duplicação\n\n'
        for q in consolidated:result+='- '+qlink(q['id'],q['id'])+' faz parte de '+qlink(q['consolidada_em'],q['consolidada_em'])+'; não perguntar consciência, poderes ou detalhes não revelados por extensão.\n'
        result+='\n'
    result+='## O que não volta à fila\n\nMistérios, paradeiros, poderes e resultados futuros; desconhecimento já declarado; nomes, endereços e censos sem impacto no fluxo; contrapontos só aparentes entre sonho e realidade ou épocas distintas. '
    result+='Não repetir identidade de Kael/Okay, origem de Fash, causa das mortes de Lilo e Piche, retorno das portas ou outras confirmações já registradas. '
    result+='As perguntas originais ficam nos registros como histórico.\n\n'+link('Pendencias/Indice','Lista completa separada por critério')
    return result
