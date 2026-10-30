"""Resolve proveniência histórica sem aceitar sumiços não autorizados de fontes.

Os manifestos conservam o caminho original. Uma cópia arquivada só substitui
uma origem ausente se manifesto, auditoria e execução concluída concordarem
sobre o mesmo caminho e SHA-256; os bytes são reconferidos a cada resolução.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


def require_regeneration_opt_in(root: Path) -> None:
    """Uma conferência pós-limpeza não deve regravar curadoria por acidente."""
    if (Path(root) / "conteudo/Fontes").is_dir() and "--regenerar-fontes-curadas" not in sys.argv:
        raise RuntimeError(
            "Há fontes já convertidas/curadas. Este script sobrescreve saídas; "
            "use verificar_migracao.py para conferir. Regeneração deliberada exige "
            "--regenerar-fontes-curadas e revisão das alterações."
        )


class SourceResolutionError(ValueError):
    """Fonte ausente, alterada ou sem registro válido de remoção."""


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise SourceResolutionError(f"Registro de fontes ilegível: {path}: {exc}") from exc


def _relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SourceResolutionError(f"Caminho de proveniência inválido: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ":" in value or any(p in ("", ".", "..") for p in value.split("/")):
        raise SourceResolutionError(f"Caminho de proveniência inválido: {value!r}")
    return path


class SourceResolver:
    def __init__(self, root: Path):
        self.root = Path(root)
        survey = _load(self.root / "docs/inventario-fontes.json")
        self.vault = Path(survey["source_root"])
        manifest = _load(self.root / "docs/migracao/textos.json")
        self.records = {}
        for record in manifest["originais"]:
            origin = record["origem"]
            _relative(origin)
            archived = record["arquivo"]
            _relative(archived)
            if not origin.startswith(("BASE INICIAL/", "vault-42/")):
                raise SourceResolutionError(f"Origem fora do recorte: {origin}")
            if archived != "arquivo/originais/" + origin:
                raise SourceResolutionError(f"Cópia fora do arquivo esperado: {origin}")
            if origin in self.records or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
                raise SourceResolutionError(f"Registro original inválido ou repetido: {origin}")
            self.records[origin] = record
        self.execution_path = self.root / "docs/limpeza/execucao.json"
        self.execution = _load(self.execution_path) if self.execution_path.exists() else None
        self._execution_validated = False

    def original_path(self, origin: str) -> Path:
        self._record(origin)
        if origin.startswith("vault-42/"):
            return self.vault / origin.removeprefix("vault-42/")
        return self.root / origin

    def archive_path(self, origin: str) -> Path:
        return self.root / self._record(origin)["arquivo"]

    def _record(self, origin: str) -> dict:
        if origin not in self.records:
            raise SourceResolutionError(f"Origem não registrada na migração: {origin}")
        return self.records[origin]

    def validate_execution(self) -> dict:
        """Confere o registro completo, inclusive entradas que não foram usadas."""
        execution = self.execution
        if not execution or execution.get("estado") != "concluida":
            raise SourceResolutionError("Origem ausente sem execução de limpeza concluída")
        if not execution.get("data") or not execution.get("autorizacao"):
            raise SourceResolutionError("Execução de limpeza sem data ou autorização")
        candidates = _load(self.root / "docs/auditoria-exclusao/candidatos.json")
        groups = candidates.get("arquivos")
        if not isinstance(groups, dict) or set(groups) != {"BASE INICIAL", "vault-42"}:
            raise SourceResolutionError("Lista de candidatos fora do recorte auditado")
        audited = [entry for group in groups.values() for entry in group]
        completed = execution.get("arquivos")
        if not isinstance(completed, list):
            raise SourceResolutionError("Execução de limpeza sem lista de arquivos")
        expected = {origin: {"origem": origin, "copia_preservada": r["arquivo"], "sha256": r["sha256"]}
                    for origin, r in self.records.items()}
        for label, entries in (("candidatos", audited), ("execução", completed)):
            seen = set()
            for entry in entries:
                if not isinstance(entry, dict):
                    raise SourceResolutionError(f"Entrada inválida em {label}")
                origin = entry.get("origem")
                if not isinstance(origin, str) or origin in seen or origin not in expected:
                    raise SourceResolutionError(f"Origem desconhecida ou repetida em {label}: {origin}")
                if any(entry.get(key) != value for key, value in expected[origin].items()):
                    raise SourceResolutionError(f"Caminho ou hash divergente em {label}: {origin}")
                seen.add(origin)
            if seen != set(expected):
                raise SourceResolutionError(f"Lista incompleta de origens em {label}")
        self._execution_validated = True
        return execution

    @staticmethod
    def _verify(path: Path, expected: str) -> None:
        if not path.is_file():
            raise SourceResolutionError(f"Arquivo ausente: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SourceResolutionError(f"Hash divergente: {path}")

    def resolve(self, origin: str, expected_sha256: str | None = None) -> Path:
        record = self._record(origin)
        expected = record["sha256"]
        if expected_sha256 is not None and expected_sha256 != expected:
            raise SourceResolutionError(f"Hash esperado difere do manifesto: {origin}")
        original = self.original_path(origin)
        archived = self.archive_path(origin)
        self._verify(archived, expected)
        if original.exists():
            self._verify(original, expected)
            return original
        if not self._execution_validated:
            self.validate_execution()
        return archived

    def verify_output(self, relative_path: str, expected_sha256: str) -> Path:
        """Mantém hashes históricos; só o conversor registrado pode ser atualizado."""
        _relative(relative_path)
        path = self.root / relative_path
        if not path.is_file():
            raise SourceResolutionError(f"Arquivo ausente: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual == expected_sha256:
            return path
        # O manifesto DOCX também arrolou o próprio script como saída gerada.
        # Isso não autoriza exceções nos documentos, anexos ou outros caminhos.
        if relative_path == "tools/converter_docx.py":
            if not self._execution_validated:
                self.validate_execution()
            updates = self.execution.get("scripts_atualizados", [])
            if isinstance(updates, list) and len(updates) == 1:
                update = updates[0]
                if (isinstance(update, dict) and update.get("caminho") == relative_path
                        and update.get("sha256_antes") == expected_sha256
                        and update.get("sha256_depois") == actual and update.get("motivo")):
                    return path
        raise SourceResolutionError(f"Hash divergente: {path}")
