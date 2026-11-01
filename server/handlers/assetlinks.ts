// /.well-known/assetlinks.json: proves the Android app (android/) belongs to this site, so it opens
// the panel full screen without the address bar. Fingerprint(s) of the signing key in NUXT_TWA_SHA256.
export default defineEventHandler((event) => {
  const { twaPackage, twaSha256 } = useRuntimeConfig(event)
  const prints = String(twaSha256).split(',').map((s) => s.trim()).filter(Boolean)
  setHeader(event, 'Content-Type', 'application/json')
  return prints.length
    ? [{ relation: ['delegate_permission/common.handle_all_urls'], target: { namespace: 'android_app', package_name: twaPackage, sha256_cert_fingerprints: prints } }]
    : []
})
