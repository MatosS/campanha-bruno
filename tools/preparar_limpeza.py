"""Prepara, sem escrever no vault externo, a limpeza explicitamente autorizada."""
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path('C:/sources/vault-42')
OUT = ROOT / 'docs/limpeza'
POINTER = 'Campanha de Fash e Glim - Base externa'
POINTER_REL = f'30 Areas/RPG/{POINTER}.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def active_sub(text, pattern, replace):
    """Protege exemplos em código; mantém links funcionais no frontmatter."""
    parts = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`)', text)
    return ''.join(re.sub(pattern, replace, part) if i % 2 == 0 else part
                   for i, part in enumerate(parts))


def main():
    candidates = json.loads((ROOT / 'docs/auditoria-exclusao/candidatos.json').read_text(encoding='utf-8'))
    assert [len(candidates['arquivos'][k]) for k in ('BASE INICIAL', 'vault-42')] == [12, 53]
    records = [x for group in candidates['arquivos'].values() for x in group]
    for item in records:
        source = (VAULT / item['origem'][9:] if item['origem'].startswith('vault-42/')
                  else ROOT / item['origem'])
        archive = ROOT / item['copia_preservada']
        assert sha(source) == sha(archive) == item['sha256'], item['origem']
    expected = {x['origem'] for x in candidates['arquivos']['BASE INICIAL']}
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'BASE INICIAL').rglob('*') if p.is_file()}
    assert actual == expected, (actual - expected, expected - actual)
    protected = {}
    for folder in ('arquivo/originais', 'conteudo/Fontes', 'conteudo/Anexos'):
        for p in (ROOT / folder).rglob('*'):
            if p.is_file() and p.name != 'Indice.md':
                protected[p.relative_to(ROOT).as_posix()] = sha(p)
    save_json(OUT / 'protecao-antes.json', protected)
    conversion = {x['origem']: x['destino'] for x in json.loads((ROOT / 'docs/migracao/textos.json').read_text(encoding='utf-8'))['conversoes']}
    selected = {x['origem'][9:]: x for x in candidates['arquivos']['vault-42']}
    names = {Path(rel).stem: rel for rel in selected}
    aliases = {}
    for rel in selected:
        if not rel.endswith('.md'):
            continue
        text = (VAULT / rel).read_text(encoding='utf-8-sig')
        head = text.split('---', 2)[1] if text.startswith('---') else ''
        match = re.search(r'^aliases:[ \t]*\n((?:[ \t]+.*\n)*)', head, re.M)
        if match:
            for line in match[1].splitlines():
                alias = line.strip().removeprefix('- ').strip('\"\'')
                aliases.setdefault(alias, rel)
    def lookup(value):
        name = value.replace('\\', '/').removesuffix('.md')
        return selected.get(name + '.md') and name + '.md' or names.get(Path(name).name) or aliases.get(name)

    patches = []
    for path in VAULT.rglob('*.md'):
        rel = path.relative_to(VAULT).as_posix()
        if rel in selected or rel.startswith(('.git/', '.obsidian/', 'docs/', '00 System/')):
            continue
        original = path.read_bytes()
        text = original.decode('utf-8-sig')
        newline = '\r\n' if '\r\n' in text else '\n'
        text = text.replace('\r\n', '\n')
        changes = []
        def wiki(match):
            target, sep, label = match[1].partition('|')
            name, anchor_sep, anchor = target.partition('#')
            dest = lookup(name)
            if not dest:
                return match[0]
            visible = label if sep else name
            changes.append({'antes': match[0], 'origem': dest, 'fragmento_anterior': anchor if anchor_sep else None})
            return f'[[{POINTER}#{Path(dest).stem}|{visible}]]'
        changed = active_sub(text, r'\[\[([^\]\n]+)\]\]', wiki)
        def markdown(match):
            raw = match[2].strip('<>')
            target = unquote(raw.split('#', 1)[0])
            if re.match(r'^[a-zA-Z]+:', target):
                return match[0]
            resolved = (path.parent / target).resolve()
            try:
                old = resolved.relative_to(VAULT).as_posix()
            except ValueError:
                return match[0]
            if old not in selected:
                return match[0]
            changes.append({'antes': match[0], 'origem': old})
            target_url = quote(os.path.relpath(VAULT / POINTER_REL, path.parent).replace('\\', '/'), safe='/')
            target_url += '#' + quote(Path(old).stem, safe='')
            return f'[{match[1]}]({target_url})'
        changed = active_sub(changed, r'\[([^\]\n]+)\]\((<[^>\n]+>|[^)\n]+)\)', markdown)
        if changed == text:
            continue
        output = changed.replace('\n', newline).encode('utf-8')
        if original.startswith(b'\xef\xbb\xbf'):
            output = b'\xef\xbb\xbf' + output
        staged = OUT / 'patches/vault-42' / rel
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(output)
        before = OUT / 'antes-links/vault-42' / rel
        before.parent.mkdir(parents=True, exist_ok=True)
        before.write_bytes(original)
        patches.append({'caminho': rel, 'antes_sha256': hashlib.sha256(original).hexdigest(),
                        'depois_sha256': hashlib.sha256(output).hexdigest(), 'links': changes})

    props = {'type': 'note', 'status': 'active', 'created': '2026-10-29', 'updated': '2026-10-29',
             'aliases': [], 'tags': ['rpg', 'migration'], 'related': ['[[RPG]]']}
    pointer = '---\n' + ''.join(f'{k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in props.items()) + '---\n\n'
    pointer += f'# {POINTER}\n\nA campanha de Fash e Glim foi transferida para a base pública dedicada. O índice de [[RPG]] continua reunindo as outras campanhas e referências pessoais.\n\n'
    def external(target):
        assert (ROOT / target).is_file(), target
        return quote(os.path.relpath(ROOT / target, VAULT / '30 Areas/RPG').replace('\\', '/'), safe='/')
    pointer += f'- [Abrir a base de conhecimento]({external("conteudo/Inicio.md")})\n'
    pointer += f'- [Pendências e sabatina]({external("conteudo/Pendencias/Indice.md")})\n\n'
    pointer += 'Os links históricos abaixo mantêm o nome da nota de origem. Cada seção leva ao conteúdo convertido e à cópia integral preservada. Caminhos mencionados como texto nos registros antigos descrevem o estado anterior à migração.\n\n'
    for rel, item in selected.items():
        pointer += f'## {Path(rel).stem}\n\nOrigem anterior: `{rel}`.\n\n'
        dest = conversion.get(item['origem'])
        if dest:
            pointer += f'- [Consultar fonte convertida]({external(dest)})\n'
        pointer += f'- [Original preservado]({external(item["copia_preservada"])})\n\n'
    staged = OUT / 'patches/vault-42' / POINTER_REL
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(pointer.rstrip() + '\n', encoding='utf-8')
    assert not (VAULT / POINTER_REL).exists()
    patches.append({'caminho': POINTER_REL, 'antes_sha256': None, 'depois_sha256': sha(staged), 'links': []})
    session_rel = '60 Daily/2026-10-29 Agent Session - RPG Base Migration Cleanup.md'
    session_props = dict(props, type='agent-session', status='review', agent='Codex',
                         task='Remover as 53 origens RPG auditadas e corrigir links para a base dedicada.',
                         files_created=[POINTER_REL], files_edited=[p['caminho'] for p in patches if p['antes_sha256']],
                         sources=['Autorização explícita do usuário em 2026-10-29', 'campanha-bruno/docs/auditoria-exclusao/candidatos.json'])
    session = '---\n' + ''.join(f'{k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in session_props.items()) + '---\n\n'
    session += '# Agent Session - 2026-10-29 - RPG Base Migration Cleanup\n\n## Request\n\nExcluir exatamente os 53 arquivos auditados de Fash e Glim, depois de conferir as cópias integrais, e ajustar os links afetados.\n\n## Context Read\n\n- AGENTS.md, Vault Guide, Schemas, Skills, obsidian-vault-42, Agent Vault Maintenance e Template - Agent Session.\n- Lista auditada, manifests de migração e notas com links afetados.\n\n## Changes\n\n'
    session += f'- Removidas 53 origens auditadas; cópias integrais preservadas em `C:/sources/campanha-bruno/arquivo/originais/vault-42`.\n- Links de {len(patches)-1} notas redirecionados para [[{POINTER}]], com seção individual para cada origem.\n- Fontes convertidas e anexos permanecem na base dedicada.\n\n## Sources\n\n- Autorização explícita do usuário nesta conversa.\n- Manifest e registro de execução: `C:/sources/campanha-bruno/docs/limpeza/`.\n\n## Decisions\n\n- Manter as outras campanhas, índices gerais, logs históricos, export ZIP e handoff TXT fora da lista.\n- Preservar o texto histórico; ajustar somente os links funcionais afetados.\n\n## Follow-Ups\n\n- Continuar a sabatina na base dedicada e preparar a futura wiki pública.\n'
    staged = OUT / 'patches/vault-42' / session_rel
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(session, encoding='utf-8')
    assert not (VAULT / session_rel).exists()
    patches.append({'caminho': session_rel, 'antes_sha256': None, 'depois_sha256': sha(staged), 'links': []})
    save_json(OUT / 'links-vault.json', {'arquivos': patches, 'arquivos_existentes_alterados': len(patches)-2,
              'links_redirecionados': sum(len(p['links']) for p in patches), 'nota_destino': POINTER_REL})
    print(json.dumps({'copias_conferidas': len(records), 'arquivos_protegidos': len(protected),
          'notas_vault_a_ajustar': len(patches)-2, 'links': sum(len(p['links']) for p in patches)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
