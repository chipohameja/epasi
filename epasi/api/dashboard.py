from functools import wraps

import frappe
from frappe import _
from frappe.utils import (
	add_days,
	add_months,
	flt,
	formatdate,
	get_first_day,
	get_first_day_of_week,
	get_last_day,
	today,
)

from epasi.epasi.money import COLLECTED, COMMISSION_PAID, LENT, MoneySummary
from epasi.epasi.report.daily_operations.daily_operations import ACTIVITIES

MANAGER_ROLES = ("Loan Manager", "System Manager")
UNPAID_STATUSES = ["Active", "Overdue", "Defaulted"]


def has_app_permission() -> bool:
	return bool(set(MANAGER_ROLES) & set(frappe.get_roles()))


def manager_only(method):
	@frappe.whitelist()
	@wraps(method)
	def wrapper(*args, **kwargs):
		frappe.only_for(MANAGER_ROLES)
		return method(*args, **kwargs)

	return wrapper


def card(value, doctype: str, fieldtype: str = "Int", **route_options) -> dict:
	return {
		"value": value,
		"fieldtype": fieldtype,
		"route": ["List", doctype],
		"route_options": route_options,
	}


def count(doctype: str, filters: dict) -> int:
	return frappe.db.count(doctype, filters)


def total_outstanding(filters: dict) -> float:
	rows = frappe.get_all(
		"Loan", filters={"docstatus": 1, **filters}, fields=[{"SUM": "outstanding", "as": "total"}]
	)
	return flt(rows[0].total)


def this_month() -> MoneySummary:
	return MoneySummary(get_first_day(today()), today())


@manager_only
def get_pending_applications(filters=None) -> dict:
	return card(count("Loan Application", {"status": "Pending"}), "Loan Application", status="Pending")


@manager_only
def get_reviews_awaiting_approval(filters=None) -> dict:
	return card(count("Review", {"is_published": 0}), "Review", is_published=0)


@manager_only
def get_loans_due_today(filters=None) -> dict:
	filters = {"docstatus": 1, "status": "Active", "due_date": today()}
	return card(count("Loan", filters), "Loan", status="Active", due_date=today())


@manager_only
def get_overdue_loans(filters=None) -> dict:
	return card(count("Loan", {"docstatus": 1, "status": "Overdue"}), "Loan", status="Overdue")


@manager_only
def get_overdue_amount(filters=None) -> dict:
	return card(total_outstanding({"status": "Overdue"}), "Loan", "Currency", status="Overdue")


@manager_only
def get_total_outstanding(filters=None) -> dict:
	value = total_outstanding({"status": ["in", UNPAID_STATUSES]})
	return card(value, "Loan", "Currency", docstatus=1, status=["in", UNPAID_STATUSES])


@manager_only
def get_lent_this_month(filters=None) -> dict:
	return card(LENT.total(get_first_day(today()), today()), "Loan", "Currency", docstatus=1)


@manager_only
def get_collected_this_month(filters=None) -> dict:
	return card(COLLECTED.total(get_first_day(today()), today()), "Loan Repayment", "Currency", docstatus=1)


@manager_only
def get_net_profit_this_month(filters=None) -> dict:
	return card(this_month().net_profit, "Expense", "Currency")


@manager_only
def get_unpaid_commissions(filters=None) -> dict:
	rows = frappe.get_all(
		"Commission", filters={"status": "Unpaid"}, fields=[{"SUM": "amount", "as": "total"}]
	)
	return card(flt(rows[0].total), "Commission", "Currency", status="Unpaid")


@manager_only
def get_commission_paid_this_month(filters=None) -> dict:
	value = COMMISSION_PAID.total(get_first_day(today()), today())
	return card(value, "Commission", "Currency", status="Paid")


@manager_only
def get_chart(chart_name: str | None = None, **kwargs) -> dict:
	builders = {
		"Lent vs Collected": get_lent_vs_collected,
		"Net Profit by Month": get_net_profit_by_month,
		"Outstanding by Status": get_outstanding_by_status,
		"Loans by Plan": get_loans_by_plan,
	}
	if chart_name not in builders:
		frappe.throw(_("Unknown chart {0}").format(chart_name))
	return builders[chart_name]()


def get_lent_vs_collected(weeks: int = 12) -> dict:
	week_starts = [add_days(get_first_day_of_week(today()), -7 * week) for week in reversed(range(weeks))]
	lent = LENT.by_date(week_starts[0], today())
	collected = COLLECTED.by_date(week_starts[0], today())
	return {
		"labels": [formatdate(start, "dd MMM") for start in week_starts],
		"datasets": [
			{"name": _("Lent"), "values": [sum_week(lent, start) for start in week_starts]},
			{"name": _("Collected"), "values": [sum_week(collected, start) for start in week_starts]},
		],
	}


def sum_week(totals_by_date: dict, week_start) -> float:
	week_end = add_days(week_start, 6)
	return sum(amount for day, amount in totals_by_date.items() if week_start <= day <= week_end)


def get_net_profit_by_month(months: int = 6) -> dict:
	month_starts = [get_first_day(today(), d_months=-month) for month in reversed(range(months))]
	profits = [MoneySummary(start, get_last_day(start)).net_profit for start in month_starts]
	labels = [formatdate(start, "MMM yyyy") for start in month_starts]
	return {"labels": labels, "datasets": [{"name": _("Net Profit"), "values": profits}]}


def get_outstanding_by_status() -> dict:
	statuses = UNPAID_STATUSES
	values = [total_outstanding({"status": status}) for status in statuses]
	return {
		"labels": [_(status) for status in statuses],
		"datasets": [{"name": _("Outstanding"), "values": values}],
	}


def get_loans_by_plan() -> dict:
	rows = frappe.get_all(
		"Loan",
		filters={"docstatus": 1},
		fields=["loan_plan", {"COUNT": "*", "as": "loans"}],
		group_by="loan_plan",
		order_by="loan_plan",
	)
	labels = [row.loan_plan for row in rows]
	return {"labels": labels, "datasets": [{"name": _("Loans"), "values": [row.loans for row in rows]}]}


@manager_only
def get_today_summary() -> dict:
	sections = [get_today_section(activity) for activity in ACTIVITIES]
	return {"date": today(), "sections": sections, "month": get_month_comparison()}


def get_today_section(activity) -> dict:
	rows = activity.get_rows(today())
	return {
		"label": _(activity.label),
		"count": len(rows),
		"total": sum(row["amount"] for row in rows),
		"rows": rows,
	}


def get_month_comparison() -> dict:
	"""This month to date against the same days of last month."""
	current = this_month()
	previous = MoneySummary(get_first_day(today(), d_months=-1), add_months(today(), -1))
	periods = [(summary.from_date, summary.to_date) for summary in (current, previous)]
	return {
		"lent": [LENT.total(*period) for period in periods],
		"collected": [COLLECTED.total(*period) for period in periods],
		"net_profit": [current.net_profit, previous.net_profit],
	}
