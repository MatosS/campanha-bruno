"""Importação auditável dos quatro DOCX recebidos em 30/10/2026.

Não executa instruções dos documentos. Preserva cada pacote e cada parágrafo,
inclusive repetições; só interpreta recursos OOXML explicitamente cobertos.
"""
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from lxml import etree as ET
from urllib.parse import quote
import hashlib
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path('C:/Users/guilh/OneDrive/Área de Trabalho')
OUT = ROOT / 'docs/importacoes/2026-10-30-firael-ryld'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
FILES = [
    ('Diário de Firael.docx', 'Diario de Firael - versao completa', ['fash']),
    ('Diário de Firael (1).docx', 'Diario de Firael - variante 1', ['fash']),
    ('Diário de Firael (2).docx', 'Diario de Firael - variante 2', ['fash']),
    ('Préludio Ryld.docx', 'Preludio de Ryld', ['glim']),
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def text(element):
    return ''.join(e.text or '' if ET.QName(e).localname == 't' else '\n'
                   for e in element.iter() if ET.QName(e).localname in ('t', 'br'))

def escape(value):
    return re.sub(r'([\\`*_\[\]|<>])', r'\\\1', value)

def on(run, name):
    prop = run.find('w:rPr/w:'+name, NS)
    return prop is not None and prop.get('{'+W+'}val', 'true') not in ('false','0','off','none')

def inline(p):
    groups=[]
    for r in p.findall('w:r', NS):
        value=text(r)
        if not value:
            continue
        high=r.find('w:rPr/w:highlight',NS)
        fmt=(on(r,'b'),on(r,'i'),on(r,'u'),high.get('{'+W+'}val') if high is not None else None)
        if groups and groups[-1][0]==fmt:
            groups[-1][1]+=value
        else:
            groups.append([fmt,value])
    assert ''.join(value for _,value in groups)==text(p)
    result=[]
    for (bold,italic,under,highlight),value in groups:
        lead,core,tail=re.fullmatch(r'(\s*)(.*?)(\s*)',value,re.S).groups()
        value=escape(core)
        if bold and core: value='**'+value+'**'
        if italic and core: value='_'+value+'_'
        if under and core: value='<u>'+value+'</u>'
        if highlight and core: value='<mark data-word-color="'+html.escape(highlight)+'">'+value+'</mark>'
        result.append(lead+value+tail)
    return ''.join(result)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for filename,title,campaigns in FILES:
        source=INPUT/filename
        data=source.read_bytes()
        archive=ROOT/'arquivo/originais/importacoes-2026-10-30'/filename
        archive.parent.mkdir(parents=True,exist_ok=True)
        if archive.exists():
            assert archive.read_bytes()==data, 'Original já arquivado diverge'
        else:
            shutil.copy2(source,archive)
        assert sha(archive.read_bytes())==sha(data)
        with ZipFile(archive) as z:
            x=ET.fromstring(z.read('word/document.xml'))
            tags=Counter(ET.QName(e).localname for e in x.iter())
            allowed={'document','body','p','pPr','rPr','rFonts','b','bCs','sz','szCs','highlight','r','t','pict','rect','u','br','lastRenderedPageBreak','numPr','ilvl','numId','i','iCs','sectPr','pgSz','pgMar','cols','docGrid','proofErr'}
            assert not (set(tags)-allowed), set(tags)-allowed
            assert not [n for n in z.namelist() if re.search(r'word/(media/|embeddings/|header|footer|footnotes|endnotes|comments)',n)]
            rects=x.xpath('//*[local-name()="rect"]')
            assert all(e.get('{urn:schemas-microsoft-com:office:office}hr')=='t' for e in rects)
            assert all(len(p)==1 and ET.QName(p[0]).localname=='rect' for p in x.xpath('//w:pict',namespaces=NS))
            nums={}
            if 'word/numbering.xml' in z.namelist():
                numbering=ET.fromstring(z.read('word/numbering.xml'))
                for n in numbering.findall('w:num',NS):
                    aid=n.find('w:abstractNumId',NS).get('{'+W+'}val')
                    abstract=numbering.xpath('./w:abstractNum[@w:abstractNumId="'+aid+'"]',namespaces=NS)[0]
                    nums[n.get('{'+W+'}numId')]={l.get('{'+W+'}ilvl'):{'format':l.find('w:numFmt',NS).get('{'+W+'}val'),'start':int(l.find('w:start',NS).get('{'+W+'}val'))} for l in abstract.findall('w:lvl',NS)}
            records=[];counters={};parts={n:sha(z.read(n)) for n in z.namelist()}
            body=x.find('w:body',NS)
            assert all(ET.QName(e).localname in ('p','sectPr') for e in body)
            for i,p in enumerate(body.findall('w:p',NS),1):
                assert all(ET.QName(e).localname in ('pPr','r','proofErr') for e in p)
                raw=text(p);md=inline(p);prefix=''
                if raw.startswith(('Diário de Firael','Capítulo ')):
                    prefix='## '
                elif raw.strip() and len(raw)<120:
                    runs=[r for r in p.findall('w:r',NS) if text(r).strip()]
                    if runs and all(on(r,'b') for r in runs):prefix='### '
                num=p.find('w:pPr/w:numPr',NS)
                numdef=None
                if num is not None:
                    nid=num.find('w:numId',NS).get('{'+W+'}val');level=num.find('w:ilvl',NS).get('{'+W+'}val');numdef=nums[nid][level]
                    key=(nid,level);counters[key]=counters.get(key,numdef['start']-1)+1
                    assert numdef['format'] in ('bullet','decimal')
                    prefix='  '*int(level)+('- ' if numdef['format']=='bullet' else str(counters[key])+'. ')
                hrs=len(p.findall('.//w:pict',NS))
                if hrs:
                    assert not raw.strip(), 'Separador com texto exige ajuste'
                    md='\n\n'.join('---' for _ in range(hrs))
                # HTML br conserva quebras internas; parágrafos mantêm a ordem.
                md=prefix+md.replace('\n','<br>\n') if not hrs else md
                records.append({'paragrafo':i,'texto':raw,'markdown':md,'lista':numdef,'separadores':hrs})
            output=ROOT/'conteudo/Fontes/Documentos'/(title+'.md')
            url=quote('../../../'+archive.relative_to(ROOT).as_posix(),safe='/.')
            header={'tipo':'fonte','titulo':title,'campanhas':campaigns,'publico':True,'status':'importado_com_perspectiva','origens':[str(source)],'aliases':[],'atualizado':'2026-10-30'}
            lines=['---']+[k+': '+json.dumps(v,ensure_ascii=False) for k,v in header.items()]+['---','','# '+title,'',f'[Original DOCX preservado]({url}). Importado em 30/10/2026. A fonte conserva a perspectiva do narrador, grafias, datas, repetições e anotações editoriais; datas dos cabeçalhos não são tratadas como anos do cenário.','','<!-- inicio-conteudo-fonte -->','']
            for record in records:
                lines.extend([record['markdown'],''])
            lines.extend(['<!-- fim-conteudo-fonte -->',''])
            output.write_text('\n'.join(lines),encoding='utf-8')
            assert len(records)==tags['p']
            assert sum(r['separadores'] for r in records)==tags['pict']
            audit=OUT/(title+' - paragrafos.json');save(audit,records)
            manifest.append({'origem':str(source),'original':archive.relative_to(ROOT).as_posix(),'sha256':sha(data),'saida':output.relative_to(ROOT).as_posix(),'saida_sha256':sha(output.read_bytes()),'auditoria':audit.relative_to(ROOT).as_posix(),'auditoria_sha256':sha(audit.read_bytes()),'paragrafos':len(records),'caracteres_textuais':sum(len(r['texto']) for r in records),'quebras_internas':tags['br'],'separadores_horizontais':tags['pict'],'recursos_ooxml':dict(tags),'partes_sha256':parts,'texto_preservado':True})
    save(OUT/'manifesto.json',{'data':'2026-10-30','documentos':manifest,'politica':'Originais intactos; parágrafos e repetições preservados; interpretações curadas separadamente.'})
    print(json.dumps([{k:d[k] for k in ('saida','paragrafos','caracteres_textuais','quebras_internas','texto_preservado')} for d in manifest],ensure_ascii=False))

if __name__=='__main__':
    main()
