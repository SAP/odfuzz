import pytest
import json

from collections import namedtuple
from lxml import etree

from pyodata.v2.model import Edmx
from odfuzz.arguments import ArgParser

NullRestrictions = namedtuple('NullRestrictions', 'include exclude')


@pytest.fixture
def metadata():
    return """
        <edmx:Edmx xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:sap="http://www.sap.com/Protocols/SAPData" Version="1.0">
         <edmx:Reference xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Uri="https://example.sap.corp/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/Vocabularies(TechnicalName='%2FIWBEP%2FVOC_COMMON',Version='0001',SAP__Origin='LOCAL')/$value">
          <edmx:Include Namespace="com.sap.vocabularies.Common.v1" Alias="Common"/>
         </edmx:Reference>
         <edmx:DataServices m:DataServiceVersion="2.0">
          <Schema xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://schemas.microsoft.com/ado/2008/09/edm" Namespace="EXAMPLE_SRV" xml:lang="en" sap:schema-version="1">
           <EntityType Name="MasterEntity" sap:content-version="1">
            <Key>
             <PropertyRef Name="Key"/>
            </Key>
            <Property Name="Key" Type="Edm.String" MaxLength="5" Nullable="false" sap:unicode="false" sap:label="Key" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:value-list="standard"/>
            <Property Name="DataType" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Key" sap:creatable="false" sap:updatable="false" sap:sortable="false"/>
            <Property Name="Data" Type="Edm.String" MaxLength="Max" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false" sap:text="DataName"/>
            <Property Name="DataName" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="FiscalYear" Type="Edm.Int32" sap:creatable="false" sap:updatable="false"/>
            <Property Name="TotalCount" Type="Edm.Int32" sap:creatable="false" sap:updatable="false"/>
            <Property Name="IsActiveEntity" Type="Edm.Boolean" Nullable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="SingleValue" Type="Edm.String" sap:filter-restriction="single-value"/>
            <Property Name="MultiValue" Type="Edm.String" sap:filter-restriction="multi-value"/>
            <Property Name="IntervalValue" Type="Edm.String" sap:filter-restriction="interval"/>
           </EntityType>
           <EntityType Name="DataEntity" sap:content-version="1" sap:value-list="true" sap:label="Data entities">
            <Key>
             <PropertyRef Name="Name"/>
            </Key>
            <Property Name="Name" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="Type" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="Value" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="Description" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false"/>
            <Property Name="Invisible" Type="Edm.String" Nullable="false" sap:unicode="false" sap:label="Data" sap:creatable="false" sap:updatable="false" sap:sortable="false" sap:filterable="false" sap:visible="false"/>
           </EntityType>
           <Association Name="toDataEntity" sap:content-version="1">
            <End Type="EXAMPLE_SRV.MasterEntity" Multiplicity="1" Role="FromRole_toDataEntity" />
            <End Type="EXAMPLE_SRV.DataEntity" Multiplicity="*" Role="ToRole_toDataEntity" />
            <ReferentialConstraint>
             <Principal Role="FromRole_toDataEntity">
              <PropertyRef Name="Key" />
             </Principal>
             <Dependent Role="ToRole_toDataEntity">
              <PropertyRef Name="Name" />
             </Dependent>
            </ReferentialConstraint>
           </Association>
           <Association Name="toMasterEntity" sap:content-version="1">
            <End Type="EXAMPLE_SRV.MasterEntity" Multiplicity="1" Role="FromRole_toMasterEntity" />
            <End Type="EXAMPLE_SRV.MasterEntity" Multiplicity="0..1" Role="ToRole_toMasterEntity" />
           </Association>
           <EntityContainer Name="EXAMPLE_SRV" m:IsDefaultEntityContainer="true" sap:supported-formats="atom json xlsx">
            <EntitySet Name="MasterSet" EntityType="EXAMPLE_SRV.MasterEntity" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:searchable="true" sap:content-version="1"/>
            <EntitySet Name="DataSet" EntityType="EXAMPLE_SRV.DataEntity" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:searchable="true" sap:content-version="1" sap:addressable="false"/>
            <AssociationSet Name="toDataEntitySet" Association="EXAMPLE_SRV.toDataEntity" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:content-version="1">
             <End EntitySet="MasterSet" Role="FromRole_toDataEntity" />
             <End EntitySet="DataSet" Role="ToRole_toDataEntity" />
            </AssociationSet>
            <AssociationSet Name="toMasterEntitySet" Association="EXAMPLE_SRV.toMasterEntity" sap:creatable="false" sap:updatable="false" sap:deletable="false" sap:content-version="1">
             <End EntitySet="MasterSet" Role="FromRole_toMasterEntity" />
             <End EntitySet="MasterSet" Role="ToRole_toMasterEntity" />
            </AssociationSet>
           </EntityContainer>
          </Schema>
         </edmx:DataServices>
        </edmx:Edmx>"""


