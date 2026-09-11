#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {
    "OK": 0,
    "INFO": 1,
    "WARNING": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def make_finding(
    severity: str,
    control_id: str,
    title: str,
    evidence: list[str] | None = None,
    recommendation: str | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "control_id": control_id,
        "title": title,
        "evidence": evidence or [],
        "recommendation": recommendation or "",
    }


def parse_sshd_config(lines: list[str]) -> dict[str, str]:
    config: dict[str, str] = {}

    for line in lines:
        parts = line.strip().split(None, 1)

        if len(parts) == 2:
            config[parts[0].lower()] = parts[1].strip().lower()

    return config


def parse_pipe_record(line: str, expected_fields: int) -> list[str] | None:
    fields = line.split("|")

    if len(fields) != expected_fields:
        return None

    return fields


def analyze_uid0(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    accounts = data.get("uid0_accounts", [])

    unexpected = []

    for entry in accounts:
        username = entry.split(":", 1)[0].strip()

        if username and username != "root":
            unexpected.append(entry)

    if unexpected:
        findings.append(
            make_finding(
                "HIGH",
                "LINUX-UID0-001",
                "Unexpected privileged account detected",
                unexpected,
                "Review every UID 0 account and remove unnecessary privileged identities.",
            )
        )

    return findings


def analyze_ssh(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    config = parse_sshd_config(data.get("sshd_config", []))

    permit_root = config.get("permitrootlogin")

    if permit_root == "yes":
        findings.append(
            make_finding(
                "HIGH",
                "SSH-ROOT-001",
                "Direct SSH root login is enabled",
                [f"permitrootlogin {permit_root}"],
                "Disable direct root login and use named administrative accounts with privilege escalation.",
            )
        )

    password_auth = config.get("passwordauthentication")

    if password_auth == "yes":
        findings.append(
            make_finding(
                "WARNING",
                "SSH-AUTH-001",
                "SSH password authentication is enabled",
                [f"passwordauthentication {password_auth}"],
                "Consider key-based authentication where operationally appropriate.",
            )
        )

    pubkey_auth = config.get("pubkeyauthentication")

    if pubkey_auth == "no":
        findings.append(
            make_finding(
                "WARNING",
                "SSH-KEY-001",
                "SSH public key authentication is disabled",
                [f"pubkeyauthentication {pubkey_auth}"],
                "Review the authentication policy and enable public key authentication if required.",
            )
        )

    return findings


def analyze_authorized_keys(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []

    for entry in data.get("authorized_keys", []):
        record = parse_pipe_record(entry, 6)

        if not record:
            continue

        path, owner, group, mode, size, modified = record

        try:
            permissions = int(mode, 8)
        except ValueError:
            continue

        if permissions & 0o022:
            findings.append(
                make_finding(
                    "WARNING",
                    "SSH-KEYPERM-001",
                    "authorized_keys file is writable by group or others",
                    [
                        f"path={path}",
                        f"owner={owner}:{group}",
                        f"mode={mode}",
                        f"size={size}",
                        f"modified={modified}",
                    ],
                    "Remove group or world write permissions from the authorized_keys file.",
                )
            )

    return findings


def analyze_web_role(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []

    if data.get("role") != "web":
        return findings

    wordpress_roots = data.get("wordpress_roots", [])

    if wordpress_roots:
        findings.append(
            make_finding(
                "INFO",
                "WEB-WP-001",
                "WordPress installation detected",
                wordpress_roots,
                "Apply the dedicated WordPress security checks to each detected installation.",
            )
        )

    return findings


def parse_postfix_config(lines: list[str]) -> dict[str, str]:
    config: dict[str, str] = {}

    for line in lines:
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        config[key.strip().lower()] = value.strip()

    return config


def analyze_mail_role(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []

    if data.get("role") != "mail":
        return findings

    postfix = parse_postfix_config(data.get("postfix_config", []))

    tls_protocols = postfix.get("smtpd_tls_protocols", "")
    mandatory_protocols = postfix.get("smtpd_tls_mandatory_protocols", "")

    combined_protocols = f"{tls_protocols} {mandatory_protocols}".lower()

    legacy_exclusions = ("!sslv2", "!sslv3", "!tlsv1", "!tlsv1.1")
    missing_exclusions = [
        protocol
        for protocol in legacy_exclusions
        if protocol not in combined_protocols
    ]

    if combined_protocols and missing_exclusions:
        findings.append(
            make_finding(
                "WARNING",
                "MAIL-TLS-001",
                "Postfix TLS protocol policy requires review",
                [
                    f"smtpd_tls_protocols={tls_protocols}",
                    f"smtpd_tls_mandatory_protocols={mandatory_protocols}",
                    "missing_explicit_exclusions="
                    + ",".join(missing_exclusions),
                ],
                "Review the supported TLS protocol policy against the security requirements of the environment.",
            )
        )

    for entry in data.get("clamav_socket", []):
        record = parse_pipe_record(entry, 4)

        if not record:
            continue

        path, owner, group, mode = record

        try:
            permissions = int(mode, 8)
        except ValueError:
            continue

        if permissions & 0o022:
            findings.append(
                make_finding(
                    "WARNING",
                    "MAIL-CLAMAV-001",
                    "ClamAV socket has permissive write permissions",
                    [
                        f"path={path}",
                        f"owner={owner}:{group}",
                        f"mode={mode}",
                    ],
                    "Restrict socket permissions according to the required service access model.",
                )
            )

    return findings


def analyze_host(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    findings.extend(analyze_uid0(data))
    findings.extend(analyze_ssh(data))
    findings.extend(analyze_authorized_keys(data))
    findings.extend(analyze_web_role(data))
    findings.extend(analyze_mail_role(data))

    if findings:
        status = max(
            (finding["severity"] for finding in findings),
            key=lambda severity: SEVERITY_ORDER[severity],
        )
    else:
        status = "OK"
        findings.append(
            make_finding(
                "OK",
                "AUDIT-OK-001",
                "No findings detected by the enabled checks",
            )
        )

    return {
        "host": data.get("host", "unknown"),
        "role": data.get("role", "generic"),
        "collected_at": data.get("collected_at"),
        "system": data.get("system", {}),
        "status": status,
        "findings": findings,
    }


def load_evidence(input_dir: Path) -> list[dict[str, Any]]:
    evidence = []

    for path in sorted(input_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        evidence.append(data)

    return evidence


def build_fleet_report(hosts: list[dict[str, Any]]) -> dict[str, Any]:
    host_status_summary = {
        severity: 0
        for severity in SEVERITY_ORDER
    }

    finding_summary = {
        severity: 0
        for severity in SEVERITY_ORDER
    }

    for host in hosts:
        status = host.get("status", "OK")

        if status in host_status_summary:
            host_status_summary[status] += 1

        for finding in host.get("findings", []):
            severity = finding.get("severity")

            if severity in finding_summary:
                finding_summary[severity] += 1

    return {
        "schema_version": "1.0",
        "host_count": len(hosts),
        "host_status_summary": host_status_summary,
        "finding_summary": finding_summary,
        "hosts": hosts,
    }

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Linux security audit evidence."
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("raw_data"),
        help="Directory containing host evidence JSON files.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/fleet-analysis.json"),
        help="Path of the generated fleet analysis JSON file.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input_dir.exists():
        raise SystemExit(
            f"Input directory does not exist: {args.input_dir}"
        )

    evidence = load_evidence(args.input_dir)

    if not evidence:
        raise SystemExit(
            f"No JSON evidence files found in: {args.input_dir}"
        )

    analyzed_hosts = [
        analyze_host(host_data)
        for host_data in evidence
    ]

    report = build_fleet_report(analyzed_hosts)

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(
            report,
            handle,
            indent=2,
            ensure_ascii=False,
        )
        handle.write("\n")

    print(
        f"Analyzed {len(analyzed_hosts)} host(s). "
        f"Report written to {args.output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
