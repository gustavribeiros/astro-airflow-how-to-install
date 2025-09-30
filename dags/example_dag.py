from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'example_hello_world_dag',
    default_args=default_args,
    description='A simple Hello World DAG',
    schedule_interval=timedelta(days=1),  # Run daily
    catchup=False,  # Don't run for past dates
    tags=['example', 'hello-world'],
)

def print_hello():
    """Simple Python function to print hello"""
    print("Hello from Airflow!")
    print("This is your first DAG running successfully!")
    return "Hello World task completed"

def print_date():
    """Print current date and time"""
    current_time = datetime.now()
    print(f"Current date and time: {current_time}")
    return f"Date task completed at {current_time}"

# Task 1: Print Hello using Python
hello_task = PythonOperator(
    task_id='hello_world_task',
    python_callable=print_hello,
    dag=dag,
)

# Task 2: Print date using Python
date_task = PythonOperator(
    task_id='print_date_task',
    python_callable=print_date,
    dag=dag,
)

# Task 3: Bash command to list directory contents
bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Running bash command..." && ls -la /opt/airflow/',
    dag=dag,
)

# Task 4: Another bash task to show system info
system_info_task = BashOperator(
    task_id='system_info_task',
    bash_command='echo "System Information:" && uname -a && echo "Date: $(date)"',
    dag=dag,
)

# Define task dependencies
hello_task >> date_task >> bash_task >> system_info_task