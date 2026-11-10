frappe.ui.form.on("Loan", {
	refresh(frm) {
		epasi.add_whatsapp_button(frm);
		if (frm.doc.docstatus !== 1) return;
		if (frm.doc.status !== "Closed") add_repayment_button(frm);
		if (["Active", "Overdue"].includes(frm.doc.status)) add_mark_defaulted_button(frm);
	},
});

function add_repayment_button(frm) {
	frm.add_custom_button(__("Record Repayment"), () => {
		frappe.new_doc("Loan Repayment", { loan: frm.doc.name, amount: frm.doc.outstanding });
	}).addClass("btn-primary");
}

function add_mark_defaulted_button(frm) {
	frm.add_custom_button(__("Mark Defaulted"), () => {
		frappe.confirm(__("Mark this loan as defaulted and forfeit its collateral?"), () =>
			frm.call("mark_defaulted").then(() => frm.reload_doc())
		);
	});
}
