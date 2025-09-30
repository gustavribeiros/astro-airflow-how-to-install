"""
Advanced Data Pipeline Example DAG

This DAG demonstrates more advanced Airflow concepts:
- Task dependencies with branching
- XCom (cross-communication) between tasks
- Task groups for organization
- Different operators
- Error handling
"""

from datetime import datetime, timedelta
import json
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup

# Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'data_pipeline_example',
    default_args=default_args,
    description='Advanced data pipeline example with branching and task groups',
    schedule_interval='@daily',
    catchup=False,
    tags=['example', 'data-pipeline', 'advanced'],
)

def extract_data(**context):
    """Simulate data extraction"""
    import random
    
    # Simulate extracting data from a source
    data = {
        'records_count': random.randint(100, 1000),
        'extraction_time': datetime.now().isoformat(),
        'source': 'api_endpoint'
    }
    
    print(f"Extracted {data['records_count']} records")
    
    # Return data to be used by other tasks via XCom
    return data

def validate_data(**context):
    """Validate extracted data"""
    data = context['task_instance'].xcom_pull(task_ids='extract_data')
    
    if data['records_count'] < 50:
        raise ValueError(f"Not enough records: {data['records_count']}")
    
    print(f"Data validation passed: {data['records_count']} records")
    return True

def check_data_quality(**context):
    """Decide which path to take based on data quality"""
    data = context['task_instance'].xcom_pull(task_ids='extract_data')
    
    if data['records_count'] > 500:
        print("High volume data detected - using parallel processing")
        return 'high_volume_processing.process_batch_1'
    else:
        print("Normal volume data - using standard processing")
        return 'standard_processing'

def process_data_standard(**context):
    """Standard data processing"""
    data = context['task_instance'].xcom_pull(task_ids='extract_data')
    print(f"Processing {data['records_count']} records using standard method")
    
    # Simulate processing
    processed_data = {
        'processed_records': data['records_count'],
        'processing_method': 'standard',
        'processing_time': datetime.now().isoformat()
    }
    
    return processed_data

def process_batch_1(**context):
    """Process first batch of high-volume data"""
    data = context['task_instance'].xcom_pull(task_ids='extract_data')
    batch_size = data['records_count'] // 2
    
    print(f"Processing batch 1: {batch_size} records")
    return {'batch': 1, 'records': batch_size}

def process_batch_2(**context):
    """Process second batch of high-volume data"""
    data = context['task_instance'].xcom_pull(task_ids='extract_data')
    batch_size = data['records_count'] // 2
    
    print(f"Processing batch 2: {batch_size} records")
    return {'batch': 2, 'records': batch_size}

def combine_batches(**context):
    """Combine results from parallel processing"""
    batch1 = context['task_instance'].xcom_pull(task_ids='high_volume_processing.process_batch_1')
    batch2 = context['task_instance'].xcom_pull(task_ids='high_volume_processing.process_batch_2')
    
    total_records = batch1['records'] + batch2['records']
    print(f"Combined {total_records} records from parallel processing")
    
    return {
        'processed_records': total_records,
        'processing_method': 'parallel',
        'processing_time': datetime.now().isoformat()
    }

def generate_report(**context):
    """Generate final report"""
    # Try to get data from either processing path
    standard_data = context['task_instance'].xcom_pull(task_ids='standard_processing')
    parallel_data = context['task_instance'].xcom_pull(task_ids='high_volume_processing.combine_batches')
    
    result_data = standard_data or parallel_data
    
    report = f"""
    Data Pipeline Report
    ===================
    Processing Method: {result_data['processing_method']}
    Records Processed: {result_data['processed_records']}
    Processing Time: {result_data['processing_time']}
    Pipeline Status: SUCCESS
    """
    
    print(report)
    return report

# Define tasks
start = DummyOperator(
    task_id='start',
    dag=dag,
)

extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

quality_check = BranchPythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    dag=dag,
)

# Standard processing path
standard_processing = PythonOperator(
    task_id='standard_processing',
    python_callable=process_data_standard,
    dag=dag,
)

# High volume processing with task group
with TaskGroup('high_volume_processing', dag=dag) as high_volume_group:
    batch1 = PythonOperator(
        task_id='process_batch_1',
        python_callable=process_batch_1,
    )
    
    batch2 = PythonOperator(
        task_id='process_batch_2',
        python_callable=process_batch_2,
    )
    
    combine = PythonOperator(
        task_id='combine_batches',
        python_callable=combine_batches,
        trigger_rule='all_success',  # Wait for both batches
    )
    
    [batch1, batch2] >> combine

# Data quality checks
quality_assurance = BashOperator(
    task_id='quality_assurance',
    bash_command='echo "Running data quality checks..." && sleep 2 && echo "Quality checks passed!"',
    trigger_rule='none_failed_or_skipped',  # Run regardless of which processing path was taken
    dag=dag,
)

# Generate report
report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    trigger_rule='none_failed_or_skipped',
    dag=dag,
)

# Cleanup task
cleanup = BashOperator(
    task_id='cleanup',
    bash_command='echo "Cleaning up temporary files..." && echo "Cleanup completed!"',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Define task dependencies
start >> extract >> validate >> quality_check
quality_check >> [standard_processing, high_volume_group] 
[standard_processing, high_volume_group] >> quality_assurance >> report >> cleanup >> end