from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_retorna_422_se_texto() -> None:
    resp = client.post("/pedido/calcular", json={
        "itens": [{"sku": "ABC", "preco_base": "cem", "quantidade": 1}]
    })
    assert resp.status_code == 422

def test_api_calcula_certo() -> None:
    resp = client.post("/pedido/calcular", json={
        "itens": [{"sku": "ABC", "preco_base": 100.0, "quantidade": 2}],
        "desconto_percent": 10
    })
    assert resp.status_code == 200
    assert resp.json()["total_liquido"] == 180.0
