# Linux Security Fleet Audit Toolkit

Automated, non-destructive security auditing for Linux server fleets using **Ansible**, **Python** and **Bash**.

The toolkit collects security-relevant evidence from Linux systems, evaluates it through security rules and approved baselines, classifies findings by severity and generates structured reports for operational review.

> **Public Edition**
>
> This repository contains a sanitized demonstration version of a toolkit designed around real-world system administration and defensive security auditing requirements.
>
> All hosts, IP addresses, credentials, findings and demonstration data included in this repository are fictitious.

---

## Overview

Linux Security Fleet Audit Toolkit turns repetitive security verification tasks into a repeatable and auditable workflow.

The project separates:

- evidence collection;
- security analysis;
- baseline comparison;
- role-aware checks;
- reporting.

The audit process is designed to be **non-destructive**.

The toolkit detects and documents conditions that require review, but it does not automatically modify audited systems or remediate detected findings.

---

## Architecture

```text
Linux Hosts
    |
    v
Ansible Evidence Collection
    |
    v
Structured Host Evidence
    |
    v
Python Analysis Engine
    |
    +--> Generic Security Rules
    +--> Baseline Drift Detection
    +--> Role-Aware Checks
    |
    v
Severity-Classified Findings
    |
    +--> JSON Analysis
    +--> HTML Security Report
    |
    v
Operational Security Review
```

This separation keeps collection, analysis and reporting independent and easier to audit.

---

## Key Features

- Multi-host Linux evidence collection with Ansible
- Non-destructive security assessment
- Python-based analysis engine
- SSH security checks
- Privileged account review
- `authorized_keys` permission analysis
- Approved baseline comparison
- Configuration drift detection
- Role-aware web and mail server checks
- Postfix TLS policy analysis
- ClamAV socket permission analysis
- WordPress installation detection
- Severity-based classification
- Structured JSON output
- Professional HTML security report
- One-command sanitized demonstration mode
- systemd service and timer templates
- Separation between demonstration data and live evidence
- Designed for repeatable and auditable operations

---

## Baseline Drift Detection

The analyzer can compare collected configuration against an approved per-host baseline.

For example:

```text
Expected:
permitrootlogin no

Current:
permitrootlogin yes

Result:
HIGH - SSH configuration differs from approved baseline
```

The Public Edition includes a fictitious baseline for `demo-web-01`.

Baseline differences are reported as findings and do not trigger automatic remediation.

---

## Role-Aware Analysis

Checks are applied according to the declared server role.

### Generic Linux

Current checks include:

- unexpected UID 0 accounts;
- SSH root login;
- SSH password authentication;
- SSH public-key authentication;
- unsafe `authorized_keys` permissions.

### Web role

Current Public Edition checks include:

- WordPress installation detection.

The architecture is designed so additional web security controls can be added without modifying the evidence model for unrelated hosts.

### Mail role

Current checks include:

- Postfix TLS protocol policy review;
- ClamAV socket permission analysis.

Role-aware execution helps reduce irrelevant findings and keeps reports focused on the function of each system.

---

## Severity Model

| Severity | Meaning |
|---|---|
| `CRITICAL` | Immediate security risk requiring urgent investigation |
| `HIGH` | Significant weakness or configuration drift requiring prompt review |
| `WARNING` | Security or configuration condition that should be assessed |
| `INFO` | Informational or contextual finding |
| `OK` | No relevant finding detected by the enabled checks |

The overall status of each host is determined by its highest active finding.

---

## Quick Start

The repository includes fully fictitious evidence and baseline data, allowing the complete analysis and reporting pipeline to be tested without connecting to any server.

Clone the repository:

```bash
git clone https://github.com/matteodilonardo41/linux-security-fleet-audit-toolkit.git
cd linux-security-fleet-audit-toolkit
```

Run the sanitized demonstration:

```bash
./run-audit.sh demo
```

The demo automatically:

1. loads fictitious host evidence;
2. loads the approved demo baseline;
3. runs the Python security analysis;
4. performs baseline drift detection;
5. classifies findings;
6. generates JSON output;
7. generates the HTML security report.

Generated files are written under:

```text
reports/
```

Generated reports are intentionally excluded from Git tracking.

---

## Live Collection

Live collection uses the Ansible evidence collector:

```bash
./run-audit.sh collect <inventory>
```

Example:

```bash
./run-audit.sh collect inventories/demo.ini
```

> The included inventory contains documentation-only TEST-NET addresses and is not intended to represent a real infrastructure.

Before using collection mode in a real environment, create your own private inventory and review the playbook and privilege requirements.

Production inventories, collected evidence and generated reports should never be committed to the public repository.

---

## Requirements

### Python

Python **3.10 or newer** is required.

The Public Edition has been tested with:

```text
Python 3.12.3
```

The analysis and HTML reporting components use only the Python Standard Library.

### Ansible

Ansible is required only for live evidence collection.

Install the project dependency with:

```bash
python3 -m pip install -r requirements.txt
```

Current requirement:

```text
ansible-core>=2.16
```

Development testing was performed with:

```text
ansible-core 2.21.2
```

---

## Demo Environment

The repository uses fictitious systems such as:

```text
demo-web-01
demo-mail-01
demo-monitoring-01
demo-app-01
```

The demonstration inventory uses RFC 5737 TEST-NET addresses:

```text
192.0.2.10
192.0.2.20
192.0.2.30
192.0.2.40
```

No real infrastructure data is required to run demo mode.

---

## Project Structure

```text
linux-security-fleet-audit-toolkit/
├── analyzer/
│   ├── analyzer.py
│   └── report_html.py
├── baselines/
│   └── demo/
├── docs/
│   ├── architecture.md
│   └── controls.md
├── examples/
│   └── demo-evidence/
├── inventories/
│   └── demo.ini
├── playbooks/
│   └── audit.yml
├── reports/
├── systemd/
│   ├── linux-security-fleet-audit.service
│   └── linux-security-fleet-audit.timer
├── .gitignore
├── README.md
├── requirements.txt
└── run-audit.sh
```

---

## Evidence and Privacy Model

Collected evidence can contain infrastructure-sensitive information.

For this reason, the repository is configured to exclude:

- collected raw evidence;
- generated reports;
- production inventories;
- production baselines;
- secrets and environment files;
- private keys and certificates.

Only sanitized demonstration data should be committed to this repository.

---

## Scheduling

Example systemd templates are included under:

```text
systemd/
```

The example timer runs once per day and uses:

```ini
Persistent=true
RandomizedDelaySec=15m
```

The templates intentionally use the generic installation path:

```text
/opt/linux-security-fleet-audit-toolkit
```

They should be reviewed and adapted before installation.

---

## Technology Stack

- Linux
- Ansible
- Python
- Bash
- systemd
- JSON
- HTML

---

## Security Philosophy

The toolkit follows a simple principle:

> **Detect, classify, document — then let the administrator decide how to remediate.**

Security auditing and remediation are intentionally separated.

This reduces unintended changes and preserves administrative control over production systems.

---

## Disclaimer

This project is intended for system administration, defensive security auditing and educational purposes.

Review the source code, configuration, baselines and collection requirements before using it against production systems.

---

## Author

**Matteo Di Lonardo**

System Administrator focused on Linux infrastructure, automation, virtualization, monitoring and defensive security.
