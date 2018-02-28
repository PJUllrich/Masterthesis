from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Storage import Delete, Get, GetContext, Put
from boa.code.builtins import sha256

from proofofconcepts.NEO.util.serialize import *

OWNER = 'OWNER'
NAME = 'NAME'
AGE = 'AGE'


def create(data):
    identity = list(length=3)
    identity[0] = data[0]
    identity[1] = data[1]
    identity[2] = data[2]

    data_serialized = serialize_array(identity)
    ctx = GetContext()
    Put(ctx, OWNER, data_serialized)

    return True


def retrieve():
    ctx = GetContext()
    contract = Get(ctx, OWNER)

    return contract


def update(data):
    return create(data)


def delete():
    ctx = GetContext()
    Delete(ctx, OWNER)

    return True


def verify(data):
    ctx = GetContext()
    saved_bytes = Get(ctx, OWNER)
    saved = deserialize_bytearray(saved_bytes)

    input = sha256(data)
    check = sha256(saved)

    return input == check


def is_owner():
    ctx = GetContext()
    contract = Get(ctx, OWNER)

    # Identity is not created yet.
    if contract is None:
        print('Identity not created yet. Allowing creation for now.')
        return True

    owner = contract[0]
    is_owner = CheckWitness(owner)
    return is_owner


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
        return retrieve()

    if operation == "Update":
        return update(data)

    if operation == "Delete":
        return delete()

    return False
