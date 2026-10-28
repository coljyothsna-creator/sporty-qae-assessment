"""Validated runtime settings, separate from test inputs and UI locators."""

import math
from dataclasses import dataclass
from urllib.parse import urlsplit

DEFAULT_BASE_URL = "https://qae-assignment-tau.vercel.app"


@dataclass(frozen=True)
class Settings:
    base_url: str = DEFAULT_BASE_URL
    ui_timeout: float = 10
    api_timeout: float = 10
    headless: bool = True

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("base_url must be an HTTP(S) origin without credentials")
        try:
            _ = parsed.port
        except ValueError as error:
            raise ValueError("base_url contains an invalid port") from error
        for name in ("ui_timeout", "api_timeout"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite positive number")
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
