from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from model.Nodes import Nodes
from model.Transaction import Transaction
from model.Blockchain import Blockchain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.post('/transactions/new')
async def new_transaction(transaction: Transaction):
    index = blockchain.new_transaction(transaction.angler, transaction.fishery, transaction.fish, transaction.weight)
    return {'message': f'Transaction will be added to Block {index}'}


@app.get('/mine')
async def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        angler="0",
        fishery=node_identifier,
        fish="karas",
        weight=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    return block


@app.get('/chain')
async def chain():
    return blockchain.chain


@app.post('/nodes/register')
async def register_nodes(nodes: Nodes):
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes.nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return response


@app.get('/nodes/resolve')
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return response
