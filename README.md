
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

---

## 📁 Estrutura e Arquivos do Projeto

Para manter o código limpo, testável e desacoplado, o projeto é dividido nos seguintes arquivos:

```text
pricing-api/
├── app/
│   ├── __init__.py      # Torna a pasta 'app' um pacote Python válido
│   ├── main.py          # Ponto de entrada da API (Rotas FastAPI e inicialização do app)
│   ├── models.py        # Modelos de dados e validações estritas (Pydantic v2)
│   └── service.py       # Regra de negócio pura, isolada e 100% testável sem o FastAPI
├── tests/
│   ├── __init__.py      # Torna a pasta 'tests' um pacote de testes
│   ├── test_api.py      # Testes de integração da API via TestClient (valida status HTTP e endpoints)
│   └── test_models.py   # Testes unitários focados nas validações e regras dos modelos Pydantic
├── Dockerfile           # Configuração de containerização otimizada para produção
└── pyproject.toml       # Gerenciamento de dependências, metadados e configuração do Mypy/Pytest
```

### Detalhes de cada componente:
* **`app/models.py`**: Define os contratos de entrada e saída usando `BaseModel` do Pydantic com `strict=True`. É aqui que garantimos que tipos errados (como strings em campos numéricos) sejam barrados na porta com um erro `422`, além de aplicar validações cruzadas (`model_validator`).
* **`app/service.py`**: Contém o coração da regra de negócio (`calcula_pedido`). Como ele não importa o FastAPI, ele pode ser testado isoladamente ou reutilizado em jobs de processamento em lote (*batch*).
* **`app/main.py`**: Configura a instância do FastAPI e expõe os endpoints HTTP (`/pedido/calcular` e `/health`), delegando o processamento pesado para a camada de serviço.
* **`tests/test_models.py`**: Valida unitariamente se as restrições e exceções do Pydantic estão funcionando conforme esperado.
* **`tests/test_api.py`**: Simula requisições HTTP reais na aplicação para garantir que os retornos e códigos de status HTTP correspondam às expectativas.
* **`pyproject.toml`**: Centraliza as dependências do projeto e as regras rígidas de tipagem estática do `mypy` (`strict = true`).

### 📥 O que a API Recebe (Request Body)
A rota `POST /pedido/calcular` espera receber um JSON contendo os dados do pedido. A estrutura aceita uma lista de itens e regras opcionais de desconto ou cupom:

```json
{
  "itens": [
    {
      "sku": "string",       // Código/SKU do produto (obrigatório)
      "preco_base": 0.0,     // Preço unitário (obrigatório, float estrito, > 0)
      "quantidade": 1        // Quantidade do item (obrigatório, inteiro, entre 1 e 50)
    }
  ],
  "desconto_percent": 10.0,  // Opcional: Desconto em porcentagem (ex: 10 para 10%)
  "cupom": "PROMO10"         // Opcional: Código de cupom de desconto
}
```
* **Regra de ouro aplicada:** O Pydantic garante que se você enviar uma string onde deveria ser um número (ex: `"preco_base": "100"`), a API rejeita imediatamente com erro `422`. Além disso, a validação cruzada impede que você envie `desconto_percent` e `cupom` ao mesmo tempo.

---

### 📤 O que a API Devolve (Response Body)
Quando a requisição é bem-sucedida (**HTTP 200 OK**), ela retorna um JSON estrito contendo os cálculos consolidados do pedido:

```json
{
  "total_bruto": 200.0,      // Valor total dos itens antes de qualquer desconto
  "total_liquido": 180.0,    // Valor final a pagar após a aplicação do desconto
  "itens": [
    {
      "sku": "ABC123",       // SKU do produto processado
      "total_item": 200.0    // Subtotal daquele item específico (preço_base × quantidade)
    }
  ]
}
```
* **Garantia de segurança:** A saída é totalmente tipada e filtrada, garantindo que nenhum dado interno ou sensível da aplicação vaze para o cliente.

---

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
```

## Testando via cURL

```bash
# Cálculo bem-sucedido
curl -X POST http://localhost:8000/pedido/calcular \
  -H "Content-Type: application/json" \
  -d '{"itens": [{"sku": "ABC123", "preco_base": 100.0, "quantidade": 2}], "desconto_percent": 10}'
{"total_bruto":200.0,"total_liquido":180.0,"itens":[{"sku":"ABC123","total_item":200.0}]}

# Tentativa de injetar string no preço (Retorna 422)
 curl -X POST http://localhost:8000/pedido/calcular \
  -H "Content-Type: application/json" \
  -d '{"itens": [{"sku": "ABC", "preco_base": "100", "quantidade": 1}]}'
{"detail":[{"type":"float_type","loc":["body","itens",0,"preco_base"],"msg":"Input should be a valid number","input":"100"}]}

```

```
