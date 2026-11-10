import frappe
from frappe import _
from frappe.model.document import Document

from epasi.setup.test_data import TestData


class EpasiSettings(Document):
	@frappe.whitelist()
	def generate_test_data(self):
		frappe.only_for("System Manager")
		TestData().generate()
		frappe.msgprint(_("Test data generated"), indicator="green", alert=True)

	@frappe.whitelist()
	def clear_test_data(self):
		frappe.only_for("System Manager")
		TestData().clear()
		frappe.msgprint(_("Test data cleared"), indicator="green", alert=True)
