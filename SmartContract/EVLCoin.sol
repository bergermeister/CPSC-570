pragma solidity >= 0.4.22 < 0.7.0;

/**
 * EVLCoin Initial Coin Offering (ICO)
 */
contract EVLCoin
{
    uint public constant Maximum = 1000000;     ///< Total number of EVLCoin tokens available
    uint public RateUSD = 1000;                 ///< USD to EVLCoin Conversion RateUSD
    uint public Purchased = 0;                  ///< Number of EVLCoins purchased by investors
    
    mapping( address => uint ) private equity;  ///< Mapping from investor address to its equity in EVLCoin
    
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
    function GetEquity( address investor ) external view returns( uint )
    {
        return( equity[ investor ] );
    }
    
    /**
     * Retrieve the equity in USD of an investor
     */ 
    function GetEquityUSD( address investor ) external view returns( uint )
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
        Purchased = coins;
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
}

