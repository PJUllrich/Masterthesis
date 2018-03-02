from boa.builtins import list, sha256
from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Storage import Delete, Get, GetContext, Put

from contracts.util.serialize import *

OWNER = 'OWNER'
NAME = 'NAME'
AGE = 'AGE'

ctx = GetContext()


def create(data):
    identity = list(length=3)
    identity[0] = data[0]
    identity[1] = data[1]
    identity[2] = data[2]

    data_serialized = serialize_array(identity)
    Put(ctx, data[0], data_serialized)

    return True


def retrieve(data):
    saved = Get(ctx, data[0])
    return deserialize_bytearray(saved)


def update(data):
    return create(data)


def delete(data):
    Delete(ctx, data[0])

    return True


def verify(data):
    saved_bytes = Get(ctx, OWNER)

    if saved_bytes is None:
        print('Identity is not created yet.')
        return False

    saved = deserialize_bytearray(saved_bytes)

    input = sha256(data)
    check = sha256(saved)

    return input == check


def is_owner():
    contract = Get(ctx, OWNER)

    # Identity is not created yet.
    if contract is None:
        print('Identity not created yet. Allowing creation for now.')
        return True

    owner = contract[0]
    return CheckWitness(owner)


def Main(operation, data):
    if operation == "Verify":
        return verify(data)

    # Only the Owner can execute methods hereafter
    if not is_owner():
        print('You are not the owner of this Identity!')
        return False

    if operation == "Create":
        return create(data)

    if operation == "Retrieve":
        return retrieve(data)

    if operation == "Update":
        return update(data)

    if operation == "Delete":
        return delete(data)

    return False
