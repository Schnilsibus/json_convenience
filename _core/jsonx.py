from json import dump, load, JSONDecodeError
from pathlib import Path

_indentLevel = 4

class NotAPropertyError(Exception):
    """
    An Error that is be raised if a python object has a type that is not mapped to a JSON type

    JSON types that are called properties are: array, string, number, boolean, null.
    The python types that are mapped to those are: tuple, str, int, float, bool, None.
    Every other python type is not considerd a JSON property.
    """

    def __init__(self, noPropertyObject: any):
        """
        Parameters
        ----------
        noPropertyObject: dict
            the python object whose type is not mapped to a JSON property
        """

        Exception.__init__(self, f"the json object {noPropertyObject} is not a property; properties are: json data types and json arrays")

class NotAObjectError(Exception):
    """
    An Error that is be raised if a python object has a type that is not mapped to a JSON object

    JSON objects are the objects enclosed in curly braces in json files.
    The python type that is mapped to this is: dict.
    Every other python type is not considerd a JSON object.
    """

    def __init__(self, noObject: any):
        """
        Parameters
        ----------
        noObject: any
            the python object whose type is not mapped to a JSON object
        """

        Exception.__init__(self, f"the json value {noObject} is not a json object")

class JSONKeyNotFoundError(Exception):
    """
    An Error that is be raised if a key is not found in a JSON file
    """

    def __init__(self, wrongKey: str, allKeysOfObject: tuple, foundKeys: tuple = None):
        """
        Parameters
        ----------
        wrongKey: str
            the key that could not be found
        allKeysOfObject: tuple
            all the keys of the object in which the wrong key could not be found
        foundKeys: tuple (default=None)
            all the keys of the parent JSON objects of the object in which the wrong key could not be found
        """
        
        Exception.__init__(self, f"key '{wrongKey}' not in {allKeysOfObject}; found keys: [{'->'.join(foundKeys)}]")

class JSONKeyAlreadyExists(Exception):
    """
    An Error that is be raised if a key already exists in a JSON object
    """
    
    def __init__(self, doubleKey: str, allKeysOfObject: tuple, foundKeys: tuple = None):
        """
        Parameters
        ----------
        doubleKey: str
            the key that already exists
        allKeysOfObject: tuple
            all the keys of the object that already contains the doubled key
        foundKeys: tuple
            all the keys of the parent JSON objects of the object that contains the doubled key
        """
        
        Exception.__init__(self, f"key '{doubleKey}' already exists in {allKeysOfObject}; found keys: [{'->'.join(foundKeys)}]")

def getProperty(filePath: Path, keys: tuple) -> any:
    """
    Returns a property of a JSON file

    Parameters
    ----------
    filePath: pathlib.Path
        the path to the json file
    keys: tuple
    """
    
    rawData = readJSONFile(filePath = filePath)
    property = _getValueOfKeys(rawData = rawData, keys = keys)
    if (_isJSONObject(rawData = property)):
        raise NotAPropertyError(noPropertyObject = property)
    return property

def setProperty(filePath: Path, keys: tuple, value: any):
    rawData = readJSONFile(filePath = filePath)
    parentObject = _getValueOfKeys(rawData = rawData, keys = keys[:-1])
    if (not _containsKey(object = parentObject, key = keys[-1])):
        raise JSONKeyNotFoundError(wrongKey = keys[-1], allKeysOfObject = tuple(parentObject.keys()), foundKeys = keys[:-1])
    elif (_isJSONObject(rawData = parentObject[keys[-1]])):
        raise NotAPropertyError(noPropertyObject = parentObject[keys[-1]])
    parentObject[keys[-1]] = value
    writeJSONFile(filePath = filePath, data = rawData)

def addProperty(filePath: Path, keys: tuple, newKey: str, value: any):
    rawData = readJSONFile(filePath = filePath)
    parentObject = _getValueOfKeys(rawData = rawData, keys = keys)
    if (_containsKey(object = parentObject, key = newKey)):
        raise JSONKeyAlreadyExists(doubleKey = newKey, allKeysOfObject = tuple(parentObject.keys()), foundKeys = keys)
    elif (not _isJSONProperty(rawData = value)):
        raise TypeError(f"'{type(value)}' is not a type that can be mapped to a json property")
    parentObject[newKey] = value
    writeJSONFile(filePath = filePath, data = rawData)

