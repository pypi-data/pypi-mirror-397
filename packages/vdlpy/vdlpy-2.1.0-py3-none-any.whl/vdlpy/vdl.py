'''
This module provides access to a virtual data lake via its web API. 
'''

import json
import requests
from . import parts


def public_level():
    '''
    Get the public access level.
    
    Returns:
      * an `Itm` object representing the public access level.
    '''
    
    return Itm('0_1')


def source_admin_level(source):
    '''
    Get the admin access level of a source.
    
    Parameters:
      * source(int): the numeric identifier of a source.
    
    Returns:
      * an `Itm` object representing the admin access level of the source.
    '''
    
    return Itm(repr(source) + '_-9223372036854775807')


def get_source_of_item(itm):
    '''
    Get the numeric identifier of the source of an item.
    
    Parameters:
      * itm('Itm'): an item.
    
    Returns:
      * the numeric identifier of the source of the item.
    '''
    
    itemid = itm.itemid
    return int(itemid[0:itemid.index('_')])


class Client:
    '''
    An API client that can be used to invoke API methods.
    '''
    
    def __init__(self, url):
        '''
        Construct an API client. The client will have a session
        that is not authenticated, so that API methods that
        require authentication must have credential_and_key
        parameters to provide it. (The `set_session` function
        can be used to replace the session by a session that has 
        been authenticated.)
        
        The client obtains the IP address of the API and uses it
        in API calls. This avoids spurious DNS lookup errors.
        
        Parameters:
          * url (String) the API's URL.
        '''
        
        self.api = url
        self.session = requests.session()

        self.request_timeout = 30
        '''
        The timeout on HTTP requests, in seconds
        '''


    def set_request_timeout(self, timeout):
        '''Set the timeout for query and update requests
        
        Parameters:
          * timeout(int) the time in seconds allowed for query and
            update requests
        '''
        
        self.request_timeout = timeout
        

    def set_session(self, session_to_be_set):
        '''Set the session for access to the API.
    
        This method enables a session that has been authenticated
        by means outside this module to be used for API interactions.
    
        Parameters:
          * session_to_be_set: the requests session to be used for
          interactions with the system's API.
        '''
        self.session = session_to_be_set
    
    
    def query(self, constraints, credential_and_key=None, meta=None):
        '''
        Get data that satisfies a set of constraints
    
        Parameters:
          * constraints: a list of constraints that the data must satisfy.
            Each constraint can be supplied either as a `Constraint` object
            or as a 3-tuple whose elements are the subject, verb and object
            of a constraint. 
          * credential_and_key: a 2-tuple whose first element is either an
            `Itm` object that is a credential to authorize the request or
            the identifier of such an object, and whose second element is 
            the credential's key. If a credential_and_key is not supplied, 
            and the `set_session` function has been invoked to set a
            pre-authenticated session, the request will be made at its 
            access level. If a credential_and_key is not supplied, 
            and no pre-authenticated session has been set, the request
            will be made at the lowest (public) level.
          * meta: a dictionary of values to be sent as metadata with the
            request. Their values are application-dependent. They may, for
            example, include authentication parameters for an application-
            specific authentication method. 
      
        Raises:
          * VdlException: if the query cannot be executed.
      
        Returns:
          * a list of dictionaries, each of which contains an assignment
          of values to unknowns that satisfies the constraints.
        '''
    
        parms = {'command': 'query'}
        scanned_constraints = []
        files = dict()
        
        for input_constraint in constraints:
            constraint = __get_constraint__(input_constraint)
            scanned_constraints.append(
                [
                    __get_quantum__(constraint.subj, files),
                    __get_quantum__(constraint.vrb, files),
                    __get_quantum__(constraint.obj, files)
                    ])
        
        files.update({"constraints": ("constraints", json.dumps(scanned_constraints), "text/plain; charset=utf-8")})
        
        if credential_and_key is not None:
            auth = __get_credential_string_and_key__(credential_and_key)
            files.update({"auth": ("auth", json.dumps(auth), "text/plain; charset=utf-8")})
            
        if meta is not None:
            scanned_meta = {k: get_datum(v, files) for (k, v) in meta.items()}
            files.update({"meta": ("meta", json.dumps(scanned_meta), "text/plain; charset=utf-8")})
            
        response = self.session.post(self.api, files=files, params=parms, timeout=self.request_timeout)
        if response.status_code == 200: return __get_assignments_dict_list__(response)
        else: __handle_http_error__(response)
    
    
    def update(self, changes, credential_and_key=None, meta=None):
        '''
        Make a set of virtual data lake changes.
        
        Parameters:
          * changes: a `Change` object or a list of `Change` objects
          * credential_and_key: a 2-tuple whose first element is either an
            `Itm` object that is a credential to authorize the request or
            the identifier of such an object, and whose second element is 
            the credential's key. If a credential_and_key is not supplied, 
            and the `set_session` function has been invoked to set a
            pre-authenticated session, the request will be made at its 
            access level. If a credential_and_key is not supplied, 
            and no pre-authenticated session has been set, the request
            will be made at the lowest (public) level (and will fail).
          * meta: a dictionary of values to be sent as metadata with the
            request. Their values are application-dependent. They may, for
            example, include authentication parameters for an application-
            specific authentication method. 
      
        Raises:
          * VdlException: if one of the changes cannot be made,
            or if an error occurred in transmitting the request or in
            receiving or decoding the response. Depending on the nature
            of the error, either all or none of the changes will have
            been made.
        
        Returns:
          * The assignments of items to the handles of the commands, 
            as a dictionary.  
        '''
    
        if isinstance(changes, Change): changes = [changes]
        parms = {'command': 'update'}
        scanned_changes = []
        files = dict()
        for change in changes:
            scanned_change = {}
        
            if isinstance(change, CreateItem):
                scanned_change['change'] = 'create item'
                scanned_change['handle'] = change.handle
                scanned_change['source'] = change.source
                if change.read is not None: scanned_change['read'] = repr(change.read)
                if change.write is not None: scanned_change['write'] = repr(change.write)
        
            elif isinstance(change, UpdateItem):
                scanned_change['change'] = 'update item'
                scanned_change['item'] = change.item.itemid
                if change.read is not None: scanned_change['read'] = repr(change.read)
                if change.write is not None: scanned_change['write'] = repr(change.write)
        
            elif isinstance(change, DeleteItem):
                scanned_change['change'] = 'delete item'
                scanned_change['item'] = change.item.itemid
        
            elif isinstance(change, PutTriple):
                scanned_change['change'] = 'put triple'
                scanned_change['subject'] = __get_quantum__(change.subj, files)
                scanned_change['verb'] = __get_quantum__(change.vrb, files)
                scanned_change['object'] = __get_quantum__(change.obj, files)
        
            elif isinstance(change, RemoveTriples):
                scanned_change['change'] = 'remove triples'
                scanned_change['subject'] = repr(change.subj)
                scanned_change['verb'] = repr(change.vrb)
                if change.obj is not None: scanned_change['object'] = get_datum(change.obj, files)
        
            elif isinstance(change, SetUniqueObject):
                scanned_change['change'] = 'set unique object'
                scanned_change['subject'] = repr(change.subj)
                scanned_change['verb'] = repr(change.vrb)
                scanned_change['object'] = __get_quantum__(change.obj, files)
            
            scanned_changes.append(scanned_change)
            
        files.update({"changes": ("changes", json.dumps(scanned_changes), "text/plain; charset=utf-8")})
        
        if credential_and_key is not None:
            auth = __get_credential_string_and_key__(credential_and_key)
            files.update({"auth": ("auth", json.dumps(auth), "text/plain; charset=utf-8")})
            
        if meta is not None:
            scanned_meta = {k: get_datum(v, files) for (k, v) in meta.items()}
            files.update({"meta": ("meta", json.dumps(scanned_meta), "text/plain; charset=utf-8")})
            
        response = self.session.post(self.api, files=files, params=parms, timeout=self.request_timeout)
        if response.status_code == 200: return __get_items_dict__(response)
        else: __handle_http_error__(response)


