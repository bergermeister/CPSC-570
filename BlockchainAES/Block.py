from datetime import datetime as time
from hashlib import sha256 as sha256

class Block:
    def __init__( self, aiIndex, aiNonce, aiTarget, aoData, aiHashPrev, aiTimestamp = 0 ):
        self.index = aiIndex
        if( aiTimestamp == 0 ):
            self.timestamp = int(time.utcnow().timestamp() )
        else:
            self.timestamp = aiTimestamp
        self.nonce = aiNonce
        self.target = aiTarget
        self.data = aoData
        self.hashPrev = aiHashPrev
        self.hashThis = self.Hash( )
    
    def Hash( self ):
        block = { 'index': self.index,
                  'timestamp': self.timestamp,
                  'nonce': self.nonce,
                  'target': self.target,
                  'data': self.data,
                  'hashPrev': self.hashPrev } 
        digest = sha256( str( block ).encode( ) ).hexdigest( )
        return( digest )

    def Mine( self, aiNonce ):
        self.nonce = aiNonce
        self.hashThis = self.Hash( )
        
    def Jsonify( self ):
        return( { 'index': self.index,
                  'timestamp': self.timestamp,
                  'nonce': self.nonce,
                  'target': self.target,
                  'data': self.data,
                  'hashPrev': self.hashPrev,
                  'hashThis': self.hashThis } )
        