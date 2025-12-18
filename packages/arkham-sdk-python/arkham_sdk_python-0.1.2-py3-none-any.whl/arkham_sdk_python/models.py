"""Models module"""

from enum import Enum
from typing import List, Literal, TypedDict, Union

from typing_extensions import NotRequired


class AccountWithdrawRequest(TypedDict):
    addressId: int
    amount: str
    beneficiary: NotRequired["WithdrawalTravelRuleBeneficiary"]
    subaccountId: int
    symbol: str


class AccountWithdrawUsingMFARequest(TypedDict):
    address: str
    amount: str
    beneficiary: NotRequired["WithdrawalTravelRuleBeneficiary"]
    chain: str
    isMoonpay: bool
    subaccountId: int
    symbol: str


class AddToWatchlistRequest(TypedDict):
    symbol: str


class Airdrop(TypedDict):
    amount: str
    assetSymbol: str
    id: int
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class AirdropClaim(TypedDict):
    address: NotRequired[str]
    amount: NotRequired[str]
    claimed: NotRequired[bool]
    eligible: bool
    passedKYC: bool
    proof: NotRequired[List[str]]
    wei: NotRequired[str]


class Alert(TypedDict):
    id: int
    lastUpdated: int
    """Time in microseconds since unix epoch"""
    message: str
    type: str


class AlertPriceType(str, Enum):
    Last = "last"
    Mark = "mark"
    Index = "index"


AlertType = Literal["above", "below"]


class AllowanceHolderAllowanceIssue(TypedDict):
    actual: str
    spender: str


class AllowanceHolderBalanceIssue(TypedDict):
    actual: str
    expected: str
    token: str


class AllowanceHolderBaseResponse(TypedDict):
    blockNumber: NotRequired[str]
    buyAmount: NotRequired[str]
    buyToken: NotRequired[str]
    fees: NotRequired["AllowanceHolderFees"]
    gas: NotRequired[str]
    gasPrice: NotRequired[str]
    issues: NotRequired["AllowanceHolderIssues"]
    liquidityAvailable: bool
    minBuyAmount: NotRequired[str]
    route: NotRequired["AllowanceHolderRoute"]
    sellAmount: NotRequired[str]
    sellToken: NotRequired[str]
    tokenMetadata: NotRequired["AllowanceHolderTokenMetadata"]
    totalNetworkFee: NotRequired[str]
    transaction: NotRequired["AllowanceHolderTransaction"]
    zid: str


class AllowanceHolderFee(TypedDict):
    amount: str
    token: str
    type: str


class AllowanceHolderFees(TypedDict):
    gasFee: "AllowanceHolderFee"
    integratorFee: "AllowanceHolderFee"
    zeroExFee: "AllowanceHolderFee"


class AllowanceHolderIssues(TypedDict):
    allowance: "AllowanceHolderAllowanceIssue"
    balance: "AllowanceHolderBalanceIssue"
    invalidSourcesPassed: List[str]
    simulationIncomplete: bool


class AllowanceHolderRoute(TypedDict):
    fills: List["AllowanceHolderRouteFill"]
    tokens: List["AllowanceHolderRouteToken"]


AllowanceHolderRouteFill = TypedDict(
    "AllowanceHolderRouteFill",
    {
        "from": str,
        "proportionBps": str,
        "source": str,
        "to": str,
    },
)


class AllowanceHolderRouteToken(TypedDict):
    address: str
    symbol: str


class AllowanceHolderTokenMetadata(TypedDict):
    buyToken: "AllowanceHolderTokenTaxMetadata"
    sellToken: "AllowanceHolderTokenTaxMetadata"


class AllowanceHolderTokenTaxMetadata(TypedDict):
    buyTaxBps: str
    sellTaxBps: str


class AllowanceHolderTransaction(TypedDict):
    data: str
    gas: str
    gasPrice: str
    to: str
    value: str


class Announcement(TypedDict):
    content: str
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int


