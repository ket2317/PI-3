from pydantic import BaseModel


class PaymentMethodResponse(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}
