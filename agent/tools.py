"""Homework 1: the remaining commerce-agent tools.

The three lecture tools (`search_help_center`, `get_order`, `issue_refund`)
are implemented in agent/agent.py and are worked examples of the pattern:
check permissions first, go through agent/db.py for data, and return a
structured dict, never a prose error. Your four tools follow the same
pattern. agent/agent.py already wraps each function below as an SDK tool, so
once a function works here it works in chat with no further wiring.

Result convention (see agent/auth.py):
  - Success: a dict with "ok": True plus the payload fields named in each
    docstring.
  - Failure: {"ok": False, "error": <code>, "reason": <human-readable str>}.

Run the contract tests with: uv run pytest tests/test_hw_holes.py -k hw1
They are marked xfail and flip to passing as you implement each function.
"""

from __future__ import annotations

from typing import Any

from agents import RunContextWrapper, function_tool

from agent import db
from agent.auth import AuthContext, can_cancel_order, permission_denied
from agent.helpcenter import load_policy_docs
from agent.killswitch import kill_switch

MAX_SEARCH_LIMIT = 25
DEFAULT_ORDER_LIMIT = 20


def lookup_store_directory(
    ctx: AuthContext,
    merchant_id: int | None = None,
    include_products: bool = False,
) -> dict[str, Any]:
    """Look up merchant-to-store associations and products. Risk tier: read.

    Merchants may inspect only their own association. Support may inspect one
    merchant by id or omit merchant_id to list all merchant associations.
    Shoppers are not given this tool because the access matrix does not grant
    them merchant-directory access.

    By default, returns only merchant names, merchant ids, store ids, and
    store names. Set include_products when the caller explicitly asks for
    products. An unknown merchant returns ``not_found``; a merchant requesting
    another merchant returns ``permission_denied``.
    """
    if ctx.role == "shopper":
        return permission_denied("role 'shopper' may not view the merchant directory")
    if ctx.role == "merchant" and merchant_id is not None and merchant_id != ctx.user_id:
        return permission_denied(
            f"merchant user {ctx.user_id} may not view merchant {merchant_id}"
        )

    conn = db.connect()
    try:
        if merchant_id is not None:
            merchant = db.get_user(conn, merchant_id)
            if merchant is None or merchant.role != "merchant":
                return {
                    "ok": False,
                    "error": "not_found",
                    "reason": f"no merchant #{merchant_id}",
                }
            merchants = [merchant]
        elif ctx.role == "merchant":
            merchant = db.get_user(conn, ctx.user_id)
            merchants = [merchant] if merchant is not None else []
        else:
            merchants = db.list_users_by_role(conn, "merchant")

        payload = []
        for merchant in merchants:
            stores = []
            if merchant.store_id is not None:
                store = db.get_store(conn, merchant.store_id)
                if store is not None:
                    stores.append(
                        {
                            "store_id": store.id,
                            "name": store.name,
                        }
                    )
                    if include_products:
                        stores[-1]["products"] = [
                            {
                                "product_id": product.id,
                                "title": product.title,
                                "description": product.description,
                                "category": product.category,
                                "price_usd": product.price_usd,
                            }
                            for product in db.list_products(conn, store.id)
                        ]
            payload.append(
                {
                    "merchant_id": merchant.id,
                    "merchant_name": merchant.name,
                    "store_ids": [store["store_id"] for store in stores],
                    "stores": stores,
                }
            )
        return {"ok": True, "merchants": payload, "count": len(payload)}
    finally:
        conn.close()


@function_tool
def lookup_store_directory_tool(
    wrapper: RunContextWrapper[AuthContext],
    merchant_id: int | None = None,
    include_products: bool = False,
) -> dict[str, Any]:
    """Look up merchant store IDs and names, optionally including products.

    This is the SDK-facing version of the store-directory helper. The homework
    expects a function decorated with @function_tool in agent/tools.py, while the
    runtime registration in agent/agent.py exposes the tool to the model.
    """
    return lookup_store_directory(
        wrapper.context,
        merchant_id=merchant_id,
        include_products=include_products,
    )


