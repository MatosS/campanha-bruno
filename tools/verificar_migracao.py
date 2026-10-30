"""Verificação de leitura: preservação, cobertura e navegação da migração."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote, urlparse

from fontes_migracao import SourceResolver, SourceResolutionError

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT/'conteudo'
ERRORS = []
COUNTS = dict(originais=0, conversoes_textuais=0, sessoes=0, hashes_saidas_binarias=0,
              notas_markdown=0, wikilinks=0, links_locais=0,
              origens_presentes=0, origens_removidas_com_registro=0)


def read(path):
    return path.read_text(encoding='utf-8-sig')


def load(name):
    return json.loads(read(ROOT/'docs/migracao'/name))


def check(condition, message):
    if not condition:
        ERRORS.append(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hash(path, expected):
    label = str(path)
    check(path.is_file(), 'Arquivo ausente: ' + label)
    if path.is_file():
        check(digest(path) == expected, 'Hash divergente: ' + label)


def verify_source(origin, expected):
    try:
        return sources.resolve(origin, expected)
    except SourceResolutionError as exc:
        check(False, str(exc))
        return None


def verify_output(relative_path, expected):
    try:
        sources.verify_output(relative_path, expected)
    except SourceResolutionError as exc:
        check(False, str(exc))


def metadata(raw, path):
    """Aceita o subconjunto YAML emitido pelos conversores, sem avaliar tags."""
    check(raw.startswith('---\n'), 'Sem frontmatter: ' + str(path))
    end = raw.find('\n---', 4)
    check(end >= 0, 'Frontmatter sem fechamento: ' + str(path))
    if end < 0:
        return {}, raw
    result = {}
    current = None
    for line in raw[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if re.match(r'^  - ', line):
            check(current is not None and isinstance(result.get(current), list), 'Lista inválida: ' + str(path))
            if current is not None:
                value = line[4:]
                try: value = json.loads(value)
                except json.JSONDecodeError: value = value.strip("'\"")
                result[current].append(value)
            continue
        match = re.match(r'^([a-zA-Z_][\w-]*):(?: (.*))?$', line)
        check(bool(match), 'YAML fora do subconjunto validado: ' + str(path) + ' — ' + line)
        if not match:
            continue
        current, value = match.groups()
        check(current not in result, 'Campo YAML repetido: ' + str(path) + ' — ' + current)
        if value is None or not value:
            result[current] = []
        else:
            try: result[current] = json.loads(value)
            except json.JSONDecodeError:
                if re.fullmatch(r'\[\s*(?:fash|glim)(?:\s*,\s*(?:fash|glim))*\s*\]', value):
                    result[current] = [x.strip() for x in value[1:-1].split(',')]
                else:
                    check(not any(x in value for x in [': ', ' #', '{', '}', '[', ']']), 'Escalar YAML ambíguo: ' + str(path))
                    result[current] = value.strip("'\"")
    for key in ['tipo','titulo','campanhas','publico','status','origens','aliases']:
        check(key in result, 'Campo obrigatório ausente: ' + str(path) + ' — ' + key)
    check(result.get('publico') is True, 'Nota não pública: ' + str(path))
    for key in ['campanhas','origens','aliases']:
        check(isinstance(result.get(key), list), 'Campo deveria ser lista: ' + str(path) + ' — ' + key)
    check(all(x in ['fash','glim'] for x in result.get('campanhas',[])), 'Campanha desconhecida: ' + str(path))
    return result, raw[end+4:]


def without_code(body):
    result = []
    fence = None
    for line in body.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append(re.sub(r'(`+).*?\1', '', line))
    return '\n'.join(result)


survey = json.loads(read(ROOT/'docs/inventario-fontes.json'))
sources = SourceResolver(ROOT)
if sources.execution is not None:
    try:
        sources.validate_execution()
    except SourceResolutionError as exc:
        check(False, str(exc))
text_manifest = load('textos.json')
for rec in text_manifest['originais']:
    archived = ROOT/rec['arquivo']
    verify_hash(archived, rec['sha256'])
    source = verify_source(rec['origem'], rec['sha256'])
    if source is not None:
        key = 'origens_presentes' if sources.original_path(rec['origem']).is_file() else 'origens_removidas_com_registro'
        COUNTS[key] += 1
    COUNTS['originais'] += 1

coverage = {}
for rec in text_manifest['conversoes']:
    dest = ROOT/rec['destino']
    check(dest.is_file(), 'Conversão textual ausente: ' + rec['destino'])
    if dest.is_file():
        match = re.search(r'<!-- inicio-conteudo-fonte -->\n(.*?)\n<!-- fim-conteudo-fonte -->', read(dest), re.S)
        check(bool(match), 'Corpo de fonte ausente: ' + rec['destino'])
        if match:
            actual = hashlib.sha256(match.group(1).encode()).hexdigest()
            check(actual == rec['corpo_convertido_sha256'], 'Corpo textual divergente: ' + rec['destino'])
    coverage.setdefault(rec['origem'], []).append(rec['destino'])
    COUNTS['conversoes_textuais'] += 1

for rec in text_manifest['sessoes']:
    dest = ROOT/rec['destino']
    raw = read(dest)
    inferred = rec['sessao'] == 'solo' or int(rec['sessao']) < 13
    expected_status = 'inferido' if inferred else 'documentado'
    check(rec.get('data_mesa_ano_status') == expected_status, 'Proveniência do ano ausente: ' + rec['destino'])
    check(f'data_mesa_ano_status: "{expected_status}"' in raw, 'Ano sem status nos metadados: ' + rec['destino'])
    match = re.search(r'<!-- inicio-diario -->\n(.*?)\n<!-- fim-diario -->', read(dest), re.S)
    check(bool(match), 'Diário ausente: ' + rec['destino'])
    if match:
        check(hashlib.sha256(match.group(1).encode()).hexdigest() == rec['corpo_sha256'], 'Texto do diário alterado: ' + rec['destino'])
    COUNTS['sessoes'] += 1

pdf = load('pdf.json')
for doc in pdf['documents']:
    coverage[doc['source']['path']] = [doc['markdown']]
    verify_source(doc['source']['path'], doc['source']['sha256'])
    for rec in doc['outputs']:
        verify_output(rec['path'], rec['sha256'])
        COUNTS['hashes_saidas_binarias'] += 1
    check(doc['text_extractors_same_characters_all_pages'], 'Extratores PDF discordam: ' + doc['source']['path'])

workbooks = load('planilhas.json')
for book in workbooks['fontes']:
    coverage[book['fonte']] = [book['indice']] + [s['saida_markdown'] for s in book['abas']]
    verify_source(book['fonte'], book['sha256'])
    for rec in book['saidas']:
        verify_output(rec['caminho'], rec['sha256'])
        COUNTS['hashes_saidas_binarias'] += 1
    for rec in book['abas']:
        for field in ['coordenadas_so_no_xml','coordenadas_so_no_openpyxl','formulas_divergentes','valores_literais_convertidos_ou_divergentes','caches_convertidos_ou_divergentes']:
            check(not rec['conferencias'].get(field), 'Divergência na planilha: ' + book['fonte'] + ' / ' + rec['nome'] + ' / ' + field)

docx = load('docx.json')
coverage[docx['fonte']['caminho']] = [docx['destino']]
verify_source(docx['fonte']['caminho'], docx['fonte']['sha256'])
for rec in docx['arquivos_gerados']:
    verify_output(rec['caminho'], rec['sha256'])
    COUNTS['hashes_saidas_binarias'] += 1
check(docx['verificacoes']['todos_paragrafos_e_celulas_texto_exato'], 'DOCX com texto divergente')
for rec in text_manifest['originais']:
    check(rec['origem'] in coverage, 'Origem sem conversão: ' + rec['origem'])

graph = {}
notes = sorted(CONTENT.rglob('*.md'))
for path in notes:
    rel = path.relative_to(CONTENT).as_posix()
    meta, body = metadata(read(path), rel)
    content = without_code(body)
    graph[rel] = []
    for link in re.findall(r'\[\[([^\]]+)\]\]', content):
        link = link.replace('\\|', '|')
        target = link.split('|')[0].split('#')[0]
        if not target:
            continue
        target_file = target if Path(target).suffix else target + '.md'
        destination = CONTENT/target_file
        check(destination.is_file(), 'Wikilink sem destino: ' + rel + ' -> ' + target)
        if destination.suffix == '.md':
            graph[rel].append(destination.relative_to(CONTENT).as_posix())
        COUNTS['wikilinks'] += 1
    for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', content):
        link = link.strip().strip('<>')
        if not link or link.startswith('#') or urlparse(link).scheme:
            continue
        dest = path.parent/unquote(link.split('#')[0])
        check(dest.is_file(), 'Link local sem destino: ' + rel + ' -> ' + link)
        COUNTS['links_locais'] += 1
    COUNTS['notas_markdown'] += 1

reachable = set()
pending = ['Inicio.md']
while pending:
    key = pending.pop()
    if key in reachable:
        continue
    reachable.add(key)
    pending.extend(graph.get(key, []))
orphans = sorted(set(graph) - reachable)
check(not orphans, 'Notas sem caminho a partir do início: ' + ', '.join(orphans))
check(COUNTS['originais'] == 65, 'Contagem inesperada de originais')
check(COUNTS['sessoes'] == 27, 'Contagem inesperada de sessões')
check(len(coverage) == 65, 'Cobertura incompleta das 65 origens')

report = dict(data='2026-10-29', aprovado=not ERRORS, contagens=COUNTS,
              origens_com_destino=len(coverage), cobertura_base_inicial={r['source']:coverage.get(r['source'],[]) for r in survey['initial_files']},
              notas_alcancaveis=len(reachable), notas_orfas=orphans, erros=ERRORS,
              escopo_yaml='Subconjunto YAML de escalares e listas produzido pelos conversores; não é um parser YAML genérico.',
              limpeza_registrada=({'estado': sources.execution.get('estado'), 'data': sources.execution.get('data'),
                                   'registro': 'docs/limpeza/execucao.json',
                                   'scripts_atualizados': sources.execution.get('scripts_atualizados', [])} if sources.execution else None),
              observacoes=['Hashes conferem as cópias arquivadas e os originais ainda presentes; ausências exigem os mesmos caminhos e hashes no manifesto, na auditoria e no registro de limpeza concluída.',
                           'A validação não transforma interpretações narrativas em fatos confirmados.',
                           'Esta verificação não exclui arquivos nem publica o site.'])
(ROOT/'docs/migracao/verificacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(aprovado=report['aprovado'],contagens=COUNTS,origens_com_destino=len(coverage),erros=ERRORS),ensure_ascii=True,indent=2))
raise SystemExit(0 if not ERRORS else 1)
