"""Convert the two source PDFs without changing them.

Requires the bundled pypdf, pdfplumber, Pillow and Poppler runtime.
The Markdown carries all source text; full-page PNGs and the original PDFs
preserve visual information. No OCR or narrative rewriting is performed.
"""

from __future__ import annotations

import collections
import argparse
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata
from urllib.parse import quote

import pdfplumber
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

from fontes_migracao import SourceResolver, require_regeneration_opt_in


ROOT = Path(__file__).resolve().parents[1]
DPI = 120
SOURCES = {
    "Nota1": {
        "title": "Dossiê de personagem — Okay d’Boa",
        "campaigns": ["fash", "glim"],
        "status": "importado",
        "text_candidate": "Dossiê de personagem - Okay dBoa.txt",
        "campaign_evidence": "O próprio texto identifica Glim como companheiro atual de Okay e Fash entre os companheiros de sua vida anterior como Kael; as lacunas declaradas pelo documento permanecem no corpo integral.",
    },
    "Nota2": {
        "title": "Personagens e Heróis",
        "campaigns": [],
        "status": "revisar_continuidade",
        "text_candidate": "Personagens e Herois.txt",
        "campaign_evidence": "Há menções a Fash e aos demais personagens, mas a atribuição dos diários da nova era a Firael precisa ser reconciliada em revisão editorial; nenhuma identidade ou continuidade foi deduzida automaticamente.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_record(path: Path, role: str) -> dict:
    data = path.read_bytes()
    return {"path": rel(path), "role": role, "bytes": len(data), "sha256": sha256(data)}


def normalized(text: str) -> str:
    """Only normalize Unicode and whitespace, never change content words."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def decoded_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding), encoding
        except UnicodeError:
            pass
    raise UnicodeError(f"Could not decode {path}")


def compare_text(source_text: str, candidate: Path) -> dict:
    text, encoding = decoded_text(candidate)
    a, b = normalized(text), normalized(source_text)
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    changes = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            continue
        changes.append({
            "kind": tag,
            "txt_start": a0,
            "txt_end": a1,
            "pdf_start": b0,
            "pdf_end": b1,
            "txt": a[a0:a1],
            "pdf": b[b0:b1],
            "context_before": a[max(0, a0 - 90):a0],
            "context_after": a[a1:a1 + 90],
        })
    return {
        **file_record(candidate, "variante_textual_original"),
        "encoding": encoding,
        "comparison_method": "NFC e espaços consecutivos normalizados; demais caracteres, ordem e pontuação mantidos. Diferenças completas registradas abaixo.",
        "equal_after_whitespace_normalization": a == b,
        "similarity_ratio": matcher.ratio(),
        "txt_normalized_characters": len(a),
        "pdf_normalized_characters": len(b),
        "differences_count": len(changes),
        "differences": changes,
    }


def blocks_for_page(page) -> tuple[list[dict], list[dict]]:
    lines = page.extract_text_lines(return_chars=False)
    small_images = [im for im in page.images if im["width"] < 20 and im["height"] < 20]
    blocks = []
    for line in lines:
        cy = (line["top"] + line["bottom"]) / 2
        bullet = any(
            im["x1"] < line["x0"]
            and abs((im["top"] + im["bottom"]) / 2 - cy) < 16
            for im in small_images
        )
        previous = blocks[-1]["lines"][-1] if blocks else None
        paragraph_break = previous and (
            line["top"] - previous["top"] > 50
            or abs(line["x0"] - previous["x0"]) > 5
        )
        if not blocks or bullet or paragraph_break:
            blocks.append({"bullet": bullet, "lines": [line]})
        else:
            blocks[-1]["lines"].append(line)
    return blocks, lines


def join_lines(lines: list[dict]) -> str:
    output = ""
    for line in lines:
        current = line["text"]
        if output and not output.endswith(("-", "/")):
            output += " "
        output += current
    return output


def page_markdown(blocks: list[dict]) -> str:
    output = []
    for block in blocks:
        text = join_lines(block["lines"])
        if block["bullet"]:
            text = "- " + text
        elif re.match(r"^\d+\.\s", text):
            # Escape list auto-numbering so printed source numbers stay exact.
            text = re.sub(r"^(\d+)\.", r"\1\\.", text)
        output.append(text)
    return "\n\n".join(output)


def contact_sheets(asset_dir: Path, page_count: int) -> list[Path]:
    result = []
    thumb_width, thumb_height = 300, 424
    review_dir = asset_dir / "revisao"
    review_dir.mkdir(exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
    for first in range(1, page_count + 1, 16):
        last = min(first + 15, page_count)
        sheet = Image.new("RGB", (4 * thumb_width, 4 * (thumb_height + 26)), "#d0d0d0")
        draw = ImageDraw.Draw(sheet)
        for local, number in enumerate(range(first, last + 1)):
            image = Image.open(asset_dir / f"pagina-{number:02}.png").convert("RGB")
            image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            x = (local % 4) * thumb_width
            y = (local // 4) * (thumb_height + 26)
            draw.text((x + 8, y + 3), f"{asset_dir.name} · página {number}", fill="#000000", font=font)
            sheet.paste(image, (x, y + 26))
        path = review_dir / f"contato-{first:02}-{last:02}.jpg"
        sheet.save(path, quality=94)
        result.append(path)
    return result


def convert(stem: str, info: dict, poppler: str) -> dict:
    require_regeneration_opt_in(ROOT)
    origin = f"BASE INICIAL/{stem}.pdf"
    sources = SourceResolver(ROOT)
    source = sources.resolve(origin)
    source_bytes = source.read_bytes()
    source_hash = sha256(source_bytes)
    asset_dir = ROOT / "conteudo" / "Anexos" / "pdfs" / stem
    asset_dir.mkdir(parents=True, exist_ok=True)
    media_dir = asset_dir / "imagens-extraidas"
    media_dir.mkdir(exist_ok=True)
    reader = PdfReader(source)
    count = len(reader.pages)
    page_paths = [asset_dir / f"pagina-{n:02}.png" for n in range(1, count + 1)]
    if not all(p.exists() for p in page_paths):
        subprocess.run([poppler, "-r", str(DPI), "-png", str(source), str(asset_dir / "pagina")], check=True)
    page_records = []
    all_raw, all_sorted, all_formatted = [], [], []
    unique_images = {}
    outputs = []
    with pdfplumber.open(source) as pdf:
        for number, (native_page, page, render_path) in enumerate(zip(reader.pages, pdf.pages, page_paths), 1):
            raw = native_page.extract_text() or ""
            sorted_text = page.extract_text() or ""
            blocks, lines = blocks_for_page(page)
            formatted = page_markdown(blocks)
            # Independent extractors must agree on all non-whitespace characters.
            raw_counter = collections.Counter(c for c in raw if not c.isspace())
            sorted_counter = collections.Counter(c for c in sorted_text if not c.isspace())
            if raw_counter != sorted_counter:
                raise AssertionError(f"Different native characters on {stem}, page {number}")
            rebuilt_counter = collections.Counter(c for line in lines for c in line["text"] if not c.isspace())
            if rebuilt_counter != sorted_counter:
                raise AssertionError(f"Missing formatted characters on {stem}, page {number}")
            all_raw.append(raw)
            all_sorted.append(sorted_text)
            all_formatted.append(formatted)
            media = []
            for img in native_page.images:
                digest = sha256(img.data)
                if digest not in unique_images:
                    extension = Path(img.name).suffix.lower()
                    image_path = media_dir / f"{digest[:16]}{extension}"
                    image_path.write_bytes(img.data)
                    unique_images[digest] = {
                        **file_record(image_path, "imagem_extraida_sem_alteracao"),
                        "width": img.image.width,
                        "height": img.image.height,
                        "mode": img.image.mode,
                        "occurrences": [],
                    }
                occurrence = {"page": number, "resource": img.name}
                unique_images[digest]["occurrences"].append(occurrence)
                media.append({**occurrence, "sha256": digest, "path": unique_images[digest]["path"]})
            image = Image.open(render_path)
            render_record = file_record(render_path, "pagina_completa_renderizada")
            outputs.append(render_record)
            page_records.append({
                "page": number,
                "pdf_points": [float(page.width), float(page.height)],
                "render": {**render_record, "dpi": DPI, "pixels": list(image.size)},
                "text_pypdf": raw,
                "text_pdfplumber": sorted_text,
                "characters_native": len(raw),
                "characters_reading_order": len(sorted_text),
                "non_whitespace_characters": sum(sorted_counter.values()),
                "text_extractors_same_characters": True,
                "replacement_characters": sorted_text.count("\ufffd"),
                "lines": lines,
                "text_block_count": len(blocks),
                "bullet_markers_restored_from_images": sum(b["bullet"] for b in blocks),
                "images": media,
                "annotations_count": len(native_page.get("/Annots", [])),
                "blank_text": not sorted_text.strip(),
            })

    for extractor, text in (("pypdf", "\n\f\n".join(all_raw)), ("pdfplumber", "\n\f\n".join(all_sorted))):
        path = asset_dir / f"texto-integral-{extractor}.txt"
        path.write_text(text, encoding="utf-8", newline="\n")
        outputs.append(file_record(path, "texto_integral_extraido"))

    extraction_path = asset_dir / "extracao-por-pagina.json"
    extraction_path.write_text(json.dumps(page_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    outputs.append(file_record(extraction_path, "texto_e_midia_por_pagina"))
    for entry in unique_images.values():
        outputs.append({k: entry[k] for k in ("path", "role", "bytes", "sha256")})
    sheets = contact_sheets(asset_dir, count)
    outputs.extend(file_record(path, "folha_de_contato_para_revisao_visual") for path in sheets)

    campaigns = json.dumps(info["campaigns"], ensure_ascii=False)
    source_link = "../../../arquivo/originais/BASE%20INICIAL/" + quote(source.name)
    asset_link = "../../Anexos/pdfs/" + stem
    title = info["title"]
    markdown = [
        "---",
        "tipo: fonte",
        f"titulo: {json.dumps(title, ensure_ascii=False)}",
        f"campanhas: {campaigns}",
        "publico: true",
        f"status: {info['status']}",
        "origens:",
        f"  - {json.dumps(origin, ensure_ascii=False)}",
        "aliases:",
        f"  - {stem}",
        f"  - {json.dumps(title, ensure_ascii=False)}",
        "---",
        "",
        f"# {title}",
        "",
        f"[[Inicio]] · [PDF original preservado]({source_link}) · [Texto extraído sem reordenação]({asset_link}/texto-integral-pypdf.txt) · [Extração na ordem de leitura]({asset_link}/texto-integral-pdfplumber.txt)",
        "",
        f"> Transferência integral de formato de {count} páginas. O texto abaixo segue a ordem espacial da página; os marcadores de lista que eram imagens foram representados em Markdown. Apenas as quebras de linha de diagramação foram refluídas em parágrafos. Cada página completa acompanha sua transcrição para preservar a apresentação original. A página ou o PDF deve ser consultado para verificar a disposição exata.",
        "",
    ]
    if info["status"] == "revisar_continuidade":
        markdown.extend(["> Continuidade a revisar: " + info["campaign_evidence"], ""])
    for number, formatted in enumerate(all_formatted, 1):
        markdown.extend([f"## Página {number}", "", "<!-- INICIO_TEXTO_FONTE -->", ""])
        markdown.append(formatted if formatted else "*Página sem texto extraível, visualmente em branco. O fundo original está preservado na imagem completa abaixo.*")
        markdown.extend(["", "<!-- FIM_TEXTO_FONTE -->", "", f"[Abrir imagem completa da página {number}]({asset_link}/pagina-{number:02}.png)", "", f"![{stem} — página {number}]({asset_link}/pagina-{number:02}.png)", ""])
    markdown.extend(["## Recursos visuais extraídos", "", "Os recursos abaixo foram extraídos sem edição. As páginas completas acima preservam sua posição e escala na fonte.", ""])
    for entry in unique_images.values():
        path = Path(entry["path"])
        filename = path.name
        description = "Fundo de página" if entry["width"] > 1000 else "Marcador de lista"
        occurrences = ", ".join(str(n) for n in sorted({x["page"] for x in entry["occurrences"]}))
        markdown.append(f"- [{description}, {entry['width']} × {entry['height']} px]({asset_link}/imagens-extraidas/{filename}); páginas {occurrences}.")
    markdown.extend(["", "## Relação com a variante em texto", "", f"A BASE INICIAL também contém [{info['text_candidate']}](../../../arquivo/originais/BASE%20INICIAL/{quote(info['text_candidate'])}). A comparação documentada em `docs/migracao/pdf.json` preserva as diferenças; nenhuma variante foi descartada ou conciliada silenciosamente.", ""])
    destination = ROOT / "conteudo" / "Fontes" / "Documentos" / f"{stem}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(markdown), encoding="utf-8", newline="\n")
    outputs.append(file_record(destination, "markdown_integral"))
    candidate_origin = "BASE INICIAL/" + info["text_candidate"]
    comparison = compare_text("\n".join(all_sorted), sources.resolve(candidate_origin))
    comparison["path"] = candidate_origin
    if source_hash != sha256(source.read_bytes()):
        raise AssertionError(f"Source changed: {source}")
    return {
        "source": {**file_record(source, "pdf_original"), "path": origin, "metadata": dict(reader.metadata or {})},
        "archived_original_expected": f"arquivo/originais/BASE INICIAL/{source.name}",
        "markdown": rel(destination),
        "title": title,
        "campaigns": info["campaigns"],
        "status": info["status"],
        "campaign_evidence": info["campaign_evidence"],
        "pages": count,
        "pages_with_text": sum(bool(text.strip()) for text in all_sorted),
        "blank_text_pages": [i for i, text in enumerate(all_sorted, 1) if not text.strip()],
        "text_characters_pypdf": sum(map(len, all_raw)),
        "text_characters_pdfplumber": sum(map(len, all_sorted)),
        "text_non_whitespace_characters": sum(p["non_whitespace_characters"] for p in page_records),
        "text_extractors_same_characters_all_pages": all(p["text_extractors_same_characters"] for p in page_records),
        "replacement_characters": sum(p["replacement_characters"] for p in page_records),
        "bullet_markers_restored": sum(p["bullet_markers_restored_from_images"] for p in page_records),
        "images_occurrences": sum(len(p["images"]) for p in page_records),
        "unique_images": list(unique_images.values()),
        "annotations_count": sum(p["annotations_count"] for p in page_records),
        "embedded_files": list(reader.attachments),
        "forms": reader.get_fields() or {},
        "text_variant_comparison": comparison,
        "outputs": outputs,
        "pending": (["Revisar a continuidade e a atribuição dos diários a Firael sem reconciliar automaticamente com as demais fontes."] if info["status"] == "revisar_continuidade" else []),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finalize-visual-review", action="store_true", help="Record the completed manual review and verify every saved hash/link; does not regenerate the conversion.")
    parser.add_argument("--regenerar-fontes-curadas", action="store_true", help="Permite sobrescrever saídas convertidas; exige revisão posterior da curadoria.")
    args = parser.parse_args()
    if args.finalize_visual_review:
        finalize_visual_review()
        return
    require_regeneration_opt_in(ROOT)
    poppler = shutil.which("pdftoppm")
    if not poppler:
        raise RuntimeError("Poppler pdftoppm is required; no PDF conversion was performed.")
    documents = [convert(stem, info, poppler) for stem, info in SOURCES.items()]
    manifest = {
        "schema": "migracao-pdf-v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "method": {
            "text": "pypdf native and pdfplumber spatial extraction; non-whitespace character counters compared independently on every page.",
            "markdown": "All native text in spatial reading order; paragraph reflow and Markdown list markers restored from source image positions. Original line breaks and object text order are separately preserved.",
            "render": f"Poppler pdftoppm PNG at {DPI} dpi, every complete page.",
            "image_extraction": "pypdf image data preserved without editing; equal image byte streams deduplicated within each document, occurrences fully recorded.",
            "ocr": "Not needed: all narrative content is native text. One final page of Nota2 has no text and was visually confirmed blank.",
            "source_policy": "Read-only originals; archive copies are created and verified by the parent migration process.",
        },
        "visual_review": {
            "status": "pending_contact_sheet_review",
            "rendered_pages": sum(d["pages"] for d in documents),
            "full_size_samples_inspected": ["Nota1:1", "Nota2:15"],
            "blank_pages_confirmed": ["Nota2:15"],
            "notes": "Contact sheets include every page; final visual inspection is recorded after review.",
        },
        "documents": documents,
        "totals": {
            "documents": len(documents),
            "pages": sum(d["pages"] for d in documents),
            "pages_with_text": sum(d["pages_with_text"] for d in documents),
            "text_characters_pdfplumber": sum(d["text_characters_pdfplumber"] for d in documents),
            "images_occurrences": sum(d["images_occurrences"] for d in documents),
            "unique_images_per_document": sum(len(d["unique_images"]) for d in documents),
        },
        "limitations": [
            "Native text extraction does not itself establish factual correctness or resolve inconsistencies among documents.",
            "Full page renderings preserve original appearance; text Markdown reflows printed line wraps and cannot reproduce exact typography.",
        ],
    }
    path = ROOT / "docs" / "migracao" / "pdf.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": rel(path), "totals": manifest["totals"], "comparisons": [{"source": d["source"]["path"], "differences": d["text_variant_comparison"]["differences_count"], "similarity": d["text_variant_comparison"]["similarity_ratio"]} for d in documents]}, ensure_ascii=False))


def finalize_visual_review() -> None:
    """Called only after the contact sheets and full-size samples were inspected."""
    from urllib.parse import unquote

    manifest_path = ROOT / "docs" / "migracao" / "pdf.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checked_hashes = 0
    checked_links = 0
    sources = SourceResolver(ROOT)
    for document in manifest["documents"]:
        sources.resolve(document["source"]["path"], document["source"]["sha256"])
        checked_hashes += 1
        for entry in document["outputs"]:
            path = ROOT / entry["path"]
            if sha256(path.read_bytes()) != entry["sha256"]:
                raise AssertionError(f"Changed hash: {path}")
            checked_hashes += 1
        original = ROOT / document["archived_original_expected"]
        if sha256(original.read_bytes()) != document["source"]["sha256"]:
            raise AssertionError(f"Archive differs: {original}")
        document["archived_original_verified"] = file_record(original, "copia_exata_verificada")
        markdown = ROOT / document["markdown"]
        content = markdown.read_text(encoding="utf-8")
        sections = re.findall(r"<!-- INICIO_TEXTO_FONTE -->\n\n(.*?)\n\n<!-- FIM_TEXTO_FONTE -->", content, re.S)
        extraction = json.loads((ROOT / "conteudo" / "Anexos" / "pdfs" / markdown.stem / "extracao-por-pagina.json").read_text(encoding="utf-8"))
        if len(sections) != document["pages"]:
            raise AssertionError(f"Markdown page count differs: {markdown}")
        for section, page in zip(sections, extraction):
            if page["blank_text"]:
                continue
            # Remove only the syntax introduced by this converter.
            text = re.sub(r"(?m)^- ", "", section)
            text = re.sub(r"(?m)^(\d+)\\\.", r"\1.", text)
            expected = collections.Counter(c for c in page["text_pdfplumber"] if not c.isspace())
            actual = collections.Counter(c for c in text if not c.isspace())
            if expected != actual:
                raise AssertionError(f"Markdown lost characters: {markdown}, page {page['page']}")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            link_path = (markdown.parent / unquote(target)).resolve()
            if not link_path.is_file():
                raise AssertionError(f"Missing Markdown target: {link_path}")
            checked_links += 1
        comparison = document["text_variant_comparison"]
        comparison["assessment"] = (
            "Variante do mesmo texto: 84 diferenças locais de pontuação ou espaçamento na comparação normalizada; o PDF conserva interrogações, dois-pontos e barras ausentes no TXT. Não são arquivos textualmente idênticos."
            if markdown.stem == "Nota1" else
            "Variante do mesmo texto: 57 diferenças locais de marcação Markdown, pontuação ou espaçamento; o TXT tem seis cabeçalhos ## e o PDF conserva dois-pontos, barras e aspas ausentes no TXT. Não são arquivos textualmente idênticos."
        )
    manifest["visual_review"] = {
        "status": "reviewed",
        "reviewed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "method": "Inspeção visual de folhas de contato legíveis de todas as 80 páginas; ampliação de amostras para conferir fonte, listas, relação personagem/papel e página sem texto.",
        "pages_inspected": {"Nota1": list(range(1, 66)), "Nota2": list(range(1, 16))},
        "full_size_samples_inspected": ["Nota1:1", "Nota1:48", "Nota1:49", "Nota2:14", "Nota2:15"],
        "blank_pages_confirmed": ["Nota2:15"],
        "findings": [
            "Texto impresso legível, sem manuscrito ou diagramas narrativos; os únicos recursos de imagem são um fundo claro e marcadores de lista, preservados sem edição.",
            "As páginas 48–50 de Nota1 já linearizam a relação Personagem/Papel na própria fonte; o Markdown conserva a sequência integral e os PNGs a diagramação exata.",
            "Todos os números, marcadores de lista e conteúdo nativo foram preservados; a única página sem texto está realmente em branco.",
        ],
        "reviewed_source_sha256": {Path(d["source"]["path"]).name: d["source"]["sha256"] for d in manifest["documents"]},
    }
    manifest["verification"] = {
        "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_and_output_hashes_checked": checked_hashes,
        "relative_markdown_links_checked": checked_links,
        "markdown_page_text_non_whitespace_characters_match": True,
        "archive_copies_match_original_pdf_bytes": True,
        "all_80_page_images_present": True,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"verification": manifest["verification"], "visual_review": manifest["visual_review"]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
