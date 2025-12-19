'''
This module copies of dictionaries between Python programs and 
virtual data lakes.

Each attribute of a dictionary to be copied must be mapped to a 
virtual data lake named item. The dictionary is represented by 
an item in the virtual data lake, with triples for its attributes 
whose verbs are the associated named items and whose objects are 
the attribute values. An attribute value can be a bool, int, 
float, str, bytes or bytearray object, a list, or a nested dict. 
The elements of list attributes can be bool, int, float, str, 
bytes or bytearray objects, or nested dicts, but must not be 
nested lists. Sets and tuples are not supported. 

The copy operations DO NOT PRESERVE THE ORDER OF LIST ELEMENTS
'''

from . import vdl


class CopyClient:
    '''
    A client that copies dictionaries to and from virtual data lakes.
    '''

    def __init__(self, vdl_client):
        '''
        Construct a copy client

        Parameters:
          * vdl_client a vdl Client object to do the copying.
        '''

        self.vdl_client = vdl_client
        self.attributes_by_name = {}
        
        
    def register_attribute(
            self, attribute_name, verb_source, verb_name):
        '''
        Register an attribute

        Parameters:
          * attribute_name(str) the name of the attribute to be registered. 
            This must not be '_itemid' as this name is reserved for use by 
            the module.
          * verb_source(int) the numeric identifier of the virtual data 
            lake source containing the named item to be mapped to the 
            attribute
          * verb_name(str) the name of the named item

        Raises:
          * `VdlCopyException` if an invalid input is supplied.
        '''

        if attribute_name == '_itemid': raise VdlCopyException(
                'You cannot register "_itemid" as an attribute')
        self.attributes_by_name[attribute_name
                ] = VdlCopyAttribute(verb_source, verb_name)
    
    
    def copy_to_vdl(
            self, dict_to_copy, source_nr, read_level,
            write_level, credential_and_key=None):
        '''
        Copy a dictionary to the virtual data lake

        Parameters:
          * dict_to_copy(dict) the dictionary to be copied
          * source_nr(int) the numeric identifier of the virtual data lake 
            source into which the dictionary is to be copied.
          * read_level a vdl Itm object that is to be the only-read 
            access level of any virtual data lake items that are created.
          * write_level a vdl Itm object that is to be the read-or-write 
            access level of any virtual data lake items that are created.
          * credential_and_key a 2-tuple whose first element is either a
            vdl Itm object that is a credential to authorize the request 
            or the identifier of such an object, and whose second element
            is the credential's key, to be supplied as a parameter to
            vdl client update requests
            
        Returns:
          * A deep copy of the supplied `dict_to_copy` with an added
            '_itemid' attribute whose value is the identifier of the vdl 
            Itm object representing the dictionary in the virtual data 
            lake. Nested dictionaries that are attribute values also have 
            '_itemid' attributes giving the identifiers of the vdl Itm 
            objects that represent them.

        Raises:
          * `VdlCopyException` if an error is detected in the parameters.
        '''

        changes = []
        next_handle_nr = 0
        (dict_to_return, next_handle_nr
         ) = self.__add_copy_dict_changes__(
                dict_to_copy, source_nr, read_level, write_level, 
                next_handle_nr, changes)
        # The changes list will have been updated
        item_assignments = self.vdl_client.update(
                changes, credential_and_key)
        __add_item_assignments__(item_assignments, dict_to_return)
        # dict_to_return will have been updated
        return dict_to_return
      
        
    def copy_from_vdl(
            self, main_item, copy_spec, credential_and_key=None):
        '''
        Copy a dictionary from the virtual data lake

        Parameters:
          * main_item the vdl Itm object representing the dictionary to 
            be copied
          * copy_spec(dict) a dict with an attribute for each attribute
            of the dictionary to be copied. The following rules apply
            to the attributes.
              - If the value of that attribute is bool, int, float, str 
                or vdl.Itm, then the value of the attribute to be copied 
                is an object of that type.              
              - If the value of that attribute is None then then the value 
                of the attribute to be copied can be a bool, int, float, 
                str or vdl.Itm            
              - If the value of that attribute is a dict then then the 
                value of the attribute to be copied is a dict, and these
                rules apply recursively to its attributes
              - If the value of that attribute is a list then it will have 
                a single element, which can be bool, int, float, str,
                vdl.Itm or dict, and the value of the attribute to be 
                copied will be a list of objects of that type.            
            The names of the attributes must have been registered with 
            the `VdlCopyClient` via its `register_attribute` method. The 
            virtual data lake must have a triple giving a value for each
            attribute or an empty copy will be returned.
          * credential_and_key a 2-tuple whose first element is either a
            vdl Itm object that is a credential to authorize the request 
            or the identifier of such an object, and whose second element
            is the credential's key, to be supplied as a parameter to
            vdl client update requests
            
        Returns:
          * the dictionary copied from the virtual data lake. As well as
            the requested attributes, the dictionary has an '_itemid' 
            attribute whose value is the identifier of the Itm object
            representing the dictionary in the virtual data lake. For
            the main dictionary, this is the identifier of the supplied
            `main_item` parameter. Nested dictionaries that are attribute
            values also have '_itemid' attributes giving the identifiers
            of the Itm objects that represent them.

        Raises
          * `VdlCopyException` if an error is detected in the parameters.
        '''

        copier = Copier(copy_spec)
        constraints = []
        self.__add_constraints__(copier, main_item, 0, constraints)
        # Constraints and copier will have been updated
        solutions = self.vdl_client.query(constraints, credential_and_key)
        return __get_copied_dict__(main_item, copier, solutions)
    
    
    def remove_from_vdl(self, main_item, copy_spec, credential_and_key=None):
        '''
        Remove a dictionary from the virtual data lake

        Parameters:
          * main_item the vdl Itm object representing the dictionary to 
            be removed
          * copy_spec(dict) a dict with an attribute for each attribute
            of the dictionary to be removed. The following rules apply
            to the attributes.
              - If the value of that attribute is bool, int, float, str 
                or vdl.Itm, then the value of the attribute of the dict
                to be removed is an object of that type.              
              - If the value of that attribute is None then then the value 
                of the attribute of the dict to be removed can be a bool, 
                int, float, str or vdl.Itm            
              - If the value of that attribute is a dict then then the 
                value of the attribute  of the dict to be removed is a
                dict, and these rules apply recursively to its attributes
              - If the value of that attribute is a list then it will have 
                a single element, which can be bool, int, float, str,
                vdl.Itm or dict, and the value of the attribute  of the 
                dict to be removed will be a list of objects of that type.            
            The names of the attributes must have been registered with 
            the `VdlCopyClient` via its `register_attribute` method. The 
            virtual data lake must have a triple giving a value for each
            attribute or nothing will  be removed.
          * credential_and_key a 2-tuple whose first element is either a
            vdl Itm object that is a credential to authorize the request 
            or the identifier of such an object, and whose second element
            is the credential's key, to be supplied as a parameter to
            vdl client update requests
            
        Returns:
          * the dictionary removed from the virtual data lake. As well as
            the requested attributes, the dictionary has an '_itemid' 
            attribute whose value is the identifier of the Itm object
            representing the dictionary in the virtual data lake. For
            the main dictionary, this is the identifier of the supplied
            `main_item` parameter. Nested dictionaries that are attribute
            values also have '_itemid' attributes giving the identifiers
            of the Itm objects that represent them. The items whose
            identifiers are returned in '_itemid' attributes will all
            have been deleted.

        Raises
          * `VdlCopyException` if an error is detected in the parameters.
        '''
        copied_dict  = self.copy_from_vdl(
                main_item, copy_spec, credential_and_key)
        if len(copied_dict) == 0: return
        changes = []
        __add_remove_changes__(copied_dict, changes)
        # Constraints will have been updated
        self.vdl_client.update(changes, credential_and_key)
        return copied_dict
                                    
    
    def __add_copy_dict_changes__(
            self, dict_to_copy, source_nr, read_level, write_level, 
            next_handle_nr, changes):
        '''
        Add to a supplied list of changes the changes to copy a 
        dictionary to the virtual data lake. This method invokes
        itself recursively when it encounters an attribute whose
        value is a nested dictionary.
        
        Parameters:
          * dict_to_copy(dict) the dictionary to be copied
          * source_nr(int) the numeric identifier of the virtual data lake 
            source into which the dictionary is to be copied.
          * read_level a vdl Itm object that is to be the only-read 
            access level of any virtual data lake items that are created.
          * write_level a vdl Itm object that is to be the read-or-write 
            access level of any virtual data lake items that are created.
          * next_handle_nr(int) the number to be used to generate the
            handle for the next vdl CreateItem change. It is incremented
            each time an item is created.
          * changes(list) the list of changes to be added to
          
        Returns:
          * a copy of the supplied `dict_to_copy` with an added '_itemid'
            attribute and with the values of attributes that are nested
            dictionaries replaced by copies that also have added '_itemid'
            attributes
          * the `next_handle_nr` parameter incremented for all CreateItem
            changes for the supplied `dict_to_copy` and nested directories
        '''
        
        dict_to_return = dict_to_copy.copy()
        subject_handle = 'H' + str(next_handle_nr)
        next_handle_nr += 1
        changes.append(vdl.CreateItem(
                subject_handle, source_nr, read_level, write_level))
        for (name, value) in dict_to_return.items():
            attribute = self.attributes_by_name.get(name)
            if attribute is None: raise VdlCopyException(
                    'VDL Copy attribute is not registered: ' + name)
            if isinstance(value, dict):
                object_handle = 'H' + str(next_handle_nr)
                (updated_dict_value, next_handle_nr
                 ) = self.__add_copy_dict_changes__(
                        value, source_nr, read_level, write_level, 
                        next_handle_nr, changes)
                # The changes list will have been updated
                # object_handle will have been used to create
                # the item for the nested dictionary
                changes.append(vdl.PutTriple(
                        vdl.Unknown(subject_handle),
                        vdl.NamedItm(attribute.verb_source, 
                                     attribute.verb_name),
                        vdl.Unknown(object_handle)))                        
                dict_to_return[name] = updated_dict_value
            elif isinstance(value, list):
                for i in range(len(value)):
                    elt = value[i]
                    if isinstance(elt, dict):
                        object_handle = 'H' + str(next_handle_nr)
                        (updated_dict_value, next_handle_nr
                         ) = self.__add_copy_dict_changes__(
                                elt, source_nr, read_level, write_level, 
                                next_handle_nr, changes)
                        # The changes list has been updated
                        # object_handle will have been used to create
                        # the item for the nested dictionary
                        changes.append(vdl.PutTriple(
                                vdl.Unknown(subject_handle),
                                vdl.NamedItm(attribute.verb_source, 
                                             attribute.verb_name),
                                vdl.Unknown(object_handle)))                        
                        value[i] = updated_dict_value
                    elif isinstance(elt, list): 
                        raise VdlCopyException(
                                'List with nested list member supplied ') + (
                                'for attribute: ' + name)
                    elif isinstance(elt, 
                                    (bool, int, float, str, 
                                     bytes, bytearray, vdl.Itm)):
                        changes.append(vdl.PutTriple(
                                vdl.Unknown(subject_handle),
                                vdl.NamedItm(attribute.verb_source, 
                                             attribute.verb_name),
                                elt))                        
                    else: raise VdlCopyException(
                            'Invalid value supplied for member of list ' + (
                            'attribute: ' + name + '-' + str(elt)))
            elif isinstance(value, 
                            (bool, int, float, str, 
                             bytes, bytearray, vdl.Itm)):
                changes.append(vdl.PutTriple(
                        vdl.Unknown(subject_handle),
                        vdl.NamedItm(attribute.verb_source, 
                                     attribute.verb_name),
                        value))
            else: raise VdlCopyException(
                    'Invalid value supplied for attribute ' + (
                    name + ': ' + str(value)))
        dict_to_return['_itemid'] = subject_handle     
        return (dict_to_return, next_handle_nr)


    def __add_constraints__(
            self, copier, subject_quantum, next_unknown_nr, 
            constraints):
        '''
        Add to a supplied list of constraints the constraints to 
        retrieve the data to be copied to a dictionary from the virtual
        data lake. This method invokes itself recursively when it 
        encounters an attribute whose value is a nested dictionary.
        
        Parameters:
          * copier a 'Copier' object supporting the copy operation
          * subject_quantum the vdl Itm object representing the 
            dictionary in the virtual data lake, or the vdl.Unknown
            object used to retrieve that item if it is not known
          * next_unknown_nr(int) the number to be used to generate the
            next vdl Unknown object in queries to retrieve data from the
            virtual data lake. It is incremented whenever a vdl Unknown 
            object is created.
          * constraints(list) the list of constraints to be added to
          
        Returns:
          * The updated value of `next_unknown_nr`
        '''
        for (name, copier_attribute
             ) in copier.copier_attributes_dict.items():
            attribute = self.attributes_by_name.get(name)
            if attribute is None: 
                raise VdlCopyException(
                        'Copy attribute is not registered: ' + name)
            object_unknown_name = 'H' + str(next_unknown_nr)
            next_unknown_nr += 1
            copier_attribute.unknown_name = object_unknown_name
            object_unknown = vdl.Unknown(object_unknown_name)
            constraints.append(vdl.Constraint(
                    subject_quantum,
                    vdl.NamedItm(attribute.verb_source,
                                 attribute.verb_name),
                    vdl.Unknown(object_unknown_name)))
            if isinstance(copier_attribute.value_type, Copier):
                next_unknown_nr = self.__add_constraints__(
                    copier_attribute.value_type, object_unknown, 
                    next_unknown_nr, constraints)
        return next_unknown_nr


