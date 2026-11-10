import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import date_diff, today

from epasi.epasi.report.daily_operations import daily_operations
from epasi.epasi.report.outstanding_loans import outstanding_loans
from epasi.epasi.report.profit_summary import profit_summary
from epasi.tests.utils import make_application, make_expense, make_loan, make_loan_with_collateral, make_repayment


def sell_collateral(sale_date: str, sale_amount: float):
	loan, collateral = make_loan_with_collateral()
	loan.mark_defaulted()
	collateral.reload()
	collateral.update({"status": "Sold", "sale_date": sale_date, "sale_amount": sale_amount})
	collateral.save()


class TestExpense(IntegrationTestCase):
	def test_amount_must_be_positive(self):
		self.assertRaises(frappe.ValidationError, make_expense, 0)


class TestOutstandingLoans(IntegrationTestCase):
	def test_lists_open_loans_with_days_overdue(self):
		late = make_loan(disbursement_date="2021-05-01")
		closed = make_loan()
		late.submit()
		closed.submit()
		make_repayment(closed.name, closed.outstanding)
		rows = {row.name: row for row in outstanding_loans.execute({})[1]}
		self.assertNotIn(closed.name, rows)
		self.assertEqual(rows[late.name].outstanding, 1270)
		self.assertEqual(rows[late.name].days_overdue, date_diff(today(), "2021-05-15"))

	def test_filters_by_status(self):
		loan = make_loan()
		loan.submit()
		rows = outstanding_loans.execute({"status": "Overdue"})[1]
		self.assertNotIn(loan.name, [row.name for row in rows])


class TestProfitSummary(IntegrationTestCase):
	def test_totals_and_daily_breakdown(self):
		loan = make_loan(disbursement_date="2021-06-01")
		loan.submit()
		make_repayment(loan.name, 500, payment_date="2021-06-03")
		make_expense(50, "2021-06-03")
		make_expense(30, "2021-06-04")
		sell_collateral("2021-06-04", 900)
		columns, data, _message, _chart, summary = profit_summary.execute(
			{"from_date": "2021-06-01", "to_date": "2021-06-30"}
		)
		self.assertEqual([row["net_profit"] for row in data], [220, 870])
		self.assertEqual([item["value"] for item in summary], [270, 900, 80, 1090])

	def test_rejects_reversed_dates(self):
		filters = {"from_date": "2021-06-30", "to_date": "2021-06-01"}
		self.assertRaises(frappe.ValidationError, profit_summary.execute, filters)


class TestDailyOperations(IntegrationTestCase):
	def test_lists_each_activity_for_the_date(self):
		loan = make_loan(disbursement_date="2021-07-01")
		loan.submit()
		make_repayment(loan.name, 300, payment_date="2021-07-01")
		make_expense(40, "2021-07-01")
		data, summary = daily_operations.execute({"date": "2021-07-01"})[1::3]
		self.assertEqual([row["activity"] for row in data], ["Disbursement", "Repayment", "Expense"])
		self.assertEqual([item["value"] for item in summary], [0, 1000, 300, 40])

	def test_lists_applications_received_today(self):
		application = make_application(status="Pending")
		data = daily_operations.execute({"date": today()})[1]
		self.assertIn(application, [row["document"] for row in data])
