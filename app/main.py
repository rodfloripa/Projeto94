from fastapi import FastAPI
from app.models import PedidoRequest, PedidoResponse
from app.service import calcula_pedido

app = FastAPI(title="Pricing API - Do Jeito Certo")

@app.post("/pedido/calcular", response_model=PedidoResponse)
def calcular(pedido: PedidoRequest) -> PedidoResponse:
    return calcula_pedido(pedido)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
