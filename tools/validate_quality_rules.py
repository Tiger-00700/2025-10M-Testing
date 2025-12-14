import sys
import os
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
rules_path = os.path.join(REPO, 'examples', '09_quality', 'quality_rules.yml')

errors = []

if not os.path.exists(rules_path):
    errors.append(f"Missing rules file: {rules_path}")
else:
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            doc = yaml.safe_load(f)
        rules = doc.get('rules')
        if not isinstance(rules, list) or len(rules) == 0:
            errors.append("rules must be a non-empty list")
        else:
            for idx, r in enumerate(rules, start=1):
                for key in ['id','name','type','target','expression','severity','on_fail']:
                    if key not in r:
                        errors.append(f"Rule[{idx}] missing key: {key}")
                if r.get('type') not in ['constraint','distribution']:
                    errors.append(f"Rule[{idx}] invalid type: {r.get('type')}")
                if r.get('severity') not in ['low','medium','high']:
                    errors.append(f"Rule[{idx}] invalid severity: {r.get('severity')}")
                # if distribution type, window recommended
                if r.get('type') == 'distribution' and 'window' not in r:
                    errors.append(f"Rule[{idx}] distribution rules should define 'window'")
    except Exception as e:
        errors.append(f"Failed to parse {rules_path}: {e}")

if errors:
    print("Quality rules validation FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("Quality rules validation PASSED.")
