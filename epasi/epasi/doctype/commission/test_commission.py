import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from epasi.epasi.money import MoneySummary
from epasi.tests.utils import make_loan, make_repayment, make_sales_agent


def make_agent_loan(principal: float = 12000, sales_agent: str | None = None):
	loan = make_loan("1 Month", principal, sales_agent=sales_agent or make_sales_agent().name)
	loan.submit()
	return loan


def repay_in_full(loan) -> str:
	return make_repayment(loan.name, loan.outstanding).name


def get_commission(loan) -> dict | None:
	return frappe.db.get_value("Commission", {"loan": loan.name}, ["amount", "status"], as_dict=True)


class TestCommission(IntegrationTestCase):
	def test_repaid_loan_above_minimum_earns_share_of_interest(self):
		loan = make_agent_loan(12000)
		self.assertIsNone(get_commission(loan))
		repay_in_full(loan)
		self.assertEqual(get_commission(loan), {"amount": 720, "status": "Unpaid"})

	def test_loan_not_above_minimum_earns_nothing(self):
		loan = make_agent_loan(10000)
		repay_in_full(loan)
		self.assertIsNone(get_commission(loan))

	def test_defaulted_loan_earns_nothing(self):
		loan = make_agent_loan()
		make_repayment(loan.name, 500)
		loan.reload().mark_defaulted()
		self.assertIsNone(get_commission(loan))

	def test_rate_is_locked_when_loan_is_submitted(self):
		loan = make_agent_loan()
		frappe.db.set_value("Sales Agent", loan.sales_agent, "commission_rate", 50)
		repay_in_full(loan)
		self.assertEqual(get_commission(loan).amount, 720)

	def test_unpaid_commission_is_removed_when_loan_reopens(self):
		loan = make_agent_loan()
		repayment = repay_in_full(loan)
		frappe.get_doc("Loan Repayment", repayment).cancel()
		self.assertIsNone(get_commission(loan))

	def test_mark_paid_records_expense_and_lowers_profit(self):
		loan = make_agent_loan()
		repay_in_full(loan)
		profit_before = MoneySummary(today(), today()).net_profit
		commission = frappe.get_doc("Commission", {"loan": loan.name})
		commission.mark_paid()
		expense = frappe.get_doc("Expense", commission.expense)
		self.assertEqual((commission.status, commission.paid_date), ("Paid", today()))
		self.assertEqual((expense.category, expense.amount), ("Commission", 720))
		self.assertEqual(MoneySummary(today(), today()).net_profit, profit_before - 720)
		self.assertRaises(frappe.ValidationError, commission.mark_paid)

	def test_agent_totals_follow_commissions(self):
		first = make_agent_loan()
		second = make_agent_loan(sales_agent=first.sales_agent)
		repay_in_full(first)
		repay_in_full(second)
		frappe.get_doc("Commission", {"loan": first.name}).mark_paid()
		totals = frappe.db.get_value(
			"Sales Agent", first.sales_agent, ["commission_earned", "commission_paid", "commission_unpaid"]
		)
		self.assertEqual(totals, (1440, 720, 720))
