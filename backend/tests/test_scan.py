from fastapi.testclient import TestClient
from unittest.mock import patch
import subprocess
import backend.main as main

client = TestClient(main.app)


# Function for local testing
def test_scan_repo_mocked():
    # Mock Git Clone Output
    mock_git_clone = subprocess.CompletedProcess(
        args=["git", "clone"], returncode=0, stdout="Mocked git clone", stderr=""
    )
    # Mock Trivy output
    mock_trivy = subprocess.CompletedProcess(
        args=["trivy"], returncode=0, stdout="Mocked Trivy output", stderr=""
    )
    # Mock Gitleaks output
    mock_gitleaks = subprocess.CompletedProcess(
        args=["gitleaks"], returncode=0, stdout="Mocked Gitleaks output", stderr=""
    )

    with patch(
        "backend.main.subprocess.run",
        side_effect=[mock_git_clone, mock_trivy, mock_gitleaks],
    ):
        response = client.post(
            "/scan", json={"repo_url": "https://github.com/example/repo.git"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["trivy_output"] == "Mocked Trivy output"
        assert data["gitleaks_output"] == "Mocked Gitleaks output"
