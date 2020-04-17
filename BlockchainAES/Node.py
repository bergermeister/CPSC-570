from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
from Crypto.Cipher import AES
from Block import Block
from Chain import Chain
import requests
import json
import numpy as np
import os

web = Flask(__name__)           # Web Application Object
chain = Chain( )                # Blockchain Object
ID = ""                         # Unique Identifier of Node
host = ""
port = 0
network = [ ]                   # List of nodes in network
networkFile = "./Network.json"  # Location to store list of nodes in network
key = {
   "17074dd6-09e7-4f6e-a8bd-b3744d397807" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" ),
   "ceb627d5-7ae0-42e9-a9af-9fe76d0c0298" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" ),
   "d95da554-75f9-489e-aecb-09673803bb66" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" )
      }

def Run( IPAddress, Port ):  
    global ID
    global host
    global port
    
    # Generate new UUID
    ID = str( uuid4( ) )
    
    # Create the Endpoint
    host = IPAddress
    port = Port
    ep = { 'uuid' : ID, 'hostname' : IPAddress, 'port' : Port }
    
    # Check if the network file exists
    print( "Building Network List..." )
    if( os.path.isfile( networkFile ) and os.access( networkFile, os.R_OK ) ):
        # Read Network File
        with open( networkFile, 'r' ) as file:
            data = file.read( )
        
        # Parse Network File
        data = json.loads( data )

        # Search for current node in list of nodes
        found = False
        for node in data:
            print( node )
            if( ( node[ 'hostname' ] == IPAddress ) and ( node[ 'port' ] == Port ) ):
                # If node is found, update the UUID
                ID = node[ 'uuid' ]
                ep[ 'uuid' ] = ID
                found = True
                
            network.append( node )
                
        # If node is not found, add new node to the list
        if( found == False ):
            print( ep )
            network.append( ep )
        
    # If no network file exists, add this node as new node to the list
    else:
        print( ep )
        network.append( ep )
    
    # Update the network file
    with open( networkFile, 'w' ) as file:
        json.dump( network, file, sort_keys = True, indent = 4 )
        
    print( "Connecting to Nodes..." )
    for node in network:
        if( node[ 'uuid' ] != ID ):
            addr = 'http://' + node[ 'hostname' ] + ':' + str( node[ 'port' ] ) + '/connect_node'
            try:
                requests.post( addr, json=ep )
                print( f'Connected to {addr}' )
            except:
                print( f'Could not connect to {addr}' ) 
    
    # Run the Web Application
    web.run( host = IPAddress, port = Port )
        
# Mining a new block
@web.route('/mine_block', methods = [ 'GET' ] )
def mine_block( ):
    global host
    global port
    
    print( 'mine_block start' )
    block = chain.Mine( 4 )
    print( 'Block mined' )
    mined = True
    for node in network:
        if( ( node[ 'hostname' ] != host ) or 
            ( node[ 'port' ] != port ) ):
            addr = 'http://' + node[ 'hostname' ] + ':' + str( node[ 'port' ] ) + '/update_chain'
            print( f'Updating chain with {addr}' )
            try:
                response = requests.post( addr, json = chain.List( ) )
                if( ( response.status_code == 200 ) and 
                    ( response.json( )[ 'valid' ] != True ) ):
                    mined = False
            except:
                print( f'Could not connect to {addr}' )
                
    if( mined == True ):   
        response = { 'message': 'Block mined successfully',       
                     'block' : block.Jsonify( ) }
    else:
        response = { 'message': 'Block mining failed' }
        
    print( 'mine_block end' )
    
    return( jsonify( response ), 200 )

