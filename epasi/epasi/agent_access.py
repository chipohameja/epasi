from functools import cached_property

import frappe

from epasi.epasi.doctype.sales_agent.sales_agent import SalesAgent

MANAGER_ROLES = {"Loan Manager", "System Manager"}
AGENT_FIELDS = {
	"Borrower": "sales_agent",
	"Loan Application": "sales_agent",
	"Loan": "sales_agent",
	"Commission": "sales_agent",
	"Sales Agent": "name",
}


class AgentAccess:
	"""Limits a loan officer to the records of their own sales agent."""

	def __init__(self, user: str | None = None):
		self.user = user or frappe.session.user

	@cached_property
	def is_limited(self) -> bool:
		roles = set(frappe.get_roles(self.user))
		return "Loan Officer" in roles and not roles & MANAGER_ROLES

	@cached_property
	def sales_agent(self) -> str:
		return SalesAgent.for_user(self.user, "Loan Officer") or ""

	def query_condition(self, doctype: str) -> str:
		if not self.is_limited:
			return ""
		return f"`tab{doctype}`.`{AGENT_FIELDS[doctype]}` = {frappe.db.escape(self.sales_agent)}"

	def allows(self, doc, ptype: str) -> bool:
		if not self.is_limited or ptype == "create" or doc.is_new():
			return True
		return bool(self.sales_agent) and doc.get(AGENT_FIELDS[doc.doctype]) == self.sales_agent


def get_query_condition(user: str | None = None, doctype: str | None = None) -> str:
	return AgentAccess(user).query_condition(doctype)


def has_permission(doc, ptype: str | None = None, user: str | None = None, debug: bool = False) -> bool:
	return AgentAccess(user).allows(doc, ptype)
