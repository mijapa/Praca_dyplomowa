# from notebook Power-Client analysis
import os

import pandas as pd
import seaborn as sns

from spade_proto.auxiliary import get_data

sns.set_style("whitegrid")
import matplotlib.pyplot as plt


def get_eventcodes():
    eventcodes = pd.read_csv('../cameo.csv', header=0, dtype=str, sep=' *, *', engine='python')
    return eventcodes


def add_event_descriptions(s):
    eventcodes = get_eventcodes()
    left = None
    if 'EventRootCode' in s.columns:
        left = 'EventRootCode'
    if 'EventBaseCode' in s.columns:
        left = 'EventBaseCode'
    return s.merge(eventcodes.set_index('CAMEOEVENTCODE'), left_on=left, right_on='CAMEOEVENTCODE', how='left')


async def get_data_with_event_description(QUERY, self):
    s = await get_data(self, QUERY)
    sm = add_event_descriptions(s)
    return sm


def count_to_percentage_crop(sm, n):
    events_sum = sm.Count.sum()
    smg = sm.groupby("EVENTDESCRIPTION", as_index=False).sum().sort_values(by="Count", ascending=False).head(n)
    if 'Unamed:0' in smg.index.names:
        del smg['Unnamed: 0']
    # del smg['EventRootCode']
    smg.Count = smg.Count.apply(lambda x: x / events_sum * 100)
    smg = smg.rename({'Count': 'Percentage'}, axis='columns')
    return smg


async def get_croped_data(QUERY, n):
    sm = await get_data_with_event_description(QUERY)
    smg = count_to_percentage_crop(sm, n)
    return smg


def create_palette_for_event_descriptions(event_descriptions):
    unique = event_descriptions.unique()
    palette = dict(zip(unique, sns.color_palette("Spectral", n_colors=len(unique))))
    return palette


def save_barplot(folder, name, palette, data, x):
    g = sns.barplot(data=data, x=data[x], y=data.Percentage, palette=palette)
    g.set_title(name)
    g.set_xticklabels(g.get_xticklabels(), rotation=60, ha="right")
    g.figure.set_size_inches(20, 8)
    if not os.path.exists(folder):
        os.mkdir(folder)
    plt.savefig(f'{folder}/{name}.png', bbox_inches='tight')
    plt.show()
    plt.close('all')


def update_palette_for_event_descriptions(old_palette, eventsdescription):
    update_palette = create_palette_for_event_descriptions(eventsdescription)
    update_palette.update(old_palette)
    return update_palette


def save_sum_up_relations_barplots(folder, name_with, data):
    palette = []
    for eventdescription in set(data.EVENTDESCRIPTION):
        eventdata = data[data['EVENTDESCRIPTION'] == eventdescription].sort_values(by="Percentage", ascending=False)
        name = f"{eventdescription} events 2015-2020 {name_with}"

        palette = update_palette_for_event_descriptions(palette, eventdata.Relation)
        save_barplot(folder=folder + '_event_sum_up', name=name, palette=palette, data=eventdata, x='Relation')
