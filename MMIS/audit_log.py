from datetime import datetime
from sqlalchemy import text

def log_access(engine, user_id, table_name, access_type, query_details=None, success=True):
    insert_sql = """
    INSERT INTO access_logs 
        (user_id, table_accessed, access_type, timestamp, query_details, success)
    VALUES 
        (:user_id, :table_accessed, :access_type, :timestamp, :query_details, :success)
    """
    params = {
        'user_id': user_id,
        'table_accessed': table_name,
        'access_type': access_type,
        'timestamp': datetime.now(),
        'query_details': query_details,
        'success': success
    }
    with engine.connect() as conn:
        conn.execute(text(insert_sql), params)
        conn.commit()