def __get_credential_string_and_key__(credential_and_key):
    '''
    Get a credential and key as dictionary entries.
    
    Parameters:
      * credential_and_key: a tuple whose first element is an item
        representing a credential, and whose second element is a string 
        that is a credential key
        
    Raises: VdlException if a tuple element is not valid
    
    Returns: a dictionary with entry 'credential' containing the identifier
        of the item representing the credential, and 'key' containing the
        key.
    '''
    
    cred = credential_and_key[0]
    if isinstance(cred, Itm): cred_string = cred.itemid
    elif isinstance(cred, str): cred_string = cred
    else: raise VdlException("Invalid credential: " + str(cred));           
    return {'credential': cred_string, 'key': credential_and_key[1]}


class Constraint:
    '''
    A constraint on data to be retrieved from a virtual data lake.
    It has a subject, a verb, and an object, each of which can be
    given or unknown.
    
    A given can be an item, a boolean, an int, a float, a string, 
    a bytes object or a bytearray object. If it is an item, it can
    be an `Itm` object or a `NamedItm` object. If it is not an item,
    it is a python quantity of the appropriate type. 
    
    An unknown is a vdl Unknown object.
    
    If a subject or a verb is given, then it must be an `Itm` object
    or a `NamedItm` object, because the subjects and verbs of triples
    are items.  If an object of a constraint is given, it can be an
    `Itm` object, a `NamedItm` object, a boolean, an int, a float,
    a string, a bytes object or a bytearray object. If a subject,
    verb or object is unknown, then it is an `Unknown` object.
    
    The data retrieved from a virtual data lake using a list of constraints
    consists of a list of dictionaries. Each dictionary represents a
    solution that satisfies the constraints. The dictionary maps the 
    unknowns to the values assigned to them in the solution. The list
    is not in any particular order.
    
    The subject, verb and object of a constraint must not all be
    unknown.
    '''
    
    def __init__(self, subj, vrb, obj):
        '''
        Construct a Constraint.
        
        The supplied subject and verb can each be an item or
        an `Unknown` object
        
        The supplied object can be:
          * an item
          * an `Unknown` object
          * a bool
          * an int
          * a float
          * a str
          * a bytes object
          * a bytearray object
        
        Parameters:
          * subj: the subject of the constraint
          * vrb: the verb of the constraint
          * obj: the object of the constraint
    
        Raises:
          * VdlException if the subject, verb or object is not valid.
        '''

        if not isinstance(subj, (Itm, NamedItm, Unknown)): 
            raise VdlException("Invalid constraint subject: " + str(subj));
        if not isinstance(vrb, (Itm, NamedItm, Unknown)): 
            raise VdlException("Invalid constraint verb: " + str(vrb));
        if not isinstance(obj, (Itm, NamedItm, Unknown, bool, int, float, str, bytes, bytearray)): 
            raise VdlException("Invalid constraint object: " + str(obj));
        if isinstance(subj, Unknown) and isinstance(vrb, Unknown) and isinstance(obj, Unknown):
            raise VdlException("The subject, verb and object of a constraint must not all be unknown");
        self.subj = subj
        self.vrb = vrb
        self.obj = obj
        
        
    def __repr__(self):
        return "CONSTRAINT(" + self.subj.__repr__() + ', ' + self.vrb.__repr__() + ', ' + self.obj.__repr__() + ')'
        
        
