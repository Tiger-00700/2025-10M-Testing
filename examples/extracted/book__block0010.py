
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime, timedelta

    def archive_unused_data():
        # 归档30天未使用的数据
        lifecycle_manager = TestDataLifecycleManager()
        # 实现归档逻辑

    dag = DAG(
        'test_data_lifecycle',
        default_args={'owner': 'test_team'},
        schedule_interval='@daily',
        start_date=datetime(2023, 1, 1)
    )

    archive_task = PythonOperator(
        task_id='archive_unused_data',
        python_callable=archive_unused_data,
        dag=dag
    )
