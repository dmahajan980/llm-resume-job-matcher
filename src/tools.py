import json
from schema.tool import Schema
from src.tool_registry import ToolRegistry, ToolType, ToolParameter


registry = ToolRegistry()


@registry.register(
    description="Search an order record by its ID and return the order details",
    tool_type=ToolType.QUERY,
    parameters=[
        ToolParameter(
            name="order_id",
            description="The ID of the order to search for",
            type="string",
            required=True,
        ),
    ],
    return_type=Schema(
        type="object",
        description="The order details",
        required=["order_id", "customer", "item", "tracking"],
        properties={
            "order_id": Schema(type="string", description="The ID of the order"),
            "customer": Schema(type="string", description="The customer of the order"),
            "item": Schema(type="string", description="The item of the order"),
            "tracking": Schema(type="string", description="The tracking of the order"),
        },
    ),
)
def find_order(order_id: str) -> str:
    order = _ORDERS.get(order_id.strip().lstrip("#"))
    if order is None:
        return f"No order found with id {order_id}."

    return {
        "order_id": order_id,
        "customer": order["customer"],
        "item": order["item"],
        "tracking": order["tracking"],
    }


@registry.register(
    description="Get the shipment status for an order by its tracking number",
    tool_type=ToolType.QUERY,
    parameters=[
        ToolParameter(
            name="tracking_number",
            description="The tracking number of the order to get the shipment status for",
            type="string",
            required=True,
        ),
    ],
    return_type=Schema(
        type="object",
        description="The shipment status",
        required=["tracking_number", "status"],
        properties={
            "tracking_number": Schema(
                type="string", description="The tracking number of the order"
            ),
            "status": Schema(type="string", description="The shipment status"),
        },
    ),
)
def get_shipment_status(tracking_number: str) -> str:
    status = _SHIPMENTS.get(tracking_number)

    if status is None:
        return f"Carrier has no record of {tracking_number}."

    return {
        "tracking_number": tracking_number,
        "status": status,
    }


@registry.register(
    description="Send an email to a recipient",
    tool_type=ToolType.ACTION,
    parameters=[
        ToolParameter(
            name="to",
            description="The email address of the recipient",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="subject",
            description="The subject of the email",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="body",
            description="The body of the email",
            type="string",
            required=True,
        ),
    ],
    return_type=Schema(
        type="string",
        description="Message indicating the email was queued",
    ),
)
def send_email(to: str, subject: str, body: str) -> str:
    return f"Email queued to {to} with subject '{subject}' and {len(body)} characters."


########################################################
# Dummy Data
########################################################
_ORDERS = {
    "12345": {
        "customer": "R. Okafor",
        "item": "Solaris headphones",
        "tracking": "ZYX987",
    },
}
_SHIPMENTS = {"ZYX987": "Out for delivery, arriving today by 8pm"}
