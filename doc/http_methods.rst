======================
HTTP Methods in ODfuzz
======================


An Overview of Supported Query Options
------------------------------------------


.. csv-table:: HTTP verb implementation
   :header: "", "GET", "DELETE", "PUT", "POST" 
   :widths: 30, 15, 15, 15, 15

   "$inlinecount", "Yes", "No", "No", "No"
   "$search", "Yes", "No", "No", "No"
   "$top", "Yes", "No", "No", "No"
   "$skip", "Yes", "No", "No", "No"
   "$orderby", "Yes", "No", "No", "No"
   "$expand", "Yes", "No", "No", "No"
   "$filter", "Yes", "No", "No", "No"
   "$format", "Yes", "No", "No", "No"
   "body value", "Yes", "Yes", "Yes", "Yes"
   "populated body", "No", "No", "Yes", "Yes"
   "Addressing Single entities", "Yes", "Yes", "Yes", "No"
   "Addressing Multiple entities", "Yes", "Yes", "No", "Yes"
   "Synced URI and body values", "No", "No", "Yes", "No"

**"body value"** refers to the fact that a value for the body is returned by *generate()* function. 
**"populated body"** refers to the fact that the value contains data, and isnt an empty JSON parsed into a string.



Introduction
------------

The class DirectBuilder provides an interface for developers to integrate the query generation functionalities into their projects.
As of ver. **0.14a2** the supported list of HTTP methods in DirectBuilder are **"GET", "DELETE", "PUT" and "POST"**. 

.. code-block:: python

    import logging
    from pathlib import Path
    from odfuzz.restrictions import RestrictionsGroup
    from odfuzz.entities import DirectBuilder
    from odfuzz.fuzzer import SingleQueryable

    def DirectBuilderExample():
        path_to_metadata = Path(__file__).parent.joinpath("metadata.xml")
        metadata_file_contents = path_to_metadata.read_bytes()
        restrictions = RestrictionsGroup(None)
        #DirectBuilder needs to be called with HTTP method, which in this case is PUT
        examplebuilder = DirectBuilder(metadata_file_contents, restrictions,"PUT")
        example_entities = example_builder.build()
        queryable_factory = SingleQueryable
        queries_list = []
        queries_list.clear()

        #this function iterates through the SingleQueryable object returned
        for queryable in example_entities.all():
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()


As shown in the snippet above, DirectBuilder is initialized with the metadata file, the restrictions, and the HTTP method defined as a string.

.. code-block:: python

 queries,body = q.generate() 

This line returns the 2 parts of the request: the URI query string, and the body as a JSON string. For **GET** and **DELETE**, body is return as an empty JSON i.e. "{}"


GET Queries
-----------

For generating GET queries, DirectBuilder needs to be called with **method = "GET"**

.. code-block:: python

    examplebuilder = DirectBuilder(metadata_file_contents, restrictions,"GET")

On calling *SingleQueryable.generate()*, this would return a fuzzed URI string and an empty JSON string.

::
     
     Categories?$expand=Products/Order_Details,Products&$top=127&$filter=CategoryID le -794650810&$inlinecount=allpages&sap-client=500&$format=json


DELETE Queries
--------------

For generating DELETE queries, DirectBuilder needs to be called with **method = "DELETE"**

.. code-block:: python

    examplebuilder = DirectBuilder(metadata_file_contents, restrictions,"DELETE")

On calling *SingleQueryable.generate()*, this would return a fuzzed URI string and an empty JSON string.

::
     
     Categories?sap-client=500



POST Queries
------------

For generating POST queries, DirectBuilder needs to be called with **method = "POST"**

.. code-block:: python

    examplebuilder = DirectBuilder(metadata_file_contents, restrictions,"GET")

On calling *SingleQueryable.generate()*, this would return a fuzzed URI string and a JSON string containing all the fuzzed properties. No keys appear in the URI.

::
     
     Categories?sap-client=500
     
     {"CategoryID": "-346633563", "CategoryName": "DNf%C2%90", "Description": "%E2%80%93Qe%C3%94%3C2%C3%B9%C3%9F%2A%C2%AC%E2%84%A2%C3%BB%C3%86E6m%40%C3%A5%C2%BA%C3%BB%C2%A9%C2%B9o1%C3%94%C2%90%C2%AAA%C2%A9%C3%A5A%E2%80%A2%C2%AC%20%C3%92%C2%BB%C2%A2%C2%B0%C3%96h%C2%8D%C3%BF%C5%92%C3%85u%3C", "Picture": "YmluYXJ5JzcyJw=="}


PUT Queries
-----------

