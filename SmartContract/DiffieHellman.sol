pragma solidity >= 0.4.22 < 0.7.0;

contract DiffieHellman
{
    uint256 private p;
    uint256 private g;
    uint256 private A;
    uint256 private B;
    
    constructor( uint256 prime, uint256 root ) public
    {
        p = prime;
        g = root;
    }
    
    function Request( uint256 publicKey ) external 
    {
        A = publicKey;
    }
    
    function Request( uint256 prime, uint256 root, uint256 publicKey ) external 
    {
        p = prime;
        g = root;
        A = publicKey;
    }
    
    function Respond( uint256 publicKey ) external
    {
        B = publicKey;
    }
    
    function GetP( ) external view returns( uint256 ) 
    {
        return( p );
    }
    
    function GetG( ) external view returns( uint256 )
    {
        return( g );
    }
    
    function GetA( ) external view returns( uint256 )
    {
        return( A );
    }
    
    function GetB( ) external view returns( uint256 )
    {
        return( B );
    }
}
