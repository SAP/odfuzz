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
        option_list_filter_query.clear()
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
        option_list_orderby_query.clear()
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

def test_direct_builder_exclusion_list_Uri():
    random.seed(30)
    methodLists = {"POST":[], "MERGE":[], "PUT":[], "DELETE":[]}
    for method in methodLists.keys():
        entities , queryable_factory = builder(method)
        methodLists[method].clear()
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                methodLists[method].append(queries.query_string)
        
        choice = random.choice(methodLists[method])
        
        if method == "POST":
            assert choice == "Suppliers?sap-client=500"
        if method == "MERGE":
            assert choice == "Invoices(CustomerName='D0t%C2%A7%C2%A94%C3%98%C2%B3%C2%BA3%C3%83t%C3%9E%C2%B5%C3%A8%C2%B0Tc%C2%BA%C2%B374fP%20J%C3%B4',Salesperson='',OrderID=-351091532,ShipperName='A%20J%E2%80%A2%C2%B3%C3%AC%C3%B4%3D%C2%BFv%C2%8D-_%C2%A4%E2%80%A6%C3%89%E2%80%A0%C3%83%C3%BD7%C3%A2%C3%B1%3C%C3%9F',ProductID=-326207683,ProductName='%C2%BB%C2%A4%C3%99BA%5D%C5%93B7%C2%B21m%C2%AFI-K%20%C2%8D%C2%A2l%24%C3%85P%C3%AFh',UnitPrice=153300388545.5303m,Quantity=-19687,Discount=1.1858723596211711e+20f)?sap-client=500"
        if method == "PUT":
            assert choice == "Invoices(CustomerName='%C3%B5%E2%80%98%C3%BFD%C3%A3R%20%C3%B5.iH%7B%C3%AF%C3%A0%C3%BC%C2%BF%C3%B0N%C3%A8',Salesperson='%C2%A9d',OrderID=2129182719,ShipperName='%C3%AF_%C2%A3YU%C3%9A%3DKI%C3%BC%C2%B2%C2%B4%C2%A4a%C3%83S%C2%AA%C3%91Dc%C2%A7G9l%C3%87q',ProductID=1798319544,ProductName='i%3E%C3%AFj%C2%BC%C3%BE%C2%AE%E2%80%9C%3DF%C3%8Ed%C3%AA%2B%3C%C3%83%3D%C3%AE%C3%B9%C3%BDG%7B5%C2%B1%C2%8D%C2%B9Vr',UnitPrice=79189778900.5386m,Quantity=26127,Discount=3.0408649179978754e+20f)?sap-client=500"
        if method == "DELETE":
            assert choice == "Suppliers(SupplierID=1075178284)/Products?sap-client=500"
    
    random.seed(10)
    for method in methodLists.keys():
        entities , queryable_factory = builder_with_restrictions(method)
        methodLists[method].clear()
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                methodLists[method].append(queries.query_string)
        
        choice = random.choice(methodLists[method])

        if method == "POST":
            assert choice == "Alphabetical_list_of_products?sap-client=500"
        if method == "MERGE":
            assert choice == "Sales_by_Categories(CategoryID=-1953083790,CategoryName='Z%C3%93%C2%AB%C2%8F%C3%BC%E2%80%A1%5D%C3%9A%E2%80%99J%E2%80%A2%C3%AC%28',ProductName='%5D%C3%A5s%C3%95z%C3%A5%C3%97%C3%B74%C3%A3%206%E2%80%A1%C3%82J%C2%B1%C3%B8%C3%A2c%3D%C3%B4%C2%B3%C3%A9%C5%93%C2%BA%C2%A4k%C2%AA%C3%A2%C3%AB%7CZ%C2%B0S%C3%BC%C3%B4Y%C2%B6%C3%9C%20')?sap-client=500"
        if method == "PUT":
            assert choice == "Sales_Totals_by_Amounts(OrderID=203510101,CompanyName='h%E2%80%9C.Kd%C3%BA%C3%A3%C2%BA%24G')?sap-client=500"
        if method == "DELETE":
            assert choice == "Orders_Qries?sap-client=500"

