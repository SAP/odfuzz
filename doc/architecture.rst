Fuzzer's Architecture
#####################

Introduction
************

ODfuzz implements the evolutionary algorithm. The components of ODfuzz conform with the design of such an algorithm. At first, an initial population is established. After that, the population is evolved in each iteration and new findings are recorded. Take a look at the following pseudo-code which properly depicts the fuzzer's behavior:

::

    SEED population with random HTTP requests
    repeat
        SELECT requests which targets single endpoint
        SELECT method of generation
        if CROSSABLE
            CROSSOVER selected requests to generate new requests
            MUTATE new requests
        else
            GENERATE new requests from scratch
        DISPATCH new requests to an OData service
        ANALYZE new requests with FITNESS function based on received responses
        DELETE worst requests from the population
        SAVE fittest queries and their metadata to a database
    until SIGINT is captured
    WRITE basic stats

The pseudo-code shows principal components and methods of the fuzzer. The fuzzer's core process is precisely displayed in the following image.

.. raw:: html
   :file: fuzzer-architecture.svg

Example Runtime Behavior
************************

In this chapter, we will discuss how ODfuzz creates queries and how these queries pass through generators and mutators. Suppose we have a running OData service and the following metadata document is exposed:

::

    <edmx:DataServices>
        <Schema Namespace="NorthwindModel">
            <EntityType Name="Product">
                <Key>
                    <PropertyRef Name="ProductID"/>
                </Key>
                <Property xmlns:p8="http://schemas.microsoft.com/ado/2009/02/edm/annotation" Name="ProductID" Type="Edm.Int32" Nullable="false"/>
                <Property Name="ProductName" Type="Edm.String" Nullable="false" MaxLength="40" Unicode="true" FixedLength="false"/>
                <Property Name="SupplierID" Type="Edm.Int32" Nullable="true"/>
                <Property Name="CategoryID" Type="Edm.Int32" Nullable="true"/>
                <Property Name="QuantityPerUnit" Type="Edm.String" Nullable="true" MaxLength="20" Unicode="true" FixedLength="false"/>
                <Property Name="Discontinued" Type="Edm.Boolean" Nullable="false"/>
            </EntityType>
            <EntityType Name="Region">
                <Key>
                    <PropertyRef Name="RegionID"/>
                </Key>
                <Property Name="RegionID" Type="Edm.Int32" Nullable="false"/>
                <Property Name="RegionDescription" Type="Edm.String" Nullable="false" MaxLength="50" Unicode="true" FixedLength="true"/>
            </EntityType>
        </Schema>
        <Schema Namespace="ODataWeb.NorthWind.Model">
            <EntityContainer>
                <EntitySet Name="Products" EntityType="NorthwindModel.Product"/>
                <EntitySet Name="Regions" EntityType="NorthwindModel.Region"/>
            </EntityContainer>
        </Schema>
    </edmx:DataServices>

Then the fuzzer will do exactly these things:

1. At first, it tries to obtain a data model from the OData service. A metadata document is retrieved via HTTP GET Request. A raw XML is then parsed by PyOData. Builder creates 0-4 objects per one entity set. For sake of simplicity, let's pretend that there are not defined any restrictions and entities are not associated. Builder creates one instance for accessing single entity from an entity set (i.e. /Products(ProductId=123)) and one instance for accessing multiple entities from the entity set (i.e. /Products). In result, we get 2 objects for 2 entities. These objects contain references to another objects for permitted query options (e.g. generators of $skip, $filter, $top). The objects are added to the list of queryables and the fuzzer proceeds to the next step.
2. Now, we have initialized all necessary data for initiating the fuzzing. A seed population is established at first. The fuzzer iterates over the queryable objects and generates random query for each entity set. Number of generated requests for a single entity set is equal to *number of properties* * *number of queryable objects* * *number of urls per property (declared in configuration file)*. The fuzzer generates values only for a random subset of all available query options in each iteration (e.g. $filter=ProductName eq 'ASDF', $top=32). The generated query options are merged together and a final query is produced. Here are examples of generated queries for the entity set Products:

    Products?$filter=ProductName eq 'ASDF' or ProductName lt '123asdf' and CategoryID eq 123321123&$top=32

    Products?$filter=CategoryID eq 0 and CategoryID eq 123321123&$skip=100

    Products?$filter=ProductName eq 'ASDF' or Discontinued eq true or Discontinued eq false

    ...

    Products(ProductID=123321)?$filter=QuantityPerUnit eq 'asdfasdf' and ProductName eq '123'

    Products(ProductID=1998)?$filter=ProductName eq 'asdfasdf'

    Products(ProductID=123321)?$filter=QuantityPerUnit eq 'asdfasdf' or SupplierID lt 1111

    ...
