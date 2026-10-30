"""Extrai integralmente as duas fontes XLSX para Markdown, sem regravar XLSX.

Requer somente a biblioteca padrão e openpyxl do runtime bundled. Cada membro
OOXML é copiado byte a byte; as notas apresentam todos os valores/formulas,
comentários, links, mesclagens e objetos. Execute da raiz do repositório.
"""
from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import warnings
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, date, time
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

import openpyxl
from openpyxl.formula.translate import Translator
from openpyxl.styles.numbers import BUILTIN_FORMATS
from openpyxl.utils.cell import coordinate_to_tuple, get_column_letter

from fontes_migracao import SourceResolver, require_regeneration_opt_in


ROOT = Path(__file__).resolve().parents[1]
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "v": "urn:schemas-microsoft-com:vml",
    "x": "urn:schemas-microsoft-com:office:excel",
}
CONFIG = [
    ("FASH PALESKIN.xlsx", "Fash Paleskin", "fash", "fash-paleskin"),
    ("GLIM SOMBRASSELVA.xlsx", "Glim Sombrasselva", "glim", "glim-sombrasselva"),
]
OUT_NOTES = ROOT / "conteudo/Fontes/Planilhas"
OUT_ATTACH = ROOT / "conteudo/Anexos/planilhas"
MIDIAS_INSPECIONADAS = {
    "f181909826a2ded3f887655fee9549bffbe3046e6fcb5ced034a42776e276c94",
    "24b901054c5ad918356263392eb076e3e415cfe3a152f29078fe25ce0f555667",
    "27824fe664f14699891c5b442bba5499097fbe4d65f4295e58fd0999bc9ba25a",
    "e606deb3e707ff064a9088bd241997dd7266e9fa389cc364e74e51d9540e716c",
    "74f0e2db455ccf33d42d1168f4970c0077d6bc257fffca76460ab5327bde8d05",
    "337b7b12bc804c00f6a4972f1e7e2f24d11b9e4a8f5edc668365a567531fb25e",
    "e65dc0dc7770795b770367e1b835db9cd8332a60f61beb8953f302e176e66d15",
}
LEGENDA_FASH = """H19 - EQUICEP
J25 - RUÍNA 3
K18 - VILA DOS GNOMOS - KRANKLEFANG LUNHOLLOW
L28 - VILA DOS FURION - LORAETH
M13 - VILA DAS FADAS ESPINHO - THORNAEVA
M22 - EM DIREÇÃO AO P22 - CRIATURA COM SÍMBOLO DA BRUXA
O20 - SAÍDA SUBTERRÂNEO - CRIAS DRACÔNICAS
O24 - PANTERA ESPECTRAL
P22 - CIDADE DROW
P25 - NYTH (PARECIDO COM FOGO-FÁTUO)
Q23 - O FORTE - VYTHARIX THRODENAAR
Q27 - RUÍNA 1
Q31 - POVO LAGARTO
R20 - VILA DAS FADAS - THAEL`VOREN
R27 - PERITON (ÁGUIA COM CABEÇA DE CERVO)
S18 - VILA MURGUL
T23 - CONCLAVE DA RAIZ ANCESTRAL
U27 - VILA DOS MEIO-DRAGÕES - DARASTRIX VURIX
Y31 - BOCARRA
X12 - VILA DOS CENTAUROS - VAEL`THARION
W23 - RUÍNA 2
AC10- VILA DAS DRÍADES - SYLTHA VAELOR
AC34 - ÁRVORE NEGRA
AD17 - CRIATURAS HÍBRIDAS GORILA/ARANHA
AN10 - PTERAPOVO
AN23 - FAROL
AP29 - CRIATURA PELUDA/FORTE DO OLHO VERDE"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rel_link(source: Path, target: Path) -> str:
    return quote(posixpath.relpath(target.as_posix(), source.parent.as_posix()), safe="/.-_")


def write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.write_bytes(data)


def save_json(path: Path, data) -> None:
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def q(name: str) -> str:
    prefix, tag = name.split(":", 1)
    return "{" + NS[prefix] + "}" + tag


def tree(node: ET.Element | None):
    if node is None:
        return None
    return {"tag": node.tag, "atributos": dict(node.attrib), "texto": node.text,
            "filhos": [tree(child) for child in node]}


def text_runs(node: ET.Element | None) -> str:
    """Texto de t/r na ordem original, sem duplicar anotações fonéticas rPh."""
    if node is None:
        return ""
    result = []
    for child in node:
        if child.tag == q("s:t"):
            result.append(child.text or "")
        elif child.tag == q("s:r"):
            result.extend(t.text or "" for t in child.findall("s:t", NS))
    return "".join(result)


def esc(value) -> str:
    if value is None:
        return "∅"
    return html.escape(str(value), quote=False).replace("|", "&#124;").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def code(value) -> str:
    return "<code>" + esc(value) + "</code>"


def yaml_head(title: str, campaign: str, origin: str, aliases: list[str]) -> list[str]:
    dump = lambda value: json.dumps(value, ensure_ascii=False)
    return ["---", "tipo: fonte", "titulo: " + dump(title),
            "campanhas: [" + campaign + "]", "publico: true", "status: importado",
            "origens:", "  - " + dump(origin), "aliases: " + dump(aliases), "---", "", "# " + title, ""]


def relationships(z: ZipFile, owner: str) -> dict:
    part = posixpath.join(posixpath.dirname(owner), "_rels", posixpath.basename(owner) + ".rels")
    if part not in z.namelist():
        return {}
    result = {}
    for r in ET.fromstring(z.read(part)):
        attrs = dict(r.attrib)
        attrs["parte_relacionamento"] = part
        if attrs.get("TargetMode") != "External":
            attrs["parte_destino"] = posixpath.normpath(posixpath.join(posixpath.dirname(owner), attrs["Target"])).lstrip("/")
        result[attrs["Id"]] = attrs
    return result


def number_formats(z: ZipFile) -> list[str]:
    node = ET.fromstring(z.read("xl/styles.xml"))
    custom = {int(x.get("numFmtId")): x.get("formatCode") for x in node.findall("s:numFmts/s:numFmt", NS)}
    return [custom.get(int(x.get("numFmtId", 0)), BUILTIN_FORMATS.get(int(x.get("numFmtId", 0)), "formato desconhecido"))
            for x in node.findall("s:cellXfs/s:xf", NS)]


def decode_value(cell_type: str, raw: str | None, strings: list[str], inline=None):
    if cell_type == "s" and raw is not None:
        return strings[int(raw)]
    if cell_type == "inlineStr":
        return text_runs(inline)
    if raw is None:
        return None
    if cell_type == "b":
        return raw == "1"
    if cell_type in ("str", "e", "d"):
        return raw
    # O número lexical original permanece em valor_xml, sem arredondamento.
    try:
        return int(raw) if re.fullmatch(r"[+-]?\d+", raw) else float(raw)
    except ValueError:
        return raw


def extract_comments(z, rels):
    comments = []
    for rel in rels.values():
        if rel["Type"].endswith("/comments"):
            part = rel["parte_destino"]
            node = ET.fromstring(z.read(part))
            authors = [x.text or "" for x in node.findall("s:authors/s:author", NS)]
            for c in node.findall("s:commentList/s:comment", NS):
                author_id = int(c.get("authorId", 0))
                comments.append({"celula": c.get("ref"), "autor": authors[author_id] if author_id < len(authors) else None,
                                 "texto": text_runs(c.find("s:text", NS)), "atributos": dict(c.attrib),
                                 "parte": part, "xml_estruturado": tree(c)})
    return comments


def extract_drawings(z, rels):
    result, vml = [], []
    for rel in rels.values():
        typ = rel["Type"].split("/")[-1]
        if typ not in ("drawing", "vmlDrawing"):
            continue
        part = rel["parte_destino"]
        node = ET.fromstring(z.read(part))
        dr_rels = relationships(z, part)
        if typ == "vmlDrawing":
            for shape in node.findall(".//v:shape", NS):
                cd = shape.find("x:ClientData", NS)
                row = cd.findtext("x:Row", default=None, namespaces=NS) if cd is not None else None
                col = cd.findtext("x:Column", default=None, namespaces=NS) if cd is not None else None
                vml.append({"parte": part, "id": shape.get("id"), "tipo": cd.get("ObjectType") if cd is not None else None,
                            "celula": get_column_letter(int(col) + 1) + str(int(row) + 1) if row is not None and col is not None else None,
                            "estilo": shape.get("style"), "texto": "".join(shape.find("v:textbox", NS).itertext()) if shape.find("v:textbox", NS) is not None else "",
                            "ancora": cd.findtext("x:Anchor", default=None, namespaces=NS) if cd is not None else None,
                            "xml_estruturado": tree(shape)})
            continue
        for i, anchor in enumerate(node, 1):
            fr = anchor.find("xdr:from", NS)
            def integer_at(parent, field):
                val = parent.findtext("xdr:" + field, default=None, namespaces=NS) if parent is not None else None
                return int(val) if val is not None else None
            row, col = integer_at(fr, "row"), integer_at(fr, "col")
            prop = anchor.find(".//xdr:cNvPr", NS)
            blips = []
            for blip in anchor.findall(".//a:blip", NS):
                rid = blip.get(q("r:embed")) or blip.get(q("r:link"))
                blips.append({"relacao": rid, **dr_rels.get(rid, {})})
            result.append({"parte": part, "ordem": i, "tipo_ancora": anchor.tag.split("}")[-1],
                           "celula": get_column_letter(col + 1) + str(row + 1) if row is not None and col is not None else None,
                           "nome": prop.get("name") if prop is not None else None,
                           "titulo": prop.get("title") if prop is not None else None,
                           "descricao": prop.get("descr") if prop is not None else None,
                           "textos": [x.text or "" for x in anchor.findall(".//a:t", NS)],
                           "midias": blips, "relacionamentos": dr_rels,
                           "xml_estruturado": tree(anchor)})
    return result, vml


def displayed(value):
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if value == "":
        return '"" (texto vazio)'
    return value


def literal_reading(cell):
    if cell.get("leitura_formato"):
        return esc(cell["leitura_formato"]) + " (serial Excel " + code(cell["valor_xml"]) + "; formato " + code(cell["formato_numero"]) + ")"
    return esc(displayed(cell["valor"]))


def convert(filename, title, campaign, slug):
    require_regeneration_opt_in(ROOT)
    origin = "BASE INICIAL/" + filename
    source = SourceResolver(ROOT).resolve(origin)
    before = sha(source.read_bytes())
    annex = OUT_ATTACH / slug
    package = annex / "ooxml"
    index_path = OUT_NOTES / (title + ".md")
    original = ROOT / "arquivo/originais/BASE INICIAL" / filename
    assert original.exists() and sha(original.read_bytes()) == before, "Cópia arquivada ausente ou divergente"
    outputs = []
    def remember(path):
        outputs.append(path)
        return local(path)
    with ZipFile(source) as z:
        members = []
        for info in z.infolist():
            if info.is_dir():
                continue
            # Nenhum membro do arquivo pode escapar da pasta autorizada.
            dest = package.joinpath(*info.filename.split("/"))
            assert dest.resolve().is_relative_to(package.resolve())
            data = z.read(info.filename)
            write(dest, data)
            members.append({"parte": info.filename, "bytes": len(data), "sha256": sha(data), "saida": remember(dest)})
            assert sha(dest.read_bytes()) == sha(data)
        workbook_root = ET.fromstring(z.read("xl/workbook.xml"))
        wb_rels = relationships(z, "xl/workbook.xml")
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = [text_runs(x) for x in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        formats = number_formats(z)
        used_shared_strings = set()
        sheets = []
        sheet_content = []
        all_warnings = []
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            check_wb = openpyxl.load_workbook(source, read_only=True, data_only=False, keep_links=True)
            cache_wb = openpyxl.load_workbook(source, read_only=True, data_only=True, keep_links=True)
            for position, sheet_node in enumerate(workbook_root.findall("s:sheets/s:sheet", NS), 1):
                name = sheet_node.get("name")
                part = wb_rels[sheet_node.get(q("r:id"))]["parte_destino"]
                node = ET.fromstring(z.read(part))
                rels = relationships(z, part)
                filename_note = re.sub(r'[<>:"/\\|?*]', "-", title + " - " + name) + ".md"
                note = OUT_NOTES / filename_note
                exact_json = annex / ("aba-" + str(position).zfill(2) + ".json")
                cells, anchors = [], {}
                for row in node.findall("s:sheetData/s:row", NS):
                    for cell in row.findall("s:c", NS):
                        formula = cell.find("s:f", NS)
                        value = cell.find("s:v", NS)
                        inline = cell.find("s:is", NS)
                        if formula is None and value is None and inline is None:
                            continue
                        coord = cell.get("r")
                        typ = cell.get("t", "n")
                        raw = value.text if value is not None else None
                        if typ == "s" and raw is not None:
                            used_shared_strings.add(int(raw))
                        item = {"celula": coord, "atributos": dict(cell.attrib), "tipo_xml": typ,
                                "valor_xml_presente": value is not None, "valor_xml": raw,
                                "valor": decode_value(typ, raw, strings, inline),
                                "formato_numero": formats[int(cell.get("s", "0"))],
                                "formula": None}
                        if inline is not None:
                            item["inline_xml"] = tree(inline)
                        if formula is not None:
                            formula_text = formula.text or ""
                            attrs = dict(formula.attrib)
                            item["formula"] = {"texto_xml": formula_text, "atributos": attrs,
                                               "expandida": "=" + formula_text if formula_text else None}
                            if attrs.get("t") == "shared" and formula_text:
                                anchors[attrs["si"]] = (coord, "=" + formula_text)
                            item["cache"] = {"estado": "ausente" if value is None else "vazio_no_xml" if raw is None else "presente",
                                             "tipo_xml": typ, "valor_xml": raw, "valor": item["valor"]}
                        cells.append(item)
                for item in cells:
                    f = item["formula"]
                    if f and f["atributos"].get("t") == "shared" and f["expandida"] is None:
                        base_coord, base = anchors[f["atributos"]["si"]]
                        f["expandida"] = Translator(base, origin=base_coord).translate_formula(item["celula"])
                        f["ancora_compartilhada"] = base_coord
                cells.sort(key=lambda c: coordinate_to_tuple(c["celula"]))
                comments = extract_comments(z, rels)
                links = []
                for link in node.findall("s:hyperlinks/s:hyperlink", NS):
                    attrs = dict(link.attrib)
                    rid = attrs.get(q("r:id"))
                    links.append({"intervalo": link.get("ref"), "atributos": attrs, "relacionamento": rels.get(rid),
                                  "destino": rels.get(rid, {}).get("Target") or link.get("location")})
                drawings, vml = extract_drawings(z, rels)
                merges = [m.get("ref") for m in node.findall("s:mergeCells/s:mergeCell", NS)]
                metadata = [tree(c) for c in node if c.tag != q("s:sheetData")]
                content = {"fonte": origin, "sha256_fonte": before, "aba": name, "ordem": position,
                           "visibilidade": sheet_node.get("state", "visible"), "parte_xml": part,
                           "celulas": cells, "comentarios": comments, "hyperlinks": links,
                           "mesclagens": merges, "drawings": drawings, "objetos_vml": vml,
                           "relacionamentos": rels, "metadados_aba": metadata,
                           "atributos_linhas": [dict(r.attrib) for r in node.findall("s:sheetData/s:row", NS)],
                           "celulas_xml_total": len(node.findall("s:sheetData/s:row/s:c", NS)),
                           "limites": ["Fórmulas não foram recalculadas. Cache é o gravado na fonte.",
                                       "Markdown não reproduz posicionamento, estilos ou interatividade do Excel. XML e binário original preservam esses recursos.",
                                       "Texto e números lexicais exatos estão neste JSON e no pacote OOXML, inclusive espaços e quebras de linha."]}
                # Conferência independente: leitura openpyxl, sem salvar ou recalcular.
                ws = check_wb[name]
                cache_ws = cache_wb[name]
                read_cells = {c.coordinate: c for row in ws.iter_rows() for c in row if c.value is not None}
                raw_nonempty = {c["celula"] for c in cells if c["formula"] or c["valor"] is not None}
                formula_mismatches = [c["celula"] for c in cells if c["formula"] and
                                      (c["celula"] not in read_cells or read_cells[c["celula"]].value != c["formula"]["expandida"])]
                cache_cells = {c.coordinate: c for row in cache_ws.iter_rows() for c in row if c.value is not None}
                cache_mismatches = []
                literal_mismatches = []
                format_conversions = []
                for c in cells:
                    expected = c["valor"]
                    target = cache_cells.get(c["celula"]) if c["formula"] else read_cells.get(c["celula"])
                    actual = target.value if target is not None else None
                    # Leitores convertem números formatados como data/hora; XML lexical é a autoridade.
                    if actual != expected:
                        record = {"celula": c["celula"], "valor_xml": expected, "openpyxl": str(actual), "tipo_openpyxl": type(actual).__name__, "formato": c["formato_numero"]}
                        if isinstance(actual, (datetime, date, time)):
                            c["interpretacao_formato"] = {"valor_iso": actual.isoformat(), "tipo": type(actual).__name__}
                            c["leitura_formato"] = actual.strftime("%d/%m") if c["formato_numero"].lower() == "dd/mm" else actual.isoformat()
                            format_conversions.append(record)
                        else:
                            (cache_mismatches if c["formula"] else literal_mismatches).append(record)
                checks = {"celulas_na_leitura_openpyxl": len(read_cells),
                          "coordenadas_so_no_xml": sorted(raw_nonempty - set(read_cells)),
                          "coordenadas_so_no_openpyxl": sorted(set(read_cells) - raw_nonempty),
                          "formulas_divergentes": formula_mismatches,
                          "conversoes_por_formato_data_hora": format_conversions,
                          "valores_literais_convertidos_ou_divergentes": literal_mismatches,
                          "caches_convertidos_ou_divergentes": cache_mismatches}
                assert not formula_mismatches, (filename, name, formula_mismatches)
                assert not checks["coordenadas_so_no_openpyxl"], checks
                assert not literal_mismatches and not cache_mismatches, checks
                content["conferencias"] = checks
                if campaign == "fash" and name == "INTERESSES":
                    content["transcricoes_visuais"] = [{"parte": "xl/media/image1.png", "ancora": "I31", "metodo": "transcrição manual após inspeção da imagem original", "texto": LEGENDA_FASH}]
                save_json(exact_json, content)
                remember(exact_json)
                lines = yaml_head(title + " — " + name, campaign, origin, [title + " - " + name])
                lines += ["Índice: [[Fontes/Planilhas/" + title + "|" + title + "]].",
                          "Fonte: [" + filename + "](" + rel_link(note, original) + ").",
                          "", f"Aba {position}, nome original **{esc(name)}**, visibilidade `{content['visibilidade']}`.",
                          f"{len(cells)} células com conteúdo, {sum(c['formula'] is not None for c in cells)} fórmulas, {len(comments)} comentários e {len(links)} hyperlinks.", "",
                          "[Dados exatos por coordenada (JSON)](" + rel_link(note, exact_json) + ") · [XML original da aba](" + rel_link(note, package / part) + ").", "",
                          "## Conteúdo integral por coordenada", "",
                          "Ordem de leitura: linha e coluna originais. `∅` indica ausência de valor. Fórmulas compartilhadas aparecem expandidas para leitura; texto XML e atributos originais estão no JSON. Cache é o valor gravado, sem recálculo. Espaços, tipos e números lexicais estão no apêndice JSON. Células sem conteúdo que só definem estilo permanecem no XML.", "",
                          "| Célula | Valor literal | Fórmula | Valor em cache |", "| --- | --- | --- | --- |"]
                cells_with_strike = []
                for c in cells:
                    f = c["formula"]
                    cache = (esc(displayed(c["cache"]["valor"])) if c["cache"]["estado"] == "presente" else "∅ (" + c["cache"]["estado"].replace("_", " ") + ")") if f else "—"
                    literal = "—" if f else literal_reading(c)
                    if not f and ws[c["celula"]].font.strike:
                        literal = "~~" + literal + "~~"
                        cells_with_strike.append(c["celula"])
                    lines.append("| " + code(c["celula"]) + " | " + literal + " | " + (code(f["expandida"]) if f else "—") + " | " + cache + " |")
                if cells_with_strike:
                    lines += ["", "O texto riscado reproduz a marcação visual da fonte; uma rasura, por si só, não prova conclusão nem define o estado atual do assunto."]
                if not cells:
                    lines += ["", "A aba não tem células com conteúdo."]
                lines += ["", "## Comentários", ""]
                if comments:
                    for c in comments:
                        lines += ["### " + c["celula"] + " — " + (c["autor"] or "autor não informado"), "", esc(c["texto"]), ""]
                else:
                    lines += ["Nenhum comentário no arquivo.", ""]
                lines += ["## Hyperlinks", ""]
                if links:
                    lines += ["| Intervalo | Destino original | Atributos adicionais |", "| --- | --- | --- |"]
                    for link in links:
                        extras = {k: v for k, v in link["atributos"].items() if k not in ("ref", q("r:id"))}
                        target = link["destino"]
                        navigable = " [abrir](<" + quote(target, safe=":/?&=#%+@-._~!$,;*'") + ">)" if target and target.startswith(("http://", "https://", "mailto:")) else ""
                        lines.append("| " + code(link["intervalo"]) + " | " + esc(target) + navigable + " | " + code(json.dumps(extras, ensure_ascii=False)) + " |")
                else:
                    lines.append("Nenhum hyperlink no arquivo.")
                lines += ["", "## Mesclagens", ""]
                if merges:
                    lines += [f"{len(merges)} intervalos mesclados, na ordem do XML:", "", "```text", *merges, "```"]
                else:
                    lines.append("Nenhuma mesclagem no arquivo.")
                lines += ["", "## Imagens e outros objetos", ""]
                if drawings:
                    for d in drawings:
                        lines += ["### Objeto " + str(d["ordem"]) + (" — " + (d["nome"] or d["tipo_ancora"])), "",
                                  "Âncora: " + code(d["celula"]) + ". Tipo: " + code(d["tipo_ancora"]) + ". Offsets e dimensões exatos no JSON.", ""]
                        for key in ("titulo", "descricao"):
                            if d[key]:
                                lines += [key.capitalize() + ": " + esc(d[key]), ""]
                        for tx in d["textos"]:
                            lines += [esc(tx), ""]
                        for media in d["midias"]:
                            if "parte_destino" in media:
                                target = package / media["parte_destino"]
                                lines += ["![" + (d["nome"] or target.name) + "](" + rel_link(note, target) + ")", ""]
                            elif media.get("Target"):
                                lines += ["Mídia externa original: " + esc(media["Target"]), ""]
                else:
                    lines += ["Nenhum objeto DrawingML com conteúdo. Os arquivos de desenho vazios também estão preservados no pacote OOXML.", ""]
                if content.get("transcricoes_visuais"):
                    lines += ["### Transcrição visual da legenda incorporada", "",
                              "Texto da imagem `image1.png`, ancorada em `I31`. A imagem original acima permanece a referência. Grafias e coordenadas próprias da imagem foram mantidas, inclusive quando diferem das células.", "", "```text", LEGENDA_FASH, "```", ""]
                if vml:
                    lines += ["### Objetos VML", "", "As caixas de comentário preservam os seguintes vínculos e âncoras. O texto dos comentários está acima.", "",
                              "| ID | Tipo | Célula | Visibilidade/estilo | Âncora original | Texto VML |", "| --- | --- | --- | --- | --- | --- |"]
                    for obj in vml:
                        lines.append("| " + " | ".join(esc(obj.get(k)) for k in ("id", "tipo", "celula", "estilo", "ancora", "texto")) + " |")
                lines += ["", "## Estrutura e preservação", "",
                          "As dimensões de linhas/colunas, linhas/colunas ocultas, filtros, validações, formatação condicional, configurações de impressão, relações e demais metadados permanecem no [JSON da aba](" + rel_link(note, exact_json) + ") e no [XML original](" + rel_link(note, package / part) + ").", "",
                          "Markdown apresenta texto e dados, sem reproduzir o posicionamento visual e a interatividade do Excel. O [XLSX original](" + rel_link(note, original) + ") acompanha a conversão para esses recursos.", ""]
                write(note, "\n".join(lines))
                remember(note)
                # Todos os registros de célula precisam aparecer na apresentação Markdown.
                rendered = note.read_text(encoding="utf-8")
                assert all("| " + code(c["celula"]) + " |" in rendered for c in cells)
                content_section = rendered.split("## Conteúdo integral por coordenada", 1)[1].split("## Comentários", 1)[0]
                assert len(re.findall(r"^\| <code>[A-Z]+\d+</code> \|", content_section, re.M)) == len(cells)
                assert all("### " + c["celula"] + " — " in rendered and esc(c["texto"]) in rendered for c in comments)
                assert all("| " + code(link["intervalo"]) + " | " + esc(link["destino"]) in rendered for link in links)
                assert all(merge in rendered for merge in merges)
                assert all(esc(obj["id"]) in rendered for obj in vml)
                metrics = {"nome": name, "ordem": position, "visibilidade": content["visibilidade"], "parte_xml": part,
                           "celulas_xml": content["celulas_xml_total"], "celulas_com_conteudo": len(cells),
                           "formulas": sum(c["formula"] is not None for c in cells),
                           "formulas_compartilhadas": sum(bool(c["formula"] and c["formula"]["atributos"].get("t") == "shared") for c in cells),
                           "cache_formulas": dict(Counter(c["cache"]["estado"] for c in cells if c["formula"])),
                           "comentarios": len(comments), "hyperlinks": len(links), "mesclagens": len(merges),
                           "objetos_drawingml": len(drawings), "objetos_vml": len(vml),
                           "cobertura_markdown": {"celulas": len(cells), "comentarios": len(comments), "hyperlinks": len(links), "mesclagens": len(merges), "objetos_vml": len(vml)},
                           "saida_markdown": local(note), "dados_json": local(exact_json), "conferencias": checks}
                sheets.append(metrics)
                sheet_content.append(content)
            check_wb.close()
            cache_wb.close()
            all_warnings = [str(w.message) for w in warning_list]
        media = []
        for member in members:
            if member["parte"].startswith("xl/media/"):
                item = dict(member)
                try:
                    from PIL import Image
                    with Image.open(package / member["parte"]) as im:
                        item.update({"formato": im.format, "largura": im.width, "altura": im.height, "modo": im.mode})
                except Exception as exc:
                    item["erro_inspecao"] = str(exc)
                item["usos"] = [{"aba": c["aba"], "celula": d["celula"], "nome_objeto": d["nome"]}
                                 for c in sheet_content for d in c["drawings"] for b in d["midias"] if b.get("parte_destino") == member["parte"]]
                if item["sha256"] in MIDIAS_INSPECIONADAS:
                    item["inspecao_visual"] = {"data": "2026-10-29", "metodo": "view_image da mídia original extraída, sem transformação",
                                              "resultado": "Imagem legível, preservada sem redimensionamento; âncora conferida no DrawingML."}
                media.append(item)
        package_manifest = annex / "pacote.json"
        unused_strings = [{"indice": i, "texto": s} for i, s in enumerate(strings) if i not in used_shared_strings]
        package_data = {"fonte": origin, "sha256_fonte": before, "membros": members,
                        "metadados_workbook": tree(workbook_root), "relacionamentos_workbook": wb_rels, "midias": media,
                        "abas": sheets, "strings_compartilhadas_sem_uso_em_celulas": unused_strings, "avisos_leitor_openpyxl": all_warnings}
        save_json(package_manifest, package_data)
        remember(package_manifest)
        lines = yaml_head(title + " — planilha original", campaign, origin, [filename, title + " (planilha)"])
        lines += ["Fonte integral da ficha e das tabelas associadas a [[Personagens/" + title + "|" + title + "]]. Os nomes, grafias e valores foram preservados.", "",
                  "[XLSX original arquivado](" + rel_link(index_path, original) + ") · [Inventário exato do pacote OOXML](" + rel_link(index_path, package_manifest) + ").", "",
                  "## Abas", "", "Todas as abas estão listadas na ordem do arquivo, inclusive qualquer aba oculta.", "",
                  "| Ordem | Aba | Estado | Células com conteúdo | Fórmulas | Comentários | Hyperlinks |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for s in sheets:
            wiki = s["saida_markdown"].removeprefix("conteudo/").removesuffix(".md")
            lines.append("| " + str(s["ordem"]) + " | [[" + wiki + "\\|" + s["nome"] + "]] | " + s["visibilidade"] + " | " + str(s["celulas_com_conteudo"]) + " | " + str(s["formulas"]) + " | " + str(s["comentarios"]) + " | " + str(s["hyperlinks"]) + " |")
        totals = {k: sum(s[k] for s in sheets) for k in ("celulas_com_conteudo", "formulas", "comentarios", "hyperlinks", "mesclagens", "objetos_drawingml", "objetos_vml")}
        lines += ["", "## Preservação", "",
                  f"A extração cobre {len(sheets)} abas, {totals['celulas_com_conteudo']} células com conteúdo, {totals['formulas']} fórmulas e {len(media)} arquivos de imagem. Cada nota conserva valores literais, fórmulas e cache separadamente, com comentários, hyperlinks, mesclagens e objetos.", "",
                  "O apêndice JSON de cada aba preserva coordenadas, tipos, números lexicais, texto de fórmulas compartilhadas, âncoras e metadados. Todos os membros do pacote OOXML foram extraídos byte a byte, com SHA-256 individual. A conferência usa uma segunda leitura com openpyxl e verifica a presença de todas as coordenadas na nota.", "",
                  "Fórmulas não foram recalculadas. Um cache vazio/ausente permanece identificado; resultados em cache podem estar desatualizados na própria fonte. Markdown não reproduz todos os estilos, dimensões, posicionamentos e recursos interativos do Excel; o binário original e o pacote OOXML preservam esses detalhes.", "",
                  "## Imagens incorporadas", "", "| Arquivo | Dimensões | Aba e âncora |", "| --- | --- | --- |"]
        for m in media:
            lines.append("| [" + posixpath.basename(m["parte"]) + "](" + rel_link(index_path, ROOT / m["saida"]) + ") | " + str(m.get("largura")) + " × " + str(m.get("altura")) + " | " + "; ".join(u["aba"] + "!" + str(u["celula"]) for u in m["usos"]) + " |")
        lines += ["", "## Textos auxiliares sem referência de célula", "",
                  "O catálogo de strings compartilhadas também foi conferido. Entradas sem referência em células são preservadas abaixo como material auxiliar do arquivo, sem atribuir uso ou posição que a fonte não informa.", ""]
        if unused_strings:
            lines += ["| Índice no catálogo original | Texto integral |", "| --- | --- |"]
            lines.extend("| " + str(s["indice"]) + " | " + esc(displayed(s["texto"])) + " |" for s in unused_strings)
        else:
            lines.append("Não há entradas sem referência de célula no catálogo.")
        lines += ["", "SHA-256 da fonte: " + code(before) + ".", ""]
        write(index_path, "\n".join(lines))
        remember(index_path)
    assert sha(source.read_bytes()) == before
    return {"fonte": origin, "bytes": source.stat().st_size, "sha256": before,
            "indice": local(index_path), "abas": sheets, "totais": totals, "midias": media,
            "abas_por_visibilidade": dict(Counter(s["visibilidade"] for s in sheets)),
            "membros_ooxml": len(members), "strings_compartilhadas_sem_uso": len(unused_strings), "objetos_embutidos": [m for m in members if "/embeddings/" in m["parte"]],
            "conferencias": {"fonte_inalterada": True, "copia_arquivada_identica": True, "membros_extraidos_identicos": len(members),
                             "todas_abas_exportadas": len(sheets) == len(workbook_root.findall("s:sheets/s:sheet", NS)),
                             "todas_coordenadas_em_markdown": True, "formulas_conferidas_openpyxl": True,
                             "avisos_openpyxl": all_warnings},
            "saidas": [{"caminho": local(p), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in outputs]}


def main():
    results = [convert(*cfg) for cfg in CONFIG]
    manifest = {"versao": 1, "data_migracao": "2026-10-29", "formato": "XLSX → Markdown UTF-8 + JSON + pacote OOXML exato",
                "script": {"caminho": local(Path(__file__)), "sha256": sha(Path(__file__).read_bytes())},
                "fontes": results,
                "limites": ["Os valores em cache são exclusivamente os gravados no XLSX. Nenhuma fórmula foi recalculada.",
                            "Markdown não reproduz posicionamento, estilos e interatividade. Os binários originais são arquivados separadamente e o pacote OOXML está integralmente extraído.",
                            "A leitura openpyxl serve de conferência independente. A autoridade sobre números lexicais e fórmulas compartilhadas é o OOXML preservado."]}
    path = ROOT / "docs/migracao/planilhas.json"
    save_json(path, manifest)
    print(json.dumps({"manifesto": local(path), "fontes": [{"arquivo": r["fonte"], "abas": len(r["abas"]), **r["totais"], "midias": len(r["midias"]), "saidas": len(r["saidas"])} for r in results]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
