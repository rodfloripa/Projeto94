

<p align="justify"><h1> API de Preço - Python com segurança de Java</h1></p>

<p align="justify">API de cálculo de pedidos feita pra provar que Python pode ser tão seguro quanto Java se usado do jeito certo.</p>

<p align="justify"><h2>Por que esse projeto existe?</h2></p>

<p align="justify">Todo tutorial de FastAPI básico permite conversões implícitas perigosas (como <code>"100"</code> + <code>"20"</code>). Este projeto aplica 6 regras de API segura:</p>

* <p align="justify"><b>Toda entrada é BaseModel strict</b> - nada de <code>dict</code> solto.</p>
  <p align="justify"><i>Localização: <code>app/models.py</code> (Linhas 12-23) e <code>app/main.py</code> (Linha 15)</i></p>

```python
# app/models.py (Linhas 12-23)
class ItemPedido(BaseModel):
    sku: str
    preco_base: StrictFloat = Field(gt=0)
    quantidade: StrictInt = Field(gt=0, le=50)

class PedidoRequest(BaseModel):
    itens: list[ItemPedido]
    desconto_percent: StrictFloat | None = Field(default=None, ge=0, le=100)
    cupom: str | None = None

# app/main.py (Linha 15)
@app.post("/pedido/calcular", response_model=PedidoResponse)
def calcular_pedido_endpoint(payload: PedidoRequest) -> PedidoResponse: ...
```

* <p align="justify"><b>Dinheiro sempre <code>strict=True</code></b> - strings mascaradas como números geram erro imediato (<code>422</code>).</p>
  <p align="justify"><i>Localização: <code>app/models.py</code> (Linha 14)</i></p>

```python
# app/models.py (Linha 14)
class ItemPedido(BaseModel):
    sku: str
    preco_base: StrictFloat = Field(gt=0)  # Rejeita "100.0" (string) com erro 422
```

* <p align="justify"><b>Regra de negócio direto no Field</b> - validações de limite (<code>gt=0</code>, <code>le=50</code>).</p>
  <p align="justify"><i>Localização: <code>app/models.py</code> (Linhas 14-15 e 20)</i></p>

```python
# app/models.py (Linhas 14-15, 20)
preco_base: StrictFloat = Field(gt=0)
quantidade: StrictInt = Field(gt=0, le=50)
desconto_percent: StrictFloat | None = Field(default=None, ge=0, le=100)
```

* <p align="justify"><b>Validação cruzada com <code>model_validator</code></b> - cupom OU desconto, nunca os dois.</p>
  <p align="justify"><i>Localização: <code>app/models.py</code> (Linhas 25-32)</i></p>

```python
# app/models.py (Linhas 25-32)
@model_validator(mode="after")
def valida_cupom_ou_desconto(self) -> "PedidoRequest":
    if self.desconto_percent is not None and self.cupom is not None:
        raise ValueError("Não é permitido aplicar desconto percentual e cupom simultaneamente.")
    return self
```

* <p align="justify"><b><code>mypy strict</code> no CI</b> - impede reatribuição incorreta de tipos.</p>
  <p align="justify"><i>Localização: <code>pyproject.toml</code> (Linhas 15-18)</i></p>

```toml
# pyproject.toml (Linhas 15-18)
[tool.mypy]
strict = true
disallow_untyped_defs = true
warn_return_any = true
```

* <p align="justify"><b>Saída tipada</b> - garante que nenhum dado sensível vaze.</p>
  <p align="justify"><i>Localização: <code>app/models.py</code> (Linhas 35-43) e <code>app/main.py</code> (Linha 15)</i></p>

```python
# app/models.py (Linhas 35-43)
class ItemResposta(BaseModel):
    sku: str
    total_item: float

class PedidoResponse(BaseModel):
    total_bruto: float
    total_liquido: float
    itens: list[ItemResposta]

# app/main.py (Linha 15)
@app.post("/pedido/calcular", response_model=PedidoResponse)
```

---

<p align="justify"><h2>📁 Estrutura e Arquivos do Projeto</h2></p>

<p align="justify">Para manter o código limpo, testável e desacoplado, o projeto é dividido nos seguintes arquivos:</p>

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

<p align="justify"><h3>Detalhes de cada componente:</h3></p>

* <p align="justify"><b><code>app/models.py</code></b>: Define os contratos de entrada e saída usando <code>BaseModel</code> do Pydantic com <code>strict=True</code>. É aqui que garantimos que tipos errados (como strings em campos numéricos) sejam barrados na porta com um erro <code>422</code>, além de aplicar validações cruzadas (<code>model_validator</code>).</p>
* <p align="justify"><b><code>app/service.py</code></b>: Contém o coração da regra de negócio (<code>calcula_pedido</code>). Como ele não importa o FastAPI, ele pode ser testado isoladamente ou reutilizado em jobs de processamento em lote (<i>batch</i>).</p>
* <p align="justify"><b><code>app/main.py</code></b>: Configura a instância do FastAPI e expõe os endpoints HTTP (<code>/pedido/calcular</code> e <code>/health</code>), delegando o processamento pesado para a camada de serviço.</p>
* <p align="justify"><b><code>tests/test_models.py</code></b>: Valida unitariamente se as restrições e exceções do Pydantic estão funcionando conforme esperado.</p>
* <p align="justify"><b><code>tests/test_api.py</code></b>: Simula requisições HTTP reais na aplicação para garantir que os retornos e códigos de status HTTP correspondam às expectativas.</p>
* <p align="justify"><b><code>pyproject.toml</code></b>: Centraliza as dependências do projeto e as regras rígidas de tipagem estática do <code>mypy</code> (<code>strict = true</code>).</p>

---

<p align="justify"><h3>📥 O que a API Recebe (Request Body)</h3></p>

