const STORAGE_KEY = 'epasi-referral'
const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000

export function saveReferral(code) {
  if (!code) return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ code, expires: Date.now() + THIRTY_DAYS }))
  } catch {
    // Storage can be blocked. The referral is optional.
  }
}

export function getReferral() {
  try {
    const referral = JSON.parse(localStorage.getItem(STORAGE_KEY))
    return referral?.expires > Date.now() ? referral.code : null
  } catch {
    return null
  }
}
