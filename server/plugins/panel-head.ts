import site from '../../data/site'

// Panel and login pages: the panel's own manifest (installable app) and iOS home-screen tags.
// Public pages keep /site.webmanifest and are not touched.
const PAGE = new RegExp(`^/(${site.languages.join('|')})/(panel|login)(/|\\?|$)`)

// iOS splash screens: CSS size × pixel ratio (same list in scripts/pwa-assets.mjs)
const SPLASH = [
  [375, 667, 2], [414, 896, 2], [375, 812, 3], [414, 896, 3], [390, 844, 3], [428, 926, 3], [393, 852, 3], [430, 932, 3], [402, 874, 3], [440, 956, 3],
]
const IOS = [
  '<meta name="apple-mobile-web-app-capable" content="yes">',
  '<meta name="mobile-web-app-capable" content="yes">',
  '<meta name="apple-mobile-web-app-status-bar-style" content="default">',
  `<meta name="apple-mobile-web-app-title" content="${site.brand}">`,
  ...SPLASH.map(([w, h, r]) =>
    `<link rel="apple-touch-startup-image" media="(device-width: ${w}px) and (device-height: ${h}px) and (-webkit-device-pixel-ratio: ${r}) and (orientation: portrait)" href="/pwa/splash-${w! * r!}x${h! * r!}.png">`),
].join('')

export default defineNitroPlugin((nitro) => {
  nitro.hooks.hook('render:html', (html, { event }) => {
    const lang = event.path.match(PAGE)?.[1]
    if (!lang) return
    html.head = html.head.map((part) => part.replace('href="/site.webmanifest"', `href="/panel.webmanifest?lang=${lang}"`))
    html.head.push(IOS)
  })
})
