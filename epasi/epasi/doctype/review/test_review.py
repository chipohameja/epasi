import frappe
from frappe.tests import IntegrationTestCase

from epasi.api.dashboard import get_reviews_awaiting_approval
from epasi.api.public import get_reviews, submit_review
from epasi.epasi.doctype.review.review import short_name
from epasi.tests.utils import make_application


def review(application: str, whatsapp_number: str = "0972000100", rating: int = 5, comment: str = "Fast!"):
	return frappe.get_doc("Review", submit_review(application, whatsapp_number, rating, comment)["name"])


class TestReview(IntegrationTestCase):
	def setUp(self):
		self.application = make_application(status="Pending")
		frappe.set_user("Guest")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_review_is_saved_unpublished_with_short_name(self):
		saved = review(self.application, rating=4)
		self.assertEqual((saved.stars, saved.is_published), (4, 0))
		self.assertEqual(saved.display_name, "Test B.")
		self.assertEqual(saved.borrower, "260972000100")

	def test_wrong_whatsapp_number_is_refused(self):
		self.assertRaises(frappe.ValidationError, review, self.application, "0972999999")

	def test_unknown_application_is_refused(self):
		self.assertRaises(frappe.ValidationError, review, "APP-99999")

	def test_second_review_for_application_is_refused(self):
		review(self.application)
		self.assertRaises(frappe.ValidationError, review, self.application)

	def test_rating_and_comment_are_checked(self):
		self.assertRaises(frappe.ValidationError, review, self.application, rating=0)
		self.assertRaises(frappe.ValidationError, review, self.application, comment=" ")
		self.assertRaises(frappe.ValidationError, review, self.application, comment="x" * 301)

	def test_only_published_reviews_are_listed(self):
		saved = review(self.application, comment="Great service")
		self.assertNotIn("Great service", [row.comment for row in get_reviews()])
		frappe.set_user("Administrator")
		saved.db_set("is_published", 1)
		listed = get_reviews()[0]
		self.assertEqual(
			(listed.comment, listed.rating, listed.display_name), ("Great service", 5, "Test B.")
		)

	def test_unpublished_reviews_are_counted_for_managers(self):
		frappe.set_user("Administrator")
		before = get_reviews_awaiting_approval()["value"]
		frappe.set_user("Guest")
		review(self.application)
		frappe.set_user("Administrator")
		self.assertEqual(get_reviews_awaiting_approval()["value"], before + 1)

	def test_short_name(self):
		self.assertEqual(short_name("mwila  chanda banda"), "mwila B.")
		self.assertEqual(short_name("Mwila"), "Mwila")
		self.assertEqual(short_name(""), "Client")
