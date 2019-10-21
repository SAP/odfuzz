[![Build Status](https://travis-ci.com/SAP/odfuzz.svg?branch=master)](https://travis-ci.com/SAP/odfuzz)
[![codecov](https://codecov.io/gh/SAP/odfuzz/branch/master/graph/badge.svg)](https://codecov.io/gh/SAP/odfuzz)

# Odata service fuzzer - odfuzz
The fuzzer for testing applications communicating via the OData protocol.

Odfuzz randomly selects entities that are **queryable**, thus, the entities which can be used in query options $filter, $orderby, $skip, and $top. For each entity, there is generated a set of query options, and final result is dispatched to OData service. Responses from the OData service are stored in a database and used for the further analysis and generation. Odfuzz creates valid requests that contain **random data** at specific places. Learn more at [Excel@Fit 2018](http://excel.fit.vutbr.cz/submissions/2018/004/4.pdf).

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
For running the tool:

- [Python 3.6+](https://www.python.org/downloads/)
- [mongoDB 3.6+](https://www.mongodb.com/)

 
## Setup
1. Clone this repository:
```
$ git clone https://github.com/SAP/odfuzz && cd odfuzz
```
2. Install the fuzzer:
    1. Docker
        1. Execute the following command to build a docker image:
        ```
        $ sudo docker build -t odfuzz:1.0 .
        ```
        2. Run the container:
        ```
        $ sudo docker run --dns=10.17.121.71 -ti odfuzz:1.0
        ```

    2. Manual
        1. [Download](https://www.mongodb.com/download-center#community) and [install](https://docs.mongodb.com/manual/administration/install-community/) the mongoDB server on your local machine.
        3. Create an executable script:
        ```
        $ python3 setup.py install
        ```


## Run configuration
To access OData services introduced in SAP, it is required to set the following **environment variables** in your system. The fuzzer will use these variables for a **basic authentication**.
```
export SAP_USERNAME=Username
export SAP_PASSWORD=Password
```

If necessary, it is possible to specify the username and the password via command line arguments. Take a look at the optional arguments:
```
$ odfuzz --help
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
  --fuzzer-config FUZZER_CONFIG
                        A configuration file for the fuzzer
  -a, --asynchronous    Allow odfuzz to send HTTP requests asynchronously
  -f, --first-touch     Automatically determine which entities are queryable
```

### Runtime
Odfuzz runs in an **infinite loop**. You may cancel an execution of the fuzzer with a **keyboard interruption** (CTRL + C).

### Output
Output of the fuzzer is stored in the directories set by a user (e.g. logs_directory, stats_directory) or in a current working directory. Odfuzz is creating stats about performed experiments and tests:
- Pivot
    - These stats are continuously extended with the latest data while the fuzzer is running.
    - Stats are loaded into CSV files and may be visualised by the javascript Pivot table. See [Pivot README](tools/pivot/README.md) to learn more. Also, in the pivot table, there is a **hash** value which is mapped to the corresponding URL located in the file *urls_list.txt*.
- Simple
    - Requests that triggered an internal server error (HTTP 500) are written into multiple *.txt files. Name of the file is the name of the corresponding entity set in which the error occurred.
    - Runtime stats are saved to the *runtime_info.txt* file. This file contains various runtime information such as a number of generated tests (HTTP GET requests), number of failed tests (status code of the response is not equal to HTTP 200 OK), number of tests created by a crossover and number of tests created by a mutation.
- Plotly
    - Response time and data count are continuously logged.
    - Data are stored in the *data_responses.csv* file. When the fuzzer ends, an interactive scatter plot can be built via scatter.py . The scatter plot is viewable by any conventional web browser. Learn more in [scatter README](tools/scatter/README.md).

#### Console output
Brief information about the runtime is also printed to a console. Find below an example of such an output.

```
Collection: FI_CORRESPONDENCE_SRV-56482b5e-b76d-46eb-9f48-e13d1fe8eea2
Initializing queryable entities...
Connecting to the database...
Fuzzing...
Generated tests: 1300 | Failed tests: 27 | Raised exceptions: 0
```

*Collection* represents a name of a collection associated with mongoDB. *Raised exceptions* describes a number of raised exceptions within the runtime, for example, connection errors.


#### Configuration
A default configuration is stored in the file *config/fuzzer/config.yaml*. The configuration file can be modified to suit the best needs. Also, it is possible to create a new configuration file which can be passed via the command line option **--fuzzer-config**. 

#### Docker volumes
The output of **odfuzz** is written into a running instance of docker image by default. If you want to view the output on the host system, you are required to use the additional **-v** option and run the docker image as follows:
```
$ sudo docker run -v /host/absolute/path:/image/absolute/path -ti odfuzz:1.0
```
Taking this into account, you have to set the fuzzer's output directories to /image/absolute/path as well. For more, visit https://docs.docker.com/storage/volumes/.

## Usage
1. Run the fuzzer, for example, as:
```
$ odfuzz <SERVICE_URL> -l logs_directory -s stats_directory -r restrictions/basic.yaml -a -f -p
```

The option **-a** enables fuzzer to send asynchronous requests. A default number of the asynchronous requests can be changed. To do so, navigate to the file *config/fuzzer/config.yaml* and modify value *async_requests_num*. Notice that some services do not support more than 10 asynchronous requests at the same time.

2. Let it run for a couple of hours (or minutes). Cancel an execution of the fuzzer with CTRL + C.
3. Browse overall stats, for example, by the following scenario:
    - You want to discover what type of queries triggers undefined behaviour. Open the *stats_overall.csv* file via [Pivot](https://github.wdf.sap.corp/I342520/Pivot). Select entities you want to examine, select an HTTP status code you want to consider (e.g. 500), select names of Properties, etc. You may notice that the filter query option caused a lot of errors. Open the *stats_filter.csv* file again via [Pivot](https://github.wdf.sap.corp/I342520/Pivot) to discover what logical operators or operands caused an internal server error.
    - The item *hash*, stored in the pivot table, contains a unique value which is mapped to the particular URL in the file *urls_list.txt*. Therefore, it is possible to browse created URLs more efficiently.
    - Queries which produced errors are saved to multiple files (names of the files start with prefix *EntitySet_*). These queries are considered to be the best by the genetic algorithm eventually. Try to reproduce the errors by sending the same queries to the server in order to ensure yourself that this is a real bug.
    - Open SAP Logon and browse the errors via transactions sm21, st22 or /n/IWFND/ERROR_LOG. Find potential threats and report them.

NOTE: **odfuzz** uses a custom header **user-agent=odfuzz/1.0** in all HTTP requests. You may be able to filter the internet traffic based on this header.

### Limitations

- **odfuzz** was created as SAP internal-only tool for purpose of testing specifically the Odata APIs for Fiori Apps on S4HANA platform - and open-sourced afterwards. As it is currently "in-the-wild", it should be expected to encounter many edge-cases (ie bugs/enhancements) when executed against Odata services either on different SAP platform (SCP) or even Odata services running on different platforms and intended for other consumers. 

- At the moment, **odfuzz** can mutate only values of types Edm.String, Edm.Int32, Edm.Decimal, Edm.Boolean, and Edm.Guid. It is planned to support more types in the future.

- The fuzzer URL generation algorithm is also currently hardcoded for purpose of testing the SAP applications. These applications use different order of function parameters within the filter query option. To change the order of the parameters, it is unavoidable to modify source code that generates such functions. The same rule applies for functions that can be implemented in two different ways, like the function substring() which can take 2 or 3 parameters.

- **odfuzz** creates a new collection in the database at each run. To preview database, run `mongo` in a terminal and select a corresponding database via `use odfuzz`. Run the command `db.getCollection("COLLECTION-NAME").find({}).pretty()` in the mongoDB shell in order to access and browse a particular collection. To delete all collections, run the command `db.dropDatabase()`. Since inteded usage is to to run inside docker and expose only result files in volume, this should not be a big of a concern. 


### Odata protocol references
Standard ODATA specification: 
https://www.odata.org/documentation/odata-version-2-0/uri-conventions/

SAP-only additional odata annotations see: 
https://wiki.scn.sap.com/wiki/display/EmTech/SAP+Annotations+for+OData+Version+2.0


## Contributing
Before contributing, please, make yourself familiar with git. You can try git online. Things would be easier for all of us if you do your changes on a branch. Use a single commit for every logical reviewable change, without unrelated modifications (that will help us if need to revert a particular commit). Please avoid adding commits fixing your previous commits, do amend or rebase instead.

Every commit must have either comprehensive commit message saying what is being changed and why or a link (an issue number on Github) to a bug report where this information is available. It is also useful to include notes about negative decisions - i.e. why you decided to not do particular things. Please bare in mind that other developers might not understand what the original problem was.

## License
Copyright (c) 2019 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the LICENSE file
