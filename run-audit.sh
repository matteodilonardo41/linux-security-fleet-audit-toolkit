#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ANALYZER="${ROOT_DIR}/analyzer/analyzer.py"
REPORT_GENERATOR="${ROOT_DIR}/analyzer/report_html.py"

REPORT_DIR="${ROOT_DIR}/reports"
RAW_DATA_DIR="${ROOT_DIR}/raw_data"

DEMO_EVIDENCE_DIR="${ROOT_DIR}/examples/demo-evidence"
DEMO_INVENTORY="${ROOT_DIR}/inventories/demo.ini"
PLAYBOOK="${ROOT_DIR}/playbooks/audit.yml"

MODE="${1:-demo}"
INVENTORY="${2:-${DEMO_INVENTORY}}"

ANALYSIS_JSON="${REPORT_DIR}/fleet-analysis.json"
REPORT_HTML="${REPORT_DIR}/fleet-report.html"


print_header() {
    printf '%s\n' \
        "============================================================" \
        " Linux Security Fleet Audit Toolkit" \
        "============================================================"
}


check_file() {
    local path="$1"

    if [[ ! -f "$path" ]]; then
        echo "Required file not found: $path" >&2
        exit 1
    fi
}


check_directory() {
    local path="$1"

    if [[ ! -d "$path" ]]; then
        echo "Required directory not found: $path" >&2
        exit 1
    fi
}


run_analysis() {
    local input_dir="$1"

    python3 "$ANALYZER" \
        --input-dir "$input_dir" \
        --output "$ANALYSIS_JSON"

    python3 "$REPORT_GENERATOR" \
        --input "$ANALYSIS_JSON" \
        --output "$REPORT_HTML"
}


run_demo() {
    echo "[MODE] Demo"
    echo "[INFO] Using sanitized evidence from: $DEMO_EVIDENCE_DIR"

    check_directory "$DEMO_EVIDENCE_DIR"

    run_analysis "$DEMO_EVIDENCE_DIR"
}


run_collection() {
    echo "[MODE] Live collection"
    echo "[INFO] Inventory: $INVENTORY"

    check_file "$INVENTORY"
    check_file "$PLAYBOOK"

    command -v ansible-playbook >/dev/null 2>&1 || {
        echo "ansible-playbook is required for collection mode." >&2
        exit 1
    }

    rm -rf "$RAW_DATA_DIR"

    ansible-playbook \
        -i "$INVENTORY" \
        "$PLAYBOOK"

    check_directory "$RAW_DATA_DIR"

    run_analysis "$RAW_DATA_DIR"
}


main() {
    print_header

    check_file "$ANALYZER"
    check_file "$REPORT_GENERATOR"

    mkdir -p "$REPORT_DIR"

    case "$MODE" in
        demo)
            run_demo
            ;;
        collect)
            run_collection
            ;;
        *)
            echo "Usage:" >&2
            echo "  ./run-audit.sh demo" >&2
            echo "  ./run-audit.sh collect [inventory]" >&2
            exit 2
            ;;
    esac

    echo
    echo "[OK] Audit completed"
    echo "[OK] JSON report: $ANALYSIS_JSON"
    echo "[OK] HTML report: $REPORT_HTML"
}


main "$@"
