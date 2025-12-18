"""Arkham Exchange WebSocket Client"""

import json
import logging
import os
import threading
import time
import uuid
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union

import websocket

try:
    from .exceptions import ArkhamError
    from .keypair import KeyPair
    from .models import *
except ImportError:
    from exceptions import ArkhamError
    from internal.sdkgen.python.templates.arkham_sdk_python.keypair import KeyPair
    from models import *


logger = logging.getLogger(__name__)


C = TypeVar("C", bound=str)
U = TypeVar("U", bound=str)
T = TypeVar("T")


class WebsocketSubscriptionResponse(Generic[C, U, T], TypedDict):
    """WebSocket subscription response"""

    channel: C
    type: U
    data: T


class WebSocketError(Exception):
    """WebSocket-specific error"""

    def __init__(self, message: str, error_id: Optional[int] = None):
        self.error_id = error_id
        super().__init__(message)


class ArkhamWebSocket:
    """Arkham Exchange WebSocket Client

    Provides real-time data streaming and blocking command execution
    over WebSocket connection.

    Example:
            ```python
            from arkham_sdk_python import ArkhamWebSocket

            ws = ArkhamWebSocket(api_key="your_key", api_secret="your_secret")
            ws.connect()

            def handle_trade(data):
                    print(f"Trade: {data}")

    # Define a handler for trade data
    def handle_trade(data: Union[WebsocketTradesUpdate, WebsocketTradesSnapshot]):
        if data["type"] == "snapshot":
            for trade in data["data"]:
                print(f"Trade snapshot received: {trade}")
        else:
            print(f"Trade update received: {data['data']}")

    def handle_ticker(data):
        print(f"Ticker update: {data}")

    # Subscribe to trades for BTC_USDT (non-blocking)
    print("Subscribing to BTC_USDT trades...")
    unsubscribe_trades = ws.subscribe_trades({"symbol": "BTC_USDT", "snapshot": True}, handle_trade)

    # Subscribe to ticker updates
    print("Subscribing to BTC_USDT ticker...")
    unsubscribe_ticker = ws.subscribe_ticker({"symbol": "BTC_USDT", "snapshot": True}, handle_ticker)

    # Let it run for a bit to see some data
    print("Listening for real-time data... (will run for 5 seconds)")
    time.sleep(5)

            # Unsubscribe
    unsubscribe_trades()
    unsubscribe_ticker()

            ws.close()
            ```
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("ARKHAM_API_KEY"),
        api_secret: Optional[str] = os.getenv("ARKHAM_API_SECRET"),
        websocket_url: str = os.getenv("ARKHAM_WS_URL", "wss://arkm.com/ws"),
    ):
        """Initialize WebSocket client

        Args:
                api_key: API key for authentication
                api_secret: API secret for authentication
                base_url: Base URL for the API (used to derive WebSocket URL)
                websocket_url: Direct WebSocket URL (overrides base_url derivation)
        """
        self._key_pair = KeyPair(api_key, api_secret) if api_key and api_secret else None
        self.websocket_url = websocket_url

        # Connection state
        self._websocket: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = threading.Event()
        self._should_stop = threading.Event()

        # Subscription management
        self._subscriptions: Dict[str, Set[Callable]] = {}
        self._subscription_lock = threading.Lock()

        # Request/response handling for execute calls
        self._pending_requests: Dict[str, threading.Event] = {}
        self._request_responses: Dict[str, Any] = {}
        self._request_errors: Dict[str, Exception] = {}
        self._request_lock = threading.Lock()

        # Connection health
        self._websocket_error: Optional[Exception] = None

    def connect(self) -> None:
        """Connect to WebSocket server

        This starts the WebSocket connection in a background thread.
        The method blocks until connection is established.
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("WebSocket client is already connected")

        self._should_stop.clear()
        self._connected.clear()

        # Create WebSocket with authentication headers
        headers = {}
        if self._key_pair:
            auth_headers = self._key_pair.sign_request("GET", "/ws")
            headers.update(auth_headers)

        self._websocket = websocket.WebSocketApp(
            self.websocket_url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        # Start WebSocket in background thread
        self._thread = threading.Thread(
            target=self._websocket.run_forever,
            kwargs={"ping_interval": 5, "ping_timeout": 3},
            daemon=True,
        )
        self._thread.start()

        # Wait for connection to be established
        if not self._connected.wait(timeout=10):
            raise WebSocketError("Failed to connect to WebSocket server within timeout")

        if self._websocket_error:
            raise self._websocket_error

    def close(self) -> None:
        """Close WebSocket connection"""
        self._should_stop.set()

        if self._websocket:
            self._websocket.close()

        if self._thread:
            self._thread.join(timeout=5)

        self._connected.clear()

    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self._connected.is_set() and not self._should_stop.is_set()

    def wait(self) -> None:
        """Block until the WebSocket connection is closed"""
        if self._thread:
            self._thread.join()
        if self._websocket_error:
            raise self._websocket_error

    def _subscribe(
        self,
        channel: str,
        params: Optional[Dict[str, Any]],
        handler: Callable[[Any], None],
    ) -> Callable[[], None]:
        """Subscribe to a channel

        Args:
                channel: Channel name (e.g., "trades", "candles", "balances")
                params: Channel-specific parameters (e.g., {"symbol": "BTC_USDT"})
                handler: Callback function to handle received data

        Returns:
                Unsubscribe function - call it to unsubscribe
        """
        if not self.is_connected():
            raise WebSocketError("WebSocket is not connected")

        subscription_key = self._get_subscription_key(channel, params)

        with self._subscription_lock:
            if subscription_key not in self._subscriptions:
                self._subscriptions[subscription_key] = set()
                # Send subscribe message
                self._send_subscribe(subscription_key, channel, params)
                self._with_request(subscription_key, lambda: self._send_subscribe(subscription_key, channel, params), timeout=30)

            self._subscriptions[subscription_key].add(handler)

        # Return unsubscribe function
        def unsubscribe():
            with self._subscription_lock:
                if subscription_key in self._subscriptions:
                    self._subscriptions[subscription_key].discard(handler)

                    # If no more handlers, unsubscribe from channel
                    if not self._subscriptions[subscription_key]:
                        del self._subscriptions[subscription_key]
                        self._send_unsubscribe(channel, params)

        return unsubscribe

    def _with_request(self, confirmation_id: str, send: Callable, timeout: float = 60.0) -> Any:
        response_event = threading.Event()

        with self._request_lock:
            self._pending_requests[confirmation_id] = response_event

        try:
            # Send command
            send()

            # Wait for response
            if not response_event.wait(timeout=timeout):
                raise WebSocketError(f"Command timeout after {timeout} seconds")

            with self._request_lock:
                if confirmation_id in self._request_errors:
                    error = self._request_errors.pop(confirmation_id)
                    raise error

                if confirmation_id in self._request_responses:
                    return self._request_responses.pop(confirmation_id)

                raise WebSocketError("No response received")

        finally:
            with self._request_lock:
                self._pending_requests.pop(confirmation_id, None)
                self._request_responses.pop(confirmation_id, None)
                self._request_errors.pop(confirmation_id, None)

    def _execute(
        self,
        channel: str,
        params: "Optional[Dict[str, Any]]" = None,
        timeout: float = 60.0,
    ) -> Any:
        """Execute a command and wait for response

        Args:
                channel: Command channel (e.g., "orders/cancel/all", "orders/new")
                params: Command parameters
                timeout: Timeout in seconds

        Returns:
                Command response data

        Raises:
                WebSocketError: On command failure or timeout
        """
        if not self.is_connected():
            raise WebSocketError("WebSocket is not connected")
        confirmation_id = str(uuid.uuid4())
        return self._with_request(confirmation_id, lambda: self._send_execute(confirmation_id, channel, params), timeout)

    def _on_open(self, ws) -> None:
        """Handle WebSocket connection opened"""
        self._connected.set()
        logger.info("WebSocket connected")

    def _on_message(self, ws, message: str) -> None:
        """Handle incoming WebSocket message"""
        data = json.loads(message)

        # Handle different message types
        if data.get("channel") == "errors":
            self._handle_error(data)
        elif "type" in data:
            self._handle_subscription_data(data)
        else:
            self._handle_response(data)

    def _on_error(self, ws, error) -> None:
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")

        self._websocket_error = error

        if not self._connected.is_set():
            self._connected.set()
        self._connected.clear()

    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket connection closed"""
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self._connected.clear()

    def _handle_error(self, data: Dict[str, Any]) -> None:
        """Handle error message"""
        confirmation_id = data.get("confirmationId")
        error_msg = data.get("message", "Unknown error")
        error_id = data.get("id", 0)
        error_name = data.get("name", "UnknownError")
        error = ArkhamError(error_msg, error_id, error_name)

        if confirmation_id:
            with self._request_lock:
                if confirmation_id in self._pending_requests:
                    self._request_errors[confirmation_id] = error
                    self._pending_requests[confirmation_id].set()

        logger.error(f"WebSocket error: {error_msg} (id: {error_id})")

    def _handle_response(self, data: Dict[str, Any]) -> None:
        """Handle command response"""
        confirmation_id = data.get("confirmationId")
        if not confirmation_id:
            return

        with self._request_lock:
            if confirmation_id in self._pending_requests:
                self._request_responses[confirmation_id] = data.get("data")
                self._pending_requests[confirmation_id].set()

    def _handle_subscription_data(self, data: Dict[str, Any]) -> None:
        """Handle subscription data"""
        channel = data.get("channel")
        subscription_key = data.get("confirmationId")
        if not channel:
            return

        for handler in self._subscriptions[subscription_key].copy():  # Copy to avoid modification during iteration
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in subscription handler: {e}")

    def _get_subscription_key(self, channel: str, params: Dict[str, Any]) -> str:
        """Generate subscription key"""
        key_parts = [channel]

        # Add relevant params to key for proper subscription management
        if "symbol" in params:
            key_parts.append(params["symbol"])
        if "subaccountId" in params:
            key_parts.append(str(params["subaccountId"]))
        if "duration" in params:
            key_parts.append(params["duration"])
        if "group" in params:
            key_parts.append(str(params["group"]))

        return ":".join(key_parts)

    def _send_subscribe(self, confirmation_id: str, channel: str, params: Optional[Dict[str, Any]]) -> None:
        """Send subscribe message"""
        message = {
            "method": "subscribe",
            "confirmationId": confirmation_id,
            "args": {"channel": channel, "params": params or {}},
        }
        self._send_message(message)

    def _send_unsubscribe(self, channel: str, params: Optional[Dict[str, Any]]) -> None:
        """Send unsubscribe message"""
        message = {
            "method": "unsubscribe",
            "args": {"channel": channel, "params": params or {}},
        }
        self._send_message(message)

    def _send_execute(self, confirmation_id: str, channel: str, params: Optional[Dict[str, Any]]) -> None:
        """Send execute message"""
        message = {
            "method": "execute",
            "confirmationId": confirmation_id,
            "args": {"channel": channel, "params": params or {}},
        }
        self._send_message(message)

    def _send_ping(self, confirmation_id: Optional[str] = None) -> None:
        """Send ping message"""
        message = {"method": "ping"}
        if confirmation_id:
            message["confirmationId"] = confirmation_id
        self._send_message(message)

    def ping(self) -> None:
        """Send ping message"""
        if not self.is_connected():
            raise WebSocketError("WebSocket is not connected")
        confirmation_id = str(uuid.uuid4())
        return self._with_request(confirmation_id, lambda: self._send_ping(confirmation_id), timeout=10)

    def _send_message(self, message: Dict[str, Any]) -> None:
        """Send message to WebSocket"""
        if self._websocket and self.is_connected():
            try:
                self._websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                raise WebSocketError(f"Failed to send message: {e}")

    def subscribe_candles(self, params: "CandleSubscriptionParams", handler: "CandlesHandler") -> Callable[[], None]:
        """Subscribe to Candlestick data channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("candles", params, handler)

    def subscribe_ticker(self, params: "TickerSubscriptionParams", handler: "TickerHandler") -> Callable[[], None]:
        """Subscribe to Ticker Updates channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("ticker", params, handler)

    def subscribe_l2_updates(self, params: "L2OrderBookSubscriptionParams", handler: "L2UpdatesHandler") -> Callable[[], None]:
        """Subscribe to L2 order book channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("l2_updates", params, handler)

    def subscribe_l1_updates(self, params: "L1OrderBookSubscriptionParams", handler: "L1UpdatesHandler") -> Callable[[], None]:
        """Subscribe to L1 order book channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("l1_updates", params, handler)

    def subscribe_trades(self, params: "TradeSubscriptionParams", handler: "TradesHandler") -> Callable[[], None]:
        """Subscribe to Trades channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("trades", params, handler)

    def subscribe_balances(self, params: "BalanceSubscriptionParams", handler: "BalancesHandler") -> Callable[[], None]:
        """Subscribe to User Balances channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("balances", params, handler)

    def subscribe_positions(self, params: "PositionSubscriptionParams", handler: "PositionsHandler") -> Callable[[], None]:
        """Subscribe to User Positions channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("positions", params, handler)

    def subscribe_order_statuses(self, params: "OrderStatusSubscriptionParams", handler: "OrderStatusesHandler") -> Callable[[], None]:
        """Subscribe to User Order Status channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("order_statuses", params, handler)

    def subscribe_margin(self, params: "MarginSubscriptionParams", handler: "MarginHandler") -> Callable[[], None]:
        """Subscribe to User Margin channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("margin", params, handler)

    def subscribe_trigger_orders(self, params: "TriggerOrderSubscriptionParams", handler: "TriggerOrdersHandler") -> Callable[[], None]:
        """Subscribe to User Trigger Orders channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("trigger_orders", params, handler)

    def subscribe_lsp_assignments(self, params: "LspAssignmentSubscriptionParams", handler: "LspAssignmentsHandler") -> Callable[[], None]:
        """Subscribe to User LSP Assignments channel

        Args:
            params: Subscription parameters
            handler: Handler function to process incoming messages

        Returns:
            Function to call to unsubscribe
        """
        return self._subscribe("lsp_assignments", params, handler)

    def create_order(self, params: "CreateOrderRequest") -> "CreateOrderResponse":
        """Place a new order

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("orders/new", params)

    def cancel_order(self, params: "CancelOrderRequest") -> "CancelOrderResponse":
        """Cancel an order

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("orders/cancel", params)

    def cancel_all(self, params: "CancelAllRequest") -> "CancelAllResponse":
        """Cancel all orders

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("orders/cancel/all", params)

    def create_trigger_order(self, params: "CreateTriggerOrderRequest") -> "CreateTriggerOrderResponse":
        """Place a new trigger order

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("trigger_orders/new", params)

    def cancel_trigger_order(self, params: "CancelTriggerOrderRequest") -> "CancelTriggerOrderResponse":
        """Cancel a trigger order

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("trigger_orders/cancel", params)

    def cancel_all_trigger_orders(self, params: "CancelAllTriggerOrdersRequest") -> "CancelAllTriggerOrdersResponse":
        """Cancel all trigger orders

        Args:
                params - Parameters for the request
        Raises:
                ArkhamError - on API error
                WebSocketError - on WebSocket error"""

        return self._execute("trigger_orders/cancel/all", params)


CandlesHandler = Callable[[WebsocketSubscriptionResponse[Literal["candles"], Literal["update"], "Candle"]], None]
TickerHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["ticker"], Literal["update"], "Ticker"], WebsocketSubscriptionResponse[Literal["ticker"], Literal["snapshot"], "Ticker"]]], None]
L2UpdatesHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["l2_updates"], Literal["update"], "L2Update"], WebsocketSubscriptionResponse[Literal["l2_updates"], Literal["snapshot"], "OrderBook"]]], None]
L1UpdatesHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["l1_updates"], Literal["update"], "L1OrderBook"], WebsocketSubscriptionResponse[Literal["l1_updates"], Literal["snapshot"], "L1OrderBook"]]], None]
TradesHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["trades"], Literal["update"], "Trade"], WebsocketSubscriptionResponse[Literal["trades"], Literal["snapshot"], List["Trade"]]]], None]
BalancesHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["balances"], Literal["update"], "Balance"], WebsocketSubscriptionResponse[Literal["balances"], Literal["snapshot"], List["Balance"]]]], None]
PositionsHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["positions"], Literal["update"], "Position"], WebsocketSubscriptionResponse[Literal["positions"], Literal["snapshot"], List["Position"]]]], None]
OrderStatusesHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["order_statuses"], Literal["update"], "Order"], WebsocketSubscriptionResponse[Literal["order_statuses"], Literal["snapshot"], List["Order"]]]], None]
MarginHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["margin"], Literal["update"], "Margin"], WebsocketSubscriptionResponse[Literal["margin"], Literal["snapshot"], "Margin"]]], None]
TriggerOrdersHandler = Callable[[Union[WebsocketSubscriptionResponse[Literal["trigger_orders"], Literal["update"], "TriggerOrder"], WebsocketSubscriptionResponse[Literal["trigger_orders"], Literal["snapshot"], List["TriggerOrder"]]]], None]
LspAssignmentsHandler = Callable[[WebsocketSubscriptionResponse[Literal["lsp_assignments"], Literal["update"], "LspAssignment"]], None]
