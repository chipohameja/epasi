import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

from epasi.epasi.doctype.borrower.borrower import Borrower, normalize_whatsapp_number


class TestNormalizeWhatsappNumber(UnitTestCase):
	def test_local_and_international_formats_match(self):
		for number in ("0972616440", "+260 972 616 440", "260-972-616-440"):
			self.assertEqual(normalize_whatsapp_number(number), "260972616440")

	def test_short_number_is_rejected(self):
		self.assertRaises(frappe.ValidationError, normalize_whatsapp_number, "12345")


class TestBorrower(IntegrationTestCase):
	def test_get_or_create_reuses_borrower(self):
		first = Borrower.get_or_create("Test Borrower", "0971000001")
		second = Borrower.get_or_create("Test Borrower", "+260971000001")
		self.assertEqual(first.name, "260971000001")
		self.assertEqual(first.name, second.name)
