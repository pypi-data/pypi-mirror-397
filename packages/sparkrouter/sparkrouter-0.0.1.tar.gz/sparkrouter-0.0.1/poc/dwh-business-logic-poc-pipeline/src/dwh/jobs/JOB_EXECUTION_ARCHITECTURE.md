# Job Execution Architecture

## Overview

This document describes how job submission and execution works in the DWH Business Logic framework. The system provides standardized patterns for job creation, configuration, and execution across different compute environments including Databricks, AWS Glue, EMR, and containerized Spark clusters.

---

## 🚀 **Job Execution Flow**

### **Complete Execution Pipeline**
```
Job Submission → Compute Environment → Generic Entry → Job Factory → Job → Business Logic
```

### **Step-by-Step Breakdown**

1. **Job Submission** (via scheduler, API, or manual trigger)
2. **Compute Environment** (Databricks, AWS Glue, EMR, etc.)
3. **Generic Entry Point Processes Arguments**
4. **Job Factory Creates Job Instance**
5. **Abstract Job Executes Business Logic**
6. **Success/Failure Notifications Sent**

---

## 🏗️ **Component Architecture**

### **1. Job Submission Layer (Airflow/MWAA)**
```python
# Primary job submission via Airflow/MWAA DAGs
# Airflow operators for different platforms:

# Databricks operator
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

# AWS Glue operator  
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

# EMR operator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator

# Example DAG task
task = DatabricksSubmitRunOperator(
    task_id="load_promos_job",
    python_wheel_task={
        "entry_point": "generic_entry",
        "parameters": [
            "--module_name", "dwh.jobs.load_promos.load_promos_job_factory",
            "--load_promos_job", json.dumps({...configuration...}),
            "--start_date", "{{ ds }}",
            "--end_date", "{{ next_ds }}",
            "--created_by", "airflow"
        ]
    }
)
```

**Purpose**: Orchestrated job submission via Airflow/MWAA
**Key Features**:
- **Airflow/MWAA** as primary orchestration platform
- **Scheduled execution** with cron expressions
- **Dependency management** between jobs
- **Retry logic** and error handling
- **Parameter templating** with Airflow macros
- **Multi-platform support** through different operators

### **2. Compute Environment**
```
Supported Platforms:
- Databricks (Notebooks, Jobs, Workflows)
- AWS Glue (PySpark Jobs)
- EMR (Spark Steps)
- Containerized Spark (Docker, Kubernetes)
- Local Spark (Development)
```

**Purpose**: Execution environment abstraction
**Key Features**:
- Platform-independent job execution
- Environment-specific configuration
- Resource management
- Dependency resolution

### **3. Generic Entry Point**
```python
# From generic_entry.py
def main(argv=None):
    # Parse command line arguments
    args = parse_args(argv)  # --module_name, --load_promos_job, etc.
    
    # Validate required arguments
    validate_required_args(args)  # Ensures module_name exists
    
    # Prepare module execution
    module_name, module_args = prepare_module_args(args)
    # Adds service_provider (DATABRICKS, GLUE, EMR, etc.) and has_spark=True
    
    # Execute the target module
    job_module = importlib.import_module(module_name)
    job_module.main(**module_args)  # Calls load_promos_job_factory.main()
```

**Purpose**: Universal entry point for all job types across platforms
**Key Features**:
- Dynamic module loading
- Argument parsing and validation
- Environment detection (Spark availability)
- Platform identification (Databricks, Glue, EMR, etc.)

### **4. Job Factory Layer**
```python
# From abstract_job_factory.py
def run(self, **kwargs):
    # Create the job instance
    job = self.create_job(**kwargs)  # LoadPromosJobFactory.create_job()
    
    # Filter kwargs to match job's execute_job signature
    sig = inspect.signature(job.execute_job)
    valid_params = {k: v for k, v in kwargs.items() if k in sig.parameters}
    
    # Execute the job
    return job.run(**valid_params)
```

**Purpose**: Factory pattern for job creation and configuration
**Key Features**:
- Configuration parsing (JSON to dict)
- Dependency injection
- Parameter filtering for job execution
- Standardized job creation interface

### **5. Job Execution Layer**
```python
# From abstract_job.py
@final
def run(self, **kwargs):
    try:
        # Execute business logic
        results = self.execute_job(**kwargs)  # LoadPromosJob.execute_job()
        
        # Handle success
        self.on_success(results)
    except Exception as e:
        # Handle failure
        self.on_failure(error_message)
        raise RuntimeError(error_message) from e
```

**Purpose**: Template method pattern for standardized job execution
**Key Features**:
- Standardized execution flow
- Comprehensive error handling
- Success/failure notification hooks
- Final method prevents override of execution logic

---

## 🔧 **Design Patterns**

### **1. Factory Pattern**
- **AbstractJobFactory** provides common job creation logic
- **Concrete factories** handle job-specific configuration
- **Dependency injection** through factory configuration
- **Configuration validation** at factory level

