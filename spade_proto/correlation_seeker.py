import itertools
import json

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sn
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

from spade_proto.pattern_seeker_connection_strength import PatternSeeker
from spade_proto.pattern_seeker_cooperate import PatternSeekerCooperate
from spade_proto.pattern_seeker_cooperate_numMen5 import PatternSeekerCooperateNumMen5


class CorrelationSeeker(Agent):
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
            config_countries = self.agent.config['countries']
            length = len(config_countries)
            combi = set(itertools.combinations(range(length), 2))
            # print(combi)
            for i, j in combi:
                # print(i, j)
                # print(f'config {config_countries}')
                actor1 = config_countries[i]
                actor2 = config_countries[j]
                self.agent.first_config = {'actors': {'actor1': actor1, 'actor2': actor2},
                                           'granulation': self.agent.config['granulation']
                                           }

                name = f"pattern_seeker_{actor1}_{actor2}@localhost"
                agent = PatternSeeker(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)

                # name = f"pattern_seeker_power_client_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerPowerClient(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_fight_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerFight(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                name = f"pattern_seeker_cooperate_{actor1}_{actor2}@localhost"
                agent = PatternSeekerCooperate(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)
                #
                # # name = f"pattern_seeker_fight_vs_all_{actor1}_{actor2}@localhost"
                # # agent = PatternSeekerFightVsAll(name, "RADiance89")
                # # await self.start_agent_and_send_config(agent, name)
                #
                name = f"pattern_seeker_cooperate_nummen5_{actor1}_{actor2}@localhost"
                agent = PatternSeekerCooperateNumMen5(name, "RADiance89")
                await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_cooperate_times_nummen_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerCooperateTimesNumMen(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)
                #
                # name = f"pattern_seeker_cooperate_times_goldstein_{actor1}_{actor2}@localhost"
                # agent = PatternSeekerCooperateTimesGoldstein(name, "RADiance89")
                # await self.start_agent_and_send_config(agent, name)


        async def start_agent_and_send_config(self, agent, name):
            # This start is inside an async def, so it must be awaited
            await agent.start(auto_register=True)
            # print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            # print(self.agent.first_config)
            msg = Message(to=name)  # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "config")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")  # Set the language of the message content
            print(f'first_config {self.agent.first_config}')
            msg.body = json.dumps(self.agent.first_config)  # Set the message content
            await self.send(msg)

    class RecvBehav(CyclicBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: running")

            timeout = 10
            msg = await self.receive(timeout=timeout)  # wait for a message for 5 seconds
            if msg:
                # print(f"{self.agent.jid}: {self.__class__.__name__}: Message received with content: {msg.body}")
                if msg.metadata["ontology"] == 'config':
                    print(f"{self.agent.jid}: {self.__class__.__name__}: CONFIG")
                    self.agent.config = json.loads(msg.body)
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
                    f = open(f"results_{res} {self.agent.config['granulation']}.json", "w")
                    f.write(results[res].to_json(orient='table'))
                    f.close()
                self.agent.add_behaviour(self.agent.SeekSimpleCorrelationBehav())
                self.agent.add_behaviour(self.agent.SeekComplexCorrelationBehav())
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
            msg.body = json.dumps(self.agent.first_config)  # Set the message content

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

    class SeekSimpleCorrelationBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            granulation = self.agent.config['granulation']

            results = self.agent.results
            for res_name in results:
                result = results[res_name]
                resun = result.unstack()[result.columns[0]]
                # print(resun)
                await self.create_global_correlation_figures(res_name, resun, granulation)

                await self.create_autocorrelation_figures(res_name, resun, granulation)

                await self.create_pairwise_rolling_correlation_figures(res_name, resun, granulation)

                await self.create_cross_correlation_figures(res_name, resun, granulation)

            # set exit_code for the behaviour
            self.exit_code = "Job Finished!"

        async def create_cross_correlation_figures(self, res_name, resun, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Create Pearson cross correlation figures")
            import numpy as np
            df = resun

            def crosscorr(datax, datay, lag=0, wrap=False):
                """ Lag-N cross correlation.
                Shifted data filled with NaNs

                Parameters
                ----------
                lag : int, default 0
                datax, datay : pandas.Series objects of equal length
                Returns
                ----------
                crosscorr : float
                """
                if wrap:
                    shiftedy = datay.shift(lag)
                    shiftedy.iloc[:lag] = datay.iloc[-lag:].values
                    return datax.corr(shiftedy)
                else:
                    return datax.corr(datay.shift(lag))

            length = len(resun.columns)
            combi = set(itertools.combinations(range(length), 2))
            # print(combi)
            for i, j in combi:
                connection_A = resun.columns[i]
                connection_B = resun.columns[j]

                d1 = df[connection_A]
                d2 = df[connection_B]

                months_lag = 10
                rs = [crosscorr(d1, d2, lag) for lag in range(-int(months_lag - 1), int(months_lag))]
                offset = np.floor(len(rs) / 2) - np.argmax(rs)
                f, ax = plt.subplots(figsize=(15, 6))
                ax.plot(rs)
                ax.axvline(np.ceil(len(rs) / 2), color='k', linestyle='--', label='Center')
                ax.axvline(np.argmax(rs), color='r', linestyle='--', label='Peak synchrony')
                title = f"{res_name}".capitalize() + \
                        f" {connection_A} and {connection_B} Pearson cross correlation 2015-2020"
                ax.set(title=f'{title}\n{connection_A} leads <> {connection_B} leads', xlabel='Offset',
                       ylabel='Pearson r')
                ax.set_xticklabels([int(item - months_lag) for item in ax.get_xticks()]);
                plt.legend()
                ax.figure.set_size_inches(15, 6)
                ax.set(ylabel='Correlation')

                path = f'figures/auto_seek/{res_name}/cross_correlation'
                import pathlib
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                plt.savefig(f'{path}/{title} {granulation}.png', bbox_inches='tight')
                # plt.show()
                plt.close('all')

        async def create_pairwise_rolling_correlation_figures(self, res_name, resun, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Create Pearson pairwise correlation figures")
            import itertools
            # Set window size to compute moving window synchrony.
            window_length = 6
            # Interpolate missing data.
            df_interpolated = resun.interpolate()
            # Compute rolling window synchrony
            length = len(resun.columns)
            combi = set(itertools.combinations(range(length), 2))
            # print(combi)
            for i, j in combi:
                connection_A = resun.columns[i]
                connection_B = resun.columns[j]
                rolling_r = df_interpolated[connection_A].rolling(window=window_length, center=True) \
                    .corr(df_interpolated[connection_B])

                g = rolling_r.plot(style='r-')
                title = f"{res_name}".capitalize() + \
                        f" {connection_A} and {connection_B} Pearson correlation with {window_length} months rolling 2015-2020"
                g.set_title(title)
                g.figure.set_size_inches(15, 6)
                g.set(ylabel='Correlation')

                g2 = g.twinx()

                g2 = resun[[connection_A, connection_B]].rolling(window=window_length, center=True).median().plot(
                    ax=g2)

                g2.set(ylabel='Percentage')

                plt.legend([g.get_lines()[0], g2.get_lines()[1], g2.get_lines()[0]],
                           ['Correlation', connection_A, connection_B])
                path = f'figures/auto_seek/{res_name}/pairwise_rolling_correlation'
                import pathlib
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                plt.savefig(f'{path}/{title} {granulation}.png', bbox_inches='tight')
                # plt.show()
                plt.close('all')

        async def create_autocorrelation_figures(self, res_name, resun, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Create Pearson autocorrelation figures")
            for connection_name in resun.columns:
                g = pd.plotting.autocorrelation_plot(resun[connection_name])
                title = f"{res_name}".capitalize() + " " \
                                                     f"{connection_name}".capitalize() + \
                        f" autocorrelation 2015-2020"
                g.set_title(title)
                g.figure.set_size_inches(15, 6)
                path = f'figures/auto_seek/{res_name}/autocorrelation'
                import pathlib
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                plt.savefig(f'{path}/{title} {granulation}.png', bbox_inches='tight')
                # plt.show()
                plt.close('all')

        async def create_global_correlation_figures(self, res_name, resun, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Create global Pearson correlation figures")
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
                plt.savefig(f'{path}/{title} {granulation}.png', bbox_inches='tight')
                # plt.show()
                plt.close('all')

    class SeekComplexCorrelationBehav(OneShotBehaviour):
        async def run(self):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Running")
            res_name = 'all'
            granulation = self.agent.config['granulation']
            resun = self.agent.results

            await self.create_global_correlation_figures(res_name, resun, granulation)

        async def create_global_correlation_figures(self, res_name, resun, granulation):
            print(f"{self.agent.jid}: {self.__class__.__name__}: Create global Pearson correlation figures")
            # methods = ['pearson', 'kendall', 'spearman']
            # for method in methods:
            #     g = sn.heatmap(resun.corr(method=method), annot=True)
            #     title = f"{res_name}".capitalize() + " " \
            #                                          f"{method}".capitalize() + \
            #             f" correlation 2015-2020"
            #     g.set_title(title)
            #     g.figure.set_size_inches(15, 6)
            #     path = f'figures/auto_seek/{res_name}/correlation'
            #     import pathlib
            #     pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            #     plt.savefig(f'{path}/{title} {granulation}.png', bbox_inches='tight')
            #     # plt.show()
            #     plt.close('all')

    async def setup(self):
        print(f"{self.jid}: Agent starting . . .")
        self.add_behaviour(self.RecvBehav())
