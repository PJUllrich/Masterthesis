from boa.builtins import sha256, list
from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Storage import Delete, Get, GetContext, Put

from contracts.util.serialize import *

IDX_KEY = 0

IDX_ADDRESS = 0
IDX_HASH = 1

ctx = GetContext()


def serialize_data(data):
    document = list(length=2)
    document[IDX_ADDRESS] = data[IDX_ADDRESS]
    document[IDX_HASH] = data[IDX_HASH]

    return serialize_array(document)


def create(data):
    """

    Parameters
    ----------
    data : boa.builtins.list
        The input data containing an address and a hash, both in bytes

    Returns
    -------
    bool
        Returns False if the entry does exist already, otherwise True
    """

    if Get(ctx, data[IDX_KEY]):
        print('Error: Entry already exists!')
        return False

    data_serialized = serialize_data(data)
    Put(ctx, data[IDX_KEY], data_serialized)
    return True


def retrieve(data):
    saved = Get(ctx, data[IDX_KEY])
    return deserialize_bytearray(saved)


def update(data):
    if Get(ctx, data[IDX_KEY]) is None:
        print('Error: Entry does not exist!')
        return False

    data_serialized = serialize_data(data)
    Put(ctx, data[IDX_KEY], data_serialized)
    return True


def delete(data):
    if not Get(ctx, data[IDX_KEY]):
        print('Error: Entry does not exist!')
        return False

    Delete(ctx, data[IDX_KEY])
    return True


def verify(data):
    saved_bytes = Get(ctx, data[IDX_KEY])

    if saved_bytes is None:
        print('Error: Entry is not created yet.')
        return False

    saved = deserialize_bytearray(saved_bytes)

    input = sha256(data)
    check = sha256(saved)

    return input == check


def is_owner(key):
    contract = Get(ctx, key)

    # Entry is not created yet.
    if contract is None:
        print('Info: Entry not created yet. Allowing creation for now.')
        return True

    owner = contract[IDX_KEY]
    return CheckWitness(owner)


def Main(operation, data):
    """

    Parameters
    ----------
    operation : str
        The operation to execute with the contract call
    data : boa.builtins.list
        A list containing an address and a hash.
        Address: Of the student to whom the document belongs
        Hash: The hash of the document belonging the the student

    Returns
    -------
    bool
        Returns a result of an operation as a boolean
    ByteArray
        Returns a ByteArray of ByteArrays when data is retrieved
    """

    if operation == "Verify":
        return verify(data)

    # Only the Owner can execute methods hereafter
    # if not is_owner(data[0]):
    #     print('You are not the owner of this Identity!')
    #     return False

    if operation == "Create":
        return create(data)

    if operation == "Retrieve":
        return retrieve(data)

    if operation == "Update":
        return update(data)

    if operation == "Delete":
        return delete(data)

    return False