def containsProperty(filePath: Path, keys: tuple) -> bool:
    rawData = readJSONFile(filePath = filePath)
    try:
        value = _getValueOfKeys(rawData = rawData, keys = keys)
        return _isJSONProperty(rawData = value)
    except JSONKeyNotFoundError as ex:
        return False

def getObject(filePath: Path, keys: tuple) -> dict:
    rawData = readJSONFile(filePath = filePath)
    object = _getValueOfKeys(rawData = rawData, keys = keys)
    if (_isJSONProperty(rawData = object)):
        raise NotAObjectError(noObject = object)
    return object

def setObject(filePath: Path, keys: tuple, object: dict):
    rawData = readJSONFile(filePath = filePath)
    parentObject = _getValueOfKeys(rawData = rawData, keys = keys[:-1])
    if (not _containsKey(object = parentObject, key = keys[-1])):
        raise JSONKeyNotFoundError(wrongKey = keys[-1], allKeysOfObject = tuple(parentObject.keys()), foundKeys = keys[:-1])
    elif(_isJSONProperty(rawData = parentObject[keys[-1]])):
        raise NotAObjectError(noObject = parentObject[keys[-1]])
    parentObject[keys[-1]] = object
    writeJSONFile(filePath = filePath, data = rawData)

def addObject(filePath: Path, keys: tuple, newKey: str, object: dict):
    rawData = readJSONFile(filePath = filePath)
    parentObject = _getValueOfKeys(rawData = rawData, keys = keys)
    if (_containsKey(object = parentObject, key = newKey)):
        raise JSONKeyAlreadyExists(doubleKey = newKey, allKeysOfObject = tuple(parentObject.keys()), foundKeys = keys)
    elif(not _isJSONObject(rawData = object)):
        raise TypeError(f"'{type(object)}' is not a type that can be mapped to a json property")
    parentObject[newKey] = object
    writeJSONFile(filePath = filePath, data = rawData)

def containsObject(filePath: Path, keys: tuple) -> bool:
    rawData = readJSONFile(filePath = filePath)
    try:
        value = _getValueOfKeys(rawData = rawData, keys = keys)
        return _isJSONObject(rawData = value)
    except JSONKeyNotFoundError as ex:
        return False

def isFormatCorrect(filePath: Path) -> bool:
    with open(file = filePath, mode = "r") as fp:
        try:
            readJSONFile(filePath = filePath)
        except JSONDecodeError:
            return False
        return True
    
def indentJSONFile(filePath: Path):
    writeJSONFile(filePath = filePath, data = readJSONFile(filePath = filePath))

def readJSONFile(filePath: Path) -> dict:
    if (not filePath.exists()):
        raise FileNotFoundError(f"the JSON file {filePath} doesn't exist")
    with filePath.open(mode = "r") as fp:
        return load(fp = fp)
    
def writeJSONFile(filePath: Path, data: dict):
    if (not filePath.exists()):
        raise FileNotFoundError(f"the JSON file {filePath} doesn't exist")
    with filePath.open(mode = "w") as fp:
        dump(obj = data, fp = fp, indent = _indentLevel)

def _getValueOfKeys(rawData: dict, keys: tuple) -> any:
    currentObject = rawData
    for i in range(len(keys)):
        if (not _containsKey(object = currentObject, key = keys[i])):
            raise JSONKeyNotFoundError(wrongKey = keys[i], allKeysOfObject = tuple(rawData.keys()), foundKeys = keys[:i])
        currentObject = currentObject[keys[i]]
    return currentObject

def _isJSONProperty(rawData: any) -> bool:
    return type(rawData) in [type(None), float, int, list, bool, str]

def _isJSONObject(rawData: any) -> bool:
    return type(rawData) == dict

def _containsKey(object: dict, key: str) -> bool:
    return key in object.keys()