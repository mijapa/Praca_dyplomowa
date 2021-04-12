import asyncio

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from spade_proto.correlation_seeker import CorrelationSeeker


class RaportGenerator(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counter = 0

        async def run(self):
            print("Counter: {}".format(self.counter))
            self.counter += 1
            if self.counter > 3:
                self.kill(exit_code=10)
                return
            await asyncio.sleep(1)

        async def on_end(self):
            print("Behaviour finished with exit code {}.".format(self.exit_code))

    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to="me1@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = "Hello World"  # Set the message content

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviou

    # create an agent from within anagent
    class CreateCorrelationSeekerBehav(OneShotBehaviour):
        seeker_jid = 'me1@localhost'

        async def on_start(self):
            print("Creating new Correlation Seeker agent behaviour . . .")

        async def run(self):
            agent = CorrelationSeeker(self.seeker_jid, "RADiance89")
            # This start is inside an async def, so it must be awaited
            await agent.start(auto_register=False)

    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Message received with content: {}".format(msg.body))
                self.agent.add_behaviour(self.agent.InformBehav())
            else:
                print("Did not received any message after 10 seconds")

    async def setup(self):
        print(f"Raport Generator {self.jid} agent starting . . .")
        self.my_behav = self.MyBehav()
        self.add_behaviour(self.my_behav)
        self.add_behaviour(self.CreateCorrelationSeekerBehav())
        self.add_behaviour(self.RecvBehav())