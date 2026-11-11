export default {
  slug: 'referrer',
  title: 'Referrer',
  who: 'You send people to Epasi and earn commission.',
  summary: 'Share your link, follow your referrals and see what you earned.',
  sections: [
    {
      title: 'Sign in',
      text: 'The loan manager gives you an account. Open the website and tap "Partner login" at the bottom of the page. Sign in with your email and password.',
      image: { file: 'referrer-login.png', alt: 'Sign in page' },
    },
    {
      title: 'Share your link',
      text: 'Your partner page shows your own referral link. Tap "Copy link" and send it on WhatsApp, Facebook or SMS.',
      image: {
        file: 'referrer-partner.png',
        alt: 'Partner page with link and referrals',
        phone: true,
      },
      example: [
        'Your link looks like this: https://epasi.site/epasi/apply?ref=BUPE',
        'A friend opens it and applies. The application is linked to you.',
      ],
      tip: 'The link stays in the phone of the person for 30 days. They can apply later and it still counts.',
    },
    {
      title: 'How you earn',
      steps: [
        'A person applies with your link.',
        'Epasi gives them a loan.',
        'They repay the full loan.',
        'You earn your commission rate on the interest they paid.',
      ],
      example: [
        'Your rate is 15%. Your friend borrows K 12,000 on the 1 Month plan.',
        'Interest is K 12,000 × 40% = K 4,800.',
        'When the loan is fully repaid, you earn K 4,800 × 15% = K 720.',
      ],
      tip: 'Some agents earn only on loans above a minimum amount. A loan that is not repaid earns nothing. Ask the loan manager about your rate and minimum.',
    },
    {
      title: 'Follow your referrals',
      text: 'The boxes at the top show what you earned, what Epasi paid you and what is still unpaid. The list shows each person you referred.',
      steps: [
        'Name: first name and the first letter of the last name.',
        'Status: Pending, Approved, Active, Closed and so on.',
        'Commission: the amount and if it is Paid or Unpaid.',
      ],
      tip: 'A person stays linked to the first agent who brought them. If they apply again later, it counts for you again.',
    },
  ],
}
