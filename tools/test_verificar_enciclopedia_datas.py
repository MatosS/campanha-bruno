import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class DatasDaEnciclopedia(unittest.TestCase):
    def verificar(self, atualizado):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            docs = root / 'docs/enciclopedia'
            docs.mkdir(parents=True)
            (docs / 'estado-fontes.json').write_text('{"arquivos": []}')
            (docs / 'registro-entidades.json').write_text('{"entidades": []}')
            notes = root / 'conteudo/Visoes'
            notes.mkdir(parents=True)
            meta = dict(tipo='indice', titulo='Fixture', campanhas=[], publico=True,
                        status='documentado_parcial', origens=[], aliases=[], atualizado=atualizado)
            (notes / 'Fixture.md').write_text('---\n' + '\n'.join(
                k + ': ' + json.dumps(v) for k, v in meta.items()) + '\n---\n\n# Fixture\n', encoding='utf-8')
            script = root / 'tools/verificar_enciclopedia.py'
            shutil.copyfile(Path(__file__).with_name(script.name), script)
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            return result.returncode, result.stdout

    def test_datas_de_rodadas_diferentes(self):
        for value in ['2026-10-29', '2026-10-30']:
            with self.subTest(value=value):
                code, output = self.verificar(value)
                self.assertEqual(code, 0, output)

    def test_datas_invalidas(self):
        for value in [None, '', '30/10/2026', '2026-02-30', '20261030']:
            with self.subTest(value=value):
                code, output = self.verificar(value)
                self.assertNotEqual(code, 0, output)


if __name__ == '__main__':
    unittest.main()
