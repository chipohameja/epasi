import frappe
from frappe.tests import IntegrationTestCase

from epasi.tests.utils import make_borrower, make_loan, make_repayment


class TestLoanRepayment(IntegrationTestCase):
	def setUp(self):
		self.loan = make_loan("2 Weeks", 1000)
		self.loan.submit()

	def test_partial_payments_cover_interest_first(self):
		first = make_repayment(self.loan.name, 200)
		second = make_repayment(self.loan.name, 300)
		self.assertEqual((first.interest_portion, first.principal_portion), (200, 0))
		self.assertEqual((second.interest_portion, second.principal_portion), (70, 230))
		self.loan.reload()
		self.assertEqual((self.loan.interest_paid, self.loan.principal_paid), (270, 230))
		self.assertEqual((self.loan.outstanding, self.loan.status), (770, "Active"))

	def test_overpayment_is_rejected(self):
		self.assertRaises(frappe.ValidationError, make_repayment, self.loan.name, 1271)

	def test_cancel_reverses_payment(self):
		make_repayment(self.loan.name, 500).cancel()
		self.loan.reload()
		self.assertEqual((self.loan.interest_paid, self.loan.principal_paid, self.loan.outstanding), (0, 0, 1270))

	def test_full_payment_closes_loan(self):
		make_repayment(self.loan.name, 1270)
		self.loan.reload()
		self.assertEqual((self.loan.outstanding, self.loan.status), (0, "Closed"))
		self.assertRaises(frappe.ValidationError, make_repayment, self.loan.name, 1)

	def test_cancel_reopens_closed_loan(self):
		make_repayment(self.loan.name, 1270).cancel()
		self.assertEqual(frappe.db.get_value("Loan", self.loan.name, "status"), "Active")

	def test_draft_loan_cannot_be_repaid(self):
		draft = make_loan()
		self.assertRaises(frappe.ValidationError, make_repayment, draft.name, 100)

	def test_borrower_totals_follow_loans_and_payments(self):
		loan = make_loan(principal=500, borrower=make_borrower("0972000200"))
		loan.submit()
		make_repayment(loan.name, 135)
		borrower = frappe.get_doc("Borrower", loan.borrower)
		self.assertEqual((borrower.total_borrowed, borrower.total_outstanding), (500, 500))