@pytest.fixture
def schema(metadata):
    parsed_schema = Edmx.parse(metadata)
    return parsed_schema


@pytest.fixture
def master_entity_type(schema):
    entity_type = schema.entity_type('MasterEntity')
    return entity_type


@pytest.fixture
def argparser():
    argument_parser = ArgParser()
    return argument_parser


@pytest.fixture
def single_entity_xml():
    return etree.fromstring("""
         <entry xmlns="http://www.w3.org/2005/Atom" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xml:base="https://example.com/EXAMPLE_SRV/">
          <id>
           https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')
          </id>
          <title type="text">
           EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')
          </title>
          <updated>2018-09-21T19:07:56Z</updated>
          <category term="EXAMPLE_SRV.EntitySetType" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
          <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')" rel="self" title="EntitySet"/>
          <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/SupportedChannelSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/SupportedChannelSet" type="application/atom+xml;type=feed" title="SupportedChannelSet"/>
          <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParametersGroupSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/ParametersGroupSet" type="application/atom+xml;type=feed" title="ParametersGroupSet"/>
          <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParameterSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/ParameterSet" type="application/atom+xml;type=feed" title="ParameterSet"/>
          <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/EmailTemplateSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/EmailTemplateSet" type="application/atom+xml;type=feed" title="EmailTemplateSet"/>
          <content type="application/xml">
           <m:properties>
            <d:Event>SAP06</d:Event>
            <d:VariantId>SAP06</d:VariantId>
            <d:Id>SAP06</d:Id>
            <d:Name/>
            <d:RequiresAccountNumber>true</d:RequiresAccountNumber>
            <d:RequiresDocument>false</d:RequiresDocument>
            <d:NumberOfDates>2</d:NumberOfDates>
            <d:Date1Text>Postings from</d:Date1Text>
            <d:Date2Text>Postings to</d:Date2Text>
            <d:CompanyCode/>
           </m:properties>
          </content>
         </entry>""")


