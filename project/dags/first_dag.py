

try:
    from datetime import timedelta
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from datetime import datetime
    from send import send_queue

    print("All Dag modules are ok ......")
except Exception as e:
    print("Error  {} ".format(e))


with DAG(
        dag_id="first_dag",
        schedule_interval="*/3 * * * *",
        default_args={
            "owner": "airflow",
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
            "start_date": datetime(2022, 1, 16),
        },
        catchup=False) as f:

    first_function_execute = PythonOperator(
        task_id="first_function_execute",
        python_callable=send_queue,
        provide_context=True,
    )


first_function_execute