3. A generated query is sent to the server and a response time, an HTTP status code, or an error message, are tracked in order to evaluate a quality of the generated query. A separate data class is used to store such information. This class also builds a dictionary and writes it to a database.
4. When the initial population is established, the fuzzer continues to evolve the population. There are two ways of a continuance:

    4.1 An overall score of the population is good enough to continue mutating queries (an average score is rising up).

        4.1.1 Two best queries are retrieved from two different sets of 30 queries from the database. The fuzzer picks:

            Products?$filter=CategoryID eq 0 and CategoryID eq 123321123&$skip=100

            Products?$filter=CategoryID lt 123&$top=10000

        4.1.2 Data are converted back to the dictionary from the database. Fhe fuzzer does not have references to the built queryable objects. We cannot store such references in the database. On the other hand, they can be easily restored from the stored data. In this stage, The fuzzer crossovers and mutates these two queries randomly. The output of possible combinations looks like this (only one child is generated in the iteration):

            Products?$filter=CategoryID lt 123&skip=101

            Products?$filter=Category ID lt 1233&$top=10000

            Products?$filter=CategoryID eq -1 and CategoryID eq 123321123&$skip=100

            Products?$skip=100&$top=10000

            Products?$filter=CategoryID eq 123321123&$skip=100

            ...

    4.2 An overall score of the population is not good enough (an average score is not rising up).

        4.2.1 A random queryable is chosen from the list of queryables. List of queryables is persistent in the arbitrator class, called Selector.

        4.2.1 For the corresponding queryable, there is generated a new query, like in the step no. 2.

5. New queries are again dispatched to the server, responses are evaluated, and saved to the database. Notice that only queries with a fit score are written back to the database. Otherwise, these queries are silently removed.
6. Then, the fuzzer goes back to the step no. 4. The process of fuzzing ends when a user trigger SIGINT (a keyboard interruption).

Fuzzer's Components
*******************

The fuzzer consists of these five main components:

- Builder (entities.py) - Initializes data structures that are used in further generation of HTTP requests. Builder utilizes PyOData library in order to properly classify entity sets, entity types, associations, association sets, or properties. The data structures are used across all modules.
- Selector (fuzzer.py) - Selects data and a method which will be used in next generation. Selector is used within the classic genetic loop. It decides if it is better to generate new data or to mutate existing data, based on an overall fitness score.
- Generator (fuzzer.py/generators.py/entities.py) - Generates new data based on specifications provided by a metadata document. Generator is an abstract labeling for a group of handlers and functions which are tethered together.
- Mutator (fuzzer.py/mutators.py/entities.py) - Mutates new data based on specifications provided by a metadata document. Mutator itself is an abstract labeling for a group of handlers and functions like Generator.
- Dispatcher (fuzzer.py) - Dispatches new data to an OData service. Data can be dispatched asynchronously by sending multiple requests at once. Threads will automatically collect and assign responses to the corresponding requests.

In the next few sections, there are described implementation details of each module and each component.

Builder
=======

Builder is implemented in the module :doc:`entities.py`. Builder, as an abstract class, is called from the module :doc:`fuzzer.py` which handles a fuzzing process. Builder's significance lies in the way how it encapsulates structures created by PyOData library.

First of all, it sends HTTP GET request to a specified OData service in order to obtain a metadata document (e.g. odata/svc/$metadata). The metadata document contains a definition of data model. The received response is parsed by PyOData. Builder iterates through entity sets and association sets only. Elements such as annotations, function imports are not relevant in terms of ODfuzz. Builder starts patching and adjusting parsed structure when the metadata document is correctly parsed.

.. note:: If an OData service contains invalid definition of annotations, or function imports, the behavior of ODfuzz is unchanged. However, due to fact that ODfuzz uses PyOData to parse a metadata document, we cannot proceed further in fuzzing because the library raises an exception after the first discovered error.

Every property in the entity set is updated with new attributes **generate** and **mutate**. The implementation of so called monkey patching is located in the module :doc:`monkey.py`. The monkey patching is primary utilized by the generation of requests which contain the $filter query option. Also, operators for properties like *eq*, *ne*, *le* are patched as well. After doing so, we generate new values in the following way:

