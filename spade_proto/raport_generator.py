import asyncio
import json
import os

from fpdf import FPDF
from pylatex import Document, Section
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from spade_proto.PDF import PDF
from spade_proto.auxiliary import load_config_from_file, change_country_names_to_codes, create_symmetry_figure
from spade_proto.correlation_seeker import CorrelationSeeker

from io import StringIO
import pandas as pd


class RaportGenerator(Agent):
    correlation_seekers = []
    symmetry_results = pd.DataFrame()

    # class MyBehav(CyclicBehaviour):
    #     async def on_start(self):
    #         print(f"{self.agent.jid}: Starting behaviour . . .")
    #         self.counter = 0
    #         config = load_config_from_file()
    #         print(config)
    #
    #     async def run(self):
    #         print(f"{self.agent.jid}: Counter: {self.counter}")
    #         self.counter += 1
    #         if self.counter > 3:
    #             self.kill(exit_code=10)
    #             return
    #         await asyncio.sleep(1)
    #
    #     async def on_end(self):
    #         print(f"{self.agent.jid}: Behaviour finished with exit code {self.exit_code}.")

    # class InformBehav(OneShotBehaviour):
    #     async def run(self):
    #         print(f"{self.agent.jid}: InformBehav running")
    #         msg = Message(to="correlation_seeker@localhost")  # Instantiate the message
    #         msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
    #         msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
    #         msg.set_metadata("language", "OWL-S")  # Set the language of the message content
    #         msg.body = "Hello World"  # Set the message content
    #
    #         await self.send(msg)
    #         print(f"{self.agent.jid}: Message sent!")
    #
    #         # set exit_code for the behaviour
    #         self.exit_code = "Job Finished!"
    #
    #         # stop agent from behaviou

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

            timeout = 60
            msg = await self.receive(timeout=timeout)  # wait for a message for 10 seconds
            if msg:
                print(f"{self.agent.jid}: {self.__class__.__name__}: Message received.")
                if msg.metadata["ontology"] == 'symmetry_results':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: RESULTS")
                    res = pd.read_json(msg.body, orient='table')
                    print(f"{self.agent.jid}: {self.__class__.__name__}: res: {res}")
                    if self.agent.symmetry_results.empty:
                        self.agent.symmetry_results = res
                    else:
                        self.agent.symmetry_results = pd.concat([self.agent.symmetry_results, res])

            else:
                print(f"{self.agent.jid}: Did not received any message after {timeout} seconds")
                self.agent.add_behaviour(self.agent.GenerateFigures())
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
            config['countries'] = change_country_names_to_codes(config['countries'])
            print(config)
            msg.body = json.dumps(config)  # Set the message content

            await self.send(msg)
            print(f"{self.agent.jid}: {self.__class__.__name__}: Message sent!")

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

            # stop agent from behaviou

    class GenerateFigures(OneShotBehaviour):
        async def run(self):
            # print(f"{self.agent.jid}: {self.__class__.__name__}: {self.agent.symmetry_results}")
            # create_symmetry_figure()
            symmetry_results = self.agent.symmetry_results
            # print(symmetry_results)
            # connections = symmetry_results['                         Percentage']['Connection'].drop_duplicates()
            # for con in connections:
            #     condf = symmetry_results.iloc[symmetry_results['                         Percentage']['Connection'] == con]
            #     print(f'{con} :condf: {condf}')
            self.agent.add_behaviour(self.agent.GeneratePdfBehav())

    class GeneratePdfBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: {self.__class__.__name__} running")
            pdf = PDF()
            pdf.set_title('Raport')
            pdf.set_author('Michal Patyk')

            pdf.add_chapter(1, 'Symmetry analyse')
            fig_dir = 'figures/symmetry'

            with os.scandir(f'{fig_dir}/') as entries:
                for entry in entries:
                    name = entry.name
                    if name.endswith(".png"):
                        pdf.add_image(f'{fig_dir}/{name}', width=180)

            pdf.add_chapter(2, 'Power-client analyse')
            fig_dir = 'figures/power-client'

            with os.scandir(f'{fig_dir}/') as entries:
                for entry in entries:
                    name = entry.name
                    if name.endswith(".png"):
                        pdf.add_image(f'{fig_dir}/{name}', width=180)

            pdf.add_chapter(3, 'Pairwise correlation')
            fig_dir = 'figures/pairwise_correlation'

            with os.scandir(f'{fig_dir}/') as entries:
                for entry in entries:
                    name = entry.name
                    if name.endswith(".png"):
                        pdf.add_image(f'{fig_dir}/{name}', width=180)

            pdf.output('Automated PDF Report.pdf')

            doc = Document('basic')
            with doc.create(Section('A section')):
                doc.append('Also some crazy characters: $&#{}')

            doc.generate_pdf(clean_tex=False)
            # doc.generate_tex('basic.tex')

        async def on_end(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Behaviour finished with exit code {self.exit_code}.")

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        # self.my_behav = self.MyBehav()
        # self.add_behaviour(self.my_behav)
        self.add_behaviour(self.CreateCorrelationSeekerBehav())
        self.add_behaviour(self.RecvBehav())
