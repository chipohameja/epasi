import frappe
from frappe.tests import IntegrationTestCase

from epasi.setup.test_data import TestData


class TestEpasiSettings(IntegrationTestCase):
	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		TestData().restore_photos()

	def setUp(self):
		self.test_data = TestData()
		self.test_data.clear()

	def test_generate_restores_every_record(self):
		self.test_data.generate()
		for record in self.test_data.records:
			self.assertTrue(TestData.exists(record), record["name"])

	def test_generate_twice_is_refused(self):
		self.test_data.generate()
		self.assertRaises(frappe.ValidationError, self.test_data.generate)

	def test_clear_keeps_other_records(self):
		self.test_data.generate()
		borrower = frappe.get_doc(doctype="Borrower", full_name="Kept Borrower", whatsapp_number="0971999999").insert()
		self.test_data.clear()
		self.assertFalse(any(TestData.exists(record) for record in self.test_data.records))
		self.assertTrue(frappe.db.exists("Borrower", borrower.name))

	def test_new_application_does_not_reuse_a_test_name(self):
		self.test_data.generate()
		application = frappe.get_doc(
			doctype="Loan Application", borrower="260972616441", loan_plan="2 Weeks", amount=100,
			collateral_description="Phone", estimated_value=300,
		).insert()
		self.assertGreater(application.name, "APP-00008")
