"""Pinned, replayable objective-verifier bundles for canonical contributions."""

from __future__ import annotations

import json
import os
import re
import selectors
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable

from . import __version__
from .artifacts import ArtifactBundle, read_verified_artifact, sha256_bytes, verify_bundle
from .errors import MathFlowError
from .repository import (
    is_ancestor,
    ledger,
    list_files_at,
    read_bytes_at,
    resolve_commit,
    sha256_json,
    validate_slug,
)


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
OCI_IMAGE = re.compile(
    r"^[a-z0-9]+(?:[._-][a-z0-9]+)*(?:[/:][a-z0-9]+(?:[._/-][a-z0-9]+)*)*"
    r"@sha256:[0-9a-f]{64}$"
)
VERIFICATION_REQUEST = "verification.json"
SUPPORTED_IMPLEMENTATIONS = {"oci-command-v1"}
SUPPORTED_PLATFORMS = {"linux/amd64", "linux/arm64"}


def _strict_object(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise MathFlowError(f"{label} must contain exactly {sorted(keys)}")
    return value


def _safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise MathFlowError(f"{label} must be a relative POSIX path")
    path = PurePosixPath(value)
    if (
        not value
        or value.startswith("-")
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != value
    ):
        raise MathFlowError(f"{label} must be a normalized relative POSIX path")
    return value


def _argument(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\0" in value or "\n" in value:
        raise MathFlowError(f"{label} must be a non-empty single-line string")
    if len(value.encode("utf-8")) > 4096:
        raise MathFlowError(f"{label} is too long")
    return value


def validate_verifier_spec(value: object, *, expected_id: str | None = None) -> dict[str, object]:
    spec = _strict_object(
        value,
        {
            "schemaVersion",
            "id",
            "description",
            "implementation",
            "environment",
            "command",
        },
        "verifier spec",
    )
    if spec["schemaVersion"] != 1 or isinstance(spec["schemaVersion"], bool):
        raise MathFlowError("verifier spec schemaVersion must be 1")
    verifier_id = spec["id"]
    if not isinstance(verifier_id, str):
        raise MathFlowError("verifier spec id must be a string")
    validate_slug(verifier_id, "verifier id")
    if expected_id is not None and verifier_id != expected_id:
        raise MathFlowError("verifier spec id does not match its filename")
    if not isinstance(spec["description"], str) or not spec["description"].strip():
        raise MathFlowError("verifier spec description must contain text")
    if spec["implementation"] not in SUPPORTED_IMPLEMENTATIONS:
        raise MathFlowError("verifier spec uses an unsupported implementation")

    environment = _strict_object(
        spec["environment"],
        {
            "kind",
            "image",
            "platform",
            "network",
            "readOnlyRoot",
            "user",
            "capabilities",
            "noNewPrivileges",
            "memoryBytes",
            "cpuCount",
            "pidsLimit",
            "tmpfsBytes",
        },
        "verifier environment",
    )
    if environment["kind"] != "oci":
        raise MathFlowError("verifier environment kind must be oci")
    if not isinstance(environment["image"], str) or not OCI_IMAGE.fullmatch(
        environment["image"]
    ):
        raise MathFlowError("verifier image must use an exact sha256 OCI digest")
    if environment["platform"] not in SUPPORTED_PLATFORMS:
        raise MathFlowError("verifier environment platform is unsupported")
    if environment["network"] != "none" or environment["readOnlyRoot"] is not True:
        raise MathFlowError(
            "verifier environment must disable networking and use a read-only root"
        )
    if (
        environment["user"] != "65534:65534"
        or environment["capabilities"] != []
        or environment["noNewPrivileges"] is not True
    ):
        raise MathFlowError(
            "verifier environment must run as nobody without capabilities or new privileges"
        )
    integer_limits = {
        "memoryBytes": (16 * 1024 * 1024, 16 * 1024 * 1024 * 1024),
        "cpuCount": (1, 32),
        "pidsLimit": (16, 4096),
        "tmpfsBytes": (1024 * 1024, 4 * 1024 * 1024 * 1024),
    }
    for key, (minimum, maximum) in integer_limits.items():
        item = environment[key]
        if isinstance(item, bool) or not isinstance(item, int) or not minimum <= item <= maximum:
            raise MathFlowError(f"verifier environment {key} is outside the allowed range")

    command = _strict_object(
        spec["command"],
        {
            "executable",
            "fixedArguments",
            "timeoutSeconds",
            "maximumOutputBytes",
            "successExitCodes",
        },
        "verifier command",
    )
    executable = _argument(command["executable"], "verifier executable")
    if any(character.isspace() for character in executable):
        raise MathFlowError("verifier executable may not contain whitespace")
    fixed = command["fixedArguments"]
    if not isinstance(fixed, list) or len(fixed) > 32:
        raise MathFlowError("verifier fixedArguments must be an array of at most 32 strings")
    for index, item in enumerate(fixed):
        _argument(item, f"verifier fixedArguments[{index}]")
    timeout = command["timeoutSeconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 3600:
        raise MathFlowError("verifier timeoutSeconds must be between 1 and 3600")
    maximum_output = command["maximumOutputBytes"]
    if (
        isinstance(maximum_output, bool)
        or not isinstance(maximum_output, int)
        or not 1024 <= maximum_output <= 16 * 1024 * 1024
    ):
        raise MathFlowError(
            "verifier maximumOutputBytes must be between 1024 and 16777216"
        )
    success_codes = command["successExitCodes"]
    if (
        not isinstance(success_codes, list)
        or not success_codes
        or len(success_codes) > 16
        or any(
            isinstance(item, bool)
            or not isinstance(item, int)
            or not 0 <= item <= 124
            for item in success_codes
        )
        or success_codes != sorted(set(success_codes))
    ):
        raise MathFlowError(
            "verifier successExitCodes must be unique sorted integers from 0 to 124"
        )
    return spec


def verifier_spec_digest(spec: dict[str, object]) -> str:
    validate_verifier_spec(spec)
    return f"sha256:{sha256_json(spec)}"


def load_verifier_spec(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read verifier spec {path}: {exc}") from exc
    return validate_verifier_spec(value, expected_id=path.stem)


def validate_verification_request(
    value: object,
    *,
    expected_verifier: dict[str, object] | None = None,
) -> dict[str, object]:
    request = _strict_object(
        value,
        {"schemaVersion", "verifier", "entrypoint", "arguments"},
        "verification request",
    )
    if request["schemaVersion"] != 1 or isinstance(request["schemaVersion"], bool):
        raise MathFlowError("verification request schemaVersion must be 1")
    verifier = _strict_object(
        request["verifier"], {"id", "specDigest"}, "verification request verifier"
    )
    verifier_id = verifier["id"]
    if not isinstance(verifier_id, str):
        raise MathFlowError("verification request verifier id must be a string")
    validate_slug(verifier_id, "verifier id")
    if not isinstance(verifier["specDigest"], str) or not DIGEST.fullmatch(
        verifier["specDigest"]
    ):
        raise MathFlowError("verification request verifier specDigest is invalid")
    _safe_relative_path(request["entrypoint"], "verification request entrypoint")
    arguments = request["arguments"]
    if not isinstance(arguments, list) or len(arguments) > 128:
        raise MathFlowError(
            "verification request arguments must be an array of at most 128 strings"
        )
    for index, item in enumerate(arguments):
        _argument(item, f"verification request arguments[{index}]")
    if expected_verifier is not None:
        if verifier["id"] != expected_verifier["id"]:
            raise MathFlowError("verification request names the wrong verifier")
        if verifier["specDigest"] != verifier_spec_digest(expected_verifier):
            raise MathFlowError("verification request verifier spec digest is stale")
    return request


def _load_json_at(root: Path, head: str, path: str, label: str) -> object:
    try:
        return json.loads(read_bytes_at(root, head, path))
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"{label} is not valid JSON: {exc}") from exc


def load_verifier_spec_at(root: Path, head: str, verifier_id: str) -> dict[str, object]:
    validate_slug(verifier_id, "verifier id")
    path = f"protocol/verifiers/{verifier_id}.json"
    return validate_verifier_spec(
        _load_json_at(root, head, path, "verifier spec"), expected_id=verifier_id
    )


def validate_contribution_verification_at(root: Path, head: str, prefix: str) -> None:
    request_path = f"{prefix}/{VERIFICATION_REQUEST}"
    if request_path not in list_files_at(root, head, prefix):
        return
    request_value = _load_json_at(root, head, request_path, "verification request")
    if not isinstance(request_value, dict):
        raise MathFlowError("verification request must be a JSON object")
    raw_verifier = request_value.get("verifier")
    verifier_id = raw_verifier.get("id") if isinstance(raw_verifier, dict) else None
    if not isinstance(verifier_id, str):
        raise MathFlowError("verification request verifier id must be a string")
    spec = load_verifier_spec_at(root, head, verifier_id)
    request = validate_verification_request(request_value, expected_verifier=spec)
    relative_files = {
        PurePosixPath(path).relative_to(PurePosixPath(prefix)).as_posix()
        for path in list_files_at(root, head, prefix)
    }
    if request["entrypoint"] not in relative_files:
        raise MathFlowError("verification request entrypoint is not a contribution artifact")


def validate_verifier_tree(root: Path) -> int:
    directory = root.resolve() / "protocol" / "verifiers"
    if not directory.exists():
        return 0
    if not directory.is_dir() or directory.is_symlink():
        raise MathFlowError(f"verifier registry must be a real directory: {directory}")
    count = 0
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.is_symlink() or path.suffix != ".json":
            raise MathFlowError(f"verifier registry may contain only JSON files: {path}")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MathFlowError(f"verifier spec is not valid JSON: {path}: {exc}") from exc
        validate_verifier_spec(value, expected_id=path.stem)
        count += 1
    return count


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool = False


Executor = Callable[[Path, dict[str, object], dict[str, object]], ExecutionResult]


def _run_bounded_process(
    invocation: list[str],
    *,
    timeout_seconds: int,
    maximum_output_bytes: int,
    cleanup: Callable[[], None] | None = None,
) -> ExecutionResult:
    """Run without allowing child output to grow host memory without bound."""

    try:
        process = subprocess.Popen(
            invocation,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise MathFlowError("Docker is required to execute an OCI verifier") from exc
    assert process.stdout is not None and process.stderr is not None
    selected = selectors.DefaultSelector()
    selected.register(process.stdout, selectors.EVENT_READ, "stdout")
    selected.register(process.stderr, selectors.EVENT_READ, "stderr")
    outputs = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout_seconds
    timed_out = False
    stopped = False
    try:
        while selected.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not stopped:
                timed_out = True
                stopped = True
                if cleanup is not None:
                    cleanup()
                process.kill()
            events = selected.select(max(0.0, min(remaining, 0.1)) if not stopped else 0.1)
            if not events and process.poll() is not None:
                events = [
                    (key, selectors.EVENT_READ) for key in list(selected.get_map().values())
                ]
            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selected.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                current_size = len(outputs["stdout"]) + len(outputs["stderr"])
                if current_size + len(chunk) > maximum_output_bytes:
                    if cleanup is not None:
                        cleanup()
                    process.kill()
                    process.wait(timeout=10)
                    raise MathFlowError(
                        "verifier output exceeded its governed maximumOutputBytes"
                    )
                outputs[str(key.data)].extend(chunk)
        process.wait(timeout=10)
    finally:
        selected.close()
        process.stdout.close()
        process.stderr.close()
        if process.poll() is None:
            if cleanup is not None:
                cleanup()
            process.kill()
            process.wait(timeout=10)
    return ExecutionResult(
        exit_code=None if timed_out else process.returncode,
        stdout=bytes(outputs["stdout"]),
        stderr=bytes(outputs["stderr"]),
        timed_out=timed_out,
    )


def docker_oci_executor(
    contribution_dir: Path,
    spec: dict[str, object],
    request: dict[str, object],
) -> ExecutionResult:
    validate_verifier_spec(spec)
    validate_verification_request(request, expected_verifier=spec)
    environment = spec["environment"]
    command = spec["command"]
    assert isinstance(environment, dict) and isinstance(command, dict)
    with tempfile.TemporaryDirectory(prefix="math-flow-verifier-container-") as temporary:
        cidfile = Path(temporary) / "container.cid"
        invocation = [
            "docker",
            "run",
            "--rm",
            "--cidfile",
            str(cidfile),
            "--network",
            "none",
            "--read-only",
            "--user",
            str(environment["user"]),
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(environment["pidsLimit"]),
            "--memory",
            str(environment["memoryBytes"]),
            "--cpus",
            str(environment["cpuCount"]),
            "--platform",
            str(environment["platform"]),
            "--mount",
            f"type=bind,src={contribution_dir.resolve()},dst=/work,readonly",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,size={environment['tmpfsBytes']}",
            "--workdir",
            "/work",
            str(environment["image"]),
            str(command["executable"]),
            *[str(item) for item in command["fixedArguments"]],
            str(request["entrypoint"]),
            *[str(item) for item in request["arguments"]],
        ]

        def cleanup() -> None:
            try:
                container_id = cidfile.read_text(encoding="utf-8").strip()
            except OSError:
                return
            if not container_id:
                return
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_id],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15,
                )
            except (OSError, subprocess.SubprocessError):
                pass

        return _run_bounded_process(
            invocation,
            timeout_seconds=int(command["timeoutSeconds"]),
            maximum_output_bytes=int(command["maximumOutputBytes"]),
            cleanup=cleanup,
        )


def _transaction(
    root: Path, problem: str, head: str, transaction: str
) -> tuple[dict[str, object], dict[str, object]]:
    source = ledger(root, problem, head)
    transaction_sha = resolve_commit(root, transaction)
    matches = [
        item for item in source["transactions"] if item["transactionId"] == transaction_sha
    ]
    if len(matches) != 1:
        raise MathFlowError("verifier subject is not a canonical contribution transaction")
    return source, matches[0]


def _input_index(root: Path, transaction: str, prefix: str) -> list[dict[str, object]]:
    prefix_path = PurePosixPath(prefix)
    inputs = []
    for path in list_files_at(root, transaction, prefix):
        relative = PurePosixPath(path).relative_to(prefix_path).as_posix()
        value = read_bytes_at(root, transaction, path)
        inputs.append(
            {"path": relative, "digest": sha256_bytes(value), "bytes": len(value)}
        )
    return inputs


def _materialize_inputs(
    root: Path, transaction: str, prefix: str, destination: Path
) -> None:
    for item in _input_index(root, transaction, prefix):
        relative = _safe_relative_path(item["path"], "attestation input path")
        target = destination.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(read_bytes_at(root, transaction, f"{prefix}/{relative}"))


def _load_subject(
    root: Path, problem: str, head: str, transaction: str
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    list[dict[str, object]],
]:
    source, item = _transaction(root, problem, head, transaction)
    transaction_sha = str(item["transactionId"])
    prefix = str(item["path"])
    request_path = f"{prefix}/{VERIFICATION_REQUEST}"
    files = list_files_at(root, transaction_sha, prefix)
    if request_path not in files:
        raise MathFlowError("contribution does not contain verification.json")
    raw_request = _load_json_at(
        root, transaction_sha, request_path, "verification request"
    )
    raw_verifier = raw_request.get("verifier") if isinstance(raw_request, dict) else None
    verifier_id = raw_verifier.get("id") if isinstance(raw_verifier, dict) else None
    if not isinstance(verifier_id, str):
        raise MathFlowError("verification request verifier id must be a string")
    spec = load_verifier_spec_at(root, transaction_sha, verifier_id)
    request = validate_verification_request(raw_request, expected_verifier=spec)
    inputs = _input_index(root, transaction_sha, prefix)
    if request["entrypoint"] not in {entry["path"] for entry in inputs}:
        raise MathFlowError("verification request entrypoint is not a contribution artifact")
    return source, item, request, spec, inputs


def _request_core(
    problem: str,
    item: dict[str, object],
    request: dict[str, object],
    spec: dict[str, object],
    inputs: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "subject": {
            "transactionId": item["transactionId"],
            "contributionId": item["contributionId"],
            "path": item["path"],
        },
        "verifier": {
            "id": spec["id"],
            "specDigest": verifier_spec_digest(spec),
            "implementation": spec["implementation"],
        },
        "environmentDigest": f"sha256:{sha256_json(spec['environment'])}",
        "entrypoint": request["entrypoint"],
        "arguments": request["arguments"],
        "inputs": inputs,
    }


def verification_requests(
    root: Path, problem: str, head: str = "HEAD"
) -> list[dict[str, object]]:
    """Return every canonical contribution that requests objective verification."""

    root = root.resolve()
    source = ledger(root, problem, head)
    requests: list[dict[str, object]] = []
    for item in source["transactions"]:
        if not isinstance(item, dict):
            continue
        transaction = str(item["transactionId"])
        prefix = str(item["path"])
        if f"{prefix}/{VERIFICATION_REQUEST}" not in list_files_at(
            root, transaction, prefix
        ):
            continue
        _, loaded_item, request, spec, inputs = _load_subject(
            root, problem, str(source["ledgerHead"]), transaction
        )
        core = _request_core(problem, loaded_item, request, spec, inputs)
        requests.append(
            {
                **core,
                "transactionId": loaded_item["transactionId"],
                "contributionId": loaded_item["contributionId"],
                "requestDigest": f"sha256:{sha256_json(core)}",
            }
        )
    return requests


def _published_attestation_entries(
    projection_root: Path, problem: str
) -> list[dict[str, object]]:
    root = projection_root.resolve()
    index_path = root / "indexes" / "problems" / problem / "runs.json"
    if not index_path.exists():
        return []
    try:
        values = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MathFlowError(f"could not read projection index {index_path}: {exc}") from exc
    if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
        raise MathFlowError(f"invalid projection index: {index_path}")
    entries: list[dict[str, object]] = []
    for item in values:
        if item.get("runKind") != "verifier-attestation":
            continue
        digest = item.get("runDigest")
        relative = item.get("path")
        if not isinstance(digest, str) or not isinstance(relative, str):
            raise MathFlowError("published verifier attestation index entry is incomplete")
        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise MathFlowError("published verifier attestation path escapes its root") from exc
        manifest, verified_digest = verify_bundle(target)
        if verified_digest != digest:
            raise MathFlowError("published verifier attestation digest does not match its index")
        inputs = manifest.get("inputs")
        request_digests = manifest.get("requestDigests")
        if (
            manifest.get("runKind") != "verifier-attestation"
            or manifest.get("problemId") != problem
            or not isinstance(inputs, dict)
            or not isinstance(inputs.get("transactionId"), str)
            or not isinstance(request_digests, list)
            or len(request_digests) != 1
            or not isinstance(request_digests[0], str)
        ):
            raise MathFlowError("published verifier attestation identity is invalid")
        entries.append(
            {
                "runDigest": digest,
                "requestDigest": request_digests[0],
                "transactionId": inputs["transactionId"],
                "path": target,
            }
        )
    return entries


def plan_verifier_attestation(
    root: Path,
    projection_root: Path,
    problem: str,
    transaction: str,
    head: str = "HEAD",
) -> dict[str, object]:
    """Plan one exact request without executing participant-controlled code."""

    root = root.resolve()
    source, item, request, spec, inputs = _load_subject(root, problem, head, transaction)
    request_core = _request_core(problem, item, request, spec, inputs)
    request_digest = f"sha256:{sha256_json(request_core)}"
    exact = [
        entry
        for entry in _published_attestation_entries(projection_root, problem)
        if entry["transactionId"] == item["transactionId"]
        and entry["requestDigest"] == request_digest
    ]
    for entry in exact:
        verify_verifier_attestation_bundle(
            root, Path(entry["path"]), str(source["ledgerHead"])
        )
    run_digests = sorted({str(entry["runDigest"]) for entry in exact})
    if len(run_digests) > 1:
        raise MathFlowError(
            "objective verification request has multiple published attestations"
        )
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "transactionId": item["transactionId"],
        "contributionId": item["contributionId"],
        "ledgerHead": source["ledgerHead"],
        "requestDigest": request_digest,
        "verifier": request_core["verifier"],
        "environmentDigest": request_core["environmentDigest"],
        "eligible": not run_digests,
        "reasonCode": "verification-request-pending"
        if not run_digests
        else "already-published",
        "publishedRunDigest": run_digests[0] if run_digests else None,
    }


def objective_attestation_status(
    root: Path,
    projection_root: Path,
    problem: str,
    transaction: str,
    head: str = "HEAD",
) -> dict[str, object]:
    """Resolve the terminal objective evidence required by one contribution.

    This is deliberately a projection-transport lookup, not a claim about the
    mathematics.  A returned terminal record has been verified against the
    canonical contribution, its pinned verifier, and the content-addressed
    published bundle.  Callers may therefore bind it into another immutable
    input without executing participant code.
    """

    root = root.resolve()
    projection_root = projection_root.resolve()
    source, item = _transaction(root, problem, head, transaction)
    transaction_id = str(item["transactionId"])
    prefix = str(item["path"])
    request_path = f"{prefix}/{VERIFICATION_REQUEST}"
    if request_path not in list_files_at(root, transaction_id, prefix):
        return {
            "schemaVersion": 1,
            "problemId": problem,
            "transactionId": transaction_id,
            "requested": False,
            "terminal": True,
            "requestDigest": None,
            "runDigest": None,
            "evidence": None,
        }

    plan = plan_verifier_attestation(
        root, projection_root, problem, transaction_id, str(source["ledgerHead"])
    )
    request_digest = str(plan["requestDigest"])
    run_digest = plan.get("publishedRunDigest")
    if not isinstance(run_digest, str):
        return {
            "schemaVersion": 1,
            "problemId": problem,
            "transactionId": transaction_id,
            "requested": True,
            "terminal": False,
            "requestDigest": request_digest,
            "runDigest": None,
            "evidence": None,
        }

    exact = [
        entry
        for entry in _published_attestation_entries(projection_root, problem)
        if entry["transactionId"] == transaction_id
        and entry["requestDigest"] == request_digest
        and entry["runDigest"] == run_digest
    ]
    if len(exact) != 1:
        raise MathFlowError(
            "objective verification request has no unique terminal attestation"
        )
    bundle = Path(str(exact[0]["path"]))
    details = verifier_attestation_details(
        root, bundle, str(source["ledgerHead"])
    )
    manifest, verified_run_digest = verify_bundle(bundle)
    artifacts = {
        str(artifact["role"]): {
            "digest": artifact["digest"],
            "bytes": artifact["bytes"],
        }
        for artifact in manifest["artifacts"]
        if isinstance(artifact, dict)
        and isinstance(artifact.get("role"), str)
    }
    evidence = {
        "schemaVersion": 1,
        "requestDigest": request_digest,
        "runDigest": verified_run_digest,
        "attestationId": details["attestationId"],
        "status": details["status"],
        "verifier": details["verifier"],
        "environmentDigest": details["environmentDigest"],
        "result": details["result"],
        "artifacts": artifacts,
        "stdout": details["stdout"],
        "stderr": details["stderr"],
    }
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "transactionId": transaction_id,
        "requested": True,
        "terminal": True,
        "requestDigest": request_digest,
        "runDigest": verified_run_digest,
        "evidence": evidence,
    }


