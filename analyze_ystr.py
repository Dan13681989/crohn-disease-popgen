#!/usr/bin/env python3
"""
Run YHP haplogroup predictor on personal Y‑STR data and append results to 
report.
"""
import subprocess
import os

YHP_PATH = os.path.join(os.path.dirname(__file__), 'yhp', 'YHP.py')
STR_FILE = os.path.join(os.path.dirname(__file__), 'yhp', 'my_strs.xlsx')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'yhp', 
'my_result.txt')
REPORT_FILE = os.path.join(os.path.dirname(__file__), 'report.md')

def run_yhp():
    print("Running YHP haplogroup prediction...")
    result = subprocess.run(
        ['python', YHP_PATH, '--input', STR_FILE, '--output', 
OUTPUT_FILE],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error running YHP:", result.stderr)
        return None
    with open(OUTPUT_FILE, 'r') as f:
        prediction = f.read()
    return prediction

def update_report(prediction):
    with open(REPORT_FILE, 'r') as f:
        content = f.read()
    marker = "## Personal Context"
    if marker in content:
        # Replace the existing personal context section with an updated 
version
        new_section = f"""## Personal Context: My Ancestry in the PCA 
(Updated with Y‑DNA Prediction)

To make this analysis personally relevant, I incorporated my own DNA test 
results from FamilyVault and ran them through the YHP haplogroup 
predictor.

- **Paternal lineage (Y‑DNA):** Haplogroup **J**, subclade **J1a2b** 
(confirmed by SNP testing). YHP prediction:  
{prediction.strip()}

- **Maternal lineage (mtDNA):** Haplogroup **U**, subclade **U4a** 
(confirmed).

Both haplogroups are most common in European and Middle Eastern 
populations, which correspond to the **EUR cluster** in the PCA plot 
(Figure 1). The black star in `chr22_pca_personal.png` marks the 
approximate position of my ancestors within that cluster – a tangible 
connection between the abstract population genetics and my own family 
history.

Interestingly, the Crohn's disease risk alleles studied here (e.g., *NOD2* 
rs2066844) are also most frequent in Europeans. While I do not have my own 
genotypes for these SNPs, my haplogroup placement suggests I belong to the 
genetic background where these variants evolved."""
        content = 
content.replace(content[content.find(marker):content.find("## ", 
content.find(marker)+1)], new_section)
    else:
        # Append the section
        new_section = f"""
## Personal Context: My Ancestry in the PCA (with Y‑DNA Prediction)

To make this analysis personally relevant, I incorporated my own DNA test 
results from FamilyVault and ran them through the YHP haplogroup 
predictor.

- **Paternal lineage (Y‑DNA):** Haplogroup **J**, subclade **J1a2b** 
(confirmed by SNP testing). YHP prediction:  
{prediction.strip()}

- **Maternal lineage (mtDNA):** Haplogroup **U**, subclade **U4a** 
(confirmed).

Both haplogroups are most common in European and Middle Eastern 
populations, which correspond to the **EUR cluster** in the PCA plot 
(Figure 1). The black star in `chr22_pca_personal.png` marks the 
approximate position of my ancestors within that cluster – a tangible 
connection between the abstract population genetics and my own family 
history.

Interestingly, the Crohn's disease risk alleles studied here (e.g., *NOD2* 
rs2066844) are also most frequent in Europeans. While I do not have my own 
genotypes for these SNPs, my haplogroup placement suggests I belong to the 
genetic background where these variants evolved.
"""
        content += new_section

    with open(REPORT_FILE, 'w') as f:
        f.write(content)
    print("✅ Report updated with Y‑DNA prediction.")

if __name__ == "__main__":
    pred = run_yhp()
    if pred:
        update_report(pred)
        print("All done! Check your report.")
