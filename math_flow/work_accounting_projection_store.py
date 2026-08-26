"""Inactive projections-branch persistence for the work-accounting CAS protocol."""

from __future__ import annotations

import copy
import fcntl
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Protocol

from .artifacts import sha256_bytes
from .errors import MathFlowError
from .github_projection import publish_github_projection
from .repository import canonical_json, sha256_json, validate_slug
from .work_accounting_pipeline import (
    CASConflict,
    CASObjectStore,
    ImmutableConflict,
    StoredValue,
    validate_work_accounting_pipeline_state,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
SAFE_PART = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

DEFAULT_MAXIMUM_OBJECT_BYTES = 5 * 1024 * 1024
DEFAULT_MAXIMUM_LANE_OBJECTS = 50_000
DEFAULT_MAXIMUM_MANIFEST_BYTES = 5 * 1024 * 1024
DEFAULT_MAXIMUM_TRANSPORT_CHUNK_BYTES = 25 * 1024 * 1024
GITHUB_MAXIMUM_FILES_PER_COMMIT = 100

PUBLICATION_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "laneScopeDigest",
    "pipelineStateDigest",
    "laneHeadVersion",
    "previousPublicationManifestDigest",
    "identityObject",
    "retainedObjects",
    "publicationManifestDigest",
}
OBJECT_FIELDS = {"logicalKey", "path", "digest", "bytes"}
MARKER_FIELDS = {
    "schemaVersion",
    "problemId",
    "projectionId",
    "projectionSpecDigest",
    "laneScopeDigest",
    "pipelineStateDigest",
    "laneHeadVersion",
    "publicationManifestDigest",
    "markerDigest",
}
PUBLISHER_REPORT_FIELDS = {
    "repository",
    "branch",
    "previousHead",
    "commit",
    "url",
    "filesAddedOrUpdated",
    "filesDeleted",
    "signature",
    "commitCount",
    "immutableCommitCount",
    "metadataCommit",
    "commits",
}
PUBLISHER_COMMIT_FIELDS = {
    "phase",
    "previousHead",
    "commit",
    "url",
    "filesAddedOrUpdated",
    "filesDeleted",
    "signature",
}


class ProjectionPublisher(Protocol):
    def __call__(
        self,
        projection_dir: Path,
        repository: str,
        branch: str,
        message: str,
        token: str,
        *,
        endpoint: str,
    ) -> dict[str, object]: ...


def work_accounting_lane_scope_digest(
    *, problem: str, projection_id: str, projection_spec_digest: str
) -> str:
    """Return the exact governed scope for one work-accounting projection lane."""

    if not isinstance(problem, str):
        raise MathFlowError("work-accounting problem ID is invalid")
    validate_slug(problem, "work-accounting problem ID")
    if not isinstance(projection_id, str) or not IDENTIFIER.fullmatch(projection_id):
        raise MathFlowError("work-accounting projection ID is invalid")
    spec = _require_digest(projection_spec_digest, "projection spec digest")
    scope = {
        "schemaVersion": 1,
        "problemId": problem,
        "projectionId": projection_id,
        "projectionSpecDigest": spec,
    }
    return f"sha256:{sha256_json(scope)}"


