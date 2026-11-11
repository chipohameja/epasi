import frappe
from frappe.tests import IntegrationTestCase

from epasi.api.partner import get_partner_summary, short_name
from epasi.tests.utils import make_agent_with_user, make_borrower, make_sales_agent

REFERRER = "referrer@epasi.test"


def make_referral(whatsapp_number: str, sales_agent: str, full_name: str = "Mwila Banda"):
	borrower = make_borrower(whatsapp_number)
	frappe.db.set_value("Borrower", borrower, "full_name", full_name)
	return frappe.get_doc(
		doctype="Loan Application",
		borrower=borrower,
		loan_plan="2 Weeks",
		amount=1000,
		sales_agent=sales_agent,
	).insert()


class TestPartnerApi(IntegrationTestCase):
	def setUp(self):
		self.addCleanup(frappe.set_user, "Administrator")

	def test_returns_only_callers_referrals_without_contact_details(self):
		agent = make_agent_with_user(REFERRER, "Referrer", "Bupe Zulu")
		make_referral("0972000401", agent.name, "Chanda Mwale Phiri")
		make_referral("0972000402", make_sales_agent("Other Agent").name)
		frappe.set_user(REFERRER)
		summary = get_partner_summary()
		self.assertEqual(summary["referral_link"], agent.referral_link)
		self.assertEqual(
			[(row["name"], row["status"]) for row in summary["referrals"]], [("Chanda P.", "Pending")]
		)
		self.assertNotIn("972000401", frappe.as_json(summary))

	def test_user_without_agent_is_refused(self):
		frappe.set_user("Guest")
		self.assertRaises(frappe.PermissionError, get_partner_summary)

	def test_short_name(self):
		self.assertEqual(
			[short_name("Mwila Banda"), short_name("Mwila"), short_name(None)], ["Mwila B.", "Mwila", ""]
		)