def __get_constraint__(constraint_or_tuple):
    '''
    Get a constraint that is supplied either as a 'Constraint' object
    or as a 3-tuple whose elements are the constraint's subject, verb
    and object.
    
    Parameters:
      * constraint_or_tuple: either a `Constraint` object or a
        3-tuple whose elements are the constraint's subject, verb
        and object.
        
    Raises:
      * VdlException: if a tuple is supplied that is not a 3-tuple
        containing constraint's subject, verb and object.
    
    Returns: a `Constraint` object.
    
    '''
    
    if isinstance(constraint_or_tuple, Constraint): return constraint_or_tuple
    if isinstance(constraint_or_tuple, tuple) and len(constraint_or_tuple) == 3: 
        return Constraint(constraint_or_tuple[0], constraint_or_tuple[1], constraint_or_tuple[2])
    raise VdlException("Not a constraint: " + str(constraint_or_tuple))
      

class Change:
    '''
    A virtual data lake change.
    
    '''
    
    def __init__(self):
        '''
        Construct a virtual data lake change.
        
        There is seldom any need to instantiate this class.
        It is the instances of its subclasses that are useful.
        '''
        pass
    
    
class CreateItem(Change):
    '''
    A virtual data lake change that creates an item.
    '''
    
    def __init__(self, handle, source, read=None, write=None):
        '''
        Construct a virtual data lake change that creates an item.
        
        Parameters:
          * handle: a handle that can be used to refer to the created item 
            in subsequent changes. It can be supplied as an alphanumeric 
            string or as an `Unknown` object whose name is to be used as the
            handle. 
          * source(int): the numeric identifier of the source in which
            the item is to be created.
          * read: the read access level of the item to be created. 
            This is an item, specified as an `Itm` object or a `NamedItm`
            object. It defaults to the access level of the session making
            the request. Note that access levels defined in a source are
            named items, even though they aren't shown on the source's Items
            page. For example, the 'admin' access level of source 12 is 
            NamedItem(12, 'admin').
          * write: the write access level of the item to be created. 
            This is an item, specified as an `Itm` object or a `NamedItm`
            object. It defaults to the access level of the session making the
            request.
            
        Raises: 
          * VdlException if the handle is neither a string nor an `Unknown` object.
        '''
        
        if isinstance(handle, str): self.handle = handle
        elif isinstance(handle, Unknown): self.handle = handle.name
        else:  raise VdlException('Not a valid handle ' + str(handle))
        self.source = source
        self.read = read
        self.write = write
        
        
    def __repr__(self):
        if self.read is None: prread = " WITH DEFAULT READ LEVEL"
        else: prread = " WITH READ LEVEL " + self.read.__repr__()
        if self.write is None: prwrite = " AND DEFAULT WRITE LEVEL"
        else: prwrite = " WITH WRITE LEVEL " + self.write.__repr__()
        return "CREATE ITEM " + self.handle + ' IN SOURCE ' + str(self.source) + prread + prwrite
    
    
