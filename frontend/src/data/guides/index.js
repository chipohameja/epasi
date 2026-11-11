import administrator from './administrator'
import applicant from './applicant'
import loanManager from './loan-manager'
import loanOfficer from './loan-officer'
import referrer from './referrer'

export const guides = [applicant, referrer, loanOfficer, loanManager, administrator]

export function findGuide(slug) {
  return guides.find((guide) => guide.slug === slug)
}

export function screenshotUrl(file) {
  return `/assets/epasi/images/guide/${file}`
}