.. code-block:: python

    operator = weighted_random(proprty.operators.get_all())
    operand = proprty.generate()
    string = f'$filter={proprty.name} {operator} {operand}'


Accessible Entity Sets
----------------------

Some entity sets may be associated with another entity sets. This allows us to query entities through associated sets (AssociatedEntity/Entity). Associations are always established between two entity sets. In the metadata document, there is element `<End>` which is used to describe the role between those entity sets. If an allowed multiplicity of the entity set is set to 1, or a referential constraint specify the principal role explicitly, then the entity set is principal. Principal entities are fetched from the data model based on the aforementioned specifications.

Principal entities are also the only way to query entity sets which are not accessible directly. That means that the entities require usage of associated entities in order to process requests (e.g. insertion of parameters). In Builder, a list of principal entities associated to every entity set is maintained.

Accessible entity sets are objects used for generating endpoint path in a URL:

- /EntitySet(ID=1)? - a path targeting a single entity within an entity set. Accessible keys (e.i. ID) are generated according to the types of key properties (SingleEntity).
- /EntitySet? - a classic path for entity set endpoint (MultipleEntities).
- /AssocSet(ID=1)/EntitySet? - a path targeting associated entity set (AssociatedEntities). Where AssocSet is the principal entity set.

Current implementation of ODfuzz supports just HTTP GET requests. Next sections take that into account.

Query Groups
------------

Suppose that the entity sets are endpoints for all types of queries. Builder creates multiple objects that represents a single type of the query:

1. `QueryGroupMultiple` - Targets an entity set (e.g. odata/svc/EntitySet). This group initializes generators for all related query options ($filter, $expand, $orderby, $top, $skip, search, $inlinecount) as well.
2. `QueryGroupSingle` - Targets one entity in an entity set (e.g. odata/svc/EntitySet(Id='1')). This group initializes generators for all related query options ($filter, $expand) as well.
3. `QueryGroupAssociation` - Targets a entity set via associated entity set (e.g. odata/svc/AssociatedEntity/NavigationProperty). The group is created if the multiplicity of final entity set is ranged from 0 to 1. This group initializes generators for all related query options ($filter, $expand) as well.
4. `QueryGroupAssociationSet` - Targets an entity set via associated entity set (e.g. odata/svc/AssociatedEntity/NavigationProperty). The group is created if the multiplicity of final entity set is set to infinity. This group initializes generators for all related query options ($filter, $expand, $orderby, $top, $skip, search, $inlinecount) as well.

Navigation properties are references to associated entity sets. ODfuzz can fetch a type of entity set from the navigation property thanks to PyOData.

The objects `QueryGroupMultiple`, `QueryGroupSingle`, `QueryGroupAssociation`, `QueryGroupAssociationSet` are created for every entity set if possible. If an entity set does not have defined any relations, nor does not have any references to other entity sets, Builder does not generate objects `QueryGroupAssociation` and `QueryGroupAssociationSet`.

To sum up the situation for the query groups objects:

- Each entity set is internally represented by a group of multiple objects.
- Each object targets only one entity set (one endpoint).
- Each object contains different types of generator's methods for the corresponding context.
- Each object provides a unified interface for listing and generating.

Query groups contain methods for generating accessible paths (those are the paths for accessing entities via their principal entities) and for accessing all objects that represent implementation of query options (e.g. $filter, $expand, etc.). The fuzzer reads query groups one by one when establishing the initial population. It picks random query options that are going to be generated based on the type of group and entity set.

The implementations for the query options are located in the module :doc:`entities.py` too. The following classes are implemented:

1. InlineCountQuery,
2. SearchQuery,
3. ExpandQuery,
4. OrderbyQuery,
5. TopQuery,
6. SkipQuery,
7. FilterQuery.

A query group builds a list of the valid query options in the process of initialization. When the fuzzer os generating new queries from scratch, the method `generate()`, which belongs to a particular class, is evoked and proper values are generated:

.. code-block:: python

    for option in self._queryable.random_options():
        generated_option = option.generate()


Selector
========

Selector is an arbitrator in the decision making process of the evolution. When the fitness score is stagnating for a while, it determines that it is more suitable to generate new candidates instead of mutating the old. This decision was based upon empirical studies. When the mutation does not improve an overall fitness score of a population for a longer time, it is preferable to start generate a new subset of requests which can improve the population's fitness.

