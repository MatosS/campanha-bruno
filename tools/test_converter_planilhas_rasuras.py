"""Regression check against the generated artifact and the original font styles."""
from pathlib import Path
import unittest
import openpyxl

from fontes_migracao import SourceResolver

ROOT = Path(__file__).resolve().parents[1]


class GeneratedStrikeFormatting(unittest.TestCase):
    def test_fash_interesses_exposes_exact_source_strikes_without_claiming_completion(self):
        expected = {
            'C3': 'Nyth (P25)',
            'D4': 'Não causa grandes problemas porém os mestiços não conseguem eliminar',
            'C24': 'Fantasma me seguindo/espionando (Foi embora)',
            'C25': 'Ossos de Dragão (Concluído)',
            'C51': 'Portal: Cabeça de Gigante',
            'C52': 'Portal: 4 Costelas Grandes',
        }
        source_path = SourceResolver(ROOT).resolve('BASE INICIAL/FASH PALESKIN.xlsx')
        wb = openpyxl.load_workbook(source_path, read_only=True, data_only=False)
        source = {c.coordinate: c.value for row in wb['INTERESSES'].iter_rows() for c in row
                  if c.value is not None and c.font.strike}
        wb.close()
        self.assertEqual(source, expected)
        md = (ROOT / 'conteudo/Fontes/Planilhas/Fash Paleskin - INTERESSES.md').read_text(encoding='utf-8')
        for coord, text in expected.items():
            with self.subTest(coord=coord):
                self.assertIn('| <code>' + coord + '</code> | ~~' + text + '~~ |', md)
        self.assertEqual(md.count(' | ~~'), 6)
        self.assertIn('rasura, por si só, não prova conclusão', md)


if __name__ == '__main__':
    unittest.main()
