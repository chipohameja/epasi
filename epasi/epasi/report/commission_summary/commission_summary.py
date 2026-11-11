import frappe
from frappe import _
from frappe.utils import flt, getdate

AMOUNTS = {"earned": _("Earned"), "paid": _("Paid"), "unpaid": _("Unpaid")}


def execute(filters=None):
	report = CommissionSummary(filters or {})
	return report.get_columns(), report.get_data()


class CommissionSummary:
	"""Per agent: commission earned and paid in the period, and what is still unpaid of it."""

	def __init__(self, filters: dict):
		self.period = [getdate(filters.get("from_date")), getdate(filters.get("to_date"))]
		if self.period[0] > self.period[1]:
			frappe.throw(_("From Date must be before To Date"))
		self.agent_filter = {"sales_agent": filters["sales_agent"]} if filters.get("sales_agent") else {}

	def get_data(self) -> list[dict]:
		earned = self.sum_by_agent({"earned_date": ["between", self.period]})
		paid = self.sum_by_agent({"paid_date": ["between", self.period], "status": "Paid"})
		unpaid = self.sum_by_agent({"earned_date": ["between", self.period], "status": "Unpaid"})
		agents = sorted(set(earned) | set(paid))
		names = dict(
			frappe.get_all(
				"Sales Agent",
				filters={"name": ["in", agents or [""]]},
				fields=["name", "full_name"],
				as_list=True,
			)
		)
		return [
			{
				"sales_agent": agent,
				"full_name": names.get(agent),
				"earned": earned.get(agent, 0),
				"paid": paid.get(agent, 0),
				"unpaid": unpaid.get(agent, 0),
			}
			for agent in agents
		]

	def sum_by_agent(self, filters: dict) -> dict:
		rows = frappe.get_all(
			"Commission",
			filters={**self.agent_filter, **filters},
			fields=["sales_agent", {"SUM": "amount", "as": "total"}],
			group_by="sales_agent",
		)
		return {row.sales_agent: flt(row.total) for row in rows}

	def get_columns(self) -> list[dict]:
		columns = [
			{
				"fieldname": "sales_agent",
				"label": _("Sales Agent"),
				"fieldtype": "Link",
				"options": "Sales Agent",
				"width": 130,
			},
			{"fieldname": "full_name", "label": _("Name"), "fieldtype": "Data", "width": 180},
		]
		return columns + [
			{"fieldname": name, "label": label, "fieldtype": "Currency", "width": 140}
			for name, label in AMOUNTS.items()
		]