class ApiKey(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int
    ipWhitelist: List[str]
    name: str
    read: bool
    write: bool


class ApiKeyUpdateRequest(TypedDict):
    ipWhitelist: List[str]
    name: str
    read: bool
    write: bool


class ApiKeyWithSecret(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int
    ipWhitelist: List[str]
    key: "UUID"
    name: str
    read: bool
    secret: "Secret"
    write: bool


class Asset(TypedDict):
    chains: List["Blockchain"]
    featuredPair: str
    geckoId: str
    imageUrl: str
    minDeposit: str
    minWithdrawal: str
    moonPayChain: NotRequired[str]
    moonPayCode: NotRequired[str]
    name: str
    stablecoin: bool
    status: "ListingStatus"
    symbol: str
    withdrawalFee: str


class Balance(TypedDict):
    balance: str
    balanceUSDT: str
    free: str
    freeUSDT: str
    lastUpdateAmount: str
    lastUpdateId: int
    lastUpdateReason: "PositionUpdateReason"
    lastUpdateTime: int
    """Time in microseconds since unix epoch"""
    priceUSDT: str
    subaccountId: int
    symbol: str


class BalanceSubscriptionParams(TypedDict):
    snapshot: bool
    snapshotInterval: "SnapshotInterval"
    subaccountId: int


class BalanceUpdate(TypedDict):
    amount: str
    assetSymbol: str
    balance: str
    id: int
    reason: "PositionUpdateReason"
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""


class Blockchain(TypedDict):
    assetSymbol: str
    blockTime: int
    confirmations: int
    name: str
    symbol: str
    type: int


class CancelAllRequest(TypedDict):
    subaccountId: int
    timeToCancel: int
    """Time to cancel all orders, 0 for immediate. Granularity is 1 second. Use this to set a dead man's switch."""


class CancelAllResponse(TypedDict):
    pass


class CancelAllTriggerOrdersRequest(TypedDict):
    subaccountId: int
    symbol: str
    triggerPriceType: NotRequired["TriggerPriceType"]


class CancelAllTriggerOrdersResponse(TypedDict):
    subaccountId: int
    symbol: str
    triggerPriceType: NotRequired["TriggerPriceType"]


class CancelOrderRequest(TypedDict):
    clientOrderId: str
    """client order ID to cancel, required if orderId is not provided"""
    orderId: int
    """order ID to cancel, required if clientOrderId is not provided"""
    subaccountId: int
    timeToCancel: int
    """Time to cancel the order, 0 for immediate. Granularity is 1 second."""


class CancelOrderResponse(TypedDict):
    orderId: int


class CancelReplaceOrderRequest(TypedDict):
    brokerId: NotRequired[int]
    """The ID of the broker used to create this order"""
    cancelClientOrderId: NotRequired[str]
    """Client Order ID of the order to cancel and replace with the new order"""
    cancelOrderId: NotRequired[int]
    """ID of the order to cancel and replace with the new order"""
    cancelSubaccountId: NotRequired[int]
    """Subaccount ID of the order to cancel and replace with the new order"""
    clientOrderId: NotRequired[str]
    postOnly: NotRequired[bool]
    """if true, the order will be closed if it can be matched immediately. Only supported on limit gtc orders."""
    price: NotRequired[str]
    """limit price, 0 for market orders"""
    reduceOnly: NotRequired[bool]
    """if true, the order will only reduce the position size."""
    side: "OrderSide"
    size: str
    subaccountId: NotRequired[int]
    symbol: str
    type: "OrderType"


class CancelReplaceOrderResponse(TypedDict):
    cancelResponse: "CancelOrderResponse"
    createResponse: "CreateOrderResponse"


class CancelTriggerOrderRequest(TypedDict):
    clientOrderId: NotRequired[str]
    subaccountId: NotRequired[int]
    symbol: str
    triggerOrderId: NotRequired[int]
    triggerPriceType: NotRequired["TriggerPriceType"]


class CancelTriggerOrderResponse(TypedDict):
    clientOrderId: NotRequired[str]
    subaccountId: NotRequired[int]
    symbol: str
    triggerOrderId: NotRequired[int]
    triggerPriceType: NotRequired["TriggerPriceType"]


class Candle(TypedDict):
    close: str
    duration: Literal[60000000, 300000000, 900000000, 1800000000, 3600000000, 21600000000, 86400000000]
    high: str
    low: str
    open: str
    quoteVolume: str
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    volume: str


class CandleDuration(str, Enum):
    D1m = "1m"
    D5m = "5m"
    D15m = "15m"
    D30m = "30m"
    D1h = "1h"
    D6h = "6h"
    D24h = "24h"


class CandleSubscriptionParams(TypedDict):
    duration: NotRequired["CandleDuration"]
    symbol: str


class Commission(TypedDict):
    amount: str
    assetSymbol: str
    id: int
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class CompetitionOptInRequest(TypedDict):
    competition_id: int


class ConfirmWithdrawalAddressRequest(TypedDict):
    code: "UUID"


class CreateAirdropAddressRequest(TypedDict):
    address: str


class CreateApiKeyRequest(TypedDict):
    ipWhitelist: List[str]
    name: str
    read: bool
    write: bool


class CreateFireblocksApiKeyRequest(TypedDict):
    name: str


class CreateOrderRequest(TypedDict):
    brokerId: NotRequired[int]
    """The ID of the broker used to create this order"""
    clientOrderId: NotRequired[str]
    postOnly: NotRequired[bool]
    """if true, the order will be closed if it can be matched immediately. Only supported on limit gtc orders."""
    price: NotRequired[str]
    """limit price, 0 for market orders"""
    reduceOnly: NotRequired[bool]
    """if true, the order will only reduce the position size."""
    side: "OrderSide"
    size: str
    subaccountId: NotRequired[int]
    symbol: str
    type: "OrderType"


class CreateOrderResponse(TypedDict):
    clientOrderId: NotRequired[str]
    orderId: int
    price: str
    side: "OrderSide"
    size: str
    subaccountId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    type: "OrderType"


class CreateOrdersBatchRequest(TypedDict):
    orders: List["CreateOrderRequest"]


class CreateOrdersBatchResponse(TypedDict):
    orders: List["OrderBatchItem"]


class CreatePerpTransferRequest(TypedDict):
    fromSubaccountId: int
    symbol: str
    toSubaccountId: int


class CreatePerpTransferResponse(TypedDict):
    transferId: int


class CreateSimpleOrderRequest(TypedDict):
    brokerId: NotRequired[int]
    """The ID of the broker used to create this order"""
    side: "OrderSide"
    size: str
    subaccountId: int
    symbol: str


class CreateStateDisclaimerAcknowledgementRequest(TypedDict):
    stateCode: str


class CreateStateDisclaimerAcknowledgementResponse(TypedDict):
    acknowledged: bool


class CreateSubaccountRequest(TypedDict):
    name: str


class CreateSubaccountResponse(TypedDict):
    id: int


class CreateTransferRequest(TypedDict):
    amount: str
    fromSubaccountId: int
    symbol: str
    toSubaccountId: int


class CreateTransferResponse(TypedDict):
    transferId: int


class CreateTriggerOrderRequest(TypedDict):
    brokerId: NotRequired[int]
    """The ID of the broker used to create this order"""
    clientOrderId: NotRequired[str]
    postOnly: NotRequired[bool]
    """if true, the order will be closed if it can be matched immediately. Only supported on limit gtc orders."""
    price: NotRequired[str]
    """limit price, 0 for market orders"""
    reduceOnly: NotRequired[bool]
    """if true, the order will only reduce the position size."""
    side: "OrderSide"
    size: str
    subaccountId: NotRequired[int]
    symbol: str
    triggerPrice: str
    triggerPriceType: "TriggerPriceType"
    triggerType: "TriggerType"
    type: "OrderType"


class CreateTriggerOrderResponse(TypedDict):
    price: str
    side: "OrderSide"
    size: str
    symbol: str
    triggerOrderId: int
    type: "OrderType"


class CreateWithdrawalAddressRequest(TypedDict):
    address: str
    chain: str
    label: str
    memo: NotRequired[int]


class DeleteSessionRequest(TypedDict):
    sessionId: int


class Deposit(TypedDict):
    amount: str
    chain: str
    confirmed: bool
    depositAddress: str
    id: int
    price: str
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    transactionHash: str


class DepositAddressesResponse(TypedDict):
    addresses: List[str]


class Error(TypedDict):
    id: "ErrorId"
    message: str
    """Additional details about the error"""
    name: "ErrorName"


class ErrorCode(int, Enum):
    InternalError = 0
    BadRequest = 1
    Unauthorized = 2
    InvalidSymbol = 3
    SymbolRequired = 4
    InvalidMethod = 5
    MethodRequired = 6
    InvalidChannel = 7
    ChannelRequired = 8
    InvalidGroup = 10
    RateLimitExceeded = 11
    Forbidden = 13


class ErrorId(int, Enum):
    """The unique identifier for the error"""

    InternalError = 10000
    BadRequest = 10001
    Unauthorized = 10002
    InvalidSymbol = 10003
    SymbolRequired = 10004
    RateLimitExceeded = 10005
    Forbidden = 10006
    InvalidIP = 10007
    Throttled = 10008
    KeyNotPermitted = 10009
    ParsingKey = 10010
    VerifyingKey = 10011
    RequiresRead = 10012
    RequiresWrite = 10013
    SignatureMissing = 10014
    ExpiresMissing = 10015
    ParsingExpires = 10016
    ExpiresTooFar = 10017
    ExpiredSignature = 10018
    SignatureMismatch = 10019
    IPNotAllowed = 10020
    MFA = 10021
    ParsingRequest = 10022
    SubaccountNotFound = 10023
    Conflict = 10024
    NotFound = 10025
    InvalidMethod = 20001
    MethodRequired = 20002
    InvalidChannel = 20003
    ChannelRequired = 20004
    InvalidGroup = 20005
    InvalidSize = 30001
    InvalidPrice = 30002
    InvalidPostOnly = 30003
    InvalidReduceOnly = 30004
    InvalidNotional = 30005
    UnknownOrderType = 30006
    PairNotEnabled = 30007
    TradingFreeze = 30008
    PostOnly = 30009
    InsufficientBalance = 30010
    InvalidPair = 30011
    NoMarkPrice = 30012
    InsufficientLiquidity = 30013
    ClientOrderIdAlreadyExists = 30014
    ClientOrderIdNotFound = 30015
    ReduceOnlyInvalid = 30016
    UnsupportedOrderSide = 30017
    UnsupportedAssetType = 30018
    PositionLimit = 30019
    InvalidClientOrderID = 30020
    InvalidTriggerType = 30021
    InvalidTriggerPriceType = 30022
    InvalidOrderSide = 30023
    InvalidOrderType = 30024
    InvalidBrokerId = 30025
    UserFrozen = 30026
    UserDeleted = 30027
    OrderIdNotFound = 30028
    FailedRiskCheck = 40001
    MemoNotSupported = 40002
    InvalidWithdrawalAddress = 40003
    PositionNotFound = 40004
    InvalidChain = 40005
    FuturesNotEnabled = 40006
    SubaccountHasOpenFuturePositions = 40007
    LspAssignmentGreaterThanMaxNotional = 40008
    LspMaxNotionalGreaterThanMarginLimit = 40009
    LspMaxNotionalMustNotBeNegative = 40010
    PortfolioLiquidation = 40011
    NegativeAmount = 40012
    ZeroAmount = 40013
    NeedStateAcknowledgement = 40014
    InvalidAlertType = 90001
    InvalidAlertPriceType = 90002
    InvalidVoucherStatus = 90003
    InvalidCandleDuration = 90004
    InvalidNotificationType = 90005
    TooManyMFAAttempts = 90006
    InvalidMFA = 90007
    TooManyAttempts = 90008
    InvalidRole = 90009
    InvalidEmail = 90010
    ChangeEmailRequestRateLimited = 90011


class ErrorName(str, Enum):
    """The name of the error"""

    InternalError = "InternalError"
    BadRequest = "BadRequest"
    Unauthorized = "Unauthorized"
    InvalidSymbol = "InvalidSymbol"
    SymbolRequired = "SymbolRequired"
    RateLimitExceeded = "RateLimitExceeded"
    Forbidden = "Forbidden"
    InvalidIP = "InvalidIP"
    Throttled = "Throttled"
    KeyNotPermitted = "KeyNotPermitted"
    ParsingKey = "ParsingKey"
    VerifyingKey = "VerifyingKey"
    RequiresRead = "RequiresRead"
    RequiresWrite = "RequiresWrite"
    SignatureMissing = "SignatureMissing"
    ExpiresMissing = "ExpiresMissing"
    ParsingExpires = "ParsingExpires"
    ExpiresTooFar = "ExpiresTooFar"
    ExpiredSignature = "ExpiredSignature"
    SignatureMismatch = "SignatureMismatch"
    IPNotAllowed = "IPNotAllowed"
    MFA = "MFA"
    ParsingRequest = "ParsingRequest"
    SubaccountNotFound = "SubaccountNotFound"
    Conflict = "Conflict"
    NotFound = "NotFound"
    InvalidMethod = "InvalidMethod"
    MethodRequired = "MethodRequired"
    InvalidChannel = "InvalidChannel"
    ChannelRequired = "ChannelRequired"
    InvalidGroup = "InvalidGroup"
    InvalidSize = "InvalidSize"
    InvalidPrice = "InvalidPrice"
    InvalidPostOnly = "InvalidPostOnly"
    InvalidReduceOnly = "InvalidReduceOnly"
    InvalidNotional = "InvalidNotional"
    UnknownOrderType = "UnknownOrderType"
    PairNotEnabled = "PairNotEnabled"
    TradingFreeze = "TradingFreeze"
    PostOnly = "PostOnly"
    InsufficientBalance = "InsufficientBalance"
    InvalidPair = "InvalidPair"
    NoMarkPrice = "NoMarkPrice"
    InsufficientLiquidity = "InsufficientLiquidity"
    ClientOrderIdAlreadyExists = "ClientOrderIdAlreadyExists"
    ClientOrderIdNotFound = "ClientOrderIdNotFound"
    ReduceOnlyInvalid = "ReduceOnlyInvalid"
    UnsupportedOrderSide = "UnsupportedOrderSide"
    UnsupportedAssetType = "UnsupportedAssetType"
    PositionLimit = "PositionLimit"
    InvalidClientOrderID = "InvalidClientOrderID"
    InvalidTriggerType = "InvalidTriggerType"
    InvalidTriggerPriceType = "InvalidTriggerPriceType"
    InvalidOrderSide = "InvalidOrderSide"
    InvalidOrderType = "InvalidOrderType"
    InvalidBrokerId = "InvalidBrokerId"
    UserFrozen = "UserFrozen"
    UserDeleted = "UserDeleted"
    OrderIdNotFound = "OrderIdNotFound"
    FailedRiskCheck = "FailedRiskCheck"
    MemoNotSupported = "MemoNotSupported"
    InvalidWithdrawalAddress = "InvalidWithdrawalAddress"
    PositionNotFound = "PositionNotFound"
    InvalidChain = "InvalidChain"
    FuturesNotEnabled = "FuturesNotEnabled"
    SubaccountHasOpenFuturePositions = "SubaccountHasOpenFuturePositions"
    LspAssignmentGreaterThanMaxNotional = "LspAssignmentGreaterThanMaxNotional"
    LspMaxNotionalGreaterThanMarginLimit = "LspMaxNotionalGreaterThanMarginLimit"
    LspMaxNotionalMustNotBeNegative = "LspMaxNotionalMustNotBeNegative"
    PortfolioLiquidation = "PortfolioLiquidation"
    NegativeAmount = "NegativeAmount"
    ZeroAmount = "ZeroAmount"
    NeedStateAcknowledgement = "NeedStateAcknowledgement"
    InvalidAlertType = "InvalidAlertType"
    InvalidAlertPriceType = "InvalidAlertPriceType"
    InvalidVoucherStatus = "InvalidVoucherStatus"
    InvalidCandleDuration = "InvalidCandleDuration"
    InvalidNotificationType = "InvalidNotificationType"
    TooManyMFAAttempts = "TooManyMFAAttempts"
    InvalidMFA = "InvalidMFA"
    TooManyAttempts = "TooManyAttempts"
    InvalidRole = "InvalidRole"
    InvalidEmail = "InvalidEmail"
    ChangeEmailRequestRateLimited = "ChangeEmailRequestRateLimited"


class Exchange(str, Enum):
    Binance = "binance"
    Bybit = "bybit"
    Okx = "okx"
    Coinbase = "coinbase"
    Kraken = "kraken"
    Kucoin = "kucoin"
    Gateio = "gateio"
    BitMart = "bitmart"
    Htx = "htx"
    Mexc = "mexc"
    Bitget = "bitget"
    CryptoDotCom = "crypto.com"
    Gemini = "gemini"
    BinanceUS = "binance_us"
    Arkham = "arkham"


class FireblocksApiKey(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int
    name: str


class FireblocksApiKeyUpdateRequest(TypedDict):
    name: str


class FireblocksApiKeyWithSecret(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int
    key: "UUID"
    name: str
    secret: "Secret"


class FormDataAuthenticateRequest(TypedDict):
    redirectPath: str
    tradeInToken: str


class FreezeSettings(TypedDict):
    freezeAccountMgmt: bool
    freezeDeposit: bool
    freezeReduceOnlyTrading: bool
    freezeTrading: bool
    freezeWithdrawal: bool
    offboardingMode: bool


class FundingRateHistoryItem(TypedDict):
    time: int
    """Time in microseconds since unix epoch"""
    value: str


class FundingRatePayment(TypedDict):
    amount: str
    assetSymbol: str
    id: int
    indexPrice: str
    pairSymbol: str
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class HistoricBalance(TypedDict):
    amount: str
    time: int
    """Time in microseconds since unix epoch"""


class IPInfo(TypedDict):
    location: "IPInfoLocation"
    privacy: "IPInfoPrivacy"


class IPInfoLocation(TypedDict):
    city: str
    country: str
    latitude: float
    longitude: float
    postalCode: str
    region: str
    timezone: str


class IPInfoPrivacy(TypedDict):
    hosting: bool
    proxy: bool
    relay: bool
    service: NotRequired[str]
    tor: bool
    vpn: bool


class IndexPrice(TypedDict):
    constituents: List["IndexPriceConstituent"]
    price: str
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""


class IndexPriceConstituent(TypedDict):
    exchange: "Exchange"
    price: str
    time: int
    """Time of the last update according to the exchange"""
    weight: str


class IndexPriceHistoryItem(TypedDict):
    time: int
    """Time in microseconds since unix epoch"""
    value: str


class L1OrderBook(TypedDict):
    askPrice: NotRequired[str]
    askSize: NotRequired[str]
    bidPrice: NotRequired[str]
    bidSize: NotRequired[str]
    revisionId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""


class L1OrderBookSubscriptionParams(TypedDict):
    snapshot: NotRequired[bool]
    symbol: str


class L2OrderBookSubscriptionParams(TypedDict):
    group: NotRequired[str]
    """Price group for aggregation, must be a multiple of 1, 10, 100 or 1000 of the tick size. Default is the tick size."""
    snapshot: NotRequired[bool]
    symbol: str


class L2Update(TypedDict):
    group: str
    price: str
    revisionId: int
    side: "OrderSide"
    size: str
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""


class LiquidationPrice(TypedDict):
    price: NotRequired[str]
    subaccountId: int
    symbol: str


class ListingStatus(str, Enum):
    Staged = "staged"
    Listed = "listed"
    Delisted = "delisted"


Locale = Literal["en", "zh", "vi", "uk", "es"]


class LspAssignment(TypedDict):
    base: str
    id: int
    pairSymbol: str
    price: str
    quote: str
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class LspAssignmentSubscriptionParams(TypedDict):
    subaccountId: int


class LspSetting(TypedDict):
    maxAssignmentNotional: str
    maxExposureNotional: str
    symbol: str


class Margin(TypedDict):
    available: str
    """Total margin available for opening new positions"""
    bonus: str
    """Total margin bonus"""
    initial: str
    """Initial margin required to open a position"""
    liquidation: str
    """Amount of Margin required to prevent portfolio liquidations"""
    locked: str
    """Total margin locked due to open positions and open orders"""
    maintenance: str
    """Amount of Margin required to prevent partial liquidations"""
    pnl: str
    """Total unrealized PnL"""
    subaccountId: int
    total: str
    """Total margin in the account, includes unrealized PnL"""
    totalAssetValue: str
    """Total value of all assets in the account in USDT"""


class MarginSchedule(TypedDict):
    bands: List["MarginScheduleBand"]
    name: "MarginScheduleName"


class MarginScheduleBand(TypedDict):
    leverageRate: str
    """leverage rate applied in this band"""
    marginRate: str
    """Initial margin rate applied in this band"""
    positionLimit: str
    """Maximum position size for this band"""
    rebate: str
    """Initial margin rebate applied in this band"""


MarginScheduleName = Literal["A", "B", "C", "D", "E", "F", "G"]


class MarginSubscriptionParams(TypedDict):
    snapshot: bool
    snapshotInterval: "SnapshotInterval"
    subaccountId: int


class MarkReadNotificationsRequest(TypedDict):
    lastReadTime: int
    """Time in microseconds since unix epoch"""


class MarketCapHistoricData__market_cap_chart(TypedDict):
    market_cap: List[List[float]]
    volume: List[List[float]]


class MarketCapHistoricData(TypedDict):
    market_cap_chart: MarketCapHistoricData__market_cap_chart


class MarketCapResponse(TypedDict):
    market_cap_change_percentage_24h_usd: float
    market_cap_percentage_btc: float
    total_market_cap: float


class NewDepositAddressRequest(TypedDict):
    chain: str
    subaccountId: int


class NewDepositAddressResponse(TypedDict):
    address: str


class Notification(TypedDict):
    id: int
    isRead: bool
    message: str
    orderId: NotRequired[int]
    subaccountId: int
    symbol: NotRequired[str]
    time: int
    """Time in microseconds since unix epoch"""
    title: str
    type: "NotificationType"


NotificationType = Literal["announcement", "order", "price", "margin", "deposit", "withdrawal", "deleverage", "rebate", "commission", "adjustment", "airdrop", "reward", "expiration"]


class Order(TypedDict):
    arkmFeePaid: str
    """Total ARKM fee paid so far in the order"""
    avgPrice: str
    """Average price filled so far in the order"""
    brokerId: NotRequired[int]
    """The ID of the broker used to create this order. If unset or 0, this will be omitted from the response."""
    clientOrderId: NotRequired[str]
    creditFeePaid: str
    """Total fee paid via credits so far in the order"""
    executedNotional: str
    """Total notional value filled so far in the order, 0 if no fills"""
    executedSize: str
    """Total quantity filled so far in the order"""
    lastArkmFee: str
    """ARKM fee paid for the last trade, only present on taker and maker statuses"""
    lastCreditFee: str
    """Credit fee paid for the last trade, only present on taker and maker statuses"""
    lastMarginBonusFee: str
    """Margin bonus fee paid for the last trade, only present on taker and maker statuses"""
    lastPrice: str
    """Price of the last trade, only present on taker and maker statuses"""
    lastQuoteFee: str
    """Quote fee paid for the last trade, only present on taker and maker statuses"""
    lastSize: str
    """Size of the last trade, only present on taker and maker statuses"""
    lastTime: int
    """Time of the last status update on the order"""
    marginBonusFeePaid: str
    """Total fee paid via margin bonus so far in the order"""
    orderId: int
    postOnly: bool
    """If true the order is post-only"""
    price: str
    """The original price of the order"""
    quoteFeePaid: str
    """Total quote fee paid so far in the order"""
    reduceOnly: bool
    """If true the order is reduce-only"""
    revisionId: int
    """An identifier for the order's current state, unique to the pair"""
    side: "OrderSide"
    size: str
    """The original size of the order"""
    status: "OrderStatus"
    subaccountId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    triggerOrderId: NotRequired[int]
    """The ID of the trigger order that created this order, if any"""
    type: "OrderType"
    userId: int


class OrderBatchItem(TypedDict):
    clientOrderId: NotRequired[str]
    error: NotRequired["Error"]
    orderId: NotRequired[int]
    price: str
    side: "OrderSide"
    size: str
    subaccountId: int
    symbol: str
    type: "OrderType"


class OrderBook(TypedDict):
    asks: List["OrderBookEntry"]
    bids: List["OrderBookEntry"]
    group: str
    lastTime: int
    """Time in microseconds since unix epoch"""
    symbol: str


class OrderBookEntry(TypedDict):
    price: str
    size: str


class OrderHistoryWithTotalResponse(TypedDict):
    orders: List["Order"]
    total: int


class OrderSide(str, Enum):
    Buy = "buy"
    Sell = "sell"


class OrderStatus(str, Enum):
    New = "new"
    Taker = "taker"
    Booked = "booked"
    Maker = "maker"
    Cancelled = "cancelled"
    Closed = "closed"


class OrderStatusSubscriptionParams(TypedDict):
    snapshot: bool
    subaccountId: int


class OrderType(str, Enum):
    LimitGtc = "limitGtc"
    LimitIoc = "limitIoc"
    LimitFok = "limitFok"
    Market = "market"


class Pair(TypedDict):
    baseGeckoId: str
    baseImageUrl: str
    baseIsStablecoin: bool
    baseName: str
    baseSymbol: str
    marginSchedule: NotRequired[Literal["A", "B", "C", "D", "E", "F", "G"]]
    maxLeverage: NotRequired[str]
    maxPrice: str
    maxPriceScalarDown: str
    """Orders rejected if price is less than this scalar times the index price"""
    maxPriceScalarUp: str
    """Orders rejected if price is greater than this scalar times the index price"""
    maxSize: str
    minLotSize: str
    minNotional: str
    """Minimum notional (price * size) for orders"""
    minPrice: str
    minSize: str
    minTickPrice: str
    pairType: "PairType"
    quoteGeckoId: str
    quoteImageUrl: str
    quoteIsStablecoin: bool
    quoteName: str
    quoteSymbol: str
    status: "ListingStatus"
    symbol: str


class PairType(str, Enum):
    Spot = "spot"
    Perpetual = "perpetual"


class Position(TypedDict):
    averageEntryPrice: str
    base: str
    breakEvenPrice: NotRequired[str]
    initialMargin: str
    lastUpdateBaseDelta: str
    lastUpdateId: int
    lastUpdateQuoteDelta: str
    lastUpdateReason: "PositionUpdateReason"
    lastUpdateTime: int
    """Time in microseconds since unix epoch"""
    maintenanceMargin: str
    markPrice: str
    openBuyNotional: str
    openBuySize: str
    openSellNotional: str
    openSellSize: str
    pnl: str
    quote: str
    subaccountId: int
    symbol: str
    value: str


class PositionLeverage(TypedDict):
    leverage: str
    symbol: str


class PositionSubscriptionParams(TypedDict):
    snapshot: bool
    snapshotInterval: "SnapshotInterval"
    subaccountId: int


class PositionUpdate(TypedDict):
    avgEntryPrice: str
    base: str
    baseDelta: str
    id: int
    pairSymbol: str
    quote: str
    quoteDelta: str
    reason: "PositionUpdateReason"
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""


class PositionUpdateReason(str, Enum):
    Deposit = "deposit"
    Withdraw = "withdraw"
    OrderFill = "orderFill"
    FundingFee = "fundingFee"
    AssetTransfer = "assetTransfer"
    Liquidation = "liquidation"
    RealizePNL = "realizePNL"
    LspAssignment = "lspAssignment"
    Deleverage = "deleverage"
    TradingFee = "tradingFee"
    Rebate = "rebate"
    Commission = "commission"
    Adjustment = "adjustment"
    Reward = "reward"
    Expiration = "expiration"
    WithdrawalFee = "withdrawalFee"
    PerpTransfer = "perpTransfer"
    Airdrop = "airdrop"


class PriceAlert(TypedDict):
    alertPrice: str
    alertPriceType: "AlertPriceType"
    symbol: str


PublicTradesResponse = List["Trade"]


class RealizedPnl(TypedDict):
    amount: str
    assetSymbol: str
    id: int
    pairSymbol: str
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class Rebate(TypedDict):
    amount: str
    assetSymbol: str
    id: int
    subaccountId: int
    time: int
    """Time in microseconds since unix epoch"""
    userId: int


class ReferralLink(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    deletedAt: NotRequired[int]
    """Time in microseconds since unix epoch"""
    id: str
    lastUsedAt: NotRequired[int]
    """Time in microseconds since unix epoch"""
    slug: NotRequired[str]
    uses: int


ReferralLinkId = List[int]


class ReferralLinkResponse(TypedDict):
    linkId: "ReferralLinkId"


class RemoveFromWatchlistRequest(TypedDict):
    symbol: str


RewardType = Literal["trading_fee_discount", "fee_credit", "margin_bonus", "points", "tokens"]


class RewardsInfo(TypedDict):
    feeCredit: str
    feeCreditExpires: int
    """Time in microseconds since unix epoch"""
    marginBonus: str
    marginBonusExpires: int
    """Time in microseconds since unix epoch"""
    points: int
    tradingFeeDiscount: str
    tradingFeeDiscountExpires: int
    """Time in microseconds since unix epoch"""


class RewardsVoucher(TypedDict):
    actionDescription: str
    bullets: List[str]
    conditions: List["RewardsVoucherCondition"]
    conditionsJSON: str
    createdAt: int
    """Time in microseconds since unix epoch"""
    id: int
    name: str
    sequenceId: NotRequired[int]
    sequencePosition: NotRequired[int]
    status: "VoucherStatus"
    type: "RewardType"


class RewardsVoucherCondition(TypedDict):
    action: str
    completed: float
    progressSummary: str
    progressText: str
    type: "VoucherConditionType"


Secret = str


class ServerTimeResponse(TypedDict):
    serverTime: int
    """Time in microseconds since unix epoch"""


class Session(TypedDict):
    createdAt: str
    deletedAt: NotRequired[str]
    expiresAt: str
    id: int
    ipAddress: str
    ipApproved: bool
    ipInfo: "IPInfo"
    lastMfaAt: NotRequired[str]
    lastUsedAt: str
    maxExpiration: NotRequired[str]
    updatedAt: str
    userAgent: str
    userId: int


class SessionsResponse(TypedDict):
    currentSession: int
    sessions: List["Session"]


class SetPositionLeverageRequest(TypedDict):
    leverage: str
    subaccountId: NotRequired[int]
    symbol: str


class SetPriceAlertRequest(TypedDict):
    alertPrice: str
    alertPriceType: "AlertPriceType"
    alertType: "AlertType"


class SizeTimeSeries(TypedDict):
    size: str
    time: int
    """Time in microseconds since unix epoch"""


SnapshotInterval = int


class SubaccountSettingsRequest(TypedDict):
    futuresEnabled: bool
    isLsp: bool
    lspSettingUpdates: List["LspSetting"]
    payFeesInArkm: bool
    """if true and ARKM balance is sufficient fees are paid in ARKM with a discount. This is only available for USDT pairs"""
    subaccountId: int


class SubaccountWithSettings(TypedDict):
    createdAt: int
    """Time in microseconds since unix epoch"""
    futuresEnabled: bool
    """if true futures trading is enabled for the subaccount"""
    id: int
    isLsp: bool
    """if true the subaccount is a liquidity provider"""
    lspSettings: List["LspSetting"]
    name: str
    payFeesInArkm: bool
    """if true and ARKM balance is sufficient fees are paid in ARKM with a discount. This is only available for USDT pairs"""
    pinned: bool


SubscriptionParams = Union[
    "CandleSubscriptionParams",
    "TickerSubscriptionParams",
    "L2OrderBookSubscriptionParams",
    "L1OrderBookSubscriptionParams",
    "TradeSubscriptionParams",
    "BalanceSubscriptionParams",
    "PositionSubscriptionParams",
    "OrderStatusSubscriptionParams",
    "MarginSubscriptionParams",
    "TriggerOrderSubscriptionParams",
    "LspAssignmentSubscriptionParams",
]


class SwapSubmitRequest(TypedDict):
    zid: str


class SwapToken(TypedDict):
    address: str
    chainId: int
    decimals: int
    logoURI: NotRequired[str]
    name: str
    symbol: str


class SwapTradeHistoryItem(TypedDict):
    buyAmount: NotRequired[str]
    buyTokenAddress: NotRequired[str]
    buyTokenName: NotRequired[str]
    chainId: NotRequired[int]
    integratorFeeUsd: NotRequired[str]
    sellAmount: NotRequired[str]
    sellTokenAddress: NotRequired[str]
    sellTokenName: NotRequired[str]
    taker: str
    tradeTimestamp: str
    transactionHash: NotRequired[str]
    volumeUsd: int
    zid: str


class Ticker(TypedDict):
    baseSymbol: str
    fundingRate: str
    high24h: str
    indexCurrency: str
    indexPrice: str
    low24h: str
    markPrice: str
    nextFundingRate: str
    nextFundingTime: int
    """Time in microseconds since unix epoch"""
    openInterest: str
    openInterestUSD: str
    price: str
    price24hAgo: str
    productType: "PairType"
    quoteSymbol: str
    quoteVolume24h: str
    symbol: str
    usdVolume24h: str
    volume24h: str


class TickerSubscriptionParams(TypedDict):
    snapshot: NotRequired[bool]
    symbol: str


class Trade(TypedDict):
    price: str
    revisionId: int
    size: str
    symbol: str
    takerSide: "OrderSide"
    time: int
    """Time in microseconds since unix epoch"""


class TradeSubscriptionParams(TypedDict):
    snapshot: NotRequired[bool]
    symbol: str


class TradingVolume(TypedDict):
    perpVolume: str
    spotVolume: str


class TradingVolumeStats(TypedDict):
    perpMakerFees: str
    perpMakerVolume: str
    perpTakerFees: str
    perpTakerVolume: str
    perpVolume: List["SizeTimeSeries"]
    spotMakerFees: str
    spotMakerVolume: str
    spotTakerFees: str
    spotTakerVolume: str
    spotVolume: List["SizeTimeSeries"]
    totalVolume: List["SizeTimeSeries"]


class Transfer(TypedDict):
    amount: str
    """Amount of asset transferred, negative if sent, positive if received."""
    counterparty: int
    id: int
    subaccountId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""


class TriggerOrder(TypedDict):
    clientOrderId: str
    postOnly: bool
    price: str
    reduceOnly: bool
    side: "OrderSide"
    size: str
    status: "TriggerStatus"
    subaccountId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    triggerOrderId: int
    triggerPrice: str
    triggerPriceType: "TriggerPriceType"
    triggerType: "TriggerType"
    type: "OrderType"


class TriggerOrderSubscriptionParams(TypedDict):
    snapshot: bool
    subaccountId: int


class TriggerPriceType(str, Enum):
    Last = "last"
    Mark = "mark"
    Index = "index"


class TriggerStatus(str, Enum):
    Staged = "staged"
    Triggered = "triggered"
    Cancelled = "cancelled"


class TriggerType(str, Enum):
    TakeProfit = "takeProfit"
    StopLoss = "stopLoss"


UUID = str


class UpdateReferralLinkSlugRequest(TypedDict):
    slug: str


class UpdateSubaccountRequest(TypedDict):
    id: int
    name: NotRequired[str]
    pinned: NotRequired[bool]


class UpdateUserSettingsRequest(TypedDict):
    allowSequenceEmails: bool
    autogenDepositAddresses: bool
    confirmBeforePlaceOrder: bool
    hideBalances: bool
    language: "Locale"
    marginUsageThreshold: float
    notifyAnnouncements: bool
    notifyCommissions: bool
    notifyDeposits: bool
    notifyMarginUsage: bool
    notifyOrderFills: bool
    notifyPushNotifications: bool
    notifyRebates: bool
    notifySendEmail: bool
    notifyWithdrawals: bool
    tickerTapeScroll: bool
    updatesFlash: bool


class UpdateWithdrawalAddressLabelRequest(TypedDict):
    label: str


class UserDisplay(TypedDict):
    airdropKycAt: int
    """Time in microseconds since unix epoch"""
    becameVipAt: int
    """Time in microseconds since unix epoch"""
    country: NotRequired[str]
    createdAt: int
    """Time in microseconds since unix epoch"""
    dmm: bool
    email: str
    featureFlags: List[str]
    """List of feature flags enabled for the user"""
    freezeSettings: "FreezeSettings"
    id: int
    kycVerifiedAt: int
    """Time in microseconds since unix epoch"""
    pmm: bool
    requireMFA: bool
    settings: "UserSettings"
    subaccounts: List["SubaccountWithSettings"]
    username: str


class UserFees(TypedDict):
    perpMakerFee: str
    perpTakerFee: str
    spotMakerFee: str
    spotTakerFee: str


class UserPoints(TypedDict):
    points: int
    rank: int


class UserSettings(TypedDict):
    allowSequenceEmails: bool
    autogenDepositAddresses: bool
    confirmBeforePlaceOrder: bool
    hideBalances: bool
    language: NotRequired["Locale"]
    marginUsageThreshold: float
    notifyAnnouncements: bool
    notifyCommissions: bool
    notifyDeposits: bool
    notifyMarginUsage: bool
    notifyOrderFills: bool
    notifyPushNotifications: bool
    notifyRebates: bool
    notifySendEmail: bool
    notifyWithdrawals: bool
    tickerTapeScroll: bool
    updatesFlash: bool


class UserTrade(TypedDict):
    arkmFee: str
    clientOrderId: str
    orderId: int
    price: str
    quoteFee: str
    revisionId: int
    size: str
    symbol: str
    takerSide: "OrderSide"
    time: int
    """Time in microseconds since unix epoch"""
    userSide: "OrderSide"


class UserTradesWithTotalsResponse(TypedDict):
    total: int
    trades: List["UserTrade"]


class VoucherClaimRequest(TypedDict):
    voucherId: int


VoucherConditionType = Literal["deposited_usd", "deposited_token", "traded_usd", "traded_token", "basic_kyc", "mobile_installed", "mobile_traded_usd", "traded_spot_usd", "traded_perp_usd"]
VoucherStatus = Literal["not_started", "unavailable", "in_progress", "claimable", "claimed"]


class WebsocketBalancesSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.Balances]"
    confirmationId: NotRequired[str]
    data: List["Balance"]
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketBalancesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Balances]"
    params: "BalanceSubscriptionParams"


class WebsocketBalancesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Balances]"
    confirmationId: NotRequired[str]
    data: "Balance"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketCandlesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Candles]"
    params: "CandleSubscriptionParams"


class WebsocketCandlesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Candles]"
    confirmationId: NotRequired[str]
    data: "Candle"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketChannel(str, Enum):
    Errors = "errors"
    Candles = "candles"
    Ticker = "ticker"
    L2Updates = "l2_updates"
    L1Updates = "l1_updates"
    Trades = "trades"
    Balances = "balances"
    Positions = "positions"
    OrderStatuses = "order_statuses"
    Margin = "margin"
    TriggerOrders = "trigger_orders"
    LspAssignments = "lsp_assignments"
    OrdersNew = "orders/new"
    OrdersCancel = "orders/cancel"
    OrdersCancelAll = "orders/cancel/all"
    TriggerOrdersNew = "trigger_orders/new"
    TriggerOrdersCancel = "trigger_orders/cancel"
    TriggerOrdersCancelAll = "trigger_orders/cancel/all"
    Pong = "pong"
    Confirmations = "confirmations"


