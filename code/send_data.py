import constants
import boto3


datasets_path = constants.datasets_local_filesystem_path
stream_name = ""
stream_names = constants.delivery_stream_file_name

client = boto3.client('firehose')
datasets = []

with open(datasets_path, 'rb') as dataset:
    for line in dataset:
        line = line.decode()
        datasets.append(line.strip())

print("Datasets paths:", datasets)

for i in datasets:
    for j,k in stream_names:
        if j in i:
            stream_name = k
            break
    print('Start:', i)
    with open(i, 'rb') as dataset:
        for line in dataset:
            line = line.decode()
            response = client.put_record(
                DeliveryStreamName=stream_name,
                Record={
                    'Data': line
                }
            )
    print('Finish:', i)