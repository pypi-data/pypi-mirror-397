from __future__ import annotations

import datetime as dt
import hashlib
import json
from typing import Any, Callable, Iterable, List, Optional

from infrapilot_cli.auth.integration.aws_auth import AWSAuthenticator
from infrapilot_cli.core.logging import component_logger

try:  # Optional dependency is already in requirements
    import boto3  # type: ignore
    from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
except Exception:  # pragma: no cover - handled in Auth
    boto3 = None  # type: ignore
    BotoCoreError = ClientError = Exception  # type: ignore

LOGGER = component_logger("cli.discovery.aws", name=__name__)


def run_discovery(authenticator: AWSAuthenticator) -> dict[str, Any]:
    """
    Collect a lightweight AWS snapshot using the provided authenticator.
    """

    ctx = authenticator.validate()
    session = ctx.session
    if session is None and boto3:
        session = boto3.Session(profile_name=ctx.profile)

    if session is None:
        raise RuntimeError("AWS session unavailable for discovery.")

    region = session.region_name or "us-east-1"

    ec2 = session.client("ec2", region_name=region)
    ecs = session.client("ecs", region_name=region)
    ecr = session.client("ecr", region_name=region)
    lam = session.client("lambda", region_name=region)
    s3 = session.client("s3", region_name=region)
    rds = session.client("rds", region_name=region)
    iam = session.client("iam")

    snapshot: dict[str, Any] = {
        "account_id": ctx.account_id,
        "region": region,
        "vpcs": _safe(ec2, "vpcs", lambda: _list_vpcs(ec2)),
        "ec2_instances": _safe(ec2, "ec2_instances", lambda: _list_ec2_instances(ec2)),
        "subnets": _safe(ec2, "subnets", lambda: _list_subnets(ec2)),
        "security_groups": _safe(ec2, "security_groups", lambda: _list_security_groups(ec2)),
        "ecr_repositories": _safe(ecr, "ecr_repositories", lambda: _list_ecr(ecr)),
        "ecs_clusters": _safe(ecs, "ecs_clusters", lambda: _list_ecs_clusters(ecs)),
        "ecs_services": _safe(ecs, "ecs_services", lambda: _list_ecs_services(ecs)),
        "lambda_functions": _safe(lam, "lambda_functions", lambda: _list_lambda(lam)),
        "s3_buckets": _safe(s3, "s3_buckets", lambda: _list_s3_buckets(s3)),
        "rds_instances": _safe(rds, "rds_instances", lambda: _list_rds(rds)),
        "iam_roles": _safe(iam, "iam_roles", lambda: _list_iam_roles(iam)),
    }

    return _json_ready(snapshot)


def snapshot_hash(snapshot: dict[str, Any]) -> str:
    normalized = _normalize(snapshot)
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Collectors ------------------------------------------------------------------


def _list_vpcs(ec2) -> List[dict]:
    resp = ec2.describe_vpcs()
    return [
        {"vpc_id": v.get("VpcId"), "name": _tag(v, "Name")}
        for v in resp.get("Vpcs", [])
        if v.get("VpcId")
    ]


def _list_ec2_instances(ec2) -> List[dict]:
    paginator = ec2.get_paginator("describe_instances")
    instances: List[dict] = []
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                instance_id = inst.get("InstanceId")
                if not instance_id:
                    continue
                security_groups: List[dict] = []
                for sg in inst.get("SecurityGroups", []):
                    sg_id = sg.get("GroupId")
                    sg_name = sg.get("GroupName")
                    if sg_id or sg_name:
                        security_groups.append({"group_id": sg_id, "name": sg_name})
                instances.append(
                    {
                        "instance_id": instance_id,
                        "name": _tag(inst, "Name"),
                        "state": (inst.get("State") or {}).get("Name"),
                        "instance_type": inst.get("InstanceType"),
                        "az": (inst.get("Placement") or {}).get("AvailabilityZone"),
                        "vpc_id": inst.get("VpcId"),
                        "subnet_id": inst.get("SubnetId"),
                        "public_ip": inst.get("PublicIpAddress"),
                        "private_ip": inst.get("PrivateIpAddress"),
                        "security_groups": security_groups,
                    }
                )
    return instances


