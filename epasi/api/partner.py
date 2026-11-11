import frappe
from frappe import _

from epasi.epasi.doctype.sales_agent.sales_agent import SalesAgent

AGENT_FIELDS = ["full_name", "referral_link", "commission_earned", "commission_paid", "commission_unpaid"]


@frappe.whitelist()
def get_partner_summary() -> dict:
	sales_agent = SalesAgent.for_user()
	if not sales_agent:
		frappe.throw(_("Your account is not linked to a sales agent"), frappe.PermissionError)
	return PartnerSummary(sales_agent).as_dict()


class PartnerSummary:
	"""What a sales agent may see about the borrowers they referred."""

	def __init__(self, sales_agent: str):
		self.sales_agent = sales_agent

	def as_dict(self) -> dict:
		agent = frappe.db.get_value("Sales Agent", self.sales_agent, AGENT_FIELDS, as_dict=True)
		return {**agent, "referrals": self.get_referrals()}

	def get_referrals(self) -> list[dict]:
		applications = frappe.get_all(
			"Loan Application",
			filters={"sales_agent": self.sales_agent},
			fields=["name", "applicant_name", "status", "creation"],
			order_by="creation desc",
		)
		loans = self.get_loans([application.name for application in applications])
		return [self.get_referral(application, loans.get(application.name)) for application in applications]

	def get_loans(self, applications: list[str]) -> dict:
		loans = frappe.get_all(
			"Loan",
			filters={"loan_application": ["in", applications or [""]], "docstatus": 1},
			fields=["name", "loan_application", "status"],
		)
		commissions = self.get_commissions([loan.name for loan in loans])
		return {loan.loan_application: {**loan, **commissions.get(loan.name, {})} for loan in loans}

	def get_commissions(self, loans: list[str]) -> dict:
		rows = frappe.get_all(
			"Commission",
			filters={"loan": ["in", loans or [""]]},
			fields=["loan", "amount", "status"],
		)
		return {row.loan: {"commission": row.amount, "commission_status": row.status} for row in rows}

	def get_referral(self, application, loan: dict | None) -> dict:
		loan = loan or {}
		return {
			"name": short_name(application.applicant_name),
			"date": application.creation.date(),
			"status": loan.get("status") or application.status,
			"commission": loan.get("commission", 0),
			"commission_status": loan.get("commission_status"),
		}


def short_name(full_name: str | None) -> str:
	first, *rest = (full_name or "").split() or [""]
	return f"{first} {rest[-1][0]}." if rest else first
