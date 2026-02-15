#!/usr/bin/env python3
"""
General Y‑DNA Haplogroup Predictor – accepts any user‑supplied STR CSV.
Usage: python analyze_ystr.py <your_data.csv>
"""
import subprocess
import os
import sys

YHP_SCRIPT = os.path.join(os.path.dirname(__file__), 'yhp', 'py_src', 'pred.py')

if len(sys.argv) != 2:
    print("Usage: python analyze_ystr.py <path_to_your_str_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]
if not os.path.exists(input_file):
    print(f"❌ File not found: {input_file}")
    sys.exit(1)

# Convert CSV to Excel (YHP requires .xlsx)
excel_file = input_file.replace('.csv', '.xlsx')
try:
    import pandas as pd
    df = pd.read_csv(input_file)
    df.to_excel(excel_file, index=False)
except Exception as e:
    print(f"❌ Failed to convert CSV to Excel: {e}")
    sys.exit(1)

output_file = input_file.replace('.csv', '_result.txt')

# Use the same Python interpreter (the one with all packages)
python_exe = sys.executable
result = subprocess.run(
    [python_exe, YHP_SCRIPT, '--input', excel_file, '--output', output_file],
    capture_output=True, text=True
)

if result.returncode != 0 or not os.path.exists(output_file):
    print("❌ YHP prediction failed.")
    print("=== stdout ===")
    print(result.stdout)
    print("=== stderr ===")
    print(result.stderr)
    sys.exit(1)

with open(output_file, 'r') as f:
    prediction = f.read()

print("\n🧬 Predicted Haplogroup:")
print(prediction)
print(f"\n✅ Full result saved to: {output_file}")