def get_policy(ctx: AuthContext, policy_id: str) -> dict[str, Any]:
    """Fetch one policy doc by its exact id. Risk tier: read.

    Every role may read every policy doc (the corpus is public help-center
    content), so this tool needs no permission check.

    Args:
        ctx: The caller's auth context. Unused here, but every tool takes it.
        policy_id: An exact policy id, e.g. "cw-returns" or
            "store-juniper-home-goods-policy". Matching is exact and
            case-sensitive; ids are the `policy_id` front-matter field of the
            files in data/policies/.

    Returns:
        On success: {"ok": True, "policy_id": str, "title": str,
        "audience": str, "body": str} where body is the markdown body of the
        doc without the front matter.
        If no doc has that id: {"ok": False, "error": "not_found",
        "reason": ...} naming the id that was requested.

    Implementation notes:
        agent.helpcenter.load_policy_docs() returns every parsed doc.
    """
    for doc in load_policy_docs():
        if doc.policy_id == policy_id:
            return {
                "ok": True,
                "policy_id": doc.policy_id,
                "title": doc.title,
                "audience": doc.audience,
                "body": doc.body,
            }
    return {"ok": False, "error": "not_found", "reason": f"no policy '{policy_id}'"}


def search_products(
    ctx: AuthContext,
    query: str,
    store: str | None = None,
    max_price_usd: float | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Search the product catalog. Risk tier: read.

    Every role may search products. Matching is deterministic keyword
    matching, not semantic search: a product matches when every whitespace
    token of `query` appears case-insensitively as a substring of the
    product's title or description.

    Args:
        ctx: The caller's auth context.
        query: Free-text query. Must be non-empty after stripping whitespace;
            otherwise return {"ok": False, "error": "invalid_argument",
            "reason": ...}.
        store: Optional store filter. Matched with
            agent.db.get_store_by_name (case-insensitive name or slug). If
            given and no store matches, return {"ok": False, "error":
            "not_found", "reason": ...} naming the store string.
        max_price_usd: Optional inclusive price ceiling. If given and not
            strictly positive, return an "invalid_argument" error.
        limit: Maximum products to return. Clamp to the range
            [1, MAX_SEARCH_LIMIT]; do not error on out-of-range values.

    Returns:
        {"ok": True, "products": [...], "count": <len(products)>} where each
        product is {"product_id": int, "store_id": int, "title": str,
        "price_usd": float}. Sort matches by price_usd ascending, then by
        product_id ascending, and truncate to `limit`. No matches is still a
        success: {"ok": True, "products": [], "count": 0}.

    Implementation notes:
        agent.db.list_products(conn, store_id) gives the candidate set.
        Open the database with agent.db.connect() and close it when done.
    """
    query_tokens = query.split()
    if not query_tokens:
        return {
            "ok": False,
            "error": "invalid_argument",
            "reason": "query must not be empty",
        }
    if max_price_usd is not None and max_price_usd <= 0:
        return {
            "ok": False,
            "error": "invalid_argument",
            "reason": "max_price_usd must be positive",
        }
    result_limit = max(1, min(limit, MAX_SEARCH_LIMIT))

    conn = db.connect()
    try:
        store_id = None
        if store is not None:
            matched_store = db.get_store_by_name(conn, store)
            if matched_store is None:
                return {
                    "ok": False,
                    "error": "not_found",
                    "reason": f"no store '{store}'",
                }
            store_id = matched_store.id

        products = []
        for product in db.list_products(conn, store_id):
            searchable = f"{product.title} {product.description}".lower()
            if not all(token.lower() in searchable for token in query_tokens):
                continue
            if max_price_usd is not None and product.price_usd > max_price_usd:
                continue
            products.append(product)

        products.sort(key=lambda product: (product.price_usd, product.id))
        payload = [
            {
                "product_id": product.id,
                "store_id": product.store_id,
                "title": product.title,
                "price_usd": product.price_usd,
            }
            for product in products[:result_limit]
        ]
        return {"ok": True, "products": payload, "count": len(payload)}
    finally:
        conn.close()


def list_my_orders(ctx: AuthContext) -> dict[str, Any]:
    """List recent orders in the caller's own scope. Risk tier: read.

    Role behavior, straight from the access matrix in SPEC.md:
        - shopper: the caller's own orders.
        - merchant: the caller's store's orders (ctx.store_id).
        - support: support staff have no orders of their own and look up
          specific orders with get_order instead, so return {"ok": False,
          "error": "invalid_argument", "reason": ...} saying exactly that.

    Returns:
        For shopper and merchant: {"ok": True, "orders": [...],
        "count": <len(orders)>} where each order is
        agent.db.Order.to_public_dict() and the list holds at most
        DEFAULT_ORDER_LIMIT orders, newest first (agent.db.list_orders_for_user
        and list_orders_for_store already sort and limit this way).

    Implementation notes:
        No permission check is needed beyond the role dispatch, because the
        scope is baked into which query you run. That is the point of the
        tool: the model cannot ask for someone else's orders through it.
    """
    if ctx.role == "support":
        return {
            "ok": False,
            "error": "invalid_argument",
            "reason": "support staff have no orders of their own; use get_order instead",
        }

    conn = db.connect()
    try:
        if ctx.role == "shopper":
            orders = db.list_orders_for_user(conn, ctx.user_id, DEFAULT_ORDER_LIMIT)
        else:
            orders = db.list_orders_for_store(conn, ctx.store_id, DEFAULT_ORDER_LIMIT)
        payload = [order.to_public_dict() for order in orders]
        return {"ok": True, "orders": payload, "count": len(payload)}
    finally:
        conn.close()


def cancel_order(ctx: AuthContext, order_id: int, reason: str) -> dict[str, Any]:
    """Cancel an order. Risk tier: write.

    This is the homework's write tool, and it must enforce two independent
    rules in this order:

    1. The access matrix (scope): use agent.auth.can_cancel_order. Shoppers
       may cancel only their own orders, merchants only their own store's
       orders, support any order. On failure return
       agent.auth.permission_denied(...) with a reason naming the role and
       the order id. Scope is checked before the status rule so that an
       out-of-scope caller learns nothing about the order's state.
    2. The pre-shipment rule (facts.yaml `cancel_cutoff`): only orders whose
       status is exactly "placed" can be cancelled, for every role. If the
       order is in scope but its status is not "placed", return
       {"ok": False, "error": "not_eligible", "reason": ...} that names the
       current status and states that orders can be cancelled only before
       shipment.

    Args:
        ctx: The caller's auth context.
        order_id: The order to cancel.
        reason: Free-text reason from the user; not validated.

    Returns:
        If no order has this id: {"ok": False, "error": "not_found",
        "reason": ...}.
        On success: {"ok": True, "order_id": order_id, "status": "cancelled"}
        after persisting the new status with agent.db.set_order_status.

    Implementation notes:
        Fetch with agent.db.get_order. Note the argument order of
        can_cancel_order(ctx, order_user_id, order_store_id).

    The Module 4 kill switch is checked first (before the scope and
    status rules and before your code), so that a paused write tool touches
    nothing. It is provided; the default ("off") returns None and falls
    through to your implementation.
    """
    paused = kill_switch("cancel_order")
    if paused is not None:
        return {"ok": False, "error": "paused", "reason": paused}
    conn = db.connect()
    try:
        order = db.get_order(conn, order_id)
        if order is None:
            return {"ok": False, "error": "not_found", "reason": f"no order #{order_id}"}
        if not can_cancel_order(ctx, order.user_id, order.store_id):
            return permission_denied(
                f"role '{ctx.role}' (user {ctx.user_id}) may not cancel order #{order_id}"
            )
        if order.status != "placed":
            return {
                "ok": False,
                "error": "not_eligible",
                "reason": (
                    f"order #{order_id} has status '{order.status}'; "
                    "orders can be cancelled only before shipment"
                ),
            }
        db.set_order_status(conn, order_id, "cancelled")
        return {"ok": True, "order_id": order_id, "status": "cancelled"}
    finally:
        conn.close()


def find_order(ctx: AuthContext, query: str) -> dict[str, Any]:
    """Search the caller's orders by product name. Risk tier: read.

    Takes a natural-language query (e.g., "earmuffs I bought last week")
    and searches the authenticated user's orders for products whose name
    matches. Use fuzzy string matching (e.g., thefuzz.fuzz.partial_ratio
    or SQLite LIKE) to find orders whose product name is close to the
    query.

    Access rules: a shopper searches only the shopper's own orders, a
    merchant searches orders from the merchant's store, and support staff
    can search any orders. Use agent.db.list_orders_for_user for shoppers
    and agent.db.list_orders_for_store for merchants. For support staff,
    use agent.db.list_orders_for_user with no user filter, or search
    across all orders.

    Args:
        ctx: The caller's auth context.
        query: A natural-language description of the product.

    Returns:
        {"ok": True, "orders": [...]} with a list of matching orders
        (at most 5), each as the dict returned by agent.db. If no orders
        match, return {"ok": True, "orders": []}.
    """
    conn = db.connect()
    try:
        if ctx.role == "shopper":
            orders = db.list_orders_for_user(conn, ctx.user_id)
        elif ctx.role == "merchant":
            orders = db.list_orders_for_store(conn, ctx.store_id)
        else:
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY ordered_at DESC, id DESC"
            ).fetchall()
            orders = [db._order_from_row(row) for row in rows]

        query_terms = query.lower().split()
        matches = []
        for order in orders:
            product = conn.execute(
                "SELECT title FROM products WHERE id = ?", (order.product_id,)
            ).fetchone()
            if product is None:
                continue
            title = product["title"].lower()
            if all(term in title for term in query_terms):
                matches.append({"id": order.id, **order.to_public_dict()})
            if len(matches) == 5:
                break
        return {"ok": True, "orders": matches}
    finally:
        conn.close()