@pytest.fixture
def multiple_entity_sets_xml():
    return etree.fromstring("""
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
          xml:base="https://example.com/EXAMPLE_SRV">
          <id>
           https://example.com/EXAMPLE_SRV/EntitySet
          </id>
          <title type="text">EntitySet</title>
          <updated>2018-09-21T18:17:25Z</updated>
          <author>
           <name/>
          </author>
          <link href="EntitySet" rel="self" title="EntitySet"/>
          <entry>
           <id>
            https://example.com/EXAMPLE_SRV/EntitySet(Customer='1',CompanyCode='')
           </id>
           <title type="text">
            EntitySet(Customer='1',CompanyCode='')
           </title>
           <updated>2018-09-21T18:17:25Z</updated>
           <category term="EXAMPLE_SRV.EntitySetType" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
           <link href="EntitySet(Customer='1',CompanyCode='')" rel="self" title="EntitySetType"/>
           <content type="application/xml">
            <m:properties xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
             <d:Customer>1</d:Customer>
             <d:CompanyCode/>
             <d:CustomerName>ZBASH201603040921471</d:CustomerName>
             <d:CityName>Kusel</d:CityName>
             <d:PostalCode>66345</d:PostalCode>
             <d:Country>DE</d:Country>
             <d:CustomerAccountGroup>0001</d:CustomerAccountGroup>
             <d:AuthorizationGroup/>
             <d:CoCodeSpcfcAuthorizationGroup/>
            </m:properties>
           </content>
          </entry>
          <entry>
           <id>
            https://example.com/EXAMPLE_SRV/EntitySet(Customer='92',CompanyCode='')
           </id>
           <title type="text">
            EntitySet(Customer='92',CompanyCode='')
           </title>
           <updated>2018-09-21T18:17:25Z</updated>
           <category term="EXAMPLE_SRV.EntitySetType" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
           <link href="EntitySet(Customer='92',CompanyCode='')" rel="self" title="EntitySetType"/>
           <content type="application/xml">
            <m:properties xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
             <d:Customer>92</d:Customer>
             <d:CompanyCode/>
             <d:CustomerName>NEW_NAME1</d:CustomerName>
             <d:CityName>PATNA</d:CityName>
             <d:PostalCode>110027</d:PostalCode>
             <d:Country>IN</d:Country>
             <d:CustomerAccountGroup>DEBI</d:CustomerAccountGroup>
             <d:AuthorizationGroup/>
             <d:CoCodeSpcfcAuthorizationGroup/>
            </m:properties>
           </content>
          </entry>
          <entry>
           <id>
            https://example.com/EXAMPLE_SRV/EntitySet(Customer='93',CompanyCode='')
           </id>
           <title type="text">
            EntitySet(Customer='93',CompanyCode='')
           </title>
           <updated>2018-09-21T18:17:25Z</updated>
           <category term="EXAMPLE_SRV.EntitySetType" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
           <link href="EntitySet(Customer='93',CompanyCode='')" rel="self" title="EntitySetType"/>
           <content type="application/xml">
            <m:properties xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
             <d:Customer>93</d:Customer>
             <d:CompanyCode/>
             <d:CustomerName>NEW_NAME1</d:CustomerName>
             <d:CityName>PATNA</d:CityName>
             <d:PostalCode>110027</d:PostalCode>
             <d:Country>IN</d:Country>
             <d:CustomerAccountGroup>DEBI</d:CustomerAccountGroup>
             <d:AuthorizationGroup/>
             <d:CoCodeSpcfcAuthorizationGroup/>
            </m:properties>
           </content>
          </entry>
         </feed> """)


