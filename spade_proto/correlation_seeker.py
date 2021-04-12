from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.pattern_seeker import PatternSeeker


class CorrelationSeeker(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to="me@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = f"Hello World from {self.agent.jid}"  # Set the message content

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    # create an agent from within anagent
    class CreatePatternSeekerBehav(OneShotBehaviour):
        async def on_start(self):
            print(f"Creating new Pattern Seeker agent behaviour . . .")

        async def run(self):
            agent = PatternSeeker("me2@localhost", "RADiance89")
            # This start is inside an async def, so it must be awaited
            await agent.start(auto_register=False)

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print(f"{self.agent.jid}: Message received with content: {msg.body}")
            else:
                print("Did not received any message after 10 seconds")
                self.kill()

    async def setup(self):
        print(f"Correlation Seeker {self.jid} agent starting . . .")
        self.add_behaviour(self.InformBehav())
        self.add_behaviour(self.CreatePatternSeekerBehav())
        self.add_behaviour(self.RecvBehav())