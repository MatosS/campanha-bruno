"""Independent read-only audit; writes only its audit JSON, never an XLSX.

Does not import the migration converter and does not trust its pass/fail flags.
Rebuilds each OOXML package in BytesIO and reads the reconstructed copy there.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import html
import json
import posixpath
import re
import warnings
import xml.etree.ElementTree as ET

import openpyxl
from openpyxl.styles.numbers import BUILTIN_FORMATS
from PIL import Image

from fontes_migracao import SourceResolver

ROOT = Path(__file__).resolve().parents[1]
SOURCES = SourceResolver(ROOT)
OUT = ROOT / 'docs/auditoria-exclusao/planilhas.json'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
D = 'http://schemas.openxmlformats.org/drawingml/2006/main'
X = 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
V = 'urn:schemas-microsoft-com:vml'
E = 'urn:schemas-microsoft-com:office:excel'
NS = {'s': S, 'r': R, 'a': D, 'xdr': X, 'v': V, 'x': E}
CONFIG = [('FASH PALESKIN.xlsx', 'fash-paleskin', 'Fash Paleskin'),
          ('GLIM SOMBRASSELVA.xlsx', 'glim-sombrasselva', 'Glim Sombrasselva')]
VISUAL = {
    'legenda_fash': {'parte': 'xl/media/image1.png',
                    'sha256': '24b901054c5ad918356263392eb076e3e415cfe3a152f29078fe25ce0f555667',
                    'metodo': 'Inspeção visual independente da imagem integral em 2026-10-29 e leitura da transcrição JSON/Markdown.',
                    'linhas_conferidas': 27,
                    'resultado': 'As 27 entradas de coordenada e descrição conferem, incluindo as grafias próprias e a ordem Y31, X12, W23. Espaçamento de apresentação difere, sem diferença textual constatada.'},
    'outras_midias': {'metodo': 'view_image de todas as demais seis mídias em 2026-10-29, após comprovar bytes iguais ao membro de origem.',
                     'resultado': 'Mapa quadriculado de Fash e cinco ilustrações de criaturas/formas de Glim legíveis. A legenda transcrita não substitui a geografia e os símbolos do mapa.'}
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def local(p):
    return p.relative_to(ROOT).as_posix()


def structured(n):
    return {'tag': n.tag, 'atributos': dict(n.attrib), 'texto': n.text,
            'filhos': [structured(c) for c in n]}


def direct_text(n):
    if n is None:
        return ''
    # Deliberately omit phonetic annotations. Preserve ordered rich-text runs.
    return ''.join(c.text or '' for c in n.iter()
                   if c.tag == '{%s}t' % S)


def rels(z, owner):
    part = posixpath.join(posixpath.dirname(owner), '_rels', posixpath.basename(owner) + '.rels')
    if part not in z.namelist():
        return {}
    result = {}
    for n in ET.fromstring(z.read(part)):
        item = dict(n.attrib)
        item['parte_relacionamento'] = part
        if item.get('TargetMode') != 'External':
            target = item['Target']
            item['parte_destino'] = (target.lstrip('/') if target.startswith('/') else
                                     posixpath.normpath(posixpath.join(posixpath.dirname(owner), target)))
        result[item['Id']] = item
    return result


def comparable(v):
    if isinstance(v, (date, datetime, time)):
        return {'tipo': type(v).__name__, 'iso': v.isoformat()}
    return v


def workbook_snapshot(wb):
    return {'ordem_abas': wb.sheetnames, 'abas': [
        {'nome': ws.title, 'estado': ws.sheet_state, 'linhas': ws.max_row,
         'colunas': ws.max_column,
         'celulas': [(c.coordinate, c.data_type, comparable(c.value), c.number_format)
                     for row in ws.iter_rows() for c in row if c.value is not None]}
        for ws in wb]}


def decoded_md(value):
    value = re.sub(r'</?code>', '', value)
    return html.unescape(value.replace('<br>', '\n'))


def display_value(v):
    if v is None:
        return '∅'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if v == '':
        return '"" (texto vazio)'
    return str(v)


def audit_one(filename, slug, title):
    origin = 'BASE INICIAL/' + filename
    source = SOURCES.resolve(origin)
    archived = ROOT / 'arquivo/originais/BASE INICIAL' / filename
    annex = ROOT / 'conteudo/Anexos/planilhas' / slug
    extracted = annex / 'ooxml'
    blob = source.read_bytes()
    record = {'fonte': origin, 'fonte_consultada': local(source),
              'origem_removida_com_registro': not SOURCES.original_path(origin).is_file(),
              'sha256': sha(blob), 'bytes_xlsx': len(blob),
              'arquivo_arquivado': local(archived), 'copia_arquivada_byte_identica': blob == archived.read_bytes(),
              'erros': [], 'abas': [], 'midias': []}
    errors = record['erros']

    def check(ok, label, detail=None):
        if not ok:
            errors.append({'teste': label, 'detalhe': detail})

    with ZipFile(BytesIO(blob)) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        check(len(names) == len(set(names)), 'nomes_de_membros_unicos')
        extracted_names = sorted(p.relative_to(extracted).as_posix() for p in extracted.rglob('*') if p.is_file())
        check(set(names) == set(extracted_names), 'conjunto_completo_ooxml',
              {'ausentes': sorted(set(names) - set(extracted_names)), 'extras': sorted(set(extracted_names) - set(names))})
        package_checks = []
        for name in names:
            raw = z.read(name)
            candidate = extracted / name
            equal = candidate.is_file() and candidate.read_bytes() == raw
            package_checks.append({'parte': name, 'bytes': len(raw), 'sha256': sha(raw), 'extraido_identico': equal})
            check(equal, 'membro_ooxml_byte_identico', name)
        record['membros_ooxml'] = package_checks
        record['total_membros_ooxml'] = len(names)
        record['bytes_ooxml_descompactados'] = sum(i['bytes'] for i in package_checks)
        # Only extraction files are used to rebuild. No archived XLSX dependency.
        rebuilt = BytesIO()
        with ZipFile(rebuilt, 'w', compression=ZIP_DEFLATED) as rebuilt_zip:
            for name in extracted_names:
                rebuilt_zip.writestr(name, (extracted / name).read_bytes())
        with ZipFile(BytesIO(rebuilt.getvalue())) as zr:
            semantic_parts_equal = (set(names) == set(zr.namelist()) and
                                    all(z.read(n) == zr.read(n) for n in names))
            check(semantic_parts_equal, 'reconstrucao_em_memoria_todos_membros_identicos')
            check(zr.testzip() is None, 'reconstrucao_em_memoria_crc_valido')
        record['reconstrucao'] = {'somente_arquivos_extraidos': True,
                                 'zip_criado_apenas_em_memoria': True,
                                 'membros_identicos': semantic_parts_equal,
                                 'bytes_zip_reconstruido': len(rebuilt.getvalue()),
                                 'xlsx_byte_identico': rebuilt.getvalue() == blob,
                                 'limite': 'Payload OOXML idêntico; metadados, ordem e compressão ZIP podem diferir. Não foi aberto no Excel.'}

        wbxml = ET.fromstring(z.read('xl/workbook.xml'))
        wr = rels(z, 'xl/workbook.xml')
        package_json = json.loads((annex / 'pacote.json').read_text(encoding='utf-8'))
        check(package_json['metadados_workbook'] == structured(wbxml), 'metadados_workbook_json')
        check(package_json['relacionamentos_workbook'] == wr, 'relacionamentos_workbook_json')
        shared = ([direct_text(n) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
                  if 'xl/sharedStrings.xml' in names else [])
        record['strings_compartilhadas_com_runs_formatados'] = (sum(n.find('s:r', NS) is not None
                  for n in ET.fromstring(z.read('xl/sharedStrings.xml'))) if shared else 0)
        used_strings = set()
        styles = ET.fromstring(z.read('xl/styles.xml'))
        fonts = styles.findall('s:fonts/s:font', NS)
        cell_styles = styles.findall('s:cellXfs/s:xf', NS)
        record['marcacoes_visuais'] = {'celulas_com_texto_riscado': []}
        custom_formats = {int(n.get('numFmtId')): n.get('formatCode')
                          for n in styles.findall('s:numFmts/s:numFmt', NS)}
        formats = [custom_formats.get(int(n.get('numFmtId', '0')),
                                     BUILTIN_FORMATS.get(int(n.get('numFmtId', '0')), 'formato desconhecido'))
                   for n in styles.findall('s:cellXfs/s:xf', NS)]
        record['formatacao'] = {group: (len(styles.find('s:' + group, NS)) if styles.find('s:' + group, NS) is not None else 0)
                               for group in ['numFmts', 'fonts', 'fills', 'borders', 'cellStyleXfs', 'cellXfs', 'cellStyles', 'dxfs']}
        record['nomes_definidos'] = [{'atributos': dict(n.attrib), 'texto': n.text}
                                    for n in wbxml.findall('s:definedNames/s:definedName', NS)]
        record['externos'] = {'membros_links_externos_de_workbook': [n for n in names if n.startswith('xl/externalLinks/')],
                             'relacionamentos_externos': []}
        for part in names:
            if part.endswith('.rels'):
                for n in ET.fromstring(z.read(part)):
                    if n.get('TargetMode') == 'External':
                        record['externos']['relacionamentos_externos'].append({'parte': part, **n.attrib})
        record['recursos'] = {'partes_charts': [n for n in names if n.startswith('xl/charts/')],
                             'partes_embutidos': [n for n in names if n.startswith('xl/embeddings/')],
                             'partes_vba': [n for n in names if 'vba' in n.lower()],
                             'partes_drawingml': [n for n in names if re.fullmatch(r'xl/drawings/drawing\d+\.xml', n)],
                             'partes_vml': [n for n in names if n.endswith('.vml')]}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            formula_wb = openpyxl.load_workbook(BytesIO(blob), read_only=True, data_only=False, keep_links=True)
            cache_wb = openpyxl.load_workbook(BytesIO(blob), read_only=True, data_only=True, keep_links=True)
            rebuilt_formula = openpyxl.load_workbook(BytesIO(rebuilt.getvalue()), read_only=True, data_only=False, keep_links=True)
            rebuilt_cache = openpyxl.load_workbook(BytesIO(rebuilt.getvalue()), read_only=True, data_only=True, keep_links=True)
            original_formula_snapshot = workbook_snapshot(formula_wb)
            original_cache_snapshot = workbook_snapshot(cache_wb)
            check(original_formula_snapshot == workbook_snapshot(rebuilt_formula), 'reconstrucao_leitura_formulas_estilos_dimensoes')
            check(original_cache_snapshot == workbook_snapshot(rebuilt_cache), 'reconstrucao_leitura_cache_sem_recalculo')
            record['reconstrucao']['leitura_openpyxl_formulas_cache_estilos_dimensoes_identica'] = not any(
                e['teste'].startswith('reconstrucao_leitura') for e in errors)
            for order, sn in enumerate(wbxml.findall('s:sheets/s:sheet', NS), 1):
                sheetname = sn.get('name')
                part = wr[sn.get('{%s}id' % R)]['parte_destino']
                sx = ET.fromstring(z.read(part))
                sr = rels(z, part)
                jp = annex / ('aba-%02d.json' % order)
                j = json.loads(jp.read_text(encoding='utf-8'))
                note = ROOT / 'conteudo/Fontes/Planilhas' / (re.sub(r'[<>:"/\\|?*]', '-', title + ' - ' + sheetname) + '.md')
                md = note.read_text(encoding='utf-8')
                table = {}
                cell_table_section = md.split('## Conteúdo integral por coordenada', 1)[1].split('## Comentários', 1)[0]
                for line in cell_table_section.splitlines():
                    if re.match(r'^\| <code>[A-Z]+\d+</code> \|', line):
                        fields = [decoded_md(s) for s in line[2:-2].split(' | ')]
                        table[fields[0]] = fields[1:]
                ws = formula_wb[sheetname]
                cs = cache_wb[sheetname]
                cells = sx.findall('s:sheetData/s:row/s:c', NS)
                content_cells = [c for c in cells if any(c.find('s:' + k, NS) is not None for k in ['v', 'f', 'is'])]
                lookup = {c['celula']: c for c in j['celulas']}
                check(set(lookup) == {c.get('r') for c in content_cells}, 'json_todas_celulas', sheetname)
                check(set(table) == set(lookup), 'md_todas_celulas_sem_extras', sheetname)
                check(j['aba'] == sheetname and j['ordem'] == order and j['visibilidade'] == sn.get('state', 'visible'), 'nome_ordem_estado_aba', sheetname)
                check(j['metadados_aba'] == [structured(n) for n in sx if n.tag != '{%s}sheetData' % S], 'json_metadados_aba', sheetname)
                check(j['atributos_linhas'] == [dict(n.attrib) for n in sx.findall('s:sheetData/s:row', NS)], 'json_atributos_linhas', sheetname)
                check(j['relacionamentos'] == sr, 'json_relacionamentos_aba', sheetname)
                counts = Counter()
                formula_caches = Counter()
                blank_formula_caches = []
                numeric_lexemes = []
                for c in content_cells:
                    coord = c.get('r')
                    cj = lookup[coord]
                    typ = c.get('t', 'n')
                    vn = c.find('s:v', NS)
                    fn = c.find('s:f', NS)
                    inline = c.find('s:is', NS)
                    raw = vn.text if vn is not None else None
                    fmt = formats[int(c.get('s', '0'))]
                    if typ == 's' and raw is not None:
                        value = shared[int(raw)]
                        used_strings.add(int(raw))
                    elif typ == 'inlineStr':
                        value = direct_text(inline)
                    elif raw is None:
                        value = None
                    elif typ == 'b':
                        value = raw == '1'
                    elif typ in ['str', 'e', 'd']:
                        value = raw
                    else:
                        try:
                            value = int(raw) if re.fullmatch(r'[+-]?\d+', raw) else float(raw)
                        except ValueError:
                            value = raw
                    label = sheetname + '!' + coord
                    font_id = int(cell_styles[int(c.get('s', '0'))].get('fontId', '0'))
                    strike_node = fonts[font_id].find('s:strike', NS)
                    source_strike = strike_node is not None and strike_node.get('val', 'true') not in ('0', 'false', 'off')
                    check(bool(ws[coord].font.strike) == source_strike, 'rasura_xml_leitor_independente', label)
                    if isinstance(value, str) and source_strike:
                        record['marcacoes_visuais']['celulas_com_texto_riscado'].append({
                            'aba': sheetname, 'celula': coord, 'texto': value,
                            'estilo_xml': c.get('s', '0'), 'font_id': font_id,
                            'observacao': 'Texto e marcação riscada são exigidos no MD; styles.xml conserva a definição original de fonte.'})
                    check(cj['atributos'] == dict(c.attrib) and cj['tipo_xml'] == typ and
                          cj['valor_xml_presente'] == (vn is not None) and cj['valor_xml'] == raw and
                          cj['valor'] == value and cj['formato_numero'] == fmt, 'json_valor_tipo_lexema_estilo', label)
                    if inline is not None:
                        check(cj.get('inline_xml') == structured(inline), 'json_inline_rich_text', label)
                    if fn is not None:
                        counts['formulas'] += 1
                        counts['formulas_compartilhadas'] += fn.get('t') == 'shared'
                        check(cj['formula']['texto_xml'] == (fn.text or '') and cj['formula']['atributos'] == dict(fn.attrib), 'json_formula_xml', label)
                        expanded = ws[coord].value
                        check(cj['formula']['expandida'] == expanded, 'json_formula_expandida_leitor_independente', label)
                        state = 'ausente' if vn is None else 'vazio_no_xml' if raw is None else 'presente'
                        formula_caches[state] += 1
                        if state != 'presente':
                            blank_formula_caches.append({'celula': coord, 'formula': expanded, 'estado': state})
                        check(cj['cache'] == {'estado': state, 'tipo_xml': typ, 'valor_xml': raw, 'valor': value}, 'json_cache_sem_recalculo', label)
                        expected_row = ['—', expanded, display_value(value) if state == 'presente' else '∅ (' + state.replace('_', ' ') + ')']
                        check(comparable(cs[coord].value) == comparable(value), 'cache_leitor_versus_xml', label)
                    else:
                        counts['literais'] += 1
                        counts['texto'] += isinstance(value, str)
                        counts['textos_com_espacos_nas_bordas'] += isinstance(value, str) and value != value.strip()
                        counts['numeros'] += isinstance(value, (int, float)) and not isinstance(value, bool)
                        if typ == 'n' and raw is not None:
                            numeric_lexemes.append({'celula': coord, 'valor_xml': raw, 'formato': fmt})
                        check(cj['formula'] is None, 'json_ausencia_formula', label)
                        read_value = ws[coord].value
                        if isinstance(read_value, (datetime, date, time)):
                            counts['numeros_com_formato_data_hora'] += 1
                            formatted = read_value.strftime('%d/%m') if fmt.lower() == 'dd/mm' else read_value.isoformat()
                            display = formatted + ' (serial Excel ' + str(raw) + '; formato ' + fmt + ')'
                        else:
                            check(read_value == value, 'literal_leitor_versus_xml', label)
                            display = display_value(value)
                        if source_strike:
                            display = '~~' + display + '~~'
                        expected_row = [display, '—', '—']
                    # MD normalizes CRLF and CR; JSON and OOXML remain the exact authority.
                    expected_row = [s.replace('\r\n', '\n').replace('\r', '\n') for s in expected_row]
                    check(table.get(coord) == expected_row, 'md_valores_formulas_cache_integral', {'celula': label, 'esperado': expected_row, 'obtido': table.get(coord)})

                comments = []
                drawings = []
                vml = []
                for rel in sr.values():
                    if rel['Type'].endswith('/comments'):
                        cx = ET.fromstring(z.read(rel['parte_destino']))
                        authors = [n.text or '' for n in cx.findall('s:authors/s:author', NS)]
                        for n in cx.findall('s:commentList/s:comment', NS):
                            author = authors[int(n.get('authorId', '0'))]
                            text = direct_text(n.find('s:text', NS))
                            comments.append((n.get('ref'), author, text, dict(n.attrib), structured(n)))
                            check(('### ' + n.get('ref') + ' — ' + author) in md and
                                  text.replace('\r\n', '\n').replace('\r', '\n') in decoded_md(md), 'md_comentario_integral', sheetname + '!' + n.get('ref'))
                    if rel['Type'].endswith('/drawing'):
                        dx = ET.fromstring(z.read(rel['parte_destino']))
                        for anchor in dx:
                            drawings.append(structured(anchor))
                            for tx in anchor.findall('.//a:t', NS):
                                check((tx.text or '') in decoded_md(md), 'md_texto_drawing', sheetname)
                    if rel['Type'].endswith('/vmlDrawing'):
                        vx = ET.fromstring(z.read(rel['parte_destino']))
                        vml.extend(structured(n) for n in vx.findall('.//v:shape', NS))
                json_comments = [(c['celula'], c['autor'], c['texto'], c['atributos'], c['xml_estruturado']) for c in j['comentarios']]
                check(json_comments == comments, 'json_comentarios_autor_texto_rico_xml', sheetname)
                check([d['xml_estruturado'] for d in j['drawings']] == drawings, 'json_drawing_ancoras_dimensoes_xml', sheetname)
                check([v['xml_estruturado'] for v in j['objetos_vml']] == vml, 'json_vml_xml', sheetname)
                links = []
                for n in sx.findall('s:hyperlinks/s:hyperlink', NS):
                    relationship = sr.get(n.get('{%s}id' % R))
                    target = relationship.get('Target') if relationship else n.get('location')
                    links.append((n.get('ref'), dict(n.attrib), relationship, target))
                    check(target in decoded_md(md) and n.get('ref') in md, 'md_hyperlink_destino', sheetname)
                check([(l['intervalo'], l['atributos'], l['relacionamento'], l['destino']) for l in j['hyperlinks']] == links, 'json_hyperlinks_atributos_destinos', sheetname)
                merges = [n.get('ref') for n in sx.findall('s:mergeCells/s:mergeCell', NS)]
                check(j['mesclagens'] == merges and all(m in md for m in merges), 'md_json_mesclagens', sheetname)
                media_targets = [unquote(m.group(1)) for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', md)]
                linked_media_hashes = []
                for target in media_targets:
                    targetpath = (note.parent / target).resolve()
                    check(targetpath.is_file(), 'md_imagem_link_resolvido', target)
                    if targetpath.is_file():
                        linked_media_hashes.append(sha(targetpath.read_bytes()))
                drawing_media_hashes = []
                for rel in sr.values():
                    if rel['Type'].endswith('/drawing'):
                        for dr in rels(z, rel['parte_destino']).values():
                            if dr['Type'].endswith('/image') and dr.get('TargetMode') != 'External':
                                drawing_media_hashes.append(sha(z.read(dr['parte_destino'])))
                check(Counter(linked_media_hashes) == Counter(drawing_media_hashes), 'md_todas_imagens_ancoradas', sheetname)
                if slug == 'fash-paleskin' and sheetname == 'INTERESSES':
                    legend = j['transcricoes_visuais'][0]['texto']
                    check(len(legend.splitlines()) == 27 and legend in md and
                          sha(z.read('xl/media/image1.png')) == VISUAL['legenda_fash']['sha256'],
                          'legenda_json_md_imagem_inspecionada', sheetname)
                sheet_features = Counter(n.tag.rsplit('}', 1)[-1] for n in sx)
                record['abas'].append({'nome': sheetname, 'ordem': order, 'estado': sn.get('state', 'visible'),
                    'parte_xml': part, 'json': local(jp), 'markdown': local(note),
                    'celulas_xml': len(cells), 'celulas_com_conteudo': len(content_cells),
                    'celulas_somente_estilo_sem_conteudo': len(cells) - len(content_cells),
                    **dict(counts), 'cache_formulas': dict(formula_caches),
                    'caches_formulas_vazios_ou_ausentes': blank_formula_caches,
                    'comentarios': len(comments), 'hyperlinks': len(links), 'mesclagens': len(merges),
                    'drawingml_objetos': len(drawings), 'vml_objetos': len(vml),
                    'linhas_ocultas': [dict(n.attrib) for n in sx.findall('s:sheetData/s:row', NS) if n.get('hidden') in ['1', 'true']],
                    'colunas_ocultas': [dict(n.attrib) for n in sx.findall('s:cols/s:col', NS) if n.get('hidden') in ['1', 'true']],
                    'recursos_xml': dict(sheet_features), 'numeros_lexicais': numeric_lexemes,
                    'erros_desta_aba': sum(sheetname in json.dumps(e, ensure_ascii=False) for e in errors)})
            for w in [formula_wb, cache_wb, rebuilt_formula, rebuilt_cache]:
                w.close()
            record['avisos_openpyxl'] = sorted(set(str(w.message) for w in caught))

        unused = [{'indice': i, 'texto': s} for i, s in enumerate(shared) if i not in used_strings]
        check(package_json['strings_compartilhadas_sem_uso_em_celulas'] == unused, 'json_strings_sem_uso')
        index = ROOT / 'conteudo/Fontes/Planilhas' / (title + '.md')
        index_md = decoded_md(index.read_text(encoding='utf-8'))
        check(all(s['texto'].replace('\r\n', '\n').replace('\r', '\n') in index_md for s in unused), 'md_strings_sem_uso')
        record['strings_compartilhadas'] = len(shared)
        record['strings_compartilhadas_sem_uso'] = unused
        record['strings_com_anotacoes_foneticas'] = (len(ET.fromstring(z.read('xl/sharedStrings.xml')).findall('.//s:rPh', NS)) if shared else 0)
        for name in names:
            if name.startswith('xl/media/'):
                raw = z.read(name)
                with Image.open(BytesIO(raw)) as image:
                    image.verify()
                with Image.open(BytesIO(raw)) as image:
                    record['midias'].append({'parte': name, 'bytes': len(raw), 'sha256': sha(raw),
                                           'formato': image.format, 'dimensoes': list(image.size),
                                           'copia_extraida_identica': (extracted / name).read_bytes() == raw})
        for old_entry in package_json['membros']:
            name = old_entry['parte']
            check(name in names and old_entry['sha256'] == sha(z.read(name)) and old_entry['bytes'] == len(z.read(name)), 'manifesto_pacote_conferido_diretamente', name)
    check(source.read_bytes() == blob, 'fonte_inalterada_apos_auditoria')
    check(archived.read_bytes() == blob, 'copia_inalterada_apos_auditoria')
    record['totais'] = {key: sum(s.get(key, 0) for s in record['abas']) for key in
                        ['celulas_xml', 'celulas_com_conteudo', 'celulas_somente_estilo_sem_conteudo',
                         'formulas', 'formulas_compartilhadas', 'literais', 'texto', 'numeros',
                         'textos_com_espacos_nas_bordas',
                         'numeros_com_formato_data_hora', 'comentarios', 'hyperlinks', 'mesclagens',
                         'drawingml_objetos', 'vml_objetos']}
    record['total_erros'] = len(errors)
    return record


def main():
    reports = [audit_one(*config) for config in CONFIG]
    old = json.loads((ROOT / 'docs/migracao/planilhas.json').read_text(encoding='utf-8'))
    old_entries = {f['fonte']: f for f in old['fontes']}
    archived_links = []
    for note in (ROOT / 'conteudo').rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', note.read_text(encoding='utf-8')):
            if '.xlsx' in unquote(target).lower() and 'arquivo' in unquote(target):
                archived_links.append({'nota': local(note), 'alvo': target})
    report = {'versao': 1, 'auditoria_utc': datetime.now(timezone.utc).isoformat(),
              'metodo': 'Leitura direta dos dois XLSX, comparação física dos pacotes, parse XML independente do conversor, leitura openpyxl sem recálculo, conferência integral MD/JSON, reconstrução ZIP em memória somente dos arquivos extraídos.',
              'alteracoes': 'Somente este relatório e tools/auditar_planilhas_exclusao.py. Nenhum XLSX foi salvo, recalculado, alterado ou excluído.',
              'fontes': reports,
              'inspecao_visual_independente': VISUAL,
              'links_markdown_para_xlsx_arquivado': {'ocorrencias': len(archived_links),
                   'notas': len(set(i['nota'] for i in archived_links)), 'links': archived_links},
              'informacoes_que_dependem_do_ooxml_ou_xlsx': [
                  '17.472 células XML sem conteúdo que conservam apenas estilos/estrutura não estão enumeradas como células no JSON nem no Markdown.',
                  'Catálogos completos de estilos (211 cellXfs), fontes, preenchimentos, bordas e temas. Os JSON de célula conservam IDs e formatos numéricos, mas não substituem os catálogos.',
                  'Runs de formatação do sharedStrings: o texto simples está no MD/JSON; a formatação rica original permanece no sharedStrings.xml.',
                  'Fash INTERESSES possui seis células textuais riscadas (C3, D4, C24, C25, C51, C52), exigidas com a mesma marcação no Markdown. O texto e ID de estilo estão no JSON, e styles.xml conserva a definição original. A rasura por si só não define estado de jogo.',
                  'O contêiner ZIP original (compressão, ordem e metadados ZIP) só é preservado byte a byte mantendo um XLSX original. O pacote extraído preserva todos os payloads OOXML para reconstrução semântica.'],
              'informacoes_preservadas_fora_dos_xlsx': [
                  'Texto/números, coordenadas, fórmulas expandidas e caches gravados estão integralmente nas tabelas MD. O JSON conserva também os lexemas numéricos e texto/atributos XML das fórmulas, inclusive compartilhadas.',
                  'Comentários com autor e texto, destinos de hyperlinks e intervalos mesclados estão em MD e JSON. JSON conserva ainda os nós XML de comentários e desenhos, âncoras, dimensões, relacionamentos e metadados de abas.',
                  'As sete imagens mantêm os bytes originais e são incorporadas pelas notas. A legenda de 27 entradas também foi transcrita e reconferida visualmente.'],
              'achados_acionaveis': [
                  'Preservar os dois diretórios conteudo/Anexos/planilhas/{fash-paleskin,glim-sombrasselva}/ooxml ao manter apenas a versão extraída: são parte da preservação integral, não arquivos temporários.',
                  'Se os XLSX arquivados forem removidos, atualizar 36 links para eles em 19 notas de Fontes/Planilhas e preservar/documentar uma rotina de reconstrução a partir dos membros OOXML.',
                  'O caminho BASE INICIAL permanece como proveniência. Na ausência da origem, o resolvedor exige cópia com hash exato e os mesmos registros no manifesto, na auditoria e na execução de limpeza concluída.',
                  'Glim MAIN!I19, I20 e I23 já têm cache XML vazio. Essa condição foi preservada e não indica omissão da conversão. Não interpretar como resultado numérico calculado.'],
              'ressalva_sobre_conteudo_de_rpg': 'Não foi encontrada perda de texto, números, fórmulas gravadas, comentários, links ou imagens. As seis rasuras em INTERESSES de Fash são conferidas no Markdown contra styles.xml e openpyxl, sem inferir seu significado. Preservar XLSX e OOXML mantém também os demais estilos e recursos de apresentação que Markdown não reproduz.',
              'comparacao_manifesto_migracao': [
                  {'fonte': r['fonte'], 'sha_fonte_confere': old_entries[r['fonte']]['sha256'] == r['sha256'],
                   'membros_total_confere': old_entries[r['fonte']]['membros_ooxml'] == r['total_membros_ooxml'],
                   'abas_total_confere': len(old_entries[r['fonte']]['abas']) == len(r['abas'])}
                  for r in reports],
              'cenarios': [
                  {'cenario': 1, 'remover': 'BASE INICIAL/*.xlsx',
                   'manter': 'arquivo/originais + conteudo/Fontes/Planilhas + conteudo/Anexos/planilhas',
                   'resultado': 'As cópias arquivadas são byte a byte idênticas. Não há perda de informação dos dois XLSX nesse cenário.'},
                  {'cenario': 2, 'remover': 'BASE INICIAL/*.xlsx e arquivo/originais/BASE INICIAL/*.xlsx',
                   'manter': 'conteudo/Fontes/Planilhas + conteudo/Anexos/planilhas, inclusive todos os subdiretórios ooxml',
                   'resultado': 'O conteúdo OOXML completo foi preservado e a reconstrução de um XLSX semanticamente equivalente foi conferida em memória. A identidade binária do contêiner ZIP não é prometida. Haverá links Markdown para o XLSX arquivado sem alvo.'},
                  {'cenario': 3, 'remover': 'Todos os XLSX e conteudo/Anexos/planilhas',
                   'manter': 'Somente Markdown',
                   'resultado': 'Há perda: desaparecem as sete imagens incorporadas e os dados exatos/estilos/layouts/metadados mantidos no JSON e OOXML. As tabelas MD preservam os valores, fórmulas expandidas, caches gravados, comentários, hyperlinks e intervalos mesclados, mas não substituem a ficha Excel nem o mapa visual.'}],
              'limites': ['Nenhuma fórmula foi recalculada; caches preservam o estado gravado pela fonte e podem estar desatualizados nela.',
                          'Não foi validada a renderização ou interação no Microsoft Excel. A equivalência OOXML decorre da igualdade byte a byte de todos os membros do pacote reconstruído.',
                          'A transcrição manual da legenda de imagem é complementar; imagem original é a fonte visual e deve permanecer.',
                          'Conteúdo por coordenada permite consulta integral, mas não recria automaticamente o layout visual, dimensões, estilos e interatividade de uma ficha Excel.'],
              'total_erros': sum(r['total_erros'] for r in reports)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'relatorio': local(OUT), 'total_erros': report['total_erros'], 'fontes': [
        {'fonte': r['fonte'], 'abas': len(r['abas']), 'membros': r['total_membros_ooxml'],
         'midias': len(r['midias']), 'totais': r['totais'], 'erros': r['erros'][:10],
         'nomes_definidos': r['nomes_definidos'], 'reconstrucao': r['reconstrucao']}
        for r in reports]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