def __add_remove_changes__(copied_dict, changes):
    '''
    Add to a supplied list of changes the changes to remove a 
    dictionary from the virtual data lake. This method invokes
    itself recursively when it encounters an attribute whose
    value is a nested dictionary.
    
    Parameters:
      * copied_dict(dict) a copy retrieved by `copy_from_vdl`
        of the dictionary to be removed
      * changes(list) the list of changes to be added to
    '''
    
    for value in copied_dict.values():
        if isinstance(value, dict):
            __add_remove_changes__(value, changes)
    changes.append(vdl.DeleteItem(vdl.Itm(copied_dict['_itemid'])))
  
    
def __add_item_assignments__(item_assignments, returned_dict):
    '''
    Add to a dictionary copied to the virtual data lake 
    '_itemid' attributes giving the items representing the 
    dictionary and nested directory attributes
    
    Parameters:
      * item_assignments(dict) the assignments of items to the 
        handles of changes returned by the vdl update method
        invocation that copied the dictionary to the virtual
        data lake
      * returned_dict(dict) a deep copy of the dict that was 
        copied to the virtual data lake 
    '''
    
    item_handle = returned_dict['_itemid']
    assigned_item = item_assignments[item_handle]
    returned_dict['_itemid'] = assigned_item.itemid
    for value in returned_dict.values():
        if isinstance(value, dict):
            __add_item_assignments__(item_assignments, value)
        elif isinstance(value, list):
            for elt in value:
                if isinstance(elt, dict):
                    __add_item_assignments__(item_assignments, elt)


