from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class AuthBase(ABC):
    @abstractmethod
    def apply_headers(self, headers: dict[str, str]) -> None:
        """Mutate headers in-place to apply authentication."""
        raise NotImplementedError


@dataclass
class ApiKeyAuth(AuthBase):
    api_key: str
    header_name: str = "X-API-Key"

    def apply_headers(self, headers: dict[str, str]) -> None:
        headers[self.header_name] = self.api_key
