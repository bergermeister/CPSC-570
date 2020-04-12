from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
from Block import Block
from Chain import Chain
import requests
import json
import numpy as np
import os

web = Flask(__name__)   # Web Application Object
chain = Chain( )        # Blockchain Object
id = ""                 # Unique Identifier of Node
network = [ ]           # List of nodes in network
networkFile = "./Network.json"


def Run( IPAddress, Port ):  
    # Generate new UUID
    id = str( uuid4( ) )
    
    # Initialize Network list to empty
    network = [ ]
    
    # Check if the network file exists
    if( os.path.isfile( networkFile ) and os.access( networkFile, os.R_OK ) ):
        
        # Read Network File
        with open( networkFile, 'r' ) as file:
            data = file.read( )
        
        # Parse Network File
        network = json.loads( data )

        # Search for current node in list of nodes
        found = False
        print( "Read in Nodes:" )
        for node in network:
            print( node )
            if( ( node[ 'hostname' ] == IPAddress ) and 
                ( node[ 'port' ] == Port ) ):
                # If node is found, update the UUID
                node[ 'uuid' ] = id
                found = True
                
        # If node is not found, add new node to the list
        if( found == False ):
            network.append( { 'uuid' : id, 'hostname' : IPAddress, 'port' : Port } )
        
    # If no network file exists, add this node as new node to the list
    else:
        network.append( { 'uuid' : id, 'hostname' : IPAddress, 'port' : Port } )
    
    # Update the network file
    with open( networkFile, 'w' ) as file:
        json.dump( network, file, sort_keys = True, indent = 4 )
    
    print( "Nodes after startup" )
    for key in network:
            print( key )
    
    # Run the Web Application
    web.run( host = IPAddress, port = Port )
        
# Mining a new block
@web.route('/mine_block', methods = [ 'GET' ] )
def mine_block( ):
    block = chain.Mine( 4 )
    mined = True
    for node in network:
        if( node[ 'uuid' ] != id ):
            response = requests.post( node[ 'hostname' ] + ':' + 
                                      node[ 'port' ] +
                                      'verify_block',
                                      block.Jsonify( ) )
            if( ( response.status_code == 200 ) and 
                ( response.json( )[ 'valid' ] != True ) ):
                mined = False
    if( mined == True ):   
        for node in network:
            if( node[ 'uuid' ] != id ):
                response = requests.post( node[ 'hostname' ] + ':' + 
                                          node[ 'port' ] +
                                          'add_block',
                                          block.Jsonify( ) )
                if( ( response.status_code == 200 ) and 
                    ( response.json( )[ 'valid' ] != True ) ):
                    mined = False
        response = { 'message': 'Block mined successfully',       
                     'block' : block.Jsonify( ) }
    else:
        response = { 'message': 'Block mining failed' }
        
    return( jsonify( response ), 200 )
    
@web.route('/verify_block', methods = [ 'POST' ] )
def verify_block( ):
    blockJson = request.get_json( )
    blockThis = Block( blockJson[ 'index' ], 
                       blockJson[ 'nonce' ], 
                       blockJson[ 'target' ], 
                       blockJson[ 'data' ], 
                       blockJson[ 'hashPrev'],
                       blockJson[ 'Timestamp' ] )
    
    if( chain.IsBlockValid( blockThis ) ):
        response = { 'message': 'Block is valid', 'valid': True }
    
    return( jsonify( response ), 200 )

@web.route('/add_block', methods = [ 'POST' ] )
def add_block( ):
    blockJson = request.get_json( )
    blockThis = Block( blockJson[ 'index' ], 
                       blockJson[ 'nonce' ], 
                       blockJson[ 'target' ], 
                       blockJson[ 'data' ], 
                       blockJson[ 'hashPrev'],
                       blockJson[ 'Timestamp' ] )
    chain.block.append( blockThis )
    response = { 'message': 'Block added', 'block': blockJson }
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
    response = {'message': 'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# Connecting new nodes
@web.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    #for node in nodes:
    #    blockchain.add_node(node)
    #response = {'message': 'All the nodes are now connected. The UBcoin Blockchain now contains the following nodes:',
    #            'total_nodes': list(blockchain.nodes)}
    response = {}
    return jsonify(response), 201
