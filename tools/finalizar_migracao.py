"""Gera somente índices e documentação; não reexecuta conversões."""
from pathlib import Path
import json
import re

from fontes_migracao import require_regeneration_opt_in

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'conteudo'
require_regeneration_opt_in(ROOT)


def title(path):
    raw = path.read_text(encoding='utf-8')
    match = re.search(r'(?m)^titulo: (.+)$', raw)
    if not match:
        return path.stem
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return match.group(1).strip('"\'')


def index(path, heading, intro, pages):
    meta = dict(tipo='indice', titulo=heading, campanhas=['fash','glim'], publico=True,
                status='organizado', origens=[], aliases=[])
    front = '\n'.join(k + ': ' + json.dumps(v, ensure_ascii=False) for k, v in meta.items())
    links = '\n'.join('- [[' + p.relative_to(CONTENT).as_posix().removesuffix('.md') + '|' + title(p) + ']]' for p in pages)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + front + '\n---\n\n# ' + heading + '\n\n' + intro + '\n\n' + links + '\n\n[[Inicio|Voltar ao início]]\n', encoding='utf-8')


for folder, heading in [('Personagens','Personagens'),('Faccoes','Facções e grupos'),('Lugares','Lugares'),('Itens','Itens'),('Eventos','Eventos')]:
    directory = CONTENT / folder
    pages = sorted(p for p in directory.glob('*.md') if p.name != 'Indice.md')
    index(directory/'Indice.md', heading, 'Entradas de navegação com referências às fontes. O conteúdo integral permanece disponível no acervo.', pages)

source_indexes = []
for folder, heading in [('Documentos','Documentos integrais'),('Vault','Notas importadas do vault-42'),('Transcricoes','Transcrições'),('Planilhas','Planilhas convertidas')]:
    directory = CONTENT/'Fontes'/folder
    if folder != 'Transcricoes':
        index(directory/'Indice.md', heading,
              'Fontes preservadas em Markdown. Hipóteses, divergências e erros da própria fonte permanecem identificados; a importação não é uma confirmação de todas as afirmações.',
              sorted(p for p in directory.glob('*.md') if p.name != 'Indice.md'))
    source_indexes.append(directory/'Indice.md')
index(CONTENT/'Fontes/Indice.md', 'Acervo de fontes',
      'Documentos integrais que sustentam a base. As cópias exatas dos arquivos de origem ficam em `arquivo/originais/`, fora da pasta de publicação. Variantes que diferem em texto ou apresentação permanecem separadas.',
      source_indexes + [CONTENT/'Fontes/Referencias do vault.md'])

(ROOT/'README.md').write_text('''# Campanha de Fash e Glim

Base pública de conhecimento da campanha. O ponto de entrada é [conteudo/Inicio.md](conteudo/Inicio.md).

A pasta `conteudo/` reúne as notas Markdown e seus anexos. Ela pode ser aberta como um vault no Obsidian. Diários de Glim estão separados por sessão; documentos, transcrições e planilhas convertidas ficam em `Fontes/`.

Os arquivos originais foram preservados em `arquivo/originais/`, com hashes e destinos documentados. Essa pasta é um arquivo de preservação separado do conteúdo da futura página estática. Os links locais para originais dependem dessa estrutura; a distribuição dos downloads no site será definida na etapa de publicação.

## Documentação

- [Formato da base](docs/formato-da-base.md)
- [Relatório da migração](docs/migracao/relatorio.md)
- [Verificação automática](docs/migracao/verificacao.json)
- [Levantamento anterior à migração](docs/levantamento-inicial.md)

O vault-42 e a BASE INICIAL permanecem intactos. O site ainda não foi implementado. Fontes com continuidade ou interpretação incerta foram preservadas e sinalizadas.

## Conferir novamente

`tools/verificar_migracao.py` é uma conferência de leitura: valida hashes, cobertura, estrutura dos metadados, destinos dos links e os corpos dos diários. Execute com o Python do runtime de documentos.

Os demais scripts são os conversores usados nesta migração. Reexecutá-los sobrescreve seus arquivos gerados; não os use sobre notas que já tenham recebido edição manual sem revisar antes.
''', encoding='utf-8')
print(json.dumps({'indices_gerados':9,'markdown_atual':len(list(CONTENT.rglob('*.md')))}, ensure_ascii=True))