class WebsocketConfirmation(TypedDict):
    channel: "Literal[WebsocketChannel.Confirmations]"
    confirmationId: str


class WebsocketDataType(str, Enum):
    Update = "update"
    Snapshot = "snapshot"


class WebsocketErrorResponse__channel(str, Enum):
    Errors = "errors"


class WebsocketErrorResponse(TypedDict):
    channel: WebsocketErrorResponse__channel
    code: "ErrorCode"
    confirmationId: NotRequired[str]
    id: "ErrorId"
    message: str
    name: "ErrorName"


class WebsocketExecuteRequest(TypedDict):
    args: "WebsocketExecuteRequestArgs"
    confirmationId: NotRequired[str]
    method: "Literal[WebsocketMethod.Execute]"


WebsocketExecuteRequestArgs = Union["WebsocketOrdersNewExecutionArgs", "WebsocketOrdersCancelExecutionArgs", "WebsocketOrdersCancelAllExecutionArgs", "WebsocketTriggerOrdersNewExecutionArgs", "WebsocketTriggerOrdersCancelExecutionArgs", "WebsocketTriggerOrdersCancelAllExecutionArgs"]


class WebsocketL1UpdatesSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.L1Updates]"
    confirmationId: NotRequired[str]
    data: "L1OrderBook"
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketL1UpdatesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.L1Updates]"
    params: "L1OrderBookSubscriptionParams"


