import os
import psycopg2
from io import StringIO
import csv
import logging
from google.cloud import storage
import functions_framework
logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.INFO)

# Configuration
# DB_USER = os.getenv('DB_USER')
# DB_PASS = os.getenv('DB_PASS')
# DB_NAME = os.getenv('DB_NAME')
# DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')

# These have been hardcoded here for local testing and would have been switched over to environment variables
# when deployed for security. Have commited this to VCS just for visibility (would not normally do this)
DB_USER = 'ngt'
DB_PASS = 'eaRiqJ5<Fod*i~Zp'
DB_NAME = 'postgres'
DB_HOST = '34.89.74.186'

connection = psycopg2.connect(host=DB_HOST, user=DB_USER,
                              password=DB_PASS,
                              dbname=DB_NAME, port=DB_PORT)

cursor = connection.cursor()



def process_data(data: str, ticker: str):
    """

    :param data: A string representation of a CSV file containing ticker data
    :param ticker: The ticker this data is for e.g. AAPL
    :return:
    """
    f = StringIO(data)
    reader = csv.reader(f, delimiter=',')
    index = 0
    # The rows that will be inserted into the database
    to_insert = []
    for line in reader:
        date = line[0]
        openn = line[1]
        high = line[2]
        low = line[3]
        close = line[4]
        adj_close = line[5]
        volume = line[6]
        if index > 0:
            # Skipping the header line of the file and only processing data
            to_insert.append((ticker, date, openn, high, low, close, adj_close, volume))
            # Would
        if index == 1:
            # I have included this just so that when testing functionality, it is only inserting a single row
            break
        index += 1
    sql = "INSERT INTO ticker_data(ticker,date,open,high,low,close,adj_close,volume) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(sql, to_insert)
    connection.commit()
    logger.info(f"Successfully processed and inserted {len(to_insert)} rows")


# This was used for initial local testing

# fp = "C:/Users/Mario/Desktop/stock_data/AAPL.csv"
# logger.info(f"Processing file {fp.split('/')[-1]}")
# data = open(fp, 'r').read()
# process_data(data, 'AAPL')
# print(len(data))

def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket. (Pulled from Google documentation)"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    return blob.download_as_string()


# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def ngt_test_cloud_function(cloud_event):
    """
    The function that is triggered when an object is finalized in a bucket.
    (Pulled from the example Cloud Function and customized)
    """
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    content = download_blob(bucket, name)
    data = content.decode('utf8')
    logger_string = f"Event ID: {event_id}" \
                    f"Event type: {event_type}" \
                    f"Bucket: {bucket}" \
                    f"File: {name}" \
                    f"Metageneration: {metageneration}" \
                    f"Created: {timeCreated}" \
                    f"Updated: {updated}"
    print(logger_string)
    logger.info(logger_string)
    # Have both the print and logger as only print seems to work in the Cloud Function log

    # Takes the data extracted and decoded from the file and passes it to be processed
    process_data(data, name)




