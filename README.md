# Pricing API - Python com segurança de Java

API de cálculo de pedidos feita pra provar que Python pode ser tão seguro quanto Java se usado do jeito certo.

## Por que esse projeto existe?

Todo tutorial de FastAPI básico permite conversões implícitas perigosas (como `"100"` + `"20"`). 
Este projeto aplica 6 regras de API segura:

1. **Toda entrada é BaseModel strict** - nada de `dict` solto.
2. **Dinheiro sempre `strict=True`** - strings mascaradas como números geram erro imediato (`422`).
3. **Regra de negócio direto no Field** - validações de limite (`gt=0`, `le=50`).
4. **Validação cruzada com `model_validator`** - cupom OU desconto, nunca os dois.
5. **`mypy strict` no CI** - impede reatribuição incorreta de tipos.
6. **Saída tipada** - garante que nenhum dado sensível vaze.

## Como rodar localmente

```bash
# Instalar dependências em modo editável com grupo de desenvolvimento
pip install -e . --group dev

# Executar verificação estática de tipos
mypy app/

# Rodar a bateria de testes unitários e de integração
pytest -v

# Subir o servidor de desenvolvimento
uvicorn app.main:app --reload
