#!/usr/bin/env python3
"""
Automated Crohn's Disease Population Genetics Pipeline
"""

import os
import sys
import subprocess
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# ----------------------------------------------------------------------
PLINK_BED = "/Users/diba/Documents/Research/Genetics/genetic_data_archive/chr22_data"
PLINK2 = "plink2"  # or full path
OUTPUT_BASE = "crohn_pipeline_output"
# ----------------------------------------------------------------------

def create_output_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(OUTPUT_BASE, timestamp)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def fetch_gwas_snps(trait_name="Crohn's disease"):
    url = "https://www.ebi.ac.uk/gwas/rest/api/associations/search"
    params = {"trait": trait_name, "size": 10000}
    print(f"Fetching GWAS associations for '{trait_name}'...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    snps = []
    for assoc in data.get("_embedded", {}).get("associations", []):
        for locus in assoc.get("loci", []):
            for variant in locus.get("strongestRiskAlleles", []):
                rsid = variant.get("snp")
                if rsid and rsid.startswith("rs"):
                    snps.append({
                        "rsid": rsid,
                        "pvalue": assoc.get("pvalue"),
                        "trait": assoc.get("efoTraits", [{}])[0].get("trait") if assoc.get("efoTraits") else None
                    })
    print(f"Found {len(snps)} unique SNPs.")
    return snps

def filter_chr22_snps(rsid_list):
    chr22_snps = []
    print("Checking chromosomes for each SNP via Ensembl...")
    for rsid in rsid_list:
        url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
        try:
            resp = requests.get(url, headers={"Content-Type": "application/json"}, timeout=5)
            if resp.ok:
                data = resp.json()
                mappings = data.get("mappings", [])
                for m in mappings:
                    if m.get("seq_region_name") == "22":
                        chr22_snps.append(rsid)
                        break
            time.sleep(0.2)
        except Exception as e:
            print(f"Error querying {rsid}: {e}")
    print(f"Found {len(chr22_snps)} SNPs on chromosome 22.")
    return chr22_snps

def fetch_allele_frequencies(rsid_list, out_dir):
    freq_data = []
    for rsid in rsid_list:
        url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
        try:
            resp = requests.get(url, headers={"Content-Type": "application/json"}, timeout=5)
            if resp.ok:
                data = resp.json()
                row = {"rsid": rsid}
                for pop in data.get("populations", []):
                    pop_name = pop.get("population")
                    freq = pop.get("frequency")
                    if pop_name and freq is not None:
                        if "African" in pop_name:
                            row["AFR"] = freq
                        elif "Latino" in pop_name or "Admixed American" in pop_name:
                            row["AMR"] = freq
                        elif "East Asian" in pop_name:
                            row["EAS"] = freq
                        elif "European" in pop_name:
                            if "non-Finnish" in pop_name:
                                row["EUR"] = freq
                            elif "EUR" not in row:
                                row["EUR"] = freq
                        elif "South Asian" in pop_name:
                            row["SAS"] = freq
                freq_data.append(row)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching frequencies for {rsid}: {e}")
    df = pd.DataFrame(freq_data)
    out_file = os.path.join(out_dir, "allele_frequencies.csv")
    df.to_csv(out_file, index=False)
    print(f"Allele frequencies saved to {out_file}")
    return df

def run_plink_pca(out_dir):
    print("Running PLINK PCA...")
    cmd = [PLINK2, "--bfile", PLINK_BED, "--pca", "10", "--out", os.path.join(out_dir, "chr22_pca")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("PLINK error:", result.stderr)
        sys.exit(1)
    print("PLINK PCA completed.")
    return os.path.join(out_dir, "chr22_pca.eigenvec")

def plot_pca(eigenvec_file, out_dir):
    eigenvec = pd.read_csv(eigenvec_file, sep=r"\s+", header=None,
                           names=["FID", "IID"] + [f"PC{i}" for i in range(1,11)])
    panel_path = os.path.expanduser("~/Documents/Crohn_Project/Data/integrated_call_samples_v3.20130502.ALL.panel")
    if not os.path.exists(panel_path):
        print("Population panel not found. Downloading...")
        import urllib.request
        url = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"
        urllib.request.urlretrieve(url, panel_path)
    panel = pd.read_csv(panel_path, sep=r"\s+")
    merged = eigenvec.merge(panel[['sample', 'super_pop']], left_on='IID', right_on='sample')
    
    plt.figure(figsize=(8,6))
    colors = {'EUR': 'blue', 'AFR': 'green', 'AMR': 'red', 'EAS': 'orange', 'SAS': 'purple'}
    for pop, color in colors.items():
        subset = merged[merged['super_pop'] == pop]
        plt.scatter(subset['PC1'], subset['PC2'], label=pop, alpha=0.7, s=10, c=color)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.legend()
    plt.title('PCA of 1000 Genomes Chromosome 22')
    out_png = os.path.join(out_dir, "chr22_pca.png")
    plt.savefig(out_png)
    plt.close()
    print(f"PCA plot saved to {out_png}")

def main():
    out_dir = create_output_dir()
    print(f"Output directory: {out_dir}")
    
    # Step 1: Fetch GWAS SNPs
    snps = fetch_gwas_snps()
    if not snps:
        print("No SNPs found. Exiting.")
        return
    rsids = [s['rsid'] for s in snps]
    
    # Step 2: Try to filter chr22 (if none, we still run PCA)
    chr22_rsids = filter_chr22_snps(rsids)
    if chr22_rsids:
        with open(os.path.join(out_dir, "chr22_rsids.txt"), "w") as f:
            for rs in chr22_rsids:
                f.write(rs + "\n")
        # Step 3: Fetch allele frequencies for chr22 SNPs
        fetch_allele_frequencies(chr22_rsids, out_dir)
    else:
        print("No chromosome 22 SNPs found. Skipping frequency fetch.")
    
    # Step 4: Always run PCA (uses your existing data)
    eigenvec_file = run_plink_pca(out_dir)
    # Step 5: Plot PCA
    plot_pca(eigenvec_file, out_dir)
    
    print("\nAll done! Results are in:", out_dir)

if __name__ == "__main__":
    main()
