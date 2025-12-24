from typing import Any


class SettingsProvider:
    def __init__(self):
        pass

    def get_key(self, context: list[str]) -> Any:
        raise NotImplementedError()

    def set_key(self, context_name: str, key, value) -> None:
        raise NotImplementedError()


class Settings:
    def __init__(self, settings_provider: SettingsProvider):
        self._settings_provider = settings_provider
