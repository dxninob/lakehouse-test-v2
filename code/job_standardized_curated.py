import constants
import awswrangler as wr
import openpyxl
import pandas as pd


# Read standardized data
df_tables = wr.catalog.tables(database=constants.standardized_db_name)
df_tables = df_tables["Table"]

df_dict = {}
for df_table in df_tables:
    df_dict[df_table] = wr.s3.read_parquet_table(database=constants.standardized_db_name, table=df_table)

# Table 1
table_1 = df_dict["cases_in_ct_schools"]
table_1 =  table_1[["report_period_end","total_cases"]]
table_1.columns = ["date", "cases"]
table_1 = table_1.groupby(["date"]).sum().reset_index()

# Table 2
city_county = {}
with open(constants.city_county_path, 'rb') as f:
    for line in f:
        line = line.decode().strip()
        k,v = line.split(',')
        city_county[k] = v

table_2 = df_dict["cases_in_ct_schools"]
table_2 = table_2[["city","total_cases"]]
table_2["city"] = [city_county[i] for i in table_2["city"]]
table_2.columns = ["county", "cases"]
table_2 = table_2.groupby(["county"]).sum().reset_index()

# Table 3
table_3 = df_dict["county_level_data"]
table_3 = table_3[["report_date","county","cumulative_cases"]]
table_3.columns = ["date","county", "cases"]

# Table 4
table_4 = df_dict["county_level_data"]
table_4 = table_4[["report_date","census_today","fullyvax_today","partialvax_today","nonvax_today"]]
table_4.columns = ["date","census","fully_vaccinated","partial_vaccinated","non_vaccinated"]
table_4 = table_4.groupby(["date"]).sum().reset_index()

# Table 5
table_5 = df_dict["vaccinations_by_county"]
table_5 = table_5[["date","at_least_one_dose","fully_vaccinated","additional_dose_1_received_count"]].fillna(0)
table_5.columns = ["date","one_dose","two_doses","additional_dose"]
table_5 = table_5.groupby("date").sum().reset_index()
table_5['one_dose'] = table_5["one_dose"] - table_5["two_doses"]


# Delete existing data in curated bucket and catalog
db_name = constants.curated_db_name
cuarted_data_bucket_uri = 's3://' + db_name + '/'
wr.s3.delete_objects(cuarted_data_bucket_uri)

databases = wr.catalog.databases()
if db_name not in databases.values:
    wr.catalog.create_database(db_name)
    print(f'Database {db_name} was created')
else:
    wr.catalog.delete_database(db_name)
    wr.catalog.create_database(db_name)
    print(f'Database {db_name} was deleted and created')

# Write curated data
tables = [table_1, table_2, table_3, table_4, table_5]
for i in range(len(tables)):
    res = wr.s3.to_parquet(
        df=tables[i],
        path=f's3://{db_name}/table_{i+1}/',
        dataset=True,
        database=db_name,
        table=f'table_{i+1}',
        mode='append',
    )