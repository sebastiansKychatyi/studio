# Duo Studio — сайт-портфолио (Nuxt 4 + Vue 3)

Сайт на трёх языках: **словацкий** (`/sk`), **чешский** (`/cs`), **украинский** (`/uk`).

| Страница | Адрес | Дизайн |
|---|---|---|
| Общая страница студии (услуги, AI-автоматизация, портфолио, FAQ) | `/sk` | светлый, градиенты |
| Личная страница Себастьяна | `/sk/sebastian` | «разработчик»: терминал, моноширинный шрифт, сетка активности |
| Личная страница друга | `/sk/daniel` | «креатив»: антиква, стикеры, фигуры, курсор-капля |

## Язык по стране посетителя

- **Корень `/`** открывает язык в таком порядке: язык, выбранный вручную (cookie `lang`) → страна по IP (SK → `sk`, CZ → `cs`, UA → `uk`) → язык браузера → словацкий.
- **На языковых страницах** автоматического редиректа нет (иначе Google, который заходит из США, не проиндексирует версии). Вместо этого показывается подсказка на языке страны: «Схоже, ви з України — перейти на українську?».
- Страна определяется через бесплатный сервис `api.country.is` (без ключа). Соответствие стран и языков — `geoLanguages` в `data/site.ts`.

## Запуск

```bash
npm install
npm run dev        # http://localhost:3000
npm run generate   # статическая сборка в .output/public — её и загружать на хостинг
```

> Nuxt 4.6 просит Node.js ≥ 22.21 (или 24.11+). На 22.16 работает, но выводит предупреждение.

## Где менять информацию

| Что | Файл |
|---|---|
| Домен, e-mail, телефон, город, люди (имя, slug, дизайн, навыки, соцсети), проекты | `data/site.ts` |
| Все тексты: общая страница, личные страницы (`personal`), описания проектов, FAQ | `data/locales/sk.ts`, `cs.ts`, `uk.ts` |
| Скриншоты проектов | `public/img/projects/*.jpg` (1200×750) |
| Цвета и анимации общей страницы | `app/assets/css/main.css` |
| Дизайн личных страниц | `app/components/ProfileDev.vue`, `ProfileCreative.vue` |

**Перед публикацией:** замените `domain` в `data/site.ts` и `https://duostudio.sk` в `public/index.html`, впишите данные друга (имя, `slug`, тексты в `personal.people.p2`) и замените его проекты-заглушки (`placeholder: true`).

### Новый проект в портфолио
1. Добавьте объект в `projects` в `data/site.ts` (`author: 'p1'` или `'p2'`, ссылки `url` / `repo`).
2. Добавьте описание `work.projects['id'].desc` во все три файла `data/locales/*`.
3. Скриншот: `public/img/projects/<id>.jpg`, путь в поле `image`. Без скриншота рисуется CSS-макет (`layout: 4` — макет «код/API»).

## SEO и GEO

- Отдельная серверно-отрендеренная страница для каждого языка и человека: title, description, canonical, `hreflang` + x-default, Open Graph
- Geo-теги (Nitra) и schema.org (JSON-LD): ProfessionalService, Person, ProfilePage, услуги + AI-услуги, FAQPage, портфолио со ссылками на сайты и GitHub
- `/sitemap.xml` (все языки и личные страницы с hreflang), `/robots.txt` с доступом для AI-ботов, `/llms.txt` для AI-ассистентов

## Структура

```
app/
  pages/index.vue            общая страница
  pages/[slug].vue           личные страницы
  components/                секции, ProfileDev, ProfileCreative, GeoLangHint, ProjectCard…
  composables/useSite.ts     тексты текущего языка
  composables/useSiteSeo.ts  meta-теги и JSON-LD
  composables/useGeoLang.ts  определение страны и выбор языка
  plugins/motion.ts          анимации: v-reveal, v-tilt, v-magnetic, v-spot
data/                        контент и настройки
server/routes/               sitemap.xml, robots.txt, llms.txt, site.webmanifest
public/                      картинки, корневой index.html (выбор языка по стране)
```
