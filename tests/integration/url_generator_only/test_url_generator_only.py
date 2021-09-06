import logging
from pathlib import Path
import random

from odfuzz.restrictions import RestrictionsGroup
from odfuzz.entities import DirectBuilder
from odfuzz.fuzzer import SingleQueryable
from odfuzz.functionimport import FunctionImport

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


def builder(method):
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None)
    builder = DirectBuilder(metadata_file_contents, restrictions,method)
    entities = builder.build()
    queryable_factory = SingleQueryable
    return entities, queryable_factory


def test_direct_builder_http_get():
    get_entities , queryable_factory = builder("GET")
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
    del_entities , queryable_factory = builder("DELETE")
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
    put_entities , queryable_factory = builder("PUT")
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
    post_entities , queryable_factory = builder("POST")
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
    dir_entities , queryable_factory = builder("PUT")
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
    merge_entities , queryable_factory = builder("MERGE")
    body_list = []
    body_list.clear()
    for queryable in merge_entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            body_list.append(body)
    assert body_list[10] == "{\"PostalCode\": \"L\\u00ccN\\u00d2>ge\"}"


def test_function_imports():
    random.seed(10)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    function_import_list = FunctionImport.get_functionimport_list(path_to_metadata.read_bytes())
    fuzzed_fi = FunctionImport.generate_queries_for_functionimport(function_import_list[0])
    assert fuzzed_fi == "DuplicateCategory?CategoryName='%C2%A9%C2%B9%C3%91d2%C2%B3%C2%BB%E2%80%93%C3%A5Qi%C3%83%C2%BB%C5%93t%40%C3%BC%C2%90l%C2%A6K%C3%98%C2%8D%E2%80%9C%C2%A6%E2%80%94%C3%AA%29%C2%B1T%C3%AD%3A%C3%A7%C2%90J%C2%B1%20%21%C2%AC%C3%9B%60l%C3%93b~JZ%3A%C3%87%E2%80%98%21.%C3%A8%C3%8A%C2%B0%C2%AB%C2%B6q%C3%A5%C3%93%C5%93%C2%BEP7%C2%A4%21ji%C2%BD%3A%C3%99%C3%A6s%C3%86uN%E2%80%9D%C3%8F%C2%B4%C3%97NDz%C2%AERY%C5%92%C2%AA%C2%A5%C2%AF%24%C3%AC-L%C3%9C%C3%83UF_%C2%B1%3AR%C3%A7%C3%A4TU%C2%B8%E2%80%A1%C5%93%C2%AB7b%C3%89%C3%B4l%C2%81%E2%80%B0%24u%29%C2%AF%C2%A2%C3%93P%E2%80%A2%C2%BC%C3%AA%21%C3%BA%C3%84%2B%C3%83%C2%B9%C3%98%C2%BDqR%C2%BB%C3%AA%C2%B3%C2%A1J%C2%A6%C3%88%C3%93%C5%92'&DuplicateName='%C2%BB%C3%B1R%C3%8D%C2%ACA%C2%A5ja%C2%AC%C3%87qm%C5%92yNC%C3%99%C2%B1%C2%BAK%C2%B2%C2%AB%C2%BE%C2%AF%E2%80%A0%C3%B7%28%C3%B0%C2%B2%C2%A7%C2%81%C3%A4%C3%83%C3%83O%C3%BB~%C2%A8%C3%9Ci%C3%AD0%C3%A2%C3%94%C3%91%C3%9E%C2%B8gE%5D%C2%AB%40%C3%B5%5Bxl%C3%96%C3%8A%20C%3DQ%C3%A9%C2%B8L%C2%90%C3%96%C2%A1Z%C5%92Vu%C3%95Z%C2%A93z%C3%AD%3C%C2%B3%C3%BC%C3%BE%C3%AF%C3%83%C3%B6%C2%A7%C2%AF%C3%A8%C3%BC%C3%8C3_%C3%96%E2%80%98E%C3%9E%C3%9Eb3%C2%A7%C3%9A%C2%A3%E2%80%9C%C3%A41r%C2%A7xo%C5%92%2A%C2%90%C2%B1%C2%A7%7BZ%C3%9E%C3%BD%E2%80%94%C2%B5%C3%AF%5D%C2%BF%C2%BD%C2%BF%29%C2%A2%C2%AE%C3%A1%E2%80%A0%C5%92%C3%B7-%C2%B9%C2%AF%C2%B8%C3%94'&DuplicationComment='%C3%AE%C3%88%C3%B6%E2%80%98%C3%B6%C2%A2S%C3%98%C2%A5%C3%B6%C3%8Eq%C3%96%C3%B9%3Ce%C3%95%C5%93%C3%A4%C2%A8s%C3%BB%C2%9D%C3%9A%C2%B4%E2%80%94%C3%99X%21S%3Cz%C3%8Cn6%C3%8F%C3%BCs%C2%A6Z%C3%8F%C3%90%C2%AC%C3%95e%E2%84%A21%E2%80%A6%C3%91Y%C3%83%C3%8E%7D%C5%93m%C3%A6%C3%AF%C3%92mj%C3%8E%E2%80%98%C2%9D%C5%93%C3%97%C3%A1SPF%C3%99%E2%80%A1Rh%C3%B7%C3%87%C3%80%C5%92x%C2%9D%C2%AC%C3%91%C5%92pM%C2%AE%C3%B2%C2%B6%C3%9A%C2%B0%C3%B6%C2%AE%C3%98T%C2%8D%C2%A7%E2%80%A0%C3%8D%C3%81%C2%B2%E2%80%A2Zz%C2%AA%C3%A2OkX%C3%A1%C3%A0Y%C3%8F%C2%A9%C2%90%C3%8D%60m%C3%98nR%3E7m%C3%92'&DeleteOriginal=true"
