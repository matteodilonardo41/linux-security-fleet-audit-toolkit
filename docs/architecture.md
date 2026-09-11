# Architecture

## Purpose

Linux Security Fleet Audit Toolkit separates security evidence collection, analysis and reporting into independent stages.

The architecture is intentionally designed around a non-destructive audit model.

Audited systems are inspected and evaluated, while remediation remains a separate administrative activity.

---

## Processing Pipeline

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

Each stage has a clearly defined responsibility.

This separation makes the workflow easier to review, test and extend.

---

## Main Components

The Public Edition is composed of four main layers:

```text
Collection
Analysis
Reporting
Orchestration
```

Supporting configuration is provided for:

```text
Inventories
Baselines
Scheduling
Demo data
```

---

## Evidence Collection

Evidence collection is performed by Ansible through:

```text
playbooks/audit.yml
```

The playbook connects to the systems defined in an inventory and gathers security-relevant information.

The collector is designed to inspect systems without intentionally modifying their security configuration.

---

## Collected Host Evidence

The current Public Edition collects information including:

```text
UID 0 accounts
effective SSH configuration
authorized_keys metadata
cron persistence files
systemd timers
listening network sockets
WordPress installation indicators
Postfix effective configuration
ClamAV socket metadata
```

Evidence is converted into structured JSON data for subsequent analysis.

Example structure:

```text
raw_data/
├── host-01.json
├── host-02.json
└── host-03.json
```

The `raw_data` directory is intentionally excluded from Git tracking.

Collected evidence may contain infrastructure-sensitive information and should therefore remain private.

---

## Evidence Schema

Each host evidence document contains general metadata such as:

```text
schema_version
host
role
collected_at
system
```

along with the collected security evidence.

Example conceptual structure:

```json
{
  "schema_version": "1.0",
  "host": "demo-web-01",
  "role": "web",
  "system": {},
  "uid0_accounts": [],
  "sshd_config": [],
  "authorized_keys": []
}
```

The Public Edition contains only fictitious demonstration evidence.

---

## Python Analysis Engine

Security analysis is performed by:

```text
analyzer/analyzer.py
```

The analyzer loads host evidence and evaluates it against the currently implemented security controls.

It converts detected conditions into structured findings.

Each finding contains:

```text
severity
control_id
title
evidence
recommendation
```

---

## Generic Security Analysis

Generic Linux controls can be applied independently of the functional role of the server.

Current examples include:

```text
unexpected UID 0 accounts
SSH root login
SSH password authentication
SSH public-key authentication
authorized_keys permissions
```

This allows common Linux security checks to be evaluated consistently across the fleet.

---

## Baseline Drift Detection

The analyzer optionally accepts approved host baselines.

Baselines are stored separately from collected evidence.

Example:

```text
baselines/
└── demo/
    └── demo-web-01.json
```

A baseline represents the expected approved configuration for a host.

The current Public Edition demonstrates comparison of SSH settings such as:

```text
permitrootlogin
passwordauthentication
pubkeyauthentication
```

The analyzer compares:

```text
Observed configuration
```

against:

```text
Approved baseline
```

and generates a finding when they differ.

Example:

```text
Expected: permitrootlogin no
Current:  permitrootlogin yes

Result:
BASELINE-SSH-001
HIGH
```

Baseline drift detection does not automatically restore configuration.

The finding is provided for administrator review.

---

## Role-Aware Analysis

Hosts can be assigned a functional role through the inventory.

The demonstration environment includes roles such as:

```text
generic
web
mail
monitoring
```

Generic controls remain applicable across the fleet.

Additional controls are evaluated according to the assigned role.

---

## Web Role

Hosts assigned the:

```text
web
```

role receive web-specific analysis.

The current Public Edition detects WordPress installations based on evidence collected from `wp-config.php` files.

Current control:

```text
WEB-WP-001
```

The Public Edition currently performs WordPress installation detection only.

It does not perform active vulnerability scanning or exploitation testing.

---

## Mail Role

Hosts assigned the:

```text
mail
```

role receive mail-specific analysis.

Current controls include:

```text
MAIL-TLS-001
MAIL-CLAMAV-001
```

These evaluate:

```text
Postfix TLS protocol policy
ClamAV socket permissions
```

Mail-specific controls are not applied to unrelated server roles.

---

## Collected Evidence vs Implemented Controls

The architecture intentionally separates evidence collection from analysis rules.

Some information can be collected before a dedicated classification rule exists.

