---
name: ghl-workflow-analyzer
description: Procesa archivos JSON de workflows de GHL extraídos, mapea triggers y acciones, y detecta posibles colisiones (Race Conditions).
---

# GHL Workflow Analyzer

## Usage Protocol

Execute this skill AFTER extracting JSON files using `ghl-workflow-dna-sniffer`.
Run the `scripts/analyzer.py` script passing the subaccount's `location_id` as an argument.

## Output

The script generates an `audit_report.md` file in the subaccount directory inside `.agent/quarantine_lab/ghl-spy/`. Read this report to formulate optimization proposals.
