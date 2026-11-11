export default {
  slug: 'loan-manager',
  title: 'Loan Manager',
  who: 'You run the daily lending work in the back office.',
  summary:
    'Follow up applications, give loans, record repayments, pay commission and watch profit.',
  sections: [
    {
      title: 'Start with the Epasi home page',
      text: 'Tap "Loan manager login" at the bottom of the website and sign in. The Epasi page shows what needs work today. Click a card to open the list behind it.',
      image: { file: 'manager-workspace.png', alt: 'Epasi workspace with number cards' },
      steps: [
        'Needs action today: pending applications, loans due today, overdue loans and reviews to check.',
        'Money at a glance: money lent, money collected, profit and commission this month.',
        'Trends: charts for the last weeks and months.',
      ],
    },
    {
      title: 'Follow up an application',
      steps: [
        'Open a Pending application.',
        'Look at the collateral photos and the amount.',
        'Click "Chat on WhatsApp" to talk to the applicant.',
        'Change Status to Contacted, then to Approved or Rejected. Write notes if needed.',
        'Click "Save".',
      ],
      image: { file: 'manager-application.png', alt: 'Pending loan application' },
    },
    {
      title: 'Give a loan',
      text: 'Do this when the borrower brings the collateral and you give the cash.',
      steps: [
        'Open the Approved application and click "Create Loan".',
        'Check the plan, the principal and the disbursement date (the day you give the money).',
        'Click "Save", then "Submit".',
      ],
      image: {
        file: 'manager-approved-application.png',
        alt: 'Approved application with Create Loan button',
      },
      example: [
        'Principal K 12,000 on the 1 Month plan (40%).',
        'Interest K 4,800. Total due K 16,800, 30 days after the disbursement date.',
      ],
      tip: 'When you submit the loan, the system adds a Collateral record with status Held. The loan keeps its rate even if you change the plan later.',
    },
    {
      title: 'Record a repayment',
      steps: [
        'Open the loan and click "Record Repayment".',
        'Type the amount the borrower paid, the date and the mode: Cash, Mobile Money or Bank.',
        'For mobile money or bank, type the transaction reference.',
        'Click "Save", then "Submit".',
      ],
      image: { file: 'manager-repayment.png', alt: 'New loan repayment form' },
      example: [
        'Total due is K 2,540 (K 2,000 + K 540 interest).',
        'The borrower pays K 1,000. The first K 540 pays the interest, K 460 pays the principal.',
        'K 1,540 is still outstanding.',
      ],
      tip: 'The loan closes by itself when the outstanding amount is zero. Each night the system marks unpaid loans past the due date as Overdue.',
    },
    {
      title: 'Return or sell collateral',
      steps: [
        'Loan Closed: open its Collateral, set Status to Returned and give the item back.',
        'Borrower cannot pay: open the loan and click "Mark Defaulted". The collateral becomes Forfeited.',
        'When you sell forfeited collateral, set Status to Sold and type the sale date and amount.',
      ],
      image: { file: 'manager-collateral.png', alt: 'Collateral record' },
      tip: 'The sale amount counts as recovery income in the profit.',
    },
    {
      title: 'Add a referrer or loan officer',
      steps: [
        'Open Sales Agent and click "Add Sales Agent".',
        'Type the name and WhatsApp number. Choose Referrer or Loan Officer.',
        'Type the commission rate and the minimum loan amount.',
        'If they must sign in, choose their user account in "User". Ask the administrator to make the account first.',
        'Click "Save". The referral code and link are made for you.',
      ],
      image: { file: 'manager-sales-agent.png', alt: 'New sales agent form' },
      example: ['Rate 10%, minimum K 5,000: a loan must be more than K 5,000 to earn commission.'],
    },
    {
      title: 'Pay commission',
      text: 'The system adds an Unpaid commission when a referred loan is fully repaid.',
      steps: [
        'Open Commission and choose an Unpaid one.',
        'Pay the agent.',
        'Click "Mark Paid" and confirm.',
      ],
      image: { file: 'manager-commission.png', alt: 'Unpaid commission with Mark Paid button' },
      tip: 'Mark Paid also records the amount as an expense, so the profit goes down by that amount.',
    },
    {
      title: 'Record expenses',
      steps: [
        'Open Expense and click "Add Expense".',
        'Choose the date and category: Transport, Airtime, Rent, Salaries or Other.',
        'Type the amount and a short description. Click "Save".',
      ],
      image: { file: 'manager-expense.png', alt: 'New expense form' },
      example: ['Transport, K 150: "Bus fare to collect collateral in Monze".'],
    },
    {
      title: 'Publish reviews',
      text: 'Reviews from applicants wait for you. The card "Reviews Awaiting Approval" shows how many.',
      steps: [
        'Open Review and click a review.',
        'Read the comment. If it is good and polite, tick "Published" and click "Save".',
        'The home page shows the 3 newest published reviews.',
      ],
      image: { file: 'manager-review.png', alt: 'Review record with Published ticked' },
      tip: 'Until there are 3 published reviews, the home page fills the empty places with sample reviews.',
    },
    {
      title: 'Plans and reports',
      text: 'Open Loan Plan to change a rate, term or amount limits. Untick "Active" to hide a plan from the website.',
      image: { file: 'manager-report.png', alt: 'Profit Summary report' },
      steps: [
        'Profit Summary: interest collected + recovery income − expenses, by day.',
        'Daily Operations: what happened on each day.',
        'Outstanding Loans: who owes money and how much.',
        'Commission Summary: earned, paid and unpaid commission per agent.',
      ],
    },
  ],
}