@pytest.fixture
def expanded_entity_set_xml():
    return etree.fromstring("""
     <entry xmlns="http://www.w3.org/2005/Atom" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xml:base="https://example.com/EXAMPLE_SRV/">
      <id>
       https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')
      </id>
      <title type="text">
       EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')
      </title>
      <updated>2018-09-21T18:59:20Z</updated>
      <category term="EXAMPLE_SRV.EntitySetType" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
      <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')" rel="self" title="EntitySet"/>
      <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/SupportedChannelSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/SupportedChannelSet" type="application/atom+xml;type=feed" title="SupportedChannelSet">
       <m:inline>
        <feed xml:base="https://example.com/EXAMPLE_SRV/">
         <id>
          https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/SupportedChannelSet
         </id>
         <title type="text">SupportedChannelSet</title>
         <updated>2018-09-21T18:59:20Z</updated>
         <author>
          <name/>
         </author>
         <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/SupportedChannelSet" rel="self" title="SupportedChannelSet"/>
         <entry>
          <id>
           https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </id>
          <title type="text">
           SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </title>
          <updated>2018-09-21T18:59:20Z</updated>
          <category term="EXAMPLE_SRV.SupportedChannel" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
          <link href="SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')" rel="self" title="SupportedChannel"/>
          <content type="application/xml">
           <m:properties>
            <d:Event>SAP06</d:Event>
            <d:VariantId>SAP06</d:VariantId>
            <d:CorrespondenceTypeId>SAP06</d:CorrespondenceTypeId>
            <d:ChannelName>Fax</d:ChannelName>
           </m:properties>
          </content>
         </entry>
         <entry>
          <id>
           https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </id>
          <title type="text">
           SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </title>
          <updated>2018-09-21T18:59:20Z</updated>
          <category term="EXAMPLE_SRV.SupportedChannel" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
          <link href="SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')" rel="self" title="SupportedChannel"/>
          <content type="application/xml">
           <m:properties>
            <d:Event>SAP06</d:Event>
            <d:VariantId>SAP06</d:VariantId>
            <d:CorrespondenceTypeId>SAP06</d:CorrespondenceTypeId>
            <d:ChannelName>EmailOldOm</d:ChannelName>
           </m:properties>
          </content>
         </entry>
         <entry>
          <id>
           https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </id>
          <title type="text">
           SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')
          </title>
          <updated>2018-09-21T18:59:20Z</updated>
          <category term="EXAMPLE_SRV.SupportedChannel" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
          <link href="SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')" rel="self" title="SupportedChannel"/>
          <content type="application/xml">
           <m:properties>
            <d:Event>SAP06</d:Event>
            <d:VariantId>SAP06</d:VariantId>
            <d:CorrespondenceTypeId>SAP06</d:CorrespondenceTypeId>
            <d:ChannelName>Printer</d:ChannelName>
           </m:properties>
          </content>
         </entry>
        </feed>
       </m:inline>
      </link>
      <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParametersGroupSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/ParametersGroupSet" type="application/atom+xml;type=feed" title="ParametersGroupSet">
       <m:inline>
        <feed xml:base="https://example.com/EXAMPLE_SRV/">
         <id>
          https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParametersGroupSet
         </id>
         <title type="text">ParametersGroupSet</title>
         <updated>2018-09-21T18:59:20Z</updated>
         <author>
          <name/>
         </author>
         <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParametersGroupSet" rel="self" title="ParametersGroupSet"/>
        </feed>
       </m:inline>
      </link>
     <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParameterSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/ParameterSet" type="application/atom+xml;type=feed" title="ParameterSet"/>
     <link href="EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/EmailTemplateSet" rel="http://schemas.microsoft.com/ado/2007/08/dataservices/related/EmailTemplateSet" type="application/atom+xml;type=feed" title="EmailTemplateSet"/>
     <content type="application/xml">
      <m:properties>
       <d:Event>SAP06</d:Event>
        <d:VariantId>SAP06</d:VariantId>
        <d:Id>SAP06</d:Id>
        <d:Name/>
        <d:RequiresAccountNumber>true</d:RequiresAccountNumber>
        <d:RequiresDocument>false</d:RequiresDocument>
        <d:NumberOfDates>2</d:NumberOfDates>
        <d:Date1Text>Postings from</d:Date1Text>
        <d:Date2Text>Postings to</d:Date2Text>
        <d:CompanyCode/>
      </m:properties>
     </content>
    </entry>""")


@pytest.fixture
def no_entity_sets_xml():
    return etree.fromstring("""
     <feed xmlns="http://www.w3.org/2005/Atom" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xml:base="https://ldciqj3.wdf.sap.corp:44300/sap/opu/odata/sap/FI_CORRESPONDENCE_V2_SRV/">
      <id>
       https://ldciqj3.wdf.sap.corp:44300/sap/opu/odata/sap/FI_CORRESPONDENCE_V2_SRV/VL_SH_H_T012
      </id>
      <title type="text">VL_SH_H_T012</title>
      <updated>2018-09-24T11:55:20Z</updated>
      <author>
       <name/>
      </author>
      <link href="VL_SH_H_T012" rel="self" title="VL_SH_H_T012"/>
      <m:count>0</m:count>
     </feed>""")


@pytest.fixture
def no_entity_sets_json():
    return json.loads("""{"d":{"__count":"0","results":[]}}""")


