import sys
import os
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)

errors = []

# Checks for SLI/SLO YAML structure
sli_path = os.path.join(REPO, 'examples', '15_framework', 'sli_slo_baseline.yml')
if not os.path.exists(sli_path):
    errors.append(f"Missing file: {sli_path}")
else:
    try:
        with open(sli_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        required_top = ['service', 'subject', 'slis', 'slos']
        missing = [k for k in required_top if k not in data]
        if missing:
            errors.append(f"SLI/SLO YAML missing keys: {', '.join(missing)}")
        # Ensure slis/slos are non-empty lists
        if not isinstance(data.get('slis'), list) or len(data['slis']) == 0:
            errors.append("SLI list is empty or invalid")
        if not isinstance(data.get('slos'), list) or len(data['slos']) == 0:
            errors.append("SLO list is empty or invalid")
    except Exception as e:
        errors.append(f"Failed to parse {sli_path}: {e}")

# Checks for audit templates presence and minimal content
checklist_path = os.path.join(REPO, 'examples', '18_cases', 'audit_artifacts_checklist.md')
report_tmpl_path = os.path.join(REPO, 'tools', 'reports', 'templates', 'audit_artifact_report.md')

# Additional templates (evaluation scorecard and migration checklist)
scorecard_path = os.path.join(REPO, 'examples', '20_evolution', 'evaluation_scorecard.md')
migration_checklist_path = os.path.join(REPO, 'examples', '20_evolution', 'migration_checklist.md')

for p in [checklist_path, report_tmpl_path, scorecard_path, migration_checklist_path]:
    if not os.path.exists(p):
        errors.append(f"Missing file: {p}")
    else:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            if len(content.strip()) < 50:
                errors.append(f"Template too short or empty: {p}")
        except Exception as e:
            errors.append(f"Failed to read {p}: {e}")

if errors:
    print("Template validation FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("Template validation PASSED.")