class UpdateItem(Change):
    '''
    A virtual data lake change that updates an item, changing its access levels.
    '''
    
    def __init__(self, item, read, write=None):
        '''
        Construct a virtual data lake change that updates an item.
        
        Parameters:
          * item(`Itm`) the item to be updated.
          * read: the read access level that the item is to have. 
            This is an item, specified as an `Itm` object or a `NamedItem`
            object. If it is None then the item's read level is not changed.
            Note that access levels defined in a source are named items, even
            though they aren't shown on the source's Items page. For example,
            the 'admin' access level of source 12 is NamedItem(12, 'admin').
          * write: the write access level that the item is to have. 
            This is an item, specified as an `Itm` object or a `NamedItem`
            object. If it is not supplied or None then the item's write level
            is not changed.
            
        Raises: 
          * VdlException if the item is not an `Itm` object, or if the
            read and write levels are both None.
        '''
        
        if not isinstance(item, Itm): raise VdlException('Not a valid item ' + str(item))
        if read is None and write is None: 
            raise VdlException('A new read level or a new write level must be supplied')
        self.item = item
        self.read = read
        self.write = write
        
        
    def __repr__(self):
        if self.read is None: prread = None
        else: prread = "READ LEVEL " + str(self.read)
        if self.write is None: prwrite = None
        else: prwrite = "WRITE LEVEL " + str(self.write)
        ret = "UPDATE ITEM " + self.item + ' WITH ' 
        if prread is None: ret = ret + prwrite
        else:
            ret = ret + prread
            if prwrite is not None: ret = ret + ' AND ' + prwrite
        return ret
    
    
class DeleteItem(Change):
    '''
    A virtual data lake change that deletes an item.
    '''
    
    def __init__(self, item):
        '''
        Construct a virtual data lake command that deletes an item.
        
        Parameters:
          * item: (`Itm`) the item to be deleted. 
        '''
        
        self.item = item
        
        
    def __repr__(self):
        return "DELETE " + self.item.__repr__()
    
    
