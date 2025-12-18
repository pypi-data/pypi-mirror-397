# Arkham Exchange Python SDK

A Python client library for the Arkham Exchange API, providing both REST and WebSocket interfaces for trading cryptocurrency and managing your account.

## Installation

Install the SDK using pip:

```bash
pip install arkham-sdk-python
```

## Basic Usage

### REST API Client

```python
from arkham_sdk_python.client import Arkham

# Initialize the client with your API credentials
client = Arkham(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Get trading pairs
pairs = client.get_pairs()
print(f"Available pairs: {pairs}")

# Get order book for a specific pair
orderbook = client.get_orderbook(symbol="BTC_USDT")
print(f"Order book: {orderbook}")

# Place a limit order
order = client.create_order(
    {
        "symbol": "BTC_USDT",
        "side": OrderSide.Buy,
        "type": OrderType.LimitGtc,
        "size": "0.0001",
        "price": "30000",
    }
)
print(f"Order placed: {order}")
```

### WebSocket Client

```python
from arkham_sdk_python.ws_client import ArkhamWebSocket
from arkham_sdk_python.models import WebsocketTradesUpdate

def handle_trade_update(update: WebsocketTradesUpdate):
    print(f"Trade update: {update}")

# Initialize WebSocket client
ws = ArkhamWebSocket(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Connect and subscribe to trades
ws.connect()
ws.subscribe_trades("BTC-USD", handle_trade_update)

# Keep the connection alive
try:
    ws.wait()
except KeyboardInterrupt:
    ws.close()
```

## Authentication

The SDK requires API credentials to access private endpoints:

1. **API Key**: Your unique API key from Arkham Exchange
2. **API Secret**: Your secret key for signing requests

You can obtain these credentials from your Arkham Exchange account dashboard.

## Examples

For more detailed usage examples, see the `examples/` directory:

- [`examples/rest.py`](examples/rest.py) - Comprehensive REST API usage examples
- [`examples/websocket.py`](examples/websocket.py) - WebSocket client usage examples

These examples demonstrate:

- Authentication and client initialization
- Fetching market data (pairs, order books, trades)
- Placing and managing orders
- Real-time data streaming via WebSocket
- Error handling and best practices

## Features

- **REST API Client**: Full access to Arkham Exchange REST endpoints
- **WebSocket Client**: Real-time streaming of market data and order updates
- **Type Safety**: Complete type annotations for better development experience
- **Error Handling**: Comprehensive exception handling for API errors
- **Authentication**: Built-in request signing for private endpoints

## Requirements

- Python 3.8 or higher
- `requests` >= 2.25.0
- `websocket-client` >= 1.0.0
- `typing_extensions` >= 4.0.0

## Contributing

This SDK is automatically generated from the Arkham Exchange API specification. The majority of the code is generated automatically to ensure consistency with the API.

For suggestions, bug reports, or feature requests, please:

1. **Open a GitHub Issue**: Report bugs or request features via GitHub issues
2. **Provide Details**: Include relevant error messages, code snippets, and expected behavior
3. **API Changes**: For API-related changes, note that modifications may need to be made to the API specification rather than the SDK directly

We welcome feedback and will work to address issues promptly!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

For technical support or questions:

- GitHub Issues: Report bugs and request features
- Documentation: Refer to the Arkham Exchange API documentation
- Examples: Check the `examples/` directory for usage patterns

---

**Note**: This SDK is in active development. Please check the [releases page](https://github.com/arkhamintelligence/arkham-sdk-python/releases) for the latest updates and changelog.
