import base64
from io import BytesIO

import frappe
from frappe.utils import today
from PIL import Image

from epasi.epasi.collateral_photos import CollateralPhotos
from epasi.epasi.doctype.borrower.borrower import Borrower


def make_photo(image_format: str = "JPEG") -> dict:
	buffer = BytesIO()
	Image.new("RGB", (10, 10), "gold").save(buffer, format=image_format)
	return {"content": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()}


def make_borrower(whatsapp_number: str = "0972000100") -> str:
	return Borrower.get_or_create("Test Borrower", whatsapp_number).name


def make_application(loan_plan: str = "2 Weeks", amount: float = 1000, status: str = "Approved") -> str:
	application = frappe.get_doc(
		doctype="Loan Application",
		borrower=make_borrower(),
		loan_plan=loan_plan,
		amount=amount,
		status=status,
		collateral_description="Television",
		estimated_value=2500,
	).insert()
	photos = CollateralPhotos([make_photo()])
	photos.validate()
	photos.attach_to("Loan Application", application.name)
	return application.name


def make_loan(
	loan_plan: str = "2 Weeks", principal: float = 1000, disbursement_date: str | None = None, **fields
):
	return frappe.get_doc(
		doctype="Loan",
		loan_plan=loan_plan,
		principal=principal,
		disbursement_date=disbursement_date or today(),
		**{"borrower": make_borrower(), **fields},
	).insert()


def make_repayment(loan: str, amount: float, submit: bool = True, **fields):
	repayment = frappe.get_doc(doctype="Loan Repayment", loan=loan, amount=amount, **fields).insert()
	if submit:
		repayment.submit()
	return repayment


def make_loan_with_collateral() -> tuple:
	application = frappe.get_doc("Loan Application", make_application())
	loan = frappe.get_doc("Loan", application.create_loan())
	loan.submit()
	return loan, frappe.get_doc("Collateral", {"loan": loan.name})


def make_expense(amount: float, expense_date: str | None = None, category: str = "Transport"):
	return frappe.get_doc(
		doctype="Expense", amount=amount, expense_date=expense_date or today(), category=category
	).insert()


def make_sales_agent(
	full_name: str = "Mwila Banda", commission_rate: float = 15, minimum_principal: float = 10000, **fields
):
	return frappe.get_doc(
		doctype="Sales Agent",
		full_name=full_name,
		commission_rate=commission_rate,
		minimum_principal=minimum_principal,
		**fields,
	).insert()


def make_user(email: str, first_name: str = "Test") -> str:
	if not frappe.db.exists("User", email):
		frappe.get_doc(doctype="User", email=email, first_name=first_name, send_welcome_email=0).insert()
	return email


def make_agent_with_user(email: str, agent_type: str = "Loan Officer", full_name: str = "Mwila Banda"):
	return make_sales_agent(full_name, agent_type=agent_type, user=make_user(email))