class PutTriple(Change):
    '''
    A virtual data lake change that puts a triple.
    '''
    
    def __init__(self, subj, vrb, obj):
        '''
        Construct a virtual data lake change that puts a triple.
        
        This method ensures that a triple with the given subject,
        verb and object exists in the virtual data lake. If one
        exists already, a new one will not be created.
        
        Parameters:
          * subj: the subject. This can be an item, specified as an
            `Itm` object or a `NamedItem` object, or an `Unknown` that
            is the handle of an object created in a previous change.
          * vrb: the verb. This can be an item, specified as an `Itm`
            object or a `NamedItem` object, or an `Unknown` that is 
            the handle of an object created in a previous change.
          * obj: the object. This can be an item, a Boolean, an integer, 
            a real number, a text object or a binary object. An item is
            specified as an `Itm` object or a `NamedItem` object, or is
            an `Unknown` that is the handle of an object created in a
            previous change. A Boolean is given as a bool, an integer as 
            an int, a real number as a float, a text object as a string, 
            and a binary object as either a bytes or a bytearray.
        '''
    
        self.subj = subj
        self.vrb = vrb
        self.obj = obj
        
        
    def __repr__(self):
        return "PUT TRIPLE(" + self.subj.__repr__() + ', ' + self.vrb.__repr__() + ', ' + self.obj.__repr__() + ')'
    
    
class RemoveTriples(Change):
    '''
    A virtual data lake change that removes one or more triples.
    '''
    
    def __init__(self, subj, vrb, obj=None):
        '''
        Construct a virtual data lake change that removes one or more triples.
        If an object is given, all triples with the given subject,
        verb and object are removed. (Normally, there will only be one
        such triple.) If no object is given, all triples with the given
        subject and verb are removed.
        
        Parameters:
          * subj: the subject. This is an item, specified as an `Itm`
            object or a `NamedItem` object.
          * vrb: the verb. This is an item, specified as an `Itm` object
            or a `NamedItem` object.
          * obj: the object. This can be an item, a Boolean, an integer, 
            a real number, a text object or a binary object. An item is
            specified as an `Itm` object or a `NamedItem`  object. A Boolean
            is given as a bool, an integer as an int, a real number as a
            float, a text object as a string, and a binary object as either
            a bytes or a bytearray.
        '''
    
        self.subj = subj
        self.vrb = vrb
        self.obj = obj
        
        
    def __repr__(self):
        if self.obj is None: printobj = 'ALL'
        else: printobj = self.obj.__repr__()
        return "REMOVE TRIPLES(" + self.subj.__repr__() + ', ' + self.vrb.__repr__() + ', ' + printobj + ')'
    
    
class SetUniqueObject(Change):
    '''
    A virtual data lake change that sets a unique object for a given
    subject and verb.
    '''
    
    def __init__(self, subj, vrb, obj):
        '''
        Construct a virtual data lake change that sets a unique object
        for a given subject and verb.
        
        This method ensures that a triple with the given subject,
        verb and object exists in the virtual data lake and that
        there are no other triples with the given subject and verb. 
        
        If a triple with the subject, verb and object exists already, 
        a new one need not be created. If more than one triple 
        with the given subject and verb exists, then all but one
        will be deleted.
        
        Parameters:
          * subj: the subject. This is specified as an `Itm` object or a
            `NamedItem` object.
          * vrb: the verb. This is specified as an `Itm` object or a
            `NamedItem` object.
          * obj: the object. This can be an item, a Boolean, an integer, 
            a real number, a text object or a binary object. An item can
            be specified as an `Itm` object or a `NamedItem` object, or by
            an `Unknown` that is the handle of an object created in a
            previous change. A Boolean is given as a bool, an integer as an
            int, a real number as a float, a text object as a string, and a
            binary object as either a bytes or a bytearray.
        '''
    
        self.subj = subj
        self.vrb = vrb
        self.obj = obj
        
        
    def __repr__(self):
        return "SET UNIQUE OBJECT(" + self.subj.__repr__() + ', ' + self.vrb.__repr__() + ', ' + self.obj.__repr__() + ')'
        

