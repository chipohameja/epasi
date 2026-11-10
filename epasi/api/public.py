import frappe
from frappe.rate_limiter import rate_limit

from epasi.epasi.collateral_photos import CollateralPhotos
from epasi.epasi.doctype.borrower.borrower import Borrower

PLAN_FIELDS = ["name", "interest_rate", "term_days", "minimum_amount", "maximum_amount"]


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_loan_plans() -> list[dict]:
	return frappe.get_all("Loan Plan", filters={"is_active": 1}, fields=PLAN_FIELDS, order_by="term_days")


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=60 * 60)
def submit_application(
	full_name: str,
	whatsapp_number: str,
	loan_plan: str,
	amount: float,
	photos: list[dict],
	nrc_number: str | None = None,
	address: str | None = None,
	purpose: str | None = None,
	collateral_description: str | None = None,
	estimated_value: float | None = None,
) -> dict:
	collateral_photos = CollateralPhotos(photos)
	collateral_photos.validate()
	borrower = Borrower.get_or_create(full_name, whatsapp_number, nrc_number, address)
	application = frappe.get_doc(
		doctype="Loan Application",
		borrower=borrower.name,
		loan_plan=loan_plan,
		amount=amount,
		purpose=purpose,
		collateral_description=collateral_description,
		estimated_value=estimated_value,
	).insert(ignore_permissions=True)
	collateral_photos.attach_to("Loan Application", application.name)
	return {"name": application.name}
