import logging
from pathlib import Path
import random
import os
import pytest

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

def builder_with_restrictions(method):
    #static dictionary for testing the implementation of exclusion_list
    exclusion_dict = {"$ENTITY_SET$":{".*": {"Properties":["ProductID"],"Nav_Properties":[]}}}
    os.environ["ODFUZZ_IGNORE_METADATA_RESTRICTIONS"] = "True"
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    metadata_file_contents = path_to_metadata.read_bytes()
    restrictions = RestrictionsGroup(None, exclusion_dict)
    builder = DirectBuilder(metadata_file_contents, restrictions, method)
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

def test_direct_builder_filter_query_option():
    random.seed(10)
    methodLists = ["POST", "MERGE", "PUT", "DELETE", "GET"]
    for method in methodLists:
        entities , queryable_factory = builder_with_restrictions(method)
        option_list_filter_query = []
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                for option_query in queries.options_strings:
                    if option_query == "$filter":
                        if len(queries.options_strings[option_query]) != 0:
                              option_list_filter_query.append(queries.options_strings[option_query])
                        
        if method == "POST" or method == "PUT" or method == "MERGE" or method == "DELETE":
            assert option_list_filter_query == []
        else:
            for filter_queries in option_list_filter_query:
                assert "ProductID" not in filter_queries

def test_direct_builder_orderby_query_option():
    random.seed(10)
    methodLists = ["POST", "MERGE", "PUT", "DELETE", "GET"]
    for method in methodLists:
        entities , queryable_factory = builder_with_restrictions(method)
        option_list_orderby_query = []
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                for option_query in queries.options_strings:
                    if option_query == "$orderby":
                        if len(queries.options_strings[option_query]) != 0:
                              option_list_orderby_query.append(queries.options_strings[option_query])
          
        if method == "POST" or method == "PUT" or method == "MERGE" or method == "DELETE":
            assert option_list_orderby_query == []
        else:
            assert "ProductID" not in option_list_orderby_query

@pytest.mark.parametrize('method_name,URI', [
    ("POST", "Suppliers?sap-client=500"),
    ("MERGE", "Suppliers(SupplierID=1564408389)?sap-client=500"),
    ("PUT", "Order_Details_Extendeds(OrderID=-717893126,ProductID=349786362,ProductName='8%C2%A3T%E2%80%A0%C2%81%C3%A1C%C3%8F%C3%96%C3%A5%C5%92%C2%A7%29%C3%83T%C3%9A%C5%92m',UnitPrice=16647857647390.73m,Quantity=-1289,Discount=1.4474711818031789e+20f)?sap-client=500"),
    ("DELETE", "Alphabetical_list_of_products?sap-client=500")
])