Selector depends on the output of Analyzer. Analyzer analyzes responses, taking into account the following set of factors:

1. HTTP Status codes - If the status code is equal to HTTP 500 (Internal Server Error), the score is higher.
2. Response Time - If the response time is high enough even when a response's content is small in size, the score is higher.
3. Query Length - If the length of the created query is lower, the score is higher.

Score of the population is recalculated after every received response, so we can track the fitness of the population in real time.

Selector is also responsible for supplying a pair of candidates which are going to be mutated. It randomly selects a queryable entity set from the list of queryables provided by Builder. Two different candidates are then retrieved from a database according to the name and type of the queryable. These candidates are simply queries stored in JSON format. A new query is built from JSON and dispatched to the server.

For a better imagination, an example of the JSON record is shown here:

::

    {
        "_id" : ObjectId("5ceba33e26c6513344c9f38b"),
        "http" : "200",
        "error_code" : null,
        "error_message" : null,
        "entity_set" : "Cars",
        "accessible_set" : null,
        "accessible_keys" : {
                "Id" : "'17364521'"
        },
        "predecessors" : [ ],
        "string" : "Cars(ID='17364521')?$filter=Color le 'AAaa'&$format=json",
        "score" : 3,
        "order" : [
                "_$filter"
        ],
        "_$orderby" : null,
        "_$top" : null,
        "_$skip" : null,
        "_$filter" : {
                "groups" : [ ],
                "logicals" : [ ],
                "parts" : [
                        {
                                "id" : "8f65e83a-9491-4124-a3ad-4314b5da9f3e",
                                "name" : "Color",
                                "operator" : "le",
                                "operand" : "'AAaa'",
                                "replaceable" : true
                        }
                ]
        },
        "_$expand" : null,
        "_search" : null,
        "_$inlinecount" : null
    }

The structure contains all necessary values for further fuzzing. It contains response HTTP status code, fitness' score, order of query options, data for each query option, and so on. These data are employed in the mutation's process which is introduced later.

Generator
=========

Initial population is established only via Generator. Generator simply generates new queries based on the definitions of OData protocol. At the beginning of fuzzing, generator generates queries for all entity sets defined in the metadata document. It basically iterates through all queryables built by Builder. In the genetic loop, the fuzzer generates data for randomly selected queryables.

Methods for generation are distributed between multiple modules:

