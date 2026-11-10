frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Epasi Chart"] = {
	method: "epasi.api.dashboard.get_chart",
	filters: [],
};
