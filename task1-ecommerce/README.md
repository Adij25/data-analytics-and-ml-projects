# Task 1 – E-commerce Sales Analysis

## 1. Project Overview

This project focuses on analyzing e-commerce sales data to identify sales trends, understand customer purchasing behavior, evaluate order and delivery performance, and generate meaningful business insights.

The project follows an end-to-end data analytics workflow using Python, MySQL, Jupyter Notebook, and Microsoft Power BI.

The main objectives are:

- Clean and preprocess raw e-commerce datasets.
- Perform Exploratory Data Analysis (EDA).
- Analyze business performance using SQL queries.
- Identify sales patterns and customer behavior.
- Build interactive visualizations using Power BI.
- Generate a summary of business insights and recommendations.

## 2. Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Data Cleaning | Pandas, NumPy |
| Exploratory Data Analysis | Jupyter Notebook |
| Data Visualization | Matplotlib |
| Database | MySQL |
| SQL Analysis | MySQL, Window Functions |
| Business Intelligence | Microsoft Power BI |
| Reporting | PDF |

## 3. Project Structure

```text
Task-1-Ecommerce-Sales/
│
├── data/
│   ├── raw/                         # Four original CSV datasets
│   │   └── task1_*.csv
│   │
│   └── clean/                       # Cleaned datasets
│
├── src/
│   ├── clean.py                     # Data cleaning and preprocessing
│   └── make_insights_pdf.py         # Generates business insights PDF
│
├── notebooks/
│   └── cleaning_eda.ipynb           # EDA, charts, cleaning log and insights
│
├── sql/
│   ├── 00_load_mysql.sql            # MySQL schema and data loading
│   └── task1_queries.sql            # Seven SQL business queries
│
├── charts/                          # Generated visualization images
│
├── POWERBI_GUIDE.md                 # Power BI implementation guide
├── insights.pdf                     # One-page business insights summary
└── README.md
```

## 4. Data Cleaning and Preprocessing

Data cleaning is performed using Python and Pandas in:

```text
src/clean.py
```

The preprocessing workflow includes handling duplicate records, missing values, date formatting, data standardization, and calculated fields.

### Key Cleaning Decisions

- Removed 120 duplicate order records.
- Filled 60 missing state values using the corresponding customer's city information.
- Standardized state names into uppercase.
- Parsed dates using the explicit `%d-%m-%Y` format.
- Filled 40 missing `discount_pct` values with 0 and flagged the imputed records using `discount_imputed`.
- Preserved missing `delivery_date` values for Cancelled and Shipped orders.
- Calculated revenue and delivery days using Delivered orders only.

The cleaned CSV files are generated in:

```text
data/clean/
```

These cleaned datasets are used for SQL analysis and Power BI reporting.

## 5. Exploratory Data Analysis (EDA)

EDA is performed using Jupyter Notebook:

```text
notebooks/cleaning_eda.ipynb
```

The notebook covers:

- Dataset exploration and data quality checks.
- Data cleaning and preprocessing logs.
- Seven data visualizations.
- Outlier identification and handling.
- Sales and customer behavior analysis.
- Important observations and business insights.

The generated charts are saved in:

```text
charts/
```

## 6. MySQL Database and SQL Analysis

MySQL is used to store and analyze the cleaned e-commerce datasets.

The SQL implementation is divided into two files:

| SQL File | Description |
|---|---|
| `sql/00_load_mysql.sql` | Database schema creation and data loading |
| `sql/task1_queries.sql` | Seven business analysis queries |

The SQL analysis uses MySQL queries, including window functions, to answer business-related questions and identify useful patterns in the e-commerce data.

### MySQL Database Setup

Create the database:

```sql
CREATE DATABASE shop;
USE shop;
```

Load the database schema and cleaned CSV data using the MySQL setup script.

From the project root directory, execute:

```bash
mysql --local-infile=1 -u root -p shop < sql/00_load_mysql.sql
```

Execute the business analysis queries:

```bash
mysql -u root -p shop < sql/task1_queries.sql
```

Alternatively, open the SQL files in MySQL Workbench and execute them directly.

**Note:** Ensure that the CSV file paths in the loading script match your local project location. If your script uses `LOAD DATA LOCAL INFILE`, local file loading must be enabled in your MySQL client and server configuration.

## 7. Power BI Dashboard

Microsoft Power BI is used to create interactive reports and visualizations from the cleaned e-commerce datasets.

The implementation guide is available in:

```text
POWERBI_GUIDE.md
```

The Power BI implementation includes:

- Connecting Power BI to the cleaned datasets.
- Preparing the data model.
- Creating DAX measures.
- Building report visualizations.
- Adding interactive slicers.
- Implementing drill-through functionality.

The dashboard helps users explore sales performance, customer behavior, and business trends through interactive reports.

## 8. Business Insights Report

The final business insights summary is available in:

```text
insights.pdf
```

This one-page report presents the important findings from the analysis in a concise and understandable format.

To regenerate the PDF:

```bash
python src/make_insights_pdf.py
```

## 9. Installation and Setup

### Prerequisites

Install the following tools:

- Python
- MySQL Server
- MySQL Workbench (recommended)
- Jupyter Notebook
- Microsoft Power BI Desktop

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Task-1-Ecommerce-Sales
```

### Step 2: Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Data Cleaning

```bash
python src/clean.py
```

This generates the cleaned CSV files inside `data/clean/`.

### Step 5: Run the Jupyter Notebook

```bash
jupyter notebook notebooks/cleaning_eda.ipynb
```

Open the notebook and select **Run All** to execute the analysis and generate the charts.

### Step 6: Execute MySQL Scripts

Create the database and load the cleaned data:

```bash
mysql --local-infile=1 -u root -p shop < sql/00_load_mysql.sql
```

Run the SQL business analysis queries:

```bash
mysql -u root -p shop < sql/task1_queries.sql
```

You can also execute the scripts using MySQL Workbench.

### Step 7: Build the Power BI Dashboard

Follow the instructions in:

```text
POWERBI_GUIDE.md
```

Connect the cleaned datasets and create the Power BI report using the documented DAX measures, visuals, slicers, and drill-through functionality.

### Step 8: Generate the Business Insights PDF

```bash
python src/make_insights_pdf.py
```

## 10. Reproducibility

The project uses fixed random seeds (`42`) to make the data processing and analysis pipeline deterministic where applicable.

The same input data and configuration should produce consistent cleaning and analysis outputs.

## 11. Key Deliverables

| Deliverable | Description |
|---|---|
| Cleaned CSV files | Processed datasets ready for analysis |
| Jupyter Notebook | Data cleaning, EDA, seven charts, and insights |
| MySQL scripts | Database setup and seven SQL business queries |
| Power BI Dashboard | Interactive business intelligence report |
| `POWERBI_GUIDE.md` | Dashboard implementation documentation |
| `insights.pdf` | One-page summary of business findings |

## 12. Conclusion

This project demonstrates a complete e-commerce data analytics workflow, starting from raw data cleaning and preprocessing through exploratory analysis, SQL-based business analysis, and interactive Power BI reporting.

By combining Python, MySQL, Jupyter Notebook, and Power BI, the project transforms raw e-commerce data into structured information and meaningful business insights.

It demonstrates practical skills in data preparation, database management, SQL querying, data visualization, business intelligence, and analytical reporting.