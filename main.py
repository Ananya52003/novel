from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import json


# Load the item list from JSON file
with open("item_list.json", "r") as f:
    item_list = json.load(f)


def generate_monthly_bill(item_list: list, target_month: str) -> dict:
    # Get start and end of target month
    year, month = map(int, target_month.split("-"))
    month_start = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime(year, month, last_day)
    total_days_in_month = (month_end - month_start).days + 1
    grouped_items = defaultdict(lambda: {"qty": 0, "amount": 0.0})
    total_revenue = 0.0

    for item in item_list:
        # Convert dates
        item_start = datetime.strptime(item["start_date"], "%Y-%m-%d")
        item_stop = datetime.strptime(item["stop_date"], "%Y-%m-%d")

        # Determine intersection with target month
        active_start = max(item_start, month_start)
        active_end = min(item_stop, month_end)

        if active_start > active_end:
            continue  # No overlap

        active_days = (active_end - active_start).days + 1
        if active_days <= 0:
            continue

        # Clean and convert qty, rate
        qty = int(item["qty"])
        rate = float(item["rate"])

        # Calculate prorated amount
        prorated_amount = (active_days / total_days_in_month) * rate * qty

        # Key for grouping
        billing_period = (
            f"{month_start.strftime('%Y-%m-%d')} to {month_end.strftime('%Y-%m-%d')}"
        )
        group_key = (item["item_code"], rate, billing_period)

        # Grouping
        grouped_items[group_key]["qty"] += qty
        grouped_items[group_key]["amount"] += prorated_amount

    # Prepare final output
    line_items = []
    for (item_code, rate, billing_period), values in grouped_items.items():
        amount = round(values["amount"], 2)
        line_items.append(
            {
                "item_code": item_code,
                "rate": rate,
                "qty": values["qty"],
                "amount": amount,
                "billing_period": billing_period,
            }
        )
        total_revenue += amount

    return {"line_items": line_items, "total_revenue": round(total_revenue, 2)}


bill = generate_monthly_bill(item_list, "2024-11")
print(json.dumps(bill, indent=2))
