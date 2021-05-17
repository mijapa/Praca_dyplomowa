import asyncio

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from spade_proto.auxiliary import load_config_from_file, change_country_names_to_codes
from spade_proto.correlation_seeker import CorrelationSeeker

from io import StringIO
import pandas as pd


class RaportGenerator(Agent):
    correlation_seekers = []
    results = pd.DataFrame()

    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print(f"{self.agent.jid}: Starting behaviour . . .")
            self.counter = 0
            config = load_config_from_file()
            print(config)

        async def run(self):
            print(f"{self.agent.jid}: Counter: {self.counter}")
            self.counter += 1
            if self.counter > 3:
                self.kill(exit_code=10)
                return
            await asyncio.sleep(1)

        async def on_end(self):
            print(f"{self.agent.jid}: Behaviour finished with exit code {self.exit_code}.")

    class InformBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: InformBehav running")
            msg = Message(to="correlation_seeker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = "Hello World"  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviou

    # create an agent from within anagent
    class CreateCorrelationSeekerBehav(OneShotBehaviour):
        seeker_jid = 'correlation_seeker@localhost'

        async def on_start(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Creating new Correlation Seeker agent behaviour . . .")

        async def run(self):
            agent = CorrelationSeeker(self.seeker_jid, "RADiance89")
            # This start is inside an async def, so it must be awaited
            await agent.start(auto_register=True)
            self.agent.add_behaviour(self.agent.SendConfigBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: RecvBehav running")

            msg = await self.receive(timeout=20)  # wait for a message for 10 seconds
            if msg:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Message received.")
                if msg.metadata["ontology"] == 'results':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: RESULTS")
                    res = pd.read_csv(StringIO(msg.body))
                    self.agent.results = pd.concat([self.agent.results, res])
            else:
                print(f"{self.agent.jid}: Did not received any message after 10 seconds")
                self.agent.add_behaviour(self.agent.GeneratePdfBehav())
                self.kill()

    class SendConfigBehav(OneShotBehaviour):
        correlation_seekers = ['jeden']

        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: {self.__class__.__name__} running")
            msg = Message(to="correlation_seeker@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "config")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            config = load_config_from_file()
            config = change_country_names_to_codes(config)
            print(config.__str__())
            msg.body = config.__str__()  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviou

    class GeneratePdfBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: {self.__class__.__name__} running")

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)
        self.add_behaviour(self.CreateCorrelationSeekerBehav())
        self.add_behaviour(self.RecvBehav())
