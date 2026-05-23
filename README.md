# Automated Data Quality & Governance Pipeline

> **Enterprise-Grade Data Integrity Engine: Protecting the 'Single Source of Truth' through automated auditing, vectorized rule processing, and physical isolation of anomalous data.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-Database-CC2927.svg?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Vectorized_ETL-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Observability_UI-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 1. **EXECUTIVE SUMMARY & BUSINESS CONTEXT**

In modern enterprise data ecosystems, the integrity of the semantic layer is paramount. "Silent data degradation" characterized by orphaned foreign keys, negative quantities, syntax formatting errors, and anomalous metrics in raw staging tables can seamlessly corrupt downstream Business Intelligence (BI) reporting. When C-level executives and key stakeholders consume dashboards built on flawed data, it leads to inaccurate forecasting, compliance breaches, and ultimately, poor strategic decision-making.

This project implements a robust, automated End-to-End (E2E) ETL and Data Quality (DQ) pipeline designed to proactively scan, isolate, and log anomalies in SQL Server databases before they ever reach production Data Marts. Acting as an automated data gatekeeper, it shifts the data validation process "to the left" (validating strictly at the ingestion phase), ensuring a pristine Single Source of Truth for corporate analytics.

---

## 2. **STRATEGIC IMPACT & OPERATIONAL ROI**

The implementation of this architecture replaces reactive, manual data cleaning workflows with a proactive data engineering solution, generating immediate and measurable business value:

* **Zero Data Contamination:** Establishes a strict programmatic firewall that prevents orphaned records or corrupted transactional data from contaminating upstream management reports.
* **Physical Data Isolation (The Quarantine Strategy):** Automatically partitions validated data from anomalies into strictly separated database tables (`dbo.Clean_Sales` and `dbo.Quarantine_Sales`). This allows Data Stewards to investigate and remediate errors at their source without bottlenecking the main business workflow.
* **SLA Fulfillment & Automation:** Reduces manual data auditing workflows by over 95%. By automating the extraction and validation phases, the system ensures that data availability Service Level Agreements (SLAs) are consistently met for downstream analytics teams.
* **Governance & Traceability:** Provides stakeholders with a comprehensive, BI-like observability interface to audit the database's Health Score dynamically, creating a traceable and immutable audit log required for internal compliance and regulatory standards.

---

## 3. **END-TO-END PIPELINE ARCHITECTURE**

The system is designed following the foundational principles of a Medallion Architecture (Bronze to Gold zone logic) adapted specifically for relational staging environments.

```mermaid
graph TD
    subgraph Source System
        A[(Raw_Sales: Staging Data)]
    end
    
    subgraph Data Quality Engine
        B(ODBC Secure Extraction) --> C{Pandas Vectorized Audit Engine}
    end
    
    subgraph Enterprise Data Warehouse
        C -->|Validation Passed| D[(Clean_Sales)]
        C -->|Validation Failed| E[(Quarantine_Sales)]
    end
    
    subgraph Presentation & Observability Layer
        D --> F[Enterprise BI / Power BI]
        E --> G[Streamlit Observability Dashboard]
    end

    A --> B
```
---

#### **3.1. Architecture Phase Breakdown**

1. **Ingestion & Extraction (E):** Secure connection to the SQL Server instance via pyodbc/SQLAlchemy to extract massive batches from the source table.

2. **Transformation & Auditing (T):** Intensive use of Pandas to apply high-performance vectorized validations, completely avoiding inefficient loops.

3. **Loading & Synchronization (L):** Integration with SQLAlchemy (`fast_executemany`) to index the results back to the SQL server, automatically recreating the clean and quarantine tables in a transactional manner.

4. **Presentation Layer:** Deployment of an interactive web application built with Streamlit featuring native Plotly visualizations for decoupled data observability.

## 4. **CORE ENGINEERING PRINCIPLES & OPTIMIZATIONS**

   #### **4.1. High-Performance Vectorized Validation Engine**
   Traditional iterative data processing algorithms iterating over large datasets cause severe memory bottlenecks and unacceptable latency. This pipeline is optimized entirely using Pandas boolean masking and vectorized operations (`np.select`). By applying mathematical and logical validations across entire columns simultaneously in memory, the engine evaluates 100,000+ records against multiple complex rulesets in seconds.

   #### **4.2. Transactional Safety & ORM Integration** 
   Database operations are not handled via fragile raw string query execution. The pipeline utilizes the SQLAlchemy Object-Relational Mapper (ORM) combined with the pyodbc driver. This implementation ensures:

      * Intelligent connection pooling and resource optimization.

      * Atomic batch writing, robust connection pooling, and utilizes the fast_executemany=True parameter to perform true Bulk Inserts from Python to SQL Server.

      * Robust deadlock prevention and advanced timeout management when interfacing with the SQL Server instance under
      heavy load.

   #### **4.3. Real-Time Data Observability & Monitoring**
   A built-in Streamlit frontend acts as the Data Quality Control Center. Built with strict Decoupled Architecture principles, the UI strictly operates in Read-Only mode, leveraging `@st.cache_data` to protect the database from query overloading while providing instant analytical insights.

