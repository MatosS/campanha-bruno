"""Escrita de notas no formato restrito e verificável da enciclopédia."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONTEUDO = ROOT/'conteudo'

FONTES = {
    'H': 'Fontes/Vault/Vault - RPG - Handoff do cenario para o mestre',
    'J': 'Fontes/Vault/Vault - 2026-10-23 - Esclarecimentos do jogador sobre Fash e Glim',
    'F': 'Fontes/Documentos/Diario - Fash Paleskin',
    'B': 'Fontes/Documentos/Background - Glim Sombrasselva',
    'G': 'Fontes/Documentos/Diario - Glim Sombrasselva',
    'OK': 'Fontes/Documentos/Dossie de personagem - Okay dBoa',
    'PH': 'Fontes/Documentos/Personagens e Herois',
    'TIM': 'Fontes/Documentos/Resumo detalhado',
    'XF': 'Fontes/Planilhas/Fash Paleskin',
    'XG': 'Fontes/Planilhas/Glim Sombrasselva',
    'C': 'Fontes/Vault/Vault - Glim Sombrasselva - Cronologia da Campanha',
}
_inventario = json.loads((ROOT/'docs/inventario-fontes.json').read_text(encoding='utf-8'))
for _rec in _inventario['selected_transcripts']:
    FONTES[f"T{_rec['session']}"] = f"Fontes/Transcricoes/Glim - Sessao {_rec['session']:02} - {_rec['date']}"
_textos = json.loads((ROOT/'docs/migracao/textos.json').read_text(encoding='utf-8'))
for _rec in _textos['sessoes']:
    FONTES['S' + _rec['sessao'].upper()] = _rec['destino'].removeprefix('conteudo/').removesuffix('.md')


def link(destino, rotulo=None):
    return '[[' + destino.removesuffix('.md') + ('|' + rotulo if rotulo else '') + ']]'


def fonte(codigo, rotulo=None, secao=None):
    destino = FONTES.get(codigo, codigo)
    return link(destino + ('#' + secao if secao else ''), rotulo or codigo)


def escrever(caminho, titulo, tipo, campanhas, texto, fontes, aliases=None, status='documentado_parcial', **props):
    path = CONTEUDO/caminho
    if path.suffix != '.md':
        path = path.with_suffix('.md')
    path = path.resolve()
    path.relative_to(CONTEUDO.resolve())
    if any(x in {'Fontes','Anexos','Sessoes'} for x in path.relative_to(CONTEUDO).parts):
        raise ValueError('As fontes são somente leitura nesta etapa: ' + str(path))
    meta = dict(tipo=tipo,titulo=titulo,campanhas=campanhas,publico=True,status=status,
                origens=[FONTES.get(f,f).removesuffix('.md') for f in fontes],aliases=aliases or [],atualizado='2026-10-29')
    meta.update(props)
    front = '\n'.join(k + ': ' + json.dumps(v,ensure_ascii=False) for k,v in meta.items())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('---\n' + front + '\n---\n\n# ' + titulo + '\n\n' + texto.rstrip() + '\n',encoding='utf-8')
    return path.relative_to(CONTEUDO).as_posix()


def pendencia(codigo, titulo, categoria, campanhas, pergunta, contexto, fontes, entidades, prioridade='media', natureza='lacuna'):
    safe = re.sub(r'[<>:"/\\|?*]', '', titulo).strip().rstrip('.')
    destino = f'Pendencias/{categoria}/{codigo} - {safe}'
    corpo = ('## Pergunta para a sabatina\n\n' + pergunta + '\n\n## Contexto e evidências\n\n' + contexto
             + '\n\n## Entidades afetadas\n\n' + '\n'.join('- ' + link(x) for x in entidades)
             + '\n\n## Fontes\n\n' + '\n'.join('- ' + fonte(x) for x in fontes)
             + '\n\n## Resposta futura\n\nAinda não respondida. Registrar quem confirmou, a data e o alcance da resposta antes de atualizar as notas relacionadas.')
    escrever(destino,codigo + ' — ' + titulo,'pendencia',campanhas,corpo,fontes,status='aberta',
             id=codigo,categoria=categoria,prioridade=prioridade,natureza=natureza,pergunta=pergunta,entidades=entidades)
    return destino