def assert_attestation_publication_unique(
    projection_root: Path, bundle_dir: Path
) -> dict[str, str]:
    """Forbid two authoritative outcomes for one immutable request."""

    manifest, run_digest = verify_bundle(bundle_dir)
    if manifest.get("runKind") != "verifier-attestation":
        raise MathFlowError("attestation uniqueness check requires an attestation bundle")
    problem = manifest.get("problemId")
    inputs = manifest.get("inputs")
    request_digests = manifest.get("requestDigests")
    if (
        not isinstance(problem, str)
        or not isinstance(inputs, dict)
        or not isinstance(inputs.get("transactionId"), str)
        or not isinstance(request_digests, list)
        or len(request_digests) != 1
        or not isinstance(request_digests[0], str)
    ):
        raise MathFlowError("verifier attestation publication identity is invalid")
    for entry in _published_attestation_entries(projection_root, problem):
        if (
            entry["transactionId"] == inputs["transactionId"]
            and entry["requestDigest"] == request_digests[0]
            and entry["runDigest"] != run_digest
        ):
            raise MathFlowError(
                "objective verification request already has a different published attestation"
            )
    return {
        "problemId": problem,
        "transactionId": str(inputs["transactionId"]),
        "requestDigest": str(request_digests[0]),
        "runDigest": run_digest,
    }


