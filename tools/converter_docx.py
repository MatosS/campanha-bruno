"""Conversão auditável da fonte Resumo detalhado.docx, sem alterar o original.

Executar com o Python bundled do Codex. Este conversor é deliberadamente
específico: interrompe diante de recursos não representados pelo documento
auditado, em vez de ignorar conteúdo de um DOCX futuro silenciosamente.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

from docx import Document
from lxml import etree as ET

from fontes_migracao import SourceResolver, require_regeneration_opt_in


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "BASE INICIAL/Resumo detalhado.docx"
ARCHIVE = ROOT / "arquivo/originais/BASE INICIAL/Resumo detalhado.docx"
OUTPUT = ROOT / "conteudo/Fontes/Documentos/Resumo detalhado.md"
ATTACHMENTS = ROOT / "conteudo/Anexos/documentos/resumo-detalhado"
MANIFEST = ROOT / "docs/migracao/docx.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text_of(element: ET._Element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS))


def enabled(element: ET._Element, name: str) -> bool:
    prop = element.find(f"w:rPr/w:{name}", NS)
    return prop is not None and prop.get(f"{{{W}}}val", "true") not in ("0", "false", "off")


def escape(text: str) -> str:
    return re.sub(r"([\\`*_\[\]|])", r"\\\1", text)


def inline(paragraph: ET._Element) -> tuple[str, list[dict]]:
    groups = []
    runs = []
    for run in paragraph.findall("w:r", NS):
        content = text_of(run)
        bold, italic = enabled(run, "b"), enabled(run, "i")
        runs.append({"texto": content, "negrito": bold, "italico": italic})
        if groups and groups[-1][0] == (bold, italic):
            groups[-1][1] += content
        else:
            groups.append([(bold, italic), content])
    result = []
    for (bold, italic), content in groups:
        match = re.fullmatch(r"(\s*)(.*?)(\s*)", content, flags=re.S)
        lead, core, tail = match.groups()
        marker = ("**" if bold else "") + ("_" if italic else "")
        result.append(lead + (marker + escape(core) + marker[::-1] if core else "") + tail)
    return "".join(result), runs


def plain(markdown: str) -> str:
    # Os caracteres literais escapados ficam protegidos antes de retirar ênfase.
    chars = []
    protected = {}
    cursor = 0
    while cursor < len(markdown):
        if markdown[cursor] == "\\" and cursor + 1 < len(markdown):
            token = chr(0xE000 + len(protected))
            protected[token] = markdown[cursor + 1]
            chars.append(token)
            cursor += 2
        else:
            chars.append(markdown[cursor])
            cursor += 1
    value = "".join(chars).replace("**", "").replace("_", "")
    for token, char in protected.items():
        value = value.replace(token, char)
    return value


def main() -> None:
    require_regeneration_opt_in(ROOT)
    source = SourceResolver(ROOT).resolve(local(SOURCE))
    source_bytes = source.read_bytes()
    source_hash = sha(source_bytes)
    with ZipFile(source) as package:
        part_names = package.namelist()
        xml_parts = {name: ET.fromstring(package.read(name)) for name in part_names if name.endswith(".xml")}
        part_hashes = {name: sha(package.read(name)) for name in part_names}
        document = xml_parts["word/document.xml"]
        body = document.find("w:body", NS)
        features = Counter(ET.QName(e).localname for e in document.iter())
        rels = ET.fromstring(package.read("word/_rels/document.xml.rels"))
        relationships = [dict(rel.attrib) for rel in rels]

        # Cobertura explícita: estes recursos não existem nesta fonte. Caso
        # apareçam em uma versão futura, exigem conversão própria antes de seguir.
        unsupported = {
            "hyperlink", "drawing", "pict", "object", "footnoteReference", "endnoteReference",
            "commentReference", "commentRangeStart", "commentRangeEnd", "ins", "del",
            "moveFrom", "moveTo", "delText", "txbxContent", "altChunk", "fldSimple",
            "instrText", "fldChar", "sdt", "sym", "oMath", "oMathPara", "tab", "br",
            "gridSpan", "vMerge", "customXml", "subDoc",
        }
        unexpected = {name: features[name] for name in unsupported if features[name]}
        extra_content_parts = [name for name in part_names if re.search(
            r"word/(header|footer|footnotes|endnotes|comments|embeddings|media)", name)]
        assert not unexpected, f"Recursos que exigem nova conversão: {unexpected}"
        assert not extra_content_parts, f"Partes adicionais exigem inspeção: {extra_content_parts}"
        assert not any(rel.get("Type", "").endswith("/hyperlink") for rel in relationships)
        assert all(ET.QName(b).localname in ("p", "tbl", "sectPr") for b in body)
        assert all(ET.QName(c).localname in ("pPr", "r") for p in body.findall("w:p", NS) for c in p)

        numbering = xml_parts["word/numbering.xml"]
        number_defs = {}
        for num in numbering.findall("w:num", NS):
            numid = num.get(f"{{{W}}}numId")
            abstract_id = num.find("w:abstractNumId", NS).get(f"{{{W}}}val")
            abstract = numbering.xpath(f'./w:abstractNum[@w:abstractNumId="{abstract_id}"]', namespaces=NS)[0]
            number_defs[numid] = {}
            for level in abstract.findall("w:lvl", NS):
                level_id = level.get(f"{{{W}}}ilvl")
                number_defs[numid][level_id] = {
                    "formato": level.find("w:numFmt", NS).get(f"{{{W}}}val"),
                    "inicio": int(level.find("w:start", NS).get(f"{{{W}}}val")),
                    "marcador_original": level.find("w:lvlText", NS).get(f"{{{W}}}val"),
                }

    original_url = quote("../../../arquivo/originais/BASE INICIAL/Resumo detalhado.docx", safe="/.")
    lines = [
        "---", "tipo: fonte", 'titulo: "Resumo detalhado — Diário de Timo Pé-de-Musgo"',
        "campanhas: []", "publico: true", "status: revisar_continuidade", "origens:",
        '  - "BASE INICIAL/Resumo detalhado.docx"', "aliases:",
        '  - "Resumo detalhado"', '  - "Resumo do Diário de Timo Pé-de-Musgo"', "---", "",
        f"> **Nota editorial de migração:** [Original DOCX preservado]({original_url}). "
        "A transcrição integral começa no título abaixo. Esta fonte trata de Timo Pé-de-Musgo e menciona "
        "Fesh; essas grafias foram preservadas. O documento, por si só, não comprova a ligação com as "
        "campanhas de Fash e Glim nem permite equiparar esses personagens. A continuidade permanece em revisão.", "",
    ]
    source_start_line = len(lines) + 1
    blocks, source_paragraphs, verification_records = [], [], []
    list_counters = defaultdict(int)
    current_section = None

    for position, block in enumerate(body):
        kind = ET.QName(block).localname
        if kind == "sectPr":
            continue
        record = {"ordem": len(blocks) + 1, "indice_ooxml": position, "tipo": kind,
                  "linha_markdown_inicial": len(lines) + 1}
        if kind == "p":
            text = text_of(block)
            formatted, runs = inline(block)
            assert "".join(run["texto"] for run in runs) == text
            nonempty = [run for run in runs if run["texto"].strip()]
            all_bold = bool(nonempty) and all(run["negrito"] for run in nonempty)
            num = block.find("w:pPr/w:numPr", NS)
            marker = ""
            level = None
            if position == 0:
                level = 1
            elif all_bold and re.match(r"^\d+\.\d+\. ", text):
                level = 3
            elif all_bold and re.match(r"^\d+\. ", text):
                level = 2
                current_section = text.split(".", 1)[0]
            elif all_bold:
                level = 4 if current_section == "2" else 3
            if level:
                marker = "#" * level + " "
                rendered = marker + escape(text)
                record["nivel_titulo_markdown"] = level
                verification_records.append((text, rendered[len(marker):]))
            elif num is not None:
                numid = num.find("w:numId", NS).get(f"{{{W}}}val")
                ilvl = num.find("w:ilvl", NS).get(f"{{{W}}}val")
                definition = number_defs[numid][ilvl]
                assert definition["formato"] in ("bullet", "decimal")
                counter_key = (numid, ilvl)
                if not list_counters[counter_key]:
                    list_counters[counter_key] = definition["inicio"] - 1
                list_counters[counter_key] += 1
                marker = "  " * int(ilvl) + ("- " if definition["formato"] == "bullet" else f"{list_counters[counter_key]}. ")
                rendered = marker + formatted
                record["lista"] = {"numId": numid, "nivel": int(ilvl), **definition,
                                   "numero_renderizado": list_counters[counter_key] if definition["formato"] == "decimal" else None}
                verification_records.append((text, rendered[len(marker):]))
            else:
                rendered = formatted
                verification_records.append((text, rendered))
            record.update({"texto": text, "sha256_texto_utf8": sha(text.encode()), "runs": runs,
                           "quebras_pagina_em_cache": len(block.findall(".//w:lastRenderedPageBreak", NS))})
            source_paragraphs.append(text)
            lines.append(rendered)
        else:
            rows = []
            for row in block.findall("w:tr", NS):
                cells = []
                for cell in row.findall("w:tc", NS):
                    paragraphs = cell.findall("w:p", NS)
                    assert len(paragraphs) == 1, "Tabela com múltiplos parágrafos exige nova representação"
                    paragraph = paragraphs[0]
                    text = text_of(paragraph)
                    formatted, runs = inline(paragraph)
                    cells.append({"texto": text, "sha256_texto_utf8": sha(text.encode()), "runs": runs})
                    source_paragraphs.append(text)
                    verification_records.append((text, formatted))
                rows.append(cells)
                rendered_cells = [inline(p)[0] for cell in row.findall("w:tc", NS) for p in cell.findall("w:p", NS)]
                lines.append("| " + " | ".join(rendered_cells) + " |")
                if len(rows) == 1:
                    lines.append("| " + " | ".join("---" for _ in cells) + " |")
            record.update({"linhas": rows, "quantidade_linhas": len(rows),
                           "quantidade_colunas": len(rows[0]), "celulas": sum(map(len, rows))})
        record["linha_markdown_final"] = len(lines)
        blocks.append(record)
        lines.append("")

    # Verificação Unicode por parágrafo/célula após retirada apenas da sintaxe
    # acrescentada. Mantém até espaços finais originais na versão Markdown.
    failures = [i for i, (source, md) in enumerate(verification_records) if source != plain(md)]
    assert not failures, f"Parágrafos divergentes: {failures}"
    all_xml_paragraphs = [text_of(p) for p in document.xpath(".//w:p", namespaces=NS)]
    assert source_paragraphs == all_xml_paragraphs
    independent = Document(source)
    independent_body = []
    for block in independent.element.body:
        if ET.QName(block).localname == "p":
            from docx.text.paragraph import Paragraph
            independent_body.append(Paragraph(block, independent).text)
        elif ET.QName(block).localname == "tbl":
            from docx.table import Table
            independent_body.extend(p.text for row in Table(block, independent).rows for cell in row.cells for p in cell.paragraphs)
    assert independent_body == source_paragraphs

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    # Confere o arquivo persistido, incluindo células, sem depender do JSON auxiliar.
    persisted = OUTPUT.read_text(encoding="utf-8").splitlines()
    reread_paragraphs = []
    for block in blocks:
        content = persisted[block["linha_markdown_inicial"] - 1:block["linha_markdown_final"]]
        if block["tipo"] == "p":
            value = re.sub(r"^(?:#{1,6} |(?:  )*(?:- |\d+\. ))", "", content[0], count=1)
            reread_paragraphs.append(plain(value))
        else:
            for row_index, row in enumerate(content):
                if row_index == 1:
                    continue
                encoded = re.split(r"(?<!\\) \| ", row[2:-2])
                reread_paragraphs.extend(plain(value) for value in encoded)
    assert reread_paragraphs == source_paragraphs
    source_text_sha = sha("\0".join(source_paragraphs).encode())
    parsed_text_sha = sha("\0".join(reread_paragraphs).encode())
    structure_file = ATTACHMENTS / "estrutura.json"
    write_json(structure_file, {
        "fonte": local(SOURCE), "sha256_fonte": source_hash, "markdown": local(OUTPUT),
        "primeira_linha_transcricao": source_start_line,
        "nota": "Blocos na ordem do corpo OOXML; linhas Markdown são de base 1. Textos e runs preservam Unicode e espaços originais.",
        "blocos": blocks,
    })
    assert sha(source.read_bytes()) == source_hash
    archive_hash = sha(ARCHIVE.read_bytes()) if ARCHIVE.exists() else None
    assert archive_hash in (None, source_hash)
    counts = {
        "blocos_corpo": len(blocks), "paragrafos_diretos": features["p"] - features["tc"],
        "paragrafos_totais_incluindo_celulas": features["p"], "trechos_texto_ooxml": features["t"],
        "caracteres_texto_unicode": sum(map(len, source_paragraphs)),
        "tabelas": features["tbl"], "linhas_tabela": features["tr"], "celulas_tabela": features["tc"],
        "itens_lista": features["numPr"],
        "itens_lista_marcadores": sum(b.get("lista", {}).get("formato") == "bullet" for b in blocks),
        "itens_lista_numerada": sum(b.get("lista", {}).get("formato") == "decimal" for b in blocks),
        "titulos_markdown": sum("nivel_titulo_markdown" in b for b in blocks),
        "runs_negrito": len(document.xpath(".//w:r[w:rPr/w:b]", namespaces=NS)),
        "propriedades_paragrafo_negrito": len(document.xpath(".//w:pPr/w:rPr/w:b", namespaces=NS)),
        "quebras_pagina_em_cache": features["lastRenderedPageBreak"],
    }
    absent_features = {name: features[name] for name in sorted(unsupported)}
    generated = [OUTPUT, structure_file, Path(__file__)]
    manifest = {
        "formato_manifesto": 1, "data_migracao": "2026-10-29", "tipo": "conversao_docx_integral",
        "fonte": {"caminho": local(SOURCE), "bytes": len(source_bytes), "sha256": source_hash,
                  "original_arquivado": local(ARCHIVE), "sha256_arquivo": archive_hash},
        "destino": local(OUTPUT), "campanhas": [], "status": "revisar_continuidade",
        "contagens": counts,
        "recursos_preservados": [
            "Texto integral de todos os 337 parágrafos do corpo e das células, na ordem OOXML, sem reescrita.",
            "Título e títulos numerados ou integralmente em negrito convertidos em hierarquia Markdown.",
            "Ênfase em negrito nos trechos do corpo e nas células; texto original e runs no JSON auxiliar.",
            "Todas as 64 entradas de lista, com distinção entre marcadores e numeração e ordinais calculados a partir de numbering.xml.",
            "Tabela completa de 16 linhas e 2 colunas na posição original, incluindo a linha de cabeçalho.",
            "As menções textuais ao arquivo Diário de Timo são mantidas como texto; a fonte não contém hyperlinks reais.",
            "Pacote DOCX original exato acompanha a migração no arquivo de originais para preservar propriedades e apresentação Word.",
        ],
        "recursos_ausentes_confirmados_ooxml": absent_features,
        "partes_conteudo_adicionais": extra_content_parts,
        "partes_pacote_e_sha256": part_hashes,
        "relacionamentos_documento": relationships,
        "metadados_ooxml": {
            "core": {ET.QName(e).localname: e.text for e in xml_parts["docProps/core.xml"]},
            "app": {ET.QName(e).localname: e.text for e in xml_parts["docProps/app.xml"]},
        },
        "verificacoes": {
            "todos_blocos_ordenados": True, "todos_paragrafos_e_celulas_texto_exato": True,
            "quantidade_paragrafos_comparados": len(source_paragraphs),
            "comparacao_independente_python_docx": True, "markdown_reaberto_e_comparado": True,
            "sha256_texto_fonte_separado_por_nul": source_text_sha,
            "sha256_texto_markdown_reconstruido_separado_por_nul": parsed_text_sha,
            "fonte_inalterada": True,
            "original_arquivado_hash_identico": archive_hash == source_hash if archive_hash else None,
            "cobertura_estrutural": "Auditoria de todas as partes XML, todos os filhos do corpo e todos os 362 nós w:t; verificações bloqueiam recursos adicionais não convertidos.",
            "renderizacao_visual": {"executada": False, "motivo": "O loader não forneceu LibreOffice bundled e a busca em dependencies não encontrou soffice/libreoffice. Nenhuma instalação desktop do usuário foi utilizada."},
        },
        "limitacoes": [
            "Markdown preserva conteúdo e estrutura de leitura, mas não a paginação, fontes, margens ou geometria exata do Word; essas propriedades permanecem no original DOCX.",
            "As 16 quebras de página em cache e o metadado Pages=17 são registros do Word, não uma contagem visual validada nesta conversão.",
            "Não houve renderização visual por ausência de LibreOffice bundled; a completude textual/estrutural foi validada sem esse renderer.",
            "O vínculo do relato de Timo Pé-de-Musgo e do nome Fesh com Fash/Glim não é comprovado por esta fonte e exige revisão de continuidade; nenhuma identidade foi equiparada.",
            "A fonte chama a si própria de resumo e cita um diário externo; a conversão preserva integralmente este resumo, sem alegar ter recuperado o diário não incluído no pacote.",
        ],
        "arquivos_gerados": [{"caminho": local(path), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())} for path in generated],
    }
    actual_mentions = sum(text.count("🌿 Diário de Timo Pé-de-Musgo.docx") for text in source_paragraphs)
    manifest["contagens"]["mencoes_textuais_arquivo_diario"] = actual_mentions
    manifest["recursos_preservados"][5] = (
        f"Todas as {actual_mentions} menções textuais ao arquivo Diário de Timo são mantidas como texto; a fonte não contém hyperlinks reais."
    )
    write_json(MANIFEST, manifest)
    print(json.dumps({"destino": local(OUTPUT), "manifesto": local(MANIFEST), "contagens": counts,
                      "fonte_sha256": source_hash, "sha_texto_fonte": source_text_sha,
                      "sha_texto_markdown": parsed_text_sha}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
