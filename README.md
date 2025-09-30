# Apache Airflow with Docker - Complete Setup Guide

This repository provides a complete, step-by-step guide to set up Apache Airflow locally using Docker. You'll learn how to run DAGs (Directed Acyclic Graphs) in a containerized environment, making it easy to develop and test your data workflows.

## 📋 Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Docker** (version 20.10.0 or later)
- **Docker Compose** (version 2.0.0 or later)
- At least **4GB of RAM** available for Docker
- At least **2 CPU cores**
- At least **1GB of disk space**

### Verify Prerequisites

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Check available system resources
docker system info
```

## 🚀 Quick Start

### Step 1: Clone This Repository

```bash
git clone https://github.com/gustavribeiros/astro-airflow-how-to-install.git
cd astro-airflow-how-to-install
```

### Step 2: Set Up Environment Variables

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit the `.env` file if needed. For Linux/macOS users, you should set the correct user ID:

```bash
echo -e "AIRFLOW_UID=$(id -u)" >> .env
```

### Step 3: Initialize Airflow

Run the initialization command to set up the database and create an admin user:

```bash
docker compose up airflow-init
```

Wait for the initialization to complete. You should see a message like "airflow-init exited with code 0".

### Step 4: Start Airflow Services

Start all Airflow services in detached mode:

```bash
docker compose up -d
```

This will start:
- **PostgreSQL database** (for Airflow metadata)
- **Airflow webserver** (Web UI)
- **Airflow scheduler** (Task scheduler)
- **Airflow triggerer** (For deferrable tasks)

### Step 5: Access the Airflow Web UI

1. Open your web browser
2. Go to `http://localhost:8080`
3. Log in with the default credentials:
   - **Username**: `airflow`
   - **Password**: `airflow`

You should see the Airflow dashboard with your DAGs!

## 📁 Project Structure

```
astro-airflow-how-to-install/
├── dags/                    # Your DAG files go here
│   └── example_dag.py      # Sample DAG to get you started
├── logs/                   # Airflow task logs
├── plugins/                # Custom Airflow plugins
├── config/                 # Additional Airflow configuration
├── docker-compose.yml      # Docker Compose configuration
├── .env.example           # Environment variables template
├── .env                   # Your environment variables (create from template)
├── requirements.txt       # Python dependencies for your DAGs
└── README.md              # This file
```

## 🔧 Working with DAGs

### Understanding the Example DAG

The included `example_dag.py` demonstrates:
- **Python operators** for custom Python functions
- **Bash operators** for shell commands
- **Task dependencies** and execution order
- **Basic DAG configuration**

### Creating Your Own DAG

1. Create a new Python file in the `dags/` directory
2. Follow this basic structure:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'your-name',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_first_dag',
    default_args=default_args,
    description='My first DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def my_task():
    print("Hello from my DAG!")
    return "Success"

task1 = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag,
)
```

3. Save the file and refresh the Airflow web UI
4. Your new DAG should appear in the list

### Running DAGs

1. In the Airflow web UI, find your DAG in the list
2. Click the toggle switch to enable the DAG
3. Click on the DAG name to view details
4. Click "Trigger DAG" to run it manually
5. Monitor the progress in the "Graph" or "Tree" view

## 🛠️ Managing the Environment

### Adding Python Dependencies

To add Python packages for your DAGs:

1. Edit the `.env` file:
```bash
_PIP_ADDITIONAL_REQUIREMENTS=pandas==1.5.3 requests==2.28.1
```

2. Restart the services:
```bash
docker compose down
docker compose up -d
```

### Viewing Logs

Check container logs:
```bash
# View all services
docker compose logs

# View specific service
docker compose logs airflow-webserver
docker compose logs airflow-scheduler

# Follow logs in real-time
docker compose logs -f airflow-scheduler
```

### Stopping Airflow

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ This will delete your data!)
docker compose down --volumes --remove-orphans
```

### Restarting Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart airflow-webserver
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied Errors (Linux/macOS)

**Problem**: Files created by Docker have wrong permissions.

**Solution**: Make sure `AIRFLOW_UID` is set correctly in your `.env` file:
```bash
echo "AIRFLOW_UID=$(id -u)" >> .env
docker compose down
docker compose up airflow-init
docker compose up -d
```

#### 2. Port 8080 Already in Use

**Problem**: Another service is using port 8080.

**Solution**: Change the port in `docker-compose.yml`:
```yaml
airflow-webserver:
  ports:
    - "8081:8080"  # Change to 8081 or any available port
```

#### 3. Not Enough Memory

**Problem**: Docker doesn't have enough memory allocated.

**Solution**: 
- Increase Docker's memory limit to at least 4GB
- Close other applications to free up memory

#### 4. DAGs Not Appearing

**Problem**: Your DAG files are not showing up in the web UI.

**Solutions**:
1. Check for Python syntax errors in your DAG files
2. Verify the file is in the `dags/` directory
3. Check the scheduler logs: `docker compose logs airflow-scheduler`
4. Refresh the web UI (Ctrl+F5)

#### 5. Database Connection Issues

**Problem**: Airflow can't connect to the PostgreSQL database.

**Solution**: Restart all services:
```bash
docker compose down
docker compose up -d
```

### Checking Service Health

```bash
# Check if all containers are running
docker compose ps

# Check container health
docker compose exec airflow-webserver airflow db check

# Test database connection
docker compose exec airflow-webserver airflow db check-migrations
```

## 📚 Next Steps

Once you have Airflow running, explore these topics:

1. **Learn about Airflow Operators**: BashOperator, PythonOperator, EmailOperator, etc.
2. **Understand Connections**: Set up connections to databases, APIs, and cloud services
3. **Explore XComs**: Pass data between tasks
4. **Work with Variables**: Store configuration values in Airflow
5. **Set up Monitoring**: Configure alerts and monitoring for your DAGs
6. **Production Deployment**: Learn about deploying Airflow in production environments

## 🤝 Contributing

Feel free to contribute to this guide by:
- Reporting issues
- Suggesting improvements
- Adding new example DAGs
- Improving documentation

## 📖 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#writing-a-dag-file)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy DAG building!** 🚀