def _result_record(result: ExecutionResult, success_codes: list[int]) -> dict[str, object]:
    if result.timed_out or result.exit_code is None:
        status = "error"
    elif result.exit_code in success_codes:
        status = "passed"
    elif result.exit_code in {125, 126, 127}:
        status = "error"
    else:
        status = "failed"
    return {
        "status": status,
        "exitCode": result.exit_code,
        "timedOut": result.timed_out,
    }


def run_verifier_attestation_bundle(
    root: Path,
    problem: str,
    transaction: str,
    head: str,
    output_dir: Path,
    *,
    executor: Executor | None = None,
) -> dict[str, object]:
    root = root.resolve()
    validate_slug(problem, "problem id")
    source, item, request, spec, inputs = _load_subject(
        root, problem, head, transaction
    )
    transaction_sha = str(item["transactionId"])
    request_core = _request_core(problem, item, request, spec, inputs)
    request_digest = f"sha256:{sha256_json(request_core)}"
    with tempfile.TemporaryDirectory(prefix="math-flow-verifier-") as temporary:
        materialized = Path(temporary) / "contribution"
        materialized.mkdir()
        _materialize_inputs(root, transaction_sha, str(item["path"]), materialized)
        execution = (executor or docker_oci_executor)(materialized, spec, request)
    if not isinstance(execution, ExecutionResult):
        raise MathFlowError("verifier executor returned an invalid result")
    if (execution.timed_out and execution.exit_code is not None) or (
        not execution.timed_out and execution.exit_code is None
    ):
        raise MathFlowError("verifier executor returned an inconsistent exit result")
    command = spec["command"]
    assert isinstance(command, dict)
    if len(execution.stdout) + len(execution.stderr) > int(
        command["maximumOutputBytes"]
    ):
        raise MathFlowError(
            "verifier output exceeded its governed maximumOutputBytes"
        )
    result = _result_record(execution, list(command["successExitCodes"]))
    outputs = {
        "stdout": {
            "digest": sha256_bytes(execution.stdout),
            "bytes": len(execution.stdout),
        },
        "stderr": {
            "digest": sha256_bytes(execution.stderr),
            "bytes": len(execution.stderr),
        },
    }
    attestation_core = {
        "schemaVersion": 1,
        "subject": request_core["subject"],
        "verifier": request_core["verifier"],
        "environment": spec["environment"],
        "environmentDigest": request_core["environmentDigest"],
        "requestDigest": request_digest,
        "inputs": inputs,
        "invocation": {
            "executable": command["executable"],
            "fixedArguments": command["fixedArguments"],
            "entrypoint": request["entrypoint"],
            "arguments": request["arguments"],
            "timeoutSeconds": command["timeoutSeconds"],
            "maximumOutputBytes": command["maximumOutputBytes"],
            "successExitCodes": command["successExitCodes"],
        },
        "result": result,
        "outputs": outputs,
        "producer": {
            "implementation": "math-flow-oci-attestation-producer-v1",
            "mathFlowVersion": __version__,
        },
    }
    attestation = {
        **attestation_core,
        "attestationId": f"sha256:{sha256_json(attestation_core)}",
    }
    bundle = ArtifactBundle(output_dir)
    bundle.add_json("attestation.json", attestation, "verifier-attestation")
    bundle.add_bytes(
        "stdout.log", execution.stdout, "verifier-stdout", "application/octet-stream"
    )
    bundle.add_bytes(
        "stderr.log", execution.stderr, "verifier-stderr", "application/octet-stream"
    )
    envelope = {
        "protocolVersion": 1,
        "runKind": "verifier-attestation",
        "problemId": problem,
        "ledgerHead": source["ledgerHead"],
        "problemLedgerHead": source["problemLedgerHead"],
        "problemLedgerDigest": source["problemLedgerDigest"],
        "runner": {
            "implementation": "math-flow-oci-attestation-producer-v1",
            "mathFlowVersion": __version__,
        },
        "verifier": request_core["verifier"],
        "baseRun": None,
        "outputProfile": "math-flow/verifier-attestation-v1",
        "requestDigests": [request_digest],
        "providerRuns": [],
        "inputs": {
            "transactionId": item["transactionId"],
            "contributionId": item["contributionId"],
            "verifierSpecDigest": request_core["verifier"]["specDigest"],
            "environmentDigest": request_core["environmentDigest"],
        },
    }
    return bundle.finalize(envelope)


