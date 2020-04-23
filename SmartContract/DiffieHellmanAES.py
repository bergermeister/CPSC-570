from Crypto.Cipher import AES
from hashlib import sha256 as sha256

class DiffieHellmanAES:
    def __init__( self, prime, root, secretA, secretB ):
        self.p = prime
        self.g = root
        self.a = secretA
        self.b = secretB
        self.s = ( self.GetA( ) ** self.b ) % self.p
        
    def GetA( self ):
        return( ( self.g ** self.a ) % self.p )
    
    def GetB( self ):
        return( ( self.g ** self.b ) % self.p )

    def Dump( self ):
        print( f"p={self.p} | g={self.g}" )
        print( f"a={self.a} | b={self.b}" )
        print( f"A={self.GetA()} | B={self.GetB()}" )
        print( f"s={( self.GetA( ) ** self.b ) % self.p} | s={( self.GetB( ) ** self.a ) % self.p}" )

    def Encrypt( self, plaintext ):
        dataLen = len( plaintext )
        pad = ( 16 - ( dataLen % 16 ) ) % 16
        plaintext = plaintext.ljust( dataLen + pad, '~' )
        key = bytes.fromhex( sha256( str( self.s ).encode( ) ).hexdigest( ) )
        cipher = AES.new( key )
        ciphertext = cipher.encrypt( plaintext )
        return( ciphertext.hex( ) )

    def Decrypt( self, ciphertext ):
        key = bytes.fromhex( sha256( str( self.s ).encode( ) ).hexdigest( ) )
        cipher = AES.new( key )
        plaintext = cipher.decrypt( bytes.fromhex( ciphertext ) )
        return( plaintext )


