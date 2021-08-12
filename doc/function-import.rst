Function Imports in ODfuzz
==========================


Overview
--------

.. csv-table:: Function Import Overview
   :widths: 50, 50

   "HTTP GET", "YES"
   "HTTP POST ", "YES"
   "HTTP DELETE", "NO"
   "HTTP PUT", "NO"
   "HTTP MERGE", "NO"
   "Request Body", "NO"


Introduction
------------

Function Imports are a feature of the OData Protocol which is used to implement Service Operations in an OData service.
They are essentially complex CRUD Operations combined into a single service request, or any scenario that cannot be implemented in simple CRUD operation(s) on entity sets.

For example, an ML-based service needs to identify a picture and provide an inference. By the normal CRUD operations,
the picture needs to be first uploaded using a **POST**, then the inference service has to be triggered, and the results need to be fetched using a **GET**.

Instead, we can define a Function Import which already has this sequence of actions implemented, and all we need is to provide the image in a single service request.


Method types
------------

Function Imports are either of method type **GET** or **POST**. If the method type is missing or unspecified then it usually defaults to **GET**. 
The same Function Import shall not be accessible via different methods though.


URI and Body
------------

All the function import parameter names and values are put in the URI itself as part of query parameters. The body of the Function Import request does not carry any value, *even for POST*.


Metadata
--------

Function Imports are defined within the Entity Container in the *$metadata* of the service. Below is an example of one such definition.

::

    <FunctionImport Name="ExecuteBooking" ReturnType="ODATA_SRV.BookingResponse" m:HttpMethod="POST" sap:action-for="ODATA_SRV.Booking">
      <Parameter Name="ReturnBookingComment" Type="Edm.String" Mode="In" MaxLength="256"/>
      <Parameter Name="OutwardBookingComment" Type="Edm.String" Mode="In" MaxLength="256"/>
      <Parameter Name="ReturnFlightDate" Type="Edm.DateTime" Mode="In" Precision="0"/>
      <Parameter Name="ReturnFlightNumber" Type="Edm.String" Mode="In"/>
      <Parameter Name="ReturnAirlineId" Type="Edm.String" Mode="In" MaxLength="4"/>
      <Parameter Name="ReserveOnly" Type="Edm.Boolean" Mode="In"/>
      <Parameter Name="OutwardFlightNumber" Type="Edm.String" Mode="In" MaxLength="4"/>
      <Parameter Name="OutwardFlightDate" Type="Edm.DateTime" Mode="In" Precision="0"/>
      <Parameter Name="OutwardAirlineId" Type="Edm.String" Mode="In" MaxLength="3"/>
    </FunctionImport>


Each Function Import has a *Name* which also serves as the relative service operation endpoint. The *m:HttpMethod* specifies the method type.
The Parameters define inputs this endpoint requires, their EDM Type, along with additional facets (length, precision, etc if exists).

All the parameters need to be present in the service request, and a subset might not work depending on the service implementation. For such scenarios the 'null' value might be used.

::

    ExecuteBooking?ReturnBookingComment='2%BC%C3%8BZ%C3%93%E2%84%A2~R5'&OutwardBookingComment='fc%C2%A4y%C2%B2%C3%B1%C3%84%C3%81'&ReturnFlightDate=datetime'7027-09-01T11:38:24'&ReturnFlightNumber='%C3%B5%C3%B3%21%C3%A4%C3%8C'&ReturnAirlineId='ja'&ReserveOnly=true&OutwardFlightNumber='Vs%E2%84%A2~'&OutwardFlightDate=datetime'9174-08-06T09:31:16'&OutwardAirlineId='%C3%8Bq'

This is an example of a fuzzed payload based on the definition provided above. This service request has to made with **POST** method.


Further Learning
----------------

https://www.odata.org/documentation/odata-version-2-0/uri-conventions/ (3.3. Addressing Service Operations)
https://help.sap.com/saphelp_nw74/helpdata/en/c5/dc22512c312314e10000000a44176d/frameset.htm
