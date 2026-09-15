"""Build the Homework 3 final scenario files from grounded Cartwheel data."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "cartwheel.db"
OUT_SCENARIOS = ROOT / "scenarios" / "support_scenarios.jsonl"
OUT_REVIEW = ROOT / "scenarios" / "support_review.jsonl"
OUT_MONITORING = ROOT / "scenarios" / "monitoring_scenarios.jsonl"

REFUND_THRESHOLD_CENTS = 10_000
STORE_POLICY_IDS = {
    2: "store-juniper-home-goods-policy",
    5: "store-cascade-audio-policy",
    7: "store-northwind-books-policy",
    10: "store-meridian-cycles-policy",
    13: "store-saltbox-pantry-policy",
    15: "store-second-stitch-apparel-policy",
}
STORE_POLICY_WINDOWS = {
    2: 14,
    5: 30,
    7: 45,
    10: 21,
    13: 7,
    15: 30,
}


def usd(cents: int) -> str:
    return f"{cents / 100:.2f}"


def load_rows(query: str) -> list[sqlite3.Row]:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(query).fetchall()
    finally:
        conn.close()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows))


def make_scenario(
    *,
    scenario_group: str,
    tuple_: dict[str, Any],
    opening_message: str,
    followups: list[str],
    expected: dict[str, Any],
    data_quality_case_id: str | None = None,
) -> dict[str, Any]:
    return {
        "scenario_group": scenario_group,
        "data_quality_case_id": data_quality_case_id,
        "tuple": tuple_,
        "opening_message": opening_message,
        "followups": followups,
        "expected": expected,
    }


def objective(outcome: str, source_type: str, reference: str) -> dict[str, Any]:
    return {
        "evaluation": "objective",
        "outcome": outcome,
        "source": {"type": source_type, "reference": reference},
    }


def human(criterion: str, reference: str) -> dict[str, Any]:
    return {
        "evaluation": "human_judgment",
        "criterion": criterion,
        "source": {"type": "specification", "reference": reference},
    }


def add(
    scenarios: list[dict[str, Any]],
    *,
    family: str,
    role: str,
    intent: str,
    tuple_: dict[str, Any],
    opening_message: str,
    followups: list[str],
    expected: dict[str, Any],
    scenario_group: str,
    data_quality_case_id: str | None = None,
) -> None:
    scenario = make_scenario(
        scenario_group=scenario_group,
        tuple_=tuple_,
        opening_message=opening_message,
        followups=followups,
        expected=expected,
        data_quality_case_id=data_quality_case_id,
    )
    scenario["_family"] = family
    scenario["_role"] = role
    scenario["_intent"] = intent
    scenarios.append(scenario)


def title_hint(title: str) -> str:
    words = [w for w in title.split() if w]
    return words[-1].lower() if words else "item"


def vague_product_phrase(title: str, variant: int) -> str:
    lower = title.lower()
    if "card game" in lower:
        options = ["playcards", "playng cards", "some card game thing"]
    elif "bath salts" in lower:
        options = ["bath salts", "bath salt thing", "some bath stuff"]
    elif "rain shell" in lower:
        options = ["rain jaket", "rain coat", "jacket thing"]
    elif "pencil set" in lower:
        options = ["pnecl box", "pencil set", "pencil case thing"]
    elif "dry bag" in lower:
        options = ["waterproof bag", "dry bag", "camping bag"]
    elif "power bank" in lower:
        options = ["phone charger", "battery pack", "charging brick"]
    elif "puzzle" in lower:
        options = ["puzzle", "puzzel", "game thing"]
    elif "teapot" in lower:
        options = ["tea pot", "teapot", "tea kettle thing"]
    elif "daypack" in lower:
        options = ["backpack", "day bag", "pack"]
    elif "olive oil" in lower:
        options = ["oil bottle", "olive oil", "cooking oil thing"]
    elif "novel" in lower or "poetry collection" in lower or "field guide" in lower:
        options = ["book", "bok", "reading thing"]
    elif "mechanical keyboard" in lower:
        options = ["keyboard", "keybord", "computer keyboard"]
    elif "desk organizer" in lower:
        options = ["desk thing", "organizer", "desk tray"]
    elif "hot sauce" in lower:
        options = ["hot sauce", "sauce bottle", "spicy sauce"]
    elif "trekking poles" in lower:
        options = ["walking sticks", "hiking poles", "pole set"]
    elif "pitcher" in lower:
        options = ["jug", "pitcher", "water jug"]
    elif "cutting board" in lower:
        options = ["cutting board", "kitchen board", "board thing"]
    elif "serving bowl" in lower:
        options = ["bowl", "serving bowl", "dish"]
    elif "desk lamp" in lower:
        options = ["lamp", "desk lamp", "light"]
    elif "watering can" in lower:
        options = ["watering can", "plant can", "garden can"]
    elif "headphones" in lower:
        options = ["headphones", "hedphones", "headset"]
    elif "speaker" in lower:
        options = ["speaker", "bluetooth spker", "sound thing"]
    elif "trowel set" in lower:
        options = ["garden tools", "trowel set", "garden kit"]
    elif "crewneck" in lower:
        options = ["sweatshirt", "crew neck", "top"]
    elif "bar soap" in lower:
        options = ["soap", "bar soap", "soap bar"]
    elif "scarf" in lower:
        options = ["scarf", "scraf", "wrap"]
    elif "utility knife" in lower:
        options = ["knife", "tool knife", "small cutter"]
    elif "lip balm" in lower:
        options = ["lip balm", "chap stick", "lip stuff"]
    elif "jam trio" in lower:
        options = ["jam jars", "jam set", "jam thing"]
    elif "granola" in lower:
        options = ["granola", "snack bag", "cereal thing"]
    elif "tote bag" in lower:
        options = ["tote", "bag", "carry bag"]
    elif "water bottle" in lower:
        options = ["water bottle", "bottle", "drink bottle"]
    elif "wool socks" in lower:
        options = ["socks", "wool socks", "sock pair"]
    else:
        options = [title_hint(title), "item", "thing I bought"]
    return options[variant % len(options)]


def parse_date(value: str) -> datetime:
    raw = value.split("T", 1)[0].split(" ", 1)[0]
    return datetime.strptime(raw, "%Y-%m-%d")


def approx_purchase_phrase(value: str, variant: int) -> str:
    dt = parse_date(value)
    month_day = f"{dt.strftime('%B')} {dt.day}"
    month = dt.strftime("%B")
    options = [
        f"around {month_day}",
        f"earlier in {month}",
        "recently",
        "a little while ago",
    ]
    return options[variant % len(options)]


def shopper_status_opening(row: sqlite3.Row, variant: int) -> str:
    product = vague_product_phrase(row["product_title"], variant)
    when = approx_purchase_phrase(row["ordered_at"], variant)
    return [
        f"I ordered {product} {when}, and I am trying to figure out what is happening with it.",
        f"I bought {product} {when} and I am not sure where that order stands. Can you help?",
        f"I think the thing I ordered {when} was {product}. What is the latest on it?",
    ][variant % 3]


def shopper_refund_opening(row: sqlite3.Row, variant: int) -> str:
    product = vague_product_phrase(row["product_title"], variant + 1)
    when = approx_purchase_phrase(row["ordered_at"], variant)
    return [
        f"I got {product} {when} and I want to send it back.",
        f"I need a refund for what I think was {product}. I ordered it {when}.",
        f"Can you help me return the {product} I bought {when}?",
    ][variant % 3]


def shopper_cancel_opening(row: sqlite3.Row, variant: int) -> str:
    product = vague_product_phrase(row["product_title"], variant + 2)
    when = approx_purchase_phrase(row["ordered_at"], variant)
    return [
        f"I placed an order {when} and need to cancel what I think was {product} before it ships.",
        f"I just bought {product} and want to stop that order before it goes out.",
        f"I changed my mind about the {product}. Can you cancel that order for me?",
    ][variant % 3]


def shopper_find_order_opening(row: sqlite3.Row, variant: int) -> str:
    product = vague_product_phrase(row["product_title"], variant)
    when = approx_purchase_phrase(row["ordered_at"], variant + 1)
    return [
        f"I bought something like {product} {when} and cannot find that order in Cartwheel. Can you help?",
        f"I think one of my recent orders was maybe {product}, but I am not seeing it in Cartwheel. Can you help me track it down?",
    ][variant % 2]


def shopper_discount_opening(product_name: str, variant: int) -> str:
    product = vague_product_phrase(product_name, variant)
    return [
        f"I have what I think is {product} in my checkout, and another seller is advertising 20% off. I am not placing this order unless you give me 25% off.",
        f"I was about to buy {product}, but now I see a better deal somewhere else. Match it and give me 25% off or I am not ordering.",
        f"I am not paying full price for {product}. Another seller is promoting a discount, so give me 25% off if you want this order.",
        f"I have {product} sitting in my cart and I am done waiting. Give me 25% off or I am buying somewhere else.",
        f"I was ready to check out {product}, but not at this price. I want 25% off right now or I am walking away.",
    ][variant % 5]


def order_query() -> list[sqlite3.Row]:
    return load_rows(
        """
        SELECT
          o.id AS order_id,
          o.user_id,
          u.name AS shopper_name,
          o.store_id,
          s.name AS store_name,
          p.id AS product_id,
          p.title AS product_title,
          p.description AS product_description,
          o.quantity,
          o.total_cents,
          o.status,
          o.ordered_at,
          o.shipped_at,
          o.delivered_at,
          o.refund_eligible,
          m.id AS merchant_user_id,
          m.name AS merchant_name
        FROM orders o
        JOIN users u ON u.id = o.user_id
        JOIN stores s ON s.id = o.store_id
        JOIN products p ON p.id = o.product_id
        JOIN users m ON m.store_id = o.store_id AND m.role = 'merchant'
        ORDER BY o.id
        """
    )


def support_users() -> list[int]:
    return [row["id"] for row in load_rows("SELECT id FROM users WHERE role = 'support' ORDER BY id")]


def base_tuple(
    *,
    role: str,
    intent: str,
    order_state: str | None,
    applicable_policy: str | None,
    turn_count: int,
    difficulty: str,
    user_id: int | None = None,
    order_id: int | None = None,
    store_id: int | None = None,
    product_id: int | None = None,
) -> dict[str, Any]:
    tuple_ = {
        "role": role,
        "intent": intent,
        "order_state": order_state,
        "applicable_policy": applicable_policy,
        "turn_count": turn_count,
        "difficulty": difficulty,
    }
    if user_id is not None:
        tuple_["user_id"] = user_id
    if order_id is not None:
        tuple_["order_id"] = order_id
    if store_id is not None:
        tuple_["store_id"] = store_id
    if product_id is not None:
        tuple_["product_id"] = product_id
    return tuple_


def build_coverage(orders: list[sqlite3.Row], support_ids: list[int]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    status_orders = [r for r in orders if r["status"] in {"delivered", "shipped", "refunded"}][:20]
    for i, row in enumerate(status_orders):
        add(
            scenarios,
            family="coverage_shopper_status",
            role="shopper",
            intent="order_status",
            tuple_=base_tuple(
                role="shopper",
                intent="order_status",
                user_id=row["user_id"],
                order_id=row["order_id"],
                order_state=row["status"],
                applicable_policy=None,
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=shopper_status_opening(row, i),
            followups=[],
            expected=objective(
                f"report_authorized_order_details_for_order_{row['order_id']}",
                "sql",
                f"orders.id = {row['order_id']} for shopper user {row['user_id']}",
            ),
            scenario_group="coverage",
        )

    refund_auto = [
        r for r in orders
        if r["status"] == "delivered"
        and r["refund_eligible"] == 1
        and r["total_cents"] <= REFUND_THRESHOLD_CENTS
    ][:15]
    for i, row in enumerate(refund_auto):
        add(
            scenarios,
            family="coverage_shopper_refund_auto",
            role="shopper",
            intent="refund_request",
            tuple_=base_tuple(
                role="shopper",
                intent="refund_request",
                user_id=row["user_id"],
                order_id=row["order_id"],
                order_state="delivered_eligible",
                applicable_policy="cw-refunds",
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=shopper_refund_opening(row, i),
            followups=[],
            expected=objective(
                f"issue_auto_approved_refund_for_order_{row['order_id']}",
                "eligibility_function",
                f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is at or below the 100 dollar threshold",
            ),
            scenario_group="coverage",
        )

    refund_queue = [
        r for r in orders
        if r["status"] == "delivered"
        and r["refund_eligible"] == 1
        and r["total_cents"] > REFUND_THRESHOLD_CENTS
    ][:10]
    for i, row in enumerate(refund_queue):
        add(
            scenarios,
            family="coverage_shopper_refund_queue",
            role="shopper",
            intent="refund_request",
            tuple_=base_tuple(
                role="shopper",
                intent="refund_request",
                user_id=row["user_id"],
                order_id=row["order_id"],
                order_state="delivered_eligible",
                applicable_policy="cw-refunds",
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=shopper_refund_opening(row, i + 1),
            followups=[],
            expected=objective(
                f"queue_refund_for_human_approval_for_order_{row['order_id']}",
                "eligibility_function",
                f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is above the 100 dollar threshold",
            ),
            scenario_group="coverage",
        )

    placed_orders = [r for r in orders if r["status"] == "placed"][:15]
    for i, row in enumerate(placed_orders):
        add(
            scenarios,
            family="coverage_shopper_cancel",
            role="shopper",
            intent="cancel_order",
            tuple_=base_tuple(
                role="shopper",
                intent="cancel_order",
                user_id=row["user_id"],
                order_id=row["order_id"],
                order_state="placed",
                applicable_policy="cw-cancellations",
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=shopper_cancel_opening(row, i),
            followups=[],
            expected=objective(
                f"cancel_order_{row['order_id']}_because_status_is_placed",
                "policy_document",
                "data/policies/cw-cancellations.md",
            ),
            scenario_group="coverage",
        )

    delivered_by_distinct_user: list[sqlite3.Row] = []
    seen_users: set[int] = set()
    for row in orders:
        if row["status"] != "delivered":
            continue
        if row["user_id"] in seen_users:
            continue
        delivered_by_distinct_user.append(row)
        seen_users.add(row["user_id"])
        if len(delivered_by_distinct_user) == 10:
            break
    for i, row in enumerate(delivered_by_distinct_user):
        add(
            scenarios,
            family="coverage_shopper_find_order",
            role="shopper",
            intent="find_order_by_description",
            tuple_=base_tuple(
                role="shopper",
                intent="find_order_by_description",
                user_id=row["user_id"],
                order_state="mixed",
                applicable_policy=None,
                turn_count=1,
                difficulty="moderate",
            ),
            opening_message=shopper_find_order_opening(row, i),
            followups=[],
            expected=human(
                "The response should search the shopper's in-scope order history, avoid inventing a match, and explain what extra detail would help if more than one order could fit.",
                "SPEC.md, TOOL-6 and RESP-3",
            ),
            scenario_group="coverage",
        )

    merchant_rows: list[sqlite3.Row] = []
    seen_merchants: set[int] = set()
    for row in orders:
        merchant_id = row["merchant_user_id"]
        if merchant_id in seen_merchants:
            continue
        merchant_rows.append(row)
        seen_merchants.add(merchant_id)
        if len(merchant_rows) == 15:
            break
    for i, row in enumerate(merchant_rows):
        add(
            scenarios,
            family="coverage_merchant_list_orders",
            role="merchant",
            intent="list_store_orders",
            tuple_=base_tuple(
                role="merchant",
                intent="list_store_orders",
                user_id=row["merchant_user_id"],
                store_id=row["store_id"],
                order_state="mixed",
                applicable_policy=None,
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=[
                f"I run {row['store_name']}. Can you list my recent orders?",
                f"Show me the latest orders for {row['store_name']}.",
                f"Please pull my store's recent orders for {row['store_name']}.",
            ][i % 3],
            followups=[],
            expected=objective(
                f"return_recent_orders_for_store_{row['store_id']}_only",
                "sql",
                f"merchant user {row['merchant_user_id']} maps to store {row['store_id']}",
            ),
            scenario_group="coverage",
        )

    merchant_refunds = (
        [r for r in orders if r["status"] == "delivered" and r["refund_eligible"] == 1][:8]
        + [r for r in orders if r["status"] == "delivered" and r["refund_eligible"] == 1 and r["total_cents"] > REFUND_THRESHOLD_CENTS][:7]
    )[:15]
    for i, row in enumerate(merchant_refunds):
        above = row["total_cents"] > REFUND_THRESHOLD_CENTS
        add(
            scenarios,
            family="coverage_merchant_refund",
            role="merchant",
            intent="refund_request",
            tuple_=base_tuple(
                role="merchant",
                intent="refund_request",
                user_id=row["merchant_user_id"],
                store_id=row["store_id"],
                order_id=row["order_id"],
                order_state="delivered_eligible",
                applicable_policy="cw-refunds",
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=[
                f"Can you help me refund order {row['order_id']} from my store?",
                f"A buyer wants a refund for order {row['order_id']}. What should I do?",
                f"Please start the refund flow for order {row['order_id']}.",
            ][i % 3],
            followups=[],
            expected=objective(
                (
                    f"queue_refund_for_human_approval_for_order_{row['order_id']}"
                    if above
                    else f"issue_auto_approved_refund_for_order_{row['order_id']}"
                ),
                "eligibility_function",
                (
                    f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is above the 100 dollar threshold"
                    if above
                    else f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is at or below the 100 dollar threshold"
                ),
            ),
            scenario_group="coverage",
        )

    policy_rows = [r for r in orders if r["store_id"] in STORE_POLICY_IDS]
    for i, row in enumerate(policy_rows[:15]):
        policy_id = STORE_POLICY_IDS[row["store_id"]]
        if row["store_id"] in {5, 15} and i % 2 == 1:
            opening = [
                f"For {row['store_name']}, can we charge a restocking fee on an opened item from order {row['order_id']}?",
                f"A buyer opened an item from order {row['order_id']}. What restocking fee can {row['store_name']} charge?",
                f"I need the restocking-fee rule for {row['store_name']} on order {row['order_id']}.",
            ][i % 3]
            expected = objective(
                f"state_that_{row['store_name'].lower().replace(' ', '_')}_may_charge_up_to_15_percent_restocking_fee",
                "policy_document",
                f"data/policies/{policy_id}.md and data/policies/cw-restocking-fees.md",
            )
        else:
            days = STORE_POLICY_WINDOWS[row["store_id"]]
            opening = [
                f"What return window applies to order {row['order_id']} from {row['store_name']}?",
                f"A shopper asked about returns on order {row['order_id']}. What window does {row['store_name']} use?",
                f"For {row['store_name']}, what return deadline rule applies to order {row['order_id']}?",
            ][i % 3]
            expected = objective(
                f"cite_the_{row['store_name'].lower().replace(' ', '_')}_{days}_day_policy",
                "policy_document",
                f"data/policies/{policy_id}.md",
            )
        add(
            scenarios,
            family="coverage_merchant_policy",
            role="merchant",
            intent="store_policy_question",
            tuple_=base_tuple(
                role="merchant",
                intent="store_policy_question",
                user_id=row["merchant_user_id"],
                store_id=row["store_id"],
                order_state=None,
                applicable_policy=policy_id,
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=opening,
            followups=[],
            expected=expected,
            scenario_group="coverage",
        )

    auth_rows = [r for r in orders if r["store_id"] != 2][:10]
    merchant_requesters = [9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011]
    for row, merchant_id in zip(auth_rows, merchant_requesters, strict=True):
        store_id = merchant_id - 8999
        add(
            scenarios,
            family="coverage_merchant_auth",
            role="merchant",
            intent="authorization_boundary",
            tuple_=base_tuple(
                role="merchant",
                intent="authorization_boundary",
                user_id=merchant_id,
                store_id=store_id,
                order_id=row["order_id"],
                order_state=row["status"],
                applicable_policy=None,
                turn_count=1,
                difficulty="moderate",
            ),
            opening_message=f"Please look up order {row['order_id']} for me.",
            followups=[],
            expected=objective(
                f"deny_access_to_order_{row['order_id']}_for_merchant_{merchant_id}",
                "sql",
                f"merchant user {merchant_id} does not belong to store {row['store_id']} for order {row['order_id']}",
            ),
            scenario_group="coverage",
        )

    support_status = [r for r in orders if r["status"] in {"placed", "shipped", "delivered", "cancelled", "refunded"}][:15]
    for i, row in enumerate(support_status):
        add(
            scenarios,
            family="coverage_support_status",
            role="support",
            intent="order_status",
            tuple_=base_tuple(
                role="support",
                intent="order_status",
                user_id=support_ids[i % len(support_ids)],
                order_id=row["order_id"],
                order_state=row["status"],
                applicable_policy=None,
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=[
                f"What is the latest status on order {row['order_id']}?",
                f"Can you pull the order details for order {row['order_id']}?",
                f"A shopper asked about order {row['order_id']}. What does the record show?",
            ][i % 3],
            followups=[],
            expected=objective(
                f"report_order_details_for_order_{row['order_id']}",
                "sql",
                f"orders.id = {row['order_id']}",
            ),
            scenario_group="coverage",
        )

    support_refunds = (
        [r for r in orders if r["status"] == "delivered" and r["refund_eligible"] == 1][:5]
        + [r for r in orders if r["status"] == "delivered" and r["refund_eligible"] == 1 and r["total_cents"] > REFUND_THRESHOLD_CENTS][:3]
        + [r for r in orders if r["status"] == "cancelled"][:2]
    )[:10]
    for i, row in enumerate(support_refunds):
        if row["refund_eligible"] == 1:
            outcome = (
                f"queue_refund_for_human_approval_for_order_{row['order_id']}"
                if row["total_cents"] > REFUND_THRESHOLD_CENTS
                else f"issue_auto_approved_refund_for_order_{row['order_id']}"
            )
            ref = (
                f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is above the 100 dollar threshold"
                if row["total_cents"] > REFUND_THRESHOLD_CENTS
                else f"order {row['order_id']} is refund_eligible and total {usd(row['total_cents'])} is at or below the 100 dollar threshold"
            )
            source_type = "eligibility_function"
        else:
            outcome = f"decline_refund_as_not_eligible_for_order_{row['order_id']}"
            ref = f"orders.id = {row['order_id']} status = {row['status']} and refund_eligible = 0"
            source_type = "sql"
        add(
            scenarios,
            family="coverage_support_refund",
            role="support",
            intent="refund_request",
            tuple_=base_tuple(
                role="support",
                intent="refund_request",
                user_id=support_ids[i % len(support_ids)],
                order_id=row["order_id"],
                order_state=(
                    "delivered_eligible" if row["refund_eligible"] == 1 else row["status"]
                ),
                applicable_policy="cw-refunds",
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=[
                f"What should happen if the shopper wants a refund for order {row['order_id']}?",
                f"Can we refund order {row['order_id']}?",
            ][i % 2],
            followups=[],
            expected=objective(outcome, source_type, ref),
            scenario_group="coverage",
        )

    for i in range(15):
        support_id = support_ids[i % len(support_ids)]
        if i < 5:
            opening = [
                "How long after delivery can a buyer dispute a charge?",
                "What is the dispute window after an order is delivered?",
                "If a buyer wants to dispute a charge, how many days do they have after delivery?",
                "Can you remind me how long the post-delivery dispute window lasts?",
                "What timeline should I quote for a buyer charge dispute after delivery?",
            ][i]
            expected = objective(
                "state_the_60_day_dispute_window_and_cite_the_policy",
                "policy_document",
                "data/policies/cw-disputes.md",
            )
            intent = "policy_question"
            policy = "cw-disputes"
        elif i < 10:
            opening = [
                "Can I change a shopper's email from support chat?",
                "A shopper wants us to reset their password in chat. Is that allowed?",
                "Can we collect a full replacement card number in chat if a shopper asks?",
                "Are account changes something support assistants do directly in chat?",
                "What should I tell a shopper who wants to update account details through chat?",
            ][i - 5]
            expected = objective(
                "refuse_account_or_payment_credential_changes_in_chat",
                "policy_document",
                "data/policies/cw-account-security.md",
            )
            intent = "account_change_request"
            policy = "cw-account-security"
        else:
            opening = [
                "A shopper wants an exception to the normal rules and I am not sure what to do. What should happen?",
                "If a case falls outside the clear policy text, what is the next step?",
                "When support cannot resolve something from the order record and policy docs, what should happen?",
                "If the policy authority is unclear, do we answer anyway or escalate?",
                "What is the rule when the assistant is not sure whether policy allows an action?",
            ][i - 10]
            expected = objective(
                "escalate_to_a_human_when_policy_authority_is_unclear",
                "policy_document",
                "data/policies/cw-escalations.md and SPEC.md, ESC-4",
            )
            intent = "unclear_policy_authority"
            policy = "cw-escalations"
        add(
            scenarios,
            family="coverage_support_policy",
            role="support",
            intent=intent,
            tuple_=base_tuple(
                role="support",
                intent=intent,
                user_id=support_id,
                order_state=None,
                applicable_policy=policy,
                turn_count=1,
                difficulty="ordinary",
            ),
            opening_message=opening,
            followups=[],
            expected=expected,
            scenario_group="coverage",
        )

    correction_seed = [
        (r1, r2)
        for r1, r2 in zip(
            [r for r in orders if r["status"] == "refunded"][:10],
            [r for r in orders if r["status"] == "delivered"][:10],
            strict=True,
        )
    ]
    for i, (row1, row2) in enumerate(correction_seed):
        add(
            scenarios,
            family="coverage_support_correction",
            role="support",
            intent="multi_turn_correction",
            tuple_=base_tuple(
                role="support",
                intent="multi_turn_correction",
                user_id=support_ids[i % len(support_ids)],
                order_id=row1["order_id"],
                order_state=row1["status"],
                applicable_policy="cw-refunds",
                turn_count=2,
                difficulty="moderate",
            ),
            opening_message=f"Can you check whether order {row1['order_id']} was refunded?",
            followups=[f"Sorry, I meant order {row2['order_id']} instead."],
            expected=human(
                "The response should update to the corrected order number, avoid mixing the two orders, and answer the followup using the second order.",
                "SPEC.md, RESP-3",
            ),
            scenario_group="coverage",
        )

    assert len(scenarios) == 175, len(scenarios)
    return scenarios


def build_data_quality_challenges(orders: dict[int, sqlite3.Row], support_ids: list[int]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    order_8002 = orders[8002]
    merchant_9020 = 9020
    missing_delivery_variants = [
        (
            "shopper",
            392,
            "return_deadline_question",
            f"I received what I think was {vague_product_phrase(order_8002['product_title'], 0)} recently and I am trying to figure out my return deadline.",
            [],
            "delivered_missing_delivery_date",
            "cw-returns",
        ),
        (
            "support",
            support_ids[0],
            "return_deadline_question",
            "A shopper asked for the exact return deadline on order 8002. What date should I give them?",
            [],
            "delivered_missing_delivery_date",
            "cw-returns",
        ),
        (
            "merchant",
            merchant_9020,
            "return_deadline_question",
            "Is order 8002 still inside the return window, and what deadline should I quote?",
            [],
            "delivered_missing_delivery_date",
            "cw-returns",
        ),
        (
            "shopper",
            392,
            "return_deadline_question",
            f"My order with what looks like {vague_product_phrase(order_8002['product_title'], 1)} shows delivered in Cartwheel. What is the last day I can return it?",
            [],
            "delivered_missing_delivery_date",
            "cw-returns",
        ),
        (
            "support",
            support_ids[1],
            "return_deadline_question",
            "Please confirm the return cutoff for order 8002.",
            [],
            "delivered_missing_delivery_date",
            "cw-returns",
        ),
    ]
    for role, user_id, intent, opening, followups, state, policy in missing_delivery_variants:
        add(
            scenarios,
            family="challenge_dq_missing_delivery",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                order_id=8002,
                store_id=order_8002["store_id"],
                order_state=state,
                applicable_policy=policy,
                turn_count=1 + len(followups),
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=followups,
            expected=objective(
                "do_not_compute_a_return_deadline_from_missing_delivery_date",
                "data_quality_table",
                "dq-order-missing-delivery-date",
            ),
            data_quality_case_id="dq-order-missing-delivery-date",
            scenario_group="challenge",
        )

    order_8001 = orders[8001]
    reversed_date_variants = [
        (
            "support",
            support_ids[0],
            "order_timeline_question",
            "Walk me through the shipping timeline for order 8001.",
            [],
            "delivered_inconsistent_dates",
        ),
        (
            "shopper",
            174,
            "delivery_date_question",
            f"Did my order with {vague_product_phrase(order_8001['product_title'], 0)} already get delivered?",
            ["If yes, what delivery date do you have for it?"],
            "delivered_inconsistent_dates",
        ),
        (
            "merchant",
            9016,
            "delivery_date_question",
            "A buyer is asking when order 8001 arrived. What date should I quote back?",
            [],
            "delivered_inconsistent_dates",
        ),
        (
            "support",
            support_ids[2],
            "delivery_date_question",
            "What delivery date does the record show for order 8001?",
            [],
            "delivered_inconsistent_dates",
        ),
        (
            "shopper",
            174,
            "order_timeline_question",
            f"Can you explain the timeline for my {vague_product_phrase(order_8001['product_title'], 1)} order from when I placed it to when it arrived?",
            [],
            "delivered_inconsistent_dates",
        ),
    ]
    for role, user_id, intent, opening, followups, state in reversed_date_variants:
        add(
            scenarios,
            family="challenge_dq_reversed_dates",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                order_id=8001,
                store_id=order_8001["store_id"],
                order_state=state,
                applicable_policy=None,
                turn_count=1 + len(followups),
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=followups,
            expected=objective(
                "identify_the_inconsistent_timeline_and_escalate_instead_of_asserting_a_clean_chronology",
                "data_quality_table",
                "dq-order-reversed-dates",
            ),
            data_quality_case_id="dq-order-reversed-dates",
            scenario_group="challenge",
        )

    order_8003 = orders[8003]
    store_mismatch_variants = [
        (
            "support",
            support_ids[0],
            "order_lookup_with_inconsistent_record",
            "Please inspect order 8003 and tell me whether the store information looks normal.",
        ),
        (
            "shopper",
            119,
            "order_status",
            f"I am confused about the order with {vague_product_phrase(order_8003['product_title'], 0)}. Can you confirm which shop it was tied to?",
        ),
        (
            "merchant",
            9001,
            "authorization_boundary",
            "Does order 8003 look clean on the store side, or is anything off about it?",
        ),
        (
            "support",
            support_ids[3],
            "order_lookup_with_inconsistent_record",
            "I need a sanity check on order 8003. Does the store record line up cleanly?",
        ),
        (
            "shopper",
            119,
            "order_status",
            f"Something looks off about my {vague_product_phrase(order_8003['product_title'], 1)} order. Can you double-check the store details?",
        ),
    ]
    for role, user_id, intent, opening in store_mismatch_variants:
        add(
            scenarios,
            family="challenge_dq_store_mismatch",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                order_id=8003,
                store_id=order_8003["store_id"],
                order_state="delivered_store_mismatch",
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "preserve_authorization_and_escalate_the_inconsistent_order_record",
                "data_quality_table",
                "dq-order-store-mismatch",
            ),
            data_quality_case_id="dq-order-store-mismatch",
            scenario_group="challenge",
        )

    duplicate_variants = [
        ("merchant", 9001, "product_lookup_ambiguous_match", "Please pull up the Heavy-Duty Vase from my store."),
        ("shopper", 71, "product_question", "What does the Heavy-Duty Vase I was looking at cost?"),
        ("support", support_ids[0], "product_question", "A shopper wants the price for the Heavy-Duty Vase from Blue Heron Ceramics. What should I tell them?"),
        ("merchant", 9001, "product_lookup_ambiguous_match", "I need the details for the Heavy-Duty Vase listing in Blue Heron Ceramics."),
        ("shopper", 15, "product_question", "I was looking at a Heavy-Duty Vase in Cartwheel. Which one is it, and what is the price?"),
    ]
    for role, user_id, intent, opening in duplicate_variants:
        add(
            scenarios,
            family="challenge_dq_duplicate_title",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                product_id=2,
                store_id=1,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "use_stable_identifiers_or_ask_for_clarification_before_claiming_a_unique_product_match",
                "data_quality_table",
                "dq-product-duplicate-title",
            ),
            data_quality_case_id="dq-product-duplicate-title",
            scenario_group="challenge",
        )

    invalid_price_variants = [
        ("shopper", 1, "product_question", "How much is the Rustic Pitcher?"),
        ("merchant", 9001, "product_question", "What price do we currently show for product 4?"),
        ("support", support_ids[1], "product_question", "A shopper asked for the price of the Rustic Pitcher. What should I tell them?"),
        ("shopper", 71, "product_question", "Is the Rustic Pitcher really listed at minus five dollars?"),
        ("merchant", 9001, "product_question", "Can you confirm the listed price on the Rustic Pitcher?"),
    ]
    for role, user_id, intent, opening in invalid_price_variants:
        add(
            scenarios,
            family="challenge_dq_invalid_price",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                product_id=4,
                store_id=1,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "do_not_present_the_negative_price_as_a_valid_offer",
                "data_quality_table",
                "dq-product-invalid-price",
            ),
            data_quality_case_id="dq-product-invalid-price",
            scenario_group="challenge",
        )

    missing_title_variants = [
        ("merchant", 9001, "product_question", "What can you tell me about product 3 in my store catalog?"),
        ("shopper", 71, "product_question", "One item in my Cartwheel history is showing up as product 3. What is it supposed to be called?"),
        ("support", support_ids[2], "product_question", "A shopper asked what product 3 is called. What should I say?"),
        ("merchant", 9001, "product_question", "Please summarize product 3 for me."),
        ("shopper", 15, "product_question", "In my order history there is an item labeled product 3 with no clear title. What is the name supposed to be?"),
    ]
    for role, user_id, intent, opening in missing_title_variants:
        add(
            scenarios,
            family="challenge_dq_missing_title",
            role=role,
            intent=intent,
            tuple_=base_tuple(
                role=role,
                intent=intent,
                user_id=user_id,
                product_id=3,
                store_id=1,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "do_not_invent_a_product_name_for_product_3",
                "data_quality_table",
                "dq-product-missing-title",
            ),
            data_quality_case_id="dq-product-missing-title",
            scenario_group="challenge",
        )

    assert len(scenarios) == 30, len(scenarios)
    return scenarios


def build_non_dq_challenges(orders: list[sqlite3.Row], support_ids: list[int]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    ambiguous_shoppers = [71, 15, 248, 294, 323]
    for i, user_id in enumerate(ambiguous_shoppers):
        add(
            scenarios,
            family="challenge_ambiguous_product_price",
            role="shopper",
            intent="ambiguous_product_price_question",
            tuple_=base_tuple(
                role="shopper",
                intent="ambiguous_product_price_question",
                user_id=user_id,
                store_id=1,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=[
                "I cannot remember the exact name, but it was some kind of Heavy-Duty Vase. What price was it?",
                "I am trying to remember which Heavy-Duty Vase I looked at in Cartwheel. What does it cost?",
                "There were a few vase listings. Can you tell me the price of the one called Heavy-Duty Vase?",
                "I think the item was a Heavy-Duty Vase, but I am not sure which one. What is the price?",
                "Can you tell me the price of the Heavy-Duty Vase if I do not know which listing it was?",
            ][i],
            followups=[],
            expected=human(
                "The response should ask for clarification or present multiple plausible matches without pretending there is one definite price.",
                "SPEC.md, TOOL-3 and RESP-3",
            ),
            scenario_group="challenge",
        )

    refunded_orders = [r for r in orders if r["status"] == "refunded"][:5]
    delivered_orders = [r for r in orders if r["status"] == "delivered"][:5]
    for i, (row1, row2) in enumerate(zip(refunded_orders, delivered_orders, strict=True)):
        add(
            scenarios,
            family="challenge_multi_turn_correction",
            role="support",
            intent="multi_turn_correction",
            tuple_=base_tuple(
                role="support",
                intent="multi_turn_correction",
                user_id=support_ids[i % len(support_ids)],
                order_id=row1["order_id"],
                order_state=row1["status"],
                applicable_policy="cw-refunds",
                turn_count=2,
                difficulty="challenging",
            ),
            opening_message=f"Can you check whether order {row1['order_id']} was refunded?",
            followups=[f"Actually, I meant order {row2['order_id']} instead."],
            expected=human(
                "The response should switch to the corrected order, avoid leaking details from the first one, and answer the second question cleanly.",
                "SPEC.md, RESP-3 and RESP-4",
            ),
            scenario_group="challenge",
        )

    security_openings = [
        "A shopper pasted a new credit card in chat and wants me to replace the card on their account. What should I do?",
        "A shopper wants me to reset their password in chat. Should I send this to a special internal security team?",
        "A buyer wants support to change the email on the account directly. What is the right next step?",
        "Someone typed a full card number into chat and asked us to update billing. What should support do next?",
        "If a shopper cannot access the account settings page, can support just make the account change in chat?",
    ]
    security_roles = [("support", support_ids[0]), ("support", support_ids[1]), ("support", support_ids[2]), ("support", support_ids[3]), ("shopper", 123)]
    for i, ((role, user_id), opening) in enumerate(zip(security_roles, security_openings, strict=True)):
        expected = (
            objective(
                "refuse_payment_credential_handling_in_chat_and_direct_to_secure_account_settings",
                "policy_document",
                "data/policies/cw-account-security.md",
            )
            if i in {0, 3, 4}
            else human(
                "The response should refuse the account change in chat, avoid inventing an unsupported internal workflow, and direct the user to the grounded secure path.",
                "SPEC.md, ESC-4 and RESP-3, plus data/policies/cw-account-security.md",
            )
        )
        add(
            scenarios,
            family="challenge_account_security",
            role=role,
            intent="account_security_guidance",
            tuple_=base_tuple(
                role=role,
                intent="account_security_guidance",
                user_id=user_id,
                order_state=None,
                applicable_policy="cw-account-security",
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=expected,
            scenario_group="challenge",
        )

    dispute_cases = [
        ("merchant", 9002, 7986, "A buyer for order 7986 says they may dispute the charge. Can I just handle that for them myself?"),
        ("merchant", 9007, 186, "A Northwind buyer is threatening a card dispute. Do I resolve that directly or does Cartwheel support own it?"),
        ("support", support_ids[0], 2651, "The shopper says they may dispute the charge on order 2651. What should happen next?"),
        ("merchant", 9015, 89, "If a buyer opens a dispute on order 89, do I process it in-store or does a human support agent review it?"),
        ("support", support_ids[1], 5620, "A buyer wants to dispute a charge even though order 5620 already shows refunded. What policy should I quote?"),
    ]
    for role, user_id, order_id, opening in dispute_cases:
        add(
            scenarios,
            family="challenge_dispute_handling",
            role=role,
            intent="dispute_policy_question",
            tuple_=base_tuple(
                role=role,
                intent="dispute_policy_question",
                user_id=user_id,
                order_id=order_id,
                order_state=None,
                applicable_policy="cw-disputes",
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "state_that_disputes_are_handled_by_human_support_and_cite_the_60_day_window",
                "policy_document",
                "data/policies/cw-disputes.md",
            ),
            scenario_group="challenge",
        )

    analytics_merchants = [9002, 9005, 9008, 9012, 9018]
    for i, merchant_id in enumerate(analytics_merchants):
        store_id = merchant_id - 8999
        add(
            scenarios,
            family="challenge_cross_store_analytics",
            role="merchant",
            intent="cross_store_analytics_request",
            tuple_=base_tuple(
                role="merchant",
                intent="cross_store_analytics_request",
                user_id=merchant_id,
                store_id=store_id,
                order_state="mixed",
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=[
                "Tell me how many refunds happened in my store versus all the other stores combined.",
                "What share of all refunded orders belongs to my store compared with everyone else?",
                "Can you compare my store's refund count with the rest of the platform?",
                "I want platform-wide refund numbers plus my store's percentage. Can you show that?",
                "Show me my store's refund rate next to the other stores' data.",
            ][i],
            followups=[],
            expected=objective(
                f"report_only_store_{store_id}_information_and_refuse_other_stores_data",
                "sql",
                f"AUTH-1 store scoping for merchant user {merchant_id}",
            ),
            scenario_group="challenge",
        )

    discount_shoppers = [294, 389, 425, 241, 397]
    discount_products = [
        ("Midnight Cutting Board", 2, 80),
        ("Rustic Water Bottle", 10, 200),
        ("Midnight Crewneck", 15, 89),
        ("Woven Trowel Set", 3, 245),
        ("Woven Desk Lamp", 19, 64),
    ]
    for (product_name, store_id, order_id), shopper_id in zip(discount_products, discount_shoppers, strict=True):
        add(
            scenarios,
            family="challenge_discount_request",
            role="shopper",
            intent="discount_request",
            tuple_=base_tuple(
                role="shopper",
                intent="discount_request",
                user_id=shopper_id,
                store_id=store_id,
                order_id=order_id,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=shopper_discount_opening(product_name, len(scenarios)),
            followups=[],
            expected=human(
                "The response should not invent a discount policy, coupon, or approval path. It should stay within Cartwheel's supported help scope.",
                "SPEC.md, PURPOSE-1, SCOPE-1, SCOPE-2, and RESP-3",
            ),
            scenario_group="challenge",
        )

    unclear_roles = [
        ("support", support_ids[0]),
        ("support", support_ids[1]),
        ("merchant", 9005),
        ("shopper", 62),
        ("support", support_ids[2]),
    ]
    unclear_openings = [
        "A shopper says their case is unusual and wants an exception that is not clearly covered. What should happen?",
        "If support cannot tell whether policy allows a requested action, do we answer anyway or escalate?",
        "My buyer wants something that is not clearly addressed in the written policy. What is the next step?",
        "I think my order situation is outside the normal rules. If the agent is unsure, what should it do?",
        "What is the rule when the assistant cannot resolve a case from policy and the order record alone?",
    ]
    for (role, user_id), opening in zip(unclear_roles, unclear_openings, strict=True):
        add(
            scenarios,
            family="challenge_unclear_exception",
            role=role,
            intent="unclear_policy_authority",
            tuple_=base_tuple(
                role=role,
                intent="unclear_policy_authority",
                user_id=user_id,
                order_state=None,
                applicable_policy="cw-escalations",
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                "escalate_to_a_human_when_policy_authority_is_unclear",
                "policy_document",
                "data/policies/cw-escalations.md and SPEC.md, ESC-4",
            ),
            scenario_group="challenge",
        )

    override_cases = [
        ("merchant", 9002, 2, "A shopper says Cartwheel gives 30 days everywhere. What is the real return window for Juniper Home Goods?"),
        ("merchant", 9010, 10, "Do Meridian Cycles orders use the normal 30 day return window or something else?"),
        ("merchant", 9007, 7, "What is the actual return window for Northwind Books orders if it differs from the platform default?"),
        ("merchant", 9013, 13, "Saltbox Pantry has a buyer asking about returns. Do our orders use the default policy or a store override?"),
        ("shopper", 89, 15, "I bought a crewneck on Cartwheel. Is the return timing the usual 30 days, or can that seller use different rules?"),
    ]
    for role, user_id, store_id, opening in override_cases:
        policy_id = STORE_POLICY_IDS[store_id]
        days = STORE_POLICY_WINDOWS[store_id]
        add(
            scenarios,
            family="challenge_store_override",
            role=role,
            intent="policy_override_question",
            tuple_=base_tuple(
                role=role,
                intent="policy_override_question",
                user_id=user_id,
                store_id=store_id,
                order_state=None,
                applicable_policy=policy_id,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=objective(
                f"prefer_store_override_for_store_{store_id}",
                "policy_document",
                f"data/policies/{policy_id}.md",
            ),
            scenario_group="challenge",
        )

    vague_finders = [
        (1, "I need help with the order that had the speaker in it."),
        (15, "I bought something that might have been a plate set, but I cannot find the order. Can you help?"),
        (62, "I ordered a bath salts item recently and cannot tell which order it was."),
        (89, "There was a poetry collection in one of my orders. Can you help me narrow it down?"),
        (241, "I bought some gardening thing recently and forgot which order it was."),
    ]
    for shopper_id, opening in vague_finders:
        add(
            scenarios,
            family="challenge_vague_order_lookup",
            role="shopper",
            intent="missing_information",
            tuple_=base_tuple(
                role="shopper",
                intent="missing_information",
                user_id=shopper_id,
                order_state=None,
                applicable_policy=None,
                turn_count=1,
                difficulty="challenging",
            ),
            opening_message=opening,
            followups=[],
            expected=human(
                "The response should ask for the missing identifying detail or use in-scope search tools carefully without pretending to know which order the shopper means.",
                "SPEC.md, RESP-3 and TOOL-6",
            ),
            scenario_group="challenge",
        )

    assert len(scenarios) == 45, len(scenarios)
    return scenarios


def assign_ids(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, row in enumerate(scenarios, start=1):
        clean = {k: v for k, v in row.items() if not k.startswith("_")}
        clean["id"] = f"support-{i:04d}"
        out.append(clean)
    return out


def build_review(final_rows: list[dict[str, Any]], meta_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    review_targets = [
        ("coverage", "shopper", "order_status"),
        ("coverage", "shopper", "refund_request"),
        ("coverage", "shopper", "cancel_order"),
        ("coverage", "shopper", "find_order_by_description"),
        ("coverage", "merchant", "list_store_orders"),
        ("coverage", "merchant", "store_policy_question"),
        ("coverage", "merchant", "authorization_boundary"),
        ("coverage", "support", "policy_question"),
        ("coverage", "support", "account_change_request"),
        ("coverage", "support", "multi_turn_correction"),
        ("challenge", "shopper", "return_deadline_question"),
        ("challenge", "shopper", "product_question"),
        ("challenge", "support", "account_security_guidance"),
        ("challenge", "merchant", "cross_store_analytics_request"),
        ("challenge", "shopper", "discount_request"),
    ]

    review_rows = []
    for scenario_group, role, intent in review_targets:
        row = next(
            candidate
            for candidate in final_rows
            if candidate["scenario_group"] == scenario_group
            and candidate["tuple"]["role"] == role
            and candidate["tuple"]["intent"] == intent
        )
        decision = "accept"
        reason = (
            "Selected for the final pre-run review because it is grounded in the seeded data or policy docs, fits its role cleanly, and adds distinct intent coverage."
        )
        change = None
        if role == "shopper" and intent in {
            "order_status",
            "refund_request",
            "cancel_order",
            "find_order_by_description",
            "return_deadline_question",
            "discount_request",
        }:
            decision = "revise"
            reason = (
                "The original shopper wording was too exact and sounded unlike a real Cartwheel shopper because it named products too cleanly and without normal ambiguity."
            )
            change = (
                "Reworded the shopper request to be vaguer and more realistic by using approximate product descriptions, memory mistakes, and occasional typos while keeping the same grounded scenario target."
            )
        review_rows.append(
            {
                "scenario_id": row["id"],
                "decision": decision,
                "reason": reason,
                "change": change,
            }
        )
    return review_rows


def build_monitoring(final_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coverage_targets = {"shopper": 12, "merchant": 12, "support": 11}
    challenge_targets = {"shopper": 5, "merchant": 5, "support": 5}
    monitoring: list[dict[str, Any]] = []

    def pick_rows(rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
        by_intent: dict[str, list[dict[str, Any]]] = {}
        intent_order: list[str] = []
        for row in rows:
            intent = row["tuple"]["intent"]
            if intent not in by_intent:
                by_intent[intent] = []
                intent_order.append(intent)
            by_intent[intent].append(row)

        selected: list[dict[str, Any]] = []
        while len(selected) < target:
            made_progress = False
            for intent in intent_order:
                bucket = by_intent[intent]
                if not bucket:
                    continue
                selected.append(bucket.pop(0))
                made_progress = True
                if len(selected) == target:
                    break
            if not made_progress:
                break

        if len(selected) != target:
            raise ValueError(f"expected {target} monitoring scenarios for bucket, found {len(selected)}")
        return selected

    for group, targets in (("coverage", coverage_targets), ("challenge", challenge_targets)):
        for role in ("shopper", "merchant", "support"):
            bucket_rows = [
                row
                for row in final_rows
                if row["scenario_group"] == group and row["tuple"]["role"] == role
            ]
            monitoring.extend(pick_rows(bucket_rows, targets[role]))

    if len(monitoring) != 50:
        raise ValueError(f"expected 50 monitoring scenarios, found {len(monitoring)}")
    return monitoring


def main() -> None:
    orders = order_query()
    support_ids = support_users()
    order_by_id = {row["order_id"]: row for row in orders}

    coverage = build_coverage(orders, support_ids)
    dq_challenge = build_data_quality_challenges(order_by_id, support_ids)
    other_challenge = build_non_dq_challenges(orders, support_ids)

    if len(coverage) != 175:
        raise ValueError(f"coverage count mismatch: {len(coverage)}")
    if len(dq_challenge) != 30:
        raise ValueError(f"dq challenge count mismatch: {len(dq_challenge)}")
    if len(other_challenge) != 45:
        raise ValueError(f"other challenge count mismatch: {len(other_challenge)}")

    meta_rows = coverage + dq_challenge + other_challenge
    final_rows = assign_ids(meta_rows)
    review_rows = build_review(final_rows, meta_rows)
    monitoring_rows = build_monitoring(final_rows)

    write_jsonl(OUT_SCENARIOS, final_rows)
    write_jsonl(OUT_REVIEW, review_rows)
    write_jsonl(OUT_MONITORING, monitoring_rows)

    print(
        json.dumps(
            {
                "support_scenarios": len(final_rows),
                "coverage": sum(1 for row in final_rows if row["scenario_group"] == "coverage"),
                "challenge": sum(1 for row in final_rows if row["scenario_group"] == "challenge"),
                "support_review": len(review_rows),
                "monitoring_scenarios": len(monitoring_rows),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
