export default {
  slug: 'administrator',
  title: 'Administrator',
  who: 'You set up the system and the user accounts.',
  summary: 'Make accounts for staff and partners, give roles, and load sample data for training.',
  sections: [
    {
      title: 'Make a user account',
      text: 'Each loan manager, loan officer and referrer who signs in needs an account.',
      steps: [
        'Search for "User" and click "Add User".',
        'Type the email and first name. Keep "Send Welcome Email" ticked so the person can set a password.',
        'Click "Save".',
      ],
      image: { file: 'admin-new-user.png', alt: 'New user form' },
      example: ['Email: chanda@example.com', 'First name: Chanda'],
    },
    {
      title: 'Give the right role',
      steps: [
        'Loan manager: open the user, go to "Roles & Permissions", tick "Loan Manager" and save.',
        'Loan officer or referrer: do not tick a role. Open their Sales Agent record and choose the user in "User". The system gives the "Loan Officer" or "Referrer" role when you save.',
      ],
      image: { file: 'manager-sales-agent.png', alt: 'Sales agent form with User field' },
      tip: 'Loan officers and referrers see only their own records. Referrers cannot open the back office; they see only their partner page.',
    },
    {
      title: 'Sample data for training',
      text: 'Open "Epasi Settings". Use these buttons to practise without real customers.',
      steps: [
        '"Generate Test Data" adds sample borrowers, applications, loans, repayments, collateral, agents and photos.',
        '"Clear Test Data" deletes only those sample records. Real records stay.',
      ],
      image: { file: 'admin-settings.png', alt: 'Epasi Settings with test data buttons' },
      example: [
        'Sample loan officer: Natasha Mulenga, with walk-in applications.',
        'Sample referrer: Bupe Zulu, with one referral and an unpaid commission.',
        'Ask your developer for the sample passwords.',
      ],
      tip: 'Do not load the sample data on the live site with real customers. Anyone who knows the sample passwords could sign in.',
    },
  ],
}
