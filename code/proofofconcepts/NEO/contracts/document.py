from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Storage import Delete, Get, GetContext, Put

from contracts.util.serialize import *

IDX_KEY = 0

IDX_ADDRESS = 0
IDX_HASH = 1

OWNER = b'S\xefB\xc8\xdf!^\xbeZ|z\xe8\x01\xcb\xc3\xac/\xacI)'

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
    saved_serialized = Get(ctx, data[IDX_KEY])
    saved_deserialized = deserialize_bytearray(saved_serialized)

    saved = saved_deserialized[IDX_HASH]
    check = data[IDX_HASH]

    return saved == check


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
    if not CheckWitness(OWNER):
        print('You are not the owner of this Contract!')
        return False

    if operation == "Create":
        return create(data)

    if operation == "Retrieve":
        return retrieve(data)

    if operation == "Update":
        return update(data)

    if operation == "Delete":
        return delete(data)

    print('Operation does not exist')
    return False
