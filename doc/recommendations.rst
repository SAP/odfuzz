Recommendations
===============

This chapter contains a list of best practices and recommendations based on previous observations from running the fuzzer on various OData services.

Time of an execution
--------------------

ODfuzz has to run for a long time in order to obtain good results. The longest is the fuzzer running, the higher is a probability of triggering hidden errors. On the other hand, it is not always suitable to let the fuzzer run for 5 days to test a service which contains 2 entity sets. We are assuming that a person who runs the fuzzer have a minimal knowledge of the architecture and the tested OData service. In the configuration file, there are items where you can set a number of requests which have to be generated per property. That is the number of requests which are used for establishing an initial population in terms of genetic algorithms. After some period of time, the mutation shows a better output as well. It is recommended to let the fuzzer run for two times longer that it took to establish the population.

Concurrency
-----------

Requests can be sent to the server concurrently. However, some servers do not support a high number of concurrent connections. ODfuzz uses cached pool of connections tha is kept alive at a given time. A maximum size of the pool is configurable via main configuration file (used with the option --fuzzer-config). Users should know a maximum number of viable connections before running the fuzzer. Otherwise, warnings and errors are produced while dispatching a chunk of queries.

Restrictions
------------

Restrictions can significantly reduce a state space search. ODfuzz will not generate queries which are targeting entities that do not implement some methods or return HTTP 500 as a response by default. The fuzzer tries to test entities which are used in production and are used on daily basis. Restrictions are defined by a user. Also, this user has to have a minimum knowledge of a tested OData service too.
