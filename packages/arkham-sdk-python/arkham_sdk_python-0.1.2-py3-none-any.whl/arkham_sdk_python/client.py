"""Arkham Exchange Python Client"""

import json
import os
import urllib.parse
from typing import Any, Dict, List, Optional

import requests

try:
    from .exceptions import ArkhamError
    from .keypair import KeyPair
    from .models import *
except ImportError:
    from exceptions import ArkhamError
    from keypair import KeyPair
    from models import *


class Arkham:
    """Arkham Exchange API Client

    Provides methods to interact with the Arkham Exchange REST API

    Example:
    ```python
    from arkham_sdk_python import Arkham
    client = Arkham(api_key="your_key", api_secret="your_secret")

    # Fetch pairs information
    pairs = client.get_pairs()
    print(pairs)
    ```

    """

    def __init__(
        self,
        api_key: str = os.getenv("ARKHAM_API_KEY"),
        api_secret: str = os.getenv("ARKHAM_API_SECRET"),
        base_url: str = os.getenv("ARKHAM_API_URL", "https://arkm.com/api"),
    ):
        """Initialize the client"""
        self._key_pair = KeyPair(api_key, api_secret)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Any = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the API"""

        params = {k: v for k, v in params.items() if v is not None} if params else None
        if params:
            path += "?" + urllib.parse.urlencode(params)

        url = f"{self._base_url}{path}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        data = None
        if json_data is not None:
            data = json.dumps(json_data, separators=(",", ":"))

        headers.update(self._key_pair.sign_request(method, path, data or ""))

        response = self._session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            **kwargs,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error = ArkhamError(
                    id=error_data.get("id", 0),
                    name=error_data.get("name", "UnknownError"),
                    message=error_data.get("message", "An error occurred"),
                )
            except (ValueError, AttributeError):
                response.raise_for_status()
            raise error

        try:
            return response.json()
        except ValueError:
            return {}

    def get_account_airdrops(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Airdrop"]:
        """Get Airdrops

        Get the user's airdrops

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/airdrops", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_account_balance_updates(self, *, before: Optional[int] = None, limit: Optional[int] = None, reason: Optional["PositionUpdateReason"] = None, subaccount_id: Optional[int] = None) -> List["BalanceUpdate"]:
        """Get Balance Updates

        Get the user's balance updates

        Args:
                before (int)
                limit (int)
                reason (PositionUpdateReason)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/balance-updates", params={"before": before, "limit": limit, "reason": reason, "subaccountId": subaccount_id})  # type: ignore

    def get_balances(self, *, subaccount_id: Optional[int] = None) -> List["Balance"]:
        """Get Balances

        Get the user's current balances

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/balances", params={"subaccountId": subaccount_id})  # type: ignore

    def get_all_balances(self) -> List["Balance"]:
        """Get Balances across all subaccounts

        Get the user's current balances across all subaccounts

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/balances/all")  # type: ignore

    def get_portfolio_balance_history(self, *, end: Optional[int] = None, start: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["HistoricBalance"]:
        """Get User Subaccount Balance History

        Get the balance history for a subaccount

        Args:
                end (int): Time in microseconds since unix epoch
                start (int): Time in microseconds since unix epoch
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/balances/history", params={"end": end, "start": start, "subaccountId": subaccount_id})  # type: ignore

    def get_account_commissions(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Commission"]:
        """Get Commissions

        Get the user's commissions

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/commissions", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_deposit_addresses(self, *, chain: str, subaccount_id: Optional[int] = None) -> "DepositAddressesResponse":
        """Get Deposit Addresses

        Args:
                chain (str)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/deposit/addresses", params={"chain": chain, "subaccountId": subaccount_id})  # type: ignore

    def new_deposit_address(self, request: "NewDepositAddressRequest") -> "NewDepositAddressResponse":
        """Create Deposit Address

        Args:
                request ("NewDepositAddressRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/deposit/addresses/new", json_data=request)  # type: ignore

    def get_account_deposits(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Deposit"]:
        """Get Deposits

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/deposits", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_user_fees(self) -> "UserFees":
        """Get User Fees

        Get the user's current trading fees

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/fees")  # type: ignore

    def get_funding_rate_payments(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["FundingRatePayment"]:
        """Get Funding Rate Payments

        Get the user's funding rate payments

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/funding-rate-payments", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_position_leverage(self, *, subaccount_id: Optional[int] = None) -> List["PositionLeverage"]:
        """Get Position Limits

        Gets the user specified position leverage

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/leverage", params={"subaccountId": subaccount_id})  # type: ignore

    def set_position_leverage(self, request: "SetPositionLeverageRequest") -> None:
        """Get Position Limits

        Sets the user specified position leverage for a given pair

        Args:
                request ("SetPositionLeverageRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/leverage", json_data=request)  # type: ignore

    def get_liquidation_price(self, *, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> "LiquidationPrice":
        """Get Liquidation Price

        Get liquidation price for a perpetual position

        Args:
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/liquidation-price", params={"subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def get_account_lsp_assignments(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["LspAssignment"]:
        """Get LSP Assignments

        Get the user's lsp assignments

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/lsp-assignments", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_margin(self, *, subaccount_id: Optional[int] = None) -> "Margin":
        """Get Account Margin

        Get the user's current margin usage details

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/margin", params={"subaccountId": subaccount_id})  # type: ignore

    def get_all_margin(self) -> List["Margin"]:
        """Get Account Margin across all subaccounts

        Get the user's current margin usage details

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/margin/all")  # type: ignore

    def get_notifications(self, *, limit: Optional[int] = None, offset: Optional[int] = None, type: Optional["NotificationType"] = None) -> List["Notification"]:
        """Get Notifications

        Args:
                limit (int)
                offset (int)
                type (NotificationType)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/notifications", params={"limit": limit, "offset": offset, "type": type})  # type: ignore

    def mark_read_notifications(self, request: "MarkReadNotificationsRequest") -> str:
        """Mark Notifications Read

        Args:
                request ("MarkReadNotificationsRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/notifications/read", json_data=request)  # type: ignore

    def get_account_position_updates(self, *, before: Optional[int] = None, limit: Optional[int] = None, reason: Optional["PositionUpdateReason"] = None, subaccount_id: Optional[int] = None) -> List["PositionUpdate"]:
        """Get Position Updates

        Get the user's position updates

        Args:
                before (int)
                limit (int)
                reason (PositionUpdateReason)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/position-updates", params={"before": before, "limit": limit, "reason": reason, "subaccountId": subaccount_id})  # type: ignore

    def get_positions(self, *, subaccount_id: Optional[int] = None) -> List["Position"]:
        """Get Positions

        Get list of the current positions

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/positions", params={"subaccountId": subaccount_id})  # type: ignore

    def get_account_realized_pnl(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["RealizedPnl"]:
        """Get Realized PnL

        Get the user's realized pnl

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/realized-pnl", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_account_rebates(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Rebate"]:
        """Get Rebates

        Get the user's rebates

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/rebates", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_referral_links(self) -> List["ReferralLink"]:
        """Get Referral Links

        Get the user's referral links

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/referral-links")  # type: ignore

    def create_referral_link(self) -> "ReferralLinkResponse":
        """Create Referral Link

        Create a referral link for the user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/referral-links")  # type: ignore

    def update_referral_link_slug(self, id: str, request: "UpdateReferralLinkSlugRequest") -> None:
        """Update Referral Link Slug

        Update the slug for a referral link

        Args:
                id (str)
                request ("UpdateReferralLinkSlugRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/account/referral-links/{id}/slug", json_data=request)  # type: ignore

    def get_active_sessions(self) -> "SessionsResponse":
        """Get Active Sessions

        Get the user's active sessions

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/sessions")  # type: ignore

    def handle_delete_session(self, request: "DeleteSessionRequest") -> None:
        """Delete Session

        Delete a session for the user

        Args:
                request ("DeleteSessionRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/sessions/delete", json_data=request)  # type: ignore

    def handle_terminate_all(self) -> None:
        """Terminate All Sessions

        Terminate all sessions for the user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/sessions/terminate-all")  # type: ignore

    def get_user_settings(self) -> "UserSettings":
        """Get User Settings

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/settings")  # type: ignore

    def get_price_alert(self, *, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> "PriceAlert":
        """Get Price Alerts

        Args:
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/settings/price-alert", params={"subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def set_price_alert(self, request: "SetPriceAlertRequest", *, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> None:
        """Set Price Alert

        Args:
                request ("SetPriceAlertRequest"):
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/account/settings/price-alert", params={"subaccountId": subaccount_id, "symbol": symbol}, json_data=request)  # type: ignore

    def delete_price_alert(self, *, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> None:
        """Delete Price Alert

        Args:
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("DELETE", f"/account/settings/price-alert", params={"subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def update_user_settings(self, request: "UpdateUserSettingsRequest") -> str:
        """Update User Settings

        Args:
                request ("UpdateUserSettingsRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/settings/update", json_data=request)  # type: ignore

    def create_state_disclaimer_acknowledgement(self, request: "CreateStateDisclaimerAcknowledgementRequest") -> "CreateStateDisclaimerAcknowledgementResponse":
        """Create State Disclaimer Acknowledgement

        Acknowledge a state-specific disclaimer

        Args:
                request ("CreateStateDisclaimerAcknowledgementRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/state-disclaimer/acknowledgements", json_data=request)  # type: ignore

    def get_account_transfers(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Transfer"]:
        """Get Transfers

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/transfers", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def get_account_watchlist(self) -> List[str]:
        """Get Watchlist

        Get a list of the pairs in your watchlist

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/watchlist")  # type: ignore

    def add_to_watchlist(self, request: "AddToWatchlistRequest") -> None:
        """Add to Watchlist

        Add a pair to the watchlist

        Args:
                request ("AddToWatchlistRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/watchlist/add", json_data=request)  # type: ignore

    def remove_from__watchlist(self, request: "RemoveFromWatchlistRequest") -> None:
        """Remove from Watchlist

        Remove a pair from your watchlise

        Args:
                request ("RemoveFromWatchlistRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/watchlist/remove", json_data=request)  # type: ignore

    def account_withdraw(self, request: "AccountWithdrawRequest") -> int:
        """Account Withdraw

        Args:
                request ("AccountWithdrawRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/withdraw", json_data=request)  # type: ignore

    def account_withdraw_using_mfa(self, request: "AccountWithdrawUsingMFARequest") -> int:
        """Account Withdraw With MFA

        Args:
                request ("AccountWithdrawUsingMFARequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/withdraw/with-mfa", json_data=request)  # type: ignore

    def list_withdrawal_addresses(self) -> List["WithdrawalAddress"]:
        """List Withdrawal Addresses

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/withdrawal/addresses")  # type: ignore

    def create_withdrawal_address(self, request: "CreateWithdrawalAddressRequest") -> int:
        """Create Withdrawal Address

        Args:
                request ("CreateWithdrawalAddressRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/withdrawal/addresses", json_data=request)  # type: ignore

    def confirm_withdrawal_address(self, request: "ConfirmWithdrawalAddressRequest") -> str:
        """Confirm Withdrawal Address

        Args:
                request ("ConfirmWithdrawalAddressRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/account/withdrawal/addresses/confirm", json_data=request)  # type: ignore

    def get_withdrawal_address(self, id: int) -> "WithdrawalAddress":
        """Get Withdrawal Address

        Args:
                id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/withdrawal/addresses/{id}")  # type: ignore

    def update_withdrawal_address_label(self, id: int, request: "UpdateWithdrawalAddressLabelRequest") -> str:
        """Update Withdrawal Address Label

        Args:
                id (int)
                request ("UpdateWithdrawalAddressLabelRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/account/withdrawal/addresses/{id}", json_data=request)  # type: ignore

    def delete_withdrawal_address(self, id: int) -> str:
        """Delete Withdrawal Address

        Args:
                id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("DELETE", f"/account/withdrawal/addresses/{id}")  # type: ignore

    def get_account_withdrawals(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None) -> List["Withdrawal"]:
        """Get Withdrawals

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/account/withdrawals", params={"before": before, "limit": limit, "subaccountId": subaccount_id})  # type: ignore

    def commissions_earned(self) -> str:
        """Commission earned for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/commission-earned")  # type: ignore

    def min_arkm_last30d(self) -> str:
        """Min ARKM last 30d for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/min-arkm-last-30d")  # type: ignore

    def user_points(self) -> "UserPoints":
        """Points leaderboard for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/points")  # type: ignore

    def user_points_season1(self) -> "UserPoints":
        """Points leaderboard season 1 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/points-season-1")  # type: ignore

    def user_points_season2(self) -> "UserPoints":
        """Points leaderboard season 2 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/points-season-2")  # type: ignore

    def realized_pnl(self) -> List["SizeTimeSeries"]:
        """Realized PnL for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/realized-pnl")  # type: ignore

    def rebate_balance(self) -> str:
        """Rebate balance for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/rebate-balance")  # type: ignore

    def referral_count(self) -> int:
        """Referral count for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/referral-count")  # type: ignore

    def user_referrals_season1(self) -> int:
        """Referrals leaderboard season 1 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/referrals-season-1")  # type: ignore

    def user_referrals_season2(self) -> int:
        """Referrals leaderboard season 2 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/referrals-season-2")  # type: ignore

    def trading_volume_stats(self) -> "TradingVolumeStats":
        """Trading volume stats for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/trading-volume-stats")  # type: ignore

    def user_volume_season1(self) -> "TradingVolume":
        """Volume leaderboard season 1 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/volume-season-1")  # type: ignore

    def user_volume_season2(self) -> "TradingVolume":
        """Volume leaderboard season 2 for user

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/affiliate-dashboard/volume-season-2")  # type: ignore

    def get_airdrop_address(self) -> str:
        """Get Airdrop Address

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/airdrop")  # type: ignore

    def create_airdrop_address(self, request: "CreateAirdropAddressRequest") -> str:
        """Create Airdrop Address

        Args:
                request ("CreateAirdropAddressRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/airdrop", json_data=request)  # type: ignore

    def get_airdrop_claim(self) -> "AirdropClaim":
        """Get Airdrop Claim

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/airdrop/claim")  # type: ignore

    def api_keys_list(self) -> List["ApiKey"]:
        """Api Key List

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/api-key")  # type: ignore

    def api_key_create(self, request: "CreateApiKeyRequest") -> "ApiKeyWithSecret":
        """Api Key Create

        Args:
                request ("CreateApiKeyRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/api-key/create", json_data=request)  # type: ignore

    def fireblocks_api_keys_list(self) -> List["FireblocksApiKey"]:
        """Fireblocks Api Key List

        List all Fireblocks Network Link API keys for the authenticated user.

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/api-key/fireblocks")  # type: ignore

    def fireblocks_api_key_create(self, request: "CreateFireblocksApiKeyRequest") -> "FireblocksApiKeyWithSecret":
        """Create Fireblocks API Key

        Create a new Fireblocks Network Link API key.

        Args:
                request ("CreateFireblocksApiKeyRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/api-key/fireblocks/create", json_data=request)  # type: ignore

    def fireblocks_api_key_update(self, id: int, request: "FireblocksApiKeyUpdateRequest") -> str:
        """Update Fireblocks API Key

        Update a Fireblocks Network Link API key.

        Args:
                id (int)
                request ("FireblocksApiKeyUpdateRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/api-key/fireblocks/update/{id}", json_data=request)  # type: ignore

    def fireblocks_api_key_delete(self, id: int) -> None:
        """Delete Fireblocks API Key

        Delete a Fireblocks Network Link API key.

        Args:
                id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("DELETE", f"/api-key/fireblocks/{id}")  # type: ignore

    def api_key_update(self, id: int, request: "ApiKeyUpdateRequest") -> str:
        """Api Key Update

        Args:
                id (int)
                request ("ApiKeyUpdateRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/api-key/update/{id}", json_data=request)  # type: ignore

    def api_keys_delete(self, id: int) -> None:
        """Api Key Delete

        Args:
                id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("DELETE", f"/api-key/{id}")  # type: ignore

    def competition_opt_in_status(self, *, competition_id: Optional[int] = None) -> bool:
        """Check competition opt-in status

        Args:
                competition_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/competitions/opt-in-status", params={"competition_id": competition_id})  # type: ignore

    def get_orders(self, *, subaccount_id: Optional[int] = None) -> List["Order"]:
        """Get Orders

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders", params={"subaccountId": subaccount_id})  # type: ignore

    def get_open_order_by_client_order_id(self, *, client_order_id: Optional[str] = None, subaccount_id: Optional[int] = None) -> "Order":
        """Get Open Order By Client Order Id

        Args:
                client_order_id (str)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders/by-client-order-id", params={"clientOrderId": client_order_id, "subaccountId": subaccount_id})  # type: ignore

    def cancel_order(self, request: "CancelOrderRequest") -> "CancelOrderResponse":
        """Cancel Order

        Args:
                request ("CancelOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/orders/cancel", json_data=request)  # type: ignore

    def cancel_replace_order(self, request: "CancelReplaceOrderRequest") -> "CancelReplaceOrderResponse":
        """Cancel and Replace Order

        Args:
                request ("CancelReplaceOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/orders/cancel-replace", json_data=request)  # type: ignore

    def get_order_history(self, *, limit: Optional[int] = None, offset: Optional[int] = None, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> List["Order"]:
        """Get Order History

        Args:
                limit (int)
                offset (int)
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders/history", params={"limit": limit, "offset": offset, "subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def get_all_orders_by_client_order_id(self, *, client_order_id: Optional[str] = None, subaccount_id: Optional[int] = None) -> List["Order"]:
        """Get all order for Client Order Id

        Args:
                client_order_id (str)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders/history/by-client-order-id", params={"clientOrderId": client_order_id, "subaccountId": subaccount_id})  # type: ignore

    def get_order_history_with_total(self, *, limit: Optional[int] = None, offset: Optional[int] = None, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> "OrderHistoryWithTotalResponse":
        """Get Total Orders

        Args:
                limit (int)
                offset (int)
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders/history_offset", params={"limit": limit, "offset": offset, "subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def create_order(self, request: "CreateOrderRequest") -> "CreateOrderResponse":
        """Create Order

        Args:
                request ("CreateOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/orders/new", json_data=request)  # type: ignore

    def create_order_batch(self, request: "CreateOrdersBatchRequest") -> "CreateOrdersBatchResponse":
        """Create Multiple Orders

        Orders are processed sequentially and returned in the same order as the input requests.

        Args:
                request ("CreateOrdersBatchRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/orders/new/batch", json_data=request)  # type: ignore

    def create_simple_order(self, request: "CreateSimpleOrderRequest") -> "CreateOrderResponse":
        """Create Simple Order

        Args:
                request ("CreateSimpleOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/orders/new/simple", json_data=request)  # type: ignore

    def get_order_by_id(self, id: int, *, subaccount_id: Optional[int] = None) -> "Order":
        """Get Order By Id

        Args:
                id (int)
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/orders/{id}", params={"subaccountId": subaccount_id})  # type: ignore

    def get_alerts(self) -> List["Alert"]:
        """Get Alerts

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/alerts")  # type: ignore

    def get_announcements(self, *, locale: "Locale") -> List["Announcement"]:
        """Get Announcements

        Get announcements for a specific locale

        Args:
                locale (Locale)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/announcements", params={"locale": locale})  # type: ignore

    def get_assets(self) -> List["Asset"]:
        """Get Assets

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/assets")  # type: ignore

    def get_book(self, *, symbol: str, limit: Optional[int] = None) -> "OrderBook":
        """Get Book

        Args:
                symbol (str)
                limit (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/book", params={"limit": limit, "symbol": symbol})  # type: ignore

    def get_candles(self, *, duration: "CandleDuration", end: int, start: int, symbol: str) -> List["Candle"]:
        """Get Candles

        Args:
                duration (CandleDuration)
                end (int): Time in microseconds since unix epoch
                start (int): Time in microseconds since unix epoch
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/candles", params={"duration": duration, "end": end, "start": start, "symbol": symbol})  # type: ignore

    def get_chains(self) -> List["Blockchain"]:
        """Get Chains

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/chains")  # type: ignore

    def get_contracts(self) -> List["Ticker"]:
        """Get Contracts

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/contracts")  # type: ignore

    def get_funding_rate_history(self, *, end: int, start: int, symbol: str) -> List["FundingRateHistoryItem"]:
        """Get Funding Rate History

        Args:
                end (int): Time in microseconds since unix epoch
                start (int): Time in microseconds since unix epoch
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/funding-rate-history", params={"end": end, "start": start, "symbol": symbol})  # type: ignore

    def get_index_price(self, *, symbol: str) -> "IndexPrice":
        """Get Index Price

        Args:
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/index-price", params={"symbol": symbol})  # type: ignore

    def get_index_price_history(self, *, end: int, start: int, symbol: str) -> List["IndexPriceHistoryItem"]:
        """Get Index Price History

        Args:
                end (int): Time in microseconds since unix epoch
                start (int): Time in microseconds since unix epoch
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/index-price-history", params={"end": end, "start": start, "symbol": symbol})  # type: ignore

    def get_index_prices(self) -> List["IndexPrice"]:
        """Get Index Prices

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/index-prices")  # type: ignore

    def get_l1_book(self, *, symbol: str, limit: Optional[int] = None) -> "L1OrderBook":
        """Get L1 Book

        Args:
                symbol (str)
                limit (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/level-one-book", params={"limit": limit, "symbol": symbol})  # type: ignore

    def get_margin_schedules(self) -> List["MarginSchedule"]:
        """Get Margin Schedules

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/margin-schedules")  # type: ignore

    def get_market_cap_chart(self) -> "MarketCapHistoricData":
        """Get MarketCap Chart

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/marketcapchart")  # type: ignore

    def get_market_caps(self) -> "MarketCapResponse":
        """Get Market Caps

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/marketcaps")  # type: ignore

    def get_pair(self, *, symbol: str) -> "Pair":
        """Get Pair

        Args:
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/pair", params={"symbol": symbol})  # type: ignore

    def get_pairs(self) -> List["Pair"]:
        """Get Pairs

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/pairs")  # type: ignore

    def server_time(self) -> "ServerTimeResponse":
        """Get Server Time

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/server-time")  # type: ignore

    def get_ticker(self, *, symbol: str) -> "Ticker":
        """Get Ticker

        Args:
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/ticker", params={"symbol": symbol})  # type: ignore

    def get_tickers(self) -> List["Ticker"]:
        """Get Tickers

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/tickers")  # type: ignore

    def get_public_trades(self, *, symbol: str, before: Optional[int] = None, limit: Optional[int] = None) -> "PublicTradesResponse":
        """Get Public Trades

        Args:
                symbol (str)
                before (int)
                limit (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/public/trades", params={"before": before, "limit": limit, "symbol": symbol})  # type: ignore

    def rewards_info(self) -> "RewardsInfo":
        """Rewards info

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/rewards/info")  # type: ignore

    def vouchers(self, *, claimed: Optional[bool] = None, locale: Optional[str] = None) -> List["RewardsVoucher"]:
        """Vouchers for user

        Args:
                claimed (bool)
                locale (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/rewards/vouchers", params={"claimed": claimed, "locale": locale})  # type: ignore

    def get_subaccounts(self) -> List["SubaccountWithSettings"]:
        """Get Subaccounts

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/subaccounts")  # type: ignore

    def create_subaccount(self, request: "CreateSubaccountRequest") -> "CreateSubaccountResponse":
        """Create Subaccount

        Args:
                request ("CreateSubaccountRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/subaccounts", json_data=request)  # type: ignore

    def update_subaccount(self, request: "UpdateSubaccountRequest") -> None:
        """Update Subaccount

        Args:
                request ("UpdateSubaccountRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("PUT", f"/subaccounts", json_data=request)  # type: ignore

    def create_perp_transfer(self, request: "CreatePerpTransferRequest") -> "CreatePerpTransferResponse":
        """Create Perpetual Transfer

        Args:
                request ("CreatePerpTransferRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/subaccounts/perp-transfer", json_data=request)  # type: ignore

    def create_transfer(self, request: "CreateTransferRequest") -> "CreateTransferResponse":
        """Create Transfer

        Args:
                request ("CreateTransferRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/subaccounts/transfer", json_data=request)  # type: ignore

    def update_portfolio_settings(self, request: "SubaccountSettingsRequest") -> str:
        """Update Portfolio Settings

        Args:
                request ("SubaccountSettingsRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/subaccounts/update-settings", json_data=request)  # type: ignore

    def delete_subaccount(self, subaccount_id: int) -> None:
        """Delete Subaccount

        Deletes the specified subaccount by ID

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("DELETE", f"/subaccounts/{subaccount_id}")  # type: ignore

    def swap_price(self, *, buy_token: Optional[str] = None, chain_id: Optional[int] = None, sell_amount: Optional[str] = None, sell_token: Optional[str] = None, slippage_bps: Optional[int] = None, taker: Optional[str] = None) -> "AllowanceHolderBaseResponse":
        """Get 0x allowance holder price

        Proxies the 0x Allowance Holder price endpoint with Arkham's affiliate fee configuration.

        Args:
                buy_token (str)
                chain_id (int)
                sell_amount (str)
                sell_token (str)
                slippage_bps (int)
                taker (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/swap/price", params={"buyToken": buy_token, "chainId": chain_id, "sellAmount": sell_amount, "sellToken": sell_token, "slippageBps": slippage_bps, "taker": taker})  # type: ignore

    def swap_quote(self, *, buy_token: Optional[str] = None, chain_id: Optional[int] = None, sell_amount: Optional[str] = None, sell_token: Optional[str] = None, slippage_bps: Optional[int] = None, taker: Optional[str] = None) -> "AllowanceHolderBaseResponse":
        """Get 0x allowance holder quote

        Proxies the 0x Allowance Holder firm quote endpoint with Arkham's affiliate fee configuration.

        Args:
                buy_token (str)
                chain_id (int)
                sell_amount (str)
                sell_token (str)
                slippage_bps (int)
                taker (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/swap/quote", params={"buyToken": buy_token, "chainId": chain_id, "sellAmount": sell_amount, "sellToken": sell_token, "slippageBps": slippage_bps, "taker": taker})  # type: ignore

    def swap_submit(self, request: "SwapSubmitRequest") -> None:
        """Submit swap trade

        Record a submitted swap trade by ZID. Anonymous requests are stored without a user association when authentication is not present.

        Args:
                request ("SwapSubmitRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/swap/submit", json_data=request)  # type: ignore

    def get_swap_token_list(self) -> List["SwapToken"]:
        """Get swap token list

        Returns a list of supported tokens for the swap feature.

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/swap/token-list")  # type: ignore

    def swap_trade_history(self, *, address: Optional[str] = None, chain_id: Optional[int] = None, limit: Optional[int] = None) -> List["SwapTradeHistoryItem"]:
        """Get confirmed swap trades

        Returns confirmed swap trades for a taker address.

        Args:
                address (str)
                chain_id (int)
                limit (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/swap/trades", params={"address": address, "chainId": chain_id, "limit": limit})  # type: ignore

    def get_user_trades(self, *, before: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> List["UserTrade"]:
        """Get User Trades

        Args:
                before (int)
                limit (int)
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/trades", params={"before": before, "limit": limit, "subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def get_user_trades_with_totals(self, *, limit: Optional[int] = None, offset: Optional[int] = None, subaccount_id: Optional[int] = None, symbol: Optional[str] = None) -> "UserTradesWithTotalsResponse":
        """Get User Trades History

        Args:
                limit (int)
                offset (int)
                subaccount_id (int)
                symbol (str)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/trades/history", params={"limit": limit, "offset": offset, "subaccountId": subaccount_id, "symbol": symbol})  # type: ignore

    def get_user_trades_by_time(self, *, from_: Optional[int] = None, limit: Optional[int] = None, subaccount_id: Optional[int] = None, to: Optional[int] = None) -> List["UserTrade"]:
        """Get User Trades By Time

        Args:
                from_ (int): time from, inclusive
                limit (int)
                subaccount_id (int)
                to (int): time to, inclusive
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/trades/time", params={"from": from_, "limit": limit, "subaccountId": subaccount_id, "to": to})  # type: ignore

    def get_trigger_orders(self, *, subaccount_id: Optional[int] = None) -> List["TriggerOrder"]:
        """Get Trigger Orders

        Get all trigger orders for the authenticated user.

        Args:
                subaccount_id (int)
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/trigger-orders", params={"subaccountId": subaccount_id})  # type: ignore

    def cancel_trigger_order(self, request: "CancelTriggerOrderRequest") -> "CancelTriggerOrderResponse":
        """Cancel Trigger Order

        Args:
                request ("CancelTriggerOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/trigger-orders/cancel", json_data=request)  # type: ignore

    def cancel_all_trigger_orders(self, request: "CancelAllTriggerOrdersRequest") -> "CancelAllTriggerOrdersResponse":
        """Cancel AllTrigger Orders

        Args:
                request ("CancelAllTriggerOrdersRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/trigger-orders/cancel/all", json_data=request)  # type: ignore

    def create_trigger_order(self, request: "CreateTriggerOrderRequest") -> "CreateTriggerOrderResponse":
        """Create Trigger Order

        Args:
                request ("CreateTriggerOrderRequest"):
        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("POST", f"/trigger-orders/new", json_data=request)  # type: ignore

    def get_user(self) -> "UserDisplay":
        """Get User

        Raises:
                ArkhamError - on API error
                requests.HTTPError - on HTTP error
        """

        return self._make_request("GET", f"/user")  # type: ignore