For example, the current collector gathers:

```text
cron files
systemd timers
listening sockets
```

but the Public Edition does not currently convert all of these data points into dedicated findings.

This design allows new analysis controls to be added without redesigning the collection layer.

---

## Severity Model

Findings use the following severity hierarchy:

```text
CRITICAL
HIGH
WARNING
INFO
OK
```

The analyzer calculates the overall status of each host according to its highest active finding.

For example:

```text
Host findings:

WARNING
INFO
HIGH

Overall host status:

HIGH
```

---

## Fleet Analysis

Individual host results are combined into a fleet-level analysis.

The generated JSON contains information including:

```text
host_count
host_status_summary
finding_summary
hosts
```

This allows both machine-readable processing and human-readable reporting.

---

## Reporting Layer

HTML reporting is performed by:

```text
analyzer/report_html.py
```

The report generator reads the fleet analysis JSON and produces a human-readable security report.

The current report includes:

```text
overall fleet status
severity counters
host inventory
host roles
operating system information
technical findings
control identifiers
evidence
recommendations
```

Generated reports are written under:

```text
reports/
```

This directory is excluded from Git tracking.

---

## Orchestration Wrapper

The main operational entry point is:

```text
run-audit.sh
```

The wrapper coordinates analysis and report generation.

It currently supports two operating modes:

```text
demo
collect
```

---

## Demo Mode

Demo mode can be launched with:

```bash
./run-audit.sh demo
```

The workflow uses:

```text
examples/demo-evidence/
baselines/demo/
```

No connection to external Linux systems is required.

The demo performs:

```text
Load fictitious evidence
Load fictitious approved baseline
Run security analysis
Detect configuration drift
Generate fleet JSON
Generate HTML security report
```

This makes the repository directly testable after cloning.

---

## Live Collection Mode

Live collection can be launched with:

```bash
./run-audit.sh collect <inventory>
```

In collection mode:

```text
Inventory
    |
    v
Ansible Playbook
    |
    v
raw_data/
    |
    v
Python Analyzer
    |
    v
JSON Analysis
    |
    v
HTML Report
```

A real deployment should use a private inventory that is not committed to the public repository.

---

## Inventory Model

The Public Edition includes:

```text
inventories/demo.ini
```

The demo inventory contains fictitious systems and documentation-only TEST-NET addresses.

It exists to demonstrate the expected inventory structure.

Production inventories should remain private.

---

## Scheduling

Example systemd templates are provided under:

```text
systemd/
```

Current templates:

```text
linux-security-fleet-audit.service
linux-security-fleet-audit.timer
```

The example service uses the generic installation directory:

```text
/opt/linux-security-fleet-audit-toolkit
```

The example timer demonstrates scheduled daily execution with:

```text
Persistent=true
RandomizedDelaySec=15m
```

The templates should be reviewed and adapted before deployment.

---

## Data Separation

The project separates public demonstration assets from potentially sensitive runtime data.

Public repository content can include:

```text
source code
documentation
fictitious demo evidence
fictitious demo baselines
demo inventory
systemd templates
```

Runtime or environment-specific information should remain private.

Examples include:

```text
production inventories
raw host evidence
generated reports
production baselines
credentials
private keys
certificates
environment files
```

The repository `.gitignore` is configured to reduce the risk of accidentally committing this data.

---

## Non-Destructive Design

The toolkit is designed primarily for inspection and reporting.

The audit workflow does not intentionally:

```text
modify SSH configuration
create or remove users
change permissions
modify Postfix configuration
modify ClamAV configuration
delete detected files
apply baseline remediation
```

Detected conditions are reported for administrator review.

---

## Extensibility

The architecture is designed so additional controls can be introduced incrementally.

A new capability can generally be implemented by:

```text
1. Collecting the required evidence
2. Adding analysis logic
3. Assigning a control identifier
4. Defining severity
5. Adding evidence and recommendations
6. Updating documentation
```

Role-aware checks can be added without applying those controls to unrelated systems.

---

## Security Principle

The project follows a simple operational principle:

```text
Detect -> Classify -> Document -> Review
```

Remediation remains a separate administrative decision.

This preserves operator control and minimizes unintended changes during security auditing.

---

## Public Edition

This repository is a sanitized Public Edition.

All demonstration:

```text
hosts
IP addresses
evidence
baselines
findings
```

are fictitious.

The repository is intended to demonstrate the architecture, automation workflow and security-analysis methodology without exposing environment-specific infrastructure data.
