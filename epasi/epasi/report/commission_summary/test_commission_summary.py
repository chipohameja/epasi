import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from epasi.epasi.doctype.commission.test_commission import make_agent_loan, repay_in_full
from epasi.epasi.report.commission_summary.commission_summary import execute


class TestCommissionSummary(IntegrationTestCase):
	def test_totals_per_agent(self):
		first = make_agent_loan()
		second = make_agent_loan(sales_agent=first.sales_agent)
		repay_in_full(first)
		repay_in_full(second)
		frappe.get_doc("Commission", {"loan": first.name}).mark_paid()
		_columns, data = execute({"from_date": today(), "to_date": today(), "sales_agent": first.sales_agent})
		self.assertEqual([(row["earned"], row["paid"], row["unpaid"]) for row in data], [(1440, 720, 720)])
