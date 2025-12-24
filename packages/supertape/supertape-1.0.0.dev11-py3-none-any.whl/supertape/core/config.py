"""Centralized configuration for Supertape.

This module provides configuration management with support for default values,
environment variables, and configuration files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioConfig:
    """Audio processing configuration."""

    sample_rate: int = 44100
    buffer_size: int = 1024
    default_device: int | str | None = None
    input_timeout: float = 30.0

    @classmethod
    def from_env(cls) -> AudioConfig:
        """Load audio configuration from environment variables.

        Environment variables:
        - SUPERTAPE_SAMPLE_RATE: Audio sample rate in Hz
        - SUPERTAPE_BUFFER_SIZE: Audio buffer size
        - SUPERTAPE_AUDIO_DEVICE: Default audio device index or name substring
        - SUPERTAPE_INPUT_TIMEOUT: Input timeout in seconds

        Returns:
            AudioConfig with values from environment or defaults
        """
        device_env = os.getenv("SUPERTAPE_AUDIO_DEVICE")
        return cls(
            sample_rate=int(os.getenv("SUPERTAPE_SAMPLE_RATE", cls.sample_rate)),
            buffer_size=int(os.getenv("SUPERTAPE_BUFFER_SIZE", cls.buffer_size)),
            default_device=device_env if device_env else None,
            input_timeout=float(os.getenv("SUPERTAPE_INPUT_TIMEOUT", cls.input_timeout)),
        )


@dataclass(frozen=True)
class CompilerConfig:
    """Compilation configuration."""

    default_cpu: str = "6803"
    fcc_path: str = "/opt/fcc/bin/fcc"
    temp_dir: Path | None = None

    @classmethod
    def from_env(cls) -> CompilerConfig:
        """Load compiler configuration from environment variables.

        Environment variables:
        - SUPERTAPE_DEFAULT_CPU: Default target CPU (6800, 6803, 6303)
        - SUPERTAPE_FCC_PATH: Path to FCC compiler
        - SUPERTAPE_TEMP_DIR: Temporary directory for compilation

        Returns:
            CompilerConfig with values from environment or defaults
        """
        temp_dir_str = os.getenv("SUPERTAPE_TEMP_DIR")
        return cls(
            default_cpu=os.getenv("SUPERTAPE_DEFAULT_CPU", cls.default_cpu),
            fcc_path=os.getenv("SUPERTAPE_FCC_PATH", cls.fcc_path),
            temp_dir=Path(temp_dir_str) if temp_dir_str else None,
        )


@dataclass(frozen=True)
class RepositoryConfig:
    """Repository configuration."""

    base_path: Path | None = None  # None = ~/.supertape/tapes
    auto_commit: bool = True

    @classmethod
    def from_env(cls) -> RepositoryConfig:
        """Load repository configuration from environment variables.

        Environment variables:
        - SUPERTAPE_REPO_PATH: Repository base path
        - SUPERTAPE_AUTO_COMMIT: Enable auto-commit (true/false)

        Returns:
            RepositoryConfig with values from environment or defaults
        """
        base_path_str = os.getenv("SUPERTAPE_REPO_PATH")
        auto_commit_str = os.getenv("SUPERTAPE_AUTO_COMMIT", "true").lower()
        return cls(
            base_path=Path(base_path_str) if base_path_str else None,
            auto_commit=auto_commit_str in ("true", "1", "yes", "on"),
        )


@dataclass(frozen=True)
class SupertapeConfig:
    """Main configuration object for Supertape.

    This configuration object aggregates all subsystem configurations and
    provides methods to load from various sources (environment, files, etc.).
    """

    audio: AudioConfig = AudioConfig()
    compiler: CompilerConfig = CompilerConfig()
    repository: RepositoryConfig = RepositoryConfig()

    @classmethod
    def from_env(cls) -> SupertapeConfig:
        """Load configuration from environment variables.

        Returns:
            SupertapeConfig with values from environment or defaults

        Example:
            >>> import os
            >>> os.environ["SUPERTAPE_SAMPLE_RATE"] = "48000"
            >>> config = SupertapeConfig.from_env()
            >>> print(config.audio.sample_rate)
            48000
        """
        return cls(
            audio=AudioConfig.from_env(),
            compiler=CompilerConfig.from_env(),
            repository=RepositoryConfig.from_env(),
        )

    @classmethod
    def default(cls) -> SupertapeConfig:
        """Get default configuration.

        Returns:
            SupertapeConfig with all default values
        """
        return cls()


# Global default config instance
_default_config: SupertapeConfig | None = None


def get_config() -> SupertapeConfig:
    """Get the global configuration instance.

    On first call, creates a configuration loaded from environment variables.
    Subsequent calls return the same instance.

    Returns:
        Global SupertapeConfig instance

    Example:
        >>> config = get_config()
        >>> print(config.audio.sample_rate)
        44100
    """
    global _default_config
    if _default_config is None:
        _default_config = SupertapeConfig.from_env()
    return _default_config


def set_config(config: SupertapeConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: Configuration to use as global instance

    Example:
        >>> custom_config = SupertapeConfig(audio=AudioConfig(sample_rate=48000))
        >>> set_config(custom_config)
        >>> assert get_config().audio.sample_rate == 48000
    """
    global _default_config
    _default_config = config
