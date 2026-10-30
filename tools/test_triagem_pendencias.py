"""Regressões da fila: desconhecimento não vira pergunta automaticamente."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]

class TriagemDaSabatina(unittest.TestCase):
    def test_fila_exige_relevancia_e_respeita_fontes_em_espera(self):
        with tempfile.TemporaryDirectory(prefix='.teste-triagem-',dir=ROOT/'tools') as tmp:
            root=Path(tmp);(root/'tools').mkdir()
            for name in ['indexar_enciclopedia.py','enciclopedia_comum.py','fila_revisao.py']:
                shutil.copyfile(ROOT/'tools'/name,root/'tools'/name)
            for folder in ['docs/migracao','docs/enciclopedia','conteudo/Personagens',
                           'conteudo/Lugares','conteudo/Faccoes','conteudo/Criaturas',
                           'conteudo/Eventos','conteudo/Itens','conteudo/Cronologia',
                           'conteudo/Campanhas','conteudo/Visoes']:
                (root/folder).mkdir(parents=True,exist_ok=True)
            (root/'docs/inventario-fontes.json').write_text('{"selected_transcripts": []}',encoding='utf-8')
            (root/'docs/migracao/textos.json').write_text('{"sessoes": []}',encoding='utf-8')
            shutil.copytree(ROOT/'conteudo/Pendencias',root/'conteudo/Pendencias')
            cases={
                'EV-001':('lacuna_de_sequencia','perguntar',True,'alta'),
                'PC-021':('lacuna_de_sequencia','conferir_fontes',False,'media'),
                'PC-006':('contradicao','aguardar_fonte',False,'media'),
                'LG-015':('detalhe_sem_impacto','nao_perguntar',True,'baixa'),
                'PC-030':('em_aberto','nao_perguntar',True,'baixa'),
                'IT-005':('contradicao','perguntar',True,'alta'),
            }
            originals={}
            for p in (root/'conteudo/Pendencias').rglob('*.md'):
                raw=p.read_text(encoding='utf-8')
                if 'tipo: "pendencia"' not in raw:continue
                _,front,body=raw.split('---',2)
                meta={k:json.loads(v) for k,v in (l.split(': ',1) for l in front.strip().splitlines())}
                for key in ['classificacao_revisao','acao_revisao','justificativa_revisao',
                            'impacto_revisao','pergunta_revisada','consolidada_em']:
                    meta.pop(key,None)
                meta['status']='respondida' if meta['id']=='IT-005' else 'aberta'
                meta['retomar_na_sabatina']=True
                if meta['id'] in cases:
                    group,action,resume,priority=cases[meta['id']]
                    meta.update(classificacao_revisao=group,acao_revisao=action,
                                retomar_na_sabatina=resume,prioridade=priority,
                                justificativa_revisao='Critério explícito de triagem.',
                                impacto_revisao='Fluxo ou afirmação identificados.',
                                pergunta_revisada='Qual trecho já narrado resolve esta passagem?')
                p.write_text('---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in meta.items())+'\n---\n'+body,encoding='utf-8')
                originals[p]=p.read_bytes()
            curated={}
            for rel in ['Campanhas/Fash.md','Visoes/Missoes e fios abertos.md']:
                p=root/'conteudo'/rel
                p.write_text('---\ntipo: "visao"\ntitulo: "Curadoria"\n---\n\nCuradoria que deve sobreviver.\n',encoding='utf-8')
                curated[p]=p.read_bytes()
            result=subprocess.run([sys.executable,'-X','utf8',str(root/'tools/indexar_enciclopedia.py'),'--somente-indices'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            m=json.loads((root/'docs/enciclopedia/integracao.json').read_text(encoding='utf-8'))
            self.assertEqual(m['ids_ativos'],['EV-001','PC-021'])
            self.assertEqual(m['fila_sabatina'],['EV-001'])
            self.assertEqual(m['pendencias_ativas'],2)
            self.assertEqual(m['registros_sem_resposta_completa'],len(originals)-1)
            roteiro=(root/'conteudo/Pendencias/Roteiro da sabatina.md').read_text(encoding='utf-8')
            self.assertNotIn('|LG-015',roteiro)
            self.assertNotIn('|PC-030',roteiro)
            self.assertNotIn('qual o endereço',roteiro.lower())
            self.assertIn('Conferir fontes',roteiro)
            index=(root/'conteudo/Pendencias/Indice.md').read_text(encoding='utf-8')
            self.assertIn('Fatos em aberto',index)
            self.assertIn('Detalhes sem impacto',index)
            self.assertIn('Sem triagem',index)
            for p,raw in {**originals,**curated}.items():self.assertEqual(p.read_bytes(),raw,str(p))

if __name__=='__main__':unittest.main()