def __get_copied_dict__(item, copier, solutions):
    '''
    Create a dictionary from data copied from the virtual data lake
    for return to the program that requested the copy. This method
    is used to create the main directory and for nested directories 
    that are values of its attributes.
        
    Parameters:
      * item the vdl Itm object for the virtual data lake item that 
        represents the dictionary
      * copier a 'Copier' object supporting the copy operation
      * solutions a list of dictionaries of values keyed
        by arbitrary handles and retrieved from the data lake.
            
    Returns:
      * a dictionary in accordance with the copier parameter
        containing data copied from the virtual data lake.
        If there is no data to copy, an empty dictionary is
        returned.
    '''
    if len(solutions) == 0: return {}
    copied_dict = {'_itemid': item.itemid}
    for (name, copier_attribute
         ) in copier.copier_attributes_dict.items(): 
        if copier_attribute.single_valued:
            value = __get_single_value__(
                    name, copier_attribute, solutions)
            if isinstance(
                    copier_attribute.value_type, Copier):
                copied_dict[name] = (
                        __get_copied_dict__(
                                value, 
                                copier_attribute.value_type, 
                                solutions))
            else: copied_dict[name] = value
        elif isinstance(copier_attribute.value_type, Copier):
            copied_dict[name] = [
                    __get_copied_dict__(
                            vdl.Itm(itemid), 
                            copier_attribute.value_type, 
                            value_solutions)
                    for (itemid, value_solutions
                         ) in __get_multi_dict_solutions_by_itemid__(
                                name, copier_attribute, solutions
                            ).items()]
        else: copied_dict[name] = __get_multi_value__(
                copier_attribute, solutions)
    return copied_dict 


