# Crohn's Disease Population Genetics

![Test 
Status](https://github.com/Dan13681989/crohn-disease-popgen/actions/workflows/test.yml/badge.svg)

This project explores population structure on chromosome 22 using 1000 
Genomes data and relates it to known Crohn's disease risk alleles.

## Contents
- `report.md` – Full project report
- `chr22_pca.png` – PCA plot of 1000 Genomes chromosome 22
- `gnomad_frequencies.csv` – Allele frequencies of Crohn's SNPs from 
gnomAD
- `crohn_pipeline.py` – Python pipeline to automate the analysis

## Methods
- Downloaded 1000 Genomes Phase 3 chromosome 22 data (PLINK format).
- Ran PCA with PLINK 2.0.
- Visualized PC1 vs PC2 using matplotlib, colored by super‑population.
- Extracted Crohn's-associated SNPs from GWAS Catalog and fetched their 
allele frequencies from Ensembl.

## Results
The PCA plot clearly separates the five super‑populations (AFR, AMR, EAS, 
EUR, SAS), recapitulating known human migration history. Allele 
frequencies for two well‑studied Crohn's variants (*NOD2* rs2066844, 
*IL23R* rs11209026) show striking differences across populations, 
mirroring the PCA clusters and the higher prevalence of Crohn's in 
Europeans.

## How to Run the Pipeline
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure PLINK2 is installed and in your PATH.
4. Run: `python crohn_pipeline.py`

## Easy Local Setup

For users who prefer not to use Docker, a setup script is provided:

1. Clone the repository:
   ```bash
   git clone https://github.com/Dan13681989/crohn-disease-popgen.git
   cd crohn-disease-popgen

## Dependencies
- Python 3.8+
- requests, pandas, matplotlib
- PLINK 2.0

## References
- 1000 Genomes Project Consortium, *Nature* 2015
- Liu, J.Z. et al., *Nature Genetics* 2015
- GWAS Catalog (www.ebi.ac.uk/gwas)
