import frappe

CURRENCY = "ZMW"
LOAN_PLANS = [
	{"plan_name": "2 Weeks", "interest_rate": 27, "term_days": 14},
	{"plan_name": "1 Month", "interest_rate": 40, "term_days": 30},
]
DEFAULT_LIMITS = {"minimum_amount": 100, "maximum_amount": 50000}


def after_install():
	set_default_currency()
	create_loan_plans()


def set_default_currency():
	frappe.db.set_value("Currency", CURRENCY, "enabled", 1)
	frappe.db.set_single_value("System Settings", "currency", CURRENCY)


def create_loan_plans():
	for plan in LOAN_PLANS:
		if not frappe.db.exists("Loan Plan", plan["plan_name"]):
			frappe.get_doc(doctype="Loan Plan", **plan, **DEFAULT_LIMITS).insert(ignore_permissions=True)
