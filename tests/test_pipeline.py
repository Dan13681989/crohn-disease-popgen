import os
import pytest
import pandas as pd
from crohn_pipeline import fetch_gwas_snps

def test_fetch_gwas_snps():
    snps = fetch_gwas_snps("Crohn's disease")
    assert isinstance(snps, list)
    assert len(snps) > 0
    assert all(s.startswith("rs") for s in snps[:10])

def test_plot_pca_missing_file(tmp_path):
    # Test graceful handling when eigenvec doesn't exist
    from crohn_pipeline import plot_pca
    # Should not crash; we capture stderr or just run
    # (we'll mock if needed, but for now just ensure it doesn't raise)
    try:
        plot_pca("nonexistent.eigenvec", str(tmp_path))
    except FileNotFoundError:
        pass  # expected
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
