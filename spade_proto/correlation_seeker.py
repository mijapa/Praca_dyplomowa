import itertools
from io import StringIO

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.auxiliary import string_to_list
from spade_proto.pattern_seeker_connection_strength import PatternSeeker

import pandas as pd

from spade_proto.pattern_seeker_cooperate import PatternSeekerCooperate
from spade_proto.pattern_seeker_cooperate_numMen30 import PatternSeekerCooperateNumMen30
from spade_proto.pattern_seeker_fight import PatternSeekerFight
from spade_proto.pattern_seeker_fight_vs_all import PatternSeekerFightVsAll
from spade_proto.pattern_seeker_power_client import PatternSeekerPowerClient


class CorrelationSeeker(Agent):
    config = []
    first_config = {}
    symmetry_results = pd.DataFrame()
    #
    # class InformBehav(OneShotBehaviour):
    #     async def run(self):
    #         print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
    #         msg = Message(to="raport_generator@localhost")  # Instantiate the message
    #         msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
    #         msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
    #         msg.set_metadata("language", "OWL-S")  # Set the language of the message content
    #         msg.body = self.agent.symmetry_results.to_string()  # Set the message content
    #
    #         await self.send(msg)
    #         print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")
    #
    #         # set exit_code for the behaviour
    #         self.exit_code = "Job Finished!"

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

                agent = PatternSeekerPowerClient(f"pattern_seeker_power_client_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_power_client_{self.agent.first_config['actors']['actor1']}_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

                agent = PatternSeekerFight(f"pattern_seeker_fight_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_fight_{self.agent.first_config['actors']['actor1']}"
                       f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

                agent = PatternSeekerCooperate(f"pattern_seeker_cooperate_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_cooperate_{self.agent.first_config['actors']['actor1']}"
                       f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

                # agent = PatternSeekerFightVsAll(f"pattern_seeker_fight_vs_all_{actor1}_{actor2}@localhost", "RADiance89")
                # # This start is inside an async def, so it must be awaited
                # await agent.start(auto_register=True)
                #
                # # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # # print(self.agent.first_config)
                # msg = Message(
                #     to=f"pattern_seeker_fight_vs_all_{self.agent.first_config['actors']['actor1']}"
                #        f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                # msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                # msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                # msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                # print(f'first_config {self.agent.first_config}')
                # msg.body = self.agent.first_config.__str__()  # Set the message content
                # await self.send(msg)

                agent = PatternSeekerCooperateNumMen30(f"pattern_seeker_cooperate_nummen30_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_cooperate_nummen30_{self.agent.first_config['actors']['actor1']}"
                       f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: running")

            timeout = 25
            msg = await self.receive(timeout=timeout)  # wait for a message for 5 seconds
            if msg:
                # print(f"{self.agent.jid}: {self.__class__.__name__}: Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = string_to_list(msg.body)
                    self.agent.add_behaviour(self.agent.CreatePatternSeekerBehav())
                if msg.metadata["ontology"] == 'symmetry_results':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: SYMMETRY RESULTS")
                    # print(f"{self.agent.jid}: {self.__class__.__name__}: msg.body: {msg.body}")

                    res = pd.read_json(msg.body, orient='table')

                    # print(f"{self.agent.jid}: {self.__class__.__name__}: res: {res}")

                    if self.agent.symmetry_results.empty:
                        self.agent.symmetry_results = res
                    else:
                        self.agent.symmetry_results = pd.concat([self.agent.symmetry_results, res])
                        # print(self.agent.symmetry_results)

            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: "
                      f"Did not received any message after {timeout} seconds")
                self.agent.add_behaviour(self.agent.SendResultsBehav())
                f = open("res.json", "w")
                f.write(self.agent.symmetry_results.to_json(orient='table'))
                f.close()
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

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
