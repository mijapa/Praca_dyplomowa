import os
from ast import literal_eval

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

import pandas as pd
import matplotlib.pyplot as plt

from spade_proto.auxiliary import authenticate_google_cloud, perform_query, string_to_list, create_symmetry_figure, \
    create_power_client_figure


class PatternSeekerPowerClient(Agent):
    config = []

    class SendResultsBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="correlation_seeker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "results")  # Set the ontology of the message content
            msg.set_metadata("type", "power-client")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content

            msg.body = self.agent.symmetry.to_json(orient='table')  # Set the message content

            # print(f"{self.agent.jid}: {self.__class__.__name__}: msg.body {msg.body}")

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())

    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: RecvBehav running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print(f"{self.agent.jid}: {self.__class__.__name__}:Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = literal_eval(msg.body)
                    self.agent.add_behaviour(self.agent.AnalyseSymmetryBehav())
            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Did not received any message after 10 seconds")

    class AnalyseSymmetryBehav(OneShotBehaviour):
        clients = []

        async def on_start(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Starting behaviour . . .")
            self.clients = authenticate_google_cloud()

        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            print(f"{self.agent.jid}: {self.__class__.__name__}: {self.agent.config}")
            actor1 = self.agent.config['actors']['actor1']
            actor2 = self.agent.config['actors']['actor2']

            ac1ac2 = await self.calculate_connection_strength(actor1, actor2)
            ac2ac1 = await self.calculate_connection_strength(actor2, actor1)

            symmetry = ac1ac2.append(ac2ac1)
            create_power_client_figure(symmetry, actor1, actor2)

            self.agent.symmetry = symmetry

            self.agent.add_behaviour(self.agent.SendResultsBehav())

        async def calculate_connection_strength(self, actor1, actor2):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Calculating connection strength {actor1}-{actor2}")
            QUERY = (f"""SELECT
  MonthYear,
  COUNT(*) AS Count
FROM
  `gdelt-bq.gdeltv2.events`
WHERE
  Year >= 2015
  AND Year <= 2020
  AND Actor1CountryCode = "{actor1}"
  AND NumMentions >= 50
GROUP BY
  MonthYear""")

            ac1monthyear = await self.get_data(QUERY)

            ac1monthyear["Time"] = pd.to_datetime(ac1monthyear['MonthYear'], format='%Y%m').dt.strftime('%Y-%m')

            QUERY = (f"""SELECT
  MonthYear,
  COUNT(*) AS Count
FROM
  `gdelt-bq.gdeltv2.events`
WHERE
  Year >= 2015
  AND Year <= 2020
  AND Actor1CountryCode = "{actor2}"
  AND NumMentions >= 50
GROUP BY
  MonthYear""")

            ac2monthyear = await self.get_data(QUERY)

            ac2monthyear["Time"] = pd.to_datetime(ac1monthyear['MonthYear'], format='%Y%m').dt.strftime('%Y-%m')

            s = ac1monthyear.groupby(["Time"]).agg({'Count': 'sum'})
            t = ac2monthyear.groupby(["Time"]).agg({'Count': 'sum'})
            s['Ratio'] = s['Count'] / t['Count']
            s['Countries'] = f'{actor1} to {actor2}'
            # print(s)
            s = s.groupby(["Time", "Countries"]).agg({'Ratio': 'last'})
            # print(s)
            # g = s.unstack().plot(y='Percentage')

            # g.set(ylabel='Percentage')
            # g.set_title(f"Connection strength {actor1}-{actor2} 2015-2020")
            # g.figure.set_size_inches(20, 8)
            # plt.savefig(f'figures/{actor1}-{actor2}connection.png', bbox_inches='tight')
            # print(s)
            return s

        async def get_data(self, QUERY):
            # name = ''.join(QUERY.split())
            name = QUERY
            if not os.path.isfile(f'queries_results_auto/{name}.csv'):
                print(f"{self.agent.jid}: {self.__class__.__name__}: Local data miss. Performing query"
                      # f"\n {QUERY}"
                      )
                result = perform_query(clients=self.clients, QUERY=QUERY)
                result.to_csv(f'queries_results_auto/{name}.csv')
            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Local data hit. Reading from file"
                      # f"\n{QUERY}.csv"
                      )
                result = pd.read_csv(f'queries_results_auto/{name}.csv')
            return result

        async def on_end(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Behaviour finished with exit code {self.exit_code}.")
