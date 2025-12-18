"""
License validation module for Aigie SDK.

Validates license keys with the Kytte licensing server and
reports usage telemetry from self-hosted installations.
"""

import asyncio
import logging
import platform
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class LicenseError(Exception):
    """Raised when license validation fails."""
    pass


class LicenseExpiredError(LicenseError):
    """Raised when license has expired."""
    pass


class LicenseRevokedError(LicenseError):
    """Raised when license has been revoked."""
    pass


class LicenseLimitExceededError(LicenseError):
    """Raised when license limits are exceeded."""
    pass


@dataclass
class LicenseInfo:
    """License information returned from validation."""
    valid: bool
    tier: Optional[str] = None
    max_seats: int = 0
    max_traces_per_month: int = 0
    max_projects: int = 0
    features: Dict[str, bool] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    error: Optional[str] = None

    @property
    def is_unlimited(self) -> bool:
        """Check if license has unlimited limits (enterprise)."""
        return self.max_traces_per_month < 0


@dataclass
class UsageSummary:
    """Current usage summary."""
    traces_this_month: int = 0
    traces_remaining: int = -1
    spans_this_month: int = 0
    active_users: int = 0
    api_calls_this_month: int = 0


@dataclass
class UsageMetrics:
    """Usage metrics to report."""
    traces_count: int = 0
    spans_count: int = 0
    active_users: int = 0
    api_calls: int = 0


