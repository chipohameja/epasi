import base64
import binascii
from io import BytesIO

import frappe
from frappe import _
from PIL import Image, UnidentifiedImageError

MAXIMUM_PHOTOS = 5
MAXIMUM_PHOTO_SIZE = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class CollateralPhotos:
	"""Validates base64 photos from the public form and attaches them as private files."""

	def __init__(self, photos: list[dict]):
		self.photos = photos or []

	def validate(self):
		if not 1 <= len(self.photos) <= MAXIMUM_PHOTOS:
			frappe.throw(_("Add between 1 and {0} photos of your collateral").format(MAXIMUM_PHOTOS))
		self.images = [self.decode(photo) for photo in self.photos]

	def attach_to(self, doctype: str, name: str):
		for number, (content, extension) in enumerate(self.images, start=1):
			frappe.get_doc(
				doctype="File",
				file_name=f"{name}-collateral-{number}.{extension}",
				attached_to_doctype=doctype,
				attached_to_name=name,
				is_private=1,
				content=content,
			).insert(ignore_permissions=True)

	def decode(self, photo: dict) -> tuple[bytes, str]:
		try:
			content = base64.b64decode(photo.get("content", "").split(",")[-1], validate=True)
		except binascii.Error:
			frappe.throw(_("A photo could not be read. Please choose it again."))
		if len(content) > MAXIMUM_PHOTO_SIZE:
			frappe.throw(_("Each photo must be smaller than 5 MB"))
		return content, self.get_extension(content)

	def get_extension(self, content: bytes) -> str:
		try:
			image_format = Image.open(BytesIO(content)).format
		except UnidentifiedImageError:
			image_format = None
		if image_format not in ALLOWED_FORMATS:
			frappe.throw(_("Photos must be JPEG, PNG or WEBP images"))
		return image_format.lower()


def copy_photos(from_doctype: str, from_name: str, to_doctype: str, to_name: str):
	files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": from_doctype, "attached_to_name": from_name},
		fields=["file_name", "file_url", "is_private"],
	)
	for file in files:
		frappe.get_doc(doctype="File", attached_to_doctype=to_doctype, attached_to_name=to_name, **file).insert(
			ignore_permissions=True
		)
