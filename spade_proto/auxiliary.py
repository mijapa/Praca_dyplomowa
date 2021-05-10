def load_config_from_file():
    config = []
    with open('config', 'r') as reader:
        for line in reader:
            if not line.startswith('#'):
                config.append(line.split('\n')[0])
    return config


def authenticate_google_cloud():
    from google.oauth2 import service_account

    # TODO(developer): Set key_path to the path to the service account key
    #                  file.
    key_path = "service-account-file.json"

    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    from google.cloud import bigquery_storage

    bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

    from google.cloud import bigquery

    client = bigquery.Client(project="hazel-form-273711", credentials=credentials)

    return client, bqstorageclient


def perform_query(clients, QUERY):
    client, bqstorageclient = clients

    query_job = client.query(QUERY)  # API request
    results = query_job.result()  # Waits for query to finish
    dataframe = results.to_dataframe(bqstorage_client=bqstorageclient)
    return dataframe


def string_to_list(string):
    return string.strip('\']\'[').split('\', \'')


def change_country_names_to_codes(names_list):
    import pandas as pd
    codes_list = []
    codes = pd.read_csv('../CAMEO.country.txt', header=0, sep='\t')
    for country_name in names_list:
        code = codes.loc[codes.LABEL == country_name].CODE.values[0]
        codes_list.append(code)
    return codes_list
