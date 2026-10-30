"""Confere a remoção autorizada, a preservação e os links redirecionados."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path('C:/sources/vault-42')
OUT = ROOT / 'docs/limpeza'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))


def active_parts(text):
    return re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`)', text)[::2]


def main():
    errors = []
    execution = read('execucao.json')
    plan = read('links-vault.json')
    baseline = read('protecao-antes.json')
    assert execution['estado'] == 'concluida'
    assert len(execution['arquivos']) == 65
    archive_ok = removed_ok = preserved_ok = patch_ok = external_ok = wiki_ok = 0
    for item in execution['arquivos']:
        source = VAULT / item['origem'][9:] if item['origem'].startswith('vault-42/') else ROOT / item['origem']
        if source.exists():
            errors.append(f'Origem ainda presente: {item["origem"]}')
        else:
            removed_ok += 1
        copy = ROOT / item['copia_preservada']
        if copy.is_file() and sha(copy) == item['sha256']:
            archive_ok += 1
        else:
            errors.append(f'Cópia ausente ou divergente: {item["copia_preservada"]}')
    if (ROOT / 'BASE INICIAL').exists():
        errors.append('BASE INICIAL ainda presente')
    for name, expected in baseline.items():
        p = ROOT / name
        if p.is_file() and sha(p) == expected:
            preserved_ok += 1
        else:
            errors.append(f'Arquivo protegido alterado: {name}')
    pointer = VAULT / plan['nota_destino']
    pointer_text = pointer.read_text(encoding='utf-8')
    pointer_title = pointer.stem
    headings = set(re.findall(r'^## (.+)$', pointer_text, re.M))
    for patch in plan['arquivos']:
        p = VAULT / patch['caminho']
        if not p.is_file() or sha(p) != patch['depois_sha256']:
            errors.append(f'Patch divergente: {patch["caminho"]}')
            continue
        patch_ok += 1
        text = p.read_text(encoding='utf-8-sig')
        if patch['antes_sha256'] is None:
            header = text.split('---', 2)[1]
            props = {line.split(':', 1)[0]: json.loads(line.split(':', 1)[1].strip())
                     for line in header.splitlines() if ':' in line}
            required = {'type', 'status', 'created', 'updated', 'aliases', 'tags', 'related'}
            if not required <= props.keys() or '[[RPG]]' not in props['related']:
                errors.append(f'Metadados incompletos: {patch["caminho"]}')
        else:
            before = (OUT / 'antes-links/vault-42' / patch['caminho']).read_text(encoding='utf-8-sig')
            # A transformação insere apenas letras, espaços e delimitadores dentro
            # das mesmas strings YAML. Estrutura/aspas/indentação ficam inalteradas.
            old_header = before.split('---', 2)[1]
            new_header = text.split('---', 2)[1]
            normalize = lambda s: re.sub(r'\[\[[^\]\n]+\]\]', 'WIKILINK', s).replace('\r\n', '\n')
            if normalize(old_header) != normalize(new_header):
                errors.append(f'Estrutura YAML alterada: {patch["caminho"]}')
        for part in active_parts(text):
            for link in re.findall(r'\[\[([^\]\n]+)\]\]', part):
                dest = link.split('|', 1)[0]
                if dest.startswith(pointer_title + '#'):
                    if dest.split('#', 1)[1] not in headings:
                        errors.append(f'Seção inexistente: {patch["caminho"]}: {dest}')
                    else:
                        wiki_ok += 1
    for raw in re.findall(r'\]\(([^)\n]+)\)', pointer_text):
        dest = (pointer.parent / unquote(raw)).resolve()
        if dest.is_file():
            external_ok += 1
        else:
            errors.append(f'Link externo da ponte ausente: {raw}')
    selected = {Path(x['origem']).stem for x in execution['arquivos'] if x['origem'].startswith('vault-42/')}
    for p in VAULT.rglob('*.md'):
        rel = p.relative_to(VAULT).as_posix()
        if rel.startswith(('.git/', '.obsidian/', 'docs/', '00 System/')):
            continue
        for part in active_parts(p.read_text(encoding='utf-8-sig')):
            for link in re.findall(r'\[\[([^\]\n]+)\]\]', part):
                dest = link.split('|', 1)[0].split('#', 1)[0]
                if Path(dest.removesuffix('.md')).name in selected:
                    errors.append(f'Link ativo para origem removida: {rel}: {link}')
    report = {'aprovado': not errors, 'origens_removidas': removed_ok,
              'originais_preservados_conferidos': archive_ok,
              'fontes_anexos_originais_sem_alteracao': preserved_ok,
              'arquivos_protegidos_total': len(baseline), 'patches_vault_conferidos': patch_ok,
              'wikilinks_redirecionados_conferidos': wiki_ok,
              'links_da_ponte_conferidos': external_ok, 'erros': errors}
    (OUT / 'verificacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
