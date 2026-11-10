import base64

import frappe
from frappe.tests import IntegrationTestCase

from epasi.epasi.collateral_photos import MAXIMUM_PHOTO_SIZE, CollateralPhotos
from epasi.tests.utils import make_photo


class TestCollateralPhotos(IntegrationTestCase):
	def test_photo_count_is_limited(self):
		self.assertRaises(frappe.ValidationError, CollateralPhotos([]).validate)
		self.assertRaises(frappe.ValidationError, CollateralPhotos([make_photo()] * 6).validate)

	def test_non_image_is_rejected(self):
		text = {"content": base64.b64encode(b"<script>alert(1)</script>").decode()}
		self.assertRaises(frappe.ValidationError, CollateralPhotos([text]).validate)

	def test_large_photo_is_rejected(self):
		large = {"content": base64.b64encode(b"0" * (MAXIMUM_PHOTO_SIZE + 1)).decode()}
		self.assertRaises(frappe.ValidationError, CollateralPhotos([large]).validate)

	def test_invalid_base64_is_rejected(self):
		self.assertRaises(frappe.ValidationError, CollateralPhotos([{"content": "not base64!"}]).validate)

	def test_photos_are_private_attachments_named_by_document(self):
		photos = CollateralPhotos([make_photo("JPEG"), make_photo("PNG")])
		photos.validate()
		photos.attach_to("Loan Plan", "2 Weeks")
		files = frappe.get_all(
			"File",
			filters={"attached_to_doctype": "Loan Plan", "attached_to_name": "2 Weeks"},
			fields=["file_name", "is_private"],
			order_by="file_name",
		)
		self.assertEqual([file.file_name for file in files], ["2 Weeks-collateral-1.jpeg", "2 Weeks-collateral-2.png"])
		self.assertTrue(all(file.is_private for file in files))
