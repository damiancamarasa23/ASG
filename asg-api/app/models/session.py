from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    consumer_platform_id: str
    user_id: str
    brand: str = "gucci"


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: str


class GetUploadUrlRequest(BaseModel):
    session_id: str
    filename: str  # e.g. "01_gg_canvas.jpg"


class GetUploadUrlResponse(BaseModel):
    upload_url: str
    filename: str


class ConfirmUploadRequest(BaseModel):
    session_id: str
    filename: str


class ConfirmUploadResponse(BaseModel):
    session_id: str
    filename: str
    confirmed: bool
