# Security Controls

This document describes the security checks currently implemented in the Public Edition of the Linux Security Fleet Audit Toolkit.

The Public Edition is intentionally limited to controls that are actually implemented in the repository.

---

## Generic Linux Controls

Generic Linux controls are evaluated on all audited hosts.

### Privileged Accounts

The analyzer reviews collected UID 0 accounts and reports unexpected privileged identities.

Control ID:

```text
LINUX-UID0-001
```

Severity:

```text
HIGH
```

The expected privileged account is:

```text
root
```

Any additional account with UID 0 is reported for administrative review.

---

### SSH Root Login

The analyzer evaluates the effective SSH configuration and detects direct root login when:

```text
permitrootlogin yes
```

Control ID:

```text
SSH-ROOT-001
```

Severity:

```text
HIGH
```

Recommended action:

Disable direct SSH access for root and use named administrative accounts with privilege escalation.

---

### SSH Password Authentication

Password-based SSH authentication is reported when:

```text
passwordauthentication yes
```

Control ID:

```text
SSH-AUTH-001
```

Severity:

```text
WARNING
```

Recommended action:

Review whether key-based authentication can be used instead.

---

### SSH Public-Key Authentication

The analyzer detects when SSH public-key authentication is explicitly disabled:

```text
pubkeyauthentication no
```

Control ID:

```text
SSH-KEY-001
```

Severity:

```text
WARNING
```

Recommended action:

Review the authentication policy and enable public-key authentication where appropriate.

---

### authorized_keys Permissions

The collector retrieves metadata for detected:

```text
authorized_keys
```

files.

The analyzer checks whether those files are writable by the group or by other users.

Control ID:

```text
SSH-KEYPERM-001
```

Severity:

```text
WARNING
```

Collected evidence includes:

```text
path
owner
group
mode
size
modification timestamp
```

Recommended action:

Remove unnecessary group or world write permissions from authorized key files.

---

## Baseline Drift Detection

The analyzer can compare selected collected configuration values against an approved per-host baseline.

The Public Edition currently supports SSH baseline comparison for:

```text
permitrootlogin
passwordauthentication
pubkeyauthentication
```

Control ID:

```text
BASELINE-SSH-001
```

The baseline contains the expected approved state.

Example:

```text
Expected:
permitrootlogin no

Current:
permitrootlogin yes

Result:
Configuration drift detected
```

The severity of the baseline finding is determined by the highest-impact difference.

Current severity mapping:

```text
permitrootlogin        -> HIGH
passwordauthentication -> WARNING
pubkeyauthentication   -> WARNING
```

Baseline comparison is analytical only.

The toolkit does not automatically restore the expected configuration.

---

## Web Role Controls

Web-specific checks are applied only to hosts assigned the:

```text
web
```

role.

### WordPress Installation Detection

The Ansible collector searches for WordPress installation indicators by locating:

```text
wp-config.php
```

under the configured web paths.

Detected WordPress roots are passed to the analyzer.

Control ID:

```text
WEB-WP-001
```

Severity:

```text
INFO
```

This finding indicates that a WordPress installation was detected and can be subject to additional security review.

The Public Edition currently performs detection only.

It does not perform active vulnerability scanning or exploitation testing.

---

## Mail Role Controls

Mail-specific checks are applied only to hosts assigned the:

```text
mail
```

role.

### Postfix TLS Protocol Policy

The collector retrieves the effective Postfix configuration through:

```text
postconf -n
```

The analyzer reviews:

```text
smtpd_tls_protocols
smtpd_tls_mandatory_protocols
```

The current Public Edition checks for explicit exclusion of legacy protocol versions:

```text
SSLv2
SSLv3
TLSv1
TLSv1.1
```

Control ID:

```text
MAIL-TLS-001
```

Severity:

```text
WARNING
```

A finding is generated when the collected configuration does not explicitly contain the expected legacy protocol exclusions.

Recommended action:

Review the effective TLS policy against the security requirements of the environment.

---

### ClamAV Socket Permissions

The collector inspects ClamAV socket metadata when a supported socket path is present.

Example paths include:

```text
/run/clamav/clamd.ctl
/var/run/clamav/clamd.ctl
```

Collected metadata includes:

```text
path
owner
group
mode
```

The analyzer reports socket permissions that allow group or world write access.

Control ID:

```text
MAIL-CLAMAV-001
```

Severity:

```text
WARNING
```

Recommended action:

Restrict socket permissions according to the required service access model.

---

## Collected Evidence Not Currently Classified

The Ansible collector also gathers additional evidence that is retained for inspection or future controls.

Current examples include:

```text
cron persistence files
systemd timers
listening network sockets
```

These data points are collected by the current playbook but are not yet converted into dedicated findings by the Public Edition analyzer.

This distinction is intentional.

The documentation separates evidence collection from implemented analysis controls so the repository does not claim functionality that is not actually present in the code.

---

## Role-Aware Evaluation

Checks are evaluated according to the role assigned to each host.

Current demonstration roles include:

```text
generic
web
mail
monitoring
```

Generic Linux controls remain applicable across the fleet.

Role-specific controls are evaluated only when relevant.

Examples:

```text
web  -> WordPress installation detection
mail -> Postfix TLS and ClamAV checks
```

The monitoring role is currently included in the demonstration inventory but does not yet have dedicated analysis controls.

This architecture allows new role-specific checks to be added without applying irrelevant rules to unrelated systems.

---

## Finding Classification

Every detected condition is assigned one of the following severities:

| Severity | Meaning |
|---|---|
| `CRITICAL` | Immediate security risk requiring urgent investigation |
| `HIGH` | Significant weakness or configuration drift requiring prompt review |
| `WARNING` | Security or configuration condition requiring assessment |
| `INFO` | Informational or contextual finding |
| `OK` | No relevant finding detected by the enabled checks |

The overall status of each host is determined by the highest active severity detected during analysis.

---

## Findings Structure

Each generated finding contains:

```text
severity
control_id
title
evidence
recommendation
```

This structure is used consistently in the JSON analysis output and HTML report.

---

## Non-Destructive Operational Model

The toolkit follows a non-destructive security audit model.

It is designed to:

- collect evidence;
- evaluate security-relevant configuration;
- compare approved baselines;
- classify detected conditions;
- generate structured reports.

It does not automatically:

- change SSH configuration;
- modify user accounts;
- change file permissions;
- alter Postfix configuration;
- modify ClamAV configuration;
- remove detected files;
- remediate baseline drift.

Any remediation remains an explicit administrative decision.

---

## Public Edition Scope

The repository contains only sanitized demonstration content.

Hosts, IP addresses, evidence, baselines and findings included in the examples are fictitious.

Production inventories, raw evidence, generated reports and environment-specific baselines should remain private and must not be committed to the public repository.
