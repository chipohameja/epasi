import frappe
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_user


class TestUserGuidePage(IntegrationTestCase):
	def test_only_system_manager_can_open_guide(self):
		page = frappe.get_doc("Page", "user-guide")
		self.assertTrue(page.is_permitted())
		user = make_user("guide-manager@example.com")
		frappe.get_doc("User", user).add_roles("Loan Manager")
		with self.set_user(user):
			self.assertFalse(page.is_permitted())
