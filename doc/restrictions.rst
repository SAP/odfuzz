Restrictions
=============

OData services developed in SAP do not support some functions provided by the OData protocol (for example, day(), substring(), length()). Also, they may not implement GET_ENTITYSET methods for all entities. By using the restrictions, one can easily decrease a number of queries that are worthless.

ODfuzz generates HTTP requests based on definitions provided by a metadata document. However, in some cases we may want to restrict a testing of a particular entity set. Restrictions allow users to define rules which forbid a usage of some entities, functions, or properties in queries. The restrictions are defined in the following YAML format:

.. code-block:: yaml

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
        ...


In the example, there is a special construction which starts and ends with the character "[", or "]" respectively. It represents a list of restriction's keywords, separated by "|", which can be used in the corresponding context. Only one of these keywords can be used within the line. When we declare restrictions, we omit "[", "]", and "|" characters, because they are used just for a better illustration.

Sample restriction files can be found in the *restrictions* folder. Bear in mind that some restrictions are related to the previous version of ODfuzz. For example, the keyword "\$E_ALL\$" is deprecated, therefore, the keyword "\$ENTITY_SET\$" should be used instead.

Restriction Types
-------------------------
Restrictions are used to embed data in queries or to suppress generation of query's fractions which are not limited in the metadata document by default. In this section, we provide an overview of restriction types and their basic use cases.

EXCLUDE Restrictions
........................
* \$ENTITY_SET\$. The fuzzer will not generate HTTP requests for all method types - GET, POST, DELETE, PUT and MERGE for the specified list of entity sets. For example, when we define the following restriction, ODfuzz will skip a generation of query options for the entity set Products 

URI:

https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=ProductID%20lt%202

.. code-block:: yaml

   Exclude:
       $ENTITY_SET$:
           Products:
                Properties:
                Nav_Properties:
             
* \$ENTITY_SET Propertries\$. The fuzzer will not generate HTTP requests for method types - POST, PUT and MERGE for the specified list of properties of a specific entity set. This will remove the following property from the body of the request. For example, when we define the following restriction, ODfuzz will skip a generation of query options for the property ProductID for entity set Products 

URI:

https://services.odata.org/V2/Northwind/Northwind.svc/Products?sap-client=500

Body:

{"ProductName": "Q!a\u00bfbg\u2026\u00b5|\u00ce\u00c9qj\u00eb\u00b7\u00c1{SC@\u00e0\u2026VEs\u2019i\u2026(\u00b5", "SupplierID": 1593960140, "CategoryID": -1745367456, "QuantityPerUnit": "lM\u2013\u00ceo\u00a9\u00f7\u00b4\u00f8\u00e4\u00e0\u00bc<", "UnitPrice": "203518542564.221m", "UnitsInStock": 19375, "UnitsOnOrder": -12443, "ReorderLevel": 875, "Discontinued": true}

.. code-block:: yaml

   Exclude:
       $ENTITY_SET$:
           Products:
                Properties:
                    - ProductID
                Nav_Properties:
 
* \$ENTITY_SET Navigation Properties\$. The fuzzer will not generate HTTP requests for all method types - GET, POST, DELETE, PUT and MERGE for the specified list of navigation properties of a specific entity set. This will remove the generation of URI for following navigation property. For example, when we define the following restriction, ODfuzz will skip a generation of query options for the navigation property Categories for entity set Products 

URI:

https://services.odata.org/V2/Northwind/Northwind.svc/Categories(CategoryID=950596305)/Products?sap-client=500

.. code-block:: yaml

   Exclude:
       $ENTITY_SET$:
           Products:
                Properties:
                Nav_Properties:
                    - Category

* \$ENTITY_SET\$. The fuzzer will not generate HTTP GET requests for a specified list of entity sets. For example, when we define the following restriction, ODfuzz will skip a generation of \$filter query options for the entity set Products (e.g. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=ProductID%20lt%202):

.. code-block:: yaml

   Exclude:
       $filter:
           $ENTITY_SET$:
               - Products