For generating PUT queries, DirectBuilder needs to be called with **method = "PUT"**

.. code-block:: python

    examplebuilder = DirectBuilder(metadata_file_contents, restrictions,"PUT")

On calling *SingleQueryable.generate()*, this would return a fuzzed URI string and a JSON string containing all the fuzzed properties. All the keys appear in the URI and are synchronized with the body. 

::
     
     Categories(CategoryID=1714953551,CategoryName='%21%C2%9Dla%C3%92l%24',Description='hz%60%C3%8F%C3%8F%7B%C3%AAi%2Bk%C3%81%C2%A4%C3%96xc%C5%93%C2%A85k%C3%93%2A%C3%B5%C2%BBrLD%2A%E2%80%A1',Picture=binary'ac9916669fAeb2')?sap-client=500   
     
     {"CategoryID": "1714953551", "CategoryName": "%21%C2%9Dla%C3%92l%24", "Description": "hz%60%C3%8F%C3%8F%7B%C3%AAi%2Bk%C3%81%C2%A4%C3%96xc%C5%93%C2%A85k%C3%93%2A%C3%B5%C2%BBrLD%2A%E2%80%A1", "Picture": "YmluYXJ5J2FjOTkxNjY2OWZBZWIyJw=="}





==================
Code Documentation
==================

The **method** parameter in DirectBuilder
----------------------------------------

DirectBuilder now has an additional parameter called **method**. This accepts the users choice of HTTP method to get the fuzzed requests. The DirectBuilder *init* checks for validity and calls the *Config.fuzzer* setter to set the value in the Config object.

.. code-block:: python

    def __init__(self, metadata, restrictions,method):
        if method not in ["GET","DELETE","PUT","POST"]:
            raise ValueError("The http method value \'{}\' is invalid\nUse either GET, DELETE, PUT or POST".format(method))
        self._queryable = QueryableEntities()
        self._metadata_string = metadata
        self._restrictions = restrictions
        Config.init()
        Config.fuzzer.http_method_enabled = method

In config.py, this would be used to build the Config object, which would be looked up during query construction and check which HTTP method is set.

Truncating Query Options
------------------------

For Odata queries other than **GET**, query options need to be truncated. To implement this, in fuzzer.py *Query.build_string()* would first check if *Config.fuzzer.http_method_enabled == "GET"* before generating the options and appending them. 
The list of options are illustrated in the table above.


Generating a Body
-----------------

For PUT and POST queries, a new element for the queries need to be generated i.e. the **body** of the request. 
The first change is returning a tuple of *query, body* instead of just the *query* from *SingleQueryable.generate()*.
A new function *generate_body()* is added which fetches the proprties from the metadata and calls the generator on each of them, and appends them is a dictionary.
The dictionary is jsonified before being returned as the body. This process is skipped for **GET** and **DELETE**,and they return an empty jsonified string instead, to be compatible with the tuple returned. The changes made to the generators are described further below.


Differentiating between PUT and POST
------------------------------------

PUT is idempotent and address single entities, whereas POST isnt idempotent and addresses multiple entities. Therefore changes are made in *DirectBuilder._append_queryable()* so that PUT avoids generating multiple entities and POST avoids generating single entities, during query generation.

.. code-block:: python

    def _append_queryable(self, query_group_data):
        # TODO REFACTOR DRY this method is direct copypaste from DispatchedBuilder just to have a prototype for integration. Intentionally no abstract class at the moment.
        if Config.fuzzer.http_method_enabled != "POST":
            self._append_corresponding_queryable(QueryGroupSingle(query_group_data))
        if Config.fuzzer.http_method_enabled != "PUT":
            self._append_corresponding_queryable(QueryGroupMultiple(query_group_data))
            self._append_associated_queryables(query_group_data)


Alternative EDM Generators for Body
-----------------------------------

Some EDM data types have different representation format in the body than in the URI. So the generators needed to adapt for the body implementation. The *generate()* function in the generator classes now have an additional parameter **format** which is provided the value "body". The default generation is done by **generate(format="uri")**. Following is an example of calling generator on a property for body format.

.. code-block:: python

    generated_body = prprty.generate(format='body')



Synchronizing values between URI and Body
-----------------------------------------

The fuzzed values for properties in both the URI and Body needs to be in sync, even across the formats to make them valid Odata requests in most cases. For this scenario, both the URI and body value for a property needs to be generated simultaneously in both the formats in a single step. A new **format** value "key" is used for this purpose.

.. code-block:: python

    uri_value, body_value = prprty.generate(format="key")

This would return a tuple, where the first value would be in the standard URI(literal) format, and the second value would be the same in body(JSON) format.