def _validate_attestation_record(value: object) -> dict[str, object]:
    attestation = _strict_object(
        value,
        {
            "schemaVersion",
            "attestationId",
            "subject",
            "verifier",
            "environment",
            "environmentDigest",
            "requestDigest",
            "inputs",
            "invocation",
            "result",
            "outputs",
            "producer",
        },
        "verifier attestation",
    )
    if attestation["schemaVersion"] != 1:
        raise MathFlowError("verifier attestation schemaVersion must be 1")
    if not isinstance(attestation["attestationId"], str) or not DIGEST.fullmatch(
        attestation["attestationId"]
    ):
        raise MathFlowError("verifier attestation id is invalid")
    core = {key: value for key, value in attestation.items() if key != "attestationId"}
    if attestation["attestationId"] != f"sha256:{sha256_json(core)}":
        raise MathFlowError("verifier attestation id does not match its content")
    subject = _strict_object(
        attestation["subject"],
        {"transactionId", "contributionId", "path"},
        "verifier attestation subject",
    )
    if (
        not isinstance(subject["transactionId"], str)
        or not re.fullmatch(r"[0-9a-f]{40}", subject["transactionId"])
        or not isinstance(subject["contributionId"], str)
        or not isinstance(subject["path"], str)
    ):
        raise MathFlowError("verifier attestation subject is invalid")
    verifier = _strict_object(
        attestation["verifier"],
        {"id", "specDigest", "implementation"},
        "verifier attestation verifier",
    )
    if (
        not isinstance(verifier["id"], str)
        or not isinstance(verifier["specDigest"], str)
        or not DIGEST.fullmatch(verifier["specDigest"])
        or verifier["implementation"] not in SUPPORTED_IMPLEMENTATIONS
    ):
        raise MathFlowError("verifier attestation verifier is invalid")
    for key in ("environmentDigest", "requestDigest"):
        if not isinstance(attestation[key], str) or not DIGEST.fullmatch(attestation[key]):
            raise MathFlowError(f"verifier attestation {key} is invalid")
    result = _strict_object(
        attestation["result"], {"status", "exitCode", "timedOut"}, "verifier result"
    )
    if (
        result["status"] not in {"passed", "failed", "error"}
        or (
            result["exitCode"] is not None
            and (isinstance(result["exitCode"], bool) or not isinstance(result["exitCode"], int))
        )
        or not isinstance(result["timedOut"], bool)
        or (result["timedOut"] and result["exitCode"] is not None)
        or (not result["timedOut"] and result["exitCode"] is None)
    ):
        raise MathFlowError("verifier attestation result is invalid")
    producer = _strict_object(
        attestation["producer"],
        {"implementation", "mathFlowVersion"},
        "verifier attestation producer",
    )
    if (
        producer["implementation"] != "math-flow-oci-attestation-producer-v1"
        or not isinstance(producer["mathFlowVersion"], str)
        or not producer["mathFlowVersion"]
    ):
        raise MathFlowError("verifier attestation producer is invalid")
    return attestation