class WebsocketL1UpdatesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.L1Updates]"
    confirmationId: NotRequired[str]
    data: "L1OrderBook"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketL2UpdatesSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.L2Updates]"
    confirmationId: NotRequired[str]
    data: "OrderBook"
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketL2UpdatesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.L2Updates]"
    params: "L2OrderBookSubscriptionParams"


class WebsocketL2UpdatesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.L2Updates]"
    confirmationId: NotRequired[str]
    data: "L2Update"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketLspAssignmentsSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.LspAssignments]"
    params: "LspAssignmentSubscriptionParams"


class WebsocketLspAssignmentsUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.LspAssignments]"
    confirmationId: NotRequired[str]
    data: "LspAssignment"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketMarginSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.Margin]"
    confirmationId: NotRequired[str]
    data: "Margin"
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketMarginSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Margin]"
    params: "MarginSubscriptionParams"


class WebsocketMarginUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Margin]"
    confirmationId: NotRequired[str]
    data: "Margin"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketMethod(str, Enum):
    Ping = "ping"
    Execute = "execute"
    Subscribe = "subscribe"
    Unsubscribe = "unsubscribe"


class WebsocketOrderStatusesSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.OrderStatuses]"
    confirmationId: NotRequired[str]
    data: List["Order"]
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketOrderStatusesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.OrderStatuses]"
    params: "OrderStatusSubscriptionParams"


class WebsocketOrderStatusesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.OrderStatuses]"
    confirmationId: NotRequired[str]
    data: "Order"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketOrdersCancelAllExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersCancelAll]"
    params: "CancelAllRequest"


class WebsocketOrdersCancelAllResponse(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersCancelAll]"
    confirmationId: NotRequired[str]
    data: "CancelAllResponse"


class WebsocketOrdersCancelExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersCancel]"
    params: "CancelOrderRequest"


class WebsocketOrdersCancelResponse(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersCancel]"
    confirmationId: NotRequired[str]
    data: "CancelOrderResponse"


class WebsocketOrdersNewExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersNew]"
    params: "CreateOrderRequest"


class WebsocketOrdersNewResponse(TypedDict):
    channel: "Literal[WebsocketChannel.OrdersNew]"
    confirmationId: NotRequired[str]
    data: "CreateOrderResponse"


class WebsocketPingRequest(TypedDict):
    confirmationId: NotRequired[str]
    method: "Literal[WebsocketMethod.Ping]"


class WebsocketPongResponse(TypedDict):
    channel: "Literal[WebsocketChannel.Pong]"


class WebsocketPositionsSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.Positions]"
    confirmationId: NotRequired[str]
    data: List["Position"]
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketPositionsSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Positions]"
    params: "PositionSubscriptionParams"


class WebsocketPositionsUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Positions]"
    confirmationId: NotRequired[str]
    data: "Position"
    type: "Literal[WebsocketDataType.Update]"


WebsocketRequest = Union["WebsocketPingRequest", "WebsocketExecuteRequest", "WebsocketSubscribeRequest", "WebsocketUnsubscribeRequest"]
WebsocketResponse = Union[
    "WebsocketErrorResponse",
    "WebsocketCandlesUpdate",
    "WebsocketTickerUpdate",
    "WebsocketTickerSnapshot",
    "WebsocketL2UpdatesUpdate",
    "WebsocketL2UpdatesSnapshot",
    "WebsocketL1UpdatesUpdate",
    "WebsocketL1UpdatesSnapshot",
    "WebsocketTradesUpdate",
    "WebsocketTradesSnapshot",
    "WebsocketBalancesUpdate",
    "WebsocketBalancesSnapshot",
    "WebsocketPositionsUpdate",
    "WebsocketPositionsSnapshot",
    "WebsocketOrderStatusesUpdate",
    "WebsocketOrderStatusesSnapshot",
    "WebsocketMarginUpdate",
    "WebsocketMarginSnapshot",
    "WebsocketTriggerOrdersUpdate",
    "WebsocketTriggerOrdersSnapshot",
    "WebsocketLspAssignmentsUpdate",
    "WebsocketOrdersNewResponse",
    "WebsocketOrdersCancelResponse",
    "WebsocketOrdersCancelAllResponse",
    "WebsocketTriggerOrdersNewResponse",
    "WebsocketTriggerOrdersCancelResponse",
    "WebsocketTriggerOrdersCancelAllResponse",
    "WebsocketPongResponse",
    "WebsocketConfirmation",
]


