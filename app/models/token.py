from pydantic import BaseModel


class DownloadToken(BaseModel):
    token: str
