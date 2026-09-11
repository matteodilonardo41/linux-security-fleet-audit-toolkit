# Linux Security Fleet Audit Toolkit

Automated, non-destructive security auditing for Linux server fleets using **Ansible** and **Python**.

The toolkit collects security-relevant evidence from multiple Linux systems, evaluates it through configurable rules and baselines, classifies findings by severity, and generates structured reports for operational review.

> **Public Edition**
>
> This repository contains a sanitized demonstration version of a toolkit originally designed around real-world system administration and security auditing requirements.
>
> All hosts, domains, IP addresses, credentials, findings, and example data included in this repository are fictitious.

---

## Overview

The project is designed to turn repetitive Linux security checks into a repeatable, auditable and non-destructive workflow.

It focuses on visibility and assessment and does **not** automatically remediate detected issues or modify audited systems.


---

## Architecture

The audit workflow follows a simple and auditable pipeline:

```text
Linux Hosts
    |
    v
Ansible Evidence Collection
    |
    v
Python Analysis Engine
    |
    +--> Security Rules
    +--> Baseline Comparison
    +--> Role-Aware Checks
    |
    v
Structured Findings
    |
    +--> JSON Output
    +--> HTML Report
    +--> PDF Report
    |
    v
Operational Security Review
```

This separation keeps evidence collection, analysis logic and reporting clearly isolated.

---

## Key Features

- Multi-host Linux auditing with Ansible
- Non-destructive and read-only evidence collection
- Python-based security analysis engine
- Baseline drift detection
- Role-aware checks for different server types
- Severity-based classification of findings
- Structured JSON output
- Human-readable HTML and PDF reporting
- Scheduled execution support with systemd
- Designed for repeatable and auditable operations

---

## Security Areas

The Public Edition demonstrates checks across multiple security domains, including:

- Privileged and administrative access
- SSH configuration and authorized keys
- Configuration and baseline drift
- Scheduled persistence mechanisms
- systemd services and timers
- Network and service exposure
- Mail server security
- Postfix TLS configuration
- SASL authentication anomalies
- DKIM validation
- ClamAV integration and permissions
- Web and WordPress security
- WPScan-based vulnerability assessment
- XML-RPC exposure
- Publicly accessible WordPress files and endpoints
- Rootkit and malware scanner findings

Role-specific checks are applied only to systems where they are relevant, reducing noise and unnecessary findings.

---

## Severity Model

Findings are classified using five severity levels:

| Severity | Meaning |
|---|---|
| `CRITICAL` | Immediate security risk requiring urgent investigation |
| `HIGH` | Significant weakness or suspicious condition requiring prompt review |
| `WARNING` | Configuration or security condition that should be assessed |
| `INFO` | Informational finding, known condition or low-priority exposure |
| `OK` | Check completed without relevant findings |

The overall status of each host is determined by the highest active severity detected during the audit.

---

## Project Structure

```text
linux-security-fleet-audit-toolkit/
├── analyzer/
├── baselines/
├── docs/
├── examples/
├── inventories/
├── playbooks/
├── reports/
├── systemd/
├── .gitignore
├── README.md
├── requirements.txt
└── run-audit.sh
```

The Public Edition separates demonstration content from production data and real environment specific configuration.

---

## Demo Environment

The public repository uses fictitious systems such as:

```text
demo-web-01
demo-mail-01
demo-monitoring-01
demo-app-01
```
All IP, hostname, domain, credential and finding data used in examples are intentionally fictitious.

---

## Technology Stack

- Linux
- Ansible
- Python 3
- Bash
- systemd
- JSON
- HTML
- PDF reporting

---

## Disclaimer

This project is intended for system administration, defensive security auditing and educational purposes.

Always review the source code, rules and configuration before using the toolkit in a production environment.

---

## Author

**Matteo Di Lonardo**

System Administrator focused on Linux infrastructure, automation, virtualization, monitoring and defensive security.