def verify_verifier_attestation_bundle(
    root: Path,
    bundle_dir: Path,
    head: str = "HEAD",
    *,
    replay: bool = False,
    executor: Executor | None = None,
) -> dict[str, object]:
    root = root.resolve()
    manifest, run_digest = verify_bundle(bundle_dir)
    _strict_object(
        manifest,
        {
            "protocolVersion",
            "runKind",
            "problemId",
            "ledgerHead",
            "problemLedgerHead",
            "problemLedgerDigest",
            "runner",
            "verifier",
            "baseRun",
            "outputProfile",
            "requestDigests",
            "providerRuns",
            "inputs",
            "artifacts",
        },
        "verifier attestation run manifest",
    )
    if (
        manifest.get("runKind") != "verifier-attestation"
        or manifest.get("outputProfile") != "math-flow/verifier-attestation-v1"
        or manifest.get("baseRun") is not None
        or manifest.get("providerRuns") != []
    ):
        raise MathFlowError("bundle is not a verifier attestation")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or {
        (item.get("path"), item.get("role"))
        for item in artifacts
        if isinstance(item, dict)
    } != {
        ("attestation.json", "verifier-attestation"),
        ("stdout.log", "verifier-stdout"),
        ("stderr.log", "verifier-stderr"),
    }:
        raise MathFlowError("verifier attestation bundle has an invalid artifact profile")
    try:
        attestation_value = json.loads(
            read_verified_artifact(bundle_dir, manifest, "verifier-attestation")
        )
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"verifier attestation is not valid JSON: {exc}") from exc
    attestation = _validate_attestation_record(attestation_value)
    stdout = read_verified_artifact(bundle_dir, manifest, "verifier-stdout")
    stderr = read_verified_artifact(bundle_dir, manifest, "verifier-stderr")
    outputs = _strict_object(
        attestation.get("outputs"), {"stdout", "stderr"}, "verifier attestation outputs"
    )
    for role, value in (("stdout", stdout), ("stderr", stderr)):
        record = outputs.get(role)
        if not isinstance(record, dict) or record != {
            "digest": sha256_bytes(value),
            "bytes": len(value),
        }:
            raise MathFlowError(f"verifier attestation {role} metadata is invalid")

    problem = manifest.get("problemId")
    ledger_head = manifest.get("ledgerHead")
    subject = attestation.get("subject")
    if (
        not isinstance(problem, str)
        or not isinstance(ledger_head, str)
        or not isinstance(subject, dict)
    ):
        raise MathFlowError("verifier attestation manifest identity is invalid")
    transaction_id = subject.get("transactionId")
    if not isinstance(transaction_id, str):
        raise MathFlowError("verifier attestation subject transaction is invalid")
    source, item, request, spec, inputs = _load_subject(
        root, problem, ledger_head, transaction_id
    )
    if source.get("ledgerHead") != ledger_head or resolve_commit(root, ledger_head) != ledger_head:
        raise MathFlowError("verifier attestation ledger head is not an exact commit ID")
    current_head = resolve_commit(root, head)
    if not is_ancestor(root, ledger_head, current_head):
        raise MathFlowError(
            "verifier attestation ledger head is not an ancestor of the requested head"
        )
    _transaction(root, problem, current_head, transaction_id)
    for key in ("problemLedgerHead", "problemLedgerDigest"):
        if manifest.get(key) != source.get(key):
            raise MathFlowError(f"verifier attestation has a forged or stale {key}")
    request_core = _request_core(problem, item, request, spec, inputs)
    request_digest = f"sha256:{sha256_json(request_core)}"
    if attestation.get("requestDigest") != request_digest:
        raise MathFlowError("verifier attestation request digest is stale")
    if attestation.get("subject") != request_core["subject"]:
        raise MathFlowError("verifier attestation subject is forged")
    if attestation.get("verifier") != request_core["verifier"]:
        raise MathFlowError("verifier attestation verifier identity is forged or stale")
    if attestation.get("environment") != spec["environment"] or attestation.get(
        "environmentDigest"
    ) != request_core["environmentDigest"]:
        raise MathFlowError("verifier attestation environment is unpinned or forged")
    if attestation.get("inputs") != inputs:
        raise MathFlowError("verifier attestation input index is forged or stale")
    command = spec["command"]
    assert isinstance(command, dict)
    if len(stdout) + len(stderr) > int(command["maximumOutputBytes"]):
        raise MathFlowError(
            "verifier attestation output exceeds its governed maximumOutputBytes"
        )
    expected_invocation = {
        "executable": command["executable"],
        "fixedArguments": command["fixedArguments"],
        "entrypoint": request["entrypoint"],
        "arguments": request["arguments"],
        "timeoutSeconds": command["timeoutSeconds"],
        "maximumOutputBytes": command["maximumOutputBytes"],
        "successExitCodes": command["successExitCodes"],
    }
    if attestation.get("invocation") != expected_invocation:
        raise MathFlowError("verifier attestation invocation is forged or stale")
    result = attestation.get("result")
    assert isinstance(result, dict)
    expected_status = _result_record(
        ExecutionResult(
            result["exitCode"],
            b"",
            b"",
            bool(result["timedOut"]),
        ),
        list(command["successExitCodes"]),
    )["status"]
    if result["status"] != expected_status:
        raise MathFlowError("verifier attestation result status is inconsistent")
    if manifest.get("verifier") != request_core["verifier"]:
        raise MathFlowError("verifier attestation manifest verifier identity is invalid")
    if manifest.get("runner") != attestation.get("producer"):
        raise MathFlowError("verifier attestation manifest producer is invalid")
    manifest_inputs = manifest.get("inputs")
    expected_manifest_inputs = {
        "transactionId": item["transactionId"],
        "contributionId": item["contributionId"],
        "verifierSpecDigest": request_core["verifier"]["specDigest"],
        "environmentDigest": request_core["environmentDigest"],
    }
    if manifest_inputs != expected_manifest_inputs or manifest.get("requestDigests") != [
        request_digest
    ]:
        raise MathFlowError("verifier attestation manifest inputs are invalid")

    if replay:
        with tempfile.TemporaryDirectory(prefix="math-flow-verifier-replay-") as temporary:
            materialized = Path(temporary) / "contribution"
            materialized.mkdir()
            _materialize_inputs(root, transaction_id, str(item["path"]), materialized)
            execution = (executor or docker_oci_executor)(materialized, spec, request)
        replay_result = _result_record(execution, list(command["successExitCodes"]))
        if replay_result != attestation.get("result"):
            raise MathFlowError("verifier attestation replay result does not match")
        if execution.stdout != stdout or execution.stderr != stderr:
            raise MathFlowError("verifier attestation replay output does not match")

    return {
        "schemaVersion": 1,
        "attestationId": attestation["attestationId"],
        "runDigest": run_digest,
        "problemId": problem,
        "transactionId": transaction_id,
        "status": attestation.get("result", {}).get("status")
        if isinstance(attestation.get("result"), dict)
        else None,
        "replayed": replay,
    }


