// GDPR privacy policy texts. Placeholders: {name}, {email}, {phone}, {city}.
// Template, not legal advice — have it reviewed before launch.

type Privacy = { title: string; updated: string; intro: string; sections: [string, string[]][] }

export const privacy: { sk: Privacy; cs: Privacy; uk: Privacy; en: Privacy } = {
  sk: {
    title: 'Ochrana osobných údajov',
    updated: 'Platné od 27. 10. 2026',
    intro: 'Na tejto stránke vysvetľujeme, aké osobné údaje spracúvame, keď používate náš web alebo nás kontaktujete, prečo to robíme a aké máte práva podľa nariadenia GDPR.',
    sections: [
      ['Prevádzkovateľ', ['Prevádzkovateľom osobných údajov je {name}, {city}, Slovensko. Kontakt: {email}, {phone}.']],
      ['Aké údaje spracúvame', [
        'Kontaktný formulár: meno, e-mail, typ dopytu a text správy, ktorý nám pošlete.',
        'Komunikácia e-mailom alebo telefonicky: údaje, ktoré nám v nej sami poskytnete.',
        'Technické údaje: IP adresa a údaje o prehliadači, ktoré automaticky zaznamenáva server hostingu pri návšteve webu.',
      ]],
      ['Účel a právny základ', [
        'Odpoveď na váš dopyt a príprava cenovej ponuky — opatrenia pred uzavretím zmluvy (čl. 6 ods. 1 písm. b) GDPR).',
        'Ochrana webu a formulára pred zneužitím a spamom — oprávnený záujem (čl. 6 ods. 1 písm. f) GDPR).',
        'Anonymná štatistika návštevnosti bez cookies — oprávnený záujem na zlepšovaní webu (čl. 6 ods. 1 písm. f) GDPR).',
      ]],
      ['Príjemcovia a služby tretích strán', [
        'Poskytovateľ hostingu, na ktorom web beží.',
        'Telegram — doručenie upozornenia o novom dopyte z formulára.',
        'Web3Forms — doručenie správy z formulára na náš e-mail.',
        'api.country.is — určenie krajiny podľa IP adresy, aby sme vám ponúkli správny jazyk webu. Krajinu neukladáme na serveri.',
        'Google Fonts — načítanie písma; Google pri tom môže spracovať vašu IP adresu.',
        'Ak je zapnutá analytika (Umami alebo Plausible), funguje bez cookies a bez ukladania osobných údajov.',
        'Pri službách mimo EÚ prebieha prenos na základe štandardných zmluvných doložiek alebo rámca EU–US Data Privacy Framework.',
      ]],
      ['Doba uchovávania', [
        'Dopyty uchovávame najviac 2 roky od poslednej komunikácie, ak nevznikne zmluva.',
        'Ak uzavrieme zmluvu, údaje uchovávame počas jej trvania a podľa zákonných lehôt (napr. účtovné doklady 10 rokov).',
      ]],
      ['Cookies a lokálne úložisko', [
        'Nepoužívame reklamné ani sledovacie cookies.',
        'Ukladáme iba cookie „lang" so zvoleným jazykom (1 rok) a v úložisku prehliadača informáciu o krajine a o skrytí jazykovej nápovedy počas relácie. Ide o technicky nevyhnutné údaje, ktoré nevyžadujú súhlas.',
      ]],
      ['Vaše práva', [
        'Máte právo na prístup k údajom, ich opravu, vymazanie, obmedzenie spracúvania, prenosnosť a právo namietať proti spracúvaniu.',
        'Ak spracúvame údaje na základe súhlasu, môžete ho kedykoľvek odvolať.',
        'Sťažnosť môžete podať na Úrad na ochranu osobných údajov SR, Hraničná 12, 820 07 Bratislava (dataprotection.gov.sk), alebo na dozorný orgán v štáte EÚ, v ktorom žijete.',
      ]],
      ['Kontakt', ['S otázkami o ochrane osobných údajov nám napíšte na {email}.']],
    ],
  },
  cs: {
    title: 'Ochrana osobních údajů',
    updated: 'Platné od 27. 10. 2026',
    intro: 'Na této stránce vysvětlujeme, jaké osobní údaje zpracováváme, když používáte náš web nebo nás kontaktujete, proč to děláme a jaká máte práva podle nařízení GDPR.',
    sections: [
      ['Správce', ['Správcem osobních údajů je {name}, {city}, Slovensko. Kontakt: {email}, {phone}.']],
      ['Jaké údaje zpracováváme', [
        'Kontaktní formulář: jméno, e-mail, typ poptávky a text zprávy, který nám pošlete.',
        'Komunikace e-mailem nebo telefonicky: údaje, které nám v ní sami poskytnete.',
        'Technické údaje: IP adresa a údaje o prohlížeči, které automaticky zaznamenává server hostingu při návštěvě webu.',
      ]],
      ['Účel a právní základ', [
        'Odpověď na vaši poptávku a příprava cenové nabídky — opatření před uzavřením smlouvy (čl. 6 odst. 1 písm. b) GDPR).',
        'Ochrana webu a formuláře před zneužitím a spamem — oprávněný zájem (čl. 6 odst. 1 písm. f) GDPR).',
        'Anonymní statistika návštěvnosti bez cookies — oprávněný zájem na zlepšování webu (čl. 6 odst. 1 písm. f) GDPR).',
      ]],
      ['Příjemci a služby třetích stran', [
        'Poskytovatel hostingu, na kterém web běží.',
        'Telegram — doručení upozornění o nové poptávce z formuláře.',
        'Web3Forms — doručení zprávy z formuláře na náš e-mail.',
        'api.country.is — určení země podle IP adresy, abychom vám nabídli správný jazyk webu. Zemi neukládáme na serveru.',
        'Google Fonts — načtení písma; Google přitom může zpracovat vaši IP adresu.',
        'Pokud je zapnutá analytika (Umami nebo Plausible), funguje bez cookies a bez ukládání osobních údajů.',
        'U služeb mimo EU probíhá předání na základě standardních smluvních doložek nebo rámce EU–US Data Privacy Framework.',
      ]],
      ['Doba uchovávání', [
        'Poptávky uchováváme nejvýše 2 roky od poslední komunikace, pokud nevznikne smlouva.',
        'Pokud uzavřeme smlouvu, údaje uchováváme po dobu jejího trvání a podle zákonných lhůt (např. účetní doklady 10 let).',
      ]],
      ['Cookies a lokální úložiště', [
        'Nepoužíváme reklamní ani sledovací cookies.',
        'Ukládáme pouze cookie „lang" se zvoleným jazykem (1 rok) a v úložišti prohlížeče informaci o zemi a o skrytí jazykové nápovědy během relace. Jde o technicky nezbytné údaje, které nevyžadují souhlas.',
      ]],
      ['Vaše práva', [
        'Máte právo na přístup k údajům, jejich opravu, výmaz, omezení zpracování, přenositelnost a právo vznést námitku proti zpracování.',
        'Pokud zpracováváme údaje na základě souhlasu, můžete ho kdykoli odvolat.',
        'Stížnost můžete podat na Úrad na ochranu osobných údajov SR (dataprotection.gov.sk), na Úřad pro ochranu osobních údajů v ČR (uoou.gov.cz) nebo na dozorový úřad v zemi EU, kde žijete.',
      ]],
      ['Kontakt', ['S dotazy k ochraně osobních údajů nám napište na {email}.']],
    ],
  },
  uk: {
    title: 'Захист персональних даних',
    updated: 'Діє з 27.10.2026',
    intro: 'На цій сторінці пояснюємо, які персональні дані ми обробляємо, коли ви користуєтеся сайтом або зв’язуєтеся з нами, навіщо ми це робимо та які права ви маєте відповідно до регламенту GDPR.',
    sections: [
      ['Контролер даних', ['Контролером персональних даних є {name}, {city}, Словаччина. Контакт: {email}, {phone}.']],
      ['Які дані ми обробляємо', [
        'Контактна форма: ім’я, e-mail, тип запиту та текст повідомлення, яке ви надсилаєте.',
        'Листування або дзвінки: дані, які ви самі нам надаєте.',
        'Технічні дані: IP-адреса та дані браузера, які автоматично фіксує сервер хостингу під час відвідування сайту.',
      ]],
      ['Мета та правова підстава', [
        'Відповідь на ваш запит і підготовка комерційної пропозиції — дії до укладення договору (ст. 6(1)(b) GDPR).',
        'Захист сайту та форми від зловживань і спаму — законний інтерес (ст. 6(1)(f) GDPR).',
        'Анонімна статистика відвідувань без cookies — законний інтерес щодо покращення сайту (ст. 6(1)(f) GDPR).',
      ]],
      ['Отримувачі та сервіси третіх сторін', [
        'Хостинг-провайдер, на якому працює сайт.',
        'Telegram — доставка сповіщення про новий запит із форми.',
        'Web3Forms — доставка повідомлення з форми на наш e-mail.',
        'api.country.is — визначення країни за IP-адресою, щоб запропонувати правильну мову сайту. Країну ми не зберігаємо на сервері.',
        'Google Fonts — завантаження шрифтів; Google при цьому може обробити вашу IP-адресу.',
        'Якщо ввімкнено аналітику (Umami або Plausible), вона працює без cookies і без збереження персональних даних.',
        'Для сервісів поза ЄС передача відбувається на підставі стандартних договірних положень або рамки EU–US Data Privacy Framework.',
      ]],
      ['Строк зберігання', [
        'Запити зберігаємо не довше 2 років від останнього спілкування, якщо договір не укладено.',
        'Якщо ми уклали договір, дані зберігаються протягом його дії та в межах законних строків (наприклад, бухгалтерські документи — 10 років).',
      ]],
      ['Cookies і локальне сховище', [
        'Ми не використовуємо рекламні чи відстежувальні cookies.',
        'Зберігаємо лише cookie «lang» з обраною мовою (1 рік) і в сховищі браузера — інформацію про країну та про приховану мовну підказку протягом сесії. Це технічно необхідні дані, для яких згода не потрібна.',
      ]],
      ['Ваші права', [
        'Ви маєте право на доступ до даних, їх виправлення, видалення, обмеження обробки, перенесення та право заперечити проти обробки.',
        'Якщо ми обробляємо дані на підставі згоди, ви можете будь-коли її відкликати.',
        'Скаргу можна подати до Úrad na ochranu osobných údajov SR, Hraničná 12, 820 07 Bratislava (dataprotection.gov.sk), або до наглядового органу в країні ЄС, де ви проживаєте.',
      ]],
      ['Контакт', ['З питань захисту персональних даних пишіть нам на {email}.']],
    ],
  },
  en: {
    title: 'Privacy policy',
    updated: 'Effective from 27 October 2026',
    intro: 'This page explains what personal data we process when you use our website or contact us, why we do it and what rights you have under the GDPR.',
    sections: [
      ['Data controller', ['The controller of your personal data is {name}, {city}, Slovakia. Contact: {email}, {phone}.']],
      ['What data we process', [
        'Contact form: your name, e-mail, type of enquiry and the message you send us.',
        'E-mail or phone communication: the data you provide to us yourself.',
        'Technical data: IP address and browser information automatically logged by the hosting server when you visit the website.',
      ]],
      ['Purpose and legal basis', [
        'Replying to your enquiry and preparing a quote — steps prior to entering into a contract (Art. 6(1)(b) GDPR).',
        'Protecting the website and form against abuse and spam — legitimate interest (Art. 6(1)(f) GDPR).',
        'Anonymous, cookie-less visitor statistics — legitimate interest in improving the website (Art. 6(1)(f) GDPR).',
      ]],
      ['Recipients and third-party services', [
        'The hosting provider the website runs on.',
        'Telegram — delivering a notification about a new enquiry from the form.',
        'Web3Forms — delivering the form message to our e-mail.',
        'api.country.is — detecting your country from your IP address to offer the right website language. We do not store the country on our server.',
        'Google Fonts — loading fonts; Google may process your IP address in doing so.',
        'If analytics is enabled (Umami or Plausible), it works without cookies and without storing personal data.',
        'For services outside the EU, transfers are based on standard contractual clauses or the EU–US Data Privacy Framework.',
      ]],
      ['Retention period', [
        'We keep enquiries for no longer than 2 years after the last communication if no contract is concluded.',
        'If we conclude a contract, we keep the data for its duration and in line with statutory periods (e.g. accounting records for 10 years).',
      ]],
      ['Cookies and local storage', [
        'We do not use advertising or tracking cookies.',
        'We only store a "lang" cookie with your chosen language (1 year) and, in your browser storage, your country and whether you dismissed the language hint during the session. These are strictly necessary and do not require consent.',
      ]],
      ['Your rights', [
        'You have the right to access, rectify and erase your data, to restrict processing, to data portability and to object to processing.',
        'Where we process data based on consent, you can withdraw it at any time.',
        'You can lodge a complaint with the Office for Personal Data Protection of the Slovak Republic, Hraničná 12, 820 07 Bratislava (dataprotection.gov.sk), or with the supervisory authority in the EU country where you live.',
      ]],
      ['Contact', ['For questions about personal data protection, write to us at {email}.']],
    ],
  },
}
