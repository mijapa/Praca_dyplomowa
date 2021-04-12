from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class PatternSeeker(Agent):
    class InformBehav(OneShotBehaviour):
        async def run(self):
            print("InformBehav running")
            msg = Message(to="me1@localhost")  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            msg.body = f"Hello World from {self.agent.jid}"  # Set the message content

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

    async def setup(self):
        print(f"Correlation Seeker {self.jid} agent starting . . .")
        self.add_behaviour(self.InformBehav())