import logging
from pathlib import Path
import random

from odfuzz.restrictions import RestrictionsGroup
from odfuzz.entities import DirectBuilder
from odfuzz.fuzzer import SingleQueryable

logger = logging.getLogger("testDirectBuilder")
logger.setLevel(logging.CRITICAL)
#logger is needed not for the test but as part of DirectBuilder constructor


def test_expected_integration_sample():
    """ This test is example of intended usage of DirectBuilder class and fixture of its API since will be used in external tools

    see https://github.com/SAP/odfuzz/issues/37
    """

    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    # do not pass metadata as python string but read as bytes, usually ends with Unicode vs xml encoding mismatch.

    restrictions = RestrictionsGroup(None)
    builder = DirectBuilder(metadata_file_contents, restrictions,"GET")
    entities = builder.build()

    ''' uncomment for code sample purposes
    print('\n entity count: ', len(entities.all()) )
    for x in entities.all():
        print(x.__class__.__name__, '  --  ', x.entity_set)
    print('\n--End of listing the parsed entities--')
    '''

    queryable_factory = SingleQueryable

    for queryable in entities.all():
        URL_COUNT_PER_ENTITYSET = len(queryable.entity_set.entity_type.proprties()) * 1
        #Leaving as 1 instead of default 20, so the test output is more understandable and each property has one URL generated

        ''' uncomment for code sample purposes
        print('Population range for entity \'{}\' - {} - is set to {}'.format(queryable.entity_set.name, queryable.__class__, URL_COUNT_PER_ENTITYSET))
        '''

        for _ in range(URL_COUNT_PER_ENTITYSET):
            q = queryable_factory(queryable, logger, 1)
            queries = q.generate()
            ''' uncomment for code sample purposes            
            print(queries[0].query_string)    
            #hardcoded 0, since SingleQueryable is used and therefore generate only one URL
            '''
            assert queries[0].query_string != ""



def test_direct_builder_http_get():
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    get_builder = DirectBuilder(metadata_file_contents, restrictions,"GET")
    get_entities = get_builder.build()
    queryable_factory = SingleQueryable
    queries_list = []
    queries_list.clear()
    for queryable in get_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries, body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=set(queries_list)
    choice = queries_list.pop()
    assert ("filter" in choice or "expand" in choice or "startswith" in choice or "replace" in choice or "substring" in choice or "inlinecount" in choice) == True


def test_direct_builder_http_delete():
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    del_builder = DirectBuilder(metadata_file_contents, restrictions,"DELETE")
    del_entities = del_builder.build()
    queryable_factory = SingleQueryable
    queries_list = []
    queries_list.clear()
    for queryable in del_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=set(queries_list)
    choice = queries_list.pop()
    assert ("filter" in choice or "expand" in choice or "startswith" in choice or "replace" in choice or "substring" in choice or "inlinecount" in choice) == False

def test_direct_builder_http_put_url():
    random.seed(20)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    put_builder = DirectBuilder(metadata_file_contents, restrictions,"PUT")
    put_entities = put_builder.build()
    queryable_factory = SingleQueryable
    queries_list = []
    queries_list.clear()
    for queryable in put_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Orders(OrderID=264879099)?sap-client=500" == choice

def test_direct_builder_http_post_url():
    random.seed(20)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    post_builder = DirectBuilder(metadata_file_contents, restrictions,"POST")
    post_entities = post_builder.build()
    queryable_factory = SingleQueryable
    queries_list = []
    queries_list.clear()
    for queryable in post_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Suppliers?sap-client=500" == choice

def test_direct_builder_body_generation():
    random.seed(20)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    dir_builder = DirectBuilder(metadata_file_contents, restrictions,"PUT")
    dir_entities = dir_builder.build()
    queryable_factory = SingleQueryable
    body_list = []
    body_list.clear()
    for queryable in dir_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            body_list.append(body)
    assert random.choice(body_list) == "{\"OrderID\": 264879099, \"CustomerID\": \"PE\", \"EmployeeID\": 1232571814, \"OrderDate\": \"/Date(129712006108)/\", \"RequiredDate\": \"/Date(190417733358)/\", \"ShippedDate\": \"/Date(144052759134)/\", \"ShipVia\": -1121991714, \"Freight\": \"77202251625.6257m\", \"ShipName\": \"\\u00e8r\\u00fefy\\u00f4\\u2020hpD\\u00ff:fVK\\u00e1\\u00f1\\u201d\\u00da^:\", \"ShipAddress\": \"\\u0081\\u00c7\\u00d0F\\u00f0\\u2014\", \"ShipCity\": \"\\u00f6\\u00a1rsH\\u00f6\\u00ac*$\\u00fe\\u00d5\\u00f3\\u00a8\", \"ShipRegion\": \"\\u00eb\", \"ShipPostalCode\": \"d\\u00f2\\u00ae\\u00ff\\u00ea\", \"ShipCountry\": \"ZS\\u00fd\\u0192\\u00c0\"}"

def test_direct_builder_http_merge_body():
    random.seed(20)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    dir_builder = DirectBuilder(metadata_file_contents, restrictions,"MERGE")
    dir_entities = dir_builder.build()
    queryable_factory = SingleQueryable
    body_list = []
    body_list.clear()
    for queryable in dir_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            body_list.append(body)
    assert body_list[10] == "{\"PostalCode\": \"L\\u00ccN\\u00d2>ge\"}"