class LicenseValidator:
    """
    Validates Aigie tokens with the Aigie licensing server.

    Usage:
        validator = LicenseValidator(
            aigie_token="kytte_lic_pro_xxx"
        )
        license_info = await validator.validate()
        if not license_info.valid:
            raise LicenseError(license_info.error)

    Or simply set AIGIE_TOKEN environment variable and use the SDK.
    """

    DEFAULT_LICENSE_SERVER = "https://licensing-server-790000401149.us-central1.run.app"
    CACHE_TTL = 3600  # 1 hour cache for valid licenses
    HEARTBEAT_INTERVAL = 3600  # 1 hour between heartbeats
    USAGE_REPORT_INTERVAL = 86400  # 24 hours between usage reports

    def __init__(
        self,
        aigie_token: str,
        license_server_url: Optional[str] = None,
        installation_id: Optional[str] = None,
        enable_telemetry: bool = True,
        # Backwards compatibility
        license_key: Optional[str] = None,
    ):
        """
        Initialize the license validator.

        Args:
            aigie_token: Your Aigie token (get one at https://app.aigie.io)
            license_server_url: URL of the licensing server (uses default if not provided)
            installation_id: Unique ID for this installation (auto-generated if not provided)
            enable_telemetry: Whether to report usage telemetry
            license_key: Deprecated, use aigie_token instead
        """
        # Support both aigie_token and legacy license_key
        self.aigie_token = aigie_token or license_key
        if not self.aigie_token:
            raise ValueError("aigie_token is required")
        self.license_server_url = (license_server_url or self.DEFAULT_LICENSE_SERVER).rstrip("/")
        self.installation_id = installation_id or self._generate_installation_id()
        self.enable_telemetry = enable_telemetry

        # Cached license info
        self._license_info: Optional[LicenseInfo] = None
        self._usage_summary: Optional[UsageSummary] = None
        self._cache_expires_at: Optional[datetime] = None

        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._usage_report_task: Optional[asyncio.Task] = None

        # Usage tracking
        self._local_usage = UsageMetrics()

        # HTTP client
        self._client: Optional[httpx.AsyncClient] = None

    def _generate_installation_id(self) -> str:
        """Generate a unique installation ID."""
        # Use a combination of machine info and random UUID
        try:
            machine_id = platform.node()
        except Exception:
            machine_id = "unknown"
        return f"{machine_id}-{uuid.uuid4().hex[:8]}"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the validator and stop background tasks."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._usage_report_task:
            self._usage_report_task.cancel()
            try:
                await self._usage_report_task
            except asyncio.CancelledError:
                pass

        if self._client:
            await self._client.aclose()
            self._client = None

    async def validate(self, force: bool = False) -> LicenseInfo:
        """
        Validate the license key with the licensing server.

        Args:
            force: Force validation even if cached

        Returns:
            LicenseInfo with validation result

        Raises:
            LicenseError: If license is invalid
            LicenseExpiredError: If license has expired
            LicenseRevokedError: If license has been revoked
        """
        # Check cache
        if not force and self._is_cache_valid():
            return self._license_info

        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.license_server_url}/api/v1/licenses/validate",
                json={
                    "license_key": self.aigie_token,
                    "installation_id": self.installation_id,
                }
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("valid"):
                error = data.get("error", "License validation failed")
                if "expired" in error.lower():
                    raise LicenseExpiredError(error)
                elif "revoked" in error.lower():
                    raise LicenseRevokedError(error)
                else:
                    raise LicenseError(error)

            # Parse license info
            license_data = data.get("license", {})
            expires_at = None
            if license_data.get("expires_at"):
                try:
                    expires_at = datetime.fromisoformat(
                        license_data["expires_at"].replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            self._license_info = LicenseInfo(
                valid=True,
                tier=license_data.get("tier"),
                max_seats=license_data.get("max_seats", 0),
                max_traces_per_month=license_data.get("max_traces_per_month", 0),
                max_projects=license_data.get("max_projects", 0),
                features=license_data.get("features", {}),
                expires_at=expires_at,
            )

            # Parse usage summary
            usage_data = data.get("usage", {})
            self._usage_summary = UsageSummary(
                traces_this_month=usage_data.get("traces_this_month", 0),
                traces_remaining=usage_data.get("traces_remaining", -1),
                spans_this_month=usage_data.get("spans_this_month", 0),
                active_users=usage_data.get("active_users", 0),
                api_calls_this_month=usage_data.get("api_calls_this_month", 0),
            )

            # Update cache
            self._cache_expires_at = datetime.utcnow() + timedelta(seconds=self.CACHE_TTL)

            logger.info(f"License validated: tier={self._license_info.tier}")
            return self._license_info

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                raise LicenseExpiredError("License expired or payment required")
            raise LicenseError(f"License validation failed: {e}")
        except (httpx.RequestError, httpx.TimeoutException) as e:
            # Network error - check if we have cached info
            if self._license_info and self._license_info.valid:
                logger.warning(f"License server unreachable, using cached info: {e}")
                return self._license_info
            raise LicenseError(f"Cannot reach license server: {e}")

    def _is_cache_valid(self) -> bool:
        """Check if cached license info is still valid."""
        if not self._license_info or not self._cache_expires_at:
            return False
        return datetime.utcnow() < self._cache_expires_at

    async def check_feature(self, feature: str) -> bool:
        """
        Check if a feature is available in the current license.

        Args:
            feature: Feature name to check

        Returns:
            True if feature is available
        """
        if not self._license_info:
            await self.validate()

        return self._license_info.features.get(feature, False)

    def is_within_limits(self, metric: str, value: int) -> bool:
        """
        Check if a usage metric is within license limits.

        Args:
            metric: Metric name (e.g., "traces", "seats", "projects")
            value: Current value

        Returns:
            True if within limits
        """
        if not self._license_info:
            return False

        limits = {
            "traces": self._license_info.max_traces_per_month,
            "seats": self._license_info.max_seats,
            "projects": self._license_info.max_projects,
        }

        limit = limits.get(metric, 0)
        if limit < 0:  # Unlimited
            return True

        return value <= limit

    def track_usage(
        self,
        traces: int = 0,
        spans: int = 0,
        api_calls: int = 0,
    ):
        """
        Track local usage for periodic reporting.

        Args:
            traces: Number of traces created
            spans: Number of spans created
            api_calls: Number of API calls made
        """
        self._local_usage.traces_count += traces
        self._local_usage.spans_count += spans
        self._local_usage.api_calls += api_calls

    async def report_usage(self) -> bool:
        """
        Report accumulated usage to the licensing server.

        Returns:
            True if report was successful
        """
        if not self.enable_telemetry:
            return True

        if (
            self._local_usage.traces_count == 0 and
            self._local_usage.spans_count == 0 and
            self._local_usage.api_calls == 0
        ):
            return True

        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.license_server_url}/api/v1/licenses/usage",
                json={
                    "license_key": self.aigie_token,
                    "installation_id": self.installation_id,
                    "metrics": {
                        "traces_count": self._local_usage.traces_count,
                        "spans_count": self._local_usage.spans_count,
                        "active_users": self._local_usage.active_users,
                        "api_calls": self._local_usage.api_calls,
                    },
                    "sdk_version": self._get_sdk_version(),
                    "python_version": platform.python_version(),
                }
            )
            response.raise_for_status()

            # Reset local usage after successful report
            self._local_usage = UsageMetrics()
            logger.debug("Usage report sent successfully")
            return True

        except Exception as e:
            logger.warning(f"Failed to report usage: {e}")
            return False

    async def send_heartbeat(self) -> bool:
        """
        Send heartbeat to licensing server.

        Returns:
            True if heartbeat was successful
        """
        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.license_server_url}/api/v1/licenses/heartbeat",
                json={
                    "license_key": self.aigie_token,
                    "installation_id": self.installation_id,
                }
            )
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            if status == "revoked":
                raise LicenseRevokedError("License has been revoked")
            if status == "expired":
                raise LicenseExpiredError("License has expired")

            # Update features and limits from heartbeat
            if self._license_info:
                self._license_info.features = data.get("features", self._license_info.features)

            logger.debug("Heartbeat sent successfully")
            return True

        except (LicenseRevokedError, LicenseExpiredError):
            raise
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")
            return False

    async def start_background_tasks(self):
        """Start background tasks for heartbeat and usage reporting."""
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        if self._usage_report_task is None and self.enable_telemetry:
            self._usage_report_task = asyncio.create_task(self._usage_report_loop())

    async def _heartbeat_loop(self):
        """Background loop for sending heartbeats."""
        while True:
            try:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                await self.send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def _usage_report_loop(self):
        """Background loop for reporting usage."""
        while True:
            try:
                await asyncio.sleep(self.USAGE_REPORT_INTERVAL)
                await self.report_usage()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Usage report error: {e}")

    def _get_sdk_version(self) -> str:
        """Get the SDK version."""
        try:
            from . import __version__
            return __version__
        except Exception:
            return "unknown"

    @property
    def license_info(self) -> Optional[LicenseInfo]:
        """Get cached license info."""
        return self._license_info

    @property
    def usage_summary(self) -> Optional[UsageSummary]:
        """Get cached usage summary."""
        return self._usage_summary

    @property
    def tier(self) -> Optional[str]:
        """Get license tier."""
        return self._license_info.tier if self._license_info else None

    @property
    def features(self) -> Dict[str, bool]:
        """Get available features."""
        return self._license_info.features if self._license_info else {}
