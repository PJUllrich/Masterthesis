import os
import shutil

from boa.compiler import Compiler

from neo.Prompt.Commands.BuildNRun import TestBuild
from neo.Settings import settings
from tests.test_base import BoaFixtureTest

settings.USE_DEBUG_STORAGE = True
settings.DEBUG_STORAGE_PATH = './fixtures/debugstorage'

LENGTH_ADDRESS = 16
LENGTH_HASH = 32


class TestContract(BoaFixtureTest):
    contract = None
    data = None

    class ContractData:
        operation = None
        student_address = None
        document_hash = None

        def __init__(self, student_address, document_hash):
            self.student_address = student_address
            self.document_hash = document_hash

        def to_array(self):
            return [self.operation, [self.student_address, self.document_hash]]

    def setUp(self):
        self.dropDebugStorage()

        contract_schema = Compiler.instance().load('%s/NEO/contracts/document.py' % TestContract.dirname).default
        self.contract = contract_schema.write()

        random_address = bytearray(os.urandom(LENGTH_ADDRESS))
        random_hash = bytearray(os.urandom(LENGTH_ADDRESS))

        self.data = self.ContractData(random_address, random_hash)

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

    def test_when_caller_is_not_owner_should_return_false(self):
        self.data.operation = 'Test'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet2(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(b'', results[0].GetByteArray())  # Asserts to False in Bytes

    def test_when_operation_not_implemented_should_return_false(self):
        self.data.operation = 'OperationDoesNotExist'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(b'', results[0].GetByteArray())  # Asserts to False in Bytes

    def test_when_create_new_should_return_true(self):
        self.data.operation = 'Create'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(b'\x01', results[0].GetByteArray())  # Asserts to True in Bytes

    def test_when_create_existing_should_return_false(self):
        self.data.operation = 'Create'

        tx, results1, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')
        tx, results2, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results2))
        self.assertEqual(b'', results2[0].GetByteArray())

    def test_when_retrieve_should_return_created_contract_data(self):
        # First, make sure that something was stored in Storage
        self.create_entry()

        # Perform Retrieve operation
        self.data.operation = 'Retrieve'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        # Check that the retrieved data is equal to the initially saved data
        self.assert_result_equal_to_data(results)

    def test_when_update_should_return_true(self):
        self.create_entry()

        self.data.operation = 'Update'

        # Change the age field to a random new number
        original_value = self.data.document_hash
        while self.data.document_hash == original_value:
            self.data.document_hash = bytearray(os.urandom(LENGTH_HASH))

        # Perform the update and check that the Contract returns True
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')
        self.assertEqual(1, len(results))
        self.assertEqual(True, results[0].GetBigInteger())

    def test_when_delete_existing_should_return_true(self):
        self.create_entry()

        self.data.operation = 'Delete'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(True, results[0].GetBigInteger())

    def test_when_delete_non_existing_should_return_false(self):
        self.data.operation = 'Delete'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(False, results[0].GetBigInteger())

    def test_when_verify_with_equal_hash_should_return_true(self):
        self.create_entry()

        self.data.operation = 'Verify'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(True, results[0].GetBigInteger())

    def test_when_verify_with_different_hash_should_return_false(self):
        self.create_entry()

        self.data.operation = 'Verify'
        self.data.document_hash = bytearray(os.urandom(LENGTH_HASH))
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')

        self.assertEqual(1, len(results))
        self.assertEqual(False, results[0].GetBigInteger())

    def assert_result_equal_to_data(self, results):
        self.assertEqual(1, len(results))
        self.assertEqual(len(self.data.to_array()[1]), len(results[0].GetArray()))

        data_to_check = results[0].GetArray()
        self.assertEqual(self.data.student_address, data_to_check[0].GetByteArray())
        self.assertEqual(self.data.document_hash, data_to_check[1].GetByteArray())

    def create_entry(self):
        self.data.operation = 'Create'
        tx, results, total_ops, engine = TestBuild(self.contract, self.data.to_array(), self.GetWallet1(), '0710', '05')
