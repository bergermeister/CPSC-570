from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
import requests
from Chain import Chain
import numpy as np

# Create a Web App
web = Flask(__name__)

# Create a Blockchain        
chain = Chain( )

def Run( IPAddress, Port ):
    # Run the Web App
    web.run( host = IPAddress, port = Port )
        
# Mining a new block
@web.route('/mine_block', methods = [ 'GET' ] )
def mine_block( ):
    block = chain.Mine( 4 )
    response = { 'message': 'Congratulations, you just mined a block!',       
                 'index': block.index,
                 'timestamp': block.timestamp,
                 'nonce': block.nonce,
                 'target': block.target,
                 'data': block.data,
                 'hashPrev': block.hashPrev,
                 'hashThis': block.hashThis }
    return( jsonify( response ), 200 )
    
# Get the full Blockchain
@web.route('/get_chain', methods = [ 'GET' ] )
def get_chain( ):
    response = { 'chain': chain.List( ),
                 'Length': len( chain.block ) }
    return( jsonify( response ), 200 )

# Check if blockhain is valid
@web.route('/is_valid', methods = [ 'GET' ] )
def is_valid( ):
    is_valid = chain.IsValid( )
    if( is_valid ):
        response = { 'message' : 'The Blockchain is valid.' }
    else:
        response = { 'message' : 'The Blocklchain is NOT valid.' }
    return( jsonify( response ), 200 )

# Adding a new transaction to the Blockchain
@web.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transactionKeys = [ 'sender', 'receiver', 'data' ]
    if not all(key in json for key in transactionKeys):
        return 'Some elements of the transaction are missing', 400
    index = chain.AddTransaction(json['sender'], json['receiver'], json['data'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201
