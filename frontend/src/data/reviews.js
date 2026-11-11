import { useCall } from 'frappe-ui'

export const REVIEW_SLOTS = 3

const placeholders = [
  {
    display_name: 'Natasha M.',
    rating: 5,
    comment: 'I applied in the morning and had my money the same day. Very professional.',
  },
  {
    display_name: 'Joseph B.',
    rating: 5,
    comment: 'Clear rates and no surprises. They kept my TV safe and returned it when I paid.',
  },
  {
    display_name: 'Chilufya K.',
    rating: 4,
    comment: 'Quick help for my business stock. The WhatsApp updates made it easy.',
  },
]

export function useReviews() {
  return useCall({ url: '/api/v2/method/epasi.api.public.get_reviews', cacheKey: 'reviews' })
}

export function fillReviewSlots(reviews) {
  return [...(reviews || []), ...placeholders].slice(0, REVIEW_SLOTS)
}