def _git(worktree: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(worktree), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "git command failed"
        raise MathFlowError(f"work-accounting projection Git operation failed: {detail}") from exc
    return result.stdout.rstrip("\n")


def _canonical_bytes(value: object) -> bytes:
    try:
        return (canonical_json(value) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MathFlowError("work-accounting projection value is not canonical JSON") from exc


def _json_object(content: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"{label} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be a JSON object")
    return value


def _content_digest(value: Mapping[str, object], digest_field: str) -> str:
    content = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != digest_field
    }
    return f"sha256:{sha256_json(content)}"


def _require_digest(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _safe_relative(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise MathFlowError(f"{label} is not a safe relative path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or not path.parts
        or any(
            part in {"", ".", ".."} or not SAFE_PART.fullmatch(part)
            for part in path.parts
        )
    ):
        raise MathFlowError(f"{label} is not a safe relative path")
    return path


def _require_regular_file(root: Path, relative: PurePosixPath, label: str) -> Path:
    target = root.joinpath(*relative.parts)
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise MathFlowError(f"{label} traverses a symlink")
    if not target.is_file():
        raise MathFlowError(f"{label} is missing or not a regular file")
    return target


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def validate_work_accounting_projection_publication(
    value: object,
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != PUBLICATION_FIELDS:
        raise MathFlowError("work-accounting projection publication has invalid fields")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting projection publication has an invalid version")
    if not isinstance(value.get("problemId"), str):
        raise MathFlowError("work-accounting publication problem ID is invalid")
    validate_slug(value["problemId"], "publication problem ID")
    if not isinstance(value.get("projectionId"), str) or not IDENTIFIER.fullmatch(
        value["projectionId"]
    ):
        raise MathFlowError("work-accounting publication projection ID is invalid")
    for field in (
        "projectionSpecDigest",
        "laneScopeDigest",
        "pipelineStateDigest",
        "laneHeadVersion",
    ):
        _require_digest(value.get(field), f"publication {field}")
    _require_digest(
        value.get("previousPublicationManifestDigest"),
        "previous publication manifest digest",
        nullable=True,
    )
    identity = value.get("identityObject")
    if not isinstance(identity, dict):
        raise MathFlowError("work-accounting publication identity object is invalid")
    retained = value.get("retainedObjects")
    if not isinstance(retained, list):
        raise MathFlowError("work-accounting publication retained objects are invalid")
    records = [identity, *retained]
    logical_keys: list[str] = []
    paths: list[str] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != OBJECT_FIELDS:
            raise MathFlowError("work-accounting retained object has invalid fields")
        logical_key = record.get("logicalKey")
        path = record.get("path")
        if not isinstance(logical_key, str) or not logical_key:
            raise MathFlowError("work-accounting retained object logical key is invalid")
        _safe_relative(path, "work-accounting retained object path")
        _require_digest(record.get("digest"), "work-accounting retained object digest")
        size = record.get("bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise MathFlowError("work-accounting retained object byte count is invalid")
        logical_keys.append(logical_key)
        paths.append(str(path))
    retained_keys = logical_keys[1:]
    retained_paths = paths[1:]
    for logical_key in retained_keys:
        logical_path = _safe_relative(
            logical_key, "work-accounting retained object logical key"
        )
        if logical_path.parts[0] not in {"objects", "indexes"}:
            raise MathFlowError(
                "work-accounting retained object logical key has an invalid namespace"
            )
    if (
        logical_keys[0] != "@lane-identity"
        or len(logical_keys) != len(set(logical_keys))
        or len(paths) != len(set(paths))
        or retained_keys != sorted(retained_keys)
        or retained_paths != sorted(retained_paths)
    ):
        raise MathFlowError("work-accounting retained objects are not canonical")
    if value.get("publicationManifestDigest") != _content_digest(
        value, "publicationManifestDigest"
    ):
        raise MathFlowError("work-accounting projection publication digest mismatch")
    return value


def validate_work_accounting_projection_marker(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != MARKER_FIELDS:
        raise MathFlowError("work-accounting projection marker has invalid fields")
    if value.get("schemaVersion") != 1:
        raise MathFlowError("work-accounting projection marker has an invalid version")
    if not isinstance(value.get("problemId"), str):
        raise MathFlowError("work-accounting marker problem ID is invalid")
    validate_slug(value["problemId"], "marker problem ID")
    if not isinstance(value.get("projectionId"), str) or not IDENTIFIER.fullmatch(
        value["projectionId"]
    ):
        raise MathFlowError("work-accounting marker projection ID is invalid")
    for field in MARKER_FIELDS - {
        "schemaVersion",
        "problemId",
        "projectionId",
    }:
        _require_digest(value.get(field), f"marker {field}")
    if value.get("markerDigest") != _content_digest(value, "markerDigest"):
        raise MathFlowError("work-accounting projection marker digest mismatch")
    return value


class ProjectionBranchWorkAccountingStore(CASObjectStore):
    """Map one pipeline CAS lane into existing projections-branch paths."""

    def __init__(
        self,
        projection_root: Path,
        *,
        problem: str,
        projection_id: str,
        projection_spec_digest: str,
        maximum_object_bytes: int = DEFAULT_MAXIMUM_OBJECT_BYTES,
        maximum_lane_objects: int = DEFAULT_MAXIMUM_LANE_OBJECTS,
        maximum_manifest_bytes: int = DEFAULT_MAXIMUM_MANIFEST_BYTES,
        maximum_transport_chunk_bytes: int = DEFAULT_MAXIMUM_TRANSPORT_CHUNK_BYTES,
        create: bool = True,
    ) -> None:
        if not projection_root.is_dir() or projection_root.is_symlink():
            raise MathFlowError("projection worktree must be a non-symlink directory")
        self.root = projection_root.resolve()
        if not (_git(self.root, "rev-parse", "--is-inside-work-tree") == "true"):
            raise MathFlowError("projection root must be a Git worktree")
        if not isinstance(problem, str):
            raise MathFlowError("work-accounting problem ID is invalid")
        validate_slug(problem, "work-accounting problem ID")
        self.problem = problem
        if not isinstance(projection_id, str) or not IDENTIFIER.fullmatch(projection_id):
            raise MathFlowError("work-accounting projection ID is invalid")
        self.projection_id = projection_id
        spec = _require_digest(projection_spec_digest, "projection spec digest")
        assert isinstance(spec, str)
        self.projection_spec_digest = spec
        for value, label in (
            (maximum_object_bytes, "maximum object bytes"),
            (maximum_lane_objects, "maximum lane objects"),
            (maximum_manifest_bytes, "maximum manifest bytes"),
            (maximum_transport_chunk_bytes, "maximum transport chunk bytes"),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise MathFlowError(f"{label} must be a positive integer")
        self.maximum_object_bytes = maximum_object_bytes
        self.maximum_lane_objects = maximum_lane_objects
        self.maximum_manifest_bytes = maximum_manifest_bytes
        self.maximum_transport_chunk_bytes = maximum_transport_chunk_bytes
        scope_core = {
            "schemaVersion": 1,
            "problemId": self.problem,
            "projectionId": projection_id,
            "projectionSpecDigest": spec,
        }
        self.lane_scope_digest = work_accounting_lane_scope_digest(
            problem=self.problem,
            projection_id=self.projection_id,
            projection_spec_digest=self.projection_spec_digest,
        )
        self.scope_hex = self.lane_scope_digest.removeprefix("sha256:")
        self.object_root = (
            self.root
            / "objects"
            / "work-accounting-cas-v1"
            / self.problem
            / self.scope_hex
        )
        self.data_root = self.object_root / "data"
        self.identity_path = self.object_root / "identity.json"
        self.publication_root = (
            self.root
            / "objects"
            / "work-accounting-publication-v1"
            / self.problem
            / self.scope_hex
        )
        self.metadata_root = (
            self.root
            / "indexes"
            / "problems"
            / self.problem
            / "work-accounting-v1"
            / self.scope_hex
        )
        self.head_path = self.metadata_root / "head.json"
        self.marker_path = self.metadata_root / "publication.json"
        self.pipeline_lane_key = (
            "refs/work-accounting/"
            f"{self.projection_id.replace('/', '__')}/{self.problem}.json"
        )
        lock_identity = sha256_bytes(str(self.root).encode("utf-8")).removeprefix(
            "sha256:"
        )
        self.lock_root = (
            Path(tempfile.gettempdir())
            / "math-flow-work-accounting-projection-locks"
            / lock_identity
        )
        if not isinstance(create, bool):
            raise MathFlowError("work-accounting store create flag must be boolean")
        if create:
            self.lock_root.mkdir(parents=True, exist_ok=True)
            with self._locked("lane-identity"):
                self._ensure_identity(scope_core)
        else:
            self._validate_identity(scope_core)
        self._validate_lane_limits()

    def _relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError as exc:  # pragma: no cover - all paths are constructed under root
            raise MathFlowError("work-accounting projection path escapes its root") from exc

    def _logical_parts(self, key: str) -> tuple[str, ...]:
        path = _safe_relative(key, "work-accounting CAS key")
        if path.parts[0] not in {"objects", "indexes"}:
            raise MathFlowError("work-accounting immutable CAS key has an invalid namespace")
        return tuple(path.parts)

    def _assert_safe_target(self, target: Path) -> None:
        relative = PurePosixPath(self._relative(target))
        cursor = self.root
        for part in relative.parts:
            cursor = cursor / part
            if cursor.exists() and cursor.is_symlink():
                raise MathFlowError("work-accounting projection path traverses a symlink")

    def _write(self, target: Path, content: bytes) -> None:
        self._assert_safe_target(target)
        _atomic_write(target, content)

    def _immutable_path(self, key: str) -> Path:
        return self.data_root.joinpath(*self._logical_parts(key))

    def _path_for_key(self, key: str) -> Path:
        if key == self.pipeline_lane_key:
            return self.head_path
        if isinstance(key, str) and key.startswith("refs/"):
            raise MathFlowError("work-accounting CAS lane key belongs to another scope")
        return self._immutable_path(key)

    def _lock_path(self, key: str) -> Path:
        digest = sha256_bytes(key.encode("utf-8")).removeprefix("sha256:")
        return self.lock_root / f"{digest}.lock"

    def _locked(self, key: str):
        descriptor = os.open(self._lock_path(key), os.O_CREAT | os.O_RDWR, 0o600)

        class Lock:
            def __enter__(inner):
                fcntl.flock(descriptor, fcntl.LOCK_EX)
                return inner

            def __exit__(inner, exc_type, exc, traceback):
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)

        return Lock()

    def _ensure_identity(self, scope_core: Mapping[str, object]) -> None:
        identity = {
            **copy.deepcopy(dict(scope_core)),
            "laneScopeDigest": self.lane_scope_digest,
        }
        content = _canonical_bytes(identity)
        if self.identity_path.exists():
            if self.identity_path.is_symlink() or self.identity_path.read_bytes() != content:
                raise ImmutableConflict(
                    "projection work-accounting lane identity conflicts with existing bytes"
                )
            return
        self._write(self.identity_path, content)

    def _validate_identity(self, scope_core: Mapping[str, object]) -> None:
        identity = {
            **copy.deepcopy(dict(scope_core)),
            "laneScopeDigest": self.lane_scope_digest,
        }
        content = _canonical_bytes(identity)
        if (
            not self.identity_path.is_file()
            or self.identity_path.is_symlink()
            or self.identity_path.read_bytes() != content
        ):
            raise MathFlowError(
                "published work-accounting lane identity is missing or mismatched"
            )

    def _iter_data_files(self) -> list[Path]:
        if not self.data_root.exists():
            return []
        self._assert_safe_target(self.data_root)
        if self.data_root.is_symlink() or not self.data_root.is_dir():
            raise MathFlowError("work-accounting object data root is not a regular directory")
        files: list[Path] = []
        for path in self.data_root.rglob("*"):
            if path.is_symlink():
                raise MathFlowError("work-accounting object store contains a symlink")
            if path.is_file():
                files.append(path)
        return sorted(files, key=lambda item: item.relative_to(self.data_root).as_posix())

    def _validate_lane_limits(self) -> None:
        files = self._iter_data_files()
        if len(files) > self.maximum_lane_objects:
            raise MathFlowError("work-accounting lane exceeds its maximum object count")
        for path in files:
            if path.stat().st_size > self.maximum_object_bytes:
                raise MathFlowError("work-accounting lane contains an oversized object")

    def get(self, key: str) -> StoredValue | None:
        target = self._path_for_key(key)
        if not target.exists():
            return None
        relative = PurePosixPath(self._relative(target))
        target = _require_regular_file(self.root, relative, "work-accounting CAS object")
        content = target.read_bytes()
        if len(content) > self.maximum_object_bytes:
            raise MathFlowError("work-accounting CAS object exceeds its byte limit")
        return StoredValue(value=content, version=sha256_bytes(content))

    def put_immutable(self, key: str, value: bytes) -> str:
        if not isinstance(value, bytes):
            raise MathFlowError("work-accounting immutable object must be exact bytes")
        if len(value) > self.maximum_object_bytes:
            raise MathFlowError("work-accounting immutable object exceeds its byte limit")
        target = self._immutable_path(key)
        with self._locked("lane-immutable-objects"):
            current = self.get(key)
            if current is not None:
                if current.value != value:
                    raise ImmutableConflict(
                        "work-accounting immutable projection object already differs"
                    )
                return current.version
            if len(self._iter_data_files()) >= self.maximum_lane_objects:
                raise MathFlowError("work-accounting lane reached its maximum object count")
            self._write(target, value)
        return sha256_bytes(value)

    def compare_and_swap(
        self, key: str, expected_version: str | None, value: bytes
    ) -> str:
        if key != self.pipeline_lane_key:
            raise MathFlowError("projection CAS may mutate only its exact pipeline lane head")
        _require_digest(expected_version, "CAS expected version", nullable=True)
        if not isinstance(value, bytes):
            raise MathFlowError("projection CAS value must be exact bytes")
        if len(value) > self.maximum_object_bytes:
            raise MathFlowError("projection CAS value exceeds its byte limit")
        pipeline = validate_work_accounting_pipeline_state(
            _json_object(value, "work-accounting pipeline head")
        )
        if value != _canonical_bytes(pipeline):
            raise MathFlowError("projection CAS pipeline head is not canonical JSON")
        if (
            pipeline["problemId"] != self.problem
            or pipeline["projectionId"] != self.projection_id
            or pipeline["projectionSpecDigest"] != self.projection_spec_digest
        ):
            raise MathFlowError("projection CAS pipeline identity does not match its lane")
        with self._locked(f"head:{key}"):
            current = self.get(key)
            current_version = current.version if current is not None else None
            if current_version != expected_version:
                raise CASConflict("projection work-accounting head changed from expected")
            self._write(self.head_path, value)
        return sha256_bytes(value)

    def _identity_record(self) -> dict[str, object]:
        content = self.identity_path.read_bytes()
        return {
            "logicalKey": "@lane-identity",
            "path": self._relative(self.identity_path),
            "digest": sha256_bytes(content),
            "bytes": len(content),
        }

    def _retained_records(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for path in self._iter_data_files():
            content = path.read_bytes()
            logical_key = path.relative_to(self.data_root).as_posix()
            records.append(
                {
                    "logicalKey": logical_key,
                    "path": self._relative(path),
                    "digest": sha256_bytes(content),
                    "bytes": len(content),
                }
            )
        return records

    def _load_marker(self) -> dict[str, object] | None:
        if not self.marker_path.exists():
            return None
        content = _require_regular_file(
            self.root,
            PurePosixPath(self._relative(self.marker_path)),
            "work-accounting projection marker",
        ).read_bytes()
        if len(content) > self.maximum_manifest_bytes:
            raise MathFlowError("work-accounting projection marker exceeds its byte limit")
        marker = validate_work_accounting_projection_marker(
            _json_object(content, "work-accounting projection marker")
        )
        if content != _canonical_bytes(marker):
            raise MathFlowError("work-accounting projection marker is not canonical JSON")
        if (
            marker["problemId"] != self.problem
            or marker["projectionId"] != self.projection_id
            or marker["projectionSpecDigest"] != self.projection_spec_digest
            or marker["laneScopeDigest"] != self.lane_scope_digest
        ):
            raise MathFlowError("work-accounting projection marker belongs to another lane")
        return marker

    def _has_unpublished_changes(self) -> bool:
        paths = [
            self._relative(self.object_root),
            self._relative(self.publication_root),
            self._relative(self.metadata_root),
        ]
        return bool(
            _git(
                self.root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--",
                *paths,
            )
        )

    def _manifest_path(self, digest: str) -> Path:
        _require_digest(digest, "publication manifest digest")
        return self.publication_root / f"{digest.removeprefix('sha256:')}.json"

    def load_publication_manifest(self, digest: str) -> dict[str, object]:
        path = self._manifest_path(digest)
        content = _require_regular_file(
            self.root,
            PurePosixPath(self._relative(path)),
            "work-accounting publication manifest",
        ).read_bytes()
        if len(content) > self.maximum_manifest_bytes:
            raise MathFlowError("work-accounting publication manifest exceeds its byte limit")
        manifest = validate_work_accounting_projection_publication(
            _json_object(content, "work-accounting publication manifest")
        )
        if content != _canonical_bytes(manifest):
            raise MathFlowError(
                "work-accounting publication manifest is not canonical JSON"
            )
        if (
            manifest["publicationManifestDigest"] != digest
            or path.stem != digest.removeprefix("sha256:")
            or manifest["problemId"] != self.problem
            or manifest["projectionId"] != self.projection_id
            or manifest["projectionSpecDigest"] != self.projection_spec_digest
            or manifest["laneScopeDigest"] != self.lane_scope_digest
        ):
            raise MathFlowError("work-accounting publication manifest scope mismatch")
        return manifest

    def load_published_snapshot(self) -> dict[str, object] | None:
        """Read and verify the exact immutable objects selected by the lane marker."""

        marker = self._load_marker()
        if marker is None:
            return None
        manifest = self.load_publication_manifest(
            str(marker["publicationManifestDigest"])
        )
        head = self.get(self.pipeline_lane_key)
        if head is None:
            raise MathFlowError("published work-accounting lane marker has no head")
        pipeline = validate_work_accounting_pipeline_state(
            _json_object(head.value, "published work-accounting pipeline head")
        )
        if head.value != _canonical_bytes(pipeline):
            raise MathFlowError("published work-accounting pipeline head is not canonical")
        if (
            pipeline["problemId"] != self.problem
            or pipeline["projectionId"] != self.projection_id
            or pipeline["projectionSpecDigest"] != self.projection_spec_digest
            or marker["pipelineStateDigest"] != pipeline["pipelineStateDigest"]
            or marker["laneHeadVersion"] != head.version
            or manifest["pipelineStateDigest"] != pipeline["pipelineStateDigest"]
            or manifest["laneHeadVersion"] != head.version
            or manifest["publicationManifestDigest"]
            != marker["publicationManifestDigest"]
            or manifest["identityObject"] != self._identity_record()
        ):
            raise MathFlowError("published work-accounting snapshot bindings disagree")
        for record in [manifest["identityObject"], *manifest["retainedObjects"]]:
            self._verify_retained_record(record)
        return {
            "marker": marker,
            "manifest": manifest,
            "pipeline": pipeline,
            "laneHeadVersion": head.version,
        }

    def _verify_retained_record(self, record: Mapping[str, object]) -> None:
        path = _safe_relative(record["path"], "retained projection object path")
        target = _require_regular_file(
            self.root, path, "retained work-accounting projection object"
        )
        content = target.read_bytes()
        if len(content) != record["bytes"] or sha256_bytes(content) != record["digest"]:
            raise MathFlowError("retained work-accounting object binding mismatch")
        expected_root = self.object_root.resolve()
        try:
            target.resolve().relative_to(expected_root)
        except ValueError as exc:
            raise MathFlowError("retained work-accounting object escapes its lane") from exc

    def prepare_publication(self) -> dict[str, object]:
        head = self.get(self.pipeline_lane_key)
        if head is None:
            raise MathFlowError("work-accounting projection cannot publish without a lane head")
        pipeline = validate_work_accounting_pipeline_state(
            _json_object(head.value, "work-accounting pipeline head")
        )
        if head.value != _canonical_bytes(pipeline):
            raise MathFlowError("published pipeline head is not canonical JSON")
        if (
            pipeline["problemId"] != self.problem
            or pipeline["projectionId"] != self.projection_id
            or pipeline["projectionSpecDigest"] != self.projection_spec_digest
        ):
            raise MathFlowError("published pipeline head belongs to another lane")
        marker = self._load_marker()
        prior_manifest: dict[str, object] | None = None
        if marker is not None:
            prior_manifest = self.load_publication_manifest(
                str(marker["publicationManifestDigest"])
            )
            if (
                prior_manifest["pipelineStateDigest"] != marker["pipelineStateDigest"]
                or prior_manifest["laneHeadVersion"] != marker["laneHeadVersion"]
            ):
                raise MathFlowError(
                    "work-accounting marker and publication manifest disagree"
                )
            for record in [
                prior_manifest["identityObject"],
                *prior_manifest["retainedObjects"],
            ]:
                self._verify_retained_record(record)
        if marker is not None and (
            marker["pipelineStateDigest"] == pipeline["pipelineStateDigest"]
            and marker["laneHeadVersion"] == head.version
        ):
            assert prior_manifest is not None
            manifest = prior_manifest
            if (
                manifest["identityObject"] != self._identity_record()
                or manifest["retainedObjects"] != self._retained_records()
            ):
                raise MathFlowError(
                    "unchanged pipeline head has unpublished immutable objects; "
                    "refetch the projection branch before retrying"
                )
            return {
                "prepared": self._has_unpublished_changes(),
                "marker": marker,
                "manifest": manifest,
            }

        retained = self._retained_records()
        identity = self._identity_record()
        previous = (
            str(marker["publicationManifestDigest"]) if marker is not None else None
        )
        core: dict[str, object] = {
            "schemaVersion": 1,
            "problemId": self.problem,
            "projectionId": self.projection_id,
            "projectionSpecDigest": self.projection_spec_digest,
            "laneScopeDigest": self.lane_scope_digest,
            "pipelineStateDigest": pipeline["pipelineStateDigest"],
            "laneHeadVersion": head.version,
            "previousPublicationManifestDigest": previous,
            "identityObject": identity,
            "retainedObjects": retained,
        }
        manifest = {
            **core,
            "publicationManifestDigest": _content_digest(
                core, "publicationManifestDigest"
            ),
        }
        validate_work_accounting_projection_publication(manifest)
        rendered_manifest = _canonical_bytes(manifest)
        if len(rendered_manifest) > self.maximum_manifest_bytes:
            raise MathFlowError("work-accounting publication manifest exceeds its byte limit")
        manifest_path = self._manifest_path(str(manifest["publicationManifestDigest"]))
        if manifest_path.exists():
            if manifest_path.is_symlink() or manifest_path.read_bytes() != rendered_manifest:
                raise ImmutableConflict(
                    "work-accounting publication manifest content address conflicts"
                )
        else:
            self._write(manifest_path, rendered_manifest)

        marker_core = {
            "schemaVersion": 1,
            "problemId": self.problem,
            "projectionId": self.projection_id,
            "projectionSpecDigest": self.projection_spec_digest,
            "laneScopeDigest": self.lane_scope_digest,
            "pipelineStateDigest": pipeline["pipelineStateDigest"],
            "laneHeadVersion": head.version,
            "publicationManifestDigest": manifest["publicationManifestDigest"],
        }
        next_marker = {
            **marker_core,
            "markerDigest": _content_digest(marker_core, "markerDigest"),
        }
        validate_work_accounting_projection_marker(next_marker)
        self._write(self.marker_path, _canonical_bytes(next_marker))
        return {"prepared": True, "marker": next_marker, "manifest": manifest}

    def plan_retention(self) -> dict[str, object]:
        """Return a deletion-free reachability plan over every canonical marker."""

        referenced: set[str] = set()
        manifests: list[str] = []
        manifest_values: dict[str, dict[str, object]] = {}
        if self.publication_root.exists():
            self._assert_safe_target(self.publication_root)
            if self.publication_root.is_symlink() or not self.publication_root.is_dir():
                raise MathFlowError("publication manifest collection is not a directory")
            for path in sorted(self.publication_root.iterdir()):
                if path.is_symlink() or not path.is_file():
                    raise MathFlowError("publication manifest collection is not regular")
                if not re.fullmatch(r"[0-9a-f]{64}\.json", path.name):
                    raise MathFlowError("publication manifest collection has an unsafe entry")
                digest = f"sha256:{path.stem}"
                manifest = self.load_publication_manifest(digest)
                manifests.append(digest)
                manifest_values[digest] = manifest
                referenced.add(self._relative(path))
                for record in [manifest["identityObject"], *manifest["retainedObjects"]]:
                    self._verify_retained_record(record)
                    referenced.add(str(record["path"]))
        manifest_set = set(manifests)
        for manifest in manifest_values.values():
            previous = manifest["previousPublicationManifestDigest"]
            if previous is not None and previous not in manifest_set:
                raise MathFlowError("publication manifest predecessor is missing")
        marker = self._load_marker()
        if marker is not None:
            referenced.add(self._relative(self.marker_path))
            referenced.add(self._relative(self.head_path))
            if str(marker["publicationManifestDigest"]) not in manifests:
                raise MathFlowError("latest publication marker is absent from retention roots")
        all_lane_objects = {
            self._relative(path) for path in [self.identity_path, *self._iter_data_files()]
        }
        unreferenced = sorted(all_lane_objects - referenced)
        return {
            "schemaVersion": 1,
            "policy": "retain-all-canonical-work-accounting-publications",
            "problemId": self.problem,
            "projectionId": self.projection_id,
            "projectionSpecDigest": self.projection_spec_digest,
            "laneScopeDigest": self.lane_scope_digest,
            "publicationManifestDigests": manifests,
            "retainedPaths": sorted(referenced),
            "unpublishedPaths": unreferenced,
            "deletionPaths": [],
        }

    def validate_publication_changes(self) -> list[dict[str, str]]:
        """Reject deletions, cross-lane changes, and immutable rewrites."""

        raw = _git(
            self.root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "-z",
        )
        entries = raw.split("\0") if raw else []
        object_root = self._relative(self.object_root) + "/"
        data_root = self._relative(self.data_root) + "/"
        publication_root = self._relative(self.publication_root) + "/"
        identity_path = self._relative(self.identity_path)
        head_path = self._relative(self.head_path)
        marker_path = self._relative(self.marker_path)
        allowed_metadata = {head_path, marker_path}
        changes: list[dict[str, str]] = []
        for entry in entries:
            if not entry:
                continue
            if len(entry) < 4 or entry[2] != " ":
                raise MathFlowError("could not parse work-accounting projection status")
            status = entry[:2]
            path = entry[3:]
            if "R" in status or "C" in status:
                raise MathFlowError("work-accounting publication forbids renames and copies")
            in_object_data = path.startswith(data_root)
            in_publications = path.startswith(publication_root)
            if not (
                path == identity_path
                or in_object_data
                or in_publications
                or path in allowed_metadata
            ):
                raise MathFlowError(
                    f"work-accounting publication contains a cross-lane path: {path}"
                )
            if "D" in status:
                raise MathFlowError(
                    "work-accounting publication may not delete projection objects"
                )
            if (path.startswith(object_root) or in_publications) and status not in {
                "??",
                "A ",
            }:
                raise MathFlowError(
                    "work-accounting publication may not rewrite an immutable object"
                )
            changes.append({"status": status, "path": path})
        paths = {change["path"] for change in changes}
        if head_path not in paths or marker_path not in paths:
            raise MathFlowError(
                "work-accounting publication must atomically advance head and marker"
            )
        retention = self.plan_retention()
        if retention["unpublishedPaths"]:
            raise MathFlowError(
                "work-accounting publication contains immutable objects outside its manifest"
            )
        immutable_paths = sorted(
            change["path"]
            for change in changes
            if change["path"].startswith((object_root, publication_root))
        )
        for start in range(0, len(immutable_paths), GITHUB_MAXIMUM_FILES_PER_COMMIT):
            chunk = immutable_paths[start : start + GITHUB_MAXIMUM_FILES_PER_COMMIT]
            if sum((self.root / path).stat().st_size for path in chunk) > (
                self.maximum_transport_chunk_bytes
            ):
                raise MathFlowError(
                    "work-accounting immutable publication chunk exceeds its byte limit"
                )
        if sum((self.root / path).stat().st_size for path in allowed_metadata) > (
            self.maximum_transport_chunk_bytes
        ):
            raise MathFlowError(
                "work-accounting metadata publication chunk exceeds its byte limit"
            )
        return sorted(changes, key=lambda item: item["path"])


def _validate_signed_report(
    result: object,
    *,
    expected_previous_head: str,
    expected_repository: str,
    expected_branch: str,
    expected_changes: list[dict[str, str]],
) -> dict[str, object]:
    if not isinstance(result, dict):
        raise MathFlowError("projection publisher returned an invalid report")
    if set(result) != PUBLISHER_REPORT_FIELDS:
        raise MathFlowError("projection publisher report has unexpected fields")
    commits = result.get("commits")
    if (
        result.get("repository") != expected_repository
        or result.get("branch") != expected_branch
        or result.get("previousHead") != expected_previous_head
        or not isinstance(commits, list)
        or not commits
        or not isinstance(result.get("commitCount"), int)
        or isinstance(result.get("commitCount"), bool)
        or not isinstance(result.get("immutableCommitCount"), int)
        or isinstance(result.get("immutableCommitCount"), bool)
        or not isinstance(result.get("filesAddedOrUpdated"), int)
        or isinstance(result.get("filesAddedOrUpdated"), bool)
        or not isinstance(result.get("filesDeleted"), int)
        or isinstance(result.get("filesDeleted"), bool)
        or result.get("commit") != commits[-1].get("commit")
        or result.get("metadataCommit") != commits[-1].get("commit")
        or result.get("signature") != commits[-1].get("signature")
        or result.get("commitCount") != len(commits)
    ):
        raise MathFlowError("projection publisher report has invalid optimistic bindings")
    observed_metadata = False
    expected_head = expected_previous_head
    expected_immutable = sum(
        change["path"].startswith(("objects/", "publication-batches/"))
        for change in expected_changes
    )
    expected_mutable = len(expected_changes) - expected_immutable
    observed_immutable = 0
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            raise MathFlowError("projection publisher commit report is invalid")
        if set(commit) != PUBLISHER_COMMIT_FIELDS:
            raise MathFlowError("projection publisher commit report has unexpected fields")
        phase = commit.get("phase")
        if phase == "metadata":
            if observed_metadata or index != len(commits) - 1:
                raise MathFlowError("projection metadata commit is not final")
            observed_metadata = True
            if commit.get("filesAddedOrUpdated") != expected_mutable:
                raise MathFlowError(
                    "projection publisher metadata file accounting is invalid"
                )
        elif phase != "immutable" or observed_metadata:
            raise MathFlowError("projection publisher commit phases are invalid")
        else:
            added = commit.get("filesAddedOrUpdated")
            if (
                not isinstance(added, int)
                or isinstance(added, bool)
                or added < 1
                or added > GITHUB_MAXIMUM_FILES_PER_COMMIT
            ):
                raise MathFlowError(
                    "projection publisher immutable chunk accounting is invalid"
                )
            observed_immutable += added
        signature = commit.get("signature")
        if (
            not isinstance(signature, dict)
            or signature.get("isValid") is not True
            or signature.get("wasSignedByGitHub") is not True
            or commit.get("previousHead") != expected_head
            or not isinstance(commit.get("commit"), str)
            or not GIT_SHA.fullmatch(str(commit["commit"]))
            or not isinstance(commit.get("url"), str)
            or not str(commit["url"]).strip()
            or not isinstance(commit.get("filesAddedOrUpdated"), int)
            or isinstance(commit.get("filesAddedOrUpdated"), bool)
            or int(commit["filesAddedOrUpdated"]) < 0
            or not isinstance(commit.get("filesDeleted"), int)
            or isinstance(commit.get("filesDeleted"), bool)
            or int(commit["filesDeleted"]) != 0
        ):
            raise MathFlowError("projection publisher did not prove a signed commit chain")
        expected_head = str(commit["commit"])
    if not observed_metadata or observed_immutable != expected_immutable:
        raise MathFlowError("projection publisher omitted the final metadata commit")
    immutable_count = sum(commit["phase"] == "immutable" for commit in commits)
    if (
        result.get("immutableCommitCount") != immutable_count
        or result.get("filesAddedOrUpdated")
        != sum(int(commit["filesAddedOrUpdated"]) for commit in commits)
        or result.get("filesDeleted")
        != sum(int(commit["filesDeleted"]) for commit in commits)
        or result.get("filesDeleted") != 0
        or result.get("filesAddedOrUpdated") != len(expected_changes)
        or not isinstance(result.get("url"), str)
        or not str(result["url"]).strip()
    ):
        raise MathFlowError("projection publisher report file accounting is invalid")
    return result


def publish_work_accounting_projection(
    store: ProjectionBranchWorkAccountingStore,
    *,
    repository: str,
    branch: str,
    message: str,
    token: str,
    endpoint: str = "https://api.github.com/graphql",
    publisher: ProjectionPublisher = publish_github_projection,
) -> dict[str, object]:
    """Prepare one lane marker, then use the signed GitHub projection publisher."""

    prepared = store.prepare_publication()
    marker = prepared["marker"]
    manifest = prepared["manifest"]
    if prepared["prepared"] is False:
        return {
            "status": "already-published",
            "problemId": store.problem,
            "projectionId": store.projection_id,
            "projectionSpecDigest": store.projection_spec_digest,
            "pipelineStateDigest": marker["pipelineStateDigest"],
            "publicationManifestDigest": manifest["publicationManifestDigest"],
            "commit": _git(store.root, "rev-parse", "HEAD"),
        }
    changes = store.validate_publication_changes()
    previous_head = _git(store.root, "rev-parse", "HEAD")
    result = publisher(
        store.root,
        repository,
        branch,
        message,
        token,
        endpoint=endpoint,
    )
    verified = _validate_signed_report(
        result,
        expected_previous_head=previous_head,
        expected_repository=repository,
        expected_branch=branch,
        expected_changes=changes,
    )
    return {
        "status": "published",
        "problemId": store.problem,
        "projectionId": store.projection_id,
        "projectionSpecDigest": store.projection_spec_digest,
        "pipelineStateDigest": marker["pipelineStateDigest"],
        "publicationManifestDigest": manifest["publicationManifestDigest"],
        "transport": copy.deepcopy(verified),
    }
