import logging
from pathlib import Path

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
