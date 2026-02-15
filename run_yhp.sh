#!/bin/bash
# One‑click Y‑DNA CSV creation and integration

echo "🚀 Starting automated Y‑DNA CSV creation and analysis..."

# Step 1: Ensure we're in the right place
cd ~/Documents/Crohn_Project/ForGitHub || exit
source ~/crohn_pipeline/venv/bin/activate 2>/dev/null || {
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv ~/crohn_pipeline/venv
    source ~/crohn_pipeline/venv/bin/activate
    pip install pandas numpy scikit-learn openpyxl xlrd joblib
}

# Step 2: Create the CSV file with all 101 markers from your PDF
echo "📝 Creating yhp/ystr_template.csv with all 101 marker values..."
cat > create_ystr_csv.py << 'PYEOF'
import csv

data = [
    ("DYS19 a", 14),
    ("DYS390", 24),
    ("DYS437", 14),
    ("DYS438", 10),
    ("DYS439", 11),
    ("DYS447", 26),
    ("DYS448", 20),
    ("GATA H4", 11),
    ("YCAII a", 22),
    ("YCAII b", 22),
    ("DYS385 a", 13),
    ("DYS385 b", 18),
    ("DYS388", 17),
    ("DYS389i", 13),
    ("DYS389ii", 30),
    ("DYS391", 10),
    ("DYS392", 11),
    ("DYS393", 12),
    ("DYS426", 11),
    ("DYS460", 11),
    ("DYS445", 11),
    ("DYS453", 11),
    ("DYS456", 14),
    ("DYS468", 29),
    ("DYS484", 13),
    ("DYS522", 12),
    ("DYS527 a", 18),
    ("DYS527 b", 21),
    ("DYS531", 11),
    ("DYS557", 18),
    ("DYS588", 19),
    ("DYS449", 27),
    ("DYS454", 11),
    ("DYS455", 11),
    ("DYS459 a", 8),
    ("DYS459 b", 9),
    ("DYS464 a", 12),
    ("DYS464 b", 14),
    ("DYS464 c", 16),
    ("DYS464 d", 17),
    ("DYS444", 12),
    ("DYS463", 22),
    ("DYS452", 29),
    ("DYS442", 12),
    ("DYS446", 15),
    ("DYS461", 11),
    ("DYS462", 11),
    ("GATA C4", 21),
    ("GATA A10", 13),
    ("DYS570", 16),
    ("DYS710", 17),
    ("DYS518", 23),
    ("DYS711", 32),
    ("DYS481", 27),
    ("DYS614", 26),
    ("DYS607", 15),
    ("DYS644", 15),
    ("DYS612", 35),
    ("DYS436", 12),
    ("DYS472", 8),
    ("DYS511", 9),
    ("DYS520", 21),
    ("DYS537", 11),
    ("DYS576", 18),
    ("DYS590", 8),
    ("DYS724 a", 30),
    ("DYS724 b", 33),
    ("DYS534", 15),
    ("DYS568", 11),
    ("DYS578", 8),
    ("DYS640", 12),
    ("DYS413 a", 21),
    ("DYS413 b", 22),
    ("DYS641", 10),
    ("DYS495", 15),
    ("DYS492", 12),
    ("DYS713", 31),
    ("DYS617", 14),
    ("DYS450", 9),
    ("DYS540", 12),
    ("DYS505", 13),
    ("DYS549", 12),
    ("DYS487", 14),
    ("DYS632", 8),
    ("DYS533", 11),
    ("DYS508", 12),
    ("DYS572", 10),
    ("DYS494", 9),
    ("DYS717", 20),
    ("DYS434", 9),
    ("DYS435", 11),
    ("DYS716", 10),
    ("DYS575", 10),
    ("DYS712", 21),
    ("DYS504", 15),
    ("DYS714", 25),
    ("DYS626", 20),
    ("DYS532", 11),
    ("DYS594", 10),
    ("DYS513", 12),
    ("DYS589", 12)
]

with open('yhp/ystr_template.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['marker', 'value'])
    writer.writerows(data)

print("✅ CSV file created at yhp/ystr_template.csv with all 101 markers.")
PYEOF

python create_ystr_csv.py

# Step 3: Install any remaining dependencies
echo "📦 Installing xlrd (if needed)..."
pip install xlrd 2>/dev/null

# Step 4: Convert CSV to Excel
echo "📊 Converting CSV to Excel..."
python -c "import pandas as pd; pd.read_csv('yhp/ystr_template.csv').to_excel('yhp/my_strs.xlsx', index=False)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Excel file created."
else
    echo "❌ CSV to Excel conversion failed. Ensure pandas is installed."
    exit 1
fi

# Step 5: Patch YHP code for compatibility
echo "🛠️  Patching YHP code..."
sed -i.bak 's/from sklearn.externals import joblib/import joblib/' yhp/py_src/pred.py 2>/dev/null
sed -i.bak 's/import joblibb/import joblib/' yhp/py_src/pred.py 2>/dev/null
rm -f yhp/py_src/*.bak

# Step 6: Run the analyzer
echo "🧬 Running YHP haplogroup predictor..."
python analyze_ystr.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your Y‑DNA analysis is complete."
    echo "Your report.md has been updated with the prediction."
    echo ""
    echo "Next steps:"
    echo "  git add yhp/ ystr_template.csv analyze_ystr.py report.md"
    echo "  git commit -m \"Complete Y‑DNA analysis with personal haplogroup prediction\""
    echo "  git push"
else
    echo "❌ YHP analysis failed. Please check the error messages above."
    echo "You may need to manually adjust marker names in yhp/ystr_template.csv."
fi
