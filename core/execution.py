import logging
from .strategy import filter_underlying, filter_options, score_options, select_options
from models.contract import Contract
import numpy as np

logger = logging.getLogger(f"strategy.{__name__}")

def sell_puts(client, allowed_symbols, buying_power, strat_logger=None, discord_notifier=None, trades_summary=None):
    """
    Scan allowed symbols and sell short puts up to the buying power limit.
    """
    if not allowed_symbols or buying_power <= 0:
        return

    logger.info("Searching for put options...")
    filtered_symbols = filter_underlying(client, allowed_symbols, buying_power)
    if strat_logger:
        strat_logger.set_filtered_symbols(filtered_symbols)
    if len(filtered_symbols) == 0:
        logger.info("No symbols found with sufficient buying power.")
        return
    option_contracts = client.get_options_contracts(filtered_symbols, 'put')
    snapshots = client.get_option_snapshot([c.symbol for c in option_contracts])
    put_options = filter_options([Contract.from_contract_snapshot(contract, snapshots.get(contract.symbol, None)) for contract in option_contracts if snapshots.get(contract.symbol, None)])
    if strat_logger:
        strat_logger.log_put_options([p.to_dict() for p in put_options])
    
    if put_options:
        logger.info("Scoring put options...")
        scores = score_options(put_options)
        put_options = select_options(put_options, scores)
        
        for p in put_options:
            buying_power -= 100 * p.strike 
            if buying_power < 0:
                break
            
            try:
                logger.info(f"Selling put: {p.symbol}")
                client.market_sell(p.symbol)
                
                # Discord notification for successful trade
                if discord_notifier:
                    discord_notifier.send_trade_notification(
                        trade_type="PUT",
                        symbol=p.underlying,
                        contract_symbol=p.symbol,
                        strike=p.strike,
                        premium=p.bid_price,
                        expiry=f"{p.dte} days"
                    )
                
                # Update trades summary for successful trade
                if trades_summary:
                    trades_summary["puts_sold"] += 1
                    trades_summary["total_premium"] += p.bid_price or 0
                
                if strat_logger:
                    strat_logger.log_sold_puts([p.to_dict()])
                    
            except Exception as e:
                error_str = str(e)
                logger.warning(f"Failed to sell put for {p.underlying}: {error_str}")
                
                # Check if it's an insufficient funds error
                if "insufficient options buying power" in error_str.lower():
                    logger.info(f"Insufficient buying power for {p.underlying}, skipping and continuing with next symbol...")
                    
                    # Send specific insufficient funds notification
                    if discord_notifier:
                        # Try to extract amounts from error message
                        import re
                        import json
                        try:
                            # Parse the JSON error message
                            if error_str.startswith('{"code"'):
                                error_data = json.loads(error_str)
                                required = float(error_data.get("required_options_buying_power", 0))
                                available = float(error_data.get("options_buying_power", 0))
                            else:
                                # Fallback to regex parsing
                                required_match = re.search(r'required: ([\d,]+\.?\d*)', error_str)
                                available_match = re.search(r'available: ([\d,]+\.?\d*)', error_str)
                                required = float(required_match.group(1).replace(',', '')) if required_match else 0
                                available = float(available_match.group(1).replace(',', '')) if available_match else 0
                            
                            discord_notifier.send_insufficient_funds_notification(
                                symbol=p.underlying,
                                required_amount=required,
                                available_amount=available
                            )
                        except (json.JSONDecodeError, ValueError, AttributeError):
                            # Fallback notification if parsing fails
                            discord_notifier.send_insufficient_funds_notification(
                                symbol=p.underlying,
                                required_amount=100 * p.strike,  # Estimated required amount
                                available_amount=0  # Unknown available amount
                            )
                    
                    # Continue to next symbol instead of breaking
                    continue
                else:
                    # For other types of errors, log and continue
                    logger.error(f"Unexpected error selling put for {p.underlying}: {error_str}")
                    if discord_notifier:
                        discord_notifier.send_error_notification(
                            f"Failed to sell put for {p.underlying}: {error_str}",
                            "Put Option Execution"
                        )
                    continue
    else:
        logger.info("No put options found with sufficient delta and open interest.")

def sell_calls(client, symbol, purchase_price, stock_qty, strat_logger=None, discord_notifier=None):
    """
    Select and sell covered calls.
    """
    if stock_qty < 100:
        msg = f"Not enough shares of {symbol} to cover short calls!  Only {stock_qty} shares are held and at least 100 are needed!"
        logger.error(msg)
        if discord_notifier:
            discord_notifier.send_error_notification(msg, f"Insufficient shares for {symbol}")
        raise ValueError(msg)

    logger.info(f"Searching for call options on {symbol}...")
    call_options = filter_options([Contract.from_contract(option, client) for option in client.get_options_contracts([symbol], 'call')], purchase_price)    
    if strat_logger:
        strat_logger.log_call_options([c.to_dict() for c in call_options])

    if call_options:
        scores = score_options(call_options)
        contract = call_options[np.argmax(scores)]
        
        try:
            logger.info(f"Selling call option: {contract.symbol}")
            client.market_sell(contract.symbol)
            
            # Discord notification for successful trade
            if discord_notifier:
                discord_notifier.send_trade_notification(
                    trade_type="CALL",
                    symbol=contract.underlying,
                    contract_symbol=contract.symbol,
                    strike=contract.strike,
                    premium=contract.bid_price,
                    expiry=f"{contract.dte} days"
                )
            
            if strat_logger:
                strat_logger.log_sold_calls(contract.to_dict())
                
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to sell call for {symbol}: {error_str}")
            
            # Check if it's an insufficient funds error  
            if "insufficient options buying power" in error_str.lower():
                logger.info(f"Insufficient buying power for {symbol} call, skipping...")
                
                if discord_notifier:
                    # Try to extract amounts from error message
                    import re
                    import json
                    try:
                        if error_str.startswith('{"code"'):
                            error_data = json.loads(error_str)
                            required = float(error_data.get("required_options_buying_power", 0))
                            available = float(error_data.get("options_buying_power", 0))
                        else:
                            required_match = re.search(r'required: ([\d,]+\.?\d*)', error_str)
                            available_match = re.search(r'available: ([\d,]+\.?\d*)', error_str)
                            required = float(required_match.group(1).replace(',', '')) if required_match else 0
                            available = float(available_match.group(1).replace(',', '')) if available_match else 0
                        
                        discord_notifier.send_insufficient_funds_notification(
                            symbol=symbol,
                            required_amount=required,
                            available_amount=available
                        )
                    except (json.JSONDecodeError, ValueError, AttributeError):
                        discord_notifier.send_insufficient_funds_notification(
                            symbol=symbol,
                            required_amount=0,  # Unknown required amount
                            available_amount=0  # Unknown available amount
                        )
            else:
                # For other types of errors, send regular error notification
                if discord_notifier:
                    discord_notifier.send_error_notification(
                        f"Failed to sell call for {symbol}: {error_str}",
                        "Call Option Execution"
                    )
                # Re-raise non-insufficient-funds errors
                raise
    else:
        logger.info(f"No viable call options found for {symbol}")