<p align="justify">A rota <code>POST /pedido/calcular</code> espera receber um JSON contendo os dados do pedido. A estrutura aceita uma lista de itens e regras opcionais de desconto ou cupom:</p>

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

* <p align="justify"><b>Regra de ouro aplicada:</b> O Pydantic garante que se você enviar uma string onde deveria ser um número (ex: <code>"preco_base": "100"</code>), a API rejeita imediatamente com erro <code>422</code>. Além disso, a validação cruzada impede que você envie <code>desconto_percent</code> e <code>cupom</code> ao mesmo tempo.</p>

---

<p align="justify"><h3>📤 O que a API Devolve (Response Body)</h3></p>

<p align="justify">Quando a requisição é bem-sucedida (<b>HTTP 200 OK</b>), ela retorna um JSON estrito contendo os cálculos consolidados do pedido:</p>

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

* <p align="justify"><b>Garantia de segurança:</b> A saída é totalmente tipada e filtrada, garantindo que nenhum dado interno ou sensível da aplicação vaze para o cliente.</p>

---

<p align="justify"><h2>Como rodar localmente</h2></p>

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

---

<p align="justify"><h2>Testando via cURL</h2></p>

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

---

<p align="justify"><h2>🚀 Deploy da Pricing API no AWS App Runner (Passo a Passo)</h2></p>

<p align="justify">O <b>AWS App Runner</b> é a forma mais simples, rápida e moderna de rodar containers Docker em produção na AWS. Ele gerencia automaticamente o balanceamento de carga, os certificados HTTPS, a infraestrutura e o autoscaling.</p>

<p align="justify"><h3>📋 Pré-requisitos</h3></p>

* <p align="justify">Uma conta na <b>AWS</b>.</p>
* <p align="justify"><b>Docker</b> e <b>AWS CLI</b> instalados e configurados na sua máquina local.</p>
* <p align="justify">Repositório do projeto com o <code>Dockerfile</code> finalizado.</p>

---

<p align="justify"><h3>Passo 1: Subir a Imagem Docker para o Amazon ECR</h3></p>

<p align="justify">O Amazon ECR (Elastic Container Registry) é o repositório privado onde guardaremos a imagem Docker da API.</p>

<p align="justify">1. <b>Faça login no ECR via AWS CLI</b> (substitua <code>&lt;REGION&gt;</code> e <code>&lt;ACCOUNT_ID&gt;</code> pelos seus dados):</p>

```bash
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

<p align="justify">2. <b>Crie o repositório no ECR:</b></p>

```bash
aws ecr create-repository --repository-name pricing-api
```

<p align="justify">3. <b>Gere a imagem da sua aplicação:</b></p>

```bash
docker build -t pricing-api .
```

<p align="justify">4. <b>Adicione a tag da imagem apontando para o ECR:</b></p>

```bash
docker tag pricing-api:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/pricing-api:latest
```

<p align="justify">5. <b>Envie a imagem para a AWS:</b></p>

```bash
docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/pricing-api:latest
```

---

<p align="justify"><h3>⚙️ Passo 2: Configurar o AWS App Runner</h3></p>

<p align="justify">1. Acesse o <b>Console da AWS</b> e navegue até o serviço <b>AWS App Runner</b>.</p>
<p align="justify">2. Clique em <b>Create an App Runner service</b>.</p>
<p align="justify">3. Na seção <b>Source</b>:</p>

* <p align="justify">Escolha <b>Container registry</b>.</p>
* <p align="justify">Em <b>Provider</b>, selecione <b>Amazon ECR</b>.</p>
* <p align="justify">Em <b>Container image URI</b>, selecione o repositório <code>pricing-api</code> e a tag <code>latest</code>.</p>
* <p align="justify">Em <b>Deployment trigger</b>, escolha <b>Automatic</b> (assim, sempre que você mandar uma imagem nova para o ECR, o App Runner atualiza a API sozinho).</p>

<p align="justify">4. Clique em <b>Next</b>.</p>

---

<p align="justify"><h3>🔧 Passo 3: Configurar o Serviço de Aplicação</h3></p>

<p align="justify">1. <b>Service name:</b> Informe <code>pricing-api-prod</code>.</p>
<p align="justify">2. <b>Virtual CPU & Memory:</b> Escolha a menor configuração para começar (ex: <code>1 vCPU</code> e <code>2 GB</code>).</p>
<p align="justify">3. <b>Port:</b> Defina como <code>8000</code> (a porta exposta pelo seu <code>Dockerfile</code>/Uvicorn).</p>
<p align="justify">4. <b>Environment variables:</b> Adicione variáveis de produção se necessário (ex: <code>ENVIRONMENT=production</code>).</p>
<p align="justify">5. Clique em <b>Next</b>, revise as configurações e clique em <b>Create & deploy</b>.</p>

---

<p align="justify"><h3>✅ Passo 4: Validação e Teste em Produção</h3></p>

<p align="justify">Após alguns minutos, o App Runner finalizará a implantação e fornecerá uma URL pública segura (ex: <code>https://xyz123.us-east-1.awsapprunner.com</code>).</p>

<p align="justify">Para validar a API em produção, execute o <code>cURL</code> apontando para a nova URL pública:</p>

```bash
curl -X POST https://<SUA-URL-APP-RUNNER>/pedido/calcular \
  -H "Content-Type: application/json" \
  -d '{"itens": [{"sku": "ABC123", "preco_base": 100.0, "quantidade": 2}], "desconto_percent": 10}'
```

<p align="justify"><b>Resposta esperada (HTTP 200):</b></p>

```json
{"total_bruto":200.0,"total_liquido":180.0,"itens":[{"sku":"ABC123","total_item":200.0}]}
```
