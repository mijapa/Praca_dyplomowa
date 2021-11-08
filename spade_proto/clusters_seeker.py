import itertools
import json

import pandas as pd
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.clusters_auxiliary import get_data_with_event_description, update_palette_for_event_descriptions
from spade_proto.pattern_seeker_connection_strength import PatternSeeker
from spade_proto.pattern_seeker_cooperate import PatternSeekerCooperate
from spade_proto.pattern_seeker_cooperate_numMen5 import PatternSeekerCooperateNumMen5


class ClustersSeeker(Agent):
    first_config = {}
    results = {}

    class SendResultsBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="raport_generator@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "symmetry_results")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.agent.symmetry_results.to_json(orient='table')  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    # create an agent from within anagent
    class CreatePatternSeekerBehav(OneShotBehaviour):
        async def on_start(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Creating new Pattern Seeker agent behaviour . . .")

        async def run(self):
            config_countries = self.agent.config['countries']
            length = len(config_countries)
            combi = set(itertools.combinations(range(length), 2))
            # print(combi)
            for i, j in combi:
                # print(i, j)
                # print(f'config {config_countries}')
                actor1 = config_countries[i]
                actor2 = config_countries[j]
                self.agent.first_config = {'actors': {'actor1': actor1, 'actor2': actor2},
                                           'granulation': self.agent.config['granulation']
                                           }

                name = f"pattern_seeker_{actor1}_{actor2}@localhost"
                agent = PatternSeeker(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)

                # name = f"pattern_seeker_power_client_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerPowerClient(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_fight_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerFight(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                name = f"pattern_seeker_cooperate_{actor1}_{actor2}@localhost"
                agent = PatternSeekerCooperate(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)
                #
                # # name = f"pattern_seeker_fight_vs_all_{actor1}_{actor2}@localhost"
                # # agent = PatternSeekerFightVsAll(name, "RADiance89")
                # # await self.start_agent_and_send_config(agent, name)
                #
                name = f"pattern_seeker_cooperate_nummen5_{actor1}_{actor2}@localhost"
                agent = PatternSeekerCooperateNumMen5(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_cooperate_times_nummen_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerCooperateTimesNumMen(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_cooperate_times_goldstein_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerCooperateTimesGoldstein(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)

        async def start_agent_and_send_config(self, agent, name):
            # This start is inside an async def, so it must be awaited
            await agent.start(auto_register=True)
            # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            # print(self.agent.first_config)
            msg = Message(to=name)  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "config")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            print(f'first_config {self.agent.first_config}')
            msg.body = json.dumps(self.agent.first_config)  # Set the message content
            await self.send(msg)

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: running")

            timeout = 10
            msg = await self.receive(timeout=timeout)  # wait for a message for 5 seconds
            if msg:
                # print(f"{self.agent.jid}: {self.__class__.__name__}: Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = json.loads(msg.body)
                    self.agent.add_behaviour(self.agent.SeekClusters())
                    # self.agent.add_behaviour(self.agent.CreatePatternSeekerBehav())
                # if msg.metadata["ontology"] == 'results':
                #     print(f"{self.agent.jid}: {self.__class__.__name__}: RESULTS")
                #     # print(f"{self.agent.jid}: {self.__class__.__name__}: msg.body: {msg.body}")
                #
                #     res = pd.read_json(msg.body, orient='table')
                #
                #     result_type = msg.metadata["type"]
                #     try:
                #         self.agent.results[result_type] = pd.concat([self.agent.results[result_type], res])
                #     except KeyError:
                #         self.agent.results[result_type] = res


            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: "
                      f"Did not received any message after {timeout} seconds")
                # self.agent.add_behaviour(self.agent.SendResultsBehav())
                # todo: send results to raport generator
                results = self.agent.results
                for res in results:
                    f = open(f"results_{res} {self.agent.config['granulation']}.json", "w")
                    f.write(results[res].to_json(orient='table'))
                    f.close()
                # self.agent.add_behaviour(self.agent.SeekSimpleCorrelationBehav())
                # self.agent.add_behaviour(self.agent.SeekComplexCorrelationBehav())
                self.kill()

    class SendConfigBehav(OneShotBehaviour):

        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            print(self.agent.first_config)
            msg = Message(
                to=f"pattern_seeker_{self.agent.first_config['actors']['actor1']}_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "config")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            print(f'first_config {self.agent.first_config}')
            msg.body = json.dumps(self.agent.first_config)  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviou

    class SendResultsBehav(OneShotBehaviour):
        async def run(self):
            to = "raport_generator@localhost"
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to=to)  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "symmetry_results")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            # print(self.agent.symmetry_results.head())
            # print(self.agent.symmetry_results.columns)

            body = self.agent.symmetry_results.to_json(orient='table')

            # print(f"{self.agent.jid}: {self.__class__.__name__}: symmetry_results: {self.agent.symmetry_results}")
            msg.body = body  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent to: {to}")
            # print(f"{self.agent.jid}: {self.__class__.__name__}: msg.body: {msg.body}")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    class SeekClusters(OneShotBehaviour):
        async def pre_analysis(self):
            self = []

            # country = 'tjw'
            # actor1coutrycode = 'TWN'
            # actir2countrycodes = "'PRK', 'KOR', 'JPN', 'USA', 'RUS', 'CHN'"

            country = 'syr'
            actor1coutrycode = 'SYR'
            actir2countrycodes = "'USA', 'RUS', 'ISR', 'IRN', 'IRQ', 'TUR'"

            # %%

            code = "EventBaseCode"
            folder = f"fig_{code}_{country}"
            n = 20

            big_data = pd.DataFrame()

            data = pd.DataFrame()

            filtration = ''

            palette = []
            QUERY = (f"""SELECT
              EventBaseCode,
              Actor1CountryCode,
              Actor2CountryCode,
              COUNT(*) AS Count
            FROM
              `gdelt-bq.gdeltv2.events`
            WHERE
              Year >= 2015
              AND Year <= 2020
              AND Actor1CountryCode = "{actor1coutrycode}"
              AND Actor2CountryCode IN ({actir2countrycodes})
            GROUP BY
              EventBaseCode,
              Actor1CountryCode,
              Actor2CountryCode
            ORDER BY
              EventBaseCode""")

            smg = await get_data_with_event_description(QUERY, self)
            palette = update_palette_for_event_descriptions(palette, smg.EVENTDESCRIPTION)

            # create new clumn with countries names
            smg['Relation'] = smg[['Actor1CountryCode', 'Actor2CountryCode']].agg('-'.join, axis=1)
            # calculate percentage of event type for relation between countries
            smg['Percentage'] = smg.groupby(['Relation'])['Count'].apply(lambda x: x / x.sum() * 100)

            data = data.append(smg, ignore_index=True)
            # save_sum_up_relations_barplots(folder=folder+filtration, name_with=filtration, data=data)

            data['filtration'] = 'none'
            big_data = big_data.append(data, ignore_index=True)

            ######

            nummens = [5, 10]

            for nummen in nummens:
                data = pd.DataFrame()
                # parameters

                filtration = f'with mentions >={nummen}'
                filtration_short = f'nummen>={nummen}'

                palette = []
                QUERY = (f"""SELECT
                  EventBaseCode,
                  Actor1CountryCode,
                  Actor2CountryCode,
                  COUNT(*) AS Count
                FROM
                  `gdelt-bq.gdeltv2.events`
                WHERE
                  Year >= 2015
                  AND Year <= 2020
                  AND Actor1CountryCode = "{actor1coutrycode}"
                  AND Actor2CountryCode IN ({actir2countrycodes})
                  AND NumMentions >= {nummen}
                GROUP BY
                  EventBaseCode,
                  Actor1CountryCode,
                  Actor2CountryCode
                ORDER BY
                  EventBaseCode""")

                smg = await get_data_with_event_description(QUERY, self)
                palette = update_palette_for_event_descriptions(palette, smg.EVENTDESCRIPTION)

                # create new clumn with countries names
                smg['Relation'] = smg[['Actor1CountryCode', 'Actor2CountryCode']].agg('-'.join, axis=1)
                # calculate percentage of event type for relation between countries
                smg['Percentage'] = smg.groupby(['Relation'])['Count'].apply(lambda x: x / x.sum() * 100)

                data = data.append(smg, ignore_index=True)
                # save_sum_up_relations_barplots(folder=folder+filtration, name_with=filtration, data=data)

                data['filtration'] = filtration_short
                big_data = big_data.append(data, ignore_index=True)

            ######
            data = pd.DataFrame()

            # parameters
            gold = 3
            filtration = f'Goldstein Scale >={gold}'
            filtration_short = f'goldstein>={gold}'

            palette = []
            QUERY = (f"""SELECT
              EventBaseCode,
              Actor1CountryCode,
              Actor2CountryCode,
              COUNT(*) AS Count
            FROM
              `gdelt-bq.gdeltv2.events`
            WHERE
              Year >= 2015
              AND Year <= 2020
              AND Actor1CountryCode = "{actor1coutrycode}"
              AND Actor2CountryCode IN ({actir2countrycodes})
              AND GoldsteinScale >= {gold}
            GROUP BY
              EventBaseCode,
              Actor1CountryCode,
              Actor2CountryCode
            ORDER BY
              EventBaseCode""")

            smg = await get_data_with_event_description(QUERY, self)
            palette = update_palette_for_event_descriptions(palette, smg.EVENTDESCRIPTION)

            # create new clumn with countries names
            smg['Relation'] = smg[['Actor1CountryCode', 'Actor2CountryCode']].agg('-'.join, axis=1)
            # calculate percentage of event type for relation between countries
            smg['Percentage'] = smg.groupby(['Relation'])['Count'].apply(lambda x: x / x.sum() * 100)

            data = data.append(smg, ignore_index=True)
            # save_sum_up_relations_barplots(folder=folder+filtration, name_with=filtration, data=data)

            data['filtration'] = filtration_short
            big_data = big_data.append(data, ignore_index=True)

            big_data.to_csv(f'big_data_{country}.csv')

        async def clustering(self):
            country = 'syr'
            # load data from file
            big_data = pd.read_csv(f'big_data_{country}.csv',
                                   dtype={'EventRootCode': object, 'EventBaseCode': object})
            big_data = big_data[['EVENTDESCRIPTION', 'Percentage', 'Relation', 'filtration']]
            big_data['event_filtr'] = big_data[['EVENTDESCRIPTION', 'filtration']].agg('_'.join, axis=1)

            big_data = big_data[['Relation', 'Percentage', 'event_filtr']]

            selected_events = ['Make statement- not specified below_none',
                               'Return release- not specified below_goldstein>=3',
                               'Consult- not specified below_nummen>=5',
                               'Engage in negotiation_nummen>=5',
                               'Use conventional military force- not specified below_nummen>=5',
                               'Praise or endorse_nummen>=10',
                               # 'Accuse- not specified below_avgtone>=10or<=-10'
                               ]
            big_data_selected = big_data[big_data['event_filtr'].isin(selected_events)]

            big_data_selected = big_data_selected.pivot_table(values='Percentage', index='Relation',
                                                              columns=['event_filtr'])

            # UWAGA zastępuję NaN zerami!!! co nie koniecznie jest pożądane
            big_data_selected = big_data_selected.fillna(0)

            points = big_data_selected.to_numpy()

            n_clust = [2, 3, 4, 5
                       # , 6, 7, 8
                       ]
            cl_names = []
            cl_results = []

            big_data_result = big_data_selected.copy()

            for n_cl in n_clust:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=n_cl, init='random', random_state=1)
                km = kmeans.fit(points)

                # funkcja predict zwaraca etykiety klastru do jakiego został przypisany obiekt
                clusters_id = kmeans.predict(points)

                cl_name = f'n = {n_cl}'
                cl_names.append(cl_name)
                cl_names = list(dict.fromkeys(cl_names))
                big_data_result[cl_name] = clusters_id

            big_data_result = big_data_result[cl_names]
            big_data_result.columns.rename('kMeans', inplace=True)

            import seaborn as sns
            cm = sns.light_palette("green", as_cmap=True)
            big_data_styler = big_data_result.style.background_gradient(cmap='viridis')

            def df_to_png(df, file):
                import imgkit
                imgkit.from_string(df.render(), file,
                                   options={
                                       'format': 'png',
                                       'quality': '1',
                                       'width': '500',
                                       'quiet': ''
                                   })

            df_to_png(big_data_styler, f'cluster_{country}_kmeans_unscaled.png')

            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            scaled_points = scaler.fit_transform(points)

            big_data_result = big_data_selected.copy()
            cl_names = []

            for n_cl in n_clust:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=n_cl, init='random', random_state=1)
                km = kmeans.fit(scaled_points)

                clusters_id = kmeans.predict(scaled_points)

                cl_name = f'scaled n={n_cl}'
                cl_names.append(cl_name)
                cl_names = list(dict.fromkeys(cl_names))
                big_data_result[cl_name] = clusters_id

            big_data_result = big_data_result[cl_names].sort_values(cl_names[2])
            big_data_result.columns.rename('kMeans', inplace=True)
            cl_results.append(big_data_result.copy())

            import seaborn as sns
            cm = sns.light_palette("green", as_cmap=True)
            big_data_styler = big_data_result.style.background_gradient(cmap='viridis')

            def df_to_png(df, file):
                import imgkit
                imgkit.from_string(df.render(), file,
                                   options={
                                       'format': 'png',
                                       'quality': '100',
                                       'width': '830',
                                       'quiet': '',
                                   })

            df_to_png(big_data_styler, f'cluster_{country}_kmeans.png')

            big_data_result = big_data_selected.copy()
            cl_names = []

            epss = [1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6]
            for eps in epss:
                from sklearn.cluster import DBSCAN
                db = DBSCAN(eps=eps, min_samples=1).fit(scaled_points)

                cl_name = f'scaled eps={eps}'
                cl_names.append(cl_name)
                big_data_result[cl_name] = db.labels_

            big_data_result = big_data_result[cl_names].sort_values(cl_names[6])
            big_data_result.columns.rename('DBSCAN', inplace=True)
            cl_results.append(big_data_result.copy())

            import seaborn as sns
            cm = sns.light_palette("green", as_cmap=True)
            big_data_styler = big_data_result.style.background_gradient(cmap='viridis')

            def df_to_png(df, file):
                import imgkit
                imgkit.from_string(df.render(), file,
                                   options={
                                       'format': 'png',
                                       'quality': '100',
                                       'width': '830',
                                       'quiet': '',
                                   })

            df_to_png(big_data_styler, f'cluster_{country}_db.png')

            big_data_result = big_data_selected.copy()
            cl_names = []

            n_clust = [2, 3, 4, 5
                       # ,6 , 7, 8
                       ]

            for n_cl in n_clust:
                from sklearn.cluster import SpectralClustering
                model = SpectralClustering(n_clusters=n_cl, affinity='rbf',
                                           assign_labels='kmeans')

                cl_name = f'scaled n={n_cl}'
                cl_names.append(cl_name)
                big_data_result[cl_name] = model.fit_predict(scaled_points)

            big_data_result = big_data_result[cl_names].sort_values(cl_names[1])
            big_data_result.columns.rename('Spectral', inplace=True)
            cl_results.append(big_data_result.copy())

            import seaborn as sns
            cm = sns.light_palette("green", as_cmap=True)
            big_data_styler = big_data_result.style.background_gradient(cmap='viridis')

            def df_to_png(df, file):
                import imgkit
                imgkit.from_string(df.render(), file,
                                   options={
                                       'format': 'png',
                                       'quality': '100',
                                       'width': '830',
                                       'quiet': '',
                                   })

            df_to_png(big_data_styler, f'cluster_{country}_spe.png')

            big_data_result = big_data_selected.copy()
            cl_names = []

            distances = [1.4, 1.6, 1.7, 1.8, 3, 4]

            for dist in distances:
                from sklearn.cluster import AgglomerativeClustering
                agglomerative = AgglomerativeClustering(distance_threshold=dist, n_clusters=None) \
                    .fit(scaled_points)
                agglomerative.labels_

                cl_name = f'scaled - distance={dist}'
                cl_names.append(cl_name)
                big_data_result[cl_name] = agglomerative.labels_

            big_data_result = big_data_result[cl_names]
            big_data_result.columns.rename('agglomerative', inplace=True)
            cl_results.append(big_data_result.copy())

            import seaborn as sns
            cm = sns.light_palette("green", as_cmap=True)
            big_data_styler = big_data_result.style.background_gradient(cmap='viridis')

            def df_to_png(df, file):
                import imgkit
                imgkit.from_string(df.render(), file,
                                   options={
                                       'format': 'png',
                                       'quality': '100',
                                       'width': '830',
                                       'quiet': '',
                                   })

            df_to_png(big_data_styler, f'cluster_{country}_agg.png')

        async def run(self):
            print(f"Searching...!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"Countries:")
            print(self.agent.config['countries'])

            await self.pre_analysis()
            await self.clustering()

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
