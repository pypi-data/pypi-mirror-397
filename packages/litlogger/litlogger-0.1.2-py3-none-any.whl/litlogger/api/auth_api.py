from lightning_sdk.lightning_cloud.login import Auth


class AuthApi:
    def __init__(self) -> None:
        self.auth = Auth()

    def authenticate(self) -> None:
        self.auth.authenticate()
