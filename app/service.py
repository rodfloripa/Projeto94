from app.models import PedidoRequest, PedidoResponse, ItemResponse

CUPONS: dict[str, float] = {"BLACK10": 10.0, "FLORIPA20": 20.0}

def calcula_pedido(pedido: PedidoRequest) -> PedidoResponse:
    total_bruto = 0.0
    itens_resp: list[ItemResponse] = []

    for item in pedido.itens:
        total_item = item.preco_base * item.quantidade
        total_bruto += total_item
        itens_resp.append(ItemResponse(sku=item.sku, total_item=total_item))

    desconto = pedido.desconto_percent
    if pedido.cupom:
        desconto = CUPONS.get(pedido.cupom.upper(), 0.0)

    total_liquido = total_bruto * (1 - desconto / 100)
    return PedidoResponse(
        total_bruto=round(total_bruto, 2),
        total_liquido=round(total_liquido, 2),
        itens=itens_resp
    )
