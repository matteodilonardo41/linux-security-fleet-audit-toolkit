# Security Controls

This document describes the security checks demonstrated by the Public Edition of the Linux Security Fleet Audit Toolkit.

## Generic Linux Controls

- Privileged and administrative account review
- SSH configuration review
- Authorized SSH key inspection
- Baseline drift detection
- Scheduled persistence review through cron and systemd
- Security service and tooling status
- Network and service exposure review
- Rootkit and malware scanner findings

## Web and WordPress Controls

- WPScan result availability
- WordPress XML-RPC exposure
- Publicly accessible WordPress files
- Publicly reachable WordPress scheduled-task endpoints
- Web-focused findings classified separately from generic Linux checks

## Mail Server Controls

- Postfix TLS configuration
- SASL authentication anomaly detection
- DKIM validation
- ClamAV integration and socket permissions
- Mail-specific findings applied only to systems assigned the mail role

## Role-Aware Evaluation

Checks are evaluated according to the role assigned to each host. This avoids applying irrelevant mail-server controls to web servers or WordPress checks to generic infrastructure systems.

## Finding Classification

Every detected condition is assigned one of the following severities:

- `CRITICAL`
- `HIGH`
- `WARNING`
- `INFO`
- `OK`

The highest active severity determines the overall status of the audited host.

## Operational Approach

The toolkit reports evidence and classification without applying automatic remediation. Security findings remain subject to administrator validation before any change is performed.
