import sys
import os
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
contract_path = os.path.join(REPO, 'examples', '13_data_gov', 'contract_example.yml')

errors = []

if not os.path.exists(contract_path):
    errors.append(f"Missing contract file: {contract_path}")
else:
    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            doc = yaml.safe_load(f)
        if 'contract' not in doc or 'schema' not in doc:
            errors.append("Contract YAML must contain 'contract' and 'schema'")
        else:
            meta = doc['contract']
            required_meta = ['name','owner','domain','version','breaking_change']
            for k in required_meta:
                if k not in meta:
                    errors.append(f"Missing contract meta: {k}")
            # version format basic check
            ver = str(meta.get('version',''))
            if len(ver.split('.')) != 3:
                errors.append("Version should be semantic version: MAJOR.MINOR.PATCH")
            # breaking_change should be boolean
            if not isinstance(meta.get('breaking_change'), bool):
                errors.append("breaking_change must be boolean")
            # schema checks
            schema = doc['schema']
            if 'fields' not in schema or not isinstance(schema['fields'], list) or len(schema['fields']) == 0:
                errors.append("Schema fields required and non-empty")
            # Ensure primary_keys exist in fields
            pk = schema.get('primary_keys', [])
            field_names = {f.get('name') for f in schema.get('fields', [])}
            for k in pk:
                if k not in field_names:
                    errors.append(f"Primary key '{k}' not present in fields")
    except Exception as e:
        errors.append(f"Failed to parse {contract_path}: {e}")

if errors:
    print("Contract validation FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("Contract validation PASSED.")
