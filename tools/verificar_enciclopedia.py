"""Confere preservação e consistência estrutural da enciclopédia."""
from pathlib import Path
from datetime import date
import hashlib
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'conteudo'
ERRORS=[]
WARNINGS=[]


def check(value,message):
    if not value: ERRORS.append(message)


def data_iso(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def parse(path):
    raw=path.read_text(encoding='utf-8')
    check(raw.startswith('---\n'),'Metadados ausentes: '+str(path))
    parts=raw.split('---',2)
    if len(parts)<3: return {},raw
    result={}
    for line in parts[1].strip().splitlines():
        check(': ' in line,'Linha de metadado inválida: '+str(path))
        if ': ' not in line: continue
        key,val=line.split(': ',1)
        check(key not in result,'Metadado duplicado: '+str(path)+' '+key)
        try: result[key]=json.loads(val)
        except json.JSONDecodeError: ERRORS.append('Valor fora do subconjunto YAML emitido: '+str(path)+' '+key)
    return result,parts[2]


def plain(body):
    lines=[]; fence=None
    for line in body.splitlines():
        m=re.match(r'^\s*(`{3,}|~{3,})',line)
        if m:
            tok=m[1]
            if fence is None: fence=tok
            elif tok[0]==fence[0] and len(tok)>=len(fence):fence=None
            continue
        if fence is None:
            # Wikilinks can legally contain apostrophe-like backticks in names.
            line=re.sub(r'(\[\[[^\]]+\]\])|(`+).*?\2',lambda m:m[1] or '',line)
            lines.append(line)
    return '\n'.join(lines)


snapshot=json.loads((ROOT/'docs/enciclopedia/estado-fontes.json').read_text(encoding='utf-8'))
correction_file=ROOT/'docs/enciclopedia/correcoes-fontes.json'
correction_records=json.loads(correction_file.read_text(encoding='utf-8')).get('correcoes',[]) if correction_file.exists() else []
corrections={r['path']:r for r in correction_records}
applied_corrections=[]
for rec in snapshot['arquivos']:
    p=ROOT/rec['path']
    check(p.is_file(),'Fonte ausente: '+rec['path'])
    if p.is_file():
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        correction=corrections.get(rec['path'])
        if actual==rec['sha256']:
            continue
        elif correction and correction.get('antes_sha256')==rec['sha256'] and actual==correction.get('depois_sha256'):
            applied_corrections.append(correction)
        else:
            check(False,'Fonte alterada sem correção documentada: '+rec['path'])

registry=json.loads((ROOT/'docs/enciclopedia/registro-entidades.json').read_text(encoding='utf-8'))['entidades']
for row in registry:
    check((CONTENT/(row['destino']+'.md')).is_file(),'Entidade cadastrada sem nota: '+row['destino'])

folders=['Personagens','Lugares','Faccoes','Criaturas','Eventos','Itens','Cronologia','Campanhas','Visoes','Pendencias']
pages=[]
for folder in folders:pages.extend(sorted((CONTENT/folder).rglob('*.md')))
ids={}; alias_map={}; aliases_warning=[]; counts={}; question_count=0; referenced_questions=set(); body_by_path={}; metas={}
for p in pages:
    m,b=parse(p); rel=p.relative_to(CONTENT).as_posix();content=plain(b)
    metas[rel]=m;body_by_path[rel]=content
    check(m.get('publico') is True,'Nota não pública: '+rel)
    for field in ['tipo','titulo','campanhas','status','origens','aliases','atualizado']:
        check(field in m,'Metadado obrigatório ausente: '+rel+' '+field)
    for field in ['campanhas','origens','aliases']:
        check(isinstance(m.get(field),list),'Metadado deveria ser lista: '+rel+' '+field)
    check(data_iso(m.get('atualizado')),'Atualização ausente ou inválida: '+rel)
    check(not re.search(r'@\{[^}]+\}',content),'Marcador editorial não expandido: '+rel)
    check('\ufffd' not in content,'Caractere de substituição novo: '+rel)
    for src in m.get('origens',[]):
        target=src.split('#')[0]
        check((CONTENT/(target if target.endswith('.md') else target+'.md')).is_file(),'Origem sem destino: '+rel+' -> '+src)
    for rawlink in re.findall(r'\[\[([^\]]+)\]\]',content):
        target=rawlink.replace('\\|','|').split('|')[0].split('#')[0]
        if not target:continue
        file=target if target.endswith('.md') else target+'.md'
        check((CONTENT/file).is_file(),'Link enciclopédico sem destino: '+rel+' -> '+target)
        if target.startswith('Pendencias/'):referenced_questions.add(file)
    refs=set(re.findall(r'(?<!^)\[\^([^\]]+)\]',content,re.M))
    definitions=set(re.findall(r'(?m)^\[\^([^\]]+)\]:',content))
    for missing in refs-definitions:ERRORS.append('Nota de rodapé sem definição: '+rel+' -> '+missing)
    if m.get('tipo')=='pendencia':
        question_count+=1
        code=m.get('id','')
        check(bool(re.fullmatch(r'(PC|LG|FC|EV|IT|CR|FT)-\d{3}',code)),'ID inválido: '+rel)
        check(code not in ids,'ID de pendência duplicado: '+code)
        ids[code]=rel
        check(m.get('prioridade') in ['alta','media','baixa'],'Prioridade inválida: '+rel)
        check(bool(m.get('pergunta')) and '?' in m['pergunta'],'Pergunta ausente: '+rel)
        check(bool(m.get('origens')),'Pendência sem fonte: '+rel)
        check(bool(m.get('entidades')),'Pendência sem entidade afetada: '+rel)
        for entity in m.get('entidades',[]):
            check((CONTENT/(entity.removesuffix('.md')+'.md')).is_file(),'Entidade de pendência ausente: '+rel+' -> '+entity)
    elif p.name!='Indice.md' and p.parts[-2] in ['Personagens','Lugares','Faccoes','Criaturas','Eventos','Itens']:
        counts[p.parts[-2]]=counts.get(p.parts[-2],0)+1
        check(len(content.strip())>200,'Entrada sem desenvolvimento: '+rel)
        check(bool(m.get('origens')),'Entrada sem proveniência: '+rel)
        check('[[Fontes/' in content,'Entrada sem citação local: '+rel)
        check('Esta entrada reúne as referências de' not in content,'Placeholder herdado não substituído: '+rel)
        for alias in m.get('aliases',[]):
            key=unicodedata.normalize('NFKC',alias).casefold()
            alias_map.setdefault(key,[]).append(rel)

for key,paths in alias_map.items():
    unique=sorted(set(paths))
    if len(unique)>1:aliases_warning.append(dict(alias=key,notas=unique))
for code,path in ids.items():
    check(path in referenced_questions,'Pendência sem nenhuma referência de navegação: '+code)
    # Affected entities should expose a route to relevant unresolved questions.
    affected=metas[path].get('entidades',[])
    if not any(path.removesuffix('.md') in body_by_path.get(x.removesuffix('.md')+'.md','') for x in affected):
        WARNINGS.append('Pendência citada por navegação, mas sem remissão em entidade afetada: '+code)

report=dict(data=date.today().isoformat(),aprovado=not ERRORS,fontes_preservadas=len(snapshot['arquivos'])-len(applied_corrections),
            fontes_verificadas=len(snapshot['arquivos']),correcoes_apresentacao=applied_corrections,
            entidades_do_cadastro=len(registry),entidades_detalhadas=counts,total_entidades=sum(counts.values()),
            pendencias=question_count,ids_unicos=len(ids),aliases_compartilhados=aliases_warning,
            erros=ERRORS,avisos=WARNINGS,
            limites=['Citações e destinos foram verificados estruturalmente; a verificação automática não prova todas as interpretações narrativas.',
                     'Leitura primária seletiva e uso de síntese são discriminados nos manifestos de domínio.',
                     'O controle de YAML aqui é do subconjunto JSON-compatível emitido para as novas notas.'])
(ROOT/'docs/enciclopedia/verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(aprovado=report['aprovado'],fontes_verificadas=report['fontes_verificadas'],
                      fontes_identicas=report['fontes_preservadas'],correcoes_apresentacao=len(applied_corrections),entidades=counts,
                      pendencias=question_count,aliases_compartilhados=aliases_warning,erros=ERRORS,avisos=WARNINGS),ensure_ascii=True,indent=2))
raise SystemExit(0 if not ERRORS else 1)
