# Software Requirements Specification (SRS)
## Project Watchdog: Enterprise Smart Monitoring & Triage

**Version:** 1.0
**Date:** 2026-02-05
**Status:** Initial Design

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to define the software requirements for **Watchdog**, an intelligent, polyglot microservices system designed to monitor enterprise ecosystem health. This system aims to replace traditional reactive ticketing with a hybrid **Proactive + Reactive** strategy, leveraging distinct strengths of Go, Java (Spring Boot), and Python.

### 1.2 Scope
Watchdog operates as a distributed system focusing on:
1.  **High-Velocity Data Ingestion:** Buffered collection of system logs and metrics.
2.  **Intelligent Triage:** Automating ticket classification using Natural Language Processing (NLP).
3.  **Proactive Alerting:** Monitoring leading indicators (latency, saturation) to predict failures.
4.  **Centralized Orchestration:** Managing incident lifecycles and enterprise security.
5.  **Visualization:** providing a real-time operational dashboard.

### 1.3 Definitions, Acronyms, and Abbreviations
*   **SRS:** Software Requirements Specification
*   **RBAC:** Role-Based Access Control
*   **NLP:** Natural Language Processing
*   **ELK:** Elasticsearch, Logstash, Kibana
*   **JWT:** JSON Web Token
*   **mTLS:** Mutual Transport Layer Security

---

## 2. Overall Description

### 2.1 Product Perspective
Watchdog is a standalone enterprise suite composed of four primary microservices communicating via asynchronous messaging (RabbitMQ/Kafka) and synchronous APIs (REST/gRPC). It integrates with external observability tools like Prometheus, Grafana, and the ELK stack.

### 2.2 Product Functions
*   **Ingest** raw logs and metrics from external sources.
*   **Filter** noise from critical operational signals.
*   **Classify** incident logs by severity and category using AI/ML.
*   **Manage** the lifecycle of support tickets (Open -> Resolved).
*   **Visualize** real-time system health and log streams.

### 2.3 User Classes and Characteristics
*   **System Administrators/DevOps:** Monitor dashboards, configure alert thresholds, and resolve tickets.
*   **Service Accounts:** Automated agents pushing logs to the Ingestion Service.

---

## 3. System Architecture & Components

The system follows a **Microservices Architecture** with the following core components:

### 3.1 The Ears: Ingestion Service (Go)
*   **Role:** High-Throughput Log Buffer & Data Watcher.
*   **Responsibilities:**
    *   Listen for incoming logs and metrics via HTTP/gRPC.
    *   Buffer data using internal channels to handle concurrency.
    *   Filter "noise" vs. "signals" before downstream processing.
    *   Publish sanitized data to Message Brokers (RabbitMQ/Kafka).
*   **Tech Stack:** Go (Golang), Gin/Fiber.

### 3.2 The Nervous System: Core Service (Java/Spring Boot)
*   **Role:** Central Orchestrator & Business Logic.
*   **Responsibilities:**
    *   **Identity Management:** Handle User Auth, RBAC, and JWT issuance.
    *   **Ticket Management:** CRUD operations for incident tickets and state transitions.
    *   **Rules Engine:** Evaluate metrics against thresholds (e.g., "5 errors in 10s -> Critical Alert").
    *   **Data Persistence:** Store relational data (users, tickets, audit logs).
*   **Tech Stack:** Spring Boot 3, JPA, PostgreSQL, Spring Security.

### 3.3 The Nose: Intelligence Service (Python)
*   **Role:** Cognitive Layer & Classifier.
*   **Responsibilities:**
    *   Consume unstructured text (logs/descriptions).
    *   Apply NLP models (DistilBERT) to predict **Category** (e.g., Database, Network) and **Severity**.
    *   Return enrichment data to the Core Service.
*   **Tech Stack:** FastAPI, PyTorch/TensorFlow, HuggingFace.

### 3.4 The Face: Dashboard (TypeScript/React)
*   **Role:** Visualization & Control Plane.
*   **Responsibilities:**
    *   Display a real-time Kanban board for active tickets.
    *   Render a live stream of ingested logs via WebSockets.
    *   Provide administrative interfaces for user management.
*   **Tech Stack:** React, TypeScript, TailwindCSS.

### 3.5 Gateway Service (Optional/Infrastructure)
*   **Role:** Entry Point.
*   **Responsibilities:** Rate limiting, routing, and preliminary authentication checks.

---

## 4. Functional Requirements

### 4.1 Data Ingestion & Processing
*   **FR-01:** The system shall accept JSON formatted logs via HTTP POST.
*   **FR-02:** The system shall buffer high-volume requests to prevent database saturation.
*   **FR-03:** The system shall categorize inputs as either "Metric" (proactive) or "Log" (reactive).

### 4.2 Incident Management
*   **FR-04:** The system shall automatically generate a Ticket Entity when a Critical threshold is breached.
*   **FR-05:** Tickets must have the following states: `OPEN`, `INVESTIGATING`, `RESOLVED`.
*   **FR-06:** Users shall be able to manually update Ticket status and add comments.

### 4.3 Intelligent Analysis
*   **FR-07:** The system shall analyze incoming log text to detect sentiment or urgency.
*   **FR-08:** The system shall assign a probability score to the predicted Severity level.

### 4.4 Security
*   **FR-09:** All API endpoints (except Health Checks and Auth) must require a valid JWT.
*   **FR-10:** Inter-service communication should theoretically support mTLS (Roadmap).

---

## 5. Data Requirements

### 5.1 Schema Overview (Relational - PostgreSQL)
**Ticket Entity**
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Unique Identifier |
| `source` | Varchar | Origin service (e.g., "PaymentService") |
| `type` | Enum | `PROACTIVE_ALERT`, `REACTIVE_CRASH` |
| `severity` | Enum | `LOW`, `MEDIUM`, `CRITICAL` |
| `status` | Enum | `OPEN`, `INVESTIGATING`, `RESOLVED` |
| `created_at` | Timestamp | Time of creation |

### 5.2 Storage Strategy (Polyglot Persistence)
*   **PostgreSQL:** Core business data (Users, Tickets).
*   **Redis/MongoDB:** Temporary buffer for high-speed log ingestion (optional).
*   **Vector DB:** (Future) Storing embeddings for semantic search of logs.

---

## 6. Interface Requirements

### 6.1 User Interfaces
*   **Dashboard:** Web-based UI optimized for desktop monitors.
*   **Charts:** Time-series graphs for system metrics (latency, error rate).

### 6.2 Communication Interfaces
*   **External API:** RESTful JSON APIs for clients.
*   **Internal Messaging:** RabbitMQ or Kafka for decoupling Ingestion from Core.
*   **Observability:** `/metrics` endpoints compatible with Prometheus scraping.

---

## 7. Roadmap & Milestones

### Phase 1: The Skeleton
*   Initialize Monorepo structure.
*   Build basic Go HTTP Ingestor.
*   Setup Spring Boot with PostgreSQL and basic Entities.

### Phase 2: The Senses
*   Train Python NLP model on incident datasets.
*   Connect Go Ingestor to Core Service (via REST or Queue).

### Phase 3: The Intelligence
*   Implement Threshold Logic in Spring (Proactive).
*   Integrate Python Model API for real-time classification.

### Phase 4: The Interface & Ops
*   Build React Dashboard.
*   Dockerize all services.
*   Attach Grafana/Prometheus for full observability.
