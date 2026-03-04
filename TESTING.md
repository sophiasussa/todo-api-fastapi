# Testing Strategy

Este documento descreve a estratégia de testes adotada no projeto, incluindo tipos de testes, princípios arquiteturais, execução e garantias de consistência.

---

## Objetivo

Garantir:

- Correção das regras de negócio
- Confiabilidade dos endpoints HTTP
- Isolamento transacional
- Segurança contra race conditions
- Consistência do banco de dados sob concorrência

A estratégia segue uma abordagem inspirada na **Pirâmide de Testes**, priorizando testes unitários rápidos e complementando com testes de integração e concorrência.

---

# Tipos de Testes

## 1 - Unit Tests (`@pytest.mark.unit`)

Testam regras de negócio de forma isolada.

### Características:
- Foco em services
- Não dependem da camada HTTP
- Validam exceções de domínio
- Garantem rollback em caso de erro
- Executam rapidamente

### Exemplos de cenários:
- Criar task
- Completar task
- Impedir completar task já concluída
- Garantir rollback transacional

Executar:

pytest -m unit

## 2 - Integration Tests(`@pytest.mark.integration`)

Testam o fluxo completo da aplicação:

HTTP Request → Router → Service → Database → Response

### Características:

-Utilizam TestClient
-Validam contratos HTTP
-Verificam status codes
-Validam estrutura da resposta
-Confirmam persistência no banco

### Exemplos de cenários:
-Criar task via endpoint
-Atualizar task
-Buscar task
-Erros 404
-Códigos de erro padronizados

Executar:

pytest -m integration

## 3 - Concurrency Tests(`@pytest.mark.concurrency`)

Testam o comportamento do sistema sob múltiplas requisições simultâneas.
Utilizam ThreadPoolExecutor para simular chamadas concorrentes.

### Objetivos:
-Garantir atomicidade
-Validar idempotência
-Testar conflitos (409)
-Evitar race conditions
-Garantir isolamento de sessão por request

### Cenários testados:
-Duas requisições tentando completar a mesma task
-Duas requisições tentando deletar a mesma task
-Atualizações concorrentes
-Verificação de sessão isolada por request

Executar:

pytest -m concurrency

# Isolamento de Banco de Dados

Cada requisição utiliza uma sessão isolada de banco de dados.

## Isso garante:
-Segurança em ambiente concorrente
-Rollback automático em exceções
-Independência entre threads
-Consistência transacional

Os testes validam explicitamente esse comportamento.

# Garantias Arquiteturais Validadas pelos Testes
-Nenhuma operação crítica é executada duas vezes indevidamente
-Tasks já concluídas não podem ser concluídas novamente
-Atualizações concorrentes resultam em sucesso ou conflito controlado
-Deleções concorrentes não quebram o sistema
-Transações são revertidas em caso de erro
-Cada request usa sessão independente

# Executando Todos os Testes

Coverage (opcional)

Para gerar relatório de cobertura:

pytest --cov=app --cov-report=term-missing

## Filosofia

### Os testes não apenas verificam funcionalidades — eles validam decisões arquiteturais:
-Separação entre camadas
-Segurança transacional
-Tratamento explícito de erros de domínio
-Robustez sob concorrência

O objetivo é manter um backend previsível, seguro e resiliente.
