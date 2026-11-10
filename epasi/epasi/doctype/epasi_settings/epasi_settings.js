frappe.ui.form.on("Epasi Settings", {
	refresh(frm) {
		frm.disable_save();
	},
	generate_test_data(frm) {
		frm.call("generate_test_data");
	},
	clear_test_data(frm) {
		frappe.confirm(__("Delete all the test data records?"), () => frm.call("clear_test_data"));
	},
});
