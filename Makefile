.PHONY: all install plink run test dashboard clean

all: install plink run test dashboard

install:
	@echo "📦 Installing Python dependencies..."
	pip3 install -r requirements.txt

plink:
	@echo "⚙️  Installing PLINK 2.0..."
	@if ! command -v plink2 >/dev/null 2>&1; then \
		cd ~/Downloads && \
		curl -LO 
https://s3.amazonaws.com/plink2-assets/plink2_mac_20250129.zip && \
		unzip -o plink2_mac_20250129.zip && \
		(sudo mv plink2 /usr/local/bin/ 2>/dev/null || (mkdir -p 
~/bin && mv plink2 ~/bin/ && export PATH="$$HOME/bin:$$PATH" && echo 
'export PATH="$$HOME/bin:$$PATH"' >> ~/.zshrc)); \
	fi
	@plink2 --version || echo "PLINK 2.0 installed (restart terminal 
if path not loaded)."

run:
	@echo "🚀 Running pipeline on chromosome 22..."
	python3 crohn_pipeline.py --chrom 22 --outdir ./output

test:
	@echo "🧪 Running tests..."
	pytest tests/

dashboard:
	@echo "🌐 Launching Streamlit dashboard..."
	streamlit run app.py

clean:
	@echo "🧹 Cleaning output files..."
	rm -rf output/ *.pyc __pycache__/ .pytest_cache/
