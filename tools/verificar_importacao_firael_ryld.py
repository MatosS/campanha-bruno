"""Verifica originais, pacote OOXML, texto e Markdown sem reconverter fontes."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET
import hashlib,json,re,html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/importacoes/2026-10-30-firael-ryld'
sha=lambda b:hashlib.sha256(b).hexdigest()
errors=[]
def check(ok,message):
    if not ok:errors.append(message)
def visible(markdown):
    # Protege caracteres literais antes de retirar marcações da conversão.
    protected={}
    def hold(m):
        key=chr(0xE000+len(protected));protected[key]=m[1];return key
    value=re.sub(r'\\(.)',hold,markdown)
    value=re.sub(r'^(?:#{1,6} |\s*(?:- |\d+\. ))','',value)
    value=value.replace('<br>\n','\n')
    value=re.sub(r'</?(?:u|mark)(?: [^>]*)?>','',value)
    value=value.replace('**','').replace('_','')
    for key,char in protected.items():value=value.replace(key,char)
    return value

def main():
    manifest=json.loads((OUT/'manifesto.json').read_text(encoding='utf-8'))
    total=0;results=[]
    for rec in manifest['documentos']:
        archive=ROOT/rec['original'];source=Path(rec['origem']);audit=ROOT/rec['auditoria'];output=ROOT/rec['saida']
        check(sha(archive.read_bytes())==rec['sha256'],'Hash do original: '+str(archive))
        if source.exists():check(sha(source.read_bytes())==rec['sha256'],'Arquivo fornecido alterado: '+str(source))
        check(sha(audit.read_bytes())==rec['auditoria_sha256'],'Auditoria alterada: '+str(audit))
        check(sha(output.read_bytes())==rec['saida_sha256'],'Conversão alterada: '+str(output))
        records=json.loads(audit.read_text(encoding='utf-8'))
        with ZipFile(archive) as z:
            for name,digest in rec['partes_sha256'].items():check(sha(z.read(name))==digest,'Parte OOXML: '+name)
            x=ET.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            ps=x.xpath('/w:document/w:body/w:p',namespaces=ns)
            check(len(ps)==len(records)==rec['paragrafos'],'Contagem de parágrafos: '+rec['saida'])
            for p,item in zip(ps,records):
                tokens=p.xpath('.//w:t | .//w:br',namespaces=ns)
                raw=''.join((e.text or '') if e.tag.endswith('}t') else '\n' for e in tokens)
                check(raw==item['texto'],f"Texto P{item['paragrafo']}: {rec['saida']}")
                if not item['separadores']:
                    check(visible(item['markdown'])==raw,f"Markdown P{item['paragrafo']}: {rec['saida']}")
        body=output.read_text(encoding='utf-8').split('<!-- inicio-conteudo-fonte -->\n\n',1)[1].split('<!-- fim-conteudo-fonte -->',1)[0]
        check(body==''.join(item['markdown']+'\n\n' for item in records),'Ordem ou completude Markdown: '+rec['saida'])
        total+=len(records)
        results.append({'saida':rec['saida'],'paragrafos':len(records),'hash_original':rec['sha256']})
    comparison=json.loads((OUT/'comparacao.json').read_text(encoding='utf-8'))
    check(len(comparison['diferencas_narrativas'])==3,'Diferenças narrativas não preservadas')
    check(comparison['ryld_capitulo_6_repetido_identico'],'Capítulo repetido não preservado')
    report={'data':'2026-10-30','aprovado':not errors,'documentos':results,'paragrafos_verificados':total,'originais_intactos':not errors,'erros':errors,'limites':['Verificação textual e estrutural; não declara equivalência visual de paginação DOCX e Markdown.','A perspectiva narrativa não comprova todas as alegações feitas por personagens.']}
    (OUT/'verificacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'aprovado':not errors,'documentos':len(results),'paragrafos':total,'erros':errors},ensure_ascii=False))
    raise SystemExit(0 if not errors else 1)

if __name__=='__main__':main()
