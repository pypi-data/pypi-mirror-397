# System Architecture

This document provides visual architectural diagrams of the DWH Business Logic POC system.

---

## High-Level Overview

```mermaid
flowchart TB
    subgraph Execution["Job Execution"]
        Spark["Spark Jobs<br/>(Glue/EMR/Databricks)"]
    end

    subgraph SNS["SNS Topics"]
        JobEvents["job_events"]
        JobApprovals["job_approvals"]
    end

    subgraph Lambdas["Lambda Functions"]
        Indexer["job_events_indexer"]
        Alerts["quality_alerts"]
        Orchestrator["downstream_orchestrator"]
        Approval["approval_processor"]
    end

    subgraph Storage["Data Stores"]
        OpenSearch["OpenSearch Cluster"]
        S3Config["S3: workflow_config.json"]
    end

    subgraph MWAA["MWAA (Airflow)"]
        SQS["SQS Queue<br/>mwaa-triggers"]
        Dispatcher["event_dispatcher DAG"]
        TargetDAG["Target DAGs"]
    end

    subgraph Dashboards["Visualization"]
        OSD["OpenSearch Dashboards"]
    end

    Spark -->|publish event| JobEvents
    JobEvents --> Indexer
    JobEvents --> Alerts
    JobEvents --> Orchestrator
    JobApprovals --> Approval
    JobApprovals --> Orchestrator

    Indexer --> OpenSearch
    Approval --> OpenSearch
    Orchestrator --> S3Config
    Orchestrator --> SQS

    SQS --> Dispatcher
    Dispatcher --> TargetDAG

    OpenSearch --> OSD
```

---

## Job Execution & Metrics Collection

```mermaid
flowchart TB
    subgraph JobExecution["Spark Job Execution"]
        Entry["Entry Point<br/>(generic_entry.py)"]
        Factory["Job Factory<br/>(creates job + dependencies)"]
        Job["AbstractJob.run()"]

        subgraph Phases["ETL Phases"]
            Extract["EXTRACT Phase"]
            Transform["TRANSFORM Phase"]
            Load["LOAD Phase"]
        end

        Metrics["JobMetrics<br/>(collects throughout job)"]
    end

    Publisher["JobEventPublisher"]
    SNS["SNS: job_events"]

    Entry --> Factory
    Factory --> Job
    Job --> Extract
    Extract --> Transform
    Transform --> Load

    Extract -.->|record metrics| Metrics
    Transform -.->|record metrics| Metrics
    Load -.->|record metrics| Metrics

    Metrics --> Publisher
    Publisher -->|publish| SNS
```

---

## Event Processing Pipeline

```mermaid
flowchart TB
    JobComplete["Job Completes"]

    subgraph SNSTopic["SNS: job_events"]
        SNS["Fan-out to subscribers"]
    end

    subgraph Consumers["Lambda Consumers"]
        Indexer["job_events_indexer<br/>Index to OpenSearch"]
        Alerts["quality_alerts<br/>Send notifications"]
        Orchestrator["downstream_orchestrator<br/>Trigger next jobs"]
    end

    subgraph Destinations["Destinations"]
        OS["OpenSearch<br/>job-events<br/>job-events-transform-images"]
        Email["Email/PagerDuty<br/>Alerts"]
        SQS["SQS Queue<br/>MWAA Triggers"]
    end

    MWAA["MWAA DAGs"]

    JobComplete --> SNS
    SNS --> Indexer
    SNS --> Alerts
    SNS --> Orchestrator

    Indexer --> OS
    Alerts --> Email
    Orchestrator --> SQS
    SQS --> MWAA
```

---

## Downstream Job Orchestration (Detail)

