"""Auditoria independente, somente leitura das fontes; grava apenas seu relatorio.

Nao importa nem executa importadores. Compara bytes, paragrafos em ordem,
front matter literal, destinos de links e recortes de sessoes.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
import difflib
import hashlib
import json
import re
from urllib.parse import unquote

from fontes_migracao import SourceResolver

ROOT = Path(__file__).resolve().parents[1]
INV = json.loads((ROOT / 'docs/inventario-fontes.json').read_text(encoding='utf-8'))
MAN = json.loads((ROOT / 'docs/migracao/textos.json').read_text(encoding='utf-8'))
VAULT = Path(INV['source_root'])
SOURCES = SourceResolver(ROOT)
OUT = ROOT / 'docs/auditoria-exclusao/textos.json'
WIKI = re.compile(r'\[\[([^\]]+)\]\]')
errors = []
expected_origins = {x['source'] for x in INV['initial_files']} | {
    'vault-42/'+x['source'] for key in ('selected_markdown','selected_transcripts','selected_support','review_before_selection') for x in INV[key]}
expected_text_origins = {x for x in expected_origins if Path(x).suffix.lower() in ('.md','.txt','.json')}
manifest_origins = [x['origem'] for x in MAN['originais']]
converted_origins = [x['origem'] for x in MAN['conversoes']]
scope_coverage = dict(originais_esperados=len(expected_origins),textos_esperados=len(expected_text_origins),
    originais_faltantes=sorted(expected_origins-set(manifest_origins)),originais_extras=sorted(set(manifest_origins)-expected_origins),
    conversoes_faltantes=sorted(expected_text_origins-set(converted_origins)),conversoes_extras=sorted(set(converted_origins)-expected_text_origins),
    originais_duplicados=[x for x,c in Counter(manifest_origins).items() if c>1],
    conversoes_duplicadas=[x for x,c in Counter(converted_origins).items() if c>1])
if any(scope_coverage[k] for k in ('originais_faltantes','originais_extras','conversoes_faltantes','conversoes_extras','originais_duplicados','conversoes_duplicadas')):
    errors.append(dict(tipo='cobertura_escopo_incompleta',detalhes=scope_coverage))


def read(path):
    return path.read_text(encoding='utf-8-sig')


def source_path(origin):
    return SOURCES.resolve(origin)


def split_front(text):
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == '---':
        for n, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                return ''.join(lines[1:n]).rstrip('\n'), ''.join(lines[n+1:]).lstrip('\n')
    return '', text


def marked(text, start, end):
    a, b = '<!-- ' + start + ' -->', '<!-- ' + end + ' -->'
    if text.count(a) != 1 or text.count(b) != 1:
        raise ValueError('Marcadores ausentes/duplicados: ' + start)
    return text.split(a, 1)[1].split(b, 1)[0].strip('\n')


def unfence(text):
    lines = text.splitlines()
    if not lines or not re.fullmatch(r'`{3,}\w*', lines[0]):
        raise ValueError('Bloco integral sem cerca')
    if lines[-1] != re.match(r'`+', lines[0]).group():
        raise ValueError('Cerca integral incompleta')
    return '\n'.join(lines[1:-1])


def visible_wiki(match):
    target, sep, label = match.group(1).partition('|')
    return '[[' + (label if sep else target) + ']]'


def paragraphs(text, normalize_headings=False):
    if normalize_headings:
        text = re.sub(r'(?m)^([ \t]*(?:[*+-][ \t]+)?)#{1,6}[ \t]+', r'\1', text)
    text = WIKI.sub(visible_wiki, text)
    return [re.sub(r'\s+', ' ', p).strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]


def content_lines(text, normalize_headings=False):
    if normalize_headings:
        text = re.sub(r'(?m)^([ \t]*(?:[*+-][ \t]+)?)#{1,6}[ \t]+', r'\1', text)
    text = WIKI.sub(visible_wiki,text)
    return [line.rstrip(' \t') for line in text.strip('\n').rstrip().splitlines()]


def delta(a, b, maximum=5):
    differences = []
    for operation, i, j, k, l in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if operation != 'equal':
            differences.append(dict(operacao=operation, origem_intervalo=[i+1,j], destino_intervalo=[k+1,l],
                                    origem=a[i:j][:maximum], destino=b[k:l][:maximum]))
    return differences


def mdlinks(text):
    """Le links inline com parenteses balanceados, sem descartar URLs."""
    result = []
    for m in re.finditer(r'!?\[([^\[\]\n]*)\]\(', text):
        level, end = 1, m.end()
        while end < len(text) and level:
            if text[end] == '\\':
                end += 2
                continue
            if text[end] == '(':
                level += 1
            elif text[end] == ')':
                level -= 1
            end += 1
        if level == 0:
            result.append(dict(label=m.group(1), target=text[m.end():end-1], start=m.start(), end=end))
    return result


def session_parts(text, plain=False):
    """Recorte pelo titulo real, sem usar hashes ou corpo exportado do manifest."""
    boundaries = []
    pattern = r'(?m)^(Sess[ãa]o[ \t]+(?:\d+|Solo)\b[^\n]*)$' if plain else r'(?m)^#{1,6}[ \t]+([^\n]+)$'
    for m in re.finditer(pattern, text):
        heading = m.group(1).replace('**', '').replace('\\', '')
        ident = re.match(r'Sess[ãa]o\s+(\d+|Solo)\b', heading, re.I)
        if ident:
            boundaries.append((m, ident.group(1).lower(), heading))
    return [dict(sessao=ident, titulo=heading,
                 corpo=text[m.end():boundaries[i+1][0].start() if i+1 < len(boundaries) else len(text)].strip())
            for i,(m,ident,heading) in enumerate(boundaries)]


archive_records = []
for rec in MAN['originais']:
    origin = rec['origem']
    actual, archive = source_path(origin), ROOT / rec['arquivo']
    origin_exists = SOURCES.original_path(origin).is_file()
    row = dict(origem=origin, arquivo=rec['arquivo'], origem_existe=origin_exists, arquivo_existe=archive.is_file(),
               fonte_consultada=str(actual), origem_removida_com_registro=not origin_exists)
    if actual.is_file() and archive.is_file():
        a, b = actual.read_bytes(), archive.read_bytes()
        row.update(bytes_origem=len(a), bytes_arquivo=len(b), bytes_identicos=(a == b),
                   sha256_recalculado_origem=hashlib.sha256(a).hexdigest(),
                   sha256_recalculado_arquivo=hashlib.sha256(b).hexdigest(),
                   hash_manifesto_confere=(hashlib.sha256(a).hexdigest() == rec['sha256']))
    if not row.get('bytes_identicos'):
        errors.append(dict(tipo='arquivo_original_ausente_ou_divergente', origem=origin))
    archive_records.append(row)

conversions = []
wiki_changes = []
markdown_changes = []
for rec in MAN['conversoes']:
    origin = rec['origem']
    raw = read(source_path(origin))
    target_text = read(ROOT / rec['destino'])
    front, source_body = split_front(raw) if rec['metodo'] == 'markdown' else ('',raw)
    target_body = marked(target_text, 'inicio-conteudo-fonte', 'fim-conteudo-fonte')
    front_equal = True
    if front:
        match = re.search(r'<summary>Metadados da nota de origem</summary>\s*\n(`{3,})yaml\n(.*?)\n\1\s*\n', target_text, re.S)
        front_equal = bool(match and match.group(2) == front)
    source_wikis = list(WIKI.finditer(source_body))
    target_wikis = list(WIKI.finditer(target_body))
    visible_links_equal = [visible_wiki(m) for m in source_wikis] == [visible_wiki(m) for m in target_wikis]
    for n,(a,b) in enumerate(zip(source_wikis,target_wikis),1):
        old_target = a.group(1).split('|',1)[0]
        new_target = b.group(1).split('|',1)[0]
        if old_target != new_target:
            wiki_changes.append(dict(origem=origin, posicao=n, destino_original=old_target,
                                     destino_importado=new_target, rotulo_visivel_preservado=(visible_wiki(a)==visible_wiki(b))))
    a_md, b_md = mdlinks(source_body), mdlinks(target_body)
    md_equal = len(a_md) == len(b_md)
    replacements = []
    for a,b in zip(a_md,b_md):
        same = a['label'] == b['label'] and a['target'] == b['target']
        relative_transcript = (origin.endswith('Glim Sombrasselva - Session 26 Diary Draft.md') and
            unquote(a['target']) == '../../98 Attachments/GLIM - Sessao 26 - 2026-10-20 - Transcricao Completa.txt' and
            unquote(b['target']) == '../Transcricoes/Glim - Sessao 26 - 2026-10-20.md' and a['label'] == b['label'])
        md_equal = md_equal and (same or relative_transcript)
        if not same:
            markdown_changes.append(dict(origem=origin, destino_original=a['target'], destino_importado=b['target'],
                rotulo_preservado=a['label']==b['label'], reescrita_prevista=relative_transcript))
            if relative_transcript:
                replacements.append((b['start'], b['end'], source_body[a['start']:a['end']]))
    compare_body = target_body
    for begin,end,old in reversed(replacements):
        compare_body = compare_body[:begin] + old + compare_body[end:]
    integral = rec['metodo'] in ('transcricao-integral','json-integral')
    exact_integral = None
    if integral:
        compare_body = unfence(target_body)
        exact_integral = compare_body == source_body.rstrip('\n')
    normalize_headings = origin == 'BASE INICIAL/DIARIO DE RPG (Fash).md' or rec['metodo'] == 'texto-integral'
    source_paragraphs, target_paragraphs = paragraphs(source_body,normalize_headings), paragraphs(compare_body,normalize_headings)
    same_order = source_paragraphs == target_paragraphs
    same_lines = content_lines(source_body,normalize_headings) == content_lines(compare_body,normalize_headings)
    row = dict(origem=origin,destino=rec['destino'],metodo=rec['metodo'],
        paragrafos_origem=len(source_paragraphs),paragrafos_destino=len(target_paragraphs),
        paragrafos_iguais_na_mesma_ordem=same_order,linhas_iguais_apos_formatacao_declarada=same_lines,frente_yaml_presente=bool(front),frente_yaml_literal_preservada=front_equal,
        wikilinks_origem=len(source_wikis),wikilinks_destino=len(target_wikis),rotulos_wikilinks_preservados=visible_links_equal,
        links_markdown_origem=len(a_md),links_markdown_destino=len(b_md),links_markdown_preservados_ou_reescrita_s26=md_equal,
        bloco_integral_textual_exato=exact_integral)
    if not same_order:
        row['diferencas'] = delta(source_paragraphs,target_paragraphs)
    if not all((same_order,same_lines,front_equal,visible_links_equal,md_equal)) or exact_integral is False:
        errors.append(dict(tipo='diferenca_conversao',origem=origin,destino=rec['destino']))
    conversions.append(row)

diary_origin = next(x['origem'] for x in MAN['conversoes'] if x['origem'].startswith('BASE INICIAL/DIÁRIOS') and x['origem'].endswith('.md'))
diary = read(source_path(diary_origin))
parts = session_parts(diary)
by_id = {x['sessao']:x for x in parts}
sessions = []
for rec in MAN['sessoes']:
    expected = by_id[rec['sessao']]['corpo']
    body = marked(read(ROOT / rec['destino']),'inicio-diario','fim-diario')
    row = dict(sessao=rec['sessao'],destino=rec['destino'],corpo_textual_exato=(expected == body),
               paragrafos_mesma_ordem=(paragraphs(expected)==paragraphs(body)),data_mesa_ano_status=rec['data_mesa_ano_status'])
    if not row['corpo_textual_exato']:
        row['diferencas'] = delta(paragraphs(expected),paragraphs(body))
        errors.append(dict(tipo='diferenca_sessao',sessao=rec['sessao']))
    sessions.append(row)
if len(parts) != len(sessions) or len(by_id) != len(parts):
    errors.append(dict(tipo='cobertura_ou_duplicacao_sessoes',origem=len(parts),destino=len(sessions)))

variants = []
pairs = [(diary_origin,diary_origin.removesuffix('.md')+'.txt'),
    (diary_origin,'vault-42/20 Projects/Glim Sombrasselva/Glim Sombrasselva - Diary Full.md'),
    ('BASE INICIAL/BACKGROUND - GLIM SOMBRASSELVA.md','vault-42/20 Projects/Glim Sombrasselva/Glim Sombrasselva - Background Full.md'),
    ('BASE INICIAL/RPG - Handoff do cenario para o mestre.md','vault-42/70 Research/RPG - Handoff do cenario para o mestre.md')]
for left,right in pairs:
    a,b=read(source_path(left)),read(source_path(right))
    pa,pb=paragraphs(split_front(a)[1]),paragraphs(split_front(b)[1])
    sa,sb=session_parts(a,left.endswith('.txt')),session_parts(b,right.endswith('.txt'))
    row=dict(origem_a=left,origem_b=right,bytes_identicos=source_path(left).read_bytes()==source_path(right).read_bytes(),
             texto_integral_identico=(a==b),paragrafos_mesma_ordem=(pa==pb),
             paragrafos_exclusivos_a=sum((Counter(pa)-Counter(pb)).values()),
             paragrafos_exclusivos_b=sum((Counter(pb)-Counter(pa)).values()),
             ambas_variantes_têm_fontes_integrais=all(any(c['origem']==o and c['paragrafos_iguais_na_mesma_ordem'] for c in conversions) for o in (left,right)))
    row['interpretacao']='Contagens exclusivas consideram marcacao e segmentacao originais; nao significam perda narrativa. Cada variante foi comparada integralmente com sua propria nota importada.'
    if sa or sb:
        row['ordem_sessoes_a']=[x['sessao'] for x in sa]
        row['ordem_sessoes_b']=[x['sessao'] for x in sb]
        a_by,b_by={x['sessao']:x for x in sa},{x['sessao']:x for x in sb}
        row['sessoes_com_corpo_formatacao_espacos_equivalente']=[i for i in a_by.keys() & b_by.keys()
            if re.sub(r'[\\*#\s]+','',a_by[i]['corpo']) == re.sub(r'[\\*#\s]+','',b_by[i]['corpo'])]
        row['sessoes_com_corpo_formatacao_espacos_equivalente'].sort(key=lambda s:(s=='solo',int(s) if s.isdigit() else 0))
    variants.append(row)

# Somente testa existencia de destinos ja conhecidos pelo inventario: nao le outras notas do vault.
known_external = {Path(x['target']).stem: x['target'] for x in INV['wikilink_scan']['external_dependencies']}
known_external.update({'Drive - RPG BACKGROUNDS Folder':'40 Sources/Google Drive/RPG/Drive - RPG BACKGROUNDS Folder.md',
                       'Mundo de Auria':'30 Areas/RPG/Mundo de Auria.md'})
selected_paths = {'vault-42/'+x['source'] for key in ('selected_markdown','review_before_selection','selected_transcripts','selected_support') for x in INV[key]}
external_dependencies = []
for c in wiki_changes:
    old=c['destino_original'].split('#',1)[0]
    leaf=Path(old).stem
    if c['destino_importado']=='Fontes/Referencias do vault':
        candidate=known_external.get(leaf)
        path=VAULT/candidate if candidate else None
        external_dependencies.append(dict(origem=c['origem'],destino_original=old,
            caminho_conhecido_no_vault=candidate,existe_no_vault=path.is_file() if path else None,
            destino_copiado=bool(candidate and ('vault-42/'+candidate) in selected_paths),
            conteudo_destino_lido=False))

metadata_external = []
for rec in MAN['conversoes']:
    if rec['metodo'] != 'markdown':
        continue
    front,_ = split_front(read(source_path(rec['origem'])))
    for match in WIKI.finditer(front):
        old=match.group(1).split('|',1)[0].split('#',1)[0]
        candidate=known_external.get(Path(old).stem)
        if candidate and 'vault-42/'+candidate not in selected_paths:
            metadata_external.append(dict(origem=rec['origem'],destino_original=old,
                caminho_conhecido_no_vault=candidate,existe_no_vault=(VAULT/candidate).is_file(),
                destino_copiado=False,referencia_yaml_literal_preservada=True,conteudo_destino_lido=False))

provenance_origin=next(r['origem'] for r in MAN['conversoes'] if r['metodo']=='json-integral')
provenance=json.loads(read(source_path(provenance_origin)))
provenance_hashes=[]
for rec in provenance['sessions']:
    path=source_path((PurePosixPath(provenance_origin).parent/rec['fileName']).as_posix())
    raw=path.read_bytes()
    normalized=raw.decode('utf-8-sig').replace('\r\n','\n').encode('utf-8')
    provenance_hashes.append(dict(sessao=rec['session'],arquivo=path.name,
        hash_literal_atual_confere_manifesto_historico=hashlib.sha256(raw).hexdigest()==rec['consolidatedSha256'],
        hash_apos_normalizar_crlf_para_lf_confere=hashlib.sha256(normalized).hexdigest()==rec['consolidatedSha256'],
        bytes_lf=len(normalized),bytes_lf_manifesto=rec['consolidatedBytes']))

report=dict(data='2026-10-29',escopo=dict(fontes_base_textuais=7,arquivos_base_total=12,
    vault_selecionado=53,vault_markdown=37,vault_transcricoes_txt=14,vault_suporte=2,
    conversoes=60,sessoes=27,limite='Somente arquivos selecionados de Fash/Glim. Outras mesas, indices globais e dados pessoais fora do recorte nao foram lidos.'),
    metodo=dict(importadores_executados=False,fonte_comparada='Originais presentes ou cópias arquivadas com SHA-256 reconferido; ausências somente mediante auditoria e registro de limpeza concluída.',
        provas=['Igualdade direta byte a byte de fontes ainda presentes com seu arquivo; origens removidas usam a cópia cujo caminho e SHA-256 conferem nos três registros.',
            'Paragrafos integrais na mesma ordem, preservando palavras, pontuacao, URLs e marcacao que nao foi deliberadamente alterada.',
            'Rotulos dos wikilinks na mesma ordem; destinos originais e importados registrados separadamente.',
            'Blocos literais integrais das transcricoes e JSON sem interpretar/remover seu conteudo.',
            'Front matter original comparado literalmente com YAML guardado em details.',
            'Recorte independente dos titulos reais das 27 sessoes e igualdade textual integral de cada corpo.'],
        normalizacao=['Decodificacao UTF-8-sig e quebras CRLF/LF pelo leitor de texto.',
            'Espacos e quebras dentro de cada paragrafo, e linhas vazias entre paragrafos.',
            'Prefixos de titulo Markdown apenas no diario Fash e texto-integral, alterados deliberadamente na conversao.',
            'Wikilinks comparados pelo rotulo visivel, com destinos auditados em campo separado.',
            'Um link relativo da transcricao S26 convertido para seu equivalente importado.']),
    contagens=dict(originais_comparados=len(archive_records),originais_bytes_identicos=sum(x.get('bytes_identicos',False) for x in archive_records),
        origens_presentes=sum(x['origem_existe'] for x in archive_records),
        origens_removidas_com_registro=sum(x['origem_removida_com_registro'] for x in archive_records),
        conversoes_comparadas=len(conversions),conversoes_paragrafos_ordem_iguais=sum(c['paragrafos_iguais_na_mesma_ordem'] for c in conversions),
        conversoes_linhas_ordem_iguais=sum(c['linhas_iguais_apos_formatacao_declarada'] for c in conversions),
        fontes_com_front_yaml=sum(c['frente_yaml_presente'] for c in conversions),front_yaml_preservadas=sum(c['frente_yaml_presente'] and c['frente_yaml_literal_preservada'] for c in conversions),
        blocos_integrais_exatos=sum(c['bloco_integral_textual_exato'] is True for c in conversions),
        sessoes_corpos_exatos=sum(s['corpo_textual_exato'] for s in sessions),
        wikilinks_reescritos=len(wiki_changes),wikilinks_redirecionados_indice=len(external_dependencies),
        referencias_externas_yaml=len(metadata_external),
        destinos_externos_distintos_so_no_vault=len({x['caminho_conhecido_no_vault'] for x in external_dependencies+metadata_external if x['existe_no_vault']}),
        links_markdown_reescritos=len(markdown_changes),erros_reais=len(errors)),
    cobertura_escopo=scope_coverage,erros_reais=errors,arquivos_originais=archive_records,conversoes=conversions,sessoes=sessions,variantes=variants,
    alteracoes_wikilinks=wiki_changes,alteracoes_links_markdown=markdown_changes,dependencias_externas_conhecidas=external_dependencies,
    dependencias_externas_yaml=metadata_external,proveniencia_historica_transcricoes=provenance_hashes,
    fontes_consultadas=['docs/migracao/textos.json','docs/inventario-fontes.json','tools/importar_textos.py',
        'Fontes reais dos 65 registros de originais (12 BASE INICIAL e 53 vault selecionado).',
        'As 65 copias em arquivo/originais.','As 60 notas de fontes em conteudo/Fontes.','As 27 notas em conteudo/Sessoes.',
        'conteudo/Fontes/Referencias do vault.md (indice dos 3 destinos de corpo externos).',
        'Nomes/caminhos, sem conteudo, de 9 destinos externos conhecidos no vault.'],
    perdas_por_cenario={
        'apagar_apenas_BASE_INICIAL':dict(parecer_textos='Sem perda de bytes, narrativa, variantes ou ordem dos 7 textos enquanto arquivo/originais for mantido.',
            condicao='As 12 copias arquivadas sao byte a byte iguais; este subrelatorio nao verifica a qualidade das conversoes PDF/DOCX/XLSX.',
            perda='Caminho de origem e eventuais metadados de sistema de arquivos nao representados como conteudo. Nenhum arquivo foi excluido.'),
        'apagar_somente_53_arquivos_selecionados_do_vault':dict(parecer_textos='Sem perda dos bytes ou texto dos 53 selecionados enquanto arquivo/originais for mantido.',
            condicao='Excluir somente os 53 nomes explicitamente inventariados; nenhum parecer autoriza apagar o vault, pasta RPG inteira ou outras mesas.',
            perda='Links de outras notas do vault que apontam para os 53 removidos podem deixar de funcionar. Ha 9 destinos conhecidos ainda somente no vault (3 referencias de corpo e 14 referencias YAML); seus conteudos nao foram lidos nem copiados. Nao apagar esses destinos ou generalizar o parecer para todo RPG.'),
        'apagar_tambem_arquivo_originais':dict(parecer_textos='Nao e equivalente sem perdas; nao recomendado quando a exigencia e preservar todos os dados originais.',
            narrativa='Os 60 corpos importados e 27 recortes sao comparados; nenhuma omissao narrativa detectada se erros_reais estiver vazio.',
            perdas=['Bytes originais (CRLF/LF, BOM, espacos finais e formato Markdown deliberadamente alterado) nao sao reversiveis a partir das notas.',
                'Os destinos literais de 153 wikilinks reescritos deixam de estar no corpo convertido; o indice conserva os 3 nomes externos do corpo. Este relatorio registra o mapa por ocorrencia, mas o Markdown isolado nao reconstroi o formato exato de cada link original.',
                'Os 60 links de proveniencia arquivo original das notas ficam sem destino.',
                'Metadados de sistema de arquivos originais nao foram integralmente inventariados; sua recuperacao nao e garantida.'],
            preservado='Todo front matter YAML original em details; manifesto de proveniencia JSON integral; variantes narrativas e suas ordens como fontes separadas.',
            dependencia='Links e arquivos de Drive, gravacoes e notas globais fora do recorte nunca foram copiados integralmente por esta migracao.' )},
    limites=['Nao valida a transcricao frente ao audio, nem a atualidade dos documentos remotos do Drive.',
        'Nao abre documentos pessoais ou outras mesas. Existencia de destinos externos conhecidos e testada somente por nome/caminho.',
        'Nao verifica metadados NTFS completos, ADS, ACLs, datas originais ou reversibilidade byte a byte das notas convertidas.',
        'A equivalencia narrativa aceita somente as normalizacoes declaradas; os arquivos arquivados, e nao a normalizacao, provam preservacao byte a byte.',
        'Os hashes do manifesto historico de 13 transcricoes foram gerados com LF: nao correspondem aos bytes CRLF atuais, mas todos conferem apos normalizacao CRLF para LF. Nao se trata de omissao de texto da migracao.',
        'Os anos 2026 das sessoes 1-12 e solo sao inferidos e identificados como tal nas notas; nao sao informacao original confirmada.'],
    conclusao='CONDICIONAL: manter arquivo/originais permite retirar as copias de origem do recorte textual sem perder seus bytes. Remover tambem arquivo/originais perde fidelidade original e proveniencia navegavel. Nenhuma exclusao foi executada.')
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report['contagens'],ensure_ascii=True))
print(json.dumps(report['erros_reais'],ensure_ascii=True))
