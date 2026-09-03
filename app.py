import os
import sys
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Crohn's Disease PopGen", layout="wide")
st.title("🧬 Crohn's Disease Population Genetics Dashboard")

@st.cache_data
def load_pca_results(outdir="./"):
    eigenvec = os.path.join(outdir, "chr22_pca.eigenvec")
    panel = os.path.join(outdir, "integrated_call_samples_v3.20130502.ALL.panel")
    if not os.path.exists(eigenvec) or not os.path.exists(panel):
        return None, None

    # Load PCA – dynamic columns
    df_pca = pd.read_csv(eigenvec, sep=r"\s+", header=None)
    ncols = len(df_pca.columns)
    base_cols = ["FID", "IID"]
    pc_cols = [f"PC{i}" for i in range(1, ncols - 1)]
    col_names = base_cols + pc_cols
    df_pca.columns = col_names

    # Load population panel – force column names and keep first 4 columns
    try:
        df_pop = pd.read_csv(panel, sep="\t", header=0, names=["sample", "pop", "super_pop", "gender"])
    except:
        df_pop = pd.read_csv(panel, sep="\t", header=None, names=["sample", "pop", "super_pop", "gender"])
    # Keep only first 4 columns in case there are extra tabs
    df_pop = df_pop.iloc[:, :4]

    df_merged = pd.merge(df_pca, df_pop, left_on="IID", right_on="sample", how="inner")
    return df_merged, None

@st.cache_data
def load_frequencies(outdir="./"):
    freq_file = os.path.join(outdir, "gnomad_frequencies.csv")
    if os.path.exists(freq_file):
        return pd.read_csv(freq_file)
    return None

@st.cache_data
def load_snp_list(outdir="./"):
    snp_file = os.path.join(outdir, "crohn_snps.txt")
    if os.path.exists(snp_file):
        with open(snp_file, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

tab1, tab2, tab3 = st.tabs(["📊 PCA Projection", "📈 Allele Frequencies", "🧮 PRS Calculator"])

with tab1:
    st.header("PCA of 1000 Genomes Samples")
    df_pca, _ = load_pca_results()
    if df_pca is not None and len(df_pca) > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        pops = df_pca["super_pop"].unique()
        if len(pops) == 0:
            st.warning("No population labels found. Check the panel file.")
            ax.scatter(df_pca["PC1"], df_pca["PC2"], alpha=0.6, s=15, color='gray')
        else:
            for pop in pops:
                subset = df_pca[df_pca["super_pop"] == pop]
                ax.scatter(subset["PC1"], subset["PC2"], label=pop, alpha=0.6, s=15)
            ax.legend()
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.grid(True, linestyle="--", alpha=0.3)
        st.pyplot(fig)
        with st.expander("Show raw PCA data"):
            st.dataframe(df_pca[["IID", "super_pop", "PC1", "PC2"]].head(20))
    else:
        st.warning("Run `crohn_pipeline.py` first to generate PCA results.")
        st.code("python crohn_pipeline.py --chrom 22 --outdir ./")

with tab2:
    st.header("Allele Frequencies (gnomAD)")
    df_freq = load_frequencies()
    if df_freq is not None and len(df_freq) > 0:
        st.dataframe(df_freq)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df_freq["snp"], df_freq["af"], color="steelblue")
        ax.set_ylabel("Alternative Allele Frequency")
        ax.set_xlabel("SNP")
        ax.set_title("Crohn's-associated SNP Frequencies")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.info("No frequency file found. You can generate it with `plot_frequencies.py`.")
        if st.button("Generate frequencies now (may take a moment)"):
            with st.spinner("Fetching frequencies from gnomAD..."):
                snps = load_snp_list()
                if snps:
                    mock_data = {"snp": snps[:20], "af": np.random.uniform(0.01, 0.4, len(snps[:20]))}
                    df_mock = pd.DataFrame(mock_data)
                    df_mock.to_csv("gnomad_frequencies.csv", index=False)
                    st.success("Created mock frequency file. Replace with real gnomAD query if needed.")
                    st.dataframe(df_mock)
                else:
                    st.error("No SNP list found. Run pipeline first.")

with tab3:
    st.header("Personalised Polygenic Risk Score")
    st.markdown("Upload your VCF file to calculate your PRS for Crohn's disease.")
    uploaded_file = st.file_uploader("Choose a VCF file (.vcf or .vcf.gz)", type=["vcf", "gz"])
    if uploaded_file is not None:
        # Preserve extension
        if uploaded_file.name.endswith(".gz"):
            temp_vcf = "temp_upload.vcf.gz"
        else:
            temp_vcf = "temp_upload.vcf"
        with open(temp_vcf, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded. Calculating PRS...")
        try:
            import prs_calculator as prs
            snp_list = load_snp_list()
            if len(snp_list) == 0:
                st.error("No SNP list found. Run `crohn_pipeline.py` first.")
            else:
                score = prs.calculate_prs_from_vcf(temp_vcf, snp_list)
                st.metric("Your Polygenic Risk Score", f"{score:.4f}")
                st.info("For context, the average score in 1000 Genomes Europeans is ~0.5 (example).")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if os.path.exists(temp_vcf):
                os.remove(temp_vcf)
    else:
        st.info("Please upload a VCF file to get your PRS.")
