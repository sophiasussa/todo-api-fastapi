# 📝 Todo API – FastAPI

[![CI](https://github.com/sophiasussa/todo-api-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/sophiasussa/todo-api-fastapi/actions)
[![codecov](https://codecov.io/gh/sophiasussa/todo-api-fastapi/branch/main/graph/badge.svg)](https://codecov.io/gh/sophiasussa/todo-api-fastapi)

API REST para gerenciamento de tarefas (**To-do**) desenvolvida com **FastAPI**, focada em boas práticas de backend, testes automatizados e integração contínua.

---

## 🚀 Tecnologias

* Python 3.11
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pytest
* Docker
* GitHub Actions (CI)
* Codecov

---

## 📂 Estrutura do Projeto

```
app/
 ├── exceptions/
 ├── models/
 ├── routes/
 ├── database/
 ├── schemas/
 ├── services/
 └── main.py

tests/
 ├── unit/
 └── integration/
```

---

## 🧪 Testes

O projeto possui dois tipos de testes:

* **Unitários**: isolados, rápidos, usando SQLite em memória
* **Integração**: testam o sistema com PostgreSQL real em um banco de dados teste via Docker

### Rodar testes localmente

```bash
pytest -m unit
pytest -m integration
```

### Rodar testes com coverage

```bash
pytest --cov=app
```

---

## 📊 Coverage

A cobertura de testes é monitorada automaticamente pelo **Codecov**.

* Coverage mínimo exigido: **70%**
* Pull Requests falham se o coverage cair abaixo do limite

---

## 🔄 CI – Integração Contínua

O pipeline de CI roda automaticamente em:

* Push para `main` ou `develop`
* Pull Requests

Etapas do CI:

1. Instala dependências
2. Roda testes unitários
3. Roda testes de integração
4. Gera relatório de coverage
5. Envia dados para o Codecov

---

## ▶️ Executar a API localmente

A API e o banco de dados PostgreSQL são executados via Docker.

```bash
docker compose up -d
```

Acesse a documentação interativa em:

http://localhost:8000/docs

---

## 📄 Licença

Este projeto é apenas para fins de estudo e portfólio.
