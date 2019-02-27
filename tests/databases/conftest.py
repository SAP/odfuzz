import pytest

from bson import ObjectId


@pytest.fixture
def data_search_output_set():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd36"),
        "http" : "200",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceOutputSet",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceOutputSet?search=\"jeéú\"&sap-client=500&$format=json",
        "score" : 10,
        "order" : None,
        "_$orderby" : None,
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : None,
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : None
    }


@pytest.fixture
def data_search_output_set_error():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd33"),
        "http" : "500",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceOutputSet",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceOutputSet?search=\"jeéúA\"&sap-client=500&$format=json",
        "score" : 100,
        "order" : None,
        "_$orderby" : None,
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : None,
        "_$expand" : None,
        "_search" : "\"jeéúA\"",
        "_$inlinecount" : None
    }


@pytest.fixture
def data_three_filter_logicals_company_code():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd37"),
        "http" : "200",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?search=\"jeéú\"&$orderby=Currency asc,CityName&$filter=CompanyCode eq 'ÿ6' and CityName eq '' and Currency eq 'ã³>§' or CompanyCodeName eq '=9D6Ë‡ÐÉ'&$inlinecount=allpages&sap-client=500&$format=json",
        "score" : 10,
        "order" : ["_search", "_$orderby", "_$filter", "_$inlinecount"],
        "_$orderby" : [["Currency", "asc"],["CityName", ""]],
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : {
            "groups" : [ ],
            "logicals" : [
                {
                    "id" : "2968d8d2-58e8-4515-852b-be7c370c2d30",
                    "name" : "or",
                    "left_id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "right_id" : "d46ab050-466f-4463-84f0-db148c857e04"
                },
                {
                    "id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3",
                    "name" : "and",
                    "left_id" : "32746ef7-a4bb-413e-a6fa-528a46900057",
                    "right_id" : "36999108-fa66-49dd-83fa-273b243905bf"
                },
                {
                    "id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6",
                    "name" : "and",
                    "left_id" : "c4e0da45-183d-4c7e-be56-a2defe693759",
                    "right_id" : "32746ef7-a4bb-413e-a6fa-528a46900057"
                }
            ],
            "parts" : [
                {
                    "id" : "c4e0da45-183d-4c7e-be56-a2defe693759",
                    "name" : "CompanyCode",
                    "operator" : "eq",
                    "operand" : "'ÿ6'",
                    "replaceable" : True,
                    "right_id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6"
                },
                {
                    "id" : "32746ef7-a4bb-413e-a6fa-528a46900057",
                    "name" : "CityName",
                    "operator" : "eq",
                    "operand" : "''",
                    "replaceable" : True,
                    "left_id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6",
                    "right_id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3"
                },
                {
                    "id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "name" : "Currency",
                    "operator" : "eq",
                    "operand" : "'ã³>§'",
                    "replaceable" : True,
                    "left_id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3",
                    "right_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                },
                {
                    "id" : "d46ab050-466f-4463-84f0-db148c857e04",
                    "name" : "CompanyCodeName",
                    "operator" : "eq",
                    "operand" : "'=9D6Ë‡ÐÉ'",
                    "replaceable" : True,
                    "left_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                }
            ]
        },
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : "allpages"
    }


@pytest.fixture
def data_two_filter_logicals_company_code():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd38"),
        "http" : "200",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?search=\"jeéú\"&$orderby=Currency asc,CityName&$filter=CompanyCode eq 'ÿ6' and CityName eq '' and Currency eq 'ã³>§'&$inlinecount=allpages&sap-client=500&$format=json",
        "score" : 10,
        "order" : ["_search", "_$orderby", "_$filter", "_$inlinecount"],
        "_$orderby" : [["Currency", "asc"],["CityName", ""]],
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : {
            "groups" : [ ],
            "logicals" : [
                {
                    "id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3",
                    "name" : "and",
                    "left_id" : "32746ef7-a4bb-413e-a6fa-528a46900057",
                    "right_id" : "36999108-fa66-49dd-83fa-273b243905bf"
                },
                {
                    "id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6",
                    "name" : "and",
                    "left_id" : "c4e0da45-183d-4c7e-be56-a2defe693759",
                    "right_id" : "32746ef7-a4bb-413e-a6fa-528a46900057"
                }
            ],
            "parts" : [
                {
                    "id" : "c4e0da45-183d-4c7e-be56-a2defe693759",
                    "name" : "CompanyCode",
                    "operator" : "eq",
                    "operand" : "'ÿ6'",
                    "replaceable" : True,
                    "right_id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6"
                },
                {
                    "id" : "32746ef7-a4bb-413e-a6fa-528a46900057",
                    "name" : "CityName",
                    "operator" : "eq",
                    "operand" : "''",
                    "replaceable" : True,
                    "left_id" : "a2b00b3f-29f7-457b-b2c9-57f3e25639d6",
                    "right_id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3"
                },
                {
                    "id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "name" : "Currency",
                    "operator" : "eq",
                    "operand" : "'ã³>§'",
                    "replaceable" : True,
                    "left_id" : "c7079e68-c648-4519-a9aa-7e3aae0a93e3",
                },
            ]
        },
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : "allpages"
    }


