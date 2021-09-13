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
    assert "Employees(EmployeeID=-1187303908)?sap-client=500" == choice

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
    assert "Sales_Totals_by_Amounts?sap-client=500" == choice

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
    assert random.choice(body_list) == "{\"EmployeeID\": -1187303908, \"LastName\": \"\\u2021\\u0152\\u0153\\u00e3d\\u00a9\\u00dd\\u00a7\\u00ab\\u00d4\\u00f56\", \"FirstName\": \"\\u00e1(P\\u2122\\u00a9\\u00a5d\\u00d3}n\", \"Title\": \"\\u00d7\\u2020\\u00e6 \\u2018\\u00f6V\\u00c1\\u00e5\\u00db\\u2013\\u00cc\\u00cc\", \"TitleOfCourtesy\": \"\\u00ba\\u2026\", \"BirthDate\": \"/Date(251388392975)/\", \"HireDate\": \"/Date(78762567516)/\", \"Address\": \"\\u00eefI\\u00cd\\u009dJ\\u00f2\\u00fa\\u201d\\u00da\\u00dc\\u00b4sn>\\u00da\\u00d0\\u008f\\u00b23\\u00ac]=\\u009d[\\u00abQ}7\\u00a6\\u201ct\\u00acT\\u0090\\u00f3vt\\u00db\\u00fbQE8B|34\\u00c5\\u00c4\\u009d}\\u00b5:\\u00d9\\u00a1nR\", \"City\": \"C\\u00e7\\u00a3\\u00a2\\u00bc\", \"Region\": \"L-\\u00d4E\\u00db\\u00f7)4`Ef\", \"PostalCode\": \"\\u00dem\", \"Country\": \"E\", \"HomePhone\": \"\\u00b2\\u00a6OR\\u00fbLrcI\\u00bc\\u00f6\\u00efy6\\u00ab\", \"Extension\": \"k\\u00d1\", \"Photo\": \"WCdiRic=\", \"Notes\": \"\\u00f6\\u00b5[V\\u20209n\\u00b1\\u00fcf\\u00a3\\u00ec\\u00daf\\u00ce\\u00ec`\\u2026\\u00ae\\u2021\\u00cf9A\\u00b3\\u00f1_\\u00ce\\u008f\\u00db\\u00b6\\u00f1\\u0153\\u00b5e.\\u2030\\u00b9\\u2014K\\u00f7kz-\", \"ReportsTo\": 14526380, \"PhotoPath\": \"c\\u008dY\\u00c2ah\\u00db0\\u00e3.<\\u00fa\\u00da\\u00a6xdM$7\\u00a5\\u2026 GN:r5+u\\u00db\\u00d2!\\u00bc\\u00c8\\u00cf\\u2019\\u00b6{\\u00c3\\u00cf9\\u20192\\u00cc\\u2020O\\u00d4\\u00df\\u00ed\\u00f1\\u00dc\\u00ee.\\u00f8\\u00eb\\u00da\\u00d5\\u00c4f\\u00e8\\u00calR\\u00da\\u00bf\\u00b3\\u00c1\\u00ca*\\u00a8\\u0081\\u00d7t\\u00b7-@\\u00da\\u00c1n\\u00d6EXF\\u2018\\u00dc1\\u00c7\\u00f6\\u00ec\\u00efIp\\u00dd\\u201dq\\u00cb1\\u00c8O\\u00d5\\u00c8\\u2122\\u2022\\u00a5>\\u00a4\\u00c9O\\u00cf@P=4.\\u00ac\\u00dd\\u00f3\\u00a9\\u00cflu\\u00aa\\u00a5:\\u00b7\\u00f6VhE\\u00f0\\u00f6u\\u00a7-\\u2022\\u00aap\\u2019\\u00ea\\u00f1@\\u00c3xvp\\u00c2O0$F\\u00bf\\u00ae\\u00df\\u00d4N\\u0081\\u00feD\\u00cb\\u00f9\\u00d6\\u00d4!\\u00f7v\\u00e9\\u00c3Z\\u00a1\\u00eb\\u00de5--\\u00bd9S|\\u00c7\\u00f4\\u00f3O\\u00a95.\\u00dc\\u00e2\\u00aau.\\u00b1\\u00fb\\u00f8y\\u00f5\\u00da\\u00d3\\u00fa\\u00a6(\\u00c3i\\u00c1=\\u00b0\\u201c\\u00b5r\\u00dd\\u00bcU\\u00fd\\u00eaTAK\\u00ab\\u00d1u\\u00ec\\u00d9\\u00f1\\u00c1\\u00b8@\\u00d7\\u00d2S\\u00a2\\u00ccDg=|\\u00c1\\u201d\\u00dcmXaJuN_\\u00aa\"}"

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
    assert body_list[10] == "{\"Region\": \"\\u00f6\", \"ContactName\": \"\\u00a1\\u008f\\u2014\\u00e0\\u0192\\u00e6RZK\\u00bfoK-[@V\", \"Fax\": \"[|\\u00a4\\u00e0Zu\\u008f\\u00a1a\\u00efnIL=\\u00d5\\u00e6T\", \"PostalCode\": \"\\u00b61\\u0081B\\u00f9B\\u00a7\", \"CompanyName\": \"\\u00b3s\\u00f3\\u00a91\\u00b5\\u00d7\\u0081\\u00e5G\\u00ca\\u00a7o0\\u00f9\", \"Country\": \"\\u00a1\\u00d4\", \"City\": \"l]_\\u00eas\\u0090\\u00f6\\u00ff\", \"Address\": \"(F\\u00ca\\u00a4[R\\u00a7\\u00b7kT\\u00f2\\u00ef\\u2022\\u00bbd\\u00c4see\\u00cb\\u00a7y\\u2030}L6\\u2122c\\u00b4C\\u00db\\u00d1\\u00b6\\u00b1\\u00aa\\u00bc+8\\u00e2[\\u00aa^-c\\u00c6`\\u00ff\\u0081\\u00aa\", \"ContactTitle\": \"\\u00dd\\u00b5q\\u00f9\\u00bbd$E\\u0192a\\u00d0>\\u00de\\u00c8b\\u00f2u\\u00dc\\u00c1P\\u2030\"}"