def _list_subnets(ec2) -> List[dict]:
    resp = ec2.describe_subnets()
    return [
        {
            "subnet_id": s.get("SubnetId"),
            "vpc_id": s.get("VpcId"),
            "az": s.get("AvailabilityZone"),
            "name": _tag(s, "Name"),
        }
        for s in resp.get("Subnets", [])
        if s.get("SubnetId")
    ]


def _list_security_groups(ec2) -> List[dict]:
    resp = ec2.describe_security_groups()
    return [
        {
            "group_id": sg.get("GroupId"),
            "name": sg.get("GroupName"),
            "vpc_id": sg.get("VpcId"),
        }
        for sg in resp.get("SecurityGroups", [])
        if sg.get("GroupId")
    ]


def _list_ecr(ecr) -> List[dict]:
    repos: List[dict] = []
    paginator = ecr.get_paginator("describe_repositories")
    for page in paginator.paginate():
        for repo in page.get("repositories", []):
            name = repo.get("repositoryName")
            uri = repo.get("repositoryUri")
            if name:
                repos.append({"name": name, "uri": uri})
    return repos


def _list_ecs_clusters(ecs) -> List[dict]:
    paginator = ecs.get_paginator("list_clusters")
    clusters: List[dict] = []
    for page in paginator.paginate():
        for arn in page.get("clusterArns", []):
            clusters.append({"name": arn.split("/")[-1], "arn": arn})
    return clusters


def _list_ecs_services(ecs) -> List[dict]:
    services: List[dict] = []
    clusters = [c["arn"] for c in _list_ecs_clusters(ecs) if c.get("arn")]  # type: ignore[index]
    for cluster in clusters:
        paginator = ecs.get_paginator("list_services")
        for page in paginator.paginate(cluster=cluster):
            for arn in page.get("serviceArns", []):
                services.append(
                    {
                        "cluster": cluster.split("/")[-1],
                        "service": arn.split("/")[-1],
                        "arn": arn,
                    }
                )
    return services


def _list_lambda(lam) -> List[dict]:
    funcs: List[dict] = []
    paginator = lam.get_paginator("list_functions")
    for page in paginator.paginate():
        for fn in page.get("Functions", []):
            name = fn.get("FunctionName")
            if name:
                funcs.append(
                    {
                        "function_name": name,
                        "runtime": fn.get("Runtime"),
                        "memory": fn.get("MemorySize"),
                        "timeout": fn.get("Timeout"),
                        "role": fn.get("Role"),
                    }
                )
    return funcs


def _list_s3_buckets(s3) -> List[dict]:
    resp = s3.list_buckets()
    return [{"name": b.get("Name")} for b in resp.get("Buckets", []) if b.get("Name")]


def _list_rds(rds) -> List[dict]:
    resp = rds.describe_db_instances()
    items: List[dict] = []
    for db in resp.get("DBInstances", []):
        identifier = db.get("DBInstanceIdentifier")
        if identifier:
            items.append(
                {
                    "identifier": identifier,
                    "engine": db.get("Engine"),
                    "engine_version": db.get("EngineVersion"),
                    "status": db.get("DBInstanceStatus"),
                    "instance_class": db.get("DBInstanceClass"),
                }
            )
    return items


def _list_iam_roles(iam) -> List[dict]:
    roles: List[dict] = []
    paginator = iam.get_paginator("list_roles")
    for page in paginator.paginate():
        for role in page.get("Roles", []):
            name = role.get("RoleName")
            arn = role.get("Arn")
            if name or arn:
                roles.append({"name": name, "arn": arn})
    return roles


# Helpers --------------------------------------------------------------------


def _safe(client, label: str, fn: Callable[[], Iterable[dict]]) -> List[dict]:
    try:
        return list(fn())
    except (BotoCoreError, ClientError) as exc:
        LOGGER.warning("aws.discovery.partial_failure", service=label, error=str(exc))
        return []
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("aws.discovery.partial_failure", service=label, error=str(exc))
        return []


def _tag(resource: dict, key: str) -> Optional[str]:
    for tag in resource.get("Tags", []) or []:
        if tag.get("Key") == key:
            return tag.get("Value")
    return None


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_json_ready(v) for v in value if v is not None]
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    return value


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {k: _normalize(v) for k, v in value.items()}
        return dict(sorted(cleaned.items(), key=lambda item: item[0]))
    if isinstance(value, list):
        normalized_list = [_normalize(v) for v in value]
        try:
            return sorted(normalized_list, key=lambda x: json.dumps(x, sort_keys=True))
        except Exception:
            return normalized_list
    return value
