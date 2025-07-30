import pandas as pd
from sqlalchemy import create_engine

# Setup provenance log as a module-level list
provenance = []

def log_provenance(table, column, action, rows_affected):
    provenance.append({
        'table': table,
        'column': column,
        'action': action,
        'rows_affected': rows_affected,
        'timestamp': pd.Timestamp.now()
    })

def handle_missing_age(df):
    if 'age' in df.columns:
        missing_before = df['age'].isna().sum()
        median_age = df['age'].median()
        df['age_imputed'] = df['age'].isna()
        df['age'].fillna(median_age, inplace=True)
        missing_after = df['age'].isna().sum()
        log_provenance('patients', 'age', 'imputed missing ages with median', missing_before - missing_after)
    return df

def validate_timestamps(df, start_col='admit_time', end_col='discharge_time'):
    if start_col in df.columns and end_col in df.columns:
        invalid_rows = df[df[start_col] > df[end_col]]
        df.loc[df[start_col] > df[end_col], 'timestamp_invalid'] = True
        log_provenance('admissions', f'{start_col}, {end_col}', 'flagged invalid timestamps', len(invalid_rows))
    return df

def get_provenance_log():
    return pd.DataFrame(provenance)

def clean_and_store_tables(table_list, engine):
    with engine.connect() as conn:
        for table_name in table_list:
            print(f"\n🔄 Processing table: {table_name}")
            df = pd.read_sql_table(table_name, conn)

            if 'age' in df.columns:
                df = handle_missing_age(df)

            if 'admit_time' in df.columns and 'discharge_time' in df.columns:
                df = validate_timestamps(df, 'admit_time', 'discharge_time')

            df.to_sql(f"{table_name}_clean", conn, if_exists='replace', index=False)
            print(f"✅ Cleaned table stored: {table_name}_clean")

    get_provenance_log().to_csv('../outputs/data_provenance_log.csv', index=False)
    print("📝 Provenance log saved as data_provenance_log.csv")
