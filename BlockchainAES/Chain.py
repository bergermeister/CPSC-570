from Block import Block

class Chain:
    def __init__( self ):        
        target = 4
        entry = Block( 1, 1, target, [], 0 )
        valid = False
        targetStr = ''.zfill( entry.target )
        while valid is False:
            digest = entry.hashThis
            if( digest[:target] == targetStr ):
                valid = True
            else:
                entry.Mine( entry.nonce + 1 )
                
        self.transactions=[]
        self.block = []
        self.block.append( entry )

    def Last( self ):
        return( self.block[ -1 ] )
        
    def Mine( self, target ):
        # Determine the number of transactions to add to the block
        count = 10
        if( count > len( self.transactions ) ):
            count = len( self.transactions )
        
        # Take the first 'count' transactions as data
        data = self.transactions[:count]
        del self.transactions[:count]
        
        blockPrev = self.Last( )
        blockThis = Block( blockPrev.index + 1, 1, target, data, blockPrev.hashThis )
        targetStr = ''.zfill( target )
        valid = False
        while valid is False:
            digest = blockThis.Hash( )
            if( digest[:target] == targetStr ):
                valid = True
                self.block.append( blockThis )
            else:
                blockThis.Mine( blockThis.nonce + 1 )
        return( blockThis )
        
    def IsValid( self ):
        blockPrev = self.block[ 0 ]
        blockIndx = 1
        while( blockIndx < len( self.block ) ):
            block = self.block[ blockIndx ]
            if( block.hashPrev != blockPrev.Hash( ) ):
                return( False )
            digest = block.Hash( )
            targetStr = ''.zfill( block.target )
            if( block.hashThis != digest ):
                return( False )
            if( digest[:block.target] != targetStr ):
                return( False )
            blockPrev = block
            blockIndx += 1
        return( True )
        
    def List( self ):
        list = []
        for block in self.block:
            entry = { 'index': block.index,
                      'timestamp': block.timestamp,
                      'nonce': block.nonce,
                      'target': block.target,
                      'data': block.data,
                      'hashPrev': block.hashPrev,
                      'hashThis': block.hashThis }    
            list.append( entry )
        return( list )
    
    def AddTransaction( self, Sender, Receiver, Data ):
        self.transactions.append( { 'sender': Sender,
                                    'receiver': Receiver,
                                    'data': Data } )
        return( self.Last( ).index + 1 )
    