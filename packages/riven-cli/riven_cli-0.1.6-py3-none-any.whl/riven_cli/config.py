from pathlib import Path

from pydantic import Field
from pydantic_settings import (BaseSettings, PydanticBaseSettingsSource,
                               SettingsConfigDict, TomlConfigSettingsSource)

APP_NAME = "riven-cli"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.toml"


class Settings(BaseSettings):
    api_url: str = Field(
        default="http://localhost:8080", description="Riven Backend URL"
    )
    api_key: str | None = Field(default=None, description="Riven API Key")
    video_player: str = Field(default="mpv", description="Video player command")

    model_config = SettingsConfigDict(
        env_prefix="RIVEN_", toml_file=CONFIG_FILE, extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            for key, value in self.model_dump().items():
                if value is None:
                    f.write(f'# {key} = "None"\n')
                else:
                    if isinstance(value, bool):
                        val_str = str(value).lower()
                    elif isinstance(value, (int, float)):
                        val_str = str(value)
                    else:
                        val_str = f'"{value}"'

                    f.write(f"{key} = {val_str}\n")


settings = Settings()
