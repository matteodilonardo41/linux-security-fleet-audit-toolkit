# Architecture

## Purpose

The Linux Security Fleet Audit Toolkit separates evidence collection, analysis and reporting into independent stages.

The design is intentionally non-destructive: audited hosts are inspected without applying automatic remediation.

## Processing Pipeline

```text
Linux Hosts
    |
    v
Ansible Evidence Collection
    |
    v
Collected Host Data
    |
    v
Python Analysis Engine
    |
    +--> Generic Security Rules
    +--> Baseline Drift Detection
    +--> Role-Aware Checks
    |
    v
Structured Findings
    |
    +--> JSON
    +--> HTML
    +--> PDF
    |
    v
Operational Review
```

## Main Components

### Ansible Collector

Ansible connects to the configured Linux hosts and collects security-relevant evidence in a consistent and repeatable way.

### Python Analysis Engine

The analyzer evaluates collected evidence, compares selected data against trusted baselines and assigns severity levels to detected findings.

### Role-Aware Checks

Checks can be applied according to the role of each system. For example, mail-specific controls are evaluated only on mail servers, while web-specific controls are evaluated only on web servers.

### Reporting Layer

Findings are converted into structured JSON and human-readable HTML/PDF reports for operational review.

### Scheduling

The toolkit can be executed periodically through systemd services and timers, allowing unattended recurring audits.

## Security Principle

The toolkit is designed to detect, classify and document security conditions. Remediation remains a separate administrative decision.
