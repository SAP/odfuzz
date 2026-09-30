from pathlib import Path
import random
import os
import pytest

from odfuzz.restrictions import RestrictionsGroup
from odfuzz.entities import DirectBuilder
from odfuzz.fuzzer import SingleQueryable
from odfuzz.functionimport import FunctionImport


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
            q = queryable_factory(queryable)
            result = q.generate()
            assert result.url != ""


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
            q = queryable_factory(queryable)
            result = q.generate()
            queries_list.append(result.url)
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
            q = queryable_factory(queryable)
            result = q.generate()
            queries_list.append(result.url)
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
            q = queryable_factory(queryable)
            result = q.generate()
            queries_list.append(result.url)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Employees(EmployeeID=-847321771)?sap-client=500" == choice

def test_direct_builder_http_post_url():
    random.seed(20)
    post_entities , queryable_factory = builder("POST")
    queries_list = []
    queries_list.clear()
    for queryable in post_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            queries_list.append(result.url)
    queries_list=queries_list
    choice = random.choice(queries_list)
    assert "Products?sap-client=500" == choice

def test_direct_builder_body_generation():
    random.seed(20)
    dir_entities , queryable_factory = builder("PUT")
    body_list = []
    body_list.clear()
    for queryable in dir_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            body_list.append(result.body)
    assert random.choice(body_list) == "{\"EmployeeID\": -847321771, \"LastName\": \"\\u00af\\u2013\", \"FirstName\": \"]M\\u00cd\\u00c8q\\u00c0\", \"Title\": \">\\u00d9J\\u00c7\\u00c1:|\\u00cd\\u00d4\\u00fe!\", \"TitleOfCourtesy\": \"C\\u00e9\\u00a8\\u00e7\", \"BirthDate\": \"/Date(25670646156)/\", \"HireDate\": \"/Date(27987149575)/\", \"Address\": \"K\\u00d0\\u0152I\\u00d7Zn\\u00f7\\u00ed\\u00fdo\\u2022|\\u00ba\\u00f5\\u00cbh\\u00d06\\u00f0X\\u00b7vk\\u2020\\u00a9\\u00d7\\u00fb\\u2030\\u00b6\\u0192\\u009d\\u00f2kE\\u0153\\u2014\\u00d6i\\u00e0\\u00b9[c\\u00dc2\\u201c\\u00e0\\u00ce\\u2022f@\\u00e9DKYZ\", \"City\": \"l\", \"Region\": \"\\u00be\\u00e3S$zC\\u00f7\\u00ba\\u00d0\\u00a2\\u00b5\", \"PostalCode\": \"N\\u2013@\\u00f0\\u00e1\\u00fa o\\u00e5\", \"Country\": \"\\u00b07\\u00a7\\u00c0Gh\\u00c84\\u00c2yue\\u201d\\u00e8\", \"HomePhone\": \"7*fp\\u2122\\u2030[5K\\u00b2\", \"Extension\": \"\\u00d6\\u00e7C\", \"Photo\": \"YmluYXJ5JzY5NzYn\", \"Notes\": \"Ki\\u2022\\u00d5\\u00c8J\\u009d\\u00c8K\\u00ceo\\u00f4A\\u00c6\\u00cf\\u008d\\u2122\\u00fe\\u00ce\\u00ecq\\u00fabn\\u00e2i<I\\u00e3\\u00ea\\u00c2|\\u00df\\u00e4\\u2021\\u00f3\\u2014e\\u00f5\\u00e6\\u00f5\\u2026U\\u00d18\\u00b8!\\u00b4\\u00caE)q\\u00e7V\\u201d\\u00e9\\u00a8\\u00d1d\\u00fav\\u00d29)C\\u00ab\\u00c5\\u00f8\\u00a7\\u008f5\\u0192\\u0152\\u00e3U\\u00bfR\\u00e3c\\u00e3\\u00c6V\\u00f33|\\u2021\\u00ac\\u00c53v\\u00a47\\u00f9\\u00cb\\u00cb\\u201d\", \"ReportsTo\": -549769433, \"PhotoPath\": \"\\u00f6\\u00f8v)\\u00afT\\u00c8I\\u2021\\u008f\\u2026\\u00eaJk<^\\u00b4\\u2020\\u00d5\\u00be\\u00fd\\u00e3\\u00e8I\\u00f3\\u00ec\\u00f6\\u00c5\\u00d3\\u00f8>\\u00f9P\\u00a5\\u2020^\\u00df_\\u00b7+\\u00f0\\u00a9\\u00e2\\u00bf\\u2014\\u00ebX\\u00e5\\u00d2\\u00da:\\u00ee\\u00acLn\\u00ac\\u00c2B\\u00be\\u00c6\\u00f7q5\\u00f4\\u00d6cG\\u00c1`\\u00c46\\u00f5^\\u00f8x5\\u2022F\\u00b1\\u00c3)*r>\\u00a6\\u2122\\u2022\\u0152\\u2022+\\u00fb\\u00c1\\u00f3b\\u00f3\\u00c1\\u0153\\u00fe\\u2014>\\u00fc\\u00e2f\\u00d4\\u00baE*\\u00ce\\u00d8o\\u00b5\\u00e3\\u2021\\u00a4\\u2021\\u00a5*\\u00c1)\\u00b2D\\u00a2h\\u00caL\\u00f9\\u00ebk\\u00fd\\u00e4=\\u00e6\\u00a5\\u00f5\\u00ce\\u00c6H\\u2022\\u00c5\\u00da\\u00b6{\\u00a9p\\u00d4O\\u00f3\\u00barQ\\u00fc\\u00b5j\\u2122\\u00be\\u00c4\\u00f5\\u00c4\\u00b4\\u00e3\\u2013\\u00b1-hy\\u00ae\\u00fd\\u00fd\\u2013\\u00ff\\u00e6\\u00cc\\u00c1C2t\\u00fdF\\u00fe\\u0153\\u2122\\u00b0\\u00c1\\u00de9K\\u00ff\\u0192\\u00d3\\u00af6\\u00b8\\u00b7]\\u00d0+K\\u00c1\\u00f0\\u0090\\u00d9$|\\u00a8\\u00e9\\u00f1\"}"