### **2. Template Method Pattern**
- **AbstractJob.run()** is final - defines execution template
- **Concrete jobs** implement `execute_job()`, `on_success()`, `on_failure()`
- **Error handling** standardized across all jobs
- **Notification patterns** consistent

### **3. Strategy Pattern**
- **Configuration-driven** strategy selection
- **Data source strategies** (Parquet, Delta, JDBC)
- **Data sink strategies** (Delta, Parquet, Postgres, Redshift)
- **Notification strategies** (Email, Slack, SNS, Noop)

---

## 📊 **Configuration Architecture**

### **Configuration Structure**
```python
{
    # Notification configurations
    "job_failed_notifications": {"notification_service": "NOOP"},
    "job_success_notifications": {"notification_service": "NOOP"},
    "data_quality_notifications": {"notification_service": "NOOP"},
    
    # Data pipeline configurations
    "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://..."},
    "unity_loader_config": {"strategy": "DELTA", "path": "s3a://..."},
    "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://..."},
    "redshift_loader_config": {
        "strategy": "POSTGRES",
        "jdbc_url": "jdbc:postgresql://postgres:5432/postgres_db",
        "properties": {"user": "...", "password": "...", "driver": "..."}
    }
}
```

### **Configuration Principles**
- **JSON-based** configuration for flexibility
- **Strategy pattern** enables different implementations
- **Environment-specific** configurations
- **Validation** at factory level

---

## 🔄 **Data Flow Example (Load Promos Job)**

```
1. Airflow/MWAA Scheduler
   ↓ (DAG triggers job based on schedule/dependencies)
   
2. Airflow Operator (Databricks/Glue/EMR)
   ↓ (Submits job to compute platform with parameters)
   
3. Compute Environment (Databricks/Glue/EMR/etc.)
   ↓ (generic_entry.py processes arguments)
   
4. Load Promos Job Factory
   ↓ (create_job with parsed configuration)
   
5. Load Promos Job
   ↓ (execute_job with business logic)
   
6. Business Logic Pipeline:
   - Extract from S3 Parquet (PromotionExtractor)
   - Transform promotion data (PromotionTransformer)
   - Load to Unity Catalog Delta (UnityLoader)
   - Load to S3 Staging Parquet (StageLoader)
   - Load to Database Postgres/Redshift (DatabaseLoadStrategy)
   ↓
   
7. Success/Failure Notifications
   - Job completion status reported to Airflow
   - Data quality validation results
   - Error details if failures occur
   - Airflow handles retry logic and downstream dependencies
```

---

## 🎯 **Key Architectural Benefits**

### **1. Standardization**
- **Consistent execution pattern** across all job types
- **Standardized error handling** and notifications
- **Common configuration approach** for all jobs
- **Platform-agnostic** job development

### **2. Flexibility**
- **Strategy pattern** allows different implementations
- **Configuration-driven** behavior changes
- **Environment-specific** configurations
- **Pluggable components** through dependency injection

### **3. Testability**
- **Environment isolation** for comprehensive testing
- **Real infrastructure** testing (Spark, databases, storage)
- **Comprehensive validation** of end-to-end workflows
- **Production-equivalent** test environments

### **4. Reliability**
- **Fail-fast** error handling
- **Comprehensive logging** and monitoring
- **Notification integration** for operational awareness
- **Schema validation** prevents data quality issues

---

## 🔍 **Platform-Specific Execution**

### **Databricks Environment**
- **Databricks Runtime** with pre-configured Spark
- **Unity Catalog** integration for data governance
- **Databricks File System (DBFS)** for storage
- **Cluster management** with auto-scaling
- **Service provider** set to `DATABRICKS`

### **AWS Glue Environment**
- **Glue Spark runtime** with managed infrastructure
- **AWS Glue Data Catalog** for metadata management
- **S3 integration** for data storage
- **Serverless execution** with automatic scaling
- **Service provider** set to `GLUE`

### **EMR Environment**
- **EMR Spark cluster** with configurable instances
- **HDFS/S3** for distributed storage
- **YARN** for resource management
- **Custom bootstrap actions** for environment setup
- **Service provider** set to `EMR`

### **Runtime Configuration**
- **PYTHONPATH** configured for job modules
- **Spark configuration** for storage and cluster access
- **Service provider** identification for platform-specific behavior
- **has_spark** flag enabled for Spark-dependent jobs

---

## 📋 **Job Development Guidelines**

### **Creating New Jobs**
1. **Extend AbstractJob** with business logic implementation
2. **Create JobFactory** extending AbstractJobFactory
3. **Implement configuration parsing** in factory
4. **Add comprehensive tests** for multiple platforms
5. **Document configuration schema** and dependencies

### **Configuration Best Practices**
- **Use strategy pattern** for pluggable components
- **Validate configuration** at factory level
- **Provide clear error messages** for invalid configurations
- **Support platform-specific** configurations

### **Platform Compatibility**
- **Test on target platforms** (Databricks, Glue, EMR)
- **Handle platform-specific** resource constraints
- **Use platform-native** storage and compute features
- **Implement graceful degradation** for missing features

---

