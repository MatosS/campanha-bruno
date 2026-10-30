"""Seleção da revisão não confunde status histórico com relevância."""
import unittest
from fila_revisao import separate

class FilaDeRevisao(unittest.TestCase):
    def q(self,code,**values):
        return dict(id=code,status='aberta',prioridade='alta',origens=['Fonte'],**values)

    def test_aberto_e_detalhe_nao_entram_mesmo_com_flag_antiga(self):
        for group in ['em_aberto','detalhe_sem_impacto','encerrada']:
            groups,active,queue,_,_=separate([self.q('LG-015',classificacao_revisao=group,acao_revisao='perguntar',retomar_na_sabatina=True)])
            self.assertEqual(active,[])
            self.assertEqual(queue,[])

    def test_registro_sem_triagem_fica_fora_e_resposta_nao_reabre(self):
        q=self.q('IT-005',classificacao_revisao='contradicao',acao_revisao='perguntar',retomar_na_sabatina=True)
        q['status']='respondida'
        groups,active,queue,_,_=separate([q,self.q('PC-030',retomar_na_sabatina=True)])
        self.assertEqual(active,[])
        self.assertEqual(queue,[])
        self.assertEqual(len(groups['encerrada']),1)
        self.assertEqual(len(groups['sem_triagem']),1)

    def test_relevancia_sem_justificativa_nao_gera_pergunta(self):
        with self.assertRaisesRegex(ValueError,'Revisão sem'):
            separate([self.q('EV-009',classificacao_revisao='contradicao',acao_revisao='perguntar',retomar_na_sabatina=True)])

if __name__=='__main__':unittest.main()