def test_function_imports():
    random.seed(10)
    path_to_metadata = Path(__file__).parent.joinpath("metadata-northwind-v2.xml")
    function_import_list = FunctionImport.get_functionimport_list(path_to_metadata.read_bytes())
    fuzzed_fi = FunctionImport.generate_queries_for_functionimport(function_import_list[0])
    assert fuzzed_fi == "DuplicateCategory?CategoryName='%C2%AA%C2%BA%C3%92d2%C2%B5%C2%BC%E2%80%94%C3%A6Qi%C3%84%C2%BC%C2%81t%5E%C3%BD%E2%80%98l%C2%A7K%C3%99%C2%8F%E2%80%9D%C2%A7%3D%C3%AB_%C2%B2T%C3%AE%3C%C3%A8%E2%80%98J%C2%B2%24%C2%AE%C3%9C%E2%80%9Cl%C3%94b%21JZ%3C%C3%88%E2%80%99%24%E2%80%B0%C3%A9%C3%8B%C2%B1%C2%AC%C2%B7q%C3%A6%C3%94%C2%81%C2%BFP7%C2%A5%24ji%C2%BE%3C%C3%9A%C3%A7s%C3%87uN%E2%80%A2%C3%90%60%C3%98NDz%C2%AFRY%C2%8D%C2%AB%C2%A6%C2%B0%40%C3%AD%E2%80%93L%C3%9D%C3%84UF%2B%C2%B2%3CR%C3%A8%C3%A5TU%C2%B9%C5%92%C2%81%C2%AC7b%C3%8A%C3%B5l%C6%92%C2%A8%40u_%C2%B0%C2%A3%C3%94P%E2%84%A2%C2%BD%C3%AB%24%C3%BB%C3%85-%C3%84%C2%BA%C3%99%C2%BEqR%C2%BC%C3%AB%C2%B5%C2%A2J%C2%A7%C3%89%C3%94%C2%8D%C3%88'&DuplicateName='%C3%B2R%C3%8E%C2%AEA%C2%A6ja%C2%AE%C3%88qm%C2%8DyNC%C3%9A%C2%B2%C2%BBK%C2%B3%C2%AC%C2%BF%C2%B0%E2%80%A1%C3%B8%29%C3%B1%C2%B3%C2%A9%C6%92%C3%A5%C3%84%C3%84O%C3%BC%21%C5%93%C3%9Di%C3%AE0%C3%A3%C3%95%C3%92%C3%9F%C2%B9gE%7C%C2%AC%5E%C3%B6%5Dxl%C3%97%C3%8BC%5BQ%C3%AA%C2%B9L%E2%80%98%C3%97%C2%A2Z%C2%8DVu%C3%96Z%C2%AA3z%C3%AE%3E%C2%B5%C3%BD%C3%BF%C3%B0%C3%84%C3%B7%C2%A9%C2%B0%C3%A9%C3%BD%C3%8D3%2B%C3%97%E2%80%99E%C3%9F%C3%9Fb3%C2%A9'&DuplicationComment='%E2%80%9D%C3%A51r%C2%A9xo%C2%8D%28%E2%80%98%C2%B2%C2%A9%7DZ%C3%9F%C3%BE%3D%C2%B6%C3%B0%7C%C3%80%C2%BE%C3%80_%C2%A3%C2%AF%C3%A2%E2%80%A1%C2%8D%C3%B8%E2%80%93%C2%BA%C2%B0%C2%B9%C3%95%C2%B9v%C3%AF%C3%89%C3%B7%E2%80%99%C3%B7%C2%A3S%C3%99%C2%A6%C3%B7%C3%8Fq%C3%97%C3%BA%3Ee%C3%96%C2%81%C3%A5%C5%93s%C3%BC%C2%A1%C3%9B%60%3D%C3%9AX%24S%3Ez%C3%8Dn6%C3%90%C3%BDs%C2%A7Z%C3%90%C3%91%C2%AE%C3%96e%C2%9D1%E2%80%A0%C3%92Y%C3%84%C3%8F%20%C2%81m%C3%A7%C3%B0%C3%93mj%C3%8F%E2%80%99%C2%A1%C2%81%C3%98%C3%A2SPF%C3%9A%C5%92Rh%C3%B8%C3%88%C3%81%C2%8Dx%C2%A1%C2%AE%C3%92%C2%8DpM%C2%AF%C3%B3%C2%B7%C3%9B%C2%B1%C3%B7%C2%AF%C3%99T%C2%8F%C2%A9%E2%80%A1%C3%8E%C3%82%C2%B3%E2%84%A2Zz%C2%AB%C3%A3OkX%C3%A2%C3%A1Y%C3%90%C2%AA%E2%80%98%C3%8E%E2%80%9Cm%C3%99nR'&DeleteOriginal=true"
