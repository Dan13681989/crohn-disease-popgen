#!/usr/bin/env python3
import os
import sys
import gzip
import numpy as np
from typing import List, Dict, Tuple

HAS_CYVCF2 = False

DEFAULT_WEIGHTS = {
    "22:37480017": 0.35,
}

def open_vcf(vcf_path):
    """Open VCF, decompressing if gzipped (detect by magic bytes or .gz)."""
    # Check if it's gzipped by reading first two bytes
    with open(vcf_path, "rb") as f:
        magic = f.read(2)
    if magic == b'\x1f\x8b':
        return gzip.open(vcf_path, "rt")
    else:
        return open(vcf_path, "r")

def load_weights(snp_list: List[str]) -> Dict[str, float]:
    weights = {}
    for snp in snp_list:
        weights[snp] = DEFAULT_WEIGHTS.get(snp, 0.1)
    return weights

def parse_vcf_rsid(vcf_path: str, snp_list: List[str]) -> Dict[str, Tuple[int, int]]:
    genotypes = {}
    with open_vcf(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 10:
                continue
            rsid = parts[2]
            if rsid not in snp_list:
                continue
            fmt = parts[8]
            sample = parts[9]
            gt_idx = fmt.split(":").index("GT") if "GT" in fmt.split(":") else 0
            gt = sample.split(":")[gt_idx]
            if "/" in gt:
                a1, a2 = gt.split("/")
            elif "|" in gt:
                a1, a2 = gt.split("|")
            else:
                continue
            try:
                genotypes[rsid] = (int(a1), int(a2))
            except:
                continue
    return genotypes

def calculate_prs_from_vcf(vcf_path: str, snp_list: List[str]) -> float:
    weights = load_weights(snp_list)
    total = 0.0

    pos_snps = [snp for snp in snp_list if ":" in snp]
    rs_snps = [snp for snp in snp_list if ":" not in snp]

    if pos_snps:
        with open_vcf(vcf_path) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.strip().split("\t")
                if len(parts) < 10:
                    continue
                chrom = parts[0]
                pos_str = parts[1]
                key = f"{chrom}:{pos_str}"
                if key in pos_snps:
                    fmt = parts[8]
                    sample = parts[9]
                    gt_idx = fmt.split(":").index("GT") if "GT" in fmt.split(":") else 0
                    gt = sample.split(":")[gt_idx]
                    if "/" in gt:
                        a1, a2 = gt.split("/")
                    elif "|" in gt:
                        a1, a2 = gt.split("|")
                    else:
                        continue
                    try:
                        alleles = (int(a1), int(a2))
                        total += weights.get(key, 0.0) * (alleles[0] + alleles[1])
                    except:
                        continue

    if rs_snps:
        genotypes = parse_vcf_rsid(vcf_path, rs_snps)
        for rsid, (a1, a2) in genotypes.items():
            total += weights.get(rsid, 0.0) * (a1 + a2)

    return total

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcf", required=True)
    parser.add_argument("--snp-list", required=True)
    args = parser.parse_args()
    with open(args.snp_list, "r") as f:
        snps = [line.strip() for line in f if line.strip()]
    score = calculate_prs_from_vcf(args.vcf, snps)
    print(f"PRS: {score:.4f}")