def test_direct_builder_exclusion_list_body():
    random.seed(30)
    methodLists = {"POST":[], "MERGE":[], "PUT":[]}
    for method in methodLists.keys():
        entities , queryable_factory = builder(method)
        methodLists[method].clear()
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                methodLists[method].append(body)
        
        choice = random.choice(methodLists[method])
        
        if method == "POST":
            assert choice == "{\"SupplierID\": -752052732, \"CompanyName\": \"+\\u00b0\\u00a6bM\\u00f9V\\u00ec\\u00a2S\\u00b0\\u008f\\u00e1s]K\", \"ContactName\": \"\\u00fc\\u00f1!I\\u00d1\\u00ed\\u0153\\u00e6\\u00f5(\\u00b6\\u00c8J\\u008d\\u0192f\\u00f9\\u00f5.L\\u00deo\\u00e7\\u00f8\", \"ContactTitle\": \"j\\u00d6$\\u00dc\\u00a7\\u00ba\\u00c3_\\u201c\\u00ff\\u00b6|\\u2030\\u2018\\u00c8\\u00ac+\\u00e6\\u00f3\\u00bbo\", \"Address\": \"\\u00e3\", \"City\": \"\\u00abtx\\u00da\\u00e1([\\u00e9\", \"Region\": \"]\\u2020\\u00cf[5\\u00ef\\u2021\", \"PostalCode\": \"L!\\u00f7\\u008dh\\u00aeF\", \"Country\": \"\\u00c4\\u00b6(\\u00dd\\u00bd\\u00a8\", \"Phone\": \" \\u00fa\\u00eb\\u00ae\", \"Fax\": \"C\\u00d5\\u00c2\", \"HomePage\": \"\\u2030\\u2013(U\\u00ce\\u00c2[7E\\u00d2\\u00c7\\u00de\\u00bf\\u00e5\\u2014\\u00a9\\u00f6u\\u2021Vq\\u00fd\\u00b8e\\u00ceYl\\u00e7\\u00fc\\u00f9\\u00af>\\u00e8d\\u008180\\u00c9i\\u201cd\\u00ec\\u00d6\\u00a4\\u00f5}U)8\\u00a6-\\u2122ztn\\u00c5\\u00a5gU\\u00b7\\u00fa\\u0081\\u00f2\\u00af\\u00b3Ai\\u00f3F+G-n\\u00e1\\u00ff\\u0090 \\u00bf\\u00c6z\\u00f0\\u00e8Fn\\u00f3\\u00dc\\u00a3\\u00fb]\\u00f4c\\u00b5N\\u00ca\"}"
        if method == "MERGE":
            assert choice == "{\"ExtendedPrice\": \"8478871580765.81m\", \"ShipName\": \"\\u00e1\\u00a4\\u00b5E$\\u2122\\u00e1s(\\u00e5l\\u00a3\", \"OrderDate\": \"/Date(18826077145)/\", \"ShipCity\": \".\\u00ff\\u00da\\u00fd\\u2022\", \"Region\": \"L\\u00d4\\u00a7+\\u00e7\", \"CustomerID\": \"\\u00de\\u00c3\", \"ShipRegion\": \"\\u00fdI\\u00b338\\u2021\\u00c0@\\u00fb\\u00e7\"}"
        if method == "PUT":
            assert choice == "{\"ShipName\": \"i\\u00dc\\u00df\\u00a7\\u00f1\\u00d1\\u00ab\\u00b5Mh7-f\\u00a7\\u00b9\\u00e3\\u00cb\\u00bc\\u201c\\u00ffp\\u2022$\\u2020\\u00a2\\u00f0\\u00c8\\u00dc\\u00deDr\\u2021\\u00ae\\u00d1Y\", \"ShipAddress\": \"\\u00b2\\u00edY\\u00b1\\u00c3{\\u2013Mu\\u00b5\\u0192\\u2014e\\u00cdV\\u009d\\u00a7L\\u00ca\\u00e4P\\u00a9\\u00d3yn1\\u2019\\u00c13\\u00f6\\u00c5+[\\u00f1\\u00cc\\u00a4\\u00f5\\u00f3\\u00ec4\", \"ShipCity\": \"s\\u00fbB\", \"ShipRegion\": \"\\u00e5\\u00a5\\u00c1\\u00b8\\u00f9\", \"ShipPostalCode\": \"\\u00b0\\u00c95\\u0090\\u00b8\\u00ce3D!\", \"ShipCountry\": \"y\\u00ee\", \"CustomerID\": \"\\u00f5\", \"CustomerName\": \"\\u00f5\\u2018\\u00ffD\\u00e3R \\u00f5.iH{\\u00ef\\u00e0\\u00fc\\u00bf\\u00f0N\\u00e8\", \"Address\": \"\\u00d9M\", \"City\": \"p+\\u00f0\\u00d4vB\\u00a3\\u00c9Q\\u00da\\u00c0\", \"Region\": \"\\u00c3!\\u00e7\\u00f6FH\\u00c0\\u00e1\\u00cb\\u00c2\\u00a1N\\u00eeD\", \"PostalCode\": \"\\u00fa\\u00f1\\u00cc\\u00aa\\u00f7\\u2018\\u00b2\", \"Country\": \"\\u00c7-a\\u00e6\\u00ca\\u00bc\\u00a1s\", \"Salesperson\": \"\\u00a9d\", \"OrderID\": 2129182719, \"OrderDate\": \"/Date(253402300799)/\", \"RequiredDate\": \"/Date(19409152909)/\", \"ShippedDate\": \"/Date(26957101723)/\", \"ShipperName\": \"\\u00ef_\\u00a3YU\\u00da=KI\\u00fc\\u00b2\\u00b4\\u00a4a\\u00c3S\\u00aa\\u00d1Dc\\u00a7G9l\\u00c7q\", \"ProductID\": 1798319544, \"ProductName\": \"i>\\u00efj\\u00bc\\u00fe\\u00ae\\u201c=F\\u00ced\\u00ea+<\\u00c3=\\u00ee\\u00f9\\u00fdG{5\\u00b1\\u008d\\u00b9Vr\", \"UnitPrice\": \"79189778900.5386m\", \"Quantity\": 26127, \"Discount\": \"3.0408649179978754e+20f\", \"ExtendedPrice\": \"14912852064.8759m\", \"Freight\": \"19750283220367.55m\"}"

    random.seed(10)
    for method in methodLists.keys():
        entities , queryable_factory = builder_with_restrictions(method)
        methodLists[method].clear()
        for queryable in entities:
            entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
            for _ in range(entityset_urls_count):
                q = queryable_factory(queryable, logger, 1)
                queries,body = q.generate()
                methodLists[method].append(body)
        
        choice = random.choice(methodLists[method])
        
        if method == "POST":
            assert choice == "{\"ProductName\": \"_\\u00d8\\u00d8\\u00c8\\u00e2ui!\\u00acT\\u00d2\\u00bb)Q\\u00e6\\u00cf\\u00d6d$C\\u00ac\\u00e0\\u00d6\\u00eam\\u00c8sI7\\u00daFJ\", \"SupplierID\": 829092798, \"CategoryID\": -1690973651, \"QuantityPerUnit\": \"\\u2122\\u00a3-`exT\", \"UnitPrice\": \"3483815661862.28m\", \"UnitsInStock\": -17798, \"UnitsOnOrder\": -22391, \"ReorderLevel\": -28014, \"Discontinued\": true, \"CategoryName\": \"\\u00fc\\u00a4\\u00f2\\u00b3(\"}"
        if method == "MERGE":
            assert choice == "{\"ProductSales\": \"192353423455.600m\"}"
        if method == "PUT":
            assert choice == "{\"SaleAmount\": \"78307108747750.81m\", \"OrderID\": 203510101, \"CompanyName\": \"h\\u201c.Kd\\u00fa\\u00e3\\u00ba$G\", \"ShippedDate\": \"/Date(28072299659)/\"}"