def test_direct_builder_http_merge_body():
    random.seed(20)
    merge_entities , queryable_factory = builder("MERGE")
    body_list = []
    body_list.clear()
    for queryable in merge_entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            body_list.append(result.body)
    assert body_list[10] == "{\"ContactTitle\": \"li\\u00de:\\u2013Oi\\u00c3R\\u2026\\u00e0\", \"CompanyName\": \"*\\u00eeg*\\u00aa\\u00ec\\u00bdl\\u00df\\u00fapJ\\u00e4j\\u00ccK\\u00f7\\u00edR\\u00f4\\u00eee\\u2022\\u2013\\u00df\", \"Address\": \"SoA\\u2014=M\\u00c2F.\\u00d7\\u00db\\u00c9\\u00a4F\", \"City\": \"P\\u00fe\", \"ContactName\": \"\\u00f1\\u2122h\\u00f2n\\u00a1\\u008f\\u00a2\\u00fbT\\u00d6I\", \"Region\": \"*\\u0081b>\\u00bb\\u00ec\\u00b0*\\u00cd\\u00dd\\u00ff.\\u00de\", \"Country\": \"EQ\", \"Phone\": \"9\\u2013\"}"

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
                q = queryable_factory(queryable)
                result = q.generate()
                # Access the internal Query object's options_strings via url parsing
                # The result.url contains the full URL string; parse filter from it
                url = result.url
                # Extract $filter value if present
                if "$filter=" in url:
                    filter_part = url.split("$filter=")[1].split("&")[0]
                    option_list_filter_query.append(filter_part)

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
                q = queryable_factory(queryable)
                result = q.generate()
                url = result.url
                if "$orderby=" in url:
                    orderby_part = url.split("$orderby=")[1].split("&")[0]
                    option_list_orderby_query.append(orderby_part)

        if method == "POST" or method == "PUT" or method == "MERGE" or method == "DELETE":
            assert option_list_orderby_query == []
        else:
            assert "ProductID" not in option_list_orderby_query

@pytest.mark.parametrize('method_name,URI', [
    ("POST", "Products_by_Categories?sap-client=500"),
    ("MERGE", "Orders(OrderID=-487590680)?sap-client=500"),
    ("PUT", "Orders_Qries(OrderID=-74801719,CompanyName='%24%C2%B2')?sap-client=500"),
    ("DELETE", "Territories(TerritoryID='Pe%C3%BD%C3%AD%5B')?sap-client=500")
])