class Unknown:
    '''
    An unknown value in a constraint.
    '''
    
    def __init__(self, name):
        '''
        Construct an Unknown
        
        Parameters:
          * name: the name of the unknown (e.g. 'x')
        '''
        
        self.name = name
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return "UNKNOWN " + self.name

   
class Itm:
    '''
    A class whose objects represent items in the virtual data lake.
    
    An item in turn typically represents a real world object or property.
    '''
    def __init__(self, itemid):
        '''
        Construct a representation of an item.
        
        Parameters:
          * itemid(str): the identifier of an item.
          Item identifiers are assigned automatically by the virtual data lake.
          It is not possible to create an item with an arbitrary identifier.
          This constructor is used by functions that have obtained item identifiers
          by interacting with the virtual data lake or from user input. 
        '''
        self.itemid = itemid
         
    def __repr__(self):
        return str(self.itemid)
         
    def __str__(self):
        return "ITEM " + str(self.itemid)
    
    def __eq__(self, other):
        return isinstance(other, Itm) and self.itemid == other.itemid
    
    def __hash__(self):
        return hash(self.itemid)
    
    
class NamedItm:
    '''
    A class whose objects represent named items in the virtual data lake. 
    '''

    def __init__(self, source, name):
        '''
        Construct a representation of a named item that exists in the virtual data lake.
        (This does not create a named item in the virtual data lake if there is not
        already one with the given source and name.)
        
        Parameters:
          * source (int): the numeric identifier of the source containing the item.
          * name (str): the name of the item, unique within its source.
        '''
        
        self.source = source
        self.name = name
        
    def __repr__(self):
        return repr(self.source) + ':' + self.name        
        
    def __str__(self):
        return "NAMED ITEM " + str(self.source) + ':' + self.name
    
    def __eq__(self, other):
        return isinstance(other, NamedItm) and self.source == other.source and self.name == other.name
    
    def __hash__(self):
        return hash(self.source) ^ hash(self.name)
    

class Triple:
    '''
    A class whose objects represent triples in the virtual data lake.
    
    A triple has a subject, a verb, and an object. 
    (Note that the word "object" is used here in the sense 
    of a component of a triple rather than a member of a Python class.) 
    The subject of a triple is an item.
    The verb of a triple is an item.
    The object of a triple can be: an item, a Boolean, an integer, a real number,
    a piece of text, or a sequence of bytes.
    '''
    def __init__(self, subj, vrb, obj):
        '''
        Construct a representation of a triple.
        
        Parameters:
          * subj(`Itm`) a representation of the subject of the triple.
          * vrb(`Itm`): a representation of the verb of the triple.
          * obj: the object of the triple. 
        This can be: an `Itm` object that represents an item, a bool,
        an int, a float, a str, a bytes object, or a bytearray object.
        '''
        self.subj = subj
        self.vrb = vrb
        self.obj = obj
         
    def __repr__(self):
        return '<' + repr(self.subj) + "," + repr(self.vrb) + "," + repr(self.obj) + '>'
         
    def __str__(self):
        return "TRIPLE " + str(self.subj) + ", " + str(self.vrb) + ", " + str(self.obj) 


class VdlException(RuntimeError):
    '''
    A run-time exception occurring during execution of a 
    virtual data lake access function.
    '''
    def __init__(self, *messages):
        super().__init__(*messages)
       
  
def __get_assignments_dict__(response):
    '''
    Get a dict that contains a set of assignments of values to 
    unknowns from the content of a request response.
    
    Parameters:
      * content: the content of a request response returned by the
        imported requests module.
      
    Raises:
      * VdlException
      * PartException
      
    Returns:
      * a dict containing the set of values.
    '''
    
    parts = __get_parts__(response)
    json_part = parts['json']
    if json_part is None: raise VdlException('No JSON part')
    assignments = json.loads(json_part.content().decode())
    if not isinstance(assignments, dict): raise VdlException('Not a value set')
    return __get_assigned_values__(assignments, parts)
       
  