@pytest.fixture
def single_entity_json():
    return json.loads("""
    {"d":{"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')",
    "uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')","type":"EXAMPLE_SRV.Entity"},
    "Event":"SAP06","VariantId":"SAP06","Id":"SAP06","Name":"","RequiresAccountNumber":true,"RequiresDocument":false,"NumberOfDates":2,
    "Date1Text":"Postings From","Date2Text":"Postings To","CompanyCode":"",
    "SupportedChannelSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/SupportedChannelSet"}},
    "ParametersGroupSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParametersGroupSet"}},
    "ParameterSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParameterSet"}},
    "EmailTemplateSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/EmailTemplateSet"}}}}""")


@pytest.fixture
def multiple_entity_sets_json():
    return json.loads("""
    {"d":{"results":[
        {"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='1',CompanyCode='')",
        "uri":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='1',CompanyCode='')",
        "type":"EXAPLE_SRV.EntitySetType"},"Customer":"1","CompanyCode":"","CustomerName":"ZBASH201603040921471","CityName":"Kusel",
        "PostalCode":"66345","Country":"DE","CustomerAccountGroup":"0001","AuthorizationGroup":"","CoCodeSpcfcAuthorizationGroup":""},
        {"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='92',CompanyCode='')",
        "uri":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='92',CompanyCode='')",
        "type":"EXAMPLE_SRV.EntitySetType"},"Customer":"92","CompanyCode":"","CustomerName":"NEW_NAME1","CityName":"PATNA",
        "PostalCode":"110027","Country":"IN","CustomerAccountGroup":"DEBI","AuthorizationGroup":"","CoCodeSpcfcAuthorizationGroup":""},
        {"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='93',CompanyCode='')",
        "uri":"https://example.com/EXAMPLE_SRV/EntitySet(Customer='93',CompanyCode='')",
        "type":"EXAMPLE_SRV.EntitySetType"},"Customer":"93","CompanyCode":"","CustomerName":"NEW_NAME1","CityName":"PATNA",
        "PostalCode":"110027","Country":"IN","CustomerAccountGroup":"DEBI","AuthorizationGroup":"","CoCodeSpcfcAuthorizationGroup":""}
    ]}}""")


@pytest.fixture
def expanded_entity_set_json():
    return json.loads("""
    {"d":{"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')",
    "uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')","type":"EXAMPLE_SRV.EntitySet"},
    "Event":"SAP06","VariantId":"SAP06","Id":"SAP06","Name":"","RequiresAccountNumber":true,"RequiresDocument":false,
    "NumberOfDates":2,"Date1Text":"Postings from","Date2Text":"Postings to","CompanyCode":"",
    "SupportedChannelSet":{"results":[
        {"__metadata":{"id":"https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "uri":"https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "type":"EXAMPLE_SRV.SupportedChannel"},"Event":"SAP06","VariantId":"SAP06","CorrespondenceTypeId":"SAP06","ChannelName":"Fax"},
        {"__metadata":{"id":"https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "uri":"https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "type":"EXAMPLE_SRV.SupportedChannel"},"Event":"SAP06","VariantId":"SAP06","CorrespondenceTypeId":"SAP06","ChannelName":"EmailOldOm"},
        {"__metadata":{"id":"https://EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "uri":"https://example.com/EXAMPLE_SRV/SupportedChannelSet(Event='SAP06',VariantId='SAP06',CorrespondenceTypeId='SAP06')",
        "type":"EXAMPLE_SRV.SupportedChannel"},"Event":"SAP06","VariantId":"SAP06","CorrespondenceTypeId":"SAP06","ChannelName":"Printer"}]
    },
    "ParametersGroupSet":{"results":[]},
    "ParameterSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/ParameterSet"}},
    "EmailTemplateSet":{"__deferred":{"uri":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')/EmailTemplateSet"}}}}""")


@pytest.fixture
def invalid_root_key_json():
    return json.loads("""{"a":{"__metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')"}}}""")


@pytest.fixture
def invalid_metadata_key_json():
    return json.loads("""{"d":{"_not_metadata":{"id":"https://example.com/EXAMPLE_SRV/EntitySet(Event='SAP06',VariantId='SAP06',Id='SAP06')"}}}""")


@pytest.fixture
def empty_restrictions():
    class RestrictionsMock:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, _):
            return NullRestrictions({}, {})

    return RestrictionsMock()