def __get_single_value__(
        name, copier_attribute, solutions):
    '''
    Get the value of an attribute defined as having a unique
    value from data copied from the virtual data lake.
        
    Parameters:
      * name(str) the name of the attribute
      * copier_attribute a `CopierAttribute` object for the
        attribute to be copied
      * solutions a list of dictionaries of values keyed by
        arbitrary handles and retrieved from the data lake.
            
    Returns: 
      * the value of the attribute, which may be a primitive 
        object or a dict
    '''
    value_to_return = None
    for solution in solutions:
        value = solution[copier_attribute.unknown_name]     
        if isinstance(value, vdl.Itm): 
            value = ('I', value.itemid)
        elif isinstance(value, bytearray): 
            value = bytes(value)
        if value_to_return is None:
            value_to_return = value
        elif value_to_return != value:
            raise VdlCopyException(
                    'Multiple values for single-' +
                    'valued attribute: ' + name)
    if isinstance(value_to_return, tuple): 
        value_to_return = vdl.Itm(value_to_return[1])
    __check_type__(value_to_return, copier_attribute.value_type)
    return value_to_return


def __get_multi_value__(copier_attribute, solutions):
    '''
    Get the value of an attribute defined as not having a unique
    value and that is not a nested dictionary from data copied 
    from the virtual data lake.
        
    Parameters:
      * copier_attribute a `CopierAttribute` object for the
        attribute to be copied
      * solutions a list of dictionaries of values keyed by
        arbitrary handles and retrieved from the data lake.
            
    Returns: 
      * the value of the attribute, which is a list whose elements
        may be primitive objects or items
    '''
    value_set = set()
    for solution in solutions:
        value = solution[copier_attribute.unknown_name]     
        if isinstance(value, vdl.Itm): 
            value = ('I', value.itemid)
        elif isinstance(value, bytearray): 
            value = bytes(value)
        value_set.add(value)
    values_to_return = []
    for value in value_set:
        if isinstance(value, tuple): v = vdl.Itm(value[1])
        else: v = value
        __check_type__(v, copier_attribute.value_type)
        values_to_return.append(v)
    return values_to_return


