import itertools
from io import StringIO

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.auxiliary import string_to_list
from spade_proto.pattern_seeker import PatternSeeker

import pandas as pd


class CorrelationSeeker(Agent):
    config = []
    first_config = {}
    results = pd.DataFrame()

    class InformBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="raport_generator@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.agent.results.to_string()  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    class SendResultsBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="raport_generator@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "results")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.agent.results.to_string()  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    # create an agent from within anagent
    class CreatePatternSeekerBehav(OneShotBehaviour):
        async def on_start(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Creating new Pattern Seeker agent behaviour . . .")

        async def run(self):
            length = len(self.agent.config)
            combi = set(itertools.combinations(range(length), 2))
            print(combi)
            for i, j in combi:
                print(i, j)
                print(f'config {self.agent.config}')
                actor1 = self.agent.config[i]
                actor2 = self.agent.config[j]
                self.agent.first_config = {'actors': {'actor1': actor1, 'actor2': actor2}}
                agent = PatternSeeker(f"pattern_seeker_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_{self.agent.first_config['actors']['actor1']}_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content

                await self.send(msg)

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                # print(f"{self.agent.jid}: {self.__class__.__name__}: Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = string_to_list(msg.body)
                    self.agent.add_behaviour(self.agent.CreatePatternSeekerBehav())
                if msg.metadata["ontology"] == 'results':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: RESULTS")
                    res = pd.read_csv(StringIO(msg.body))
                    self.agent.results = pd.concat([self.agent.results, res])
            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Did not received any message after 10 seconds")
                self.agent.add_behaviour(self.agent.SendResultsBehav())
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
            msg.body = self.agent.first_config.__str__()  # Set the message content

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
            msg.set_metadata("ontology", "results")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = self.agent.results.to_string()  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent to: {to}")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
