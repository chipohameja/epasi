import frappe
from frappe import _
from frappe.model.document import Document

from epasi.epasi.doctype.borrower.borrower import normalize_whatsapp_number

MAXIMUM_STARS = 5
MAXIMUM_COMMENT_LENGTH = 300
HOME_PAGE_LIMIT = 3


class Review(Document):
	def validate(self):
		self.validate_rating()
		self.validate_comment()
		if self.is_new():
			self.validate_one_per_application()
			self.set_reviewer()

	def validate_rating(self):
		if not 1 <= self.stars <= MAXIMUM_STARS:
			frappe.throw(_("Choose a rating from 1 to 5 stars"))

	def validate_comment(self):
		self.comment = (self.comment or "").strip()
		if not self.comment or len(self.comment) > MAXIMUM_COMMENT_LENGTH:
			frappe.throw(_("Write a comment of at most {0} characters").format(MAXIMUM_COMMENT_LENGTH))

	def validate_one_per_application(self):
		if frappe.db.exists("Review", {"loan_application": self.loan_application}):
			frappe.throw(_("You have already reviewed this application. Thank you!"))

	def set_reviewer(self):
		self.borrower = frappe.db.get_value("Loan Application", self.loan_application, "borrower")
		full_name = frappe.db.get_value("Borrower", self.borrower, "full_name")
		self.display_name = short_name(full_name)

	@property
	def stars(self) -> int:
		return round((self.rating or 0) * MAXIMUM_STARS)

	@staticmethod
	def create(application: str, whatsapp_number: str, stars: int, comment: str) -> "Review":
		borrower = frappe.db.get_value("Loan Application", application, "borrower")
		if not borrower or borrower != normalize_whatsapp_number(whatsapp_number):
			frappe.throw(_("We could not find an application with this reference and WhatsApp number"))
		return frappe.get_doc(
			doctype="Review",
			loan_application=application,
			rating=int(stars) / MAXIMUM_STARS,
			comment=comment,
		).insert(ignore_permissions=True)

	@staticmethod
	def published() -> list[dict]:
		reviews = frappe.get_all(
			"Review",
			filters={"is_published": 1},
			fields=["display_name", "rating", "comment"],
			order_by="creation desc",
			limit=HOME_PAGE_LIMIT,
		)
		return [frappe._dict(review, rating=round(review.rating * MAXIMUM_STARS)) for review in reviews]


def short_name(full_name: str) -> str:
	parts = (full_name or "").split()
	if len(parts) < 2:
		return parts[0] if parts else _("Client")
	return f"{parts[0]} {parts[-1][0].upper()}."
