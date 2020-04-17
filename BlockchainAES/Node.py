from flask import Flask, jsonify, request
from uuid import uuid4
from Crypto.Cipher import AES
from hashlib import sha256 as sha256
from Block import Block
from Chain import Chain
import requests
import json
import os

web = Flask(__name__)           # Web Application Object
chain = Chain( )                # Blockchain Object
ID = ""                         # Unique Identifier of Node
host = ""                       # Hostname/IP Address
port = 0                        # Port Number
network = [ ]                   # List of nodes in network
networkFile = "./Network.json"  # Location to store list of nodes in network
secret = 0
shared = { }                    # Dictionary of Node:Shared Secret pairs
key = { }                       # Dictionary of Node:Key pairs
#   "17074dd6-09e7-4f6e-a8bd-b3744d397807" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" ),
#   "ceb627d5-7ae0-42e9-a9af-9fe76d0c0298" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" ),
#   "d95da554-75f9-489e-aecb-09673803bb66" : bytes.fromhex( "000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F" )
#      }

def Run( IPAddress, Port, Secret ):  
    global ID
    global host
    global port
    global secret
    
    # Generate new UUID
    ID = str( uuid4( ) )
    
    # Create the Endpoint
    host = IPAddress
    port = Port
    ep = { 'uuid' : ID, 'hostname' : IPAddress, 'port' : Port }
    
    # Record secret
    secret = Secret
    
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
       
def ProcessDHBlock( Block ):
    try:
        # For each transaction in the block
        for transaction in Block.data:
            # Read the Sender and Receiver 
            sender = transaction[ 'sender' ]
            receiver = transaction[ 'receiver' ]
            
            # Split the Data
            parts = transaction[ 'data' ].split( ';' )
            
            print( f'Processing transaction: {transaction}' )
            
            # If this node is the receiver and this is a Diffie-Hellman Key Exchange
            if( ( receiver == ID ) and ( len( parts ) == 3 ) ):
                p = int( parts[ 0 ].split( '=' )[ 1 ] )
                g = int( parts[ 1 ].split( '=' )[ 1 ] )
                A = int( parts[ 2 ].split( '=' )[ 1 ] )
                B = ( g ** secret ) % p
                s = ( A ** secret ) % p
                print( f'Processed: p={p};g={g};A={A};B={B};s={s}')
                if( sender not in shared ):
                   shared[ sender ] = s
                   key[ sender ] = bytes.fromhex( sha256( str( s ).encode( ) ).hexdigest( ) )
                   print( f'New Shared Secret = {sender}:{key[ sender ]}') 
                   if( parts[ 2 ].startswith( 'A' ) ):
                       chain.AddTransaction( ID, sender, f'p={p};g={g};B={B}')                
    except:
        print( "ERROR: Failed to parse transactions" )
    
# Mining a new block
@web.route('/mine_block', methods = [ 'GET' ] )
def mine_block( ):
    global ID
    
    # Mine a new block
    block = chain.Mine( 4 )
    
    # Check for Diffie-Hellman Blocks
    ProcessDHBlock( block )
        
    print( 'Block mined' )
    for node in network:
        if( node[ 'uuid' ] != ID ):
            addr = 'http://' + node[ 'hostname' ] + ':' + str( node[ 'port' ] ) + '/update_chain'
            print( f'Updating chain with {addr}' )
            try:
                response = requests.post( addr, json = chain.List( ) )
            except:
                print( f'Could not connect to {addr}' )
                
    response = { 'message': 'Block mined successfully',       
                 'block' : block.Jsonify( ) }
    
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
        # Check for Diffie-Hellman Blocks
        for block in chain.block:
            ProcessDHBlock( block )
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

@web.route('/add_dh_transaction', methods = ['POST'])
def add_dh_transaction():
    json = request.get_json()
    transactionKeys = [ 'p', 'g', 'receiver' ]
    if not all(key in json for key in transactionKeys):
        return 'Some elements of the transaction are missing', 
    p = json[ 'p' ]
    g = json[ 'g' ]
    A = ( g ** secret ) % p
    chain.AddTransaction( ID, json[ 'receiver' ], f'p={p};g={g};A={A}' )
    transaction = { 'sender' : ID, 'receiver' : json[ 'receiver' ],
                    'data' : f'p={p};g={g};A={A}' }
    response = { 'message' : 'Transaction created',
                 'transaction' : transaction }
    return( jsonify( response ), 201 )

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

@web.route( '/get_pending_transactions', methods = ['GET'] )
def get_pending_transactions( ):
    response = { 'message' : f'Pending Transactions in {ID}',
                 'transactions' : chain.transactions }
    return( jsonify( response ), 200 )

@web.route( '/get_transactions', methods = ['GET'] )
def get_transactions( ):
    # Creat an empty list of transactions
    transactions = [ ]
    
    # For each block in the blockchain
    for block in chain.block:
        # For each transaction in the block
        for transaction in block.data:
            # Append the transaction to the list of total transactions
            transactions.append( transaction.copy( ) ) 

    response = { 'message' : f'Transactions for {ID}',
                 'transactions' : transactions }
    return( jsonify( response ), 200 )

@web.route( '/get_decrypted_transactions', methods = ['GET'] )
def get_decrypted_transactions( ):
    # Creat an empty list of transactions
    transactions = [ ]
    
    # For each block in the blockchain
    for block in chain.block:
        # For each transaction in the block
        for transaction in block.data:
            # Append the transaction to the list of total transactions
            transactions.append( transaction.copy( ) ) 
            
            # Read the sender and receiver UUIDs
            sender = transaction[ 'sender' ]
            receiver = transaction[ 'receiver' ]
            
            # If the transaction is encrypted (Starts with AES-)
            if( transaction[ 'data' ].startswith( "AES-" ) ):
                # If this node has the key
                if( ( sender == ID ) and ( receiver in key ) ):
                    # Decrypt the data and update the list of total transactions
                    cipher = AES.new( key[ receiver ] )
                    plaintext = cipher.decrypt( bytes.fromhex( transaction[ 'data' ][ 4: ] ) )
                    transactions[ -1 ][ 'data' ] = plaintext.decode( )
                # If this node has the key
                elif( ( receiver == ID ) and ( sender in key ) ):
                    # Decrypt the data and update the list of total transactions
                    cipher = AES.new( key[ sender ] )
                    plaintext = cipher.decrypt( bytes.fromhex( transaction[ 'data' ][ 4: ] ) )
                    transactions[ -1 ][ 'data' ] = plaintext.decode( )
                    
    response = { 'message' : f'Decrypted Transactions for {ID}',
                 'transactions' : transactions }
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
