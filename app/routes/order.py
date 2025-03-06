from flask import Blueprint, jsonify, request
import MetaTrader5 as mt5
import logging
from flasgger import swag_from
import time

order_bp = Blueprint('order', __name__)
logger = logging.getLogger(__name__)

@order_bp.route('/order', methods=['POST'])
@swag_from({
    'tags': ['Order'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'symbol': {'type': 'string'},
                    'volume': {'type': 'number'},
                    'type': {'type': 'string', 'enum': ['BUY', 'SELL']},
                    'deviation': {'type': 'integer', 'default': 20},
                    'magic': {'type': 'integer', 'default': 0},
                    'comment': {'type': 'string', 'default': ''},
                    'type_filling': {'type': 'string', 'enum': ['ORDER_FILLING_IOC', 'ORDER_FILLING_FOK', 'ORDER_FILLING_RETURN']},
                    'sl': {'type': 'number'},
                    'tp': {'type': 'number'}
                },
                'required': ['symbol', 'volume', 'type']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Order executed successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'result': {
                        'type': 'object',
                        'properties': {
                            'retcode': {'type': 'integer'},
                            'order': {'type': 'integer'},
                            'magic': {'type': 'integer'},
                            'price': {'type': 'number'},
                            'symbol': {'type': 'string'},
                            # Add other relevant fields as needed
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request or order failed.'
        },
        500: {
            'description': 'Internal server error.'
        }
    }
})
def send_market_order_endpoint():
    """
    Send Market Order
    ---
    description: Execute a market order for a specified symbol with optional parameters.
    """
    try:
        data = request.get_json()
        
###############################################################
        # Initialize MetaTrader5
        if not mt5.initialize():
            logger.error("Failed to initialize MetaTrader5")
            quit()

        # Check if connected to MetaTrader5
        if not mt5.terminal_info():
            logger.error("Failed to connect to MetaTrader5 terminal")
            mt5.shutdown()
            quit()

        if not data:
            return jsonify({"error": "Order data is required"}), 400

        required_fields = ['symbol', 'volume', 'type']
        if not all(field in data for field in required_fields):
            logger.error(f"Missing required fields: {required_fields}")
            return jsonify({"error": "Missing required fields"}), 400

        # Print all received data
        print("Received data:", data)
        logger.error(f"Received data: {data}")

        order_type_dict = {
            'BUY': mt5.ORDER_TYPE_BUY,
            'SELL': mt5.ORDER_TYPE_SELL
        }

        type_filling = {
            "ORDER_FILLING_FOK" : mt5.ORDER_FILLING_FOK,
            "ORDER_FILLING_IOC" : mt5.ORDER_FILLING_IOC,
            "ORDER_FILLING_RETURN" : mt5.ORDER_FILLING_RETURN
        }

        # Sử dụng từ điển để lấy giá trị số tương ứng
        order_type = order_type_dict.get(data['type'])

        if order_type is None:
            logger.error(f"Invalid order type : buy: {mt5.ORDER_TYPE_BUY} , sell: {mt5.ORDER_TYPE_SELL}, dat type: {data['type']}")
            return jsonify({"error": "Invalid order type {order_type}"}), 400

###############################################################

        # Get current price
        tick = mt5.symbol_info_tick(data['symbol'])
        if tick is None:
            return jsonify({"error": "Failed to get symbol price"}), 400

        price_dict = {
            "BUY": tick.ask,  # Buy order uses Ask price
            "SELL": tick.bid   # Sell order uses Bid price
        }

        price = price_dict[data['type']]

        # Prepare the order request
        request_data = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": str(data['symbol']),
            "volume": float(data['volume']),
            "type": order_type,
            "price": float(price),
            "deviation": int(data.get('deviation', 20)),
            "magic": int(data.get('magic', 0)),
            "comment": str(data.get('comment', '')),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": type_filling[data.get('type_filling', 'ORDER_FILLING_IOC')],
        }

        logger.error(f"1.Request data: {request_data}")

        # Add optional SL/TP if provided
        if 'sl' in data:
            request_data["sl"] = float(data['sl'])
        if 'tp' in data:
            request_data["tp"] = float(data['tp'])

        # Send order
        logger.error(f"2.Request data: {request_data}")
        result = mt5.order_send(request_data)

        logger.debug(f"Order result: {result}")
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error_code, error_str = mt5.last_error()

            return jsonify({
                "error": f"Order failed: {result.comment}",
                "mt5_error": error_str,
                "result": result._asdict()
            }), 400

        return jsonify({
            "message": "Order executed successfully",
            "result": result._asdict()
        })

    except Exception as e:
        logger.error(f"Error in send_market_order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
