import frappe
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_borrower, make_sales_agent


def make_application(whatsapp_number: str, sales_agent: str | None = None):
	return frappe.get_doc(
		doctype="Loan Application",
		borrower=make_borrower(whatsapp_number),
		loan_plan="2 Weeks",
		amount=1000,
		sales_agent=sales_agent,
	).insert()


class TestLoanApplication(IntegrationTestCase):
	def test_borrower_stays_with_first_agent(self):
		first = make_sales_agent("Mwila Banda").name
		second = make_sales_agent("Chanda Mwale").name
		make_application("0972000201", first)
		self.assertEqual(frappe.db.get_value("Borrower", "260972000201", "sales_agent"), first)
		self.assertEqual(make_application("0972000201", second).sales_agent, first)
		self.assertEqual(make_application("0972000201").sales_agent, first)

	def test_manager_can_change_agent_after_insert(self):
		application = make_application("0972000202", make_sales_agent("Mwila Banda").name)
		application.sales_agent = make_sales_agent("Chanda Mwale").name
		application.save()
		self.assertEqual(application.reload().sales_agent, application.sales_agent)

	def test_loan_takes_agent_from_application(self):
		agent = make_sales_agent().name
		application = make_application("0972000203", agent)
		application.db_set("status", "Approved")
		self.assertEqual(frappe.db.get_value("Loan", application.create_loan(), "sales_agent"), agent)
