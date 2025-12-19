# SOFTWARE DESIGN DOCUMENT (SDD): PROJECT WATCHDOG
**Project Name:** Watchdog Enterprise Service Platform
**Version:** 1.0 (Winter Vacation 2025 Edition)
**Status:** Initial Design Phase
**Author:** [Your Name/Student ID]

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to outline the architectural design for "Watchdog," a service-oriented enterprise application. It serves as a blueprint for implementing a polyglot microservices system that leverages the strengths of Spring, Go, and Python.

### 1.2 Scope
Watchdog is designed as a distributed system to handle enterprise-grade tasks, specifically focusing on data ingestion (Go), business logic and orchestration (Spring), and intelligent text analysis/ML (Python NLP).

---

## 2. System Overview

### 2.1 Architectural Pattern
The system utilizes a **Microservices Architecture** with an **API Gateway** pattern. Each service is decoupled, maintains its own data store, and communicates via RESTful APIs and asynchronous message queues.

### 2.2 Technology Stack
* **Backend Orchestration:** Spring Boot (Java) - Handles complex business logic and security.
* **High-Performance Ingestion:** Go (Golang) - Handles concurrent data processing and system-level tasks.
* **Intelligence Layer:** Python (FastAPI/Flask) - Integrates NLP models and ML inference.
* **Frontend:** TypeScript (React/Next.js) - Provides a type-safe, responsive interface.
* **Inter-service Communication:** gRPC (internal) and REST (external).
* **Infrastructure:** Docker & Kubernetes (Local orchestration for development).

---

## 3. System Architecture

### 3.1 Subsystem Decomposition

1.  **Gateway Service (Spring Cloud Gateway / Go-based)**
    * **Role:** Single entry point for the TypeScript frontend.
    * **Tasks:** Rate limiting, routing, and preliminary authentication check.

2.  **Core Enterprise Service (Spring Boot)**
    * **Role:** Central "Brain" of the enterprise logic.
    * **Tasks:** User management, RBAC, transaction management, and coordinating between services.

3.  **Data Watcher Service (Go)**
    * **Role:** High-concurrency worker.
    * **Tasks:** Monitoring external data feeds, system logging, and high-speed data ingestion into the pipeline.

4.  **NLP Analytics Service (Python)**
    * **Role:** Cognitive layer.
    * **Tasks:** Sentiment analysis, entity recognition, and enterprise document classification using NLP models.

---

## 4. Data Design

### 4.1 Database Strategy (Database-per-Service)
* **Core Service:** PostgreSQL (Relational data, User accounts, Audit logs).
* **Watcher Service:** Redis (Fast caching of real-time events) or MongoDB (Unstructured logs).
* **NLP Service:** Vector Database (e.g., Pinecone or Milvus) for storing embeddings.

### 4.2 Data Flow
1.  **Ingestion:** Go Service picks up raw data -> Publishes to a Message Broker (Kafka/RabbitMQ).
2.  **Processing:** Spring Service consumes message -> Validates -> Stores in PostgreSQL.
3.  **Enrichment:** Python Service periodically analyzes stored data -> Updates metadata with NLP insights.

---

## 5. Component Design

### 5.1 API Interface Specifications (Examples)

#### User Authentication (Spring Boot)
* `POST /api/v1/auth/login`
* `GET /api/v1/users/profile` (Requires JWT)

#### Document Analysis (Python NLP)
* `POST /api/internal/nlp/analyze`
* **Request:** `{ "text": "Enterprise contract content..." }`
* **Response:** `{ "entities": ["Date", "Vendor"], "sentiment": 0.85 }`

#### System Health (Go)
* `GET /api/v1/health/metrics` (Real-time resource monitoring)

---

## 6. Security Design

* **Identity Management:** Spring Security with OAuth2/JWT.
* **Internal Security:** Mutual TLS (mTLS) for communication between the Go and Python services.
* **Validation:** Strict TypeScript interfaces on the frontend to prevent malformed data entry.

---

## 7. Deployment & DevOps

* **Containerization:** Each service has a dedicated `Dockerfile`.
* **Environment:** Development will use `docker-compose` to spin up the full polyglot stack locally during winter vacation.
* **Monitoring:** Go-based agents pushing metrics to a centralized dashboard.

---

## 8. Development Roadmap

1.  **Phase 1:** Setup Spring Boot Auth and TypeScript Frontend skeleton.
2.  **Phase 2:** Implement Go service for raw data ingestion.
3.  **Phase 3:** Integrate Python NLP microservice for data enrichment.
4.  **Phase 4:** Orchestrate with Docker and finalize inter-service communication.