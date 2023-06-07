datasets_local_filesystem_path = 'datasets.csv'
delivery_stream_file_name = [
    ["COVID-19_County_Level_Data.csv", "lakehouse-delivery-stream-county"],
    ["COVID-19_Vaccinations_by_County.csv", "lakehouse-delivery-stream-vaccinations"],
    ["COVID-19_Cases_in_CT_Schools.csv", "lakehouse-delivery-stream-cases"]
]
destination_bucket_name = 'lakehouse-destination-bucket'
raw_db_name = 'lakehouse-raw-data'
standardized_db_name = 'lakehouse-standardized-data'
curated_db_name = 'lakehouse-curated-data'
city_county_path = '../datasets/city_county_data.csv'