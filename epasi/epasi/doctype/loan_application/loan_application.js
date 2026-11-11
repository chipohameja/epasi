frappe.ui.form.on("Loan Application", {
	refresh(frm) {
		epasi.add_whatsapp_button(frm);
		epasi.render_photos(frm);
		add_create_loan_button(frm);
	},
});

function add_create_loan_button(frm) {
	if (frm.doc.status !== "Approved" || frm.is_dirty() || !frappe.model.can_create("Loan"))
		return;
	frm.add_custom_button(__("Create Loan"), () => {
		frm.call("create_loan").then(({ message }) => frappe.set_route("Form", "Loan", message));
	}).addClass("btn-primary");
}
