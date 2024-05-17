import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests


class Blockchain(object):
    """
        A basic implementation of a blockchain.

        Attributes:
            chain (list): A list of blocks comprising the blockchain.
            pending_transactions (list): A list of transactions yet to be added to a block.
            nodes (set): A set of network nodes running the blockchain.

        Methods:
            __init__(): Initializes the blockchain with a genesis block.
            valid_chain(chain): Validates whether a given blockchain is valid.
            resolve_conflicts(): Resolves conflicts by replacing the chain with the longest valid one in the network.
            register_node(address): Registers a new node in the network.
            proof_of_work(last_proof): Finds the proof of work for a new block.
            valid_proof(last_proof, proof): Validates the proof of work.
            new_block(proof, previous_hash=None): Creates a new block in the blockchain.
            new_transaction(angler, fishery, fish, weight): Adds a new transaction to the pending transactions list.
            hash(block): Generates the SHA-256 hash of a block.
            last_block: Returns the last block in the blockchain.
    """

    def __init__(self):
        """
           Initializes the blockchain with a genesis block.
        """
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()
        self.new_block(previous_hash="rybka", proof=100)

    def valid_chain(self, chain):
        """
            Validates whether a given blockchain is valid.

            Args:
                chain (list): The blockchain to be validated.

            Returns:
                bool: True if the chain is valid, False otherwise.
        """
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
            Resolves conflicts by replacing the chain with the longest valid one in the network.

            Returns:
                bool: True if the chain was replaced, False otherwise.
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = len(response.json())
                chain = response.json()

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def register_node(self, address):
        """
            Resolves conflicts by replacing the chain with the longest valid one in the network.

            Returns:
                bool: True if the chain was replaced, False otherwise.
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def proof_of_work(self, last_proof):
        """
            Finds the proof of work for a new block.

            Args:
                last_proof (int): The proof of work of the previous block.

            Returns:
                int: The proof of work for the new block.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
            Validates the proof of work.

            Args:
                last_proof (int): The proof of work of the previous block.
                proof (int): The proof of work to be validated.

            Returns:
                bool: True if the proof is valid, False otherwise.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def new_block(self, proof, previous_hash=None):
        """
            Creates a new block in the blockchain.

            Args:
                proof (int): The proof of work for the new block.
                previous_hash (str, optional): The hash of the previous block. Defaults to None.

            Returns:
                    dict: The newly created block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        """
                Returns the last block in the blockchain.

                Returns:
                    dict: The last block in the blockchain.
                """
        return self.chain[-1]

    def new_transaction(self, angler, fishery, fish, weight):
        """
            Adds a new transaction to the pending transactions list.

            Args:
                angler (str): The angler's name.
                fishery (str): The fishery's name.
                fish (str): The type of fish caught.
                weight (float): The weight of the fish caught.

            Returns:
                int: The index of the block that will hold this transaction.
        """
        self.pending_transactions.append({
            'angler': angler,
            'fishery': fishery,
            'fish': fish,
            'amount': weight,
        })
        return self.last_block['index'] + 1

    def hash(self, block):
        """
            Generates the SHA-256 hash of a block.

            Args:
                block (dict): The block to be hashed.

            Returns:
                str: The SHA-256 hash of the block.
        """
        string_object = json.dumps(block, sort_keys=True).encode()
        hex_hash = hashlib.sha256(string_object).hexdigest()

        return hex_hash
