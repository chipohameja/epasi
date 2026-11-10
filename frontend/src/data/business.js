export const tagline = 'Umo nchito ufukuma ku chunga.'
export const taglineMeaning = 'Hard work brings success.'

export const services = [
  'Personal loans',
  'Business loans',
  'Asset financing',
  'Education loans',
  'Flexible repayment plans',
]

export const contacts = [
  { name: 'Pasi', role: 'Founder & CEO', whatsapp: '260972616440', phone: '+260 972 616 440' },
  { name: 'Muluti', whatsapp: '260717374941', phone: '+260 717 374 941' },
]

export const email = 'Epasi002@gmail.com'
export const town = 'Mazabuka, Zambia'
export const managerLoginUrl = '/login?redirect-to=/desk/epasi'

export function whatsappLink(number, message = '') {
  return `https://wa.me/${number}${message ? `?text=${encodeURIComponent(message)}` : ''}`
}
