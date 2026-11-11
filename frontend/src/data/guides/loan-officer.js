export default {
  slug: 'loan-officer',
  title: 'Loan Officer',
  who: 'You work for Epasi and bring in borrowers.',
  summary: 'Enter walk-in applications in the back office and share your referral link.',
  sections: [
    {
      title: 'Sign in',
      text: 'Tap "Loan manager login" at the bottom of the website and sign in with your email and password. Use the menu on the left to open Borrower, Loan Application, Loan, Sales Agent and Commission.',
      image: { file: 'officer-applications.png', alt: 'Loan application list' },
      tip: 'You see only your own borrowers, applications, loans and commissions.',
    },
    {
      title: 'Add a new borrower',
      text: 'Do this when a person comes to you and is not yet in the system.',
      steps: [
        'Open Borrower and click "Add Borrower".',
        'Type the full name and WhatsApp number. Add the NRC number and address if you have them.',
        'Click "Save".',
      ],
      image: { file: 'officer-new-borrower.png', alt: 'New borrower form' },
      example: [
        'Full name: Mutinta Mweemba',
        'WhatsApp number: 0975 456 789',
        'NRC number: 234567/10/1',
      ],
      tip: 'Type the number as the person gives it. The system adds the country code 260.',
    },
    {
      title: 'Enter a walk-in application',
      steps: [
        'Open Loan Application and click "Add Loan Application".',
        'Choose the borrower. Start typing the name and pick it from the list.',
        'Choose the loan plan, type the amount and the purpose.',
        'Describe the collateral and type its estimated value.',
        'Click "Save".',
        'Add photos of the collateral with the "+" next to "Attachments" on the right.',
      ],
      image: { file: 'officer-new-application.png', alt: 'New loan application form' },
      example: [
        'Plan: 2 Weeks. Amount: K 3,000. Purpose: Business.',
        'Collateral: "Sewing machine, Singer, working well", value K 4,500.',
      ],
      tip: 'The application is linked to you. The loan manager changes the status and gives the loan.',
    },
    {
      title: 'Share your referral link',
      text: 'Open Sales Agent and click your name. Click "Copy Referral Link" at the top and send it to people. When they apply online with it, the application is yours.',
      image: { file: 'officer-referral-link.png', alt: 'Sales agent record with referral link' },
      example: ['Your link looks like this: https://epasi.site/epasi/apply?ref=NATASHA'],
    },
    {
      title: 'See your commission',
      text: 'Your Sales Agent record shows what you earned, what is paid and what is unpaid. Open Commission to see each one.',
      example: [
        'Your rate is 10% and your minimum is K 5,000.',
        'A K 6,000 loan on the 1 Month plan pays K 2,400 interest.',
        'When it is fully repaid you earn K 240.',
        'A K 4,000 loan earns nothing, because it is not above K 5,000.',
      ],
    },
  ],
}
