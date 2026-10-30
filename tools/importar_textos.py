"""Importação inicial verificável; nunca escreve nas pastas de origem."""

from pathlib import Path
import hashlib
import json
import re
import shutil

from fontes_migracao import SourceResolver, require_regeneration_opt_in

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'conteudo'
SURVEY = json.loads((ROOT / 'docs/inventario-fontes.json').read_text(encoding='utf-8'))
VAULT = Path(SURVEY['source_root'])
DATE = '2026-10-29'
GENERATED = []
ARCHIVED = []
CONVERSIONS = []
require_regeneration_opt_in(ROOT)
SOURCES = SourceResolver(ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def text(path):
    return path.read_text(encoding='utf-8-sig')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8', newline='\n')
    GENERATED.append(path.relative_to(ROOT).as_posix())


def note(path, title, body, kind='fonte', campaigns=None, origins=None, status='importado', aliases=None, **extra):
    meta = dict(tipo=kind, titulo=title, campanhas=campaigns or [], publico=True,
                status=status, origens=origins or [], aliases=aliases or [])
    meta.update(extra)
    # JSON literals are a deliberately restricted, unambiguous subset of YAML.
    front = '\n'.join(key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in meta.items())
    write(CONTENT / path, '---\n' + front + '\n---\n\n# ' + title + '\n\n' + body.rstrip() + '\n')


def wiki(path, label=None):
    return '[[' + path.removesuffix('.md') + ('|' + label if label else '') + ']]'


def archive(source, label, expected):
    raw = source.read_bytes()
    if sha(raw) != expected:
        raise ValueError('A fonte mudou desde o levantamento: ' + str(source))
    dest = ROOT / 'arquivo/originais' / label
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_bytes() != raw:
        raise ValueError('Cópia preservada divergente: ' + str(dest))
    if not dest.exists():
        shutil.copy2(source, dest)
    assert dest.read_bytes() == raw
    ARCHIVED.append(dict(origem=label, arquivo=dest.relative_to(ROOT).as_posix(), sha256=sha(raw), bytes=len(raw)))


for rec in SURVEY['initial_files']:
    archive(SOURCES.resolve(rec['source'], rec['sha256']), rec['source'], rec['sha256'])
for rec in SURVEY['selected_markdown'] + SURVEY['selected_transcripts'] + SURVEY['selected_support'] + SURVEY['review_before_selection']:
    archive(SOURCES.resolve('vault-42/' + rec['source'], rec['sha256']), 'vault-42/' + rec['source'], rec['sha256'])

vault_notes = SURVEY['selected_markdown'] + SURVEY['review_before_selection']
SOURCE_MAP = {Path(rec['source']).stem: 'Fontes/Vault/Vault - ' + Path(rec['source']).stem for rec in vault_notes}
ENTITIES = {
    'Glim Sombrasselva': 'Personagens/Glim Sombrasselva',
    'Fash Paleskin': 'Personagens/Fash Paleskin',
    'Arkhavel': 'Personagens/Arkhavel', 'Ryld': 'Personagens/Ryld',
    'Lilo Sombrasselva': 'Personagens/Lilo Sombrasselva', 'Piche': 'Personagens/Piche',
    'Ébano': 'Faccoes/Ebano', 'Ebano': 'Faccoes/Ebano',
    'Grimório de Glim': 'Itens/Grimorio de Glim', 'Roda de Estopa': 'Faccoes/Roda de Estopa',
    'Tork': 'Personagens/Tork', 'Folha-Seca': 'Personagens/Folha-Seca', 'Kenku': 'Faccoes/Kenku de Eral',
}
EXTERNAL = set()


def rewrite_links(body):
    def replace(match):
        raw = match.group(1)
        target, _, label = raw.partition('|')
        target, marker, anchor = target.partition('#')
        if not target.strip():
            return match.group(0)
        leaf = Path(target).name.removesuffix('.md')
        destination = ENTITIES.get(leaf) or SOURCE_MAP.get(leaf)
        if not destination:
            EXTERNAL.add(target)
            destination = 'Fontes/Referencias do vault'
        return wiki(destination + (marker + anchor if marker and destination != 'Fontes/Referencias do vault' else ''), label or target)
    body = re.sub(r'\[\[([^\]]+)\]\]', replace, body)
    # The only relative attachment link in these source notes is the S26 transcript.
    body = re.sub(r'\]\(\.\./\.\./98%20Attachments/GLIM%20-%20Sessao%2026%20-%202026-10-20%20-%20Transcricao%20Completa\.txt\)',
                  '](../Transcricoes/Glim%20-%20Sessao%2026%20-%202026-10-20.md)', body)
    return body


def split_front(raw):
    if raw.startswith('---\n'):
        end = raw.find('\n---', 4)
        if end >= 0:
            return raw[4:end], raw[end + 4:].lstrip('\n')
    return '', raw


def fenced(raw, language='text'):
    longest = max((len(x) for x in re.findall(r'`+', raw)), default=0)
    fence = '`' * max(3, longest + 1)
    return fence + language + '\n' + raw.rstrip('\n') + '\n' + fence


def source_note(dest, title, original, origin, campaigns, status='importado', mode='markdown'):
    front, body = split_front(original) if mode == 'markdown' else ('', original)
    if mode == 'markdown':
        converted = rewrite_links(body)
        if origin == 'BASE INICIAL/DIARIO DE RPG (Fash).md':
            # The export marked almost every paragraph H2. Preserve actual entry
            # headings, and make its prose readable without altering any words.
            converted = re.sub(r'(?m)^([*+-] )## ', r'\1', converted)
            converted = re.sub(r'(?m)^## (?!(?:\*\*)?(?:Di[áa]rio|Dia \d|\d{1,2}[/.-]\d{1,2}))', '', converted)
    elif mode == 'texto-integral':
        lines = []
        for line in body.splitlines():
            if re.match(r'^(?:Sess[ãa]o (?:\d+|Solo)\b|\d+\. [A-ZÁÉÍÓÚÂÊÔÃÕÇ])', line) and len(line) < 200:
                line = '## ' + line
            lines.append(line)
        converted = '\n'.join(lines)
    else:
        converted = fenced(body, 'json' if mode == 'json-integral' else 'text')
    from urllib.parse import quote
    archive_path = ROOT / 'arquivo/originais' / origin
    import os
    link = Path(os.path.relpath(archive_path, (CONTENT / dest).parent)).as_posix()
    intro = 'Origem preservada: [arquivo original](' + quote(link, safe='/') + ').\n\n'
    if status == 'revisar_continuidade':
        intro += '> A continuidade deste documento precisa de revisão. Os nomes e afirmações da fonte foram preservados, sem integração automática ao cânone.\n\n'
    if front:
        intro += '<details>\n<summary>Metadados da nota de origem</summary>\n\n' + fenced(front, 'yaml') + '\n\n</details>\n\n'
    content = intro + '<!-- inicio-conteudo-fonte -->\n' + converted.rstrip() + '\n<!-- fim-conteudo-fonte -->'
    note(dest, title, content, campaigns=campaigns, origins=[origin], status=status)
    CONVERSIONS.append(dict(origem=origin, destino='conteudo/' + dest, metodo=mode,
                            texto_origem_sha256=sha(original.encode()), corpo_convertido_sha256=sha(converted.rstrip().encode())))


for rec in vault_notes:
    origin = 'vault-42/' + rec['source']
    stem = Path(rec['source']).stem
    review = rec in SURVEY['review_before_selection']
    campaigns = [] if review else (['fash'] if 'Fash Paleskin - Old Archive' in stem else ['fash', 'glim'] if ('Esclarecimentos' in stem or 'Handoff' in stem) else ['glim'])
    source_note(SOURCE_MAP[stem] + '.md', 'Vault — ' + stem, text(SOURCES.resolve(origin)), origin,
                campaigns, 'revisar_continuidade' if review else 'importado')

BASE_MAP = {
    'BACKGROUND - GLIM SOMBRASSELVA.md': ('Background - Glim Sombrasselva', ['glim']),
    'DIARIO DE RPG (Fash).md': ('Diario - Fash Paleskin', ['fash']),
    'DIÁRIOS - GLIM SOMBRASSELVA.md': ('Diario - Glim Sombrasselva', ['glim']),
    'DIÁRIOS - GLIM SOMBRASSELVA.txt': ('Diario - Glim Sombrasselva - Texto', ['glim']),
    'Dossiê de personagem - Okay dBoa.txt': ('Dossie de personagem - Okay dBoa', ['fash', 'glim']),
    'Personagens e Herois.txt': ('Personagens e Herois', []),
    'RPG - Handoff do cenario para o mestre.md': ('Handoff do cenario', ['fash', 'glim']),
}
for name, (title, campaigns) in BASE_MAP.items():
    source_note('Fontes/Documentos/' + title + '.md', title, text(SOURCES.resolve('BASE INICIAL/' + name)),
                'BASE INICIAL/' + name, campaigns, 'revisar_continuidade' if not campaigns else 'importado',
                'markdown' if name.endswith('.md') else 'texto-integral')

for rec in SURVEY['selected_transcripts']:
    dest = f"Fontes/Transcricoes/Glim - Sessao {rec['session']:02} - {rec['date']}.md"
    source_note(dest, f"Glim — transcrição da sessão {rec['session']} — {rec['date']}",
                text(SOURCES.resolve('vault-42/' + rec['source'])), 'vault-42/' + rec['source'], ['glim'], mode='transcricao-integral')

for rec in SURVEY['selected_support']:
    is_json = rec['source'].endswith('.json')
    dest = 'Fontes/Transcricoes/' + ('Proveniencia - Sessoes 13 a 25.md' if is_json else 'Acervo - Sessoes 13 a 25.md')
    source_note(dest, 'Proveniência — sessões 13 a 25' if is_json else 'Acervo — sessões 13 a 25',
                text(SOURCES.resolve('vault-42/' + rec['source'])), 'vault-42/' + rec['source'], ['glim'], mode='json-integral' if is_json else 'texto-integral')

diary_origin = 'BASE INICIAL/DIÁRIOS - GLIM SOMBRASSELVA.md'
diary = text(SOURCES.resolve(diary_origin))
headings = list(re.finditer(r'(?m)^#{1,6}\s+(?:\*\*)?Sess[ãa]o\s+(\d+|Solo)\b[^\n]*', diary))
SESSIONS = []
for index, match in enumerate(headings):
    identifier = match.group(1)
    heading = match.group().strip('# *').replace('\\-', '-').replace('\\.', '.')
    body = diary[match.end():headings[index + 1].start() if index + 1 < len(headings) else len(diary)].strip()
    day, month = map(int, re.search(r'(\d\d)/(\d\d)', heading).groups())
    # S13+ have dated transcription provenance. Earlier headers only give day/month.
    date_mesa = f'2026-{month:02}-{day:02}'
    year_status = 'documentado' if identifier.isdigit() and int(identifier) >= 13 else 'inferido'
    name = 'Glim - Sessao Solo - 2026-04-22' if identifier.lower() == 'solo' else f'Glim - Sessao {int(identifier):02} - {date_mesa}'
    links = [wiki('Fontes/Documentos/Diario - Glim Sombrasselva', 'Diário integral de origem')]
    if identifier.isdigit() and int(identifier) >= 13:
        links += [wiki(SOURCE_MAP[f'Glim Sombrasselva - Session {identifier} Diary Draft'], 'Análise e preparação do diário'),
                  wiki(f'Fontes/Transcricoes/Glim - Sessao {int(identifier):02} - {date_mesa}', 'Transcrição integral')]
    intro = ' | '.join(links) + '\n\n'
    intro += '> Diário na perspectiva de Glim. O texto foi separado por sessão, sem correções narrativas.\n\n'
    if year_status == 'inferido':
        intro += f'> Data da fonte: {day:02}/{month:02}, sem ano. O ano 2026 usado na organização é inferido da continuidade do acervo e da captura histórica de maio de 2026; ainda não é uma confirmação independente da data.\n\n'
    note('Sessoes/' + name + '.md', heading, intro + '<!-- inicio-diario -->\n' + body + '\n<!-- fim-diario -->',
         kind='sessao', campaigns=['glim'], origins=[diary_origin], sessao='solo' if not identifier.isdigit() else int(identifier), data_mesa=date_mesa,
         data_mesa_original=f'{day:02}/{month:02}', data_mesa_ano_status=year_status)
    SESSIONS.append(dict(sessao=identifier.lower(), data_mesa=date_mesa, data_mesa_ano_status=year_status,
                         destino='conteudo/Sessoes/' + name + '.md', corpo_sha256=sha(body.encode())))

clarification = SOURCE_MAP['2026-10-23 - Esclarecimentos do jogador sobre Fash e Glim']
handoff = SOURCE_MAP['RPG - Handoff do cenario para o mestre']


def entity(path, title, body, sources, campaigns, kind='personagem', aliases=None, status='em_consolidacao'):
    references = '\n\n## Fontes\n\n' + '\n'.join('- ' + wiki(s) for s in sources)
    note(path + '.md', title, body + references, kind=kind, campaigns=campaigns, origins=sources,
         status=status, aliases=aliases)


entity('Personagens/Glim Sombrasselva', 'Glim Sombrasselva',
       'Personagem do jogador na campanha em andamento.\n\n- ' + wiki('Sessoes/Indice', 'Diários por sessão') + '\n- ' + wiki('Fontes/Documentos/Background - Glim Sombrasselva', 'Background integral') + '\n- ' + wiki('Fontes/Planilhas/Glim Sombrasselva', 'Ficha e abas da planilha') + '\n- ' + wiki('Cronologia/Glim Sombrasselva', 'Cronologia da campanha'),
       [SOURCE_MAP['Glim Sombrasselva'], clarification], ['glim'], aliases=['Glim', 'O Magnífico'])
entity('Personagens/Fash Paleskin', 'Fash Paleskin',
       'Personagem do jogador na campanha antiga, situada 70 anos antes da época de Glim. Os esclarecimentos registram que fundou o ' + wiki('Faccoes/Ebano', 'Ébano') + '. Sua sobrevivência na época atual permanece incerta.\n\n- ' + wiki('Fontes/Documentos/Diario - Fash Paleskin', 'Diário integral') + '\n- ' + wiki('Fontes/Planilhas/Fash Paleskin', 'Ficha e abas da planilha') + '\n\nO background de Tinkar Daergel/Eldrosia foi preservado em ' + wiki(SOURCE_MAP['Fash Paleskin']) + ' e aguarda revisão de continuidade.',
       [clarification, SOURCE_MAP['Fash Paleskin - Old Archive']], ['fash', 'glim'], aliases=['Fash'])
entity('Personagens/Okay dBoa', 'Okay d’Boa', 'Companheiro da campanha de Glim. Os esclarecimentos do jogador confirmam que é a reencarnação de ' + wiki('Personagens/Kael') + '.\n\nO ' + wiki('Fontes/Documentos/Dossie de personagem - Okay dBoa', 'dossiê integral') + ' preserva a narrativa, interpretações e questões da fonte.', [clarification, 'Fontes/Documentos/Dossie de personagem - Okay dBoa'], ['fash', 'glim'], aliases=['Okay', "Okay d'Boa"])
entity('Personagens/Kael', 'Kael', 'Personagem da campanha antiga, cuja reencarnação como ' + wiki('Personagens/Okay dBoa', 'Okay') + ' foi confirmada pelo jogador.', [clarification, handoff], ['fash', 'glim'])
entity('Faccoes/Ebano', 'Ébano', 'Organização fundada por ' + wiki('Personagens/Fash Paleskin', 'Fash') + '. Os esclarecimentos confirmam Sociedade das Sombras como outro nome do Ébano.\n\nA pergunta de classificação presente na nota antiga foi superada por essa confirmação. A nota antiga continua preservada como fonte histórica.', [clarification, SOURCE_MAP['Ébano'], handoff], ['fash', 'glim'], kind='faccao', aliases=['Ebano', 'Sociedade das Sombras'])
for original, dest, kind in [
    ('Arkhavel','Personagens/Arkhavel','personagem'), ('Ryld','Personagens/Ryld','personagem'),
    ('Lilo Sombrasselva','Personagens/Lilo Sombrasselva','personagem'), ('Piche','Personagens/Piche','personagem'),
    ('Grimório de Glim','Itens/Grimorio de Glim','item'), ('Roda de Estopa','Faccoes/Roda de Estopa','grupo')]:
    entity(dest, original, 'Esta entrada reúne as referências de ' + original + '. A nota importada e os documentos integrais preservam o conteúdo existente; a consolidação factual está em andamento.', [SOURCE_MAP[original], handoff], ['glim'], kind=kind)
for name in ['Tork','Folha-Seca']:
    entity('Personagens/' + name, name, 'Mencionado nos registros da campanha de Glim. Esta entrada resolve um link existente e reúne as fontes para consolidação posterior; ainda não é uma biografia consolidada.', [SOURCE_MAP['Glim Sombrasselva - Session 18 Diary Draft'], handoff], ['glim'])
entity('Faccoes/Kenku de Eral', 'Kenku de Eral', 'Entrada de navegação para as referências aos Kenku nos registros de Eral. A organização e os integrantes serão detalhados com base nas fontes, sem tratar toda menção à espécie como participação no mesmo grupo.', [SOURCE_MAP['Glim Sombrasselva - Session 18 Diary Draft'], handoff], ['glim'], kind='grupo')
entity('Lugares/Carruan', 'Carruan', 'Identificada como capital real nos esclarecimentos do jogador. A referência a Lazathar como capital no diário de Glim é uma errata documentada; o texto original do diário foi preservado.', [clarification, handoff], ['fash','glim'], kind='lugar')
entity('Lugares/Lazathar', 'Lazathar', 'Nome preservado nos diários. O trecho inicial de Fash é tratado no contexto de sonho indicado pelos esclarecimentos. A menção como capital por Glim foi corrigida pelo jogador para ' + wiki('Lugares/Carruan') + '; essa errata não cria uma segunda capital.', [clarification, handoff], ['fash','glim'], kind='lugar')
entity('Eventos/Noite Eterna', 'Noite Eterna', 'Noite Eterna e Doze Dias Rubros nomeiam o mesmo evento segundo os esclarecimentos do jogador. Sua relação com o encerramento da campanha de Fash está documentada; os detalhes desconhecidos permanecem em aberto.', [clarification, handoff], ['fash','glim'], kind='evento', aliases=['Doze Dias Rubros'])

session_lines = '\n'.join('- ' + wiki(x['destino'].removeprefix('conteudo/'), ('Solo' if x['sessao']=='solo' else 'Sessão ' + x['sessao']) + ' — ' + x['data_mesa']) + (' — ano inferido' if x['data_mesa_ano_status']=='inferido' else '') for x in SESSIONS)
note('Sessoes/Indice.md', 'Sessões de Glim', 'Diários integrais separados por sessão, na ordem da mesa. Datas da mesa não representam datas dentro do mundo. Nas sessões 1–12 e na solo, a fonte informa apenas dia/mês: 2026 é um ano inferido para organização. Nas sessões 13–26, o ano está documentado na proveniência das transcrições.\n\n' + session_lines + '\n\n' + wiki('Fontes/Transcricoes/Indice', 'Transcrições disponíveis'), kind='indice', campaigns=['glim'], origins=[diary_origin], status='organizado')
transcript_lines = '\n'.join('- ' + wiki(f"Fontes/Transcricoes/Glim - Sessao {r['session']:02} - {r['date']}", f"Sessão {r['session']} — {r['date']}") for r in SURVEY['selected_transcripts'])
note('Fontes/Transcricoes/Indice.md', 'Transcrições da campanha de Glim', 'Cópias integrais disponíveis das sessões 13–26. Não há transcrições de 1–12 ou da solo no acervo local consultado.\n\n' + transcript_lines + '\n\n- ' + wiki('Fontes/Transcricoes/Acervo - Sessoes 13 a 25', 'Cobertura e lacunas') + '\n- ' + wiki('Fontes/Transcricoes/Proveniencia - Sessoes 13 a 25', 'Proveniência do pacote'), kind='indice', campaigns=['glim'])
note('Campanhas/Fash.md', 'Campanha de Fash', 'Campanha antiga, situada 70 anos antes da época de Glim.\n\n- ' + wiki('Personagens/Fash Paleskin') + '\n- ' + wiki('Fontes/Documentos/Diario - Fash Paleskin', 'Diário integral') + '\n- ' + wiki('Fontes/Planilhas/Fash Paleskin', 'Ficha e registros da planilha') + '\n- ' + wiki('Cronologia/Fash e Glim', 'Continuidade entre campanhas'), kind='campanha', campaigns=['fash'], origins=['conversa com o jogador — 2026-10-29'])
note('Campanhas/Glim.md', 'Campanha de Glim', 'Campanha em andamento.\n\n- ' + wiki('Personagens/Glim Sombrasselva') + '\n- ' + wiki('Sessoes/Indice', 'Diários por sessão') + '\n- ' + wiki('Fontes/Transcricoes/Indice', 'Transcrições') + '\n- ' + wiki('Cronologia/Glim Sombrasselva', 'Cronologia') + '\n- ' + wiki(SOURCE_MAP['Glim Sombrasselva - Threads'], 'Questões e threads registradas'), kind='campanha', campaigns=['glim'])
note('Cronologia/Fash e Glim.md', 'Fash e Glim — continuidade', 'As campanhas pertencem à mesma continuidade. A época de Fash antecede a de Glim em **70 anos**, conforme informado pelo jogador nesta conversa. Essa referência não fixa datas absolutas para todos os acontecimentos.\n\n- ' + wiki('Campanhas/Fash') + '\n- ' + wiki('Campanhas/Glim') + '\n- ' + wiki('Eventos/Noite Eterna') + '\n- ' + wiki(clarification, 'Esclarecimentos do jogador') + '\n- ' + wiki(handoff, 'Handoff do cenário'), kind='cronologia', campaigns=['fash','glim'], origins=['conversa com o jogador — 2026-10-29', clarification])
note('Cronologia/Glim Sombrasselva.md', 'Glim — cronologia da campanha', 'A ' + wiki(SOURCE_MAP['Glim Sombrasselva - Cronologia da Campanha'], 'cronologia integral importada') + ' distingue estimativas e lacunas. Sua contagem numerada chega aproximadamente ao dia 55 na sessão 19; os marcos das sessões 20–26 ainda precisam de reconciliação para uma contagem atual exata.\n\n' + wiki('Sessoes/Indice', 'Sessões por data da mesa') + '\n\n' + wiki('Cronologia/Fash e Glim', 'Continuidade com Fash'), kind='cronologia', campaigns=['glim'], origins=[SOURCE_MAP['Glim Sombrasselva - Cronologia da Campanha']], status='estimativa_documentada')
note('Fontes/Referencias do vault.md', 'Referências externas ao recorte do vault', 'As notas importadas continham links para índices globais e pastas que também organizam outras campanhas ou o segundo cérebro. Esses destinos foram registrados aqui, sem importar seus conteúdos. As fontes originais preservadas mantêm os links exatos.\n\n' + '\n'.join('- `' + x + '`' for x in sorted(EXTERNAL)) + '\n\n' + wiki('Fontes/Indice', 'Fontes desta campanha'), kind='indice', campaigns=['fash','glim'])
note('Inicio.md', 'Campanha de Fash e Glim', 'Base pública da campanha, com diários, fontes e relações entre as duas épocas.\n\n## Campanhas\n\n- ' + wiki('Campanhas/Fash', 'Fash — campanha antiga') + '\n- ' + wiki('Campanhas/Glim', 'Glim — campanha atual') + '\n- ' + wiki('Cronologia/Fash e Glim', 'Continuidade e intervalo de 70 anos') + '\n\n## Consultar\n\n- ' + wiki('Sessoes/Indice', 'Diários de Glim por sessão') + '\n- ' + wiki('Fontes/Indice', 'Acervo de fontes e documentos') + '\n- ' + wiki('Personagens/Indice', 'Personagens') + '\n- ' + wiki('Faccoes/Indice', 'Facções e grupos') + '\n- ' + wiki('Lugares/Indice', 'Lugares') + '\n- ' + wiki('Itens/Indice', 'Itens') + '\n- ' + wiki('Eventos/Indice', 'Eventos') + '\n\nAs fontes integrais preservam suas perspectivas, hipóteses e divergências. As notas de entidades estão em consolidação e apontam para as evidências disponíveis.', kind='indice', campaigns=['fash','glim'], status='organizado')

manifest = dict(data=DATE, originais=ARCHIVED, conversoes=CONVERSIONS, sessoes=SESSIONS,
                arquivos_gerados=GENERATED, origens_preservadas=len(ARCHIVED), vault_alterado=False,
                base_inicial_alterada=False, fontes_excluidas=False)
(ROOT / 'docs/migracao').mkdir(exist_ok=True, parents=True)
(ROOT / 'docs/migracao/textos.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(originais=len(ARCHIVED), conversoes=len(CONVERSIONS), sessoes=len(SESSIONS), gerados=len(GENERATED)), ensure_ascii=True))
