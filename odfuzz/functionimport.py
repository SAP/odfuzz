from os import environ as ENV
from collections import namedtuple
from odfuzz.generators import (
    EdmDecimal,
    EdmString,
)

import xmltodict
from odfuzz import generators

# parses metadata to create an OrderDict, and returns the dict back
def extract_metadata(metadata_string):
    metadata = xmltodict.parse(metadata_string)
    return metadata

#generates custom objects for EdmString and EdmDecimal because the generator expects an object an object with attributes
def generate_object(parameter):
    if parameter['@Type'] == 'Edm.String':
        obj = namedtuple('obj', 'max_length')
        try:
            length = int(parameter['@MaxLength'])
        except:
            #if MaxLength is not provided
            length = 128
        payload = EdmString.generate(obj(length), generator_format = 'uri')
    else:
        obj = namedtuple('obj', ['scale', 'precision'])
        scale = int(parameter['@Scale'])
        precision = int(parameter['@Precision'])
        payload = EdmDecimal.generate(obj(scale,precision),generator_format = 'uri')
    return payload


#calls the generate() on different Edmtypes, by overloading the respective class. Equivalent to monkey.py
def generate(parameter):
    if parameter['@Type'] == 'Edm.String' or parameter['@Type'] == 'Edm.Decimal':
        payload = generate_object(parameter)
    else:
        edmtype = parameter['@Type'].replace('.','') #The metadata used Edm.<type> as the format, whereas odfuzz.generators classes dont have the dot.
        #overloading the class definition into a variable
        generator_class = getattr(generators, edmtype) 
        payload = generator_class.generate(generator_format='uri')
    return parameter['@Name'], payload


#constructs a query based on the the supplied FunctionImport 
def construct_query(function_import):
    name = function_import['@Name']
    parameters = {}
    
    #the parameter list maybe empty, in which case the 'Parameter' attribute doesnt appear
    #the parameter list might also have just 1 parameter, in which case 'Parameter' isnt a list collection
    if 'Parameter' in function_import and isinstance(function_import['Parameter'],list):
        for parameter in function_import['Parameter']:
            a = generate(parameter)
            parameters[a[0]]= a[1]
    elif 'Parameter' not in function_import:
        #if there is no parameters, dont do anything
        pass
    else:
        a=generate(function_import['Parameter'])
        parameters[a[0]]= a[1]
    
    #constructing the url
    url = name+"?"
    for i in parameters:
        url = url + i + '=' + parameters[i] + '&'
    url= url[:-1]
    
    return url


#equivalent to the main function
def start(metadata ,method,urls_per_fi):
    method_filter = ["GET", "POST", "Not Specified"]
    payload_list = []
    metadata = extract_metadata(metadata)
    if method not in method_filter:
        raise ValueError("Incorrect HTTP method. Please use either GET or POST. \"Not Specified\" would default to GET.")
    func_import_list = metadata['edmx:Edmx']['edmx:DataServices']['Schema']['EntityContainer']['FunctionImport']
    for i in func_import_list:
        if i['@m:HttpMethod'] == "Not Specified": #putting default of GET if not specified
            i['@m:HttpMethod'] = "GET"
        if i['@m:HttpMethod'] == method:
            for counter in range(urls_per_fi):
                payload = {}
                uri = construct_query(i)
                payload['uri'] = uri
                payload['body'] = "{}"
                payload_list.append(payload)
    return payload_list
