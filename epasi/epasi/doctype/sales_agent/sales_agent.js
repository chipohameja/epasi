frappe.ui.form.on("Sales Agent", {
	refresh(frm) {
		if (!frm.doc.referral_link) return;
		frm.add_custom_button(__("Copy Referral Link"), () =>
			frappe.utils.copy_to_clipboard(frm.doc.referral_link)
		);
	},
});
