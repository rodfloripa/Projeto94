import pytest
from pydantic import ValidationError
from app.models import ItemRequest, PedidoRequest

def test_barra_string_no_preco() -> None:
    with pytest.raises(ValidationError):
        ItemRequest(sku="ABC123", preco_base="100", quantidade=1) # type: ignore[arg-type]

def test_barra_desconto_maior_50() -> None:
    with pytest.raises(ValidationError):
        PedidoRequest(
            itens=[{"sku": "ABC", "preco_base": 10.0, "quantidade": 1}],
            desconto_percent=51.0
        )

def test_barra_cupom_e_desconto_juntos() -> None:
    with pytest.raises(ValidationError):
        PedidoRequest(
            itens=[{"sku": "ABC", "preco_base": 10.0, "quantidade": 1}],
            cupom="BLACK10",
            desconto_percent=10.0
        )

def test_ok() -> None:
    req = PedidoRequest(
        itens=[{"sku": "ABC", "preco_base": 10.0, "quantidade": 2}],
        desconto_percent=10.0
    )
    assert req.itens[0].preco_base == 10.0
