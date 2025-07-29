import logging
from sqlalchemy import create_engine
from audit_log import log_access

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_engine(user, password, host='localhost', port=3306, database='mimic_hipe_linkage'):
    url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    return create_engine(url)

def insert_table(df, table_name, engine, user_id='unknown_user', if_exists='replace'):
    if df.empty:
        logging.warning(f"DataFrame for table {table_name} is empty. Skipping insert.")
        log_access(engine, user_id, table_name, 'INSERT', 'Empty DataFrame, skipped insert', success=False)
        return
    try:
        logging.info(f"Inserting table {table_name} with if_exists='{if_exists}'")
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
        logging.info(f"Successfully inserted {table_name}")
        log_access(engine, user_id, table_name, 'INSERT', f'Inserted {len(df)} rows', success=True)
    except Exception as e:
        logging.error(f"Error inserting table {table_name}: {e}")
        log_access(engine, user_id, table_name, 'INSERT', f'Error: {e}', success=False)

def run_etl(dataframes_dict, tables_to_load, user, password, user_id='unknown_user'):
    engine = get_engine(user, password)
    for table_name in tables_to_load:
        if table_name in dataframes_dict:
            insert_table(dataframes_dict[table_name], table_name, engine, user_id=user_id)
        else:
            logging.warning(f"Table {table_name} not found in dataframes.")
            log_access(engine, user_id, table_name, 'INSERT', 'Table not found in dataframes', success=False)
