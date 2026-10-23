from app.domain import IdpIdentity


class IdpFake:
    def __init__(self, default_email: str) -> None:
        self.default_email = default_email

    def login_url(self, redirect_uri: str, state: str, login_hint: str | None = None) -> str:
        return f"{redirect_uri}?state={state}&email={login_hint or self.default_email}"

    async def complete(self, params: dict[str, str]) -> IdpIdentity:
        return IdpIdentity(email=params["email"])
