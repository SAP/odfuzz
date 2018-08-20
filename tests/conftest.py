import pytest

from pyodata.v2.model import Edmx
from odfuzz.arguments import ArgParser


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