def test_direct_builder_Uri_unrestricted(method_name, URI):
    random.seed(30)
    entities , queryable_factory = builder(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            methodList.append(result.url)

    choice = random.choice(methodList)

    assert choice == URI

@pytest.mark.parametrize('method_name,Body', [
    ("POST", "{\"CategoryName\": \"bbV\\u201d\\u00d8\\u2021F*\", \"ProductName\": \"\\u00fb\\u00ddd1\\u00e9\\u00b0I\\u00ae\\u00a25$\\u201c6P\\u00c5*\\u00fd\\u00d3\\u00c0R0\\u00c2\\u00e9X\\u00d6xu\\u00af.\\u00c4gG`Z.C\\u0152\\u00e3\\u00c2\", \"QuantityPerUnit\": \"r\\u00afE1\\u00fe\\u00e4\\u00f3\\u00d7P8\\u00e8\\u00c2\\u2013\\u00af\", \"UnitsInStock\": 1724, \"Discontinued\": true}"),
    ("MERGE", "{\"Freight\": \"196583300759.8999m\", \"RequiredDate\": \"/Date(253402300799)/\", \"ShipVia\": 1580076080, \"ShipName\": \"\\u00a9Fk\\u00e7t\\u00d7\\u00de7@\\u00a3\\u00a7\\u00f9\\u00a9\\u00ff\\u00bcY\\u00bd\\u00d5\\u00d45\\u00b0!\\u00d9cS}\\u00a1Vg\\u00baq\\u00c3\\u00f6\\u00d4\\u2021\", \"OrderDate\": \"/Date(29884514773)/\", \"CustomerID\": \"\\u00d5\", \"ShipPostalCode\": \"gZ[\", \"ShipCity\": \"}<]B\\u00a5\\u00de\\u2021j\", \"ShipRegion\": \"1m\\u00f7\\u00a7\\u00dbq:\\u00fd\", \"ShipAddress\": \"\\u00e5\\u00b8\\u00ebP\\u00e1\\u00a8{H\\u00fb\\u00bbqdq\"}"),
    ("PUT", "{\"OrderID\": -74801719, \"CustomerID\": \"R\\u008f\", \"EmployeeID\": -1924929169, \"OrderDate\": \"/Date(7406226575)/\", \"RequiredDate\": \"/Date(4382242045)/\", \"ShippedDate\": \"/Date(14154596310)/\", \"ShipVia\": 182879621, \"Freight\": \"1770947247616.09m\", \"ShipName\": \"\\u0152\\u00ff\\u00d5+\\u00c1Y\\u2018\\u00ee\\u00c7i\\u00c5q\\u0152G\\u00eb}\\u00ab\\u00f9b\\u00bc\\u00f8^p\\u00da\\u00eceC\\u00b2\\u00bf\\u00bb\\u00bb\\u00d2p)\\u00a5\\u00a4n\", \"ShipAddress\": \"\\u00ca\\u00a2]\\u00eaY\\u2026\\u00beFZ\\u00c1)\\u00e4=o\\u00b1X\\u00f0\\u0153_\\u00f3\\u00d8\\u00e3\\u00a8\\u00d5\\u00d3\", \"ShipCity\": \"G\\u00c1\\u2020\\u00bekz\\u00aa\\u00b9\\u00c6\\u00e8\\u00c2 \\u00d3\", \"ShipRegion\": \"z\\u00c2(SgB\\u201d\\u2030\", \"ShipPostalCode\": \"q\\u00b6\\u00ea\\u00d3\", \"ShipCountry\": \"yR\\u00eeD\", \"CompanyName\": \"$\\u00b2\", \"Address\": \"n\\u00b4g\\u00eag\\u00b6e\\u2030\\u00ee\\u00dd\\u00b1\\u00f2Ik\\u00eb\\u00fd\\u00f7\\u00a5\\u00a9\\u00bat\\u00b6\\u00a63t7\\u00a1J\\u00cd\\u2021\\u00c1\\u00c5X\\u00b1\\u00a5j\\u00e2\\u00cfs\\u00c1\\u00fbi\\u0192\\u00d7\\u2013=\\u00ed\\u2020\\u00c8\\u2026\\u00f2 \\u00a4Q\\u01923\", \"City\": \"\\u00c24m\\u00feH\\u2018:]M\", \"Region\": \"b\\u00b2\\u00eb\\u2014\\u00f9\\u00f0c\", \"PostalCode\": \"|\\u00f6\", \"Country\": \"\\u00f96\\u00efK\\u2013\\u00c4\\u00bfR\\u00de\\u00bf\"}")
])

def test_direct_builder_body_unrestricted(method_name, Body):
    random.seed(30)
    entities , queryable_factory = builder(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            methodList.append(result.body)

    choice = random.choice(methodList)

    assert choice == Body

@pytest.mark.parametrize('method_name,URI', [
    ("POST", "Orders_Qries?sap-client=500"),
    ("MERGE", "Territories(TerritoryID='%C3%A7%C3%B9eq%C3%A1%C3%BCl%5E%3AGn%C3%B5S_%C3%89Q')?sap-client=500"),
    ("PUT", "Alphabetical_list_of_products(ProductID=1951986690,ProductName='F%C3%8BLH%C3%83%C3%96%C3%B2%7B%E2%80%A6%C5%92%C3%9F%C2%BDeV%C3%A7z%C2%9D%C3%B3lVJC%C2%A1T%C3%AE%C3%A9%7B%C2%B8%C2%A4%C3%ADb%C2%AA%C2%B1',Discontinued=true,CategoryName='%C3%8CFR%28c%C2%B1%29I')?sap-client=500"),
    ("DELETE", "Suppliers?sap-client=500")
])

def test_direct_builder_Uri_unrestricted(method_name, URI):
    random.seed(10)
    entities , queryable_factory = builder_with_restrictions(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            methodList.append(result.url)

    choice = random.choice(methodList)

    assert choice == URI

@pytest.mark.parametrize('method_name,Body', [
    ("POST", "{\"OrderID\": 2033125339, \"CustomerID\": \"\\u00d0\", \"EmployeeID\": 119981761, \"OrderDate\": \"/Date(14672560418)/\", \"RequiredDate\": \"/Date(253402300799)/\", \"ShippedDate\": \"/Date(253402300799)/\", \"ShipVia\": -2138149459, \"Freight\": \"11425516230949.02m\", \"ShipName\": \"F+\\u00f7v*\\u00cf\\u2022!\\u00c2\\u00a7\", \"ShipAddress\": \"\\u00b7M\\u00a5\\u00ddI2L\\u00c8\\u2021\\u2026\\u00e0\\u00ca\\u00a98C\\u00efx\\u0153\\u00d9d\\u00e0\\u2014n\\u00de\\u2018\\u00faAs\", \"ShipCity\": \"\\u2022b\\u00c9\\u00ca:\\u00cd\", \"ShipRegion\": \"\\u00f0\\u00b6lO\\u0192\\u00ef\\u00d6F\\u00bc\\u00ee\", \"ShipPostalCode\": \"j\\u00d5\\u00b4\\u00bdJ\", \"ShipCountry\": \"n\\u00f1`\\u00d5^\\u00c5\\u00ef\\u00a2\\u00feDT\", \"CompanyName\": \"\\u0192Y\\u00c66\\u00fe]zT\\u008f\\u00e1\\u00b4eHKmu6\\u00d4\\u0153\", \"Address\": \"4{\\u00bf\\u00d1\\u2019\\u00c9\\u00f4\\u00fa\\u00eai\\u0152k\\u2013\\u2021\\u00dc\\u00b8\\u00a8y\\u00b5B]\\u00beu\\u00c5\\u00d62\\u00ca\\u00f8\", \"City\": \"\", \"Region\": \"\\u00e1\\u00beD\", \"PostalCode\": \"\\u00afC\\u00bc\\u00d8\\u00b8F\\u00cfob\", \"Country\": \"\\u00ee\\u00ed\"}"),
    ("MERGE", "{\"TerritoryDescription\": \"\\u2020\\u00bb\\u00e7\\u00fc\"}"),
    ("PUT", "{\"ProductName\": \"F\\u00cbLH\\u00c3\\u00d6\\u00f2{\\u2026\\u0152\\u00df\\u00bdeV\\u00e7z\\u009d\\u00f3lVJC\\u00a1T\\u00ee\\u00e9{\\u00b8\\u00a4\\u00edb\\u00aa\\u00b1\", \"SupplierID\": 121329056, \"CategoryID\": -185397071, \"QuantityPerUnit\": \"<iG\\u00c5z\\u00c0d\\u0152^\\u00ebde(\", \"UnitPrice\": \"394759704486.52m\", \"UnitsInStock\": -2190, \"UnitsOnOrder\": -6939, \"ReorderLevel\": -20366, \"Discontinued\": true, \"CategoryName\": \"\\u00ccFR(c\\u00b1)I\"}")
])

def test_direct_builder_body_unrestricted(method_name, Body):
    random.seed(10)
    entities , queryable_factory = builder_with_restrictions(method_name)
    methodList = []
    for queryable in entities:
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties())
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable)
            result = q.generate()
            methodList.append(result.body)

    choice = random.choice(methodList)

    assert choice == Body