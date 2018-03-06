package src

import (
	"fmt"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	peer "github.com/hyperledger/fabric/protos/peer"
)

type Document struct {
}

// Init is called during chaincode instantiation to initialize any
// data. Note that chaincode upgrade also calls this function to reset
// or to migrate data, so be careful to avoid a scenario where you
// inadvertently clobber your ledger's data!
func (t *Document) Init(stub shim.ChaincodeStubInterface) peer.Response {
	// Get the args from the transaction proposal
	args := stub.GetStringArgs()
	if len(args) != 2 {
		return shim.Error("Incorrect arguments. Expecting a key and a value")
	}

	// Set up any variables or assets here by calling stub.PutState()

	// We store the key and the value on the ledger
	err := stub.PutState(args[0], []byte(args[1]))
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to create asset: %s", args[0]))
	}
	return shim.Success(nil)
}

// Invoke is called per transaction on the chaincode. Each transaction is
// either a 'get' or a 'set' on the asset created by Init function. The 'set'
// method may create a new asset by specifying a new key-value pair.
func (t *Document) Invoke(stub shim.ChaincodeStubInterface) peer.Response {
	fn, args := stub.GetFunctionAndParameters()

	var result string
	var err error
	if fn == "Verify" {
		result, err = t.verify(stub, args)
	} else if fn == "Create" {
		result, err = t.create(stub, args)
	} else if fn == "Retrieve" {
		result, err = t.retrieve(stub, args)
	} else if fn == "Update" {
		result, err = t.update(stub, args)
	} else if fn == "Delete" {
		result, err = t.delete(stub, args)
	}
	if err != nil {
		return shim.Error(err.Error())
	}

	// Return the result as success payload
	return shim.Success([]byte(result))
}

func (t *Document) verify(stub shim.ChaincodeStubInterface, args []string) (string, error) {
	if len(args) != 2 {
		return "", fmt.Errorf("incorrect arguments. expected 2. received %d", len(args))
	}

	val, err := stub.GetState(args[0])
	if err != nil {
		return "", fmt.Errorf("error occurred while retrieving entry for %s : %s", args[0], err)
	}

	var res string
	if string(val) == args[1] {
		res = "True"
	} else {
		res = "False"
	}

	return res, nil
}

func (t *Document) create(stub shim.ChaincodeStubInterface, args []string) (string, error) {
	if len(args) != 2 {
		return "", fmt.Errorf("incorrect arguments. expected 2. received %d", len(args))
	}

	val, errGet := stub.GetState(args[0])
	if errGet != nil {
		return "", fmt.Errorf("error occurred while retrieving value for %s : %s", args[0], errGet)
	}
	if val != nil {
		return "", fmt.Errorf("entry for %s exists already", args[0])
	}

	errPut := stub.PutState(args[0], []byte(args[1]))
	if errPut != nil {
		return "", fmt.Errorf("failed to set asset: %s", args[0])
	}

	return args[1], nil
}

func (t *Document) retrieve(stub shim.ChaincodeStubInterface, args []string) (string, error) {
	if len(args) != 1 {
		return "", fmt.Errorf("incorrect arguments. expected 1. received %d", len(args))
	}

	val, err := stub.GetState(args[0])
	if err != nil {
		return "", fmt.Errorf("error occurred while retrieving entry for %s : %s", args[0], err)
	}
	if val == nil {
		return "", fmt.Errorf("entry for %s not found", args[0])
	}

	return string(val), nil
}

func (t *Document) update(stub shim.ChaincodeStubInterface, args []string) (string, error) {
	if len(args) != 2 {
		return "", fmt.Errorf("incorrect arguments. expected 2. received %d", len(args))
	}

	val, err1 := stub.GetState(args[0])
	if err1 != nil {
		return "", fmt.Errorf("error occurred while retrieving entry for %s : %s", args[0], err2)
	}
	if val == nil {
		return "", fmt.Errorf("no entry for %s was found. not updating", args[0])
	}

	err2 := stub.PutState(args[0], []byte(args[1]))
	if err2 != nil {
		return "", fmt.Errorf("error occurred while updating entry for %s : %s", args[0], err2)
	}

	return args[1], nil
}

func (t *Document) delete(stub shim.ChaincodeStubInterface, args []string) (string, error) {
	if len(args) != 1 {
		return "", fmt.Errorf("incorrect arguments. expected 1. received %d", len(args))
	}

	err := stub.DelState(args[0])
	if err != nil {
		return "", fmt.Errorf("error occurred while deleting entry for %s : %s", args[0], err)
	}

	return args[0], nil
}
