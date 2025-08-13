import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
import subprocess

# Make sure main.py is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

client = TestClient(main.app)


def test_scan_repo_mocked():
    # Mock outputs for subprocess.run
    mock_git_clone = subprocess.CompletedProcess(
        args=["git", "clone"], returncode=0, stdout="Mocked git clone", stderr=""
    )
    mock_trivy = subprocess.CompletedProcess(
        args=["trivy"], returncode=0, stdout="Mocked Trivy output", stderr=""
    )
    mock_gitleaks = subprocess.CompletedProcess(
        args=["gitleaks"], returncode=0, stdout="Mocked Gitleaks output", stderr=""
    )

    # Patch subprocess.run to avoid running real scanners or cloning
    with patch(
        "main.subprocess.run", side_effect=[mock_git_clone, mock_trivy, mock_gitleaks]
    ):
        response = client.post(
            "/scan",
            json={
                "repo_url": "https://github.com/example/repo.git",
                "branch": "main",  # Optional: matches updated route
            },
        )

        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["trivy_output"] == "Mocked Trivy output"
        assert data["gitleaks_output"] == "Mocked Gitleaks output"
        assert data["repo"] == "https://github.com/example/repo.git"
        assert data["branch"] == "main"
        assert "scan_time" in data
