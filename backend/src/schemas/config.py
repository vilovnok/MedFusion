from pydantic import BaseModel

class TunedModel(BaseModel):

    class Config:
        from_attributes = True