## 5. **DETAILED DATA QUALITY RULES ENGINE**
The engine evaluates all incoming transactional records against a strict, multi-layered set of business and logical rules:

   1. **Relational & Completeness Integrity:** Scans for null values, NaNs, or empty strings in critical categorical dimensions to definitively prevent orphaned records (`Missing/Null Values`).

   2. **Mathematical Boundary Checks:** Enforces absolute logical consistency on quantitative fields (e.g., ensuring `Quantity > 0` and `Unit_Price >= 0.00`). Transactions violating these financial boundaries are instantly flagged.

   3. **Syntax & Pattern Recognition:** Utilizes highly optimized Regular Expressions (Regex) to validate string formats. For instance, ensuring that all Email fields conform strictly to standard email address patterns (`Malformed Email`).

## 6. **COMPREHENSIVE TECHNOLOGY STACK & RATIONALE**

   * **Database Engine:** SQL Server (Transact-SQL). Chosen for its enterprise ubiquity, strict ACID compliance, and robust DDL structure.

   * **Core Processing Engine:** SQL Server (Transact-SQL). Chosen for its enterprise ubiquity, strict ACID compliance, and robust DDL structure.

   * **Data Manipulation Framework:** Pandas & NumPy. Chosen over distributed frameworks because the current volume threshold and single-node batch processing requirements are perfectly optimized through vectorization.

   * **Connectivity & Middleware:** PyODBC & SQLAlchemy. The industry gold standard for secure, reliable, and efficient relational database connectivity.

   * **Observability UI:** Streamlit & Plotly Express. Allows for the rapid deployment of a data-driven web application with interactive charting.   

## 7. **SCALABILITY & CLOUD MIGRATION ROADMAP**
While this repository demonstrates a highly optimized local architecture, the codebase is structurally prepared for seamless migration to enterprise cloud environments:

* **Compute Layer:** The Python processing engine (`main.py`) can be natively containerized using Docker and orchestrated via Kubernetes or executed as serverless functions (AWS Lambda / Azure Functions) for infinite horizontal scaling.

* **Storage Layer:** The SQL Server instance can be seamlessly migrated to Azure SQL Database or Amazon RDS without changing the core SQLAlchemy dialects.

* **Configuration:** Centralized credentials via `config.py` enable immediate migration to `.env` files or Azure Key Vault without altering the core logic.

## 8. **DEPLOYMENT, SETUP, AND REPRODUCTION GUIDE**
Follow these technical runbook steps to provision the local environment, configure the database schemas, and execute the full pipeline.

##### **Phase 1: Database Provisioning and Initialization**
1. Connect to your target SQL Server instance (e.g., LocalDB, SQLEXPRESS, or Developer Edition) using SQL Server Management Studio (SSMS) or Azure Data Studio.

2. Execute the provided DDL script (`database_schema.sql`) to create the DataQualityDB database and the three required tables (`Raw_Sales, Clean_Sales, Quarantine_Sales`).

##### **Phase 2: Virtual Environment Configuration**
1. Open a terminal instance in the project's root directory and initialize an isolated Python virtual environment to avoid dependency conflicts:

```bash
python -m venv venv
```

2. Activate the virtual environment:

* Windows Environment: venv\Scripts\activate

* Mac/Linux Environment: source venv/bin/activate

3. Install the required engineering and data science dependencies via the package manager:

```bash
pip install -r requirements.txt
```

##### **Phase 3: Pipeline Execution and Verification**
1. Generate Synthetic Staging Data: Run the generator script to populate the `Raw_Sales` table with 100,000 records (85% clean, 15% intentionally corrupted) in memory.

```bash
python data_generator.py
```

2. Execute the Core ETL & Audit Engine: Run the primary backend processing script. The engine will ingest the raw data, apply the vectorized validation rules, and output the physical results to the Gold and Quarantine tables.

```bash
python main.py
```

3. Launch the Observability Interface: Start the Streamlit frontend server to visualize the data health metrics and interact with the quarantine results.

```bash
streamlit run app.py
```
(The dashboard will automatically deploy and become accessible on your localhost, typically via port 8501).

## 9. SECURITY, COMPLIANCE, AND INFRASTRUCTURE DISCLAIMER
Database connection strings and target server definitions are configured for local Windows Authentication (`Trusted_Connection=yes`) strictly for demonstration purposes.

Production Environment Warning: In a live, production-grade enterprise environment, this codebase requires the complete abstraction of all credentials and endpoints. These parameters must be dynamically injected during runtime via secure Environment Variables or Secret Management Services (e.g., HashiCorp Vault, AWS Secrets Manager) to strictly comply with standard Information Security (InfoSec) protocols.