@pytest.fixture
def data_single_filter_logical_company_code():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd39"),
        "http" : "200",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?search=\"jeéú\"&$orderby=Currency asc,CityName&$filter=Currency eq 'ã³>§' or CompanyCodeName eq '=9D6Ë‡ÐÉ'&$inlinecount=allpages&sap-client=500&$format=json",
        "score" : 1,
        "order" : ["_search", "_$orderby", "_$filter", "_$inlinecount"],
        "_$orderby" : [["Currency", "asc"],["CityName", ""]],
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : {
            "groups" : [ ],
            "logicals" : [
                {
                    "id" : "2968d8d2-58e8-4515-852b-be7c370c2d30",
                    "name" : "or",
                    "left_id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "right_id" : "d46ab050-466f-4463-84f0-db148c857e04"
                },
            ],
            "parts" : [
                {
                    "id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "name" : "Currency",
                    "operator" : "eq",
                    "operand" : "'ã³>§'",
                    "replaceable" : True,
                    "right_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                },
                {
                    "id" : "d46ab050-466f-4463-84f0-db148c857e04",
                    "name" : "CompanyCodeName",
                    "operator" : "eq",
                    "operand" : "'=9D6Ë‡ÐÉ'",
                    "replaceable" : True,
                    "left_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                }
            ]
        },
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : "allpages"
    }


@pytest.fixture
def data_single_filter_logical_company_code_error():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd40"),
        "http" : "500",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?search=\"jeéú\"&$orderby=Currency asc,CityName&$filter=Currency eq 'ã³>§' or CompanyCodeName eq '=9D6Ë‡ÐÉ'&$inlinecount=allpages&sap-client=500&$format=json",
        "score" : 100,
        "order" : ["_search", "_$orderby", "_$filter", "_$inlinecount"],
        "_$orderby" : [["Currency", "asc"],["CityName", ""]],
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : {
            "groups" : [ ],
            "logicals" : [
                {
                    "id" : "2968d8d2-58e8-4515-852b-be7c370c2d30",
                    "name" : "or",
                    "left_id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "right_id" : "d46ab050-466f-4463-84f0-db148c857e04"
                },
            ],
            "parts" : [
                {
                    "id" : "36999108-fa66-49dd-83fa-273b243905bf",
                    "name" : "Currency",
                    "operator" : "eq",
                    "operand" : "'ã³>§'",
                    "replaceable" : True,
                    "right_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                },
                {
                    "id" : "d46ab050-466f-4463-84f0-db148c857e04",
                    "name" : "CompanyCodeName",
                    "operator" : "eq",
                    "operand" : "'=9D6Ë‡ÐÉ'",
                    "replaceable" : True,
                    "left_id" : "2968d8d2-58e8-4515-852b-be7c370c2d30"
                }
            ]
        },
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : "allpages"
    }


@pytest.fixture
def data_search_correspondence_company_code_error():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd41"),
        "http" : "500",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?search=\"jeéú\"&sap-client=500&$format=json",
        "score" : 99,
        "order" : ["_search"],
        "_$orderby" : None,
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : None,
        "_$expand" : None,
        "_search" : "\"jeéú\"",
        "_$inlinecount" : None
    }


@pytest.fixture
def data_inlinecount_correspondence_company_code_error():
    return {
        "_id" : ObjectId("5c61a1295f627d1db904dd42"),
        "http" : "500",
        "error_code" : "",
        "error_message" : "",
        "entity_set" : "C_CorrespondenceCompanyCodeVH",
        "accessible_set" : None,
        "accessible_keys" : {},
        "predecessors" : [],
        "string" : "C_CorrespondenceCompanyCodeVH?$inlinecount=allpages&sap-client=500&$format=json",
        "score" : 98,
        "order" : ["_$inlinecount"],
        "_$orderby" : None,
        "_$top" : None,
        "_$skip" : None,
        "_$filter" : None,
        "_$expand" : None,
        "_search" : None,
        "_$inlinecount" : "allpages"
    }
