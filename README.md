# BP-ODfuzz
Fuzzer for testing applications communicating via the OData protocol.

#### Requirements
- [Python 3.6](https://www.python.org/downloads/)
  - [Requests 2.18.4](http://docs.python-requests.org/en/master/)
  - [Gevent 1.3](http://www.gevent.org/)
  - [PyOData 1.1](https://github.wdf.sap.corp/FXUBRQ-QE/PyOData)
- [mongoDB 3.6](https://www.mongodb.com/)
- [PivotTable.js](https://pivottable.js.org/examples/)

#### Run configuration
To access OData services introduced in SAP, it is required to set the following environmental variables in your system:
```
SAP_USERNAME=Username
SAP_PASSWORD=Password
```
The fuzzer will use these variables for a basic authentication.

Run the fuzzer with:
```
py odfuzz.py https://ldciqj3.wdf.sap.corp:44300/sap/opu/odata/sap/FI_CORRESPONDENCE_V2_SRV -l logs -s stats -r sample/restrict.txt
```

You can cancel the execution of the fuzzer by a keyboard interruption (CTRL+C).

#### Restrictions
With restrictions, a user is able to define rules which forbid a usage of some entities, functions or properties in queries. Restrictions are defined in the following format:
```
[ Exclude | Include ]
    [ $filter | orderby | search | ... ]
        EntitySet name
            Property name
            Property name
            ...
        [ $F_ALL$ | $E_ALL$ | $P_ALL$ ]
            [ Function name | EntitySet name | Property name ]
            ...
```
Every line, except the first line, starts with a tab or set of tabs and should be properly aligned. At the moment, only entity, property and global function restrictions are implemented.

#### Known bugs
- Requests are slow due to *gevent* module: hub.py:635(wait).
