import json
import os
import shutil

import frappe
from frappe import _
from frappe.model.naming import NamingSeries
from frappe.utils.password import update_password

DOCTYPES = (
	"Borrower",
	"Loan Application",
	"Loan",
	"Loan Repayment",
	"Collateral",
	"Expense",
	"Sales Agent",
	"Commission",
)
USER_PASSWORD = "Epasi@2026test"
FOLDER = os.path.dirname(__file__)
RECORDS_PATH = os.path.join(FOLDER, "records.json")
FILES_FOLDER = os.path.join(FOLDER, "files")


class TestData:
	"""Restores or removes a snapshot of Epasi records kept in this folder."""

	def __init__(self):
		with open(RECORDS_PATH) as records_file:
			self.records = json.load(records_file)

	def generate(self):
		if existing := [record["name"] for record in self.records if self.exists(record)]:
			message = _("Clear the test data first. These records already exist: {0}")
			frappe.throw(message.format(", ".join(existing)))
		for record in self.records:
			self.insert(record)

	def clear(self):
		for record in reversed(self.records):
			if self.exists(record):
				self.delete(record["doctype"], record["name"])

	def delete(self, doctype: str, name: str):
		if frappe.db.get_value(doctype, name, "docstatus") == 1:
			frappe.db.set_value(doctype, name, "docstatus", 2, update_modified=False)
		frappe.delete_doc(doctype, name, force=True, ignore_permissions=True, delete_permanently=True)

	def insert(self, record: dict):
		document = frappe.get_doc(record)
		document.db_insert()
		for child in document.get_all_children():
			child.db_insert()
		if document.doctype == "File":
			self.copy_photo(document)
		elif document.doctype == "User":
			update_password(document.name, USER_PASSWORD)
		elif document.meta.autoname.startswith("format:"):
			self.update_series(document)

	def update_series(self, document):
		# format:XXX-{#####} names share one counter, stored under an empty prefix.
		series = NamingSeries("#####")
		number = int(document.name.rpartition("-")[2])
		series.update_counter(max(series.get_current_value(), number))

	def restore_photos(self):
		"""Copies photos back to disk for test records that still exist."""
		for record in self.records:
			if record["doctype"] == "File" and self.exists(record):
				self.copy_photo(frappe.get_doc("File", record["name"]))

	def copy_photo(self, file):
		shutil.copy(os.path.join(FILES_FOLDER, file.file_name), file.get_full_path())

	@staticmethod
	def exists(record: dict) -> bool:
		return bool(frappe.db.exists(record["doctype"], record["name"]))


def export():
	"""Saves the site's current Epasi records as the test data. Run with bench execute."""
	users = frappe.get_all("Sales Agent", filters={"user": ["is", "set"]}, pluck="user")
	records = [get_record("User", user) for user in users]
	records += [get_record(doctype, name) for doctype in DOCTYPES for name in get_names(doctype)]
	os.makedirs(FILES_FOLDER, exist_ok=True)
	for name in frappe.get_all("File", filters={"attached_to_doctype": ["in", DOCTYPES]}, pluck="name"):
		records.append(get_record("File", name))
		shutil.copy(frappe.get_doc("File", name).get_full_path(), FILES_FOLDER)
	with open(RECORDS_PATH, "w") as records_file:
		records_file.write(frappe.as_json(records) + "\n")


def get_names(doctype: str) -> list[str]:
	return frappe.get_all(doctype, pluck="name", order_by="creation")


def get_record(doctype: str, name: str) -> dict:
	return frappe.get_doc(doctype, name).as_dict(no_default_fields=False, convert_dates_to_str=True)
