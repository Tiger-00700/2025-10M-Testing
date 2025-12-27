from docx import Document
import re

def fix_specific_yaml_block(docx_path, output_path):
    """Fix the specific YAML block in 第1篇-008 anchor"""
    doc = Document(docx_path)

    # Find the paragraph containing "application_scenarios:"
    target_found = False
    paragraphs_to_fix = []

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        if 'application_scenarios:' in text:
            target_found = True
            paragraphs_to_fix.append((i, para))
            # Get the next several paragraphs that contain YAML
            for j in range(1, 20):  # Check next 20 paragraphs
                if i + j < len(doc.paragraphs):
                    next_para = doc.paragraphs[i + j]
                    next_text = next_para.text.strip()
                    if next_text and not next_text.startswith('> [第') and not next_text.startswith('**JSON'):
                        paragraphs_to_fix.append((i + j, next_para))
                    else:
                        break
            break

    if target_found:
        print(f"Found YAML block with {len(paragraphs_to_fix)} paragraphs to fix")

        # Replace with properly formatted YAML
        proper_yaml = """application_scenarios:
  ecommerce_recommendation:
    data_types: ["user_behavior_logs", "product_data"]
    key_metrics: ["click_through_rate", "conversion_rate", "personalization_accuracy"]
    script_reference: "examples/01_intro/simple_data_pipeline.md"
  financial_risk_control:
    data_types: ["transaction_records", "user_profiles"]
    key_metrics: ["fraud_detection_rate", "false_positive_rate"]
    script_reference: "examples/01_intro/data_factory.py"
  iot_monitoring:
    data_types: ["sensor_data", "device_status"]
    key_metrics: ["data_integrity", "real_time_latency"]
    script_reference: "examples/01_intro/masking_policy_demo.py"
  content_distribution:
    data_types: ["user_preferences", "content_metadata"]
    key_metrics: ["content_matching_degree", "user_retention"]
    script_reference: "examples/01_intro/qa_summary.py" """

        yaml_lines = proper_yaml.split('\n')

        # Update the paragraphs
        for idx, (para_idx, para) in enumerate(paragraphs_to_fix):
            if idx < len(yaml_lines):
                para.text = yaml_lines[idx]
            else:
                para.text = ""

        print("YAML block fixed")
    else:
        print("YAML block not found")

    doc.save(output_path)
    print(f"Fixed DOCX saved to: {output_path}")

if __name__ == '__main__':
    fix_specific_yaml_block('1225全书定稿_final.docx', '1225全书定稿_final_yaml_fixed.docx')