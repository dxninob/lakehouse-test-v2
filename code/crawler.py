import constants
import awswrangler as wr


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

db_name = constants.raw_db_name
databases = wr.catalog.databases()
if db_name not in databases.values:
    wr.catalog.create_database(db_name)
    print(f'Database {db_name} was created')
else:
    wr.catalog.delete_database(db_name)
    wr.catalog.create_database(db_name)
    # for table in wr.catalog.get_tables(database=db_name):
    #     wr.catalog.delete_table_if_exists(database=db_name, table=table["Name"])
    print(f'Database {db_name} was deleted and created')

for key,value in df_dict.items():
    header = ['col' + str(x) for x in range(len(value.columns)-3)] + ['year','month','day']
    value.columns = header
    value = value.astype(str)
    columns_types, partitions_types = wr.catalog.extract_athena_types(
        df=value,
        file_format="csv",
        partition_cols=['year','month','day'],
    )

    wr.catalog.create_csv_table(
        database=db_name,
        table=key,
        path=f'{destination_bucket_uri}{key}/',
        columns_types=columns_types,
        partitions_types=partitions_types,
    )