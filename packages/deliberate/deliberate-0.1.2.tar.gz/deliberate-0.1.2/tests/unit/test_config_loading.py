"""Tests for configuration loading from various locations."""

from pathlib import Path

import pytest

from deliberate.config import DeliberateConfig


class TestConfigLoading:
    """Tests for configuration file loading."""

    def test_get_user_config_dir(self):
        """Should return OS-specific user config directory."""
        config_dir = DeliberateConfig.get_user_config_dir()
        assert config_dir.is_absolute()
        assert "deliberate" in str(config_dir).lower()

    def test_get_config_search_paths(self):
        """Should return config search paths in priority order."""
        paths = DeliberateConfig.get_config_search_paths()
        assert len(paths) == 3
        assert paths[0] == Path(".deliberate.yaml")
        assert paths[1] == Path("deliberate.yaml")
        assert "deliberate" in str(paths[2]).lower()

    def test_load_or_default_with_explicit_path(self, tmp_path):
        """Should load from explicit path when provided."""
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("""
agents:
  test_agent:
    type: fake
    behavior: echo
""")

        config = DeliberateConfig.load_or_default(config_file)
        assert "test_agent" in config.agents
        assert config.agents["test_agent"].type == "fake"

    def test_load_or_default_from_cwd(self, tmp_path, monkeypatch):
        """Should load from current directory .deliberate.yaml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / ".deliberate.yaml"
        config_file.write_text("""
agents:
  cwd_agent:
    type: fake
""")

        config = DeliberateConfig.load_or_default()
        assert "cwd_agent" in config.agents

    def test_load_or_default_returns_default_when_no_config(self, tmp_path, monkeypatch):
        """Should return default config when no config file exists."""
        monkeypatch.chdir(tmp_path)
        # Mock user config dir to point to tmp_path so no user config is found
        monkeypatch.setattr(
            "deliberate.config.platformdirs.user_config_dir",
            lambda *args, **kwargs: str(tmp_path / "fake_user_config"),
        )

        config = DeliberateConfig.load_or_default()
        assert isinstance(config, DeliberateConfig)
        assert len(config.agents) == 0  # Default config has no agents

    def test_load_nonexistent_file_raises_error(self, tmp_path):
        """Should raise FileNotFoundError when explicit path doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError):
            DeliberateConfig.load(nonexistent)