```mermaid
flowchart TB
    subgraph Source["Source Job"]
        Job["transform_images<br/>completes with SUCCESS"]
    end

    SNS["SNS: job_events<br/>(filtered: status=SUCCESS)"]

    subgraph Lambda["Lambda: downstream_orchestrator"]
        Load["1. Load workflow config from S3"]
        Lookup["2. Look up job_name in config"]
        GetTriggers["3. Get on_success triggers"]
        Execute["4. Execute trigger_sqs_mwaa()"]
    end

    subgraph Config["S3: workflow_config.json"]
        ConfigContent["workflows:<br/>  transform_images:<br/>    on_success:<br/>      - type: sqs_mwaa<br/>        dag_id: filter_image_...<br/>        parameter_mapping:<br/>          start_date: metrics.start_date"]
    end

    subgraph SQSQueue["SQS: mwaa-triggers"]
        Message["Message:<br/>{<br/>  dag_id: filter_image_...<br/>  conf: {<br/>    start_date: 2025-01-01<br/>    triggered_by_job: transform_images<br/>  }<br/>}"]
    end

    subgraph Airflow["MWAA"]
        Dispatcher["event_dispatcher DAG<br/>1. SqsSensor polls queue<br/>2. Parse message<br/>3. trigger_dag()"]
        Target["filter_image_glue_pyspark<br/>Receives: start_date, end_date,<br/>created_by, triggered_by_*"]
    end

    Job --> SNS
    SNS --> Load
    Load --> Lookup
    Config -.-> Lookup
    Lookup --> GetTriggers
    GetTriggers --> Execute
    Execute --> Message
    Message --> Dispatcher
    Dispatcher -->|triggers| Target
```

---

## Approval Workflow

```mermaid
flowchart TB
    subgraph JobResult["Job Completion"]
        Pending["Job Status:<br/>PENDING_APPROVAL<br/>(quality issues detected)"]
    end

    subgraph Review["Human Review"]
        Dashboard["OpenSearch Dashboard<br/>Operator reviews metrics"]
        Decision["Approval Decision<br/>(APPROVED/REJECTED)"]
    end

    subgraph ApprovalSystem["Approval System"]
        API["API/UI/CLI<br/>Submit decision"]
    end

    SNS["SNS: job_approvals"]

    subgraph Processing["Lambda Processing"]
        Processor["approval_processor<br/>Update OpenSearch doc"]
        Orchestrator["downstream_orchestrator<br/>Trigger if APPROVED"]
    end

    subgraph Results["Results"]
        Updated["OpenSearch Updated:<br/>- approval_status<br/>- approved_by<br/>- approval_reason"]
        Downstream["Downstream Jobs<br/>(if on_approval defined)"]
    end

    Pending --> Dashboard
    Dashboard --> Decision
    Decision --> API
    API --> SNS
    SNS --> Processor
    SNS --> Orchestrator
    Processor --> Updated
    Orchestrator --> Downstream
```

---

## Quality Alerting

```mermaid
flowchart TB
    Job["Job Completes"]
    SNS["SNS: job_events"]

    subgraph Lambda["Lambda: quality_alerts"]
        Check["Check quality.status<br/>and failure_type"]
    end

    subgraph Outcomes["Alert Routing"]
        Green["status = GREEN<br/>No alert"]
        Yellow["status = YELLOW<br/>Warning alert"]
        Red["status = RED<br/>Critical alert"]
    end

    subgraph Notifications["Notifications"]
        WarnTopic["SNS: quality_alerts_warning"]
        CritTopic["SNS: quality_alerts_critical"]
        Email["Email"]
        PagerDuty["PagerDuty/Slack"]
    end

    Job --> SNS
    SNS --> Check
    Check --> Green
    Check --> Yellow
    Check --> Red
    Yellow --> WarnTopic
    Red --> CritTopic
    WarnTopic --> Email
    CritTopic --> PagerDuty
```

---

## OpenSearch Index Structure

```mermaid
flowchart LR
    subgraph Common["job-events (common)"]
        C1["id, timestamp"]
        C2["job_name, job_run_id"]
        C3["status, failure_type"]
        C4["quality.status, quality.checks[]"]
        C5["metrics.duration_seconds"]
        C6["metrics.records_*"]
        C7["metrics.phases.*"]
        C8["metrics.drop_reasons[]"]
        C9["error.*, approval_*"]
        CNo["NO metrics.payload"]
    end

    subgraph JobSpecific["job-events-transform-images"]
        J1["id, timestamp"]
        J2["job_name, job_run_id"]
        J3["status, failure_type"]
        J4["quality.status, quality.checks[]"]
        J5["metrics.duration_seconds"]
        J6["metrics.records_*"]
        J7["metrics.phases.*"]
        J8["metrics.drop_reasons[]"]
        J9["error.*, approval_*"]
        JYes["+ metrics.payload:"]
        JP1["  transform.data_types[]"]
        JP2["  load.output_summary[]"]
        JP3["  load.bytes_by_category[]"]
    end

    subgraph Approvals["job-approvals"]
        A1["id, timestamp"]
        A2["job_name, job_run_id"]
        A3["decision"]
        A4["decided_by"]
        A5["reason"]
    end
```

