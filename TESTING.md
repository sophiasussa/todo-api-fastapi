# Testing Strategy

This document describes the testing strategy adopted in the project, including test types, architectural principles, execution, and consistency guarantees.

---

## Objective

Ensure:

- Correctness of business rules
- Reliability of HTTP endpoints
- Transactional isolation
- Protection against race conditions
- Database consistency under concurrency

The strategy follows an approach inspired by the **Testing Pyramid**, prioritizing fast unit tests and complementing them with integration and concurrency tests.

---

# Test Types

## 1 - Unit Tests (`@pytest.mark.unit`)

Test business rules in isolation.

### Characteristics:
- Focused on services
- Do not depend on the HTTP layer
- Validate domain exceptions
- Ensure rollback on error
- Execute quickly

### Example scenarios:
- Create task
- Complete task
- Prevent completing an already completed task
- Ensure transactional rollback

Run:

pytest -m unit

## 2 - Integration Tests(`@pytest.mark.integration`)

Test the complete application flow:

HTTP Request → Router → Service → Database → Response

### Characteristics:
- Use TestClient
- Validate HTTP contracts
- Check status codes
- Validate response structure
- Confirm database persistence

### Example scenarios:
- Create task via endpoint
- Update task
- Fetch task
- 404 errors
- Standardized error codes

Run:

pytest -m integration

## 3 - Concurrency Tests(`@pytest.mark.concurrency`)

Test system behavior under multiple simultaneous requests. Use ThreadPoolExecutor to simulate concurrent calls.

### Objectives:
- Ensure atomicity
- Validate idempotency
- Test conflicts (409)
- Avoid race conditions
- Ensure per-request session isolation

### Tested scenarios:
- Two requests attempting to complete the same task
- Two requests attempting to delete the same task
- Concurrent updates
- Isolated session verification per request

Run:

pytest -m concurrency

# Database Isolation

Each request uses an isolated database session.

## This ensures:
- Safety in concurrent environments
- Automatic rollback on exceptions
- Independence between threads
- Transactional consistency

Tests explicitly validate this behavior.

# Architectural Guarantees Validated by Tests
- No critical operation is executed twice without cause
- Already completed tasks cannot be completed again
- Concurrent updates result in either success or a controlled conflict
- Concurrent deletions do not break the system
- Transactions are rolled back on error
- Each request uses an independent session

# Running All Tests

Coverage (opcional)

To generate a coverage report:

pytest --cov=app --cov-report=term-missing

## Philosophy

### Tests do not merely verify features — they validate architectural decisions:
- Separation of concerns between layers
- Transactional safety
- Explicit handling of domain errors
- Robustness under concurrency

The goal is to maintain a predictable, secure, and resilient backend.
