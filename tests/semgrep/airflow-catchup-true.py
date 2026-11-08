from airflow import DAG

# ruleid: airflow-dag-catchup-true
dag = DAG("a", catchup=True)
# ok: airflow-dag-catchup-true
dag2 = DAG("b", catchup=False)
