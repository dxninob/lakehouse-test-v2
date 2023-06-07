import constants
import awswrangler as wr
import pandas as pd
import numpy as np


destination_bucket_uri = 's3://' + constants.destination_bucket_name + '/'
destination_bucket_files = wr.s3.list_objects(destination_bucket_uri)

prefix_set = set()
for f in destination_bucket_files:
    path_split = f.split('/')
    prefix = path_split[3]
    prefix_set.add(prefix)

df_dict = {}
for prefix in prefix_set:
    path = destination_bucket_uri + prefix + '/'
    df_dict[prefix] = wr.s3.read_csv(path=path, header=None, sep=',', dataset=True)

db_name = constants.standardized_db_name
standardized_data_bucket_uri = 's3://' + db_name + '/'
wr.s3.delete_objects(standardized_data_bucket_uri)

databases = wr.catalog.databases()
if db_name not in databases.values:
    wr.catalog.create_database(db_name)
    print(f'Database {db_name} was created')
else:
    wr.catalog.delete_database(db_name)
    wr.catalog.create_database(db_name)
    print(f'Database {db_name} was deleted and created')

for key,value in df_dict.items():
    header = value.iloc[0]
    header.iloc[-3:] = ['year','month','day']
    header = header.str.lower()
    header = header.str.replace(' ','_')
    value.columns = header
    value = value[1:]

    if key == 'cases_in_ct_schools':
        value[['report_period_start','report_period_end']] = value.report_period.str.split(" - ", expand=True)
        value = value.drop(columns=['report_period'])
        value['academic_year'] = value.academic_year.str.split(pat='-', n=0).str[0]
        size = len(value.loc[value.total_cases == '<6', 'total_cases'])
        value.loc[value.total_cases == '<6', 'total_cases'] = np.random.randint(low=1, high=6, size=size)
    
    value = value.apply(pd.to_numeric, errors='ignore')
    value = value.convert_dtypes()
    if key == 'cases_in_ct_schools':
        value[['date_updated','report_period_start','report_period_end']] = value[['date_updated','report_period_start','report_period_end']].apply(pd.to_datetime, errors='ignore', format='%m/%d/%Y')
    elif key == 'county_level_data':
        value[['report_date','data_updated']] = value[['report_date','data_updated']].apply(pd.to_datetime, errors='ignore', format='%m/%d/%Y')
    elif key == 'vaccinations_by_county':
        value['date'] = value['date'].apply(pd.to_datetime, errors='ignore', format='%m/%d/%Y')
    
    value = value.fillna(0)
    print(value)
    print(value.info())

    res = wr.s3.to_parquet(
        df=value,
        path=f's3://{db_name}/{key}/',
        dataset=True,
        database=db_name,
        table=key,
        partition_cols=['year','month','day'],
        mode='append',
    )       