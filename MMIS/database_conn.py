from sqlalchemy import create_engine, text

def get_engine(user='root', password='password', host='localhost', port='3306', database='mimic_hipe_linkage'):
    url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    return create_engine(url)

def create_database_if_not_exists(user, password, host='localhost', port=3306, database='mimic_hipe_linkage'):
    root_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    engine_root = create_engine(root_url)

    with engine_root.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database};"))
