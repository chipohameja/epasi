import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

from epasi.epasi.doctype.collateral.collateral import get_recovery_income
from epasi.epasi.doctype.loan.loan import mark_overdue_loans
from epasi.tests.utils import make_loan, make_loan_with_collateral, make_repayment


class TestOverdueLoans(IntegrationTestCase):
	def test_job_marks_active_loans_past_due_date(self):
		late, current = make_loan(), make_loan()
		late.submit()
		current.submit()
		frappe.db.set_value("Loan", late.name, "due_date", add_days(today(), -1))
		mark_overdue_loans()
		self.assertEqual(frappe.db.get_value("Loan", late.name, "status"), "Overdue")
		self.assertEqual(frappe.db.get_value("Loan", current.name, "status"), "Active")

	def test_backdated_loan_is_overdue_on_submit(self):
		loan = make_loan(disbursement_date=add_days(today(), -20))
		loan.submit()
		self.assertEqual(loan.status, "Overdue")


class TestCollateralRecovery(IntegrationTestCase):
	def setUp(self):
		self.loan, self.collateral = make_loan_with_collateral()

	def test_mark_defaulted_forfeits_collateral(self):
		self.loan.mark_defaulted()
		self.collateral.reload()
		self.assertEqual((self.loan.status, self.collateral.status), ("Defaulted", "Forfeited"))

	def test_collateral_cannot_be_forfeited_while_loan_is_active(self):
		self.collateral.status = "Forfeited"
		self.assertRaises(frappe.ValidationError, self.collateral.save)

	def test_held_collateral_cannot_be_sold(self):
		self.collateral.update({"status": "Sold", "sale_date": today(), "sale_amount": 900})
		self.assertRaises(frappe.ValidationError, self.collateral.save)

	def test_sale_needs_amount(self):
		self.loan.mark_defaulted()
		self.collateral.reload()
		self.collateral.status = "Sold"
		self.assertRaises(frappe.ValidationError, self.collateral.save)

	def test_sale_amount_counts_as_recovery(self):
		self.loan.mark_defaulted()
		before = get_recovery_income(today(), today())
		self.collateral.reload()
		self.collateral.update({"status": "Sold", "sale_date": today(), "sale_amount": 900})
		self.collateral.save()
		self.assertEqual(get_recovery_income(today(), today()), before + 900)

	def test_collateral_returned_after_loan_closes(self):
		self.collateral.status = "Returned"
		self.assertRaises(frappe.ValidationError, self.collateral.save)
		make_repayment(self.loan.name, self.loan.outstanding)
		self.collateral.reload()
		self.collateral.status = "Returned"
		self.collateral.save()

	def test_closed_loan_cannot_be_defaulted(self):
		make_repayment(self.loan.name, self.loan.outstanding)
		self.loan.reload()
		self.assertRaises(frappe.ValidationError, self.loan.mark_defaulted)
