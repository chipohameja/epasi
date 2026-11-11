export default {
  slug: 'applicant',
  title: 'Applicant',
  who: 'You want to borrow money from Epasi.',
  summary: 'Apply online, get a call on WhatsApp, bring your collateral and get your cash.',
  sections: [
    {
      title: 'Choose a plan',
      text: 'Open the home page. It shows our two plans. Tap a plan to start your application with that plan.',
      image: { file: 'applicant-home.png', alt: 'Home page with the plans', phone: true },
      example: [
        '2 Weeks plan: you pay 27% interest, once.',
        '1 Month plan: you pay 40% interest, once.',
        'You can borrow from K 100 to K 50,000.',
      ],
    },
    {
      title: 'Fill in the form',
      steps: [
        'Type your full name and your WhatsApp number.',
        'Your NRC number and address help us, but you can leave them empty.',
        'Choose a plan and type the amount you need.',
        'Check the box "You will repay". It shows the total and the last day to pay.',
      ],
      image: { file: 'applicant-apply-loan.png', alt: 'Loan section of the form', phone: true },
      example: [
        'You borrow K 2,000 on the 2 Weeks plan.',
        'Interest is K 2,000 × 27% = K 540.',
        'You repay K 2,540 within 14 days.',
      ],
    },
    {
      title: 'Describe your collateral',
      text: 'Collateral is an item you leave with us until you repay. We only lend against collateral.',
      steps: [
        'Write what the item is, its brand, size and age.',
        'Type how much you think it is worth.',
        'Add 1 to 5 clear photos. Each photo must be smaller than 5 MB.',
        'Tap "Submit application".',
      ],
      image: {
        file: 'applicant-apply-collateral.png',
        alt: 'Collateral section with a photo',
        phone: true,
      },
      example: ['Good: "Samsung 55 inch TV, 2 years old, with remote".', 'Not good: "TV".'],
    },
    {
      title: 'After you apply',
      text: 'You get a reference number, for example APP-00016. Keep it. A loan manager will message you on WhatsApp to check your details.',
      steps: [
        'Wait for our message, or tap "Message us on WhatsApp".',
        'Bring your collateral to our office.',
        'Get your money the same day.',
        'Repay by the due date in cash, mobile money or bank.',
      ],
      image: { file: 'applicant-thank-you.png', alt: 'Application received page', phone: true },
      tip: 'When you repay everything, you get your collateral back.',
    },
    {
      title: 'Leave a review',
      text: 'Tell other people about your experience. Tap "Leave a review" on the thank-you page or at the bottom of the home page.',
      steps: [
        'Type your reference number and the WhatsApp number you used to apply.',
        'Choose 1 to 5 stars.',
        'Write a short comment, at most 300 characters.',
        'Tap "Send review".',
      ],
      image: { file: 'applicant-review.png', alt: 'Leave a review form', phone: true },
      tip: 'We check each review before it shows. We show only your first name and the first letter of your last name, for example "Lushomo H.".',
    },
  ],
}