---

## Terraform Structure

```mermaid
flowchart TB
    subgraph Infra["dwh-business-logic-poc-infra/infra/"]
        I1["OpenSearch domain"]
        I2["S3 buckets (code, data)"]
        I3["MWAA environment"]
        I4["VPC/networking"]
        I5["IAM roles (MWAA, Glue base)"]
        I6["SQS queue (mwaa-triggers)"]
    end

    subgraph Outputs["Remote State Outputs"]
        O1["opensearch_endpoint"]
        O2["code_bucket_id"]
        O3["mwaa_triggers_queue_url"]
        O4["mwaa_triggers_queue_arn"]
    end

    subgraph Pipeline["dwh-business-logic-poc-pipeline/terraform/"]
        subgraph SNSTopics["SNS Topics"]
            S1["job_events"]
            S2["job_approvals"]
            S3["quality_alerts_*"]
        end
        subgraph LambdaFunctions["Lambda Functions"]
            L1["job_events_indexer"]
            L2["approval_processor"]
            L3["quality_alerts"]
            L4["downstream_orchestrator"]
        end
        P1["Lambda Layer (dependencies)"]
        P2["SNS Subscriptions"]
        P3["IAM (Lambda roles, policies)"]
    end

    Infra --> Outputs
    Outputs -->|terraform_remote_state| Pipeline
```

---

## Complete Data Flow (End-to-End)

```mermaid
sequenceDiagram
    participant Spark as Spark Job
    participant Metrics as JobMetrics
    participant Publisher as JobEventPublisher
    participant SNS as SNS: job_events
    participant Indexer as Lambda: indexer
    participant Alerts as Lambda: alerts
    participant Orch as Lambda: orchestrator
    participant OS as OpenSearch
    participant SQS as SQS Queue
    participant Dispatcher as MWAA: dispatcher
    participant Target as Target DAG

    Note over Spark,Metrics: 1. Job Execution
    Spark->>Metrics: Collect metrics (records, durations, drops)

    Note over Metrics,Publisher: 2. Quality Evaluation
    Metrics->>Publisher: Evaluate quality thresholds

    Note over Publisher,SNS: 3. Event Publishing
    Publisher->>SNS: Publish job event

    Note over SNS,OS: 4. Parallel Processing
    par Index to OpenSearch
        SNS->>Indexer: Trigger
        Indexer->>OS: Index event
    and Send Alerts
        SNS->>Alerts: Trigger
        Alerts-->>Alerts: Send if YELLOW/RED
    and Orchestrate Downstream
        SNS->>Orch: Trigger
        Orch->>SQS: Send message (if SUCCESS)
    end

    Note over SQS,Target: 5. MWAA Triggering
    SQS->>Dispatcher: Poll message
    Dispatcher->>Target: trigger_dag(dag_id, conf)

    Note over Target: 6. Downstream Execution
    Target->>Target: Execute with parameters from parent
```

---

## Key Design Decisions

### 1. SNS Fan-Out Pattern
Multiple lambdas subscribe to the same SNS topic, enabling:
- Independent scaling of each concern
- Easy addition of new consumers
- Failure isolation

### 2. SQS for MWAA Integration
MWAA with private networking cannot receive direct API calls. SQS provides:
- Reliable message delivery
- Built-in retry via visibility timeout
- Dead letter queue for failed messages

### 3. Configuration-Driven Orchestration
Workflow config in S3 enables:
- No code changes for new job orchestrations
- Parameter mapping flexibility
- Easy testing and validation

### 4. Consistent OpenSearch Structure
Both indices use identical field paths:
- Scripted fields work across all indices
- One schema to learn
- Reusable visualizations

### 5. Array Format for Dynamic Keys
Converting dicts to arrays enables OpenSearch aggregation:

```json
// Before (can't aggregate)
{"parserA": 100, "parserB": 200}

// After (can aggregate on "name" field)
[{"name": "parserA", "records": 100}, {"name": "parserB", "records": 200}]
```

---

## Related Documentation

- [DASHBOARDS.md](src/dwh/jobs/transform_images/opensearch/DASHBOARDS.md) - OpenSearch visualization setup
- [DEVELOPMENT_PHILOSOPHY.md](DEVELOPMENT_PHILOSOPHY.md) - Core development principles
- [JOB_EXECUTION_ARCHITECTURE.md](JOB_EXECUTION_ARCHITECTURE.md) - Job execution patterns
