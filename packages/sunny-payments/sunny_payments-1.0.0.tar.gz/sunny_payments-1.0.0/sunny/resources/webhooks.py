"""
Sunny Payments SDK - Webhooks Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List, Union
import hmac
import hashlib

if TYPE_CHECKING:
    from sunny.client import Sunny

from sunny.types import Webhook, WebhookEvent, ListResponse


class WebhooksResource:
    """Handle webhook registration and verification."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        url: str,
        events: List[WebhookEvent],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Webhook:
        """
        Register a new webhook endpoint.
        
        Args:
            url: The URL to send webhook events to
            events: List of events to subscribe to
            description: Optional webhook description
            metadata: Optional key-value metadata
            
        Returns:
            The created Webhook object (includes secret)
        """
        data: Dict[str, Any] = {
            "url": url,
            "events": events,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata

        return self._client.request("POST", "/webhooks", data=data)

    def retrieve(self, webhook_id: str) -> Webhook:
        """
        Retrieve a webhook by ID.
        
        Args:
            webhook_id: The webhook ID
            
        Returns:
            The Webhook object
        """
        return self._client.request("GET", f"/webhooks/{webhook_id}")

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
    ) -> ListResponse:
        """
        List all webhooks.
        
        Args:
            limit: Maximum number of webhooks to return
            offset: Number of webhooks to skip
            status: Filter by status (active, disabled)
            
        Returns:
            ListResponse with webhooks data
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status:
            params["status"] = status

        return self._client.request("GET", "/webhooks", params=params)

    def update(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Webhook:
        """
        Update a webhook.
        
        Args:
            webhook_id: The webhook ID
            url: New URL
            events: New event list
            description: New description
            status: New status (active, disabled)
            metadata: New metadata
            
        Returns:
            The updated Webhook object
        """
        data: Dict[str, Any] = {}
        if url:
            data["url"] = url
        if events:
            data["events"] = events
        if description:
            data["description"] = description
        if status:
            data["status"] = status
        if metadata:
            data["metadata"] = metadata

        return self._client.request("PUT", f"/webhooks/{webhook_id}", data=data)

    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """
        Delete a webhook.
        
        Args:
            webhook_id: The webhook ID
            
        Returns:
            Deletion confirmation
        """
        return self._client.request("DELETE", f"/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> Dict[str, Any]:
        """
        Send a test event to a webhook.
        
        Args:
            webhook_id: The webhook ID
            
        Returns:
            Test result with status
        """
        return self._client.request("POST", f"/webhooks/{webhook_id}/test")

    @staticmethod
    def verify_signature(
        payload: Union[str, bytes],
        signature: str,
        secret: str,
    ) -> bool:
        """
        Verify the signature of a webhook payload.
        
        Use this to validate that incoming webhook requests are from Sunny.
        
        Args:
            payload: The raw request body (string or bytes)
            signature: The x-sunny-signature header value
            secret: Your webhook secret (from webhook.secret)
            
        Returns:
            True if signature is valid, False otherwise
            
        Example:
            >>> @app.route('/webhooks/sunny', methods=['POST'])
            ... def handle_webhook():
            ...     payload = request.data
            ...     signature = request.headers.get('x-sunny-signature')
            ...     
            ...     if not WebhooksResource.verify_signature(payload, signature, WEBHOOK_SECRET):
            ...         return 'Invalid signature', 400
            ...     
            ...     event = request.json
            ...     # Process event...
            ...     return 'OK', 200
        """
        try:
            if isinstance(payload, str):
                payload_bytes = payload.encode("utf-8")
            else:
                payload_bytes = payload

            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()

            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