def __get_multi_dict_solutions_by_itemid__(
        name, copier_attribute, solutions):
    '''
    Given a list of solutions retrieved from the virtual data
    lake, each of which includes an item representing a
    dictionary, create a mapping of lists of indexes of
    solutions that include the same dictionary items, keyed
    by the item identifiers. 
        
    Parameters:
      * name(str) the name of the attribute whose value is
        being retrieved
      * copier_attribute a `CopierAttribute` object for the
        attribute to be copied
      * solutions a list of dictionaries of values keyed by
        arbitrary handles and retrieved from the data lake.
        
    Returns:
      * a mapping of lists of solutions that include the same 
        dictionary items, keyed by the item  identifiers
    '''
    value_solutions_by_itemid = {}
    for solution in solutions:
        value = solution[copier_attribute.unknown_name]     
        if not isinstance(value, vdl.Itm): 
            raise VdlCopyException(
                    'Nested dict has non-item value: ' + name)
        value_solutions = value_solutions_by_itemid.get(
                value.itemid)
        if value_solutions is None: 
                value_solutions_by_itemid[value.itemid
                                          ] = [solution]
        else: value_solutions.append(solution)
    return value_solutions_by_itemid
            
            
def __check_type__(value, object_type):
    '''
    Check that the object type of a value is as specified for
    an attribute
    
    Parameters:
      * value an attribute value
      * object_type(str) an object_type of a `VdlCopyAttribute`
      
    Raises: 
      * `VdlCopyException` if the value object type is not as
        specified
    '''
    
    if object_type is None: return
    elif isinstance(object_type, Copier): 
        if isinstance(value, vdl.Itm): return 
    elif object_type == bytes or object_type == bytearray:
        if isinstance(value, (bytes, bytearray)): return
    elif isinstance(value, object_type): return
    raise VdlCopyException('Invalid object type: ' + (
            str(value) + ' not of type ' + str(object_type)))
    