## 🚀 **Airflow/MWAA Deployment Examples**

### **Databricks via Airflow**
```python
# Airflow DAG with Databricks operator
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'load_promos_databricks',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
)

load_promos_task = DatabricksSubmitRunOperator(
    task_id='load_promos_job',
    databricks_conn_id='databricks_default',
    new_cluster={
        'spark_version': '13.3.x-scala2.12',
        'node_type_id': 'i3.xlarge',
        'num_workers': 2
    },
    python_wheel_task={
        'package_name': 'dwh_business_logic',
        'entry_point': 'generic_entry',
        'parameters': [
            '--module_name', 'dwh.jobs.load_promos.load_promos_job_factory',
            '--load_promos_job', '{...configuration...}',
            '--start_date', '{{ ds }}',
            '--end_date', '{{ next_ds }}',
            '--created_by', 'airflow'
        ]
    },
    dag=dag
)
```

### **AWS Glue via Airflow**
```python
# Airflow DAG with Glue operator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

load_promos_glue = GlueJobOperator(
    task_id='load_promos_glue_job',
    job_name='load_promos_job',
    script_location='s3://bucket/scripts/generic_entry.py',
    s3_bucket='my-glue-bucket',
    iam_role_name='GlueServiceRole',
    create_job_kwargs={
        'GlueVersion': '4.0',
        'NumberOfWorkers': 2,
        'WorkerType': 'G.1X'
    },
    script_args={
        '--module_name': 'dwh.jobs.load_promos.load_promos_job_factory',
        '--load_promos_job': '{...configuration...}',
        '--start_date': '{{ ds }}',
        '--end_date': '{{ next_ds }}',
        '--created_by': 'airflow'
    },
    dag=dag
)
```

### **EMR via Airflow**
```python
# Airflow DAG with EMR operator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator

SPARK_STEPS = [
    {
        'Name': 'load_promos_job',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--py-files', 's3://bucket/packages/dwh_business_logic.zip',
                's3://bucket/scripts/generic_entry.py',
                '--module_name', 'dwh.jobs.load_promos.load_promos_job_factory',
                '--load_promos_job', '{...configuration...}',
                '--start_date', '{{ ds }}',
                '--end_date', '{{ next_ds }}',
                '--created_by', 'airflow'
            ]
        }
    }
]

load_promos_emr = EmrAddStepsOperator(
    task_id='load_promos_emr_step',
    job_flow_id='{{ ti.xcom_pull(task_ids="create_emr_cluster", key="return_value") }}',
    steps=SPARK_STEPS,
    dag=dag
)
```**
- **Use strategy pattern** for pluggable components
- **Validate configuration** at factory level
- **Provide clear error messages** for invalid configurations
- **Support environment-specific** configurations

### **Testing Requirements**
- **Integration tests** must use Docker containers
- **Real infrastructure** components (databases, storage)
- **End-to-end validation** of business logic
- **Comprehensive error scenario** testing

---

## 📋 **Production Considerations**

### **Platform Selection**
- **Databricks**: Best for collaborative development and Unity Catalog integration
- **AWS Glue**: Ideal for serverless, event-driven ETL workloads
- **EMR**: Optimal for cost-sensitive, long-running batch processing
- **Containerized**: Suitable for on-premises or multi-cloud deployments

### **Airflow/MWAA Configuration Management**
- **Airflow Variables** for environment-specific configurations
- **Airflow Connections** for platform credentials (Databricks, AWS)
- **AWS Systems Manager Parameter Store** integration
- **Environment-specific DAGs** (dev, staging, prod)
- **Secret management** via Airflow's built-in secret backends
- **Configuration templating** with Jinja2 macros

### **Monitoring & Observability**
- **Airflow UI** for job monitoring and troubleshooting
- **MWAA CloudWatch** integration for metrics and logs
- **Platform-native monitoring** (Databricks metrics, Glue CloudWatch)
- **Custom metrics** for business logic validation
- **Airflow alerting** via email, Slack, PagerDuty
- **DAG-level SLAs** and monitoring
- **Log aggregation** across Airflow and compute platforms

### **Scaling Considerations**
- **Auto-scaling** based on data volume and complexity
- **Resource optimization** for cost efficiency
- **Parallel execution** for independent job components
- **Performance monitoring** and tuning

---

## 📚 **Conclusion**

The job execution architecture provides a robust, platform-agnostic framework for running data processing jobs across multiple compute environments. Key strengths include:

- **Platform independence** - runs on Databricks, AWS Glue, EMR, and containerized environments
- **Standardized patterns** for job creation and execution
- **Flexible configuration** supporting multiple platforms and environments
- **Reliable error handling** with notification integration
- **Production-ready** deployment capabilities across cloud platforms

This architecture enables teams to focus on business logic implementation while Airflow/MWAA provides orchestration, scheduling, and monitoring capabilities across different compute platforms. The separation of concerns allows for flexible platform selection while maintaining consistent operational patterns.

---

**Last Updated**: 2025-01-08  
**Next Review**: When new job types or execution patterns are added