class WebsocketSubscribeRequest(TypedDict):
    args: "WebsocketSubscribeRequestArgs"
    confirmationId: NotRequired[str]
    method: "Literal[WebsocketMethod.Subscribe]"


WebsocketSubscribeRequestArgs = Union[
    "WebsocketCandlesSubscriptionArgs",
    "WebsocketTickerSubscriptionArgs",
    "WebsocketL2UpdatesSubscriptionArgs",
    "WebsocketL1UpdatesSubscriptionArgs",
    "WebsocketTradesSubscriptionArgs",
    "WebsocketBalancesSubscriptionArgs",
    "WebsocketPositionsSubscriptionArgs",
    "WebsocketOrderStatusesSubscriptionArgs",
    "WebsocketMarginSubscriptionArgs",
    "WebsocketTriggerOrdersSubscriptionArgs",
    "WebsocketLspAssignmentsSubscriptionArgs",
]


class WebsocketTickerSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.Ticker]"
    confirmationId: NotRequired[str]
    data: "Ticker"
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketTickerSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Ticker]"
    params: "TickerSubscriptionParams"


class WebsocketTickerUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Ticker]"
    confirmationId: NotRequired[str]
    data: "Ticker"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketTradesSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.Trades]"
    confirmationId: NotRequired[str]
    data: List["Trade"]
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketTradesSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.Trades]"
    params: "TradeSubscriptionParams"


class WebsocketTradesUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.Trades]"
    confirmationId: NotRequired[str]
    data: "Trade"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketTriggerOrdersCancelAllExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersCancelAll]"
    params: "CancelAllTriggerOrdersRequest"


class WebsocketTriggerOrdersCancelAllResponse(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersCancelAll]"
    confirmationId: NotRequired[str]
    data: "CancelAllTriggerOrdersResponse"


class WebsocketTriggerOrdersCancelExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersCancel]"
    params: "CancelTriggerOrderRequest"


class WebsocketTriggerOrdersCancelResponse(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersCancel]"
    confirmationId: NotRequired[str]
    data: "CancelTriggerOrderResponse"


class WebsocketTriggerOrdersNewExecutionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersNew]"
    params: "CreateTriggerOrderRequest"


class WebsocketTriggerOrdersNewResponse(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrdersNew]"
    confirmationId: NotRequired[str]
    data: "CreateTriggerOrderResponse"


class WebsocketTriggerOrdersSnapshot(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrders]"
    confirmationId: NotRequired[str]
    data: List["TriggerOrder"]
    type: "Literal[WebsocketDataType.Snapshot]"


class WebsocketTriggerOrdersSubscriptionArgs(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrders]"
    params: "TriggerOrderSubscriptionParams"


class WebsocketTriggerOrdersUpdate(TypedDict):
    channel: "Literal[WebsocketChannel.TriggerOrders]"
    confirmationId: NotRequired[str]
    data: "TriggerOrder"
    type: "Literal[WebsocketDataType.Update]"


class WebsocketUnsubscribeRequest(TypedDict):
    args: "WebsocketSubscribeRequestArgs"
    confirmationId: NotRequired[str]
    method: "Literal[WebsocketMethod.Unsubscribe]"


class Withdrawal(TypedDict):
    amount: str
    chain: str
    confirmed: bool
    id: int
    price: str
    subaccountId: int
    symbol: str
    time: int
    """Time in microseconds since unix epoch"""
    transactionHash: NotRequired[str]
    withdrawalAddress: str


class WithdrawalAddress(TypedDict):
    address: str
    chain: str
    confirmed: bool
    createdAt: int
    """Time in microseconds since unix epoch"""
    hasBeneficiary: bool
    id: int
    label: str
    updatedAt: int
    """Time in microseconds since unix epoch"""


class WithdrawalTravelRuleBeneficiary(TypedDict):
    firstName: NotRequired[str]
    isSelf: bool
    isVasp: NotRequired[bool]
    lastName: NotRequired[str]
