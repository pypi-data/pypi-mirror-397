from typing import Optional, ClassVar


class TokenStorage:
    access_token: ClassVar[Optional[str]] = None

    @classmethod
    def get_token(cls) -> Optional[str]:
        return cls.access_token

    @classmethod
    def remove_token(cls) -> Optional[str]:
        delete_token = cls.access_token
        cls.access_token = None
        return delete_token

    @classmethod
    def set_token(cls, token: str) -> None:
        cls.access_token = token
