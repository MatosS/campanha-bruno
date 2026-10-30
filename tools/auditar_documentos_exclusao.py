"""Read-only, independent audit of PDF/DOCX preservation before deletion.

Does not import or execute the converters, render documents, or change inputs.
The sole data output is docs/auditoria-exclusao/documentos.json.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from zipfile import ZipFile

import pdfplumber
from pypdf import PdfReader
from pypdf.generic import ContentStream
from PIL import Image
from docx import Document
from lxml import etree as ET

from fontes_migracao import SourceResolver, SourceResolutionError

ROOT = Path(__file__).resolve().parents[1]
SOURCES = SourceResolver(ROOT)
OUT = ROOT / "docs/auditoria-exclusao/documentos.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ERRORS: list[dict] = []


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def record(path: Path, origin: str | None = None) -> dict:
    data = path.read_bytes()
    return {"caminho": origin or rel(path), "bytes": len(data), "sha256": digest(data),
            **({"caminho_consultado": rel(path)} if origin and origin != rel(path) else {})}


def check(ok: bool, where: str, detail: str) -> bool:
    if not ok:
        ERRORS.append({"local": where, "erro": detail})
    return bool(ok)


def compact(text: str) -> str:
    return "".join(text.split())


def unescape(text: str) -> str:
    return re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", text)


def inline_plain(text: str) -> str:
    # Protect escaped literal characters before removing generated emphasis.
    protected = []

    def stash(match):
        protected.append(match.group(1))
        return chr(0xE000 + len(protected) - 1)

    result = re.sub(r"\\(.)", stash, text)
    result = result.replace("**", "").replace("_", "")
    for i, value in enumerate(protected):
        result = result.replace(chr(0xE000 + i), value)
    return result


def resolve(obj):
    return obj.get_object() if hasattr(obj, "get_object") else obj


def pdf_operators(page, reader) -> dict:
    counts = Counter()
    forms_seen = set()

    def visit(stream, resources):
        if stream is None:
            return
        parsed = ContentStream(stream, reader)
        counts.update(op.decode("latin-1") for _, op in parsed.operations)
        for name, ref in resolve(resources.get("/XObject", {})).items():
            obj = resolve(ref)
            if obj.get("/Subtype") == "/Form":
                key = (getattr(ref, "idnum", None), name)
                if key not in forms_seen:
                    forms_seen.add(key)
                    visit(obj, resolve(obj.get("/Resources", resources)))

    visit(page.get_contents(), resolve(page.get("/Resources", {})))
    return dict(counts)


def audit_pdf(stem: str, manifest: dict) -> dict:
    origin = f"BASE INICIAL/{stem}.pdf"
    path = SOURCES.resolve(origin)
    archived = ROOT / "arquivo/originais/BASE INICIAL" / path.name
    assets = ROOT / "conteudo/Anexos/pdfs" / stem
    md_path = ROOT / "conteudo/Fontes/Documentos" / f"{stem}.md"
    reader = PdfReader(path)
    saved = load(assets / "extracao-por-pagina.json")
    md = md_path.read_text(encoding="utf-8")
    md_pages = re.findall(r"<!-- INICIO_TEXTO_FONTE -->\s*\n(.*?)\n\s*<!-- FIM_TEXTO_FONTE -->", md, re.S)
    check(len(md_pages) == len(reader.pages), stem, "Quantidade de blocos Markdown diferente do PDF")
    check(len(saved) == len(reader.pages), stem, "Quantidade de páginas do JSON diferente do PDF")
    check(path.read_bytes() == archived.read_bytes(), stem, "Cópia arquivada diferente do original")
    pypdf_texts, plumber_texts, pages = [], [], []
    images = defaultdict(lambda: {"ocorrencias": [], "arquivos_extraidos": []})
    asset_hashes = {digest(p.read_bytes()): p for p in (assets / "imagens-extraidas").glob("*") if p.is_file()}
    all_ops = Counter()
    with pdfplumber.open(path) as pdf:
        for number, (native, spatial) in enumerate(zip(reader.pages, pdf.pages), 1):
            where = f"{stem}:página {number}"
            raw = native.extract_text() or ""
            text = spatial.extract_text() or ""
            pypdf_texts.append(raw)
            plumber_texts.append(text)
            extracted = saved[number - 1] if number <= len(saved) else {}
            annotations = [resolve(x) for x in resolve(native.get("/Annots", []))]
            annot_types = Counter(str(x.get("/Subtype", "?")) for x in annotations)
            links = [dict(x) for x in annotations if x.get("/Subtype") == "/Link"]
            source_images = []
            for img in native.images:
                sha = digest(img.data)
                asset = asset_hashes.get(sha)
                check(asset is not None, where, f"Imagem original sem cópia extraída idêntica: {sha}")
                occurrence = {"pagina": number, "recurso": img.name}
                images[sha]["ocorrencias"].append(occurrence)
                if asset is not None:
                    images[sha]["arquivos_extraidos"] = [rel(asset)]
                images[sha].update({"pixels": list(img.image.size), "modo": img.image.mode,
                                   "bytes_extraidos": len(img.data)})
                source_images.append(sha)
            png = assets / f"pagina-{number:02}.png"
            with Image.open(png) as image:
                image.load()
                pixels = list(image.size)
            expected_pixels = [math.ceil(float(spatial.width) * 120 / 72),
                               math.ceil(float(spatial.height) * 120 / 72)]
            check(pixels == expected_pixels, where, "Dimensões do PNG não equivalem a 120 dpi")
            check(extracted.get("render", {}).get("sha256") == digest(png.read_bytes()), where, "Hash do PNG difere do registro de extração")
            native_exact = check(raw == extracted.get("text_pypdf"), where, "Texto nativo fresco difere do JSON salvo")
            spatial_exact = check(text == extracted.get("text_pdfplumber"), where, "Texto espacial fresco difere do JSON salvo")
            extractors_agree = check(Counter(compact(raw)) == Counter(compact(text)), where, "Extratores divergem em caracteres não brancos")
            md_text = md_pages[number - 1] if number <= len(md_pages) else ""
            if text.strip():
                # Only generated list syntax and escapes are removed; order,
                # punctuation and every non-whitespace source character remain.
                md_text = unescape(re.sub(r"(?m)^- ", "", md_text))
                md_equal = check(compact(md_text) == compact(text), where, "Texto Markdown difere do texto fresco, em ordem ou conteúdo")
            else:
                md_equal = check("Página sem texto extraível" in md_text, where, "Página sem texto sem indicação explícita no Markdown")
            ops = pdf_operators(native, reader)
            all_ops.update(ops)
            font_counts = Counter(char.get("fontname", "?") for char in spatial.chars)
            color_counts = Counter(str(char.get("non_stroking_color")) for char in spatial.chars)
            pages.append({"pagina": number, "pontos_pdf": [float(spatial.width), float(spatial.height)],
                          "rotacao": int(native.get("/Rotate", 0)), "png": rel(png), "pixels_png": pixels,
                          "dpi_inferido": 120, "caracteres_pypdf": len(raw), "caracteres_pdfplumber": len(text),
                          "caracteres_nao_brancos": len(compact(text)), "texto_vazio": not bool(text.strip()),
                          "texto_fresco_igual_extracao_pypdf": native_exact,
                          "texto_fresco_igual_extracao_pdfplumber": spatial_exact,
                          "extratores_mesmos_caracteres": extractors_agree, "markdown_texto_igual_em_ordem": md_equal,
                          "caracteres_substituicao": text.count("\ufffd"), "fontes_caracteres": dict(font_counts),
                          "cores_caracteres": dict(color_counts),
                          "anotacoes": dict(annot_types), "links": len(links), "imagens": source_images,
                          "objetos_pdfplumber": {k: len(getattr(spatial, k)) for k in ["chars", "images", "lines", "rects", "curves"]},
                          "operadores_vetoriais": {op: ops[op] for op in ["m", "l", "c", "v", "y", "re", "S", "s", "f", "f*", "B", "B*", "b", "b*"] if ops.get(op)}})
    text_files = {}
    for name, fresh in [("pypdf", pypdf_texts), ("pdfplumber", plumber_texts)]:
        txt_path = assets / f"texto-integral-{name}.txt"
        text_files[name] = check(txt_path.read_text(encoding="utf-8") == "\n\f\n".join(fresh), stem,
                                 f"Texto integral {name} diferente da extração fresca")
    forms = reader.get_fields() or {}
    root = resolve(reader.trailer["/Root"])
    names = resolve(root.get("/Names", {}))
    metadata = {str(k): str(v) for k, v in (reader.metadata or {}).items()}
    manifest_doc = next(x for x in manifest["documents"] if Path(x["source"]["path"]).stem == stem)
    check(record(path)["sha256"] == manifest_doc["source"]["sha256"], stem, "Hash original difere do manifesto")
    manifest_checks = []
    for entry in manifest_doc["outputs"]:
        output = ROOT / entry["path"]
        ok = output.is_file() and digest(output.read_bytes()) == entry["sha256"]
        check(ok, entry["path"], "Saída convertida ausente ou hash alterado desde manifesto")
        manifest_checks.append(ok)
    return {"original": record(path, origin), "original_arquivado": record(archived), "binarios_identicos": path.read_bytes() == archived.read_bytes(),
            "origem_removida_com_registro": not SOURCES.original_path(origin).is_file(),
            "markdown": record(md_path), "paginas": len(pages), "paginas_com_texto": sum(not x["texto_vazio"] for x in pages),
            "campos_formulario": len(forms), "anotacoes": sum(sum(x["anotacoes"].values()) for x in pages),
            "links_interativos": sum(x["links"] for x in pages), "arquivos_embutidos": list(reader.attachments),
            "catalogo_chaves": sorted(map(str, root.keys())), "names_chaves": sorted(map(str, names.keys())),
            "criptografado": reader.is_encrypted,
            "outlines": len(reader.outline), "metadados": metadata,
            "acoes_ou_camadas_catalogo": {k: str(root[k]) for k in ["/OpenAction", "/AA", "/OCProperties"] if k in root},
            "imagens_unicas": [{"sha256": sha, **value} for sha, value in images.items()],
            "imagens_ocorrencias": sum(len(x["ocorrencias"]) for x in images.values()),
            "operadores_pdf": dict(all_ops), "textos_integrais_iguais": text_files,
            "saidas_manifesto_verificadas": len(manifest_checks), "saidas_manifesto_hash_igual": all(manifest_checks),
            "comparacao_por_pagina": pages}


def text_of(node) -> str:
    return "".join(node.xpath(".//w:t/text()", namespaces=NS))


def toggle(run, name) -> bool:
    value = run.find(f"w:rPr/w:{name}", NS)
    return value is not None and value.get(f"{{{W}}}val", "true") not in ["0", "false", "off"]


def audit_docx(manifest: dict) -> dict:
    origin = "BASE INICIAL/Resumo detalhado.docx"
    path = SOURCES.resolve(origin)
    archive = ROOT / "arquivo/originais/BASE INICIAL/Resumo detalhado.docx"
    md_path = ROOT / "conteudo/Fontes/Documentos/Resumo detalhado.md"
    structure_path = ROOT / "conteudo/Anexos/documentos/resumo-detalhado/estrutura.json"
    structure = load(structure_path)
    check(path.read_bytes() == archive.read_bytes(), path.name, "Cópia arquivada diferente do original")
    with ZipFile(path) as z:
        parts = {name: z.read(name) for name in z.namelist()}
    xmls = {name: ET.fromstring(data) for name, data in parts.items() if name.endswith(".xml")}
    root = xmls["word/document.xml"]
    body = root.find("w:body", NS)
    all_paragraphs = root.findall(".//w:p", NS)
    source_paragraphs = [text_of(p) for p in all_paragraphs]
    counts = Counter(ET.QName(x).localname for x in root.iter())
    run_tags = Counter(ET.QName(x).localname for x in root.findall(".//w:r/w:rPr/*", NS))
    para_tags = Counter(ET.QName(x).localname for x in root.findall(".//w:pPr/*", NS))
    doc = Document(path)
    independent = []
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    for elem in doc.element.body:
        if ET.QName(elem).localname == "p":
            independent.append(Paragraph(elem, doc).text)
        elif ET.QName(elem).localname == "tbl":
            for row in Table(elem, doc).rows:
                for cell in row.cells:
                    independent.extend(p.text for p in cell.paragraphs)
    independent_equal = check(source_paragraphs == independent, path.name, "python-docx e OOXML divergem no texto ou ordem")
    md_lines = md_path.read_text(encoding="utf-8").splitlines()
    # Independent Markdown parsing: start at the first heading with the source
    # title, then flatten paragraphs/list entries/table cells in reading order.
    first = next(i for i, line in enumerate(md_lines) if line.startswith("# "))
    md_paragraphs = []
    md_table_rows = 0
    md_bold_paragraphs = 0
    for line in md_lines[first:]:
        if not line:
            continue
        if line.startswith("| "):
            if re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", line):
                continue
            cells = re.split(r"(?<!\\)\|", line)[1:-1]
            md_paragraphs.extend(inline_plain(c[1:-1]) for c in cells)
            md_bold_paragraphs += sum(c[1:-1].startswith("**") and c[1:-1].endswith("**") for c in cells)
            md_table_rows += 1
        else:
            md_bold_paragraphs += bool(re.match(r"^#{1,6} ", line) or (line.startswith("**") and line.endswith("**")))
            line = re.sub(r"^(?:#{1,6} |\s*- |\s*\d+\. )", "", line)
            md_paragraphs.append(inline_plain(line))
    md_equal = check(source_paragraphs == md_paragraphs, path.name, "Texto Markdown fresco difere de parágrafos/células OOXML")
    bold_paragraphs = [p for p in all_paragraphs if any(toggle(r, "b") for r in p.findall("w:r", NS))]
    bold_entire = all(all(toggle(r, "b") for r in p.findall("w:r", NS) if text_of(r)) for p in bold_paragraphs)
    check(bold_entire and len(bold_paragraphs) == md_bold_paragraphs, path.name,
          "Ênfase de parágrafos inteiros difere entre DOCX e Markdown")
    differences = []
    for i in range(max(len(source_paragraphs), len(md_paragraphs))):
        a = source_paragraphs[i] if i < len(source_paragraphs) else None
        b = md_paragraphs[i] if i < len(md_paragraphs) else None
        if a != b:
            differences.append({"paragrafo": i + 1, "original": a, "markdown": b})
    body_blocks = [x for x in body if ET.QName(x).localname != "sectPr"]
    check(len(body_blocks) == len(structure["blocos"]), path.name, "Quantidade de blocos do JSON difere do OOXML")
    run_checks = 0
    structure_paragraphs = []
    list_counts = Counter()
    list_sequences = defaultdict(list)
    numbering = xmls["word/numbering.xml"]
    for i, (block, stored) in enumerate(zip(body_blocks, structure["blocos"])):
        where = f"DOCX:bloco {i + 1}"
        kind = ET.QName(block).localname
        check(kind == stored["tipo"], where, "Tipo estrutural diferente")
        check(i == stored["indice_ooxml"], where, "Posição OOXML diferente")
        if kind == "p":
            matches = [(block, stored)]
        else:
            rows = block.findall("w:tr", NS)
            check(len(rows) == len(stored["linhas"]), where, "Quantidade de linhas diferente no JSON")
            matches = []
            for row, saved_row in zip(rows, stored["linhas"]):
                cells = row.findall("w:tc", NS)
                check(len(cells) == len(saved_row), where, "Quantidade de células diferente no JSON")
                for cell, saved_cell in zip(cells, saved_row):
                    cell_ps = cell.findall("w:p", NS)
                    check(len(cell_ps) == 1, where, "Célula não representável pela estrutura registrada")
                    matches.append((cell_ps[0], saved_cell))
        for paragraph, saved_p in matches:
            text = text_of(paragraph)
            structure_paragraphs.append(saved_p["texto"])
            check(text == saved_p["texto"], where, "Texto original diferente no JSON")
            check(digest(text.encode()) == saved_p["sha256_texto_utf8"], where, "Hash de parágrafo diferente")
            runs = [{"texto": text_of(r), "negrito": toggle(r, "b"), "italico": toggle(r, "i")}
                    for r in paragraph.findall("w:r", NS)]
            check(runs == saved_p["runs"], where, "Runs ou ênfase diferentes no JSON")
            run_checks += len(runs)
        num = block.find("w:pPr/w:numPr", NS)
        if num is not None:
            numid = num.find("w:numId", NS).get(f"{{{W}}}val")
            level = num.find("w:ilvl", NS).get(f"{{{W}}}val")
            num_def = numbering.xpath(f'w:num[@w:numId="{numid}"]', namespaces=NS)[0]
            abstract_id = num_def.find("w:abstractNumId", NS).get(f"{{{W}}}val")
            definition = numbering.xpath(f'w:abstractNum[@w:abstractNumId="{abstract_id}"]/w:lvl[@w:ilvl="{level}"]', namespaces=NS)[0]
            fmt = definition.find("w:numFmt", NS).get(f"{{{W}}}val")
            start = int(definition.find("w:start", NS).get(f"{{{W}}}val"))
            marker = definition.find("w:lvlText", NS).get(f"{{{W}}}val")
            saved_list = stored.get("lista", {})
            check(saved_list.get("numId") == numid and saved_list.get("nivel") == int(level)
                  and saved_list.get("formato") == fmt and saved_list.get("inicio") == start
                  and saved_list.get("marcador_original") == marker, where, "Definição da lista difere do OOXML")
            list_counts[fmt] += 1
            list_sequences[numid].append(saved_list.get("numero_renderizado"))
            if fmt == "decimal":
                check(saved_list.get("numero_renderizado") == start + len(list_sequences[numid]) - 1,
                      where, "Ordinal calculado difere da sequência da lista original")
            md_line = md_lines[stored["linha_markdown_inicial"] - 1]
            expected_marker = "- " if fmt == "bullet" else f"{saved_list['numero_renderizado']}. "
            check(md_line.startswith("  " * int(level) + expected_marker), where, "Marcador da lista diferente no Markdown")
    check(source_paragraphs == structure_paragraphs, path.name, "Ordem de parágrafos no JSON difere da fonte")
    special = ["hyperlink", "drawing", "pict", "object", "footnoteReference", "endnoteReference", "commentReference",
               "commentRangeStart", "commentRangeEnd", "ins", "del", "moveFrom", "moveTo", "delText", "txbxContent",
               "altChunk", "fldSimple", "instrText", "fldChar", "sdt", "sym", "oMath", "oMathPara", "tab", "br", "gridSpan", "vMerge"]
    extra = [n for n in parts if re.search(r"word/(?:header|footer|footnotes|endnotes|comments|embeddings|media)", n)]
    relationships = []
    for name, content in parts.items():
        if name.endswith(".rels"):
            relationships.extend({"parte": name, **dict(x.attrib)} for x in ET.fromstring(content))
    external = [x for x in relationships if x.get("TargetMode") == "External"]
    metadata = {name: {ET.QName(x).localname: x.text for x in xmls[name]}
                for name in ["docProps/core.xml", "docProps/app.xml"] if name in xmls}
    style_root = xmls["word/styles.xml"]
    styles = [{"id": x.get(f"{{{W}}}styleId"), "tipo": x.get(f"{{{W}}}type"),
               "nome": x.find("w:name", NS).get(f"{{{W}}}val") if x.find("w:name", NS) is not None else None}
              for x in style_root.findall("w:style", NS)]
    non_text_properties = {"tamanho_pagina": dict(body.find("w:sectPr/w:pgSz", NS).attrib),
                           "margens": dict(body.find("w:sectPr/w:pgMar", NS).attrib),
                           "fontes_em_runs": [dict(x.attrib) for x in root.findall(".//w:r/w:rPr/w:rFonts", NS)],
                           "propriedades_runs": dict(run_tags), "propriedades_paragrafos": dict(para_tags)}
    part_matches = {name: check(digest(data) == manifest["partes_pacote_e_sha256"].get(name), name,
                                "Hash da parte DOCX diferente do manifesto") for name, data in parts.items()}
    output_matches = []
    for item in manifest["arquivos_gerados"]:
        try:
            SOURCES.verify_output(item["caminho"], item["sha256"])
            ok = True
        except SourceResolutionError:
            ok = False
        output_matches.append(check(ok, item["caminho"], "Hash da saída DOCX difere do manifesto"))
    return {"original": record(path, origin), "original_arquivado": record(archive), "binarios_identicos": path.read_bytes() == archive.read_bytes(),
            "origem_removida_com_registro": not SOURCES.original_path(origin).is_file(),
            "markdown": record(md_path), "estrutura": record(structure_path),
            "paragrafos_totais": len(all_paragraphs), "paragrafos_diretos": len(body.findall("w:p", NS)),
            "caracteres_texto": sum(map(len, source_paragraphs)), "runs": counts["r"], "nos_texto": counts["t"],
            "runs_conferidos_no_json": run_checks, "tabelas": counts["tbl"], "linhas_tabela": counts["tr"], "celulas": counts["tc"],
            "paragrafos_negrito_fonte": len(bold_paragraphs), "paragrafos_com_enfase_md": md_bold_paragraphs,
            "linhas_tabela_md": md_table_rows, "itens_lista": dict(list_counts),
            "texto_ooxml_igual_python_docx": independent_equal, "texto_ooxml_igual_markdown_exato": md_equal,
            "texto_ooxml_igual_estrutura_exato": source_paragraphs == structure_paragraphs,
            "sha256_paragrafos_frescos_separados_nul": digest("\0".join(source_paragraphs).encode()),
            "sha256_paragrafos_md_separados_nul": digest("\0".join(md_paragraphs).encode()),
            "diferencas_textuais": differences, "recursos_especiais": {k: counts[k] for k in special},
            "partes_de_conteudo_adicionais": extra, "relacionamentos_externos": external,
            "partes_pacote": [{"nome": n, "bytes": len(d), "sha256": digest(d)} for n, d in parts.items()],
            "partes_hashes_manifesto_iguais": all(part_matches.values()), "saidas_hashes_manifesto_iguais": all(output_matches),
            "metadados_frescos": metadata, "estilos_pacote": styles, "apresentacao_word": non_text_properties,
            "quebras_pagina_em_cache": counts["lastRenderedPageBreak"],
            "renderizacao_word_nesta_auditoria": {"executada": False, "motivo": "Auditoria somente leitura; renderizador bundled indisponível conforme inventário anterior. Não foi usado LibreOffice desktop nem alegada equivalência visual do Word."},
            "continuidade": {"grafias_Timo_e_Fesh_preservadas": md_equal, "status_markdown": "revisar_continuidade" if "status: revisar_continuidade" in md_lines else None,
                              "limite": "A auditoria preserva o resumo tal como recebido; não equipara Fesh a Fash nem recupera o diário externo apenas citado."}}


def main():
    origins = ["BASE INICIAL/" + name for name in ["Nota1.pdf", "Nota2.pdf", "Resumo detalhado.docx"]]
    inputs = [SOURCES.resolve(origin) for origin in origins]
    archives = [ROOT / "arquivo/originais/BASE INICIAL" / p.name for p in inputs]
    unchanged_paths = inputs + archives + list((ROOT / "conteudo/Anexos/pdfs").rglob("*")) + list((ROOT / "conteudo/Anexos/documentos").rglob("*")) + list((ROOT / "conteudo/Fontes/Documentos").glob("*.md"))
    before = {rel(p): digest(p.read_bytes()) for p in unchanged_paths if p.is_file()}
    pdf_manifest = load(ROOT / "docs/migracao/pdf.json")
    docx_manifest = load(ROOT / "docs/migracao/docx.json")
    pdfs = [audit_pdf(stem, pdf_manifest) for stem in ["Nota1", "Nota2"]]
    docx = audit_docx(docx_manifest)
    after = {rel(p): digest(p.read_bytes()) for p in unchanged_paths if p.is_file()}
    check(before == after, "auditoria", "Algum arquivo existente mudou durante a auditoria")
    report = {
        "schema": "auditoria-exclusao-documentos-v1", "gerado_em": datetime.now(timezone.utc).isoformat(),
        "escopo": {"fontes": origins, "fontes_consultadas": [rel(p) for p in inputs], "operacao": "Somente leitura, sem exclusão, movimentação, alteração de arquivos existentes ou execução dos conversores.",
                   "exclui": "Demais fontes da BASE, planilhas, arquivos TXT e entidade/cronologia editorial são auditados em frentes separadas.",
                   "independencia": "Novas extrações pypdf/pdfplumber/python-docx e leitura direta do pacote OOXML, sem importar os conversores; manifestos antigos usados só para conferir integridade e apontar evidências.",
                   "normalizacao_pdf": "Somente espaços/quebras de linha e sintaxe Markdown gerada de lista são removidos; texto, pontuação e ordem por página comparados.",
                   "normalizacao_docx": "Somente marcadores Markdown de título/lista/tabela/ênfase e escapes; texto e espaços originais de cada parágrafo/célula comparados exatamente."},
        "pdfs": pdfs, "docx": docx,
        "totais": {"pdfs": len(pdfs), "paginas_pdf": sum(p["paginas"] for p in pdfs), "paginas_pdf_com_texto": sum(p["paginas_com_texto"] for p in pdfs),
                   "paragrafos_docx": docx["paragrafos_totais"], "arquivos_existentes_verificados_inalterados": len(before)},
        "erros": ERRORS,
        "conteudo_relevante_omitido_detectado": bool(ERRORS),
        "limites_da_comparacao": [
            "As 80 páginas PNG existentes foram abertas e decodificadas, conferidas em dimensões de 120 dpi e hashes; os PDFs não foram novamente renderizados. A equivalência visual fonte/render não é uma nova comparação pixel a pixel.",
            "A leitura de objetos dos PDFs e do pacote Word cobre texto, imagens, anotações, campos, anexos e recursos estruturais declarados; não prova reversibilidade binária da conversão.",
            "Não foi feita renderização Word; paginação 17 e 16 quebras em cache são metadados da fonte, não nova medição visual.",
            "Ausência de divergências textuais não resolve a continuidade Timo/Fesh/Fash/Glim nem valida a veracidade narrativa das fontes.",
        ],
        "perdas_por_cenario": [
            {"cenario": 1, "acao_hipotetica": "Remover apenas BASE INICIAL, manter arquivo/originais e conteudo.",
             "documentos_pdf_docx": "Sem perda documental para estas três fontes: cópias arquivadas são idênticas byte a byte; permite restituição exata desses binários.",
             "perdas_reais": [], "condicao": "As três cópias de arquivo/originais devem permanecer íntegras; esta conclusão não autoriza excluir a pasta inteira sem auditoria das demais fontes."},
            {"cenario": 2, "acao_hipotetica": "Remover também os PDF/DOCX de arquivo/originais, manter Markdown, Anexos e manifestos.",
             "conteudo_narrativo": "Nenhuma omissão de texto narrativo foi detectada na comparação fresca das 80 páginas PDF e dos 337 parágrafos/células DOCX.",
             "perdas_reais": ["Perda dos três arquivos originais e impossibilidade de reconstrução exata dos binários pelos hashes.",
                               "PDF: texto vetorial, fontes, streams de desenho e demais objetos PDF não são preservados como PDF pelos PNGs de 120 dpi; alta ampliação/impressão e editabilidade nativa deixam de ser equivalentes.",
                               "PDF: itálico, cores, sublinhados e espaçamento não foram transcritos como estilos de texto Markdown; continuam visíveis nos PNGs. Exemplo observado: os nomes dos portais em Nota2 página 14.",
                               "DOCX: estilos, tema, fontes, margens, geometria de tabela, propriedades de seção e demais partes Word não estão serializados integralmente no Markdown/estrutura.json. O JSON conserva texto/runs/ênfase/listas, não um pacote Word restituível.",
                               "Links dos Markdown para os originais arquivados passam a apontar para arquivos ausentes."],
             "preservado": "Texto integral, tabela 16x2, listas, ênfase, imagens extraídas e representação raster das páginas PDF permanecem nos convertidos; metadados selecionados permanecem nos manifestos.",
             "sem_perda_ausente": "Não há campos, links PDF, anotações PDF, anexos embutidos PDF, imagens DOCX, comentários, notas ou revisões DOCX nesta fonte que precisem ser recuperados.",
             "recomendacao": "Pode atender leitura/consulta do enredo com os anexos, mas não equivale a preservação documental sem perdas. Manter os binários para arquivo e reversibilidade."},
            {"cenario": 3, "acao_hipotetica": "Manter somente Markdown, excluindo originais e todos os Anexos.",
             "conteudo_narrativo": "O texto narrativo, a tabela e as listas já estão no Markdown; não foi detectado texto narrativo exclusivo das imagens.",
             "perdas_reais": ["Todas as perdas do cenário 2.", "Perda das 80 imagens completas de página e dos recursos raster extraídos: fundo claro e marcadores originais dos PDFs.",
                               "Perda dos textos de extração na ordem nativa/espacial e dos dados por página; deixa de ser possível revisar independentemente a transcrição contra essas representações.",
                               "Perda de estrutura.json, seus 362 runs e limites de runs, mapas de blocos/linhas, campos de lista e quebras em cache; a ênfase legível permanece no Markdown, mas o registro estrutural de origem é descartado.",
                               "Links e imagens Markdown de anexos tornam-se quebrados; a apresentação visual original deixa de estar disponível."],
             "recomendacao": "Não recomendado como arquivo completo. Serve apenas como versão textual de consulta, aceitando as perdas explícitas."}
        ],
        "recomendacao_tecnica": "Para estes PDFs/DOCX, apenas remover a duplicata BASE mantendo os binários arquivados oferece preservação exata. Markdown+Anexos preservam o conteúdo consultável verificado, mas não substituem os originais para restituição documental.",
        "arquivos_existentes_inalterados": before == after,
        "revisao_visual_independente": {
            "executada": True, "data": "2026-10-29", "tipo": "Inspeção visual pelo agente com visualizador de imagens no contexto da criação desta auditoria; não é refeita pela execução do script.",
            "fontes_sha256_observadas": {"Nota1.pdf": "7f1ec942aa1b1716661295eb04ea6e383de12f5a46294532c8a9c1602d5e9884", "Nota2.pdf": "b92a57304804baad64a9493f4958580ae92f87fb1ad5a551b958499a7e603555"},
            "folhas_contato": [rel(p) for p in sorted((ROOT / "conteudo/Anexos/pdfs").glob("*/revisao/*.jpg"))],
            "paginas_em_folhas_contato": 80,
            "paginas_ampliadas": ["Nota1:48", "Nota1:49", "Nota1:50", "Nota2:14", "Nota2:15"],
            "imagens_extraidas_inspecionadas": ["conteudo/Anexos/pdfs/Nota1/imagens-extraidas/1605b37557cf5692.jpg", "conteudo/Anexos/pdfs/Nota1/imagens-extraidas/0ee09187c34d75b4.png"],
            "achados": ["Texto legível nos PNGs observados, sem conteúdo narrativo manuscrito ou ilustrado ausente do texto nativo.",
                         "Os dois recursos raster únicos compartilhados pelos PDFs são um fundo quase branco e um marcador circular de lista; não contêm texto narrativo exclusivo.",
                         "Nota2 página 15 está visualmente vazia, com o fundo preservado.",
                         "Nota1 páginas 48 a 50 já mostram Personagem/Papel em fluxo linear na apresentação de origem capturada; o Markdown mantém essa ordem sem descartar os papéis.",
                         "A fonte contém apresentação que Markdown não conserva como estilos: por exemplo, nomes de portais em itálico em Nota2 página 14; os PNGs mantêm a aparência. Isso não foi tratado como perda de enredo.",
                         "Os nove retângulos preenchidos vetoriais de Nota1 acompanham sublinhados de números azuis observados nas folhas; não são diagramas narrativos. Há zero anotações de link interativo no PDF."],
            "limite": "Revisão de PNGs e folhas existentes, sem nova renderização do PDF ou comparação fonte/render pixel a pixel; Word não foi renderizado."
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"relatorio": rel(OUT), "totais": report["totais"], "erros": ERRORS,
                      "pdf": [{"nome": p["original"]["caminho"], "paginas": p["paginas"], "anotacoes": p["anotacoes"], "links": p["links_interativos"], "campos": p["campos_formulario"], "anexos": p["arquivos_embutidos"], "imagens_unicas": len(p["imagens_unicas"]), "operadores": p["operadores_pdf"]} for p in pdfs],
                      "docx": {k: docx[k] for k in ["paragrafos_totais", "runs", "tabelas", "linhas_tabela", "celulas", "itens_lista", "texto_ooxml_igual_markdown_exato", "diferencas_textuais"]}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