def test_direct_builder_Uri_unrestricted(method_name, URI):
    random.seed(30)
    entities , queryable_factory = builder(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            methodList.append(queries.query_string)
    
    choice = random.choice(methodList)

    assert choice == URI

@pytest.mark.parametrize('method_name,Body', [
    ("POST", "{\"SupplierID\": -752052732, \"CompanyName\": \"+\\u00b0\\u00a6bM\\u00f9V\\u00ec\\u00a2S\\u00b0\\u008f\\u00e1s]K\", \"ContactName\": \"\\u00fc\\u00f1!I\\u00d1\\u00ed\\u0153\\u00e6\\u00f5(\\u00b6\\u00c8J\\u008d\\u0192f\\u00f9\\u00f5.L\\u00deo\\u00e7\\u00f8\", \"ContactTitle\": \"j\\u00d6$\\u00dc\\u00a7\\u00ba\\u00c3_\\u201c\\u00ff\\u00b6|\\u2030\\u2018\\u00c8\\u00ac+\\u00e6\\u00f3\\u00bbo\", \"Address\": \"\\u00e3\", \"City\": \"\\u00abtx\\u00da\\u00e1([\\u00e9\", \"Region\": \"]\\u2020\\u00cf[5\\u00ef\\u2021\", \"PostalCode\": \"L!\\u00f7\\u008dh\\u00aeF\", \"Country\": \"\\u00c4\\u00b6(\\u00dd\\u00bd\\u00a8\", \"Phone\": \" \\u00fa\\u00eb\\u00ae\", \"Fax\": \"C\\u00d5\\u00c2\", \"HomePage\": \"\\u2030\\u2013(U\\u00ce\\u00c2[7E\\u00d2\\u00c7\\u00de\\u00bf\\u00e5\\u2014\\u00a9\\u00f6u\\u2021Vq\\u00fd\\u00b8e\\u00ceYl\\u00e7\\u00fc\\u00f9\\u00af>\\u00e8d\\u008180\\u00c9i\\u201cd\\u00ec\\u00d6\\u00a4\\u00f5}U)8\\u00a6-\\u2122ztn\\u00c5\\u00a5gU\\u00b7\\u00fa\\u0081\\u00f2\\u00af\\u00b3Ai\\u00f3F+G-n\\u00e1\\u00ff\\u0090 \\u00bf\\u00c6z\\u00f0\\u00e8Fn\\u00f3\\u00dc\\u00a3\\u00fb]\\u00f4c\\u00b5N\\u00ca\"}"),
    ("MERGE", "{\"HomePage\": \"\", \"Region\": \"\\u00d9\", \"CompanyName\": \"\\u008d^5\\u008d\\u00ebG3G\\u00dam\\u0090\\u00fa>\\u00cc\\u2020\\u00c1\\u00e0\\u00b9\\u00fd\\u00d0u\\u00ca\\u00a4X+S\\u00a7\\u00b6\\u00c2(7\", \"ContactName\": \"d\\u00df\\u00d7\\u201c\\u00ff\\u00c2>\\u00ac\\u00cd\\u00deu\"}"),
    ("PUT", "{\"OrderID\": -717893126, \"ProductID\": 349786362, \"ProductName\": \"8\\u00a3T\\u2020\\u0081\\u00e1C\\u00cf\\u00d6\\u00e5\\u0152\\u00a7)\\u00c3T\\u00da\\u0152m\", \"UnitPrice\": \"16647857647390.73m\", \"Quantity\": -1289, \"Discount\": \"1.4474711818031789e+20f\", \"ExtendedPrice\": \"19869531782366.04m\"}")
])

def test_direct_builder_body_unrestricted(method_name, Body):
    random.seed(30)
    entities , queryable_factory = builder(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            methodList.append(body)
    
    choice = random.choice(methodList)

    assert choice == Body

@pytest.mark.parametrize('method_name,URI', [
    ("POST", "Alphabetical_list_of_products?sap-client=500"),
    ("MERGE", "Order_Details_Extendeds(OrderID=505194340,ProductID=-198767217,ProductName='%C3%B2',UnitPrice=5992329101239.70m,Quantity=14009,Discount=1.835664460305276e+20f)?sap-client=500"),
    ("PUT", "Invoices(CustomerName='%C3%82%C3%87%C2%A4%C2%AE%C3%92%20%C3%8EJ%C3%92%C3%96x%C3%8F%C2%A2%C3%B9%C3%9E%C3%91TI%C3%8E%C2%A2%C2%AB%C3%9F%C3%B3',Salesperson='h%C3%B9%C3%91%7D%C3%B3%C2%A5%C2%A1%3A3Q%C2%BE%C2%A8M%C3%84%C2%90',OrderID=340222912,ShipperName='%C3%A6%C3%BD%C2%90-%3D%C3%95%40%C2%A4k%C5%93a%C5%92U',ProductID=360629792,ProductName='%C2%B6',UnitPrice=5269337783774.461m,Quantity=-4830,Discount=4.876322097957371e+19f)?sap-client=500"),
    ("DELETE", "Regions(RegionID=260860390)/Territories?sap-client=500")
])

def test_direct_builder_Uri_unrestricted(method_name, URI):
    random.seed(10)
    entities , queryable_factory = builder_with_restrictions(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            methodList.append(queries.query_string)
    
    choice = random.choice(methodList)

    assert choice == URI

@pytest.mark.parametrize('method_name,Body', [
    ("POST", "{\"ProductName\": \"_\\u00d8\\u00d8\\u00c8\\u00e2ui!\\u00acT\\u00d2\\u00bb)Q\\u00e6\\u00cf\\u00d6d$C\\u00ac\\u00e0\\u00d6\\u00eam\\u00c8sI7\\u00daFJ\", \"SupplierID\": 829092798, \"CategoryID\": -1690973651, \"QuantityPerUnit\": \"\\u2122\\u00a3-`exT\", \"UnitPrice\": \"3483815661862.28m\", \"UnitsInStock\": -17798, \"UnitsOnOrder\": -22391, \"ReorderLevel\": -28014, \"Discontinued\": true, \"CategoryName\": \"\\u00fc\\u00a4\\u00f2\\u00b3(\"}"),
    ("MERGE", "{\"ExtendedPrice\": \"167586037575.0167m\"}"),
    ("PUT", "{\"ShipName\": \"\\u00e46)1\\u00b5H5\\u00fc+\\u20186-G\\u00abI\\u00ef\\u00c0\\u00e2\\u00816![\\u00fe\\u00ac\\u00e3\\u00cb\\u00b2\", \"ShipAddress\": \"|V9\\u0153\\u00a60>\\u0153:sx\\u00c4\\u00ef\\u00e1\\u00fb\\u00ce\\u00ee5\\u00e3\\u00b5mf\\u00c1\\u2018\\u00ca\\u00b9\\u2030\\u00a2\\u00e6\\u00f6\\u00b64\\u00b9\\u00f3hn\", \"ShipCity\": \"f\\u00f0\\u00e5\", \"ShipRegion\": \"\\u00ba\\u2013\\u00e1\\u00d3\\u00e1q\\u00c9\\u00a6]\\u00fe!\", \"ShipPostalCode\": \"s-+j\\u00a2\\u00e1\\u00bb\\u00e0\\u0192\\u201c\", \"ShipCountry\": \"\\u00c5\", \"CustomerID\": \"\\u00bc\", \"CustomerName\": \"\\u00c2\\u00c7\\u00a4\\u00ae\\u00d2 \\u00ceJ\\u00d2\\u00d6x\\u00cf\\u00a2\\u00f9\\u00de\\u00d1TI\\u00ce\\u00a2\\u00ab\\u00df\\u00f3\", \"Address\": \"\\u2021\\u00e5\\u00f64\\u2030G\\u00e5d\\u00e6\\u008d\\u00f3\\u00cd\\u2026\\u00e3\\u00d1\\u00e5\\u00e8h\\u00b3s\\u00ee9\\u00d46 \\u00edtT\\u00c0DX\\u00d4]\\u00e8\\u00ee\\u0192\\u00b3p\\u00f7d=\", \"City\": \"\\u00be\\u00eal\", \"Region\": \"\\u00f6[\\u00de\", \"PostalCode\": \"\", \"Country\": \"r\\u00c5[p5\\u2022\", \"Salesperson\": \"h\\u00f9\\u00d1}\\u00f3\\u00a5\\u00a1:3Q\\u00be\\u00a8M\\u00c4\\u0090\", \"OrderID\": 340222912, \"OrderDate\": \"/Date(21578561005)/\", \"RequiredDate\": \"/Date(5767869169)/\", \"ShippedDate\": \"/Date(1812704175)/\", \"ShipperName\": \"\\u00e6\\u00fd\\u0090-=\\u00d5@\\u00a4k\\u0153a\\u0152U\", \"ProductName\": \"\\u00b6\", \"UnitPrice\": \"5269337783774.461m\", \"Quantity\": -4830, \"Discount\": \"4.876322097957371e+19f\", \"ExtendedPrice\": \"2780466105345.283m\", \"Freight\": \"89230624851.7479m\"}")
])

def test_direct_builder_body_unrestricted(method_name, Body):
    random.seed(10)
    entities , queryable_factory = builder_with_restrictions(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries,body = q.generate()
            methodList.append(body)
    
    choice = random.choice(methodList)

    assert choice == Body