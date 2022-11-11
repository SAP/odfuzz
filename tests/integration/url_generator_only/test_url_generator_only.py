import logging
from pathlib import Path
import random
import os

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
    print('\n entity count: ', len(entities) )
    for x in entities:
        print(x.__class__.__name__, '  --  ', x.entity_set)
    print('\n--End of listing the parsed entities--')
    '''

    queryable_factory = SingleQueryable

    for queryable in entities:
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
    for queryable in get_entities:
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
    for queryable in del_entities:
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
    for queryable in put_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Invoices(CustomerName='%C3%8B%C2%B4J%E2%80%A6%C3%B4%C3%AE%C3%AC%C3%99%C3%9D%C3%A5B%C2%AFNZ%C3%96n%C3%80J%C2%A8%40%C2%BF%C3%A2%5D%C2%B0%C3%B6%C3%8A%C2%A4%C3%848%C3%90njgk%C3%82%E2%80%98',Salesperson='%20%C6%92%C2%B3%C2%A8%3D%C3%AAI%C3%94R%C3%AC_%C2%BF%C3%8E%C3%9DV%C3%8B%C3%BC9%C3%BF',OrderID=-1738698126,ShipperName='b',ProductID=-1469737969,ProductName='Rg%C3%81b%C3%8CZ%C3%95%C2%B3%3A%C2%A4mC%40%C3%B3%C2%B8%C3%AD%C3%8CO%C3%81%C2%B5%C3%ACD%C3%80',UnitPrice=109582959431.9592m,Quantity=32113,Discount=1.949561421076087e+20f)?sap-client=500" == choice

def test_direct_builder_http_post_url():
    random.seed(20)
    post_entities , queryable_factory = builder("POST")
    queries_list = []
    queries_list.clear()
    for queryable in post_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            queries_list.append(queries.query_string)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Employees?sap-client=500" == choice

def test_direct_builder_body_generation():
    random.seed(20)
    dir_entities , queryable_factory = builder("PUT")
    body_list = []
    body_list.clear()
    for queryable in dir_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            body_list.append(body)
    assert random.choice(body_list) == "{\"ShipName\": \"P\\u0192vC}\\u00e8\\u00fa\\u00b40y\\u00b8RN\\u00e5tKo\\u00d4+S\\u00c8\", \"ShipAddress\": \"\\u00e5+\\u00a5\\u00b1$_OO\\u00f5\\u00bf<G\\u00e8\\u00e1H\\u00f2\\u00c5\\u00bb\\u0153R\\u00c5P-\\u00e4 \\u00b0\\u00e7\\u00a9r^\\u00bd]\\u00d84e\\u00df-\\u009d\\u00a7\\u00d9\\u00e7\\u00d64\\u00f3 \\u00a69!\\u00f0\\u00fd7\\u2020g\\u00bb\\u0152`g$\", \"ShipCity\": \"I\\u00c0e\", \"ShipRegion\": \"\\u0090\\u00f4\\u00b5e\\u00c2j\\u00f5\\u00a4\\u00fa\\u00fe\\u00d5\\u00d2\\u00b6\\u00c7\\u00a7\", \"ShipPostalCode\": \"m\", \"ShipCountry\": \"\\u00d5\\u00feSM\\u00b9AQ\\u00d1\\u00ee*E+\\u00c0\", \"CustomerID\": \"n\\u00d8\\u00b3\", \"CustomerName\": \"\\u00cb\\u00b4J\\u2026\\u00f4\\u00ee\\u00ec\\u00d9\\u00dd\\u00e5B\\u00afNZ\\u00d6n\\u00c0J\\u00a8@\\u00bf\\u00e2]\\u00b0\\u00f6\\u00ca\\u00a4\\u00c48\\u00d0njgk\\u00c2\\u2018\", \"Address\": \"\\u00a3N\\u0192\\u00c5\\u2026\", \"City\": \"a\\u00c4\\u2021\\u008fI\\u00aa{nP\\u00b5\", \"Region\": \"!\\u00e7m2a\\u00ca\", \"PostalCode\": \"Q\\u00c2\\u00e6\\u2018R\\u00a1Z\\u00f4\\u00c1\\u00b3\", \"Country\": \"8\\u00b1Z\\u00f5\\u00bb81\", \"Salesperson\": \" \\u0192\\u00b3\\u00a8=\\u00eaI\\u00d4R\\u00ec_\\u00bf\\u00ce\\u00ddV\\u00cb\\u00fc9\\u00ff\", \"OrderID\": -1738698126, \"OrderDate\": \"/Date(10911881527)/\", \"RequiredDate\": \"/Date(31373613612)/\", \"ShippedDate\": \"/Date(8601631755)/\", \"ShipperName\": \"b\", \"ProductID\": -1469737969, \"ProductName\": \"Rg\\u00c1b\\u00ccZ\\u00d5\\u00b3:\\u00a4mC@\\u00f3\\u00b8\\u00ed\\u00ccO\\u00c1\\u00b5\\u00ecD\\u00c0\", \"UnitPrice\": \"109582959431.9592m\", \"Quantity\": 32113, \"Discount\": \"1.949561421076087e+20f\", \"ExtendedPrice\": \"71789779110.3390m\", \"Freight\": \"16854839578893.180m\"}"

def test_direct_builder_http_merge_body():
    random.seed(20)
    merge_entities , queryable_factory = builder("MERGE")
    body_list = []
    body_list.clear()
    for queryable in merge_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            body_list.append(body)
    assert body_list[10] == "{\"Region\": \"\\u00f6\", \"ContactName\": \"\\u00a1\\u008f\\u2014\\u00e0\\u0192\\u00e6RZK\\u00bfoK-[@V\", \"Fax\": \"[|\\u00a4\\u00e0Zu\\u008f\\u00a1a\\u00efnIL=\\u00d5\\u00e6T\", \"PostalCode\": \"\\u00b61\\u0081B\\u00f9B\\u00a7\", \"CompanyName\": \"\\u00b3s\\u00f3\\u00a91\\u00b5\\u00d7\\u0081\\u00e5G\\u00ca\\u00a7o0\\u00f9\", \"Country\": \"\\u00a1\\u00d4\", \"City\": \"l]_\\u00eas\\u0090\\u00f6\\u00ff\", \"Address\": \"(F\\u00ca\\u00a4[R\\u00a7\\u00b7kT\\u00f2\\u00ef\\u2022\\u00bbd\\u00c4see\\u00cb\\u00a7y\\u2030}L6\\u2122c\\u00b4C\\u00db\\u00d1\\u00b6\\u00b1\\u00aa\\u00bc+8\\u00e2[\\u00aa^-c\\u00c6`\\u00ff\\u0081\\u00aa\", \"ContactTitle\": \"\\u00dd\\u00b5q\\u00f9\\u00bbd$E\\u0192a\\u00d0>\\u00de\\u00c8b\\u00f2u\\u00dc\\u00c1P\\u2030\"}"

def test_function_imports():
    random.seed(10)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    function_import_list = FunctionImport.get_functionimport_list(path_to_metadata.read_bytes())
    fuzzed_fi = FunctionImport.generate_queries_for_functionimport(function_import_list[0])
    assert fuzzed_fi == "DuplicateCategory?CategoryName='%C2%AA%C2%BA%C3%92d2%C2%B5%C2%BC%E2%80%94%C3%A6Qi%C3%84%C2%BC%C2%81t%5E%C3%BD%E2%80%98l%C2%A7K%C3%99%C2%8F%E2%80%9D%C2%A7%3D%C3%AB_%C2%B2T%C3%AE%3C%C3%A8%E2%80%98J%C2%B2%24%C2%AE%C3%9C%E2%80%9Cl%C3%94b%21JZ%3C%C3%88%E2%80%99%24%E2%80%B0%C3%A9%C3%8B%C2%B1%C2%AC%C2%B7q%C3%A6%C3%94%C2%81%C2%BFP7%C2%A5%24ji%C2%BE%3C%C3%9A%C3%A7s%C3%87uN%E2%80%A2%C3%90%60%C3%98NDz%C2%AFRY%C2%8D%C2%AB%C2%A6%C2%B0%40%C3%AD%E2%80%93L%C3%9D%C3%84UF%2B%C2%B2%3CR%C3%A8%C3%A5TU%C2%B9%C5%92%C2%81%C2%AC7b%C3%8A%C3%B5l%C6%92%C2%A8%40u_%C2%B0%C2%A3%C3%94P%E2%84%A2%C2%BD%C3%AB%24%C3%BB%C3%85-%C3%84%C2%BA%C3%99%C2%BEqR%C2%BC%C3%AB%C2%B5%C2%A2J%C2%A7%C3%89%C3%94%C2%8D%C3%88'&DuplicateName='%C3%B2R%C3%8E%C2%AEA%C2%A6ja%C2%AE%C3%88qm%C2%8DyNC%C3%9A%C2%B2%C2%BBK%C2%B3%C2%AC%C2%BF%C2%B0%E2%80%A1%C3%B8%29%C3%B1%C2%B3%C2%A9%C6%92%C3%A5%C3%84%C3%84O%C3%BC%21%C5%93%C3%9Di%C3%AE0%C3%A3%C3%95%C3%92%C3%9F%C2%B9gE%7C%C2%AC%5E%C3%B6%5Dxl%C3%97%C3%8BC%5BQ%C3%AA%C2%B9L%E2%80%98%C3%97%C2%A2Z%C2%8DVu%C3%96Z%C2%AA3z%C3%AE%3E%C2%B5%C3%BD%C3%BF%C3%B0%C3%84%C3%B7%C2%A9%C2%B0%C3%A9%C3%BD%C3%8D3%2B%C3%97%E2%80%99E%C3%9F%C3%9Fb3%C2%A9'&DuplicationComment='%E2%80%9D%C3%A51r%C2%A9xo%C2%8D%28%E2%80%98%C2%B2%C2%A9%7DZ%C3%9F%C3%BE%3D%C2%B6%C3%B0%7C%C3%80%C2%BE%C3%80_%C2%A3%C2%AF%C3%A2%E2%80%A1%C2%8D%C3%B8%E2%80%93%C2%BA%C2%B0%C2%B9%C3%95%C2%B9v%C3%AF%C3%89%C3%B7%E2%80%99%C3%B7%C2%A3S%C3%99%C2%A6%C3%B7%C3%8Fq%C3%97%C3%BA%3Ee%C3%96%C2%81%C3%A5%C5%93s%C3%BC%C2%A1%C3%9B%60%3D%C3%9AX%24S%3Ez%C3%8Dn6%C3%90%C3%BDs%C2%A7Z%C3%90%C3%91%C2%AE%C3%96e%C2%9D1%E2%80%A0%C3%92Y%C3%84%C3%8F%20%C2%81m%C3%A7%C3%B0%C3%93mj%C3%8F%E2%80%99%C2%A1%C2%81%C3%98%C3%A2SPF%C3%9A%C5%92Rh%C3%B8%C3%88%C3%81%C2%8Dx%C2%A1%C2%AE%C3%92%C2%8DpM%C2%AF%C3%B3%C2%B7%C3%9B%C2%B1%C3%B7%C2%AF%C3%99T%C2%8F%C2%A9%E2%80%A1%C3%8E%C3%82%C2%B3%E2%84%A2Zz%C2%AB%C3%A3OkX%C3%A2%C3%A1Y%C3%90%C2%AA%E2%80%98%C3%8E%E2%80%9Cm%C3%99nR'&DeleteOriginal=true"

#static dictionary for testing the implementation of exclusion_list
exclusion_dict = {
                "$ENTITY_SET$":{
                        "Products": {
                            "Properties":["ProductID", "ProductName"],
                            "Nav_Properties":["Category"]
                        },
                        "Categories": {
                            "Properties":[],
                            "Nav_Properties":[]
                        }
                    }
                }

def test_method_for_exclusion_dict():
    #Method used for testing the implementation of exclusion_list
    os.environ["ODFUZZ_IGNORE_METADATA_RESTRICTIONS"] = "True"
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None, exclusion_dict)
    del_builder = DirectBuilder(metadata_file_contents, restrictions, "GET")
    del_entities = del_builder.build()
    queryable_factory = SingleQueryable    
    for queryable in del_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            print(queries.query_string,"\n")
            print(body,"\n\n")
 
    #FioriDast update the Exception List
    restrictions = RestrictionsGroup(None, exclusion_dict)
    del_builder.set_restrictions(restrictions)
    del_entities = del_builder.build()