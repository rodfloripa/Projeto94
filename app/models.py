from typing import Annotated
from pydantic import BaseModel, Field, model_validator

class ItemRequest(BaseModel):
    model_config = {"strict": True}
    sku: Annotated[str, Field(min_length=3, max_length=20)]
    preco_base: Annotated[float, Field(gt=0)]
    quantidade: Annotated[int, Field(gt=0, le=1000)]

class PedidoRequest(BaseModel):
    model_config = {"strict": True}
    itens: Annotated[list[ItemRequest], Field(min_length=1, max_length=100)]
    cupom: Annotated[str | None, Field(min_length=3)] = None
    desconto_percent: Annotated[float, Field(ge=0, le=50)] = 0.0

    @model_validator(mode="after")
    def valida_cupom(self) -> "PedidoRequest":
        if self.cupom and self.desconto_percent != 0:
            raise ValueError("Use cupom OU desconto_percent, não ambos")
        return self

class ItemResponse(BaseModel):
    model_config = {"strict": True}
    sku: str
    total_item: float

class PedidoResponse(BaseModel):
    model_config = {"strict": True}
    total_bruto: float
    total_liquido: float
    itens: list[ItemResponse]
