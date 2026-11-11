frappe.ui.form.on("Commission", {
	refresh(frm) {
		if (frm.doc.status !== "Unpaid" || !frm.perm[0]?.write) return;
		frm.add_custom_button(__("Mark Paid"), () =>
			frappe.confirm(
				__("Pay {0} and record it as an expense?", [format_currency(frm.doc.amount)]),
				() => frm.call("mark_paid").then(() => frm.reload_doc())
			)
		).addClass("btn-primary");
	},
});
