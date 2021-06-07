import itertools
from io import StringIO

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.auxiliary import string_to_list
from spade_proto.pattern_seeker_connection_strength import PatternSeeker

import pandas as pd

from spade_proto.pattern_seeker_cooperate import PatternSeekerCooperate
from spade_proto.pattern_seeker_cooperate_numMen5 import PatternSeekerCooperateNumMen5
from spade_proto.pattern_seeker_cooperate_times_goldstein import PatternSeekerCooperateTimesGoldstein
from spade_proto.pattern_seeker_cooperate_times_mentions import PatternSeekerCooperateTimesNumMen
from spade_proto.pattern_seeker_fight import PatternSeekerFight
from spade_proto.pattern_seeker_fight_vs_all import PatternSeekerFightVsAll
from spade_proto.pattern_seeker_power_client import PatternSeekerPowerClient


class CorrelationSeeker(Agent):
    config = []
    first_config = {}
    results = {}
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

                agent = PatternSeekerCooperateNumMen5(f"pattern_seeker_cooperate_nummen5_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_cooperate_nummen5_{self.agent.first_config['actors']['actor1']}"
                       f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

                agent = PatternSeekerCooperateTimesNumMen(f"pattern_seeker_cooperate_times_nummen_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_cooperate_times_nummen_{self.agent.first_config['actors']['actor1']}"
                       f"_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "config")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")  # Set the language of the message content
                print(f'first_config {self.agent.first_config}')
                msg.body = self.agent.first_config.__str__()  # Set the message content
                await self.send(msg)

                agent = PatternSeekerCooperateTimesGoldstein(f"pattern_seeker_cooperate_times_goldstein_{actor1}_{actor2}@localhost", "RADiance89")
                # This start is inside an async def, so it must be awaited
                await agent.start(auto_register=True)

                # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
                # print(self.agent.first_config)
                msg = Message(
                    to=f"pattern_seeker_cooperate_times_goldstein_{self.agent.first_config['actors']['actor1']}"
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
                if msg.metadata["ontology"] == 'results':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: RESULTS")
                    # print(f"{self.agent.jid}: {self.__class__.__name__}: msg.body: {msg.body}")

                    res = pd.read_json(msg.body, orient='table')

                    result_type = msg.metadata["type"]
                    try:
                        self.agent.results[result_type] = pd.concat([self.agent.results[result_type], res])
                    except KeyError:
                        self.agent.results[result_type] = res


            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: "
                      f"Did not received any message after {timeout} seconds")
                # self.agent.add_behaviour(self.agent.SendResultsBehav())
                # todo: send results to raport generator
                results = self.agent.results
                for res in results:
                    f = open(f"results_{res}.json", "w")
                    f.write(results[res].to_json(orient='table'))
                    f.close()
                self.agent.add_behaviour(self.agent.SeekCorrelationBehav())
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

    class SeekCorrelationBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")

            import seaborn as sn
            import matplotlib.pyplot as plt
            results = self.agent.results
            for res_name in results:
                resun = results[res_name].unstack()['Percentage']
                methods = ['pearson', 'kendall', 'spearman']
                for method in methods:
                    g = sn.heatmap(resun.corr(method=method), annot=True)
                    title = f"{res_name}".capitalize() + " " \
                            f"{method}".capitalize() + \
                            f" correlation 2015-2020"
                    g.set_title(title)
                    g.figure.set_size_inches(15, 6)
                    path = f'figures/auto_seek/{res_name}/correlation'
                    import pathlib
                    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                    plt.savefig(f'{path}/{title}.png', bbox_inches='tight')
                    plt.show()
                    plt.close('all')

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
