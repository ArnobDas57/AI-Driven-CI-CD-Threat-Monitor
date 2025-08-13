from fastapi.testclient import TestClient
from unittest.mock import patch
import subprocess
import main

client = TestClient(main.app)


# Function for local testing
def test_scan_repo_mocked():
    # Mock Trivy output
    mock_trivy = subprocess.CompletedProcess(
        args=["trivy"], returncode=0, stdout="Mocked Trivy output", stderr=""
    )
    # Mock Gitleaks output
    mock_gitleaks = subprocess.CompletedProcess(
        args=["gitleaks"], returncode=0, stdout="Mocked Gitleaks output", stderr=""
    )

    # Patch subprocess.run so it doesn't actually run scanners
    with patch("main.subprocess.run", side_effect=[mock_trivy, mock_gitleaks]):
        response = client.post(
            "/scan", json={"repo_url": "https://github.com/example/repo.git"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["trivy_output"] == "Mocked Trivy output"
        assert data["gitleaks_output"] == "Mocked Gitleaks output"
