import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from epasi.epasi.doctype.sales_agent.sales_agent import SalesAgent

ZAMBIA_COUNTRY_CODE = "260"


class Borrower(Document):
	def before_naming(self):
		self.whatsapp_number = normalize_whatsapp_number(self.whatsapp_number)

	def validate(self):
		self.whatsapp_number = normalize_whatsapp_number(self.whatsapp_number)
		if self.is_new() and not self.sales_agent:
			self.sales_agent = SalesAgent.for_user(agent_type="Loan Officer")

	def update_totals(self):
		totals = frappe.get_all(
			"Loan",
			filters={"borrower": self.name, "docstatus": 1},
			fields=[{"SUM": "principal", "as": "borrowed"}, {"SUM": "outstanding", "as": "outstanding"}],
		)[0]
		self.db_set({"total_borrowed": flt(totals.borrowed), "total_outstanding": flt(totals.outstanding)})

	@staticmethod
	def get_or_create(
		full_name: str, whatsapp_number: str, nrc_number: str | None = None, address: str | None = None
	) -> "Borrower":
		number = normalize_whatsapp_number(whatsapp_number)
		if frappe.db.exists("Borrower", number):
			borrower = frappe.get_doc("Borrower", number)
		else:
			borrower = frappe.new_doc("Borrower", whatsapp_number=number)
		borrower.full_name = full_name
		borrower.nrc_number = nrc_number or borrower.nrc_number
		borrower.address = address or borrower.address
		return borrower.save(ignore_permissions=True)


def normalize_whatsapp_number(number: str) -> str:
	digits = re.sub(r"\D", "", number or "")
	if digits.startswith("0"):
		digits = ZAMBIA_COUNTRY_CODE + digits[1:]
	if not 11 <= len(digits) <= 15:
		frappe.throw(_("Enter a valid WhatsApp number, for example 0972616440"))
	return digits
