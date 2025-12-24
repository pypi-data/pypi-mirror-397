from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import requests

DEFAULT_REGISTRY = "docker.io"
HTTP_TIMEOUT = 8


@dataclass(frozen=True)
class ImageRef:
    image: str
    registry: str
    repository: str
    tag: str


@dataclass(frozen=True)
class RegistryCheckResult:
    image: str
    exists: bool | None
    status: str
    detail: str | None = None
    http_status: int | None = None


def parse_image(image: str) -> ImageRef:
    """
    Parse a docker image string into registry/repo/tag components.

    Examples:
        python:3.11       -> registry docker.io, repo library/python, tag 3.11
        ghcr.io/org/app   -> registry ghcr.io, repo org/app, tag latest
        myorg/app         -> registry docker.io, repo myorg/app, tag latest
    """

    original = image.strip()
    if original.startswith("docker://"):
        original = original[len("docker://") :]

    digest: str | None = None
    name = original
    if "@" in original:
        name, digest = original.split("@", 1)

    registry = DEFAULT_REGISTRY
    remainder = name

    parts = name.split("/")
    if parts and (("." in parts[0]) or (":" in parts[0]) or parts[0] == "localhost"):
        registry = parts[0]
        remainder = "/".join(parts[1:])

    if ":" in remainder:
        repo_part, tag = remainder.rsplit(":", 1)
    else:
        repo_part, tag = remainder, digest or "latest"

    if registry == DEFAULT_REGISTRY and "/" not in repo_part:
        repo_part = f"library/{repo_part}"

    return ImageRef(image=original, registry=registry, repository=repo_part, tag=tag)


def check_docker_image_exists(image: str) -> RegistryCheckResult:
    """
    Validate that an image:tag exists on its registry using HTTP metadata endpoints only.

    Returns RegistryCheckResult with exists=True/False/None.
    """

    try:
        ref = parse_image(image)
    except Exception:
        return RegistryCheckResult(
            image=image, exists=False, status="invalid", detail="parse_failed"
        )

    registry = ref.registry.lower()
    if registry in {"docker.io", "registry.hub.docker.com", "registry-1.docker.io"}:
        return _check_dockerhub(ref)
    if registry == "ghcr.io":
        return _check_ghcr(ref)

    return RegistryCheckResult(
        image=image,
        exists=None,
        status="unsupported",
        detail=f"unsupported registry '{registry}'",
    )


def _check_dockerhub(ref: ImageRef) -> RegistryCheckResult:
    """
    Docker Hub tag lookup (no pull): https://hub.docker.com/v2/repositories/<repo>/tags/<tag>
    """

    url = f"https://hub.docker.com/v2/repositories/{ref.repository}/tags/{ref.tag}"
    return _http_registry_probe(ref, url)


def _check_ghcr(ref: ImageRef) -> RegistryCheckResult:
    """
    GHCR manifest lookup: GET https://ghcr.io/v2/<repo>/manifests/<tag>
    """

    url = f"https://ghcr.io/v2/{ref.repository}/manifests/{ref.tag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    return _http_registry_probe(ref, url, headers=headers)


def _http_registry_probe(
    ref: ImageRef, url: str, headers: Optional[dict[str, str]] = None
) -> RegistryCheckResult:
    try:
        resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
    except requests.RequestException as exc:
        return RegistryCheckResult(
            image=ref.image,
            exists=None,
            status="network_error",
            detail=str(exc),
        )

    status = resp.status_code

    if status == 200:
        return RegistryCheckResult(image=ref.image, exists=True, status="ok", http_status=status)

    if status == 401:
        return RegistryCheckResult(
            image=ref.image,
            exists=False,
            status="unauthorized",
            detail="authentication required or image is private",
            http_status=status,
        )

    if status == 404:
        return RegistryCheckResult(
            image=ref.image,
            exists=False,
            status="not_found",
            detail="image not found",
            http_status=status,
        )

    if status in {429, 503}:
        return RegistryCheckResult(
            image=ref.image,
            exists=None,
            status="transient_error",
            detail=f"transient registry error ({status})",
            http_status=status,
        )

    return RegistryCheckResult(
        image=ref.image,
        exists=None,
        status="error",
        detail=f"unexpected status {status}",
        http_status=status,
    )


IMAGE_PATTERN = re.compile(r"(?m)^\s*(image|container)\s*:\s*['\"]?([^'\"\\s]+)")
USES_PATTERN = re.compile(r"docker://([^\s'\"`]+)")


def scan_images_fallback(text: str) -> set[str]:
    """
    Heuristic fallback: extract image-like strings from raw YAML when a parser isn't available.
    """

    found = set()
    for match in IMAGE_PATTERN.finditer(text):
        candidate = match.group(2).strip()
        if candidate:
            found.add(candidate)
    for match in USES_PATTERN.finditer(text):
        candidate = match.group(1).strip()
        if candidate:
            found.add(candidate)
    return found