def json_dumpable_dict_containing_items(dict_with_items):
    '''
    Create a copy of a dict that contains values that are vdl Itm
    objects in which those objects are replaced by strings giving
    the item identifiers. The method is applied recursively to any
    values that are dicts. The resulting dict can be processed by
    the json dumps method if the supplied dict contains no set or
    tuple values or values of types other than vdl.Itm that 
    json.dumps cannot handle.
    
    Parameters:
      * dict_with_items(`dict`)
      
    Returns:
      *  A copy of the supplied dict in which values that are vdl Itm
        objects are replaced by strings giving the item identifiers.
    '''
    
    jddict = dict_with_items.copy()
    for (name, value) in jddict.items():
        jdv = json_dumpable_value(value)
        jddict[name] = jdv
    return jddict
    
    
def json_dumpable_value(value):
    if isinstance(value, list): 
        return [json_dumpable_value(elt) for elt in value]
    elif isinstance(value, dict): 
        return json_dumpable_dict_containing_items(value)
    elif isinstance(value, vdl.Itm):   
        return 'ITEM ' + value.itemid
    else: return value
                              
        
class VdlCopyAttribute:
    '''
    An item of this type represents a dictionary attribute 
    in a virtual data lake copy operation.
    '''
    
    def __init__(
            self, verb_source, verb_name):
        '''
        Construct a VdlCopyAttribute object.
        
        Parameters:
          * verb_source(int) the numeric identifier of the virtual data 
            lake source containing the named item to be mapped to the 
            attribute
          * verb_name(str) the name of the named item
        '''
        
        self.verb_source = verb_source
        self.verb_name = verb_name


class VdlCopyException(RuntimeError):
    '''
    A run-time exception occurring during execution of a 
    virtual data lake copy operation.
    '''
    
    def __init__(self, *messages):
        super().__init__(*messages)
 

class Copier:
    '''
    An instance of this class supports an operation to copy
    a dictionary from a virtual data lake. For each directory 
    attribute to be copied, it has a copier_attribute 
    attribute whose value is a CopierAttribute object. If the
    attribute is a nested directory, the value_type of its
    copier_attribute is a nested Copier object.
    '''
    
    def __init__(self, copy_spec):   
        '''
        Construct a Copier object
            
        Parameters:
          * copy_spec(dict) a dict with an attribute for each 
            attribute of the dictionary to be copied, as for the
            copy-spec parameter of `copy_from_vdl`     
        '''
          
        self.copier_attributes_dict = {} 
        for (name, value_spec) in copy_spec.items():
            if isinstance(value_spec, list):
                if len(value_spec) != 1: raise VdlCopyException(
                    'Invalid attribute specification: ' + str(
                            value_spec))
                for value_type in value_spec: break
                if isinstance(value_type, list): raise VdlCopyException(
                    'Invalid attribute specification: ' + str(
                            value_spec))
                single_valued = False
            else:
                value_type = value_spec
                single_valued = True
            if isinstance(value_type, dict):
                value_type = Copier(value_type)
            self.copier_attributes_dict[name] = CopierAttribute(
                    value_type, single_valued)
            
            
    def __repr__(self):
        return str(self.copier_attributes_dict)
  
        
class CopierAttribute:
    '''
    The characteristics of an attribute that is to be copied.
    It contains the value type of the attribute, a flag
    saying whether the attribute is single-valued, and the
    name of the vdl Unknown used to retrieve the value of
    the attribute. This name is not present when the
    CopierAttribute object is created, but is added when the
    retrieval constraints are determined.
    '''
    
    def __init__(self, value_type, single_valued):
        '''
        Construct a CopierAttribute object
        
        Parameters:
          * value_type(dict) a dict with an attribute for each 
            attribute of the dictionary to be copied, as for the
            copy-spec parameter of `copy_from_vdl`
          * single_valued(bool) whether the attribute is 
            single-valued. 
        '''
        
        self.value_type = value_type
        self.single_valued = single_valued
        self.unknown_name = None
       
       
    def __repr__(self):
        return str(self.value_type) + ', ' + str(self.single_valued)  + ', ' + str(self.unknown_name) 
        return