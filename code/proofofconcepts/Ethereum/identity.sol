pragma solidity ^0.4.0;

contract Identity {

    address public owner;
    uint public counter;
    mapping(uint => string) claims;


    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    constructor() public {
        owner = msg.sender;
    }

    function create(string data) public {
        counter++;
        claims[counter - 1] = data;
    }

    function retrieve(uint idx) public constant returns (string) {
        require(idx >= 0 && idx < counter);
        return claims[idx];
    }

    function update(uint idx, string data) public onlyOwner {
        require(idx >= 0 && idx < counter);
        claims[idx] = data;
    }

    function remove(uint idx) public onlyOwner {
        require(idx >= 0 && idx < counter);
        delete claims[idx];
    }
}
