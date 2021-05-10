from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.auxiliary import string_to_list
from spade_proto.pattern_seeker import PatternSeeker


class CorrelationSeeker(Agent):
    config = []
    first_config = {}

    class InformBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            msg = Message(to="raport_generator@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = f"Hello World from {self.agent.jid}"  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    # create an agent from within anagent
    class CreatePatternSeekerBehav(OneShotBehaviour):
        async def on_start(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Creating new Pattern Seeker agent behaviour . . .")

        async def run(self):
            for i in range(6):
                for j in range(6):
                    if i == j:
                        continue
                    print(f'config {self.agent.config}')
                    actor1 = self.agent.config[i]
                    actor2 = self.agent.config[j]
                    self.agent.first_config = {'actors': {'actor1': actor1, 'actor2': actor2}}
                    agent = PatternSeeker(f"pattern_seeker_{actor1}_{actor2}@localhost", "RADiance89")
                    # This start is inside an async def, so it must be awaited
                    await agent.start(auto_register=True)
                    self.agent.add_behaviour(self.agent.SendConfigBehav())

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: running")

            msg = await self.receive(timeout=100)  # wait for a message for 10 seconds
            if msg:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = string_to_list(msg.body)
                    self.agent.add_behaviour(self.agent.CreatePatternSeekerBehav())
            else:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Did not received any message after 10 seconds")
                self.kill()

    class SendConfigBehav(OneShotBehaviour):

        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            print(self.agent.first_config)
            msg = Message(to=f"pattern_seeker_{self.agent.first_config['actors']['actor1']}_{self.agent.first_config['actors']['actor2']}@localhost")  # Instantiate the message
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

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
        self.add_behaviour(self.InformBehav())
