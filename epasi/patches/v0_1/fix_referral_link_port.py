import frappe

from epasi.epasi.doctype.sales_agent.sales_agent import make_referral_link


def execute():
	for agent in frappe.get_all("Sales Agent", fields=["name", "referral_code"]):
		frappe.db.set_value(
			"Sales Agent",
			agent.name,
			"referral_link",
			make_referral_link(agent.referral_code),
			update_modified=False,
		)
