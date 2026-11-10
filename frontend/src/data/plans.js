import { useCall } from 'frappe-ui'

const kwacha = new Intl.NumberFormat('en-ZM', { style: 'currency', currency: 'ZMW', trailingZeroDisplay: 'stripIfInteger' })
const longDate = new Intl.DateTimeFormat('en-GB', {
  weekday: 'short',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

export function useLoanPlans() {
  return useCall({ url: '/api/v2/method/epasi.api.public.get_loan_plans', cacheKey: 'loan-plans' })
}

export function formatMoney(amount) {
  return kwacha.format(amount || 0)
}

export function getRepayment(plan, amount) {
  const dueDate = new Date()
  dueDate.setDate(dueDate.getDate() + plan.term_days)
  const interest = (amount * plan.interest_rate) / 100
  return { interest, total: amount + interest, dueDate: longDate.format(dueDate) }
}
