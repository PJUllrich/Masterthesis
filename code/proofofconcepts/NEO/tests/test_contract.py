from boa.compiler import Compiler

from tests.test_base import BoaFixtureTest


class TestContract(BoaFixtureTest):
    contract = None

    def setUp(self):
        self.contract = Compiler.instance().load('%s/NEO/contracts/identity.py' % TestContract.dirname).default

    def test_create(self):
        pass