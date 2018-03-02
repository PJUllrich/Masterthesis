import os
import random
import shutil

from boa.compiler import Compiler

from neo.Prompt.Commands.BuildNRun import TestBuild
from neo.Settings import settings
from tests.test_base import BoaFixtureTest

settings.USE_DEBUG_STORAGE = True
settings.DEBUG_STORAGE_PATH = './fixtures/debugstorage'


class TestContract(BoaFixtureTest):
    contract = None
    data = None

    class ContractData:
        operation = None
        owner = None
        name = None
        age = None

        def __init__(self, owner, name, age):
            self.owner = owner
            self.name = name
            self.age = age

        def to_array(self):
            return [self.operation, [self.owner, self.name, str(self.age)]]

        def equal_to_bytearray(self, data_to_check):
            return (data_to_check[0].GetString() == self.owner
                    and data_to_check[1].GetString() == self.name
                    and data_to_check[2].GetBigInteger() == self.age)

    def setUp(self):
        self.dropDebugStorage()

        contract_schema = Compiler.instance().load('%s/NEO/contracts/identity.py' % TestContract.dirname).default
        self.contract = contract_schema.write()

        self.data = self.ContractData(self.faker.name(), self.faker.name(), random.randint(1, 100))

    @classmethod
    def tearDownClass(cls):
        super(BoaFixtureTest, cls).tearDownClass()

        cls.dropDebugStorage()

    @classmethod
    def dropDebugStorage(cls):
        try:
            if os.path.exists(settings.DEBUG_STORAGE_PATH):
                shutil.rmtree(settings.DEBUG_STORAGE_PATH)
        except Exception as e:
            print("couldn't remove debug storage %s " % e)

    def test_create(self):
        self.data.operation = 'Create'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].GetByteArray(), b'\x01')  # Asserts to True in Bytes

    def test_retrieve(self):
        self.test_create()

        self.data.operation = 'Retrieve'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0].GetArray()), len(self.data.to_array()[1]))
        self.assertTrue(self.data.equal_to_bytearray(results[0].GetArray()))

    def test_update(self):
        pass

    def test_delete(self):
        pass

    def test_verify(self):
        pass
