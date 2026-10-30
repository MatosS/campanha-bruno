"""Provas do fallback estrito, sem executar conversores ou alterar fontes reais."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fontes_migracao import SourceResolver, SourceResolutionError, require_regeneration_opt_in


class SourceResolverTests(unittest.TestCase):
    def setUp(self):
        # O sandbox Windows pode negar criação de subpastas no TEMP do sistema.
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent,
                                                prefix=".teste-fontes-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vault = self.root / "vault-externo"
        self.origins = ["BASE INICIAL/Teste.md", "vault-42/20 Projects/Teste.md"]
        self.records = []
        for n, origin in enumerate(self.origins):
            content = f"fonte {n}\r\n".encode()
            record = dict(origem=origin, arquivo="arquivo/originais/" + origin,
                          sha256=hashlib.sha256(content).hexdigest())
            self.records.append(record)
            path = self.vault / origin.removeprefix("vault-42/") if n else self.root / origin
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            archived = self.root / record["arquivo"]
            archived.parent.mkdir(parents=True, exist_ok=True)
            archived.write_bytes(content)
        self.write_json("docs/inventario-fontes.json", dict(source_root=str(self.vault)))
        self.write_json("docs/migracao/textos.json", dict(originais=self.records))
        self.entries = [dict(origem=r["origem"], copia_preservada=r["arquivo"], sha256=r["sha256"])
                        for r in self.records]
        self.candidates = dict(arquivos={"BASE INICIAL": self.entries[:1], "vault-42": self.entries[1:]})
        self.write_json("docs/auditoria-exclusao/candidatos.json", self.candidates)
        self.execution = dict(data="2026-10-29", autorizacao="Autorização explícita do usuário",
                              estado="concluida", arquivos=self.entries)

    def write_json(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def finish_cleanup(self):
        for origin in self.origins:
            SourceResolver(self.root).original_path(origin).unlink()
        self.write_json("docs/limpeza/execucao.json", self.execution)

    def test_present_originals_and_vault_use_historical_paths_without_cleanup(self):
        resolver = SourceResolver(self.root)
        for origin in self.origins:
            self.assertEqual(resolver.resolve(origin), resolver.original_path(origin))

    def test_completed_cleanup_resolves_both_archives_and_keeps_manifest_origin(self):
        self.finish_cleanup()
        resolver = SourceResolver(self.root)
        for origin in self.origins:
            self.assertEqual(resolver.resolve(origin), resolver.archive_path(origin))
        self.assertEqual(list(resolver.records), self.origins)

    def test_missing_source_without_cleanup_is_rejected(self):
        resolver = SourceResolver(self.root)
        resolver.original_path(self.origins[0]).unlink()
        with self.assertRaisesRegex(SourceResolutionError, "concluída"):
            resolver.resolve(self.origins[0])

    def test_incomplete_or_unauthorized_cleanup_is_rejected(self):
        self.finish_cleanup()
        for field, value in (("estado", "planejada"), ("data", ""), ("autorizacao", "")):
            with self.subTest(field=field):
                changed = {**self.execution, field: value}
                self.write_json("docs/limpeza/execucao.json", changed)
                with self.assertRaises(SourceResolutionError):
                    SourceResolver(self.root).resolve(self.origins[0])

    def test_all_cleanup_entries_must_match_audit_and_manifest(self):
        self.finish_cleanup()
        variants = [self.entries[:1], self.entries + self.entries[:1],
                    [self.entries[0], {**self.entries[1], "sha256": "0" * 64}],
                    [self.entries[0], {**self.entries[1], "copia_preservada": "arquivo/alternativo.md"}],
                    [self.entries[0], {**self.entries[1], "origem": "vault-42/nao-selecionado.md"}]]
        for entries in variants:
            with self.subTest(entries=entries):
                self.write_json("docs/limpeza/execucao.json", {**self.execution, "arquivos": entries})
                with self.assertRaises(SourceResolutionError):
                    SourceResolver(self.root).resolve(self.origins[0])

    def test_changed_candidate_is_rejected_even_if_execution_matches_manifest(self):
        self.finish_cleanup()
        self.candidates["arquivos"]["vault-42"][0] = {**self.entries[1], "sha256": "0" * 64}
        self.write_json("docs/auditoria-exclusao/candidatos.json", self.candidates)
        with self.assertRaisesRegex(SourceResolutionError, "candidatos"):
            SourceResolver(self.root).resolve(self.origins[0])

    def test_changed_original_cannot_be_hidden_by_identical_archive(self):
        resolver = SourceResolver(self.root)
        resolver.original_path(self.origins[0]).write_bytes(b"alterado")
        with self.assertRaisesRegex(SourceResolutionError, "Hash divergente"):
            resolver.resolve(self.origins[0])

    def test_missing_or_changed_archive_is_rejected_before_and_after_cleanup(self):
        for cleanup in (False, True):
            with self.subTest(cleanup=cleanup):
                if cleanup:
                    self.finish_cleanup()
                resolver = SourceResolver(self.root)
                archived = resolver.archive_path(self.origins[0])
                archived.write_bytes(b"alterado")
                with self.assertRaisesRegex(SourceResolutionError, "Hash divergente"):
                    resolver.resolve(self.origins[0])
                archived.unlink()
                with self.assertRaisesRegex(SourceResolutionError, "Arquivo ausente"):
                    resolver.resolve(self.origins[0])
                archived.write_bytes(b"fonte 0\r\n")

    def test_unregistered_origin_and_conflicting_expected_hash_are_rejected(self):
        resolver = SourceResolver(self.root)
        with self.assertRaisesRegex(SourceResolutionError, "não registrada"):
            resolver.resolve("BASE INICIAL/nao-autorizado.md")
        with self.assertRaisesRegex(SourceResolutionError, "Hash esperado"):
            resolver.resolve(self.origins[0], "0" * 64)

    def test_manifest_cannot_point_outside_preserved_archive(self):
        self.records[0]["arquivo"] = "arquivo/originais/../outro.md"
        self.write_json("docs/migracao/textos.json", dict(originais=self.records))
        with self.assertRaises(SourceResolutionError):
            SourceResolver(self.root)

    def test_only_registered_converter_update_can_use_new_output_hash(self):
        self.finish_cleanup()
        path = self.root / "tools/converter_docx.py"
        path.parent.mkdir()
        path.write_bytes(b"conversor atualizado")
        before = "1" * 64
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        self.execution["scripts_atualizados"] = [dict(caminho="tools/converter_docx.py", sha256_antes=before,
                                                      sha256_depois=after, motivo="Resolver fontes arquivadas")]
        self.write_json("docs/limpeza/execucao.json", self.execution)
        self.assertEqual(SourceResolver(self.root).verify_output("tools/converter_docx.py", before), path)
        path.write_bytes(b"mudanca sem registro")
        with self.assertRaisesRegex(SourceResolutionError, "Hash divergente"):
            SourceResolver(self.root).verify_output("tools/converter_docx.py", before)
        with self.assertRaisesRegex(SourceResolutionError, "Hash divergente"):
            SourceResolver(self.root).verify_output(self.records[0]["arquivo"], before)

    def test_converter_update_requires_both_historical_and_current_hashes(self):
        self.finish_cleanup()
        path = self.root / "tools/converter_docx.py"
        path.parent.mkdir()
        path.write_bytes(b"conversor atualizado")
        before = "1" * 64
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = dict(caminho="tools/converter_docx.py", sha256_antes=before, sha256_depois=after,
                     motivo="Resolver fontes arquivadas")
        for field, value in (("sha256_antes", "0" * 64), ("sha256_depois", "0" * 64), ("motivo", "")):
            with self.subTest(field=field):
                self.execution["scripts_atualizados"] = [{**entry, field: value}]
                self.write_json("docs/limpeza/execucao.json", self.execution)
                with self.assertRaises(SourceResolutionError):
                    SourceResolver(self.root).verify_output("tools/converter_docx.py", before)

    def test_regeneration_guard_requires_explicit_opt_in_for_existing_sources(self):
        (self.root / "conteudo/Fontes").mkdir(parents=True)
        with patch("sys.argv", ["conversor.py"]):
            with self.assertRaisesRegex(RuntimeError, "sobrescreve"):
                require_regeneration_opt_in(self.root)
        with patch("sys.argv", ["conversor.py", "--regenerar-fontes-curadas"]):
            require_regeneration_opt_in(self.root)


if __name__ == "__main__":
    unittest.main()
