import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from api import get_price, place_order, get_order_status, cancel_order
from config import TRADING_PAIRS, ARBITRAGE_PARAMS, LOGGING_SETTINGS, EXCHANGE_API_KEYS, EXCHANGE_URLS, TIMING_SETTINGS

# Setup logging
logging.basicConfig(filename=LOGGING_SETTINGS['log_file'],
                    level=LOGGING_SETTINGS['log_level'].upper(),
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Detect arbitrage opportunities across exchanges
def detect_arbitrage_opportunity(pair):
    opportunities = []
    exchanges = list(EXCHANGE_API_KEYS.keys())

    for i in range(len(exchanges)):
        for j in range(i + 1, len(exchanges)):
            exchange1 = exchanges[i]
            exchange2 = exchanges[j]

            price1 = get_price(exchange1, pair)
            price2 = get_price(exchange2, pair)

            if price1 is None or price2 is None:
                logging.error("Error fetching prices for pair: %s", pair)
                continue

            price1 = float(price1['price'])
            price2 = float(price2['price'])

            # Detect opportunities
            if price1 > price2 * (1 + ARBITRAGE_PARAMS['price_difference_threshold']):
                profit = price1 - price2
                opportunities.append({
                    'buy_exchange': exchange2,
                    'sell_exchange': exchange1,
                    'buy_price': price2,
                    'sell_price': price1,
                    'profit': profit,
                    'pair': pair
                })
            elif price2 > price1 * (1 + ARBITRAGE_PARAMS['price_difference_threshold']):
                profit = price2 - price1
                opportunities.append({
                    'buy_exchange': exchange1,
                    'sell_exchange': exchange2,
                    'buy_price': price1,
                    'sell_price': price2,
                    'profit': profit,
                    'pair': pair
                })

    return opportunities

# Execute arbitrage trade
def execute_trade(opportunity):
    try:
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        pair = opportunity['pair']
        buy_price = opportunity['buy_price']
        sell_price = opportunity['sell_price']
        quantity = min(ARBITRAGE_PARAMS['trade_volume_limit'], 1)  # Can be improved to be dynamic

        # Place buy order
        buy_order = place_order(buy_exchange, pair, 'BUY', quantity, buy_price)
        if buy_order is None:
            logging.error("Failed to place buy order for %s on %s.", pair, buy_exchange)
            return False
        
        buy_order_id = buy_order.get('orderId')
        if not wait_for_order_filled(buy_exchange, buy_order_id):
            logging.error("Buy order not filled. Cancelling order %s.", buy_order_id)
            cancel_order(buy_exchange, buy_order_id)
            return False

        # Place sell order
        sell_order = place_order(sell_exchange, pair, 'SELL', quantity, sell_price)
        if sell_order is None:
            logging.error("Failed to place sell order for %s on %s.", pair, sell_exchange)
            return False

        logging.info(f"Trade executed successfully: Buy on {buy_exchange} at {buy_price}, Sell on {sell_exchange} at {sell_price}.")
        return True

    except Exception as e:
        logging.error("Error executing trade: %s", e)
        return False

# Check if the order is filled
def wait_for_order_filled(exchange, order_id):
    retries = TIMING_SETTINGS['order_retry_limit']
    while retries > 0:
        status = get_order_status(exchange, order_id)
        if status and status.get('status') == 'FILLED':
            logging.info(f"Order {order_id} filled successfully.")
            return True
        elif status and status.get('status') == 'CANCELED':
            logging.info(f"Order {order_id} was canceled.")
            return False
        else:
            retries -= 1
            time.sleep(10)  # Wait before retrying
    logging.error("Order %s not filled after retries.", order_id)
    return False

# Monitor arbitrage opportunities
def monitor_arbitrage():
    while True:
        with ThreadPoolExecutor(max_workers=ARBITRAGE_PARAMS['max_threads']) as executor:
            futures = []
            for pair_info in TRADING_PAIRS:
                pair = pair_info['pair']
                futures.append(executor.submit(detect_arbitrage_opportunity, pair))
            
            for future in as_completed(futures):
                opportunities = future.result()
                for opportunity in opportunities:
                    success = execute_trade(opportunity)
                    if success:
                        logging.info(f"Arbitrage trade completed for pair: {opportunity['pair']}")
                    else:
                        logging.error(f"Arbitrage trade failed for pair: {opportunity['pair']}")
        
        time.sleep(TIMING_SETTINGS['update_interval'])  # Wait before checking again

# Start monitoring for arbitrage opportunities
if __name__ == "__main__":
    monitor_arbitrage()