def __get_assignments_dict_list__(response):
    '''
    Get a list of dicts, each of which contains a set of assignments
    of values to unknowns, from the content of a request response.
    
    Parameters:
      * content: the content of a request response returned by the
        imported requests module.
      
    Raises:
      * VdlException
      * PartException
      
    Returns:
      * a list of dicts, each of which contains a set of assignments
        of values to unknowns.
    '''
    
    parts = __get_parts__(response)
    json_part = parts['json']
    if json_part is None: raise VdlException('No JSON part')
    assignments_list = json.loads(json_part.content().decode())
    if not isinstance(assignments_list, list): 
        raise VdlException('Not a list of value sets')
    values_list = []
    for assignments in assignments_list:
        if not isinstance(assignments, dict): raise VdlException('Not a value set')
        values_list.append(__get_assigned_values__(assignments, parts))
    return values_list
    
    
def __get_assigned_values__(assignments_dict, parts):
    '''
    Get the assigned values from an assignments dictionary in
    a multipart response.
    
    The content is returned in multipart form data format. One of
    the parts is named 'json' and contains one or more assignments 
    dictionaries. The assignments dictionaries assign python data
    values to the names. The python types of the python data values 
    depend on the virtual data lake types of the corresponding
    objects in the virtual data lake.
    
    A virtual data lake object can have one of these types: ITEM,
    BOOLEAN, INTEGRAL, REAL, TEXT, or BINARY. The corresponding
    python data types are `Itm`, bool, int, float, str, and bytes
    (or bytearray).
    
    Each entry of the assigments dictionaries is a name-value pair,
    where the value is another dictionary, which has two items: 
    'type' and 'value'. The 'type' is ITEM, BOOLEAN, INTEGRAL, REAL, 
    TEXT, or BINARY.
    
    If the type is ITEM, the value is a str that is an item identifier,
    and the assigned python data value is an `Itm` object whose itemid
    is that identifier. If the type is BOOLEAN, INTEGRAL, or REAL, 
    the value is a str representing a bool, int, or float, as appropriate,
    and the assigned python data value is the value represented by the str.
    If the type is TEXT, the value is a str and the assigned value is
    that str. If the type is BINARY, the value is a str that is the name 
    of a part of the multipart response whose content type is 
    application/octet-stream, and the assigned python value is its content.
    
    Parameters:
      * assignments_dict: an assignments dictionary in a multipart response.
      * parts: the parts of the multipart response
      
    Raises:
      * VdlException
      
    Returns:
      * a dict containing the assigned values.
    '''
    
    assigned_values = {}
    for assignment in assignments_dict.items():
        name = assignment[0]
        value_dict = assignment[1]
        if not isinstance(value_dict, dict): raise VdlException('Invalid JSON content')
        value_type = value_dict['type']
        value = value_dict['value']
        if name is None or value_type is None or value is None:
            raise VdlException('Invalid assignment in JSON content')
        if value_type == "ITEM": 
            assigned_values[name] = Itm(value)
        elif value_type == "BOOLEAN": 
            assigned_values[name] = (value.lower() == "true")
        elif value_type == "INTEGRAL": 
            assigned_values[name] = int(value)
        elif value_type == "REAL": 
            assigned_values[name] = float(value)
        elif value_type == "TEXT": 
            assigned_values[name] = value
        elif value_type == "BINARY": 
            part = parts[value]
            if part is None: raise VdlException('Missing binary content for: ' + name)
            assigned_values[name] = part.content()
        else: assigned_values[name] = str(value)
    return assigned_values
       
  
def __get_items_dict__(response):
    '''
    Get a dictionary keyed by item handles whose values are items
    from the content of a request response.
    
    Parameters:
      * content: the content of a request response returned by the
        imported requests module.
      
    Raises:
      * VdlException
      * PartException
      
    Returns:
      * a dictionary keyed by item handles whose values are item 
      identifiers.
    '''
    
    parts = __get_parts__(response)
    json_part = parts['json']
    if json_part is None: raise VdlException('No JSON part')
    itemids_dict = json.loads(json_part.content().decode())
    if not isinstance(itemids_dict, dict): 
        raise VdlException('Not a dict of item identifiers')
    items_dict = {}
    for handle in itemids_dict: items_dict[handle] = Itm(itemids_dict[handle])
    return items_dict


