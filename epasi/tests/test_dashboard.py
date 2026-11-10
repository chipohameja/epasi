import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from epasi.api import dashboard
from epasi.tests.utils import make_application, make_expense, make_loan, make_repayment


def card_values() -> dict:
	cards = [
		"get_pending_applications",
		"get_loans_due_today",
		"get_overdue_loans",
		"get_overdue_amount",
		"get_total_outstanding",
		"get_lent_this_month",
		"get_collected_this_month",
		"get_net_profit_this_month",
	]
	return {name: getattr(dashboard, name)()["value"] for name in cards}


class TestDashboardCards(IntegrationTestCase):
	def test_cards_follow_loans_repayments_and_expenses(self):
		before = card_values()
		make_application(status="Pending")
		current = make_loan(principal=1000)
		current.submit()
		late = make_loan(principal=2000, disbursement_date=add_days(today(), -20))
		late.submit()
		make_repayment(current.name, 300)
		make_expense(50)
		change = {name: value - before[name] for name, value in card_values().items()}
		self.assertEqual(change["get_pending_applications"], 1)
		self.assertEqual(change["get_overdue_loans"], 1)
		self.assertEqual(change["get_overdue_amount"], 2540)
		self.assertEqual(change["get_total_outstanding"], 1270 - 300 + 2540)
		self.assertEqual(change["get_collected_this_month"], 300)
		self.assertEqual(change["get_net_profit_this_month"], 270 - 50)

	def test_loan_due_today(self):
		before = dashboard.get_loans_due_today()["value"]
		make_loan(disbursement_date=add_days(today(), -14)).submit()
		self.assertEqual(dashboard.get_loans_due_today()["value"], before + 1)

	def test_guest_is_refused(self):
		frappe.set_user("Guest")
		try:
			self.assertRaises(frappe.PermissionError, dashboard.get_overdue_loans)
		finally:
			frappe.set_user("Administrator")


class TestDashboardCharts(IntegrationTestCase):
	def test_lent_vs_collected_has_twelve_weeks(self):
		before = dashboard.get_chart("Lent vs Collected")
		loan = make_loan(principal=1000)
		loan.submit()
		make_repayment(loan.name, 100)
		after = dashboard.get_chart("Lent vs Collected")
		self.assertEqual(len(after["labels"]), 12)
		lent, collected = (after["datasets"][i]["values"][-1] - before["datasets"][i]["values"][-1] for i in (0, 1))
		self.assertEqual((lent, collected), (1000, 100))

	def test_net_profit_by_month_ends_with_this_month(self):
		before = dashboard.get_chart("Net Profit by Month")["datasets"][0]["values"]
		make_expense(80)
		after = dashboard.get_chart("Net Profit by Month")["datasets"][0]["values"]
		self.assertEqual((len(after), after[-1] - before[-1]), (6, -80))

	def test_outstanding_by_status_and_loans_by_plan(self):
		before = dashboard.get_chart("Outstanding by Status")["datasets"][0]["values"]
		plans = dashboard.get_chart("Loans by Plan")
		plan_count = dict(zip(plans["labels"], plans["datasets"][0]["values"])).get("1 Month", 0)
		make_loan("1 Month", disbursement_date=add_days(today(), -40)).submit()
		after = dashboard.get_chart("Outstanding by Status")["datasets"][0]["values"]
		self.assertEqual(after[1] - before[1], 1400)
		plans = dashboard.get_chart("Loans by Plan")
		self.assertEqual(dict(zip(plans["labels"], plans["datasets"][0]["values"]))["1 Month"], plan_count + 1)

	def test_unknown_chart_is_rejected(self):
		self.assertRaises(frappe.ValidationError, dashboard.get_chart, "Nope")


class TestTodaySummary(IntegrationTestCase):
	def test_lists_todays_activity(self):
		loan = make_loan(principal=1000)
		loan.submit()
		make_repayment(loan.name, 200)
		expense = make_expense(25)
		summary = dashboard.get_today_summary()
		sections = {section["label"]: section for section in summary["sections"]}
		self.assertIn(loan.name, [row["document"] for row in sections["Disbursement"]["rows"]])
		self.assertIn(expense.name, [row["document"] for row in sections["Expense"]["rows"]])
		self.assertEqual(set(summary["month"]), {"lent", "collected", "net_profit"})
