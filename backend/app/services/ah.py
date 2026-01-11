"""Albert Heijn API integration service."""
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

AH_BASE_URL = "https://api.ah.nl"
AH_AUTH_URL = f"{AH_BASE_URL}/mobile-auth/v1/auth/token"
AH_SEARCH_URL = f"{AH_BASE_URL}/mobile-services/product/search/v2"
AH_SHOPPINGLIST_URL = f"{AH_BASE_URL}/mobile-services/shoppinglist/v2/items"

DEFAULT_HEADERS = {
    "User-Agent": "Appie/8.22.3",
    "Content-Type": "application/json",
    "X-Application": "AHWEBSHOP",
}


@dataclass
class AHTokens:
    """AH authentication tokens."""
    access_token: str
    refresh_token: str
    expires_at: datetime


@dataclass
class AHProduct:
    """AH product info."""
    product_id: int
    title: str
    price: float | None = None
    image_url: str | None = None


@dataclass
class SyncResult:
    """Result of syncing an item to AH."""
    item_name: str
    status: str  # "ok", "not_found", "error"
    ah_product: str | None = None
    error: str | None = None


class AHService:
    """Service for Albert Heijn API integration."""

    def __init__(self):
        self.settings = get_settings()
        self._tokens: AHTokens | None = None
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self._tokens and datetime.utcnow() < self._tokens.expires_at:
            return self._tokens.access_token

        # Need to login or refresh
        if self._tokens:
            try:
                await self._refresh_token()
                return self._tokens.access_token
            except Exception as e:
                logger.warning(f"Token refresh failed, re-authenticating: {e}")

        await self._authenticate()
        return self._tokens.access_token

    async def _authenticate(self) -> None:
        """Authenticate with AH API using email/password."""
        if not self.settings.ah_email or not self.settings.ah_password:
            raise ValueError("AH credentials not configured. Set AH_EMAIL and AH_PASSWORD.")

        # Step 1: Get anonymous token first
        anon_response = await self._client.post(
            f"{AH_BASE_URL}/mobile-auth/v1/auth/token/anonymous",
            headers=DEFAULT_HEADERS,
            json={"clientId": "appie"}
        )
        anon_response.raise_for_status()
        anon_data = anon_response.json()
        anon_token = anon_data.get("access_token")

        # Step 2: Login with credentials
        login_response = await self._client.post(
            f"{AH_AUTH_URL}/password",
            headers={
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {anon_token}",
            },
            json={
                "username": self.settings.ah_email,
                "password": self.settings.ah_password,
                "clientId": "appie",
            }
        )
        login_response.raise_for_status()
        data = login_response.json()

        self._tokens = AHTokens(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600) - 60),
        )
        logger.info("Successfully authenticated with AH API")

    async def _refresh_token(self) -> None:
        """Refresh the access token."""
        if not self._tokens:
            raise ValueError("No tokens to refresh")

        response = await self._client.post(
            f"{AH_AUTH_URL}/refresh",
            headers=DEFAULT_HEADERS,
            json={
                "refreshToken": self._tokens.refresh_token,
                "clientId": "appie",
            }
        )
        response.raise_for_status()
        data = response.json()

        self._tokens = AHTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self._tokens.refresh_token),
            expires_at=datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600) - 60),
        )
        logger.info("Successfully refreshed AH token")

    async def search_product(self, query: str) -> AHProduct | None:
        """Search for a product and return the best match."""
        token = await self._get_access_token()

        response = await self._client.get(
            AH_SEARCH_URL,
            headers={
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {token}",
            },
            params={
                "query": query,
                "sortOn": "RELEVANCE",
                "size": 1,
            }
        )
        response.raise_for_status()
        data = response.json()

        products = data.get("products", [])
        if not products:
            return None

        product = products[0]
        return AHProduct(
            product_id=product["webshopId"],
            title=product["title"],
            price=product.get("priceBeforeBonus"),
            image_url=product.get("images", [{}])[0].get("url") if product.get("images") else None,
        )

    async def add_to_shopping_list(self, product_id: int, quantity: int = 1) -> bool:
        """Add a product to the AH shopping list."""
        token = await self._get_access_token()

        response = await self._client.patch(
            AH_SHOPPINGLIST_URL,
            headers={
                **DEFAULT_HEADERS,
                "Authorization": f"Bearer {token}",
            },
            json={
                "items": [{
                    "productId": product_id,
                    "quantity": quantity,
                    "type": "SHOPPABLE",
                }]
            }
        )
        response.raise_for_status()
        return True

    async def sync_items(self, items: list[dict]) -> list[SyncResult]:
        """Sync a list of items to AH shopping list.

        Args:
            items: List of dicts with 'name' and 'qty' keys

        Returns:
            List of SyncResult for each item
        """
        results = []

        for item in items:
            name = item.get("name", "")
            qty = int(item.get("qty", 1))

            try:
                # Search for the product
                product = await self.search_product(name)

                if not product:
                    results.append(SyncResult(
                        item_name=name,
                        status="not_found",
                    ))
                    continue

                # Add to shopping list
                await self.add_to_shopping_list(product.product_id, qty)

                results.append(SyncResult(
                    item_name=name,
                    status="ok",
                    ah_product=product.title,
                ))

            except Exception as e:
                logger.error(f"Failed to sync item '{name}': {e}")
                results.append(SyncResult(
                    item_name=name,
                    status="error",
                    error=str(e),
                ))

        return results

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


# Singleton instance
_ah_service: AHService | None = None


def get_ah_service() -> AHService:
    """Get the AH service singleton."""
    global _ah_service
    if _ah_service is None:
        _ah_service = AHService()
    return _ah_service
