import preset, { content } from 'frappe-ui/tailwind'

export default {
  presets: [preset],
  content: [...content, './index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        gold: { light: '#ecd08a', DEFAULT: '#c9a24d', dark: '#9a7a2e' },
        night: { DEFAULT: '#0f0d0a', raised: '#1a1611', line: '#3a3022' },
      },
      fontFamily: { serif: ['"Playfair Display"', 'Georgia', 'serif'] },
    },
  },
}
