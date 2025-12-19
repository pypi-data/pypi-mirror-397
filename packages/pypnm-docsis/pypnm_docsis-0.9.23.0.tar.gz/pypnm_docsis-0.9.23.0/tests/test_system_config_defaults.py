import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_config_files_exist() -> None:
    settings_cfg = Path("src/pypnm/settings/system.json")
    deploy_cfg = Path("deploy/config/system.json")

    assert settings_cfg.exists(), "src/pypnm/settings/system.json must exist (symlink to deploy config)"
    assert deploy_cfg.exists(), "deploy/config/system.json must exist for runtime config"


def test_default_config_path_resolves() -> None:
    from tools.system_config.common import DEFAULT_CONFIG_PATH

    assert DEFAULT_CONFIG_PATH.exists(), f"DEFAULT_CONFIG_PATH must exist: {DEFAULT_CONFIG_PATH}"
