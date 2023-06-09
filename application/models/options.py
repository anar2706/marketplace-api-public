from pydantic import BaseModel


class CountryResponse(BaseModel):
    id: int
    name: str


class FaqResponse(BaseModel):
    question: str
    answer: str