import subprocess
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


@patch("main.subprocess.run")
def test_scan_repo_success(mock_subprocess_run):
    """
    Tests the /scan endpoint for a successful scan.
    """
    # 1. Configure the mock to simulate successful command runs
    mock_subprocess_run.return_value = MagicMock(
        stdout="Scan complete. No vulnerabilities found.", stderr="", returncode=0
    )

    # 2. Define the payload for the request
    test_payload = {"repo_url": "https://github.com/test/repo.git"}

    # 3. Send a POST request to the /scan endpoint
    response = client.post("/scan", json=test_payload)

    # 4. Assert the results
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "scanned"
    assert response_data["repo"] == "https://github.com/test/repo.git"
    assert "trivy_output" in response_data
    assert "gitleaks_output" in response_data

    # Optional: Check if the correct commands were called
    assert mock_subprocess_run.call_count == 3  # git, trivy, gitleaks
    git_call_args = mock_subprocess_run.call_args_list[0].args[0]
    assert "git" in git_call_args
    assert "clone" in git_call_args
    assert "https://github.com/test/repo.git" in git_call_args


@patch("main.subprocess.run")
def test_scan_repo_git_clone_fails(mock_subprocess_run):
    """
    Tests the /scan endpoint when the 'git clone' command fails.
    """
    # 1. Configure the mock to raise an error specifically for the git clone command
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=128, cmd=["git", "clone", "..."], output=b"Repository not found"
    )

    # 2. Define payload and send request
    test_payload = {"repo_url": "https://github.com/invalid/repo.git"}
    response = client.post("/scan", json=test_payload)

    # 3. Assert a 500 error is returned
    assert response.status_code == 500
    assert "error" in response.json()
