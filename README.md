# Multi-agent environment for management of the process of identifying and analyzing time patterns in news about political events

Data source - CAMEO - Conflict and Mediation Event Observations - database gathering information on notes on political events.

The Agent System deals with the analysis of data found in the GDELT database. Patterns describing countries and relations between them are identified. Created rules support finding patterns.

Agent groups profiled for automatic pattern search.

## Results

### Connection strength pearson correlation 2015-2020
![Connection strength pearson correlation 2015-2020 figure](spade_proto/figures/correlation/Connection%20strength%20pearson%20correlation%202015-2020.png?raw=true?)

High correlation of opposite relations (e.g.: Russia-Poland Poland-Russia 0.9).
Negative correlation of Russia-Germany and Poland-Germany relations.

### Connection strength POL and RUS 2015-2020 1M
![Connection strength POL and RUS 2015-2020 1M figure](src/fig/POL-RUS-POL.png?raw=true)

A clear increase in Poland's interest in Russia in early 2020 - parliamentary elections in Russia.

### Connection strength DEU to POL and POL to DEU Pearson cross correlation 2015-2020

![Connection strength DEU to POL and POL to DEU Pearson cross correlation 2015-2020 figure](spade_proto/figures/cross_correlation/Connection%20strength%20DEU%20to%20POL%20and%20POL%20to%20DEU%20Pearson%20cross%20correlation%202015-2020.png?raw=true)

The increase in the strength of the connection, the importance of Germany for Poland, precedes the increase in the importance of Poland for Germany by a month.

### Results of k-means clustering
![Results of k-means clustering table](Power-Client%20pre%20analysis/cluster_pl.png?raw=true)

The most interesting results seem to be for 5 clusters, where Poland's relations with Germany, Russia and the United States were found in one cluster.

### Agglomeration clustering results - Poland
![Agglomeration clustering results dendrogram](Power-Client%20pre%20analysis/cluster_pl_agg_dendrogram.png?raw=true)

All of the first resulting clusters, visible at the bottom of the dendrogram, are consistent with actual country relationships.

### Agglomeration clustering results - Taiwan
![Agglomeration clustering results dendrogram](Power-Client%20pre%20analysis/cluster_tjw_agg_dendrogram.png?raw=true)

The dendrogram clearly shows the distinctiveness of the Taiwan-North Korea relationship from the others, which is in line with the facts of the relationship between these countries.
