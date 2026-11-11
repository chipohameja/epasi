export function isLoggedIn() {
  return /(?:^|;\s*)user_id=(?!Guest(?:;|$))[^;]+/.test(document.cookie)
}

export function loginUrl(path) {
  return `/login?redirect-to=${encodeURIComponent(path)}`
}
