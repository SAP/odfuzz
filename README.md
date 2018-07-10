# BP-ODfuzz
Fuzzer for testing applications communicating via the OData protocol. ODfuzz sends valid requests, that contain random data, to the server and checks the responses. Learn more at [Excel@Fit 2018](http://excel.fit.vutbr.cz/submissions/2018/004/4.pdf).

#### Requirements
- [Python 3.6](https://www.python.org/downloads/)
  - [Requests 2.18.4](http://docs.python-requests.org/en/master/)
  - [Gevent 1.2.2](http://www.gevent.org/)
  - [PyOData 1.1](https://github.wdf.sap.corp/FXUBRQ-QE/PyOData)
  - [PyMongo 3.6.1](https://api.mongodb.com/python/3.6.1/)
  - [lxml 3.7.3](https://github.com/lxml/lxml)
- [mongoDB 3.6](https://www.mongodb.com/)
- [PivotTable.js](https://pivottable.js.org/examples/)

### Setup
1. [Download](https://www.mongodb.com/download-center#community) and [install](https://docs.mongodb.com/manual/administration/install-community/) the mongoDB server on your local machine.
2. [Download](https://github.wdf.sap.corp/I342520/BP/tree/master/sample/pivot_demo) custom implementation of the Pivot table.
3. Clone this repository:
```
git clone git@github.wdf.sap.corp:I342520/BP-ODfuzz.git
```
4. Install all requirements with:
```
pip install -r requirements.txt
```

### Run configuration
To access OData services introduced in SAP, it is required to set the following environmental variables in your system. The fuzzer will use these variables for a basic authentication.
```
SAP_USERNAME=Username
SAP_PASSWORD=Password
```

Run the fuzzer, for example, with:
```
py odfuzz.py https://ldciqj3.wdf.sap.corp:44300/sap/opu/odata/sap/FI_CORRESPONDENCE_V2_SRV -l logs_directory -s stats_directory -r restrictions/basic.txt
```

You can cancel the execution of the fuzzer by a keyboard interruption (CTRL+C).

### Output
ODfuzz is creating multiple statistics about performed experiments and tests. The most interesting statistics are loaded to CSV files and may be visualised by the javascript Pivot table. Just open the CSV files in Pivot table app.

Requests that triggered an internal server error (HTTP 500) are written into multiple *.txt files. Name of the file is the name of the corresponding entity set in which the error occurred.

#### Restrictions
With restrictions, a user is able to define rules which forbid a usage of some entities, functions or properties in queries. Restrictions are defined in the following format:
```
[ Exclude | Include ]
    [ $filter | $orderby | $skip | ... ]
        EntitySet name
            Property name
            Property name
            ...
        [ $F_ALL$ | $E_ALL$ | $P_ALL$ ]
            [ Function name | EntitySet name | Property name ]
            ...
```
Every line, except the first line, starts with a tab or set of tabs and should be properly aligned. At the moment, only entity, property and global function restrictions are implemented.

Sample restrictions files can be found in the *restrictions* folder. Use *odata_northwind.txt* file in order to run the fuzzer on [Northwind OData service](http://services.odata.org/V2/Northwind/Northwind.svc/).

#### Limitations
At the moment, ODfuzz can mutate only values of types Edm.String and Edm.Int32. It is planned to support more types in the future.

The fuzzer was developed for testing the SAP applications. These applications use different order of function parameters within the filter query option. To change the order of the parameters, it is unavoidable to modify source code that generates such functions. The same rule applies for functions that can be implemented in two different ways, like the function substring() which can take 2 or 3 parameters.

ODfuzz creates a new collection in the database at each run. Run the command `db.getCollection("COLLECTION-NAME")` in the mongoDB shell in order to access a particular collection. To delete all collections, run the command `db.dropDatabase()`. 

#### Known bugs
- While inserting a document to mongoDB, the **pymongo.errors.DocumentTooLarge** exception is sometimes raised.
- Logical parts are not correctly deleted from database.


#### TODO
- Change format of restrictions file to JSON.
- Generate filter strings for complex types.
- Add heuristics for generators based on associations.
- Create  database of valid inputs, e.g. for 'Language', 'Location', etc. (may be defined in restrictions file).
- Add custom headers for requests.
- Add unit tests. (30% done)
- Use RotatingFileHandler instead of FileHandler in logging
