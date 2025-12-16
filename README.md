# 🐕 Watchdog: Enterprise Smart Monitoring & Triage

**A Polyglot Microservices System for Proactive & Reactive Incident Management**

## 📖 Overview
**Watchdog** is an intelligent system designed to monitor enterprise ecosystem health. Unlike traditional reactive ticketing systems, Watchdog employs a **Proactive + Reactive** strategy:
1.  **Proactive:** Monitors leading indicators (latency, saturation) to alert on issues *before* they cause downtime.
2.  **Reactive:** Ingests high-volume crash logs to automate triage using NLP.

**Key Learning Goals:**
- **System Design:** Polyglot Microservices with gRPC/REST.
- **High-Concurrency:** Go-based log ingestion buffer.
- **AI/ML:** NLP for text classification (Severity/Category) using Python.
- **Observability:** Integrating "Golden Signal" monitoring (Prometheus/Grafana) and Log Aggregation (ELK).

---

## 🏗️ Architecture

### 1. The Ears: Ingestion Service (Go 🐹)
* **Role:** High-Throughput Log Buffer.
* **Responsibility:** Listens for logs and metrics. buffers them using channels, and filters "noise" from "signals."
* **Tech:** Go (Golang), Gin/Fiber, RabbitMQ/Kafka (Producer).
* **Observability Hook:** Exposes `/metrics` for Prometheus.

### 2. The Nervous System: Core Service (Java/Spring Boot 🍃)
* **Role:** The Orchestrator.
* **Responsibility:**
    * **Identity:** RBAC (Role-Based Access Control).
    * **State:** Manages Ticket lifecycle (Open -> Resolved).
    * **Rules:** Triggers alerts based on thresholds (e.g., "If 5 errors in 10s -> Critical").
* **Tech:** Spring Boot 3, JPA, PostgreSQL.

### 3. The Nose: Intelligence Service (Python 🐍)
* **Role:** The Classifier.
* **Responsibility:** Analyzes unstructured text (log messages) to predict:
    * **Category:** (Database, Network, UI, Security)
    * **Severity:** (Low, High, Critical)
* **Tech:** FastAPI, PyTorch/TensorFlow, HuggingFace (DistilBERT).
* **Experimentation:** Databricks/Colab for training.

### 4. The Face: Dashboard (TypeScript/React ⚛️)
* **Role:** Visualization & Action.
* **Responsibility:** Real-time Kanban board and Live Log Stream.
* **Tech:** React, TypeScript, TailwindCSS, WebSocket.

---

## 👁️ Observability & Infrastructure
* **Metrics:** Prometheus (scraping Go/Spring) & Grafana (Dashboards).
* **Logs:** ELK Stack (Elasticsearch, Logstash, Kibana) for deep search.
* **Containerization:** Docker & Docker Compose.

---

## 💾 Data Schema (Simplified)

### Tickets
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `source` | String | e.g., "PaymentService" |
| `type` | Enum | `PROACTIVE_ALERT`, `REACTIVE_CRASH` |
| `severity` | Enum | `LOW`, `MEDIUM`, `CRITICAL` |
| `status` | Enum | `OPEN`, `INVESTIGATING`, `RESOLVED` |

---

## 🗺️ Roadmap

### Phase 1: The Skeleton
- [ ] Initialize Monorepo.
- [ ] **Go:** Build HTTP Ingestor with Prometheus hooks.
- [ ] **Spring:** Setup PostgreSQL and Ticket Entities.

### Phase 2: The Senses
- [ ] **Python:** Train DistilBERT on "IT Incident" dataset.
- [ ] **Go:** Connect Ingestor to Core (REST or Queue).

### Phase 3: The Intelligence
- [ ] **Spring:** Implement "Threshold Logic" (Proactive).
- [ ] **Python:** Integrate Model API with Spring.

### Phase 4: The Interface
- [ ] **React:** Build Dashboard.
- [ ] **Ops:** Dockerize and attach Grafana/Prometheus.
