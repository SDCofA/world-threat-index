from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UPDATE = (ROOT / ".github" / "workflows" / "wti_update.yml").read_text(encoding="utf-8")
PAGES = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")


def test_shard_and_merge_failures_are_not_masked():
    assert "python -m pytest -q" in UPDATE
    assert "if-no-files-found: error" in UPDATE
    assert 'if [ "${#shard_files[@]}" -ne 10 ]' in UPDATE
    assert "continue-on-error" not in UPDATE
    assert "|| echo" not in UPDATE
    assert "|| true" not in UPDATE


def test_pages_deploy_retries_without_duplicate_artifacts():
    assert PAGES.count("actions/upload-pages-artifact") == 1
    assert PAGES.count("actions/deploy-pages@v5") == 2
    assert PAGES.count("continue-on-error: true") == 1
    assert "if: steps.deployment.outcome == 'failure'" in PAGES
