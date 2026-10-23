from typing import Protocol

from app.domain import IdpIdentity


class IdpPort(Protocol):
    def login_url(self, redirect_uri: str, state: str, login_hint: str | None = None) -> str: ...

    async def complete(self, params: dict[str, str]) -> IdpIdentity: ...
