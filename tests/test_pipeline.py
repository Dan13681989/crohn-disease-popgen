import subprocess

def test_script_runs():
    result = subprocess.run(["python", "crohn_pipeline.py"], 
capture_output=True, text=True)
    assert result.returncode == 0
