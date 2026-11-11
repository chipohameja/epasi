import re

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_url

REFERRAL_PATH = "/epasi/apply?ref="
AGENT_ROLES = {"Loan Officer": "Loan Officer", "Referrer": "Referrer"}


class SalesAgent(Document):
	def validate(self):
		self.referral_code = clean_code(self.referral_code) or self.make_referral_code()
		self.referral_link = get_url(REFERRAL_PATH + self.referral_code)

	def on_update(self):
		if self.has_value_changed("user") or self.has_value_changed("agent_type"):
			self.give_user_role()

	def give_user_role(self):
		if self.user:
			frappe.get_doc("User", self.user).add_roles(AGENT_ROLES[self.agent_type])

	def make_referral_code(self) -> str:
		base = clean_code(self.full_name.split()[0]) or "AGENT"
		code, number = base, 1
		while frappe.db.exists("Sales Agent", {"referral_code": code, "name": ["!=", self.name]}):
			number += 1
			code = f"{base}{number}"
		return code

	def update_commission_totals(self):
		totals = get_commission_totals(self.name)
		self.db_set(
			{
				"commission_earned": totals["Paid"] + totals["Unpaid"],
				"commission_paid": totals["Paid"],
				"commission_unpaid": totals["Unpaid"],
			}
		)

	@staticmethod
	def find_by_code(referral_code: str | None) -> str | None:
		code = clean_code(referral_code)
		return code and frappe.db.get_value("Sales Agent", {"referral_code": code, "is_active": 1})

	@staticmethod
	def for_user(user: str | None = None, agent_type: str | None = None) -> str | None:
		filters = {"user": user or frappe.session.user, "is_active": 1}
		if agent_type:
			filters["agent_type"] = agent_type
		return frappe.db.get_value("Sales Agent", filters)


def get_commission_totals(sales_agent: str) -> dict:
	rows = frappe.get_all(
		"Commission",
		filters={"sales_agent": sales_agent},
		fields=["status", {"SUM": "amount", "as": "total"}],
		group_by="status",
	)
	return {"Paid": 0, "Unpaid": 0} | {row.status: flt(row.total) for row in rows}


def clean_code(code: str | None) -> str:
	return re.sub(r"[^A-Z0-9]", "", (code or "").upper())
