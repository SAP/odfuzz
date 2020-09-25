import logging
import sys
import os
from odfuzz.restrictions import RestrictionsGroup
from odfuzz.entities import DirectBuilder
from odfuzz.fuzzer import SingleQueryable
from pip._vendor.html5lib.constants import entities
sys.path.append("\\Users\\I516382\\eclipse-workspace\\Jepper\\src")
# import replacer
print(os.environ)
os.system("cls")
py_version = sys.version
metadata = open("\\Users\\I516382\\eclipse-workspace\\Jepper\\src\\metadata.xml","r").read()
urls_per_property=10
logger = logging.getLogger("fioridast")
logger.setLevel(logging.CRITICAL)
restrictions = RestrictionsGroup(None)

# restrictions = RestrictionsGroup(None)
# builder = DirectBuilder(metadata, restrictions)
# entities = builder.build()
# queryable_factory = SingleQueryable
# queries_for_fioridast = []
# queries_for_fioridast.clear()
# for queryable in entities.all():
#     entityset_urls_count = len(queryable.entity_set.entity_type.proprties()) * urls_per_property
#     for _ in range(entityset_urls_count):
#         q = queryable_factory(queryable, logger, 1)
#         queries = q.generate()
#         queries_for_fioridast.append(queries[0].query_string)
# print ("a")
# queries_for_fioridast=set(queries_for_fioridast)
# for i in queries_for_fioridast:
#     print(i)

# print(entities)
os.environ["ODFUZZ_IGNORE_METADATA_RESTRICTIONS"]="True"
methods=["GET","DELETE"]
def buildqueries(metadata,restrictions,method):
    builder = DirectBuilder(metadata, restrictions,method)
    entities = builder.build()
    queryable_factory = SingleQueryable
    queries_for_fioridast = []
    queries_for_fioridast.clear()
    for queryable in entities.all():
        entityset_urls_count = len(queryable.entity_set.entity_type.proprties()) * urls_per_property
        for _ in range(entityset_urls_count):
            q = queryable_factory(queryable, logger, 1)
            queries = q.generate()
            queries_for_fioridast.append(queries[0].query_string)
    queries_for_fioridast=set(queries_for_fioridast)
    for i in queries_for_fioridast:
        print(i)
    

for i in methods:
    buildqueries(metadata,restrictions,method=i)
    print(i)
