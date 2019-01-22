# ODfuzz
The fuzzer for testing applications communicating via the OData protocol.

ODfuzz randomly selects entities that are **queryable**, thus, the entities which can be used in query options $filter, $orderby, $skip, and $top. For each entity, there is generated a set of query options, and final result is dispatched to OData service. Responses from the OData service are stored in a database and used for the further analysis and generation. ODfuzz creates valid requests that contain **random data** at specific places. Learn more at [Excel@Fit 2018](http://excel.fit.vutbr.cz/submissions/2018/004/4.pdf).

Example of generated queries:
```
ValueHelpPrinters?$filter=Location eq '~' and Location eq '>'&sap-client=500&$format=json
C_PaymentAdviceSubItem?$orderby=Reference1IDByBusinessPartner asc&$filter=IsActiveEntity eq false or (PaytAdviceAccountTypeForEdit ge '' or ((substringof(PaymentDifferenceReasonName, '¾JÓaÉ—bÈ¢æû´Ò>«') eq true and PaymentAdviceItem ne 'Û') and substringof(PaymentDifferenceReasonName, 'Åª•õõÿOaÞ¯@Vþ') eq true or Currency ne '9') and PaytAdviceAccountTypeForEdit lt '' and PaymentAdviceSubItemForEdit lt '8') or GrossDeductionAmountInPaytCrcy ne 948074290.8m and endswith(PaytDifferenceReasonExtCode, '‰') eq false and PaymentAdviceAccountType lt ''&$skip=1957273783&sap-client=500&$format=json
C_PaymentAdvice?$top=869&$filter=IsActiveEntity eq false or CashDiscountAmountInPaytCrcy eq 1919771231157915484160m&sap-client=500&$format=json
SupportedChannelSet(Event='Øt',VariantId='V',CorrespondenceTypeId='M.õ')?$filter=CorrespondenceTypeId ge '¨·æ' and (CorrespondenceTypeId gt 'õZ' or CorrespondenceTypeId lt '§Å') or CorrespondenceTypeId ge 'Æ'&sap-client=500&$format=json
CorrespondenceTypeSet(Event='SV',VariantId='',Id='×´Õ•')/SupportedChannelSet?$filter=(CorrespondenceTypeId eq '' and CorrespondenceTypeId ne 'ÿNœä' and CorrespondenceTypeId eq '£' or CorrespondenceTypeId ge 'ÏØà†' and CorrespondenceTypeId eq '¥C') and CorrespondenceTypeId ne 'À'&sap-client=500&$format=json
C_Cpbupaemailvh?$top=81&$skip=245&sap-client=500&$format=json
C_Cpbupaemailvh?$top=81&$filter=ContactPerson eq 'Ý¿â†' and (RelationshipCategory ne '' or RelationshipCategory eq ':7S6]') or ContactPerson lt 'Í' and RelationshipCategory ne '¹Ú•°¼m' or startswith(BusinessPartner, 'ù£f¨') eq false or ContactPerson le 'di©h¶'&$skip=245&sap-client=500&$format=json
```

#### Requirements
- [Python 3.6](https://www.python.org/downloads/)
  - [Requests 2.18.4](http://docs.python-requests.org/en/master/)
  - [Gevent 1.2.2](http://www.gevent.org/)
  - [PyMongo 3.6.1](https://api.mongodb.com/python/3.6.1/)
  - [lxml 3.7.3](https://github.com/lxml/lxml)
  - [PyOData](https://github.wdf.sap.corp/I342520/ODfuzz/tree/master/pyodata)
- [mongoDB 3.6](https://www.mongodb.com/)
- [PivotTable](https://github.wdf.sap.corp/I342520/Pivot)

## Setup
Clone this repository:
```
$ git clone https://github.wdf.sap.corp/I342520/ODfuzz && cd ODfuzz
```

### Docker
1. Execute the following command to build a docker image:
```
$ sudo docker build -t odfuzz:1.0 .
```
2. Run the container:
```
$ sudo docker run --dns=10.17.121.71 -ti odfuzz:1.0
```

### Manual
1. [Download](https://www.mongodb.com/download-center#community) and [install](https://docs.mongodb.com/manual/administration/install-community/) the mongoDB server on your local machine.
2. [Download](https://github.wdf.sap.corp/I342520/Pivot) or clone a custom implementation of the Pivot table:
```
$ git clone https://github.wdf.sap.corp/I342520/Pivot
```
3. Install all python requirements:
```
$ pip install -r requirements.txt
```

## Run configuration
To access OData services introduced in SAP, it is required to set the following **environment variables** in your system. The fuzzer will use these variables for a **basic authentication**.
```
export SAP_USERNAME=Username
export SAP_PASSWORD=Password
```

Command line arguments
```
$ python3 fuzzer.py --help
positional arguments:
  service               An OData service URL
optional arguments:
  -h, --help            Show this help message and exit
  -l LOGS, --logs LOGS  A logs directory
  -s STATS, --stats STATS
                        A statistics directory
  -r RESTR, --restr RESTR
                        A user defined restrictions
  -t TIMEOUT, --timeout TIMEOUT
                        A general timeout in seconds for a fuzzing
  -c USERNAME:PASSWORD, --credentials USERNAME:PASSWORD
                        User name and password used for authentication
  -a, --asynchronous    Allow ODfuzz to send HTTP requests asynchronously
  -f, --first-touch     Automatically determine which entities are queryable
  -p, --plot            Log response time and data, and create a scatter plot
```

### Runtime
ODfuzz runs in an **infinite loop**. You may cancel an execution of the fuzzer with a **keyboard interruption** (CTRL + C).

### Output
Output of the fuzzer is stored in the user defined directories (e.g. logs_directory, stats_directory) or in a working directory. ODfuzz is creating stats about performed experiments and tests:
- Pivot
    - These stats are continuously extended with the latest data while the fuzzer is running.
    - Stats are loaded into CSV files and may be visualised by the javascript Pivot table. See [README](https://github.wdf.sap.corp/I342520/Pivot/blob/master/README.md) to learn more.
- Simple
    - Requests that triggered an internal server error (HTTP 500) are written into multiple *.txt files. Name of the file is the name of the corresponding entity set in which the error occurred.
    - Runtime stats are saved to the *runtime_info.txt* file. This file contains various runtime information such as a number of generated tests (HTTP GET requests), number of failed tests (status code of the response is not equal to HTTP 200 OK), number of tests created by a crossover and number of tests created by a mutation.
- Plotly
    - Response time and data count are continuously logged.
    - Data are stored in the *data_responses.csv* file. When the fuzzer ends, an interactive scatter plot is built via plotly library. The scatter plot is viewable by any conventional web browser. Learn more about [plotly](https://plot.ly/python/line-and-scatter/).

When a connection is forcibly closed by a host (e.g. user was disconnected from VPN), ODfuzz ends with an error message, but still creates all necessary stats files.

##### Console output
Brief information about the runtime is also printed to a console. Find below an example of such an output.

```
Collection: FI_CORRESPONDENCE_SRV-56482b5e-b76d-46eb-9f48-e13d1fe8eea2
Initializing queryable entities...
Connecting to the database...
Fuzzing...
Generated tests: 1300 | Failed tests: 27 | Raised exceptions: 0
```

*Collection* represents a name of a collection associated with mongoDB. *Raised exceptions* describes a number of raised exceptions within the runtime, for example, connection errors.

#### Docker
The output of ODfuzz is written into running instance of docker image by default. If you want to view the output on the host system, you are required to use the additional **-v** option and run the docker image as follows:
```
sudo docker run --dns=10.17.121.71 -v /host/absolute/path:/image/absolute/path -ti odfuzz:1.0
```
Taking this into account, you have to set the fuzzer's output directories to /image/absolute/path as well. For more, visit https://docs.docker.com/storage/volumes/.

## Usage
1. Run the fuzzer, for example, as:
```
python3 fuzzer.py https://ldciqj3.wdf.sap.corp:44300/sap/opu/odata/sap/FI_CORRESPONDENCE_V2_SRV -l logs_directory -s stats_directory -r restrictions/basic.yaml -a -f -p
```

The option **-a** enables fuzzer to send asynchronous requests. A default number of the asynchronous requests can be changed. To do so, navigate to the file *config/fuzzer/fuzzer.ini* and modify value *pool*. Notice that some services do not support more than 10 asynchronous requests at the same time.

2. Let it run for a couple of hours (or minutes). Cancel execution of the fuzzer with CTRL + C.
3. Browse overall stats, for example, by the following scenario:
    - You want to discover what type of queries triggers undefined behaviour. Open the *stats_overall.csv* file via [Pivot](https://github.wdf.sap.corp/I342520/Pivot). Select entities you want to examine, select an HTTP status code you want to consider (e.g. 500), select names of Properties, etc. You may notice that the filter query option caused a lot of errors. Open the *stats_filter.csv* file again via [Pivot](https://github.wdf.sap.corp/I342520/Pivot) to discover what logical operators or operands caused an internal server error.
    - Queries which produced errors are saved to multiple files (names of the files start with prefix *EntitySet_*). These queries are considered to be the best by the genetic algorithm eventually. Try to reproduce the errors by sending the same queries to the server in order to ensure yourself that this is a real bug.
    - Open SAP Logon and browse the errors via transactions sm21, st22 or /n/IWFND/ERROR_LOG. Find potential threats and report them.

NOTE: ODfuzz uses a custom header **user-agent=odfuzz/1.0** in all HTTP requests. You may be able to filter the internet traffic based on this header.

### Restrictions
With restrictions, a user is able to define rules which forbid a usage of some entities, functions or properties in queries. Restrictions are defined in the following YAML format:
```
[ Exclude | Include ]:
    [ $FORBID$ ]:
        - $filter
        - $orderby
        ...
    [ $filter | $orderby | $skip | $top | $expand | ... ]:
        EntitySet name:
            - Property name
            - Property name
            ...
        [ $ENTITY_SET$ | $ENTITY$ | $ENTITY_ASSOC$ | $F_ALL$ | $P_ALL$ | ... ]:
            - [ Function name | EntitySet name | Property name ]
            ...
```

Sample restrictions files can be found in the *restrictions* folder. Use *odata_northwind.yaml* restrictions file for [Northwind OData service](http://services.odata.org/V2/Northwind/Northwind.svc/).

Bear in mind that some restrictions are related to the previous version of ODfuzz. Therefore, the keyword "$E_ALL$" is deprecated. In this specific case please, use the keyword "$ENTITY_SET$".

##### Why are we using restrictions at all?
OData services does not support some functions provided by the OData protocol (for example, day(), substring(), length()) or does not implement GET_ENTITYSET methods for all entities. By using the restrictions, one can easily decrease a number of queries that are worthless. Also, some services may implement handlers only for the $filter query option but does not declare that in the metadata document. Therefore, other query options cannot be used within the same request, otherwise various types of errors are produced (e.g. System query options '$orderby,$skip,$top,$skiptoken,$inlinecount' are not allowed in the requested URI). 

### Limitations
At the moment, ODfuzz can mutate only values of types Edm.String, Edm.Int32 and Edm.Guid. It is planned to support more types in the future.

The fuzzer was developed for testing the SAP applications. These applications use different order of function parameters within the filter query option. To change the order of the parameters, it is unavoidable to modify source code that generates such functions. The same rule applies for functions that can be implemented in two different ways, like the function substring() which can take 2 or 3 parameters.

ODfuzz creates a new collection in the database at each run. To preview database, run `mongo` in a terminal and select a corresponding database via `use odfuzz`. Run the command `db.getCollection("COLLECTION-NAME").find({}).pretty()` in the mongoDB shell in order to access and browse a particular collection. To delete all collections, run the command `db.dropDatabase()`.


ODfuzz may be used to test OData services outside the SAP network. There are two ways to enable ODfuzz to work on such services:
1. You **do not know** a path to the particular HTTPS certificate:
    - Change the **has_certificate** parameter at line [38](https://github.wdf.sap.corp/I342520/ODfuzz/blob/master/odfuzz/fuzzer.py#L38) to **False**. 
    - Set the following environment variable to suppress warning messages (InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised.):
        ```
        PYTHONWARNINGS=ignore:Unverified HTTPS request
        ```
2. You **do know** the path of the HTTPS certificate:
    - change line [8](https://github.wdf.sap.corp/I342520/ODfuzz/blob/master/odfuzz/constants.py#L8).

#### TODO
- Add heuristics for generators based on associations.
- Create a database of valid inputs, e.g. for 'Language', 'Location', etc. (may be defined in restrictions file).
- Add unit tests. (30% done)
- Use RotatingFileHandler instead of FileHandler in logging.
- Add support for the sap:display-format attribute. This attribute helps to determine whether a property is a type of integer or a string. For example, property FiscalPeriod is type of Edm.String with attributes MaxLength="3" and sap:display-format="NonNegative". This means that the property holds a non-negative integer value which is converted to the string.
- Add support for function imports.
- Add option for generation of invalid values.
- Create a database of test cases (e.g. invalid UTF-8 characters) that triggered an undefined behavior in the past.
- Random data sampling introduced by mongoDB cannot be reproduced by a seed.
