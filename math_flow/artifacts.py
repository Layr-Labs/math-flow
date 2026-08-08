from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from .errors import MathFlowError


def sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class ArtifactBundle:
    """Write a judge run as a manifest plus content-addressed artifacts."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir.resolve()
        if self.output_dir.exists() and any(self.output_dir.iterdir()):
            raise MathFlowError(f"judge run output directory is not empty: {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._artifacts: list[dict[str, object]] = []

    def _target(self, relative_path: str) -> Path:
        path = PurePosixPath(relative_path)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise MathFlowError(f"invalid artifact path: {relative_path}")
        target = self.output_dir.joinpath(*path.parts).resolve()
        try:
            target.relative_to(self.output_dir)
        except ValueError as exc:
            raise MathFlowError(f"artifact path escapes output directory: {relative_path}") from exc
        return target

    def add_bytes(self, relative_path: str, value: bytes, role: str, media_type: str) -> None:
        target = self._target(relative_path)
        if target.exists():
            raise MathFlowError(f"duplicate artifact path: {relative_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
        self._artifacts.append(
            {
                "path": PurePosixPath(relative_path).as_posix(),
                "role": role,
                "mediaType": media_type,
                "digest": sha256_bytes(value),
                "bytes": len(value),
            }
        )

    def add_text(self, relative_path: str, value: str, role: str, media_type: str) -> None:
        self.add_bytes(relative_path, value.encode("utf-8"), role, media_type)

    def add_json(self, relative_path: str, value: object, role: str) -> None:
        rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        self.add_text(relative_path, rendered, role, "application/json")

    def finalize(self, envelope: dict[str, object]) -> dict[str, object]:
        manifest = {**envelope, "artifacts": sorted(self._artifacts, key=lambda item: str(item["path"]))}
        target = self._target("run.json")
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return manifest


def load_manifest(bundle_dir: Path) -> tuple[dict[str, object], str]:
    path = bundle_dir.resolve() / "run.json"
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read base judge run manifest {path}: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("protocolVersion") != 1:
        raise MathFlowError(f"invalid judge run manifest: {path}")
    return manifest, sha256_bytes(raw)


def read_verified_artifact(bundle_dir: Path, manifest: dict[str, object], role: str) -> bytes:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or any(not isinstance(item, dict) for item in artifacts):
        raise MathFlowError("base judge run contains an invalid artifact index")
    matches = [item for item in artifacts if item.get("role") == role]
    if len(matches) != 1:
        raise MathFlowError(f"base judge run must contain exactly one {role!r} artifact")
    artifact = matches[0]
    path = PurePosixPath(str(artifact["path"]))
    if path.is_absolute() or ".." in path.parts:
        raise MathFlowError(f"invalid artifact path in base manifest: {path}")
    target = bundle_dir.resolve().joinpath(*path.parts).resolve()
    try:
        target.relative_to(bundle_dir.resolve())
    except ValueError as exc:
        raise MathFlowError(f"base artifact escapes bundle directory: {path}") from exc
    value = target.read_bytes()
    if sha256_bytes(value) != artifact.get("digest"):
        raise MathFlowError(f"base artifact digest mismatch: {path}")
    return value