def verifier_attestation_details(
    root: Path, bundle_dir: Path, head: str = "HEAD"
) -> dict[str, object]:
    """Return viewer/agent-safe detail after full canonical verification."""

    verified = verify_verifier_attestation_bundle(root, bundle_dir, head)
    manifest, run_digest = verify_bundle(bundle_dir)
    try:
        attestation = json.loads(
            read_verified_artifact(bundle_dir, manifest, "verifier-attestation")
        )
    except json.JSONDecodeError as exc:
        raise MathFlowError("verifier attestation is not valid JSON") from exc
    if not isinstance(attestation, dict):
        raise MathFlowError("verifier attestation record must be an object")
    stdout = read_verified_artifact(bundle_dir, manifest, "verifier-stdout")
    stderr = read_verified_artifact(bundle_dir, manifest, "verifier-stderr")

    def preview(value: bytes) -> dict[str, object]:
        maximum = 4096
        return {
            "text": value[:maximum].decode("utf-8", errors="replace"),
            "truncated": len(value) > maximum,
            "bytes": len(value),
            "digest": sha256_bytes(value),
        }

    return {
        **verified,
        "requestDigest": attestation["requestDigest"],
        "verifier": attestation["verifier"],
        "environmentDigest": attestation["environmentDigest"],
        "result": attestation["result"],
        "producer": attestation["producer"],
        "record": attestation,
        "stdout": preview(stdout),
        "stderr": preview(stderr),
        "runDigest": run_digest,
    }
