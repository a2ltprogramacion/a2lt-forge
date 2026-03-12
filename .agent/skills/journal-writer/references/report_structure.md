# Report Structure Reference — La Forja Journal
# Load when running journal_report.py or when explaining report format to operator.

## Sections in a Pattern Report

1. **Header** — batch number, generation date, entry count, date range
2. **Forjas del Batch** — count by design pattern and component type, list of forged components
3. **Análisis de Problemas** — count by severity and recurrence risk, flagged high-recurrence items
4. **Decisiones Arquitectónicas** — all ADRs with status (accepted/superseded/deprecated)
5. **Patrones Detectados** — new patterns registered in this batch
6. **Field Feedback** — average operator rating, list with individual ratings
7. **Recomendaciones para el Catálogo** — auto-generated from data: high-recurrence problems,
   low-rated field deployments, patterns that could become Core skills

## Report Naming Convention
`[YYYYMMDD]_pattern-report_batch-[N].md`
N = total_forges value at time of generation.

## When Reports Are Generated
Automatically when `total_forges - last_report_at >= report_threshold`.
Default threshold: 10 forjas. Configurable in `.forge-counter.json`.

## Reading a Report
The Recommendations section is the most actionable part.
Cross-reference flagged components against the current manifest to prioritize improvements.
