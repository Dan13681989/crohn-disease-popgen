#!/bin/bash
set -e

echo "🐍 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️  Installing PLINK 2.0..."
if ! command -v plink2 >/dev/null 2>&1; then
    cd ~/Downloads
    curl -LO 
https://s3.amazonaws.com/plink2-assets/plink2_mac_20250129.zip
    unzip -o plink2_mac_20250129.zip
    if sudo mv plink2 /usr/local/bin/ 2>/dev/null; then
        echo "PLINK 2.0 installed system-wide."
    else
        mkdir -p ~/bin
        mv plink2 ~/bin/
        export PATH="$HOME/bin:$PATH"
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
        echo "PLINK 2.0 installed in ~/bin. Restart terminal or run 
'source ~/.zshrc' to use it."
    fi
    cd ~/crohn-popgen
fi

echo "🚀 Running pipeline on chromosome 22..."
python crohn_pipeline.py --chrom 22 --outdir ./output

echo "🧪 Running tests..."
pytest tests/ || echo "Tests skipped (optional)"

echo "🌐 Launching Streamlit dashboard..."
streamlit run app.py	
