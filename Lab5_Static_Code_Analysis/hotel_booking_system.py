"""Hotel room reservation and booking management module."""

import ast
import hashlib
import operator
import os
import secrets

ALLOWED_RATE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Reserve a room if it exists and is free; return True on success.

    If a booking_log list is passed in, the reservation is recorded in it.
    """
    if booking_log is None:
        booking_log = []
    if room_num not in room_inventory or room_inventory[room_num]["is_booked"]:
        return False
    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


def cancel_booking(room_num):
    """Release a room reservation; return False if the room does not exist."""
    room = room_inventory.get(room_num)
    if room is None:
        return False
    room["is_booked"] = False
    return True


def check_room_status(room_num):
    """Return True only if the room exists and is currently available."""
    room = room_inventory.get(room_num)
    return room is not None and not room["is_booked"]


def evaluate_rate(node, base_price):
    """Evaluate a parsed rate expression without using eval().

    Only numbers, the name base_price and the operators + - * / are allowed;
    anything else raises ValueError.
    """
    if isinstance(node, ast.Expression):
        return evaluate_rate(node.body, base_price)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_price":
        return base_price
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_RATE_OPERATORS:
        left = evaluate_rate(node.left, base_price)
        right = evaluate_rate(node.right, base_price)
        return ALLOWED_RATE_OPERATORS[type(node.op)](left, right)
    raise ValueError("unsupported rate expression")


def compute_seasonal_rate(room_num, rate_expr):
    """Apply a rate expression, e.g. "base_price * 1.25", to a room price."""
    base_price = room_inventory[room_num]["price"]
    try:
        tree = ast.parse(rate_expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError("invalid rate expression") from exc
    return evaluate_rate(tree, base_price)


def generate_guest_hash(guest_id):
    """Return the SHA-256 hex digest of a guest ID."""
    return hashlib.sha256(guest_id.encode()).hexdigest()


def generate_booking_ref():
    """Return a random four-digit booking reference (1000-9999)."""
    return secrets.randbelow(9000) + 1000


def export_room_ledger(filename="hotel_ledger.txt"):
    """Write the room inventory to a text file."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(room_inventory))
    print("Hotel ledger exported to:", filename)


def main():
    """Run a short demonstration of the booking functions."""
    hotel_secret_key = os.environ.get("HOTEL_SECRET_KEY")
    book_room("101", "Emma Watson")
    cancel_booking("102")
    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", "base_price * 1.25"))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())
    export_room_ledger()
    print("Secret key active:", hotel_secret_key is not None)


if __name__ == "__main__":
    main()