1. generators.py - There are functions for generating basic Edm data types (see section Primitive Data Types https://www.odata.org/documentation/odata-version-2-0/overview/).
2. entities.py - There are placed methods for generating query options. These methods calls functions from `generators.py`.
3. fuzzer.py - In this module, the generators for particular query options are called. This module utilizes a defined interface for generating the query options from the module `entities.py`.

It is pretty straightforward how are query options generated. Each query option has defined some rules in OData standard, e.g. value fom $top cannot be negative, and those rules are hardcoded in ODfuzz.

Filter Grammar
--------------

For the $filter query option, there was created an additional context-free grammar to generate strings. Rules of the grammar are defined like so:

1. EXPRESSION -> PROPFUNC OPERATOR OPERAND | CHILD
2. CHILD -> PARENT LOGICAL PARENT
3. PARENT -> EXPRESSION | CHILD | ( CHILD )
4. LOGICAL -> or | and
5. PROPFUNC -> property1 | property2 | property3 | ...
6. PROPFUNC -> startswith(p0, p1) | endswith(p0, p1) | ...
7. OPERATOR -> eq | ne | lt | gt | ...
8. OPERAND -> str | num | bool

Non-terminal symbols are distinguished by capital letters. The generator randomly selects one from a variety of conflicting rules and derives through it. At the end, a derivation tree is created and terminal string is generated.

Generator generates only valid requests. To change this behavior, it is required to refactor the code. The reason why are we generating only valid requests is that the fuzzer is testing backend of an OData service. If we want to test backend's logic, we need to ensure that data pass through all checks and control layers (syntax parsers, semantic parsers, etc.).

Mutator
=======

Mutator mutates data. The implementation of mutator is spread into 3 modules, like Generator:

1. mutators.py - There are located functions for mutating strings, integers, and for Edm data types (e.g. Edm.Decimal, or Edm.Boolean)
2. entities.py - There are implemented methods and classes which are closely related to Mutator itself. An eligible example is the class `FilterOptionDeleter`.
3. fuzzer.py - In this module, there are invoked functions for mutating strings, or for deleting logical parts from the $filter query option.

The mutable data are retrieved from a database. ODfuzz fully depends on database state (MongoDB). Every single request and its response's HTTP status code is writen to the database. When an initial population is created, the fuzzer continues evolving the population. ODfuzz takes 2 candidates (2 related queries) from the database and mutates them. The procedure is following:

1. Crossover - Two related queries (targeting the same endpoint, same entity set) are crossed. Such queries are obtained from Selector and Mutator does not have to cope with that.

   ::

        Parent1 : $filter=Price lt 20&$top=10&$skip=5

        Parent2 : $filter=Price gt 20&$orderby=Price asc&$top=20

        Child :  $filter=Price lt 20&$top=20

2. Mutation - The child is mutated after the crossover. ODfuzz has to deal with the data which are fetched from the database. The fuzzer do not have a reference to the objects built by Builder. These references cannot be stored in MongoDB. Type of the query allows us to properly match corresponding mutator's functions.

   ::

        def mutate_query_option(query, option_name, option_value):
            if query.is_option_deletable(option_name) and random.random() < PROBABILITY:
                query.delete_option(option_name)
            else:
                # option_value is a parsed JSON record from the database
                mutate_option(query, option_name, option_value)

        def mutate_option(query, option_name, option_value):
            if option_name == FILTER:
                self._mutate_filter(option_value)
            elif option_name == ORDERBY:
                self._mutate_orderby_part(option_value)
            else:
                pass


In Mutator, there are mutated reference keys as well. Those are the keys used for accessing single entities or are used within the principal entities (PrincipalEntity(ID='123', Color='Blue')/Entity).

Dispatcher
==========

Generated queries have to be dispatched to a server. A URI of an OData service is entered as a command line argument. Responses from the service are collected and passed to Analyzer. Dispatcher is implemented in the module :doc:`fuzzer.py`.

A user can specify whether the requests should be dispatched asynchronously or not. Dispatcher sends and receives data via the module `requests`. This module is patched by another module, i.e. `gevent`, to enable Dispatcher to send multiple non-blocking asynchronous requests to the server.

ODfuzz uses special type of threads, called Greenlets, in order to dispatch multiple requests at once. To do so, greenlets pool is created. A size of the pool, or a number of generated queries which will be sent asynchronously as one chunk, is configurable (--fuzzer-config). The following snippet shows how the pool is created:

.. code-block:: python

        pool = Pool(async_requests_num)
        for query in queries:
            pool.spawn(get_response, query)
        try:
            pool.join(raise_error=True)
        except DispatcherError:
            pass

In the example, we spawn multiple greenlets which execute the method `get_response()`. The structure of `query` holds data for each query and for each response. When the method `get_response()` is initiated, a server's response is stored as a property in the structure by default.

When the user does not opt for sending asynchronous requests, the pool is not created. Requests are dispatched to the server one by one. However, this option has many drawbacks. ODfuzz waits for a response after every request separately. This has a significant impact on the fuzzer's speed.

.. note:: Greenlets provide concurrency but not parallelism. Each greenlet runs in its own context independently. Learn more at https://greenlet.readthedocs.io/en/latest/.

Due to the feature of asynchronous requests, ODfuzz implements always 2 ways of generation and mutation. When the asynchronous requests are claimed, the fuzzer generates multiple queries and prepare them for dispatching. When the asynchronous communication is forbidden, the fuzzer generates only one query per iteration. The implemented genetic loop looks like this:

::

    def initialize():
        if asynchronous:
            self._queryable_factory = MultipleQueryable
            self._dispatch = self._get_multiple_responses
        else:
            self._queryable_factory = SingleQueryable
            self._dispatch = self._get_single_response

    def evolve_population():
        selection = self._selector.select()
            if selection.crossable:
                q = self._queryable_factory(selection.queryable)
                queries = q.crossover(selection.crossable)
                self._send_queries(queries)
                analyzed_queries = self._analyze_queries(queries)
            else:
                q = self._queryable_factory(selection.queryable)
                queries = q.generate()
                self._send_queries(queries)
                analyzed_queries = self._analyze_queries(queries)
            self._remove_weak_queries(analyzed_queries, queries)


.. seealso:: To better understand meaning of fuzzing or the idea of ODfuzz itself, take a look at http://excel.fit.vutbr.cz/submissions/2018/004/4.pdf to learn more.
