frappe.query_reports["Outstanding Loans"] = {
	filters: [
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Active", "Overdue", "Defaulted"],
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "days_overdue" && data && data.days_overdue > 0) {
			return `<span class="text-danger">${value}</span>`;
		}
		return value;
	},
};