@web.route('/update_chain', methods = [ 'POST' ] )
def update_chain( ):
    print( 'update_chain start' )
    data = request.get_json( )
    print( f'Received data: {data}' )
    newChain = Chain( )
    newChain.block = [ ]
    for entry in data:
        print( f'Processing entry: {entry}' )
        index = entry[ 'index' ]
        nonce = entry[ 'nonce' ]
        target = entry[ 'target' ]
        data = entry[ 'data' ]
        hashPrev = entry[ 'hashPrev' ]
        timestamp = entry[ 'timestamp' ]
        newBlock = Block( index, nonce, target, data, hashPrev, timestamp )
        newChain.block.append( newBlock )
    print( f'Received Chain: {newChain}' )
    updated = chain.Update( newChain )
    if( updated ):
        response = { 'message': 'Chain updated', 'chain': chain.List( ) }
        code = 200
    else:
        response = { 'message': 'Chain not updated', 'chain': chain.List( ) }
        code = 400
    
    print( 'update_chain end' )
    return( jsonify( response ), code )
    
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

@web.route( '/add_encrypted_transaction', methods = ['POST'] )
def add_encrypted_transaction():
    json = request.get_json()
    transactionKeys = [ 'sender', 'receiver', 'data' ]
    if not all(key in json for key in transactionKeys):
        return 'Some elements of the transaction are missing', 400
    sender = json[ 'sender' ]
    receiver = json[ 'receiver' ]
    data = json[ 'data' ]
    if( ( sender == ID ) and ( receiver in key ) ):
        dataLen = len( data )
        pad = ( 16 - ( dataLen % 16 ) ) % 16
        data = data.ljust( dataLen + pad, '~' )
        cipher = AES.new( key[ receiver ] )
        ciphertext = cipher.encrypt( data )
        json[ 'data' ] = "AES-" + ciphertext.hex( )
        index = chain.AddTransaction(json['sender'], json['receiver'], json['data'])
        response = {'message': f'This transaction will be added to Block {index}',
                    'transaction' : json }
        code = 201
    else:
        response = { 'message' : 'Failed to add transaction to pool' }
        code = 400
    return( jsonify( response ), code ) 

@web.route( '/get_transactions', methods = ['GET'] )
def get_transactions( ):
    data = [ ]
    for block in chain.block:
        for transaction in block.data:
            if( ( transaction[ 'sender' ] == ID ) or ( transaction[ 'receiver' ] == ID ) ):
                data.append( transaction )

    response = { 'message' : f'Transactions for {ID}',
                 'transactions' : data }
    return( jsonify( response ), 200 )

@web.route( '/get_decrypted_transactions', methods = ['GET'] )
def get_decrypted_transactions( ):
    data = [ ]
    for block in chain.block:
        for transaction in block.data:
            sender = transaction[ 'sender' ]
            receiver = transaction[ 'receiver' ]
            if( transaction[ 'sender' ] == ID ):
                data.append( transaction.copy( ) )   
                if( transaction[ 'data' ].startswith( "AES-" ) ):
                    cipher = AES.new( key[ receiver ] )
                    plaintext = cipher.decrypt( bytes.fromhex( transaction[ 'data' ][ 4: ] ) )
                    data[ - 1 ][ 'data' ] = plaintext.decode( )
            elif( transaction[ 'receiver' ] == ID ):
                data.append( transaction )
                if( transaction[ 'data' ].startswith( "AES-" ) ):
                    cipher = AES.new( key[ sender ] )
                    plaintext = cipher.decrypt( bytes.fromhex( transaction[ 'data' ][ 4: ] ) )
                    data[ - 1 ][ 'data' ] = plaintext.decode( )
                    

    response = { 'message' : f'Decrypted Transactions for {ID}',
                 'transactions' : data }
    return( jsonify( response ), 200 )

# Connecting new nodes
@web.route('/connect_node', methods = ['POST'])
def connect_node():
    ep = request.get_json()
    print( f"Received Node: {ep}" )
    found = False
    print( "Nodes in Network:" )
    for node in network:
        print( node )
        if( ( node[ 'hostname' ] == ep[ 'hostname' ] ) and 
            ( node[ 'port' ] == ep['port' ] ) ):
            # If node is found, update the UUID
            node[ 'uuid' ] = ep[ 'uuid' ]
            found = True
                
    # If node is not found, add new node to the list
    if( found == False ):
        network.append( ep )
        
    # Update the network file
    with open( networkFile, 'w' ) as file:
        json.dump( network, file, sort_keys = True, indent = 4 )

    response = network
    return jsonify(response), 201
