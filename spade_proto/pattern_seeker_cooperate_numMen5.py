import os
from ast import literal_eval

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

import pandas as pd
import matplotlib.pyplot as plt

from spade_proto.auxiliary import authenticate_google_cloud, perform_query, string_to_list, create_symmetry_figure, \
    create_fight_figure, create_cooperate_figure, create_cooperate_nummen5_figure, get_data, calculate_percentage


class PatternSeekerCooperateNumMen5(Agent):
    config = []

    class SendResultsBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="correlation_seeker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "results")  # Set the ontology of the message content
            msg.set_metadata("type", "cooperate mentions >=5")  # Set the ontology of the message content
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
            granulation = self.agent.config['granulation']

            ac1ac2 = await self.calculate_cooperate_nummen5_percentage(actor1, actor2, granulation)
            ac2ac1 = await self.calculate_cooperate_nummen5_percentage(actor2, actor1, granulation)

            symmetry = ac1ac2.append(ac2ac1)
            create_cooperate_nummen5_figure(symmetry, actor1, actor2, granulation)

            self.agent.symmetry = symmetry

            self.agent.add_behaviour(self.agent.SendResultsBehav())

        async def calculate_cooperate_nummen5_percentage(self, actor1, actor2, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Calculating cooperate percentage {actor1}-{actor2}")
            QUERY = (f"""SELECT
  MonthYear,
  COUNT(*) AS Count,
  Actor2CountryCode
FROM
  `gdelt-bq.gdeltv2.events`
WHERE
  Year >= 2015
  AND Year <= 2020
  AND Actor1CountryCode = "{actor1}"
  AND EventRootCode = "03"
  AND NumMentions >= 5
GROUP BY
  MonthYear,
  Actor2CountryCode""")

            ac1monthyear = await get_data(self, QUERY)
            return await calculate_percentage(ac1monthyear, actor2, granulation,
                                              name='Cooperate',
                                              name_string=f'{actor2} with {actor1}')

        async def on_end(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Behaviour finished with exit code {self.exit_code}.")