def __get_parts__(response):
    '''
    Get the parts of a multi-part response
    
    Parameters:
      * response: a requests response object with
        multipart/form-data-encoded content
        
    Raises:
      * VdlException
      * PartException
      
    Returns:
      * the parts of the response, as a dictionary of
        parts.part objects
    '''
    
    content_type = response.headers.get('content-type')
    if content_type is None: raise VdlException(
        'No content type header. The operation may succeed if re-tried.')
    content_type_line = 'Content-Type: ' + content_type 
    content_type_header = parts.Header(content_type_line)
    boundary = content_type_header.get_parm('boundary')
    return parts.get_parts(response.content, boundary)
       
       
def __get_quantum__(spec, files):
    '''
    Get the representation of a quantity that can be given as a 
    particular item or piece of data or can be unknown.
    
    For a 'given' quantity, the value is a dict with entries
    'type' and 'value', where the type can be: 
      * ITEM: the value is then the item identifier or the item's 
        qualified name
      * BOOLEAN: the value is then a bool
      * INTEGRAL: the value is then an int
      * REAL: the value is then a float
      * TEXT: the value is then a str
      * BINARY: the value is then the name of an entry in the
        files dict, and the value of that entry is a bytes or 
        bytearray object.
      
    For an 'unknown' entry, the value is a dict with one entry:
    'unknown' whose value is the name of the unknown.
    
    Parameters:
      * spec: a specification of the subject, verb, or object.
        For a given item, this can be specified as an `Itm` object
        or a `NamedItem` object. For a given piece of data, it can be
        a bool, int, float, or str. For a binary object, it is the name
        of a files dict entry whose value is a bytes, or bytearray
        object. For an unknown quantity, it is an `Unknown` object.
      
    Raises:
      * VdlException if the specification is invalid
      
    Returns:
      * the representation of the specified quantity.
    '''
    
    if isinstance(spec, Unknown): return {'unknown': repr(spec)}
    else: return get_datum(spec, files)
       
       
def get_datum(spec, files):
    '''
    Get the representation of a quantity that is a particular item or 
    piece of data.
    
    The value is a dict with entries
    'type' and 'value', where the type can be: 
      * ITEM: the value is then the item identifier or the item's 
        qualified name
      * BOOLEAN: the value is then a bool
      * INTEGRAL: the value is then an int
      * REAL: the value is then a float
      * TEXT: the value is then a str
      * BINARY: the value is then the name of an entry in the
        files dict, and the value of that entry is a bytes or 
        bytearray object.
    
    Parameters:
      * spec: a specification of the subject, verb, or object.
        For a given item, this can be specified as an `Itm` object
        or a `NamedItem` object. For a given piece of data, it can
        be a  bool, int, float, or str. For a binary object, it is
        the name of a files dict entry whose value is a bytes, or
        bytearray object. 
      * files: a dict of binary values
      
    Raises:
      * VdlException if the specification is invalid
      
    Returns:
      * the representation of the specified quantity.
    '''
    
    if isinstance(spec, Itm): return {'type': 'ITEM', 'value': repr(spec)}
    elif isinstance(spec, NamedItm): return {'type': 'ITEM', 'value': repr(spec)}
    elif isinstance(spec, bool): return {'type': 'BOOLEAN', 'value': repr(spec)}
    elif isinstance(spec, int): return {'type': 'INTEGRAL', 'value': repr(spec)}
    elif isinstance(spec, float): return {'type': 'REAL', 'value': repr(spec)}
    elif isinstance(spec, str): return {'type': 'TEXT', 'value': str(spec)}
    elif isinstance(spec, bytes) or isinstance(spec, bytearray):
        i = len(files)
        files.update({'b'+repr(i): ('b'+repr(i), spec, 'application/octet-stream')})
        return {'type': 'BINARY', 'value': 'b'+repr(i)}
    else: raise VdlException('Invalid specification: ' + str(spec))
        
                        
def __handle_http_error__(response):
    '''
    Handle an error that occurs during an HTTP communication
    with a virtual data lake. The error may occur in transmission
    or during execution of the request by the virtual data lake.
    
    Parameters:
      * response the response to the HTTP request returned by the 
        imported requests module   
      
    Raises:
      * VdlException
    '''
    
    msg = None
    try:
        msg = response.json()['error']
    except:
        msg = str(response.status_code) + ': ' + response.reason
    raise VdlException(msg)
