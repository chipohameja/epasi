frappe.provide("epasi");

epasi.add_whatsapp_button = function (frm) {
	if (frm.is_new() || !frm.doc.whatsapp_number) return;
	frm.add_custom_button(__("Chat on WhatsApp"), () => {
		window.open(`https://wa.me/${frm.doc.whatsapp_number}`, "_blank");
	});
};

epasi.render_photos = function (frm) {
	const photos = frm.get_docinfo().attachments.filter((file) => frappe.utils.is_image_file(file.file_url));
	const thumbnails = photos.map(
		(file) => `<a href="${file.file_url}" target="_blank">
			<img src="${file.file_url}" style="height: 120px; border-radius: 8px; object-fit: cover;">
		</a>`
	);
	frm.get_field("photos_html").$wrapper.html(
		`<div style="display: flex; flex-wrap: wrap; gap: 8px;">${
			thumbnails.join("") || __("No photos")
		}</div>`
	);
};
