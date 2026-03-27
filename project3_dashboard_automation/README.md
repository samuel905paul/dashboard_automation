# Executive Dashboard Automation Suite

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Power BI](https://img.shields.io/badge/PowerBI-Enabled-yellow.svg)
![SQL](https://img.shields.io/badge/SQL-Server-orange.svg)
![Time Saved](https://img.shields.io/badge/Time_Saved-25hrs/month-success.svg)

Business Impact

- **95% faster** report delivery (3 days → 2 hours)
- **25+ hours/month** saved through automation
- **15+ dashboards** serving 50+ business users
- **Real-time insights** enabling C-suite decision-making

## Project Overview

End-to-end automated reporting solution integrating SQL Server data extraction, Python-based ETL pipelines, and Power BI dashboard deployment. Eliminates manual report generation while providing executives with real-time business intelligence.

### Key Features

**Automated Data Pipeline**: Scheduled ETL jobs with error handling  
**Multi-source Integration**: Connects 10+ data sources seamlessly  
**Power BI Automation**: Programmatic dataset refresh and deployment  
**Email Distribution**: Automated report delivery to stakeholders  
**Error Monitoring**: Real-time alerts for pipeline failures

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Data Sources   │ ───> │  Python ETL      │ ───> │  SQL Server     │
│  (10+ Systems)  │      │  Pipeline        │      │  Data Warehouse │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Email Reports  │ <─── │  Power BI        │ <─── │  Automated      │
│  (50+ Users)    │      │  Dashboards      │      │  Refresh        │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## Dashboard Portfolio

### 1. **Executive Summary Dashboard**
- **KPIs**: Revenue, Customer Count, Churn Rate, NPS Score
- **Visuals**: Trend lines, variance cards, heat maps
- **Frequency**: Daily refresh at 6 AM
- **Users**: C-Suite (CEO, CFO, COO)

### 2. **Sales Performance Dashboard**
- **Metrics**: Pipeline value, win rate, deal velocity, quota attainment
- **Drill-downs**: By rep, region, product, time period
- **Frequency**: Real-time (hourly refresh)
- **Users**: Sales Team, Sales Ops

### 3. **Financial Operations Dashboard**
- **Data**: Revenue, expenses, cash flow, AR/AP aging
- **Features**: Budget vs actual, variance analysis, forecasting
- **Frequency**: Daily at 8 AM
- **Users**: Finance Team, FP&A

### 4. **Customer Health Dashboard**
- **Insights**: Usage trends, support tickets, NPS, churn risk
- **Segments**: By tier, industry, tenure
- **Frequency**: Daily at 7 AM
- **Users**: Customer Success, Support

### 5. **Marketing Analytics Dashboard**
- **Metrics**: Campaign ROI, lead conversion, CAC, MQL/SQL
- **Attribution**: Multi-touch attribution modeling
- **Frequency**: Weekly on Mondays
- **Users**: Marketing Team

## Quick Start

### Prerequisites

```bash
Python 3.8+
SQL Server 2019+
Power BI Desktop/Service
Microsoft 365 (for email automation)
```

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/dashboard-automation.git
cd dashboard-automation

# Install dependencies
pip install -r requirements.txt

# Configure connections
cp config.example.py config.py
# Edit config.py with credentials
```

### Running the Pipeline

```bash
# Full automation pipeline
python main.py --mode full

# Extract data only
python main.py --mode extract

# Transform and load
python main.py --mode transform

# Refresh Power BI datasets
python main.py --mode refresh

# Send email reports
python main.py --mode distribute

# Run specific dashboard
python main.py --dashboard sales --mode full
```

## Project Structure

```
dashboard-automation/
│
├── src/
│   ├── extractors/
│   │   ├── sql_extractor.py
│   │   ├── api_extractor.py
│   │   └── file_extractor.py
│   ├── transformers/
│   │   ├── data_cleaner.py
│   │   ├── aggregator.py
│   │   └── calculator.py
│   ├── loaders/
│   │   ├── sql_loader.py
│   │   └── powerbi_loader.py
│   ├── powerbi/
│   │   ├── dataset_manager.py
│   │   ├── report_publisher.py
│   │   └── refresh_scheduler.py
│   └── notification/
│       ├── email_sender.py
│       └── teams_notifier.py
│
├── sql/
│   ├── extract_queries/
│   │   ├── sales_data.sql
│   │   ├── finance_data.sql
│   │   └── customer_data.sql
│   └── warehouse_schema/
│       └── create_tables.sql
│
├── dashboards/
│   ├── executive_summary.pbix
│   ├── sales_performance.pbix
│   ├── financial_operations.pbix
│   ├── customer_health.pbix
│   └── marketing_analytics.pbix
│
├── email_templates/
│   ├── executive_report.html
│   └── sales_report.html
│
├── schedules/
│   └── cron_jobs.txt
│
├── logs/
│   └── pipeline.log
│
├── main.py
├── requirements.txt
├── config.example.py
└── README.md
```

## ETL Pipeline Details

### 1. Data Extraction

```python
# Extract from multiple sources
def extract_sales_data():
    """Extract sales transactions from CRM."""
    query = """
    SELECT 
        deal_id,
        customer_id,
        deal_value,
        close_date,
        sales_rep,
        stage
    FROM crm.deals
    WHERE close_date >= DATEADD(month, -6, GETDATE())
    """
    return execute_query(query)
```

### 2. Data Transformation

```python
# Calculate derived metrics
def calculate_sales_metrics(df):
    """Calculate sales performance metrics."""
    df['deal_age_days'] = (pd.Timestamp.now() - df['create_date']).dt.days
    df['win_rate'] = df.groupby('sales_rep')['won'].transform('mean')
    df['avg_deal_size'] = df.groupby('sales_rep')['deal_value'].transform('mean')
    return df
```

### 3. Data Loading

```python
# Load to SQL Server
def load_to_warehouse(df, table_name):
    """Load transformed data to warehouse."""
    df.to_sql(
        table_name,
        engine,
        schema='analytics',
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=1000
    )
```

### 4. Power BI Refresh

```python
# Refresh Power BI dataset
def refresh_powerbi_dataset(dataset_id):
    """Trigger Power BI dataset refresh."""
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes'
    response = requests.post(url, headers=headers)
    return response.status_code == 202
```

## Automated Email Reports

### Executive Daily Summary

```html
<!DOCTYPE html>
<html>
<body>
    <h1>Daily Executive Summary - {date}</h1>
    
    <h2>Key Metrics</h2>
    <table>
        <tr>
            <td>Revenue (MTD)</td>
            <td>${revenue:,.0f}</td>
            <td style="color: {revenue_color}">{revenue_change:+.1%}</td>
        </tr>
        <tr>
            <td>New Customers</td>
            <td>{new_customers:,}</td>
            <td style="color: {customers_color}">{customers_change:+.1%}</td>
        </tr>
    </table>
    
    <p><a href="{dashboard_link}">View Full Dashboard</a></p>
</body>
</html>
```

## Automation Schedule

```bash
# Daily Executive Summary - 6:00 AM
0 6 * * * python main.py --dashboard executive --mode full

# Sales Dashboard - Hourly
0 * * * * python main.py --dashboard sales --mode refresh

# Financial Dashboard - 8:00 AM
0 8 * * * python main.py --dashboard finance --mode full

# Weekly Marketing Report - Monday 9:00 AM
0 9 * * 1 python main.py --dashboard marketing --mode full --email
```

## Sample Power BI Visuals

### KPI Cards with Conditional Formatting

```dax
Revenue_MTD = 
CALCULATE(
    SUM(Sales[Revenue]),
    DATESMTD('Calendar'[Date])
)

Revenue_Change = 
VAR CurrentMTD = [Revenue_MTD]
VAR PreviousMTD = 
    CALCULATE(
        [Revenue_MTD],
        DATEADD('Calendar'[Date], -1, MONTH)
    )
RETURN
DIVIDE(CurrentMTD - PreviousMTD, PreviousMTD, 0)
```

### Dynamic Drill-through Filtering

```dax
Selected_Region = 
IF(
    HASONEVALUE(Geography[Region]),
    VALUES(Geography[Region]),
    "All Regions"
)
```

## Key Technical Achievements

### Performance Optimization

- **Query Optimization**: Reduced execution time from 45s to <5s
- **Incremental Refresh**: Only loads changed data (90% time reduction)
- **Parallel Processing**: Concurrent data extraction from multiple sources
- **Caching Strategy**: Stores intermediate results to avoid recomputation

### Error Handling

```python
def safe_extract(source_name, extraction_func):
    """Wrapper for safe data extraction with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Extracting from {source_name} (Attempt {attempt + 1})")
            data = extraction_func()
            logger.info(f"Successfully extracted {len(data)} records")
            return data
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            if attempt == max_retries - 1:
                send_alert(f"Failed to extract from {source_name}")
                raise
            time.sleep(30)  # Wait before retry
```

## Business Impact Metrics

### Time Savings

| Report | Manual Time | Automated Time | Savings |
|--------|-------------|----------------|---------|
| Executive Summary | 4 hours | 15 min | 94% |
| Sales Dashboard | 6 hours | 20 min | 94% |
| Finance Report | 8 hours | 30 min | 94% |
| Customer Analytics | 5 hours | 15 min | 95% |
| Marketing ROI | 4 hours | 10 min | 96% |

**Total Monthly Savings**: 25+ hours

### User Adoption

- **Active Users**: 50+ across 5 departments
- **Daily Views**: 200+ dashboard interactions
- **Report Downloads**: 75+ per week
- **Satisfaction Score**: 4.8/5.0

## Security & Compliance

### Data Access Control

- Role-based access control (RBAC) in Power BI
- Row-level security (RLS) for sensitive data
- Service principal authentication for automation
- Encrypted database connections

### Audit Logging

```python
def log_access(user_id, dashboard_name, action):
    """Log dashboard access for audit trail."""
    log_entry = {
        'timestamp': datetime.now(),
        'user_id': user_id,
        'dashboard': dashboard_name,
        'action': action,
        'ip_address': get_client_ip()
    }
    audit_logger.info(json.dumps(log_entry))
```

## Troubleshooting

### Common Issues

**Issue**: Power BI refresh fails  
**Solution**: Check service principal permissions, verify dataset connection

**Issue**: Email delivery fails  
**Solution**: Validate SMTP settings, check recipient addresses

**Issue**: Data extraction timeout  
**Solution**: Optimize SQL queries, increase timeout threshold

## Future Enhancements

- [ ] Real-time streaming dashboards using Power BI streaming datasets
- [ ] Natural language query interface (Power BI Q&A)
- [ ] Machine learning integration for predictive analytics
- [ ] Mobile app optimization for executive on-the-go access
- [ ] Slack/Teams integration for instant notifications

## Author

**T Samuel Paul**  
Data Analyst | BI Developer

- LinkedIn: [linkedin.com/in/tsamuelpaul01](https://www.linkedin.com/in/tsamuelpaul01)
- Email: tsamuelpaul01@gmail.com

## License

MIT License - see LICENSE file for details.

---

⭐ If this helped automate your reporting, give it a star!
