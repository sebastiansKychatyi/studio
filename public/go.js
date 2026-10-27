// Redirects to the right language version.
// Usage: <script src="/go.js" data-path="/roman"></script> → /<lang>/roman
// Order: manual choice (cookie) → country (SK/CZ/UA, others → en) → browser language → en
(function () {
  var path = (document.currentScript && document.currentScript.getAttribute('data-path')) || '';
  var langs = ['sk', 'cs', 'uk', 'en'];
  var byCountry = { SK: 'sk', CZ: 'cs', UA: 'uk' };
  var fallback = 'en';
  var done = false;

  function go(lang) {
    if (done) return;
    done = true;
    location.replace('/' + (langs.indexOf(lang) > -1 ? lang : fallback) + path + location.hash);
  }
  function byBrowser() {
    var nav = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < nav.length; i++) {
      var c = String(nav[i]).slice(0, 2).toLowerCase();
      if (c === 'cs') return 'cs';
      if (c === 'uk' || c === 'ru') return 'uk';
      if (c === 'sk') return 'sk';
      if (c === 'en') return 'en';
    }
    return fallback;
  }

  var m = document.cookie.match(/(?:^|; )lang=([a-z]+)/);
  if (m && langs.indexOf(m[1]) > -1) return go(m[1]);

  setTimeout(function () { go(byBrowser()); }, 2000); // geo service timeout
  fetch('https://api.country.is/')
    .then(function (r) { return r.json(); })
    .then(function (d) {
      try { sessionStorage.setItem('geo_country', d.country || ''); } catch (e) {}
      go(d.country ? byCountry[d.country] || fallback : byBrowser());
    })
    .catch(function () { go(byBrowser()); });
})();
