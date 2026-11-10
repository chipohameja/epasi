frappe.ui.form.on("Loan Repayment", {
	setup(frm) {
		frm.set_query("loan", () => ({ filters: { docstatus: 1, status: ["!=", "Closed"] } }));
	},
});
