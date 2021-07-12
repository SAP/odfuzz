from collections import namedtuple

from odfuzz.generators import (
    EdmDecimal,
    EdmString,
)
from odfuzz import generators
from odfuzz.exceptions import BuilderError

from pyodata.v2.model import Edmx
from pyodata.exceptions import PyODataException 

class FunctionImport:
    #calls pyodata to parse the metadata file and give back the list of Function Imports 
    def get_functionimport(metadata_string):
        try:
            service_model = Edmx.parse(metadata_string)
        except (PyODataException, RuntimeError) as pyodata_ex:
            raise BuilderError('An exception occurred while parsing metadata: {}'.format(pyodata_ex))
        return service_model.function_imports


    #generates named tuples for EdmString and EdmDecimal because the generator expects an object with attributes
    def generate_object(parameter):
        if parameter.typ.name == 'Edm.String':
            obj = namedtuple('obj', 'max_length')
            length = parameter.max_length
            #if MaxLength is not provided, default length is set to 128
            if length == None:
                length = 128
            payload = EdmString.generate(obj(length), generator_format = 'uri')
        else:
            obj = namedtuple('obj', ['scale', 'precision'])
            scale = parameter.scale
            precision = parameter.precision
            payload = EdmDecimal.generate(obj(scale,precision),generator_format = 'uri')
        return payload


    #calls the generate() on different Edmtypes, by overloading the respective class. Equivalent to monkey.py
    def generate(parameter):
        if parameter.typ.name == 'Edm.String' or parameter.typ.name == 'Edm.Decimal':
            payload = FunctionImport.generate_object(parameter)
        else:
            edmtype = parameter.typ.name.replace('.','') #The metadata used Edm.<type> as the format, whereas odfuzz.generators classes dont have the dot.
            #overloading the class definition into a variable
            generator_class = getattr(generators, edmtype) 
            payload = generator_class.generate(generator_format='uri')
        return parameter.name, payload


    def fuzz(functionimport_single):
        name = functionimport_single.name
        parameters = {}
        for parameter in functionimport_single.parameters:
            a = FunctionImport.generate(parameter)
            parameters[a[0]]= a[1]
        #constructing the url
        url = name+"?"
        for i in parameters:
            url = url + i + '=' + parameters[i] + '&'
        url= url[:-1]
        return url



