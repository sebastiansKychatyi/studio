// Перенаправляет на нужную языковую версию страницы.
// Использование: <script src="/go.js" data-path="/roman"></script>  ->  /sk/roman, /cs/roman или /uk/roman
// Порядок: язык, выбранный вручную (cookie "lang") -> страна по IP (SK/CZ/UA) -> язык браузера -> словацкий.
(function () {
  var path = (document.currentScript && document.currentScript.getAttribute('data-path')) || '';
  var langs = ['sk', 'cs', 'uk'];
  var byCountry = { SK: 'sk', CZ: 'cs', UA: 'uk' };
  var done = false;

  function go(lang) {
    if (done) return;
    done = true;
    location.replace('/' + (langs.indexOf(lang) > -1 ? lang : 'sk') + path + location.hash);
  }
  function byBrowser() {
    var nav = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < nav.length; i++) {
      var c = String(nav[i]).slice(0, 2).toLowerCase();
      if (c === 'cs') return 'cs';
      if (c === 'uk' || c === 'ru') return 'uk';
      if (c === 'sk') return 'sk';
    }
    return 'sk';
  }

  var m = document.cookie.match(/(?:^|; )lang=([a-z]+)/);
  if (m && langs.indexOf(m[1]) > -1) return go(m[1]);

  setTimeout(function () { go(byBrowser()); }, 2000); // если геосервис не ответил
  fetch('https://api.country.is/')
    .then(function (r) { return r.json(); })
    .then(function (d) {
      try { sessionStorage.setItem('geo_country', d.country || ''); } catch (e) {}
      go(byCountry[d.country] || byBrowser());
    })
    .catch(function () { go(byBrowser()); });
})();
