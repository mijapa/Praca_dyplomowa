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


def create_symmetry_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Connection']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Connection strength {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/symmetry/{actor1} and {actor2}connection.png', bbox_inches='tight')
    return g


def create_power_client_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Countries']).last()
    g = s.unstack().plot(y='Ratio')
    g.set(ylabel='Ratio')
    g.set_title(f"Power-client {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/power-client/{actor1} and {actor2} power-client.png', bbox_inches='tight')
    return g


def create_fight_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Fight']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Fight {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/fight/{actor1} and {actor2} fight.png', bbox_inches='tight')
    return g


def create_cooperate_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Cooperate']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Express intent to cooperate {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/cooperate/{actor1} and {actor2} cooperate.png', bbox_inches='tight')
    return g


def create_fight_vs_all_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Fight vs all']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Fight vs all events{actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/fight vs all/{actor1} and {actor2} fight vs all.png', bbox_inches='tight')
    return g


def create_cooperate_nummen30_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Cooperate']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Express intent to cooperate with mentions >=30 {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/cooperate_nummen30/{actor1} and {actor2} cooperate.png', bbox_inches='tight')
    return g


def create_cooperate_times_nummen_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Cooperate']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Express intent to cooperate times mentions {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/cooperate_times_nummen/{actor1} and {actor2} cooperate times mentions.png',
                bbox_inches='tight')
    return g


def create_cooperate_times_goldstein_figure(symmetry, actor1, actor2):
    import matplotlib.pyplot as plt
    s = symmetry.groupby(['Time', 'Cooperate']).last()
    g = s.unstack().plot(y='Percentage')
    g.set(ylabel='Percentage')
    g.set_title(f"Express intent to cooperate times Goldstein {actor1} and {actor2} 2015-2020")
    g.figure.set_size_inches(20, 8)
    plt.savefig(f'figures/cooperate_times_goldstein/{actor1} and {actor2} cooperate times goldstein.png',
                bbox_inches='tight')
    return g