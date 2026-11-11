import frappe
from frappe.model.document import Document
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_agent_with_user, make_borrower, make_loan, make_sales_agent

OFFICER = "officer@epasi.test"


def make_walk_in(whatsapp_number: str) -> Document:
	return frappe.get_doc(
		doctype="Loan Application",
		borrower=make_borrower(whatsapp_number),
		loan_plan="2 Weeks",
		amount=1000,
		status="Approved",
	).insert()


class TestAgentAccess(IntegrationTestCase):
	def setUp(self):
		self.officer = make_agent_with_user(OFFICER)
		self.addCleanup(frappe.set_user, "Administrator")

	def test_saving_agent_gives_user_the_role(self):
		self.assertIn("Loan Officer", frappe.get_roles(OFFICER))
		make_agent_with_user("referrer@epasi.test", "Referrer", "Bupe Zulu")
		self.assertIn("Referrer", frappe.get_roles("referrer@epasi.test"))

	def test_walk_in_is_linked_to_officer(self):
		frappe.set_user(OFFICER)
		application = make_walk_in("0972000301")
		self.assertEqual(application.sales_agent, self.officer.name)
		self.assertEqual(application.status, "Pending")
		self.assertEqual(frappe.db.get_value("Borrower", "260972000301", "sales_agent"), self.officer.name)

	def test_officer_sees_only_own_records(self):
		other = make_sales_agent("Chanda Mwale").name
		other_loan = make_loan(sales_agent=other, borrower=make_borrower("0972000302"))
		frappe.set_user(OFFICER)
		own = make_walk_in("0972000303").name
		self.assertEqual(frappe.get_list("Loan Application", pluck="name"), [own])
		self.assertEqual(frappe.get_list("Sales Agent", pluck="name"), [self.officer.name])
		self.assertFalse(frappe.has_permission("Loan", "read", other_loan.name))

	def test_officer_cannot_issue_a_loan(self):
		frappe.set_user(OFFICER)
		application = make_walk_in("0972000304")
		frappe.set_user("Administrator")
		application.db_set("status", "Approved")
		frappe.set_user(OFFICER)
		self.assertRaises(frappe.PermissionError, application.reload().create_loan)