* \$ENTITY\$. The fuzzer will not generate HTTP GET requests for a specified list of entities. ODfuzz will skip generation of requests, which contain the '\$filter' query option and target the single entity Product, when the restrictions are defined as follows (e.g. https://services.odata.org/V2/Northwind/Northwind.svc/Products(1)):

.. code-block:: yaml

   Exclude:
       $filter:
           $ENTITY$:
               - Products

* \$ENTITY_ASSOC\$. The fuzzer will not generate HTTP GET requests for associated entity sets. ODfuzz will skip generation of the '\$filter' query option for requests which contain the associated entity set Order_Details after applying the restriction (e.i. https://services.odata.org/V2/Northwind/Northwind.svc/Products(1)/Order_Details):

.. code-block:: yaml

   Exclude:
       $filter:
           $ENTITY_ASSOC$:
               - Order_Details

* \$F_ALL\$. The fuzzer will not generate the query option '\$filter' that contains any of declared functions. ODfuzz omits the function 'indexof' in queries when the the following restriction is defined (https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=indexof(ProductName,%20%27Cha%27)%20eq%200):

.. code-block:: yaml

   Exclude:
       $filter:
           $F_ALL$:
               - indexof

* \$P_ALL\$. The fuzzer will not generate query options that contains any of declared properties. For example, ODfuzz will skip generation of the '\$filter' query options which contain the property SupplierID (e.i. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=SupplierID%20eq%201):

.. code-block:: yaml

   Exclude:
       $filter:
           $P_ALL$:
               - SupplierID

* \$FORBID\$. The fuzzer will generate HTTP GET requests without specified query options. For example, query options '\$filter' and '\$orderby' will not be generated along with other query options when the restrictions are defined in the following manner (e.g. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=ProductID%20lt%202&\$orderby=ProductID%20asc):

.. code-block:: yaml

   Exclude:
       $FORBID$:
           - $filter
           - $orderby

* \$NAV_PROP\$. The fuzzer will generate the query option '\$expand' without declared navigation properties. This restriction may be redundant with the existing restriction \$P_ALL\$ at the first sight. However, navigation properties are not equivalent to ordinary properties, and cannot be treated in the same way. ODfuzz will skip generation of the query option '\$expand' which contains the navigation property Supplier (e.i. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$expand=Supplier):

.. code-block:: yaml

   Exclude:
       $expand:
           $NAV_PROP$:
               - Supplier

Basic example
............................................

The following is set of minimal restrictions, based on what functions are not supported by SAP ODATA Gateway:

file: */restrictions/basic.yaml*


.. code-block:: yaml

    Exclude:
        $filter:
            $F_ALL$:
                - concat
                - length
                - tolower
                - toupper
                - trim
                - replace
                - indexof
                - substring
                - day
                - hour
                - minute
                - month
                - second
                - year
                - round
                - floor



Complex example (FI_CORRESPONDENCE_V2_SRV)
............................................

.. code-block:: yaml

    Exclude:
        $FORBID$:
            - search
            - $top
            - $skip
            - $inlinecount
            - $orderby
        $expand:
            $NAV_PROP$:
                - XML
                - PDF
                - Print
                - MessageSet
        $filter:
            C_CorrespondenceCompanyCodeVH:
                - CompanyCodeName
            $F_ALL$:
                - concat
                - trim
                - substring
                - toupper
                - length
                - tolower
                - replace
                - indexof
            $ENTITY_SET$:
                - DefaultValueSet
                - C_CorrespondenceCompanyCodeVH
                - C_CorrespondenceCustomerVH
                - C_CorrespondenceSupplierVH
                - C_Cpbupaemailvh
            $ENTITY_ASSOC$:
                - CorrespondenceTypeSet
                - SupportedChannelSet



INCLUDE restrictions - e.g. PRIMARY KEYs for records
........................

* \$VALUE\$. The fuzzer will employ specified values in the creation of query options. For example, ODfuzz generates the \$filter query option targeting the property UnitPrice which is afterwards compared only to two values, "18.0000" or "19.0000", when we declare the restrictions as follows (i.e. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=UnitPrice%20eq%2018.0000):

.. code-block:: yaml

   Include:
       $VALUE$:
           Products:
               UnitPrice:
                   - "18.0000"
                   - "19.0000"

Declared values are not mutable. The mutator picks a random value from the list and replaces the old value with it.

Values have to be enclosed with double quotation marks due to fact that they are simply copied to the fuzzer without any modifications or type redefinitions. All data types are represented as strings internally. Here we provide some examples of declarations for commonly used data types:

.. code-block:: yaml

   Edm.String  : "'Value'"
   Edm.Int32   : "123"
   Edm.Boolean : "true"
   Edm.Decimal : "12.00"


* \$DRAFT\$. The fuzzer will include a selected property in all queries which target a particular entity set. This restriction was previously used for testing draft entities (i.e. IsActiveEntity property was required in all queries). ODfuzz ensures that the property Discontinued is included in the filter query option when the following restriction is defined (i.e. https://services.odata.org/V2/Northwind/Northwind.svc/Products?\$filter=Discontinued%20eq%20true):

.. code-block:: yaml

   Include:
       $DRAFT$:
           Products:
               - Discontinued
