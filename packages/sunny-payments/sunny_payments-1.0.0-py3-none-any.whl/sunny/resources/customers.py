"""
Sunny Payments SDK - Customers Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from sunny.client import Sunny

from sunny.types import Customer, ListResponse


class CustomersResource:
    """Handle customer operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Customer:
        """
        Create a new customer.
        
        Args:
            email: Customer email address
            name: Optional customer name
            phone: Optional phone number
            metadata: Optional key-value metadata
            
        Returns:
            The created Customer object
        """
        data: Dict[str, Any] = {"email": email}
        if name:
            data["name"] = name
        if phone:
            data["phone"] = phone
        if metadata:
            data["metadata"] = metadata

        return self._client.request("POST", "/customers", data=data)

    def retrieve(self, customer_id: str) -> Customer:
        """
        Retrieve a customer by ID.
        
        Args:
            customer_id: The customer ID
            
        Returns:
            The Customer object
        """
        return self._client.request("GET", f"/customers/{customer_id}")

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        email: Optional[str] = None,
    ) -> ListResponse:
        """
        List all customers.
        
        Args:
            limit: Maximum number of customers to return
            offset: Number of customers to skip
            email: Filter by email address
            
        Returns:
            ListResponse with customers data
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if email:
            params["email"] = email

        return self._client.request("GET", "/customers", params=params)

    def update(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Customer:
        """
        Update a customer.
        
        Args:
            customer_id: The customer ID
            email: New email address
            name: New name
            phone: New phone number
            metadata: New metadata
            
        Returns:
            The updated Customer object
        """
        data: Dict[str, Any] = {}
        if email:
            data["email"] = email
        if name:
            data["name"] = name
        if phone:
            data["phone"] = phone
        if metadata:
            data["metadata"] = metadata

        return self._client.request("PATCH", f"/customers/{customer_id}", data=data)

    def delete(self, customer_id: str) -> Dict[str, Any]:
        """
        Delete a customer.
        
        Args:
            customer_id: The customer ID
            
        Returns:
            Deletion confirmation
        """
        return self._client.request("DELETE", f"/customers/{customer_id}")
