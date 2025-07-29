from datetime import datetime

def log_access(engine, user_id, table_name, access_type, query_details=None, success=True):
    insert_sql = """
    INSERT INTO access_logs 
        (user_id, table_accessed, access_type, timestamp, query_details, success) 
    VALUES 
        (%s, %s, %s, %s, %s, %s)
    """
    params = (user_id, table_name, access_type, datetime.now(), query_details, success)
    with engine.connect() as conn:
        conn.execute(insert_sql, params)
