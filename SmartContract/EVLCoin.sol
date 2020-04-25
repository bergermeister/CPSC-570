pragma solidity ^0.4.11;

/**
 * EVLCoin Initial Coin Offering (ICO)
 */
contract EVLCoin
{
    /**
     * Diffie-Hellman Public Key Exchange Structure
     */ 
    struct KeyExchange
    {
        uint256 p;      ///< Prime Number
        uint256 g;      ///< Primitive Root Module p
        uint256 A;      ///< Public Key A
        uint256 B;      ///< Public Key B
    }

    uint public constant Maximum = 1000000;                             ///< Total number of EVLCoin tokens available
    uint public RateUSD = 1000;                                         ///< USD to EVLCoin Conversion RateUSD
    uint public Purchased = 0;                                          ///< Number of EVLCoins purchased by investors
    
    mapping( address => uint ) private equity;                          ///< Mapping from investor address to its equity in EVLCoin
    mapping( address => mapping( address => KeyExchange ) ) dhke;       ///< Diffie-Hellman Key Exchange
    mapping( address => mapping( address => string ) ) encryptedData;   ///< Shared Encrypted Information
    
    /**
     * Modifier to check if an investor can buy EVLCoins
     */
    modifier canBuy( uint USD )
    {
        require( ( ( USD * RateUSD ) + Purchased ) <= Maximum );
        _;
    }
    
    /**
     * Modifier to check if an investor can sell EVLCoins
     */
    modifier canSell( address investor, uint coins )
    {
        require( equity[ investor ] >= coins );
        _;
    }
    
    /**
     * Retrieve the equity in EVLCoins of an investor
     */ 
    function GetEquity( address investor ) external constant returns( uint )
    {
        return( equity[ investor ] );
    }
    
    /**
     * Retrieve the equity in USD of an investor
     */ 
    function GetEquityUSD( address investor ) external constant returns( uint )
    {
        return( equity[ investor ] / RateUSD );
    }

    /**
     * Purchase EVLCoins equivalent to the given USD
     */
    function Purchase( address investor, uint usd ) external
        canBuy( usd )
    {
        uint coins = usd * RateUSD;
        equity[ investor ] += coins;
        Purchased += coins;
    }

    /**
     * Sell EVLCoins equivalent to the given number of coins
     */
    function Sell( address investor, uint coins ) external
        canSell( investor, coins )
    {
        equity[ investor ] -= coins;
        Purchased -= coins;
    }
    
    /**
     * Initiates a Diffie-Hellman Public Key Exchange between requestor and responder
     */
    function RequestExchange( address requestor, address responder, uint256 p, uint256 g, uint256 A ) external
    {
        dhke[ requestor ][ responder ].p = p;
        dhke[ requestor ][ responder ].g = g;
        dhke[ requestor ][ responder ].A = A;
    }
    
    /**
     * Completes a Diffie-Hellman Public Key Exchange between requestor and responder
     */
    function RespondExchange( address requestor, address responder, uint256 B ) external
    {
        dhke[ requestor ][ responder ].B = B;
    }
    
    /**
     * Retrieves the Prime number used in the Diffie-Hellman Public Key Exchange between requestor and responder
     */
    function GetP( address requestor, address responder ) external constant returns( uint256 )
    {
        return( dhke[ requestor ][ responder ].p );
    }
    
    /**
     * Retrieves the Primitive Root Modulo p used in the Diffie-Hellman Public Key Exchange between requestor and responder
     */
    function GetG( address requestor, address responder ) external constant returns( uint256 )
    {
        return( dhke[ requestor ][ responder ].g );
    }
    
    /**
     * Retrieves the public key of the requestor in the Diffie-Hellman Public Key Exchange
     */
    function GetA( address requestor, address responder ) external constant returns( uint256 )
    {
        return( dhke[ requestor ][ responder ].A );
    }
    
    /**
     * Retrieves the public key of the responder in the Diffie-Hellman Public Key Exchange
     */
    function GetB( address requestor, address responder ) external constant returns( uint256 )
    {
        return( dhke[ requestor ][ responder ].B );
    }
    
    /**
     * Stores encrypted data sent from sender to receiver
     */
    function StoreData( address sender, address receiver, string data ) external 
    {
        encryptedData[ sender ][ receiver ] = data;
    }
    
    /**
     * Retrieves the encrypted data sent from sender to receiver
     */
    function GetData( address sender, address receiver ) external constant returns( string memory )
    {
        return( encryptedData[ sender ][ receiver ] );
    }
}

