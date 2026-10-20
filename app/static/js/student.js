// Student Interactive Task, Slide Deck & Lab Engine

let currentRoomCode = "";
let currentTopic = null;
let tasksList = [];
let currentTaskIndex = 0;
let currentUser = null;
let heartbeatInterval = null;
let currentSlideIndex = 0;

const slidesData8 = [
    {
        num: 1,
        title: "Стиснення даних і архівування",
        content: `
            <div class="text-center mb-4">
                <div class="text-indigo-400 text-sm font-semibold uppercase tracking-wider mb-1">Інформатика • 8 клас</div>
                <h3 class="text-2xl sm:text-3xl font-black text-white">Основи стиснення даних</h3>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4">
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">💾</div>
                    <div class="font-bold text-sm text-indigo-300">Менше місця</div>
                    <div class="text-xs text-slate-300">Як зменшити обсяг даних на носії?</div>
                </div>
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">⚡</div>
                    <div class="font-bold text-sm text-emerald-300">Швидше передавання</div>
                    <div class="text-xs text-slate-300">Чому невеликі файли зручніші в мережі?</div>
                </div>
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">📦</div>
                    <div class="font-bold text-sm text-amber-300">Один архів</div>
                    <div class="text-xs text-slate-300">Як об’єднати сотні файлів в один?</div>
                </div>
            </div>
        `
    },
    {
        num: 2,
        title: "Що таке стиснення даних?",
        content: `
            <p class="text-sm sm:text-base text-slate-200 mb-4 leading-relaxed">
                <strong>Стиснення даних</strong> — це зменшення обсягу даних, потрібного для їх зберігання або передавання за певним математичним алгоритмом.
            </p>
            <div class="bg-indigo-900/40 border border-indigo-400/30 p-4 rounded-2xl text-center my-3">
                <div class="text-xs font-bold uppercase text-indigo-300 mb-1">Приклад:</div>
                <div class="text-xl sm:text-2xl font-mono font-black text-white">10 МБ ➔ 4 МБ</div>
                <div class="text-xs text-emerald-400 font-semibold mt-1">Розмір зменшився на 6 МБ (економія 60%)</div>
            </div>
            <ul class="text-xs sm:text-sm text-slate-300 space-y-1.5 mt-3">
                <li>• Після стиснення файл займає менше місця на диску чи смартфоні.</li>
                <li>• Менший файл у рази швидше копіювати, завантажувати та передавати мережею.</li>
            </ul>
        `
    },
    {
        num: 3,
        title: "Навіщо стискати дані?",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 my-3">
                <div class="p-3.5 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-bold text-sm text-indigo-300 mb-1">1. Економія місця</div>
                    <p class="text-xs text-slate-300">На жорсткому диску або флешці можна зберегти в рази більше важливих файлів.</p>
                </div>
                <div class="p-3.5 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-bold text-sm text-emerald-300 mb-1">2. Передавання</div>
                    <p class="text-xs text-slate-300">Менші файли завантажуються швидше й економлять мобільний трафік.</p>
                </div>
                <div class="p-3.5 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-bold text-sm text-amber-300 mb-1">3. Зручність</div>
                    <p class="text-xs text-slate-300">Кілька файлів чи цілі папки можна об’єднати в один зручний архів.</p>
                </div>
            </div>
            <p class="text-xs text-slate-400 italic">Стиснення не завжди дає однаковий результат: усе залежить від типу даних і обраного алгоритму.</p>
        `
    },
    {
        num: 4,
        title: "Два основні види стиснення",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 my-3">
                <div class="p-4 bg-emerald-950/40 border border-emerald-500/30 rounded-2xl">
                    <div class="flex items-center gap-2 font-bold text-base text-emerald-400 mb-2">
                        <i class="fa-solid fa-shield-halved"></i> Без втрат (Lossless)
                    </div>
                    <p class="text-xs text-slate-300 mb-2">Після розпакування отримуємо <strong>ТОЧНО ті самі початкові дані</strong> (до кожного біта).</p>
                    <div class="text-[11px] text-emerald-300 font-semibold mb-1">Підходить для:</div>
                    <p class="text-xs text-slate-300">• текстів, документів, програм, таблиць, баз даних.</p>
                    <div class="text-xs font-mono text-emerald-400 mt-2 font-bold">Формати: ZIP, 7z, RAR, PNG, FLAC</div>
                </div>
                <div class="p-4 bg-amber-950/40 border border-amber-500/30 rounded-2xl">
                    <div class="flex items-center gap-2 font-bold text-base text-amber-400 mb-2">
                        <i class="fa-solid fa-eye-slash"></i> З втратами (Lossy)
                    </div>
                    <p class="text-xs text-slate-300 mb-2">Алгоритм прибирає частину даних, які людина майже не помічає при перегляді чи слуханні.</p>
                    <div class="text-[11px] text-amber-300 font-semibold mb-1">Використовується для:</div>
                    <p class="text-xs text-slate-300">• фотографій, музики, відеофільмів.</p>
                    <div class="text-xs font-mono text-amber-400 mt-2 font-bold">Формати: JPEG, MP3, AAC, MP4, WebP</div>
                </div>
            </div>
        `
    },
    {
        num: 5,
        title: "Стиснення без втрат: проста ідея",
        content: `
            <p class="text-xs sm:text-sm text-slate-300 mb-3">Якщо однакові дані часто повторюються, їх можна описати набагато коротше (RLE):</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-white/5 p-4 rounded-2xl border border-white/10 mb-3">
                <div>
                    <div class="text-xs font-bold text-rose-400 uppercase">До стиснення (15 символів):</div>
                    <div class="font-mono text-sm sm:text-base font-bold text-white bg-black/40 p-2 rounded-lg mt-1 tracking-widest">ААААААААААБББББ</div>
                </div>
                <div>
                    <div class="text-xs font-bold text-emerald-400 uppercase">Короткий запис (8 символів):</div>
                    <div class="font-mono text-sm sm:text-base font-bold text-emerald-300 bg-black/40 p-2 rounded-lg mt-1">10 × А, 5 × Б</div>
                </div>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">
                Головне: при стисненні без втрат усі початкові дані можна відновити абсолютно точно.
            </p>
        `
    },
    {
        num: 6,
        title: "Стиснення з втратами",
        content: `
            <p class="text-xs sm:text-sm text-slate-300 mb-3">
                Алгоритм прибирає частину інформації, яку вважає менш важливою для людського ока чи слуху:
            </p>
            <div class="grid grid-cols-2 gap-3 my-2 text-center">
                <div class="bg-white/10 p-3 rounded-2xl border border-white/10">
                    <div class="text-base font-bold text-indigo-300">🖼️ Фото</div>
                    <div class="text-xs font-mono text-white mt-1">BMP ➔ JPEG</div>
                    <div class="text-[11px] text-emerald-400">часто значно менше</div>
                </div>
                <div class="bg-white/10 p-3 rounded-2xl border border-white/10">
                    <div class="text-base font-bold text-indigo-300">🎵 Звук</div>
                    <div class="text-xs font-mono text-white mt-1">WAV ➔ MP3</div>
                    <div class="text-[11px] text-emerald-400">менший обсяг</div>
                </div>
            </div>
            <div class="p-3 bg-rose-950/40 border border-rose-500/30 rounded-xl text-xs text-rose-200 mt-3">
                ⚠️ <strong>Важливо:</strong> Надмірне стиснення може помітно погіршити якість зображення (артефакти) або звуку. Менше $\neq$ завжди краще!
            </div>
        `
    },
    {
        num: 7,
        title: "Що таке архівування?",
        content: `
            <p class="text-xs sm:text-sm text-slate-300 mb-3 leading-relaxed">
                <strong>Архівування</strong> — створення архівного файлу, у якому можна компактно зберігати один або багато файлів і папок.
            </p>
            <div class="p-4 bg-indigo-900/30 border border-indigo-500/30 rounded-2xl text-center my-3">
                <div class="text-xs text-indigo-300 font-bold uppercase mb-1">Схема:</div>
                <div class="text-sm sm:text-base font-mono font-bold text-white">Фото + Текст + Папка ➔ <span class="text-emerald-400">archive.zip</span></div>
            </div>
            <ul class="text-xs text-slate-300 space-y-1 mt-2">
                <li>• Під час створення архіву дані часто додатково стискаються без втрат.</li>
                <li>• Архів зручно копіювати, надсилати та зберігати як один цілісний файл.</li>
            </ul>
        `
    },
    {
        num: 8,
        title: "Поширені формати архівів",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 my-3">
                <div class="p-3 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-mono font-black text-indigo-400 text-lg">.ZIP</div>
                    <div class="text-xs font-bold text-white mb-1">Дуже поширений</div>
                    <p class="text-[11px] text-slate-300">Підтримується Windows та іншими ОС без встановлення сторонніх програм.</p>
                </div>
                <div class="p-3 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-mono font-black text-emerald-400 text-lg">.7z</div>
                    <div class="text-xs font-bold text-white mb-1">Архіватор 7-Zip</div>
                    <p class="text-[11px] text-slate-300">Забезпечує дуже високий ступінь стиснення за алгоритмом LZMA.</p>
                </div>
                <div class="p-3 bg-white/5 rounded-2xl border border-white/10">
                    <div class="font-mono font-black text-amber-400 text-lg">.RAR</div>
                    <div class="text-xs font-bold text-white mb-1">WinRAR</div>
                    <p class="text-[11px] text-slate-300">Популярний формат з широкими можливостями захисту.</p>
                </div>
            </div>
        `
    },
    {
        num: 9,
        title: "Архівування і розпакування",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 my-3">
                <div class="p-3.5 bg-blue-950/40 border border-blue-500/30 rounded-2xl text-xs">
                    <div class="font-bold text-blue-300 text-sm mb-2">📦 Створити архів:</div>
                    <ol class="space-y-1 text-slate-300 list-decimal pl-4">
                        <li>Виділити файли або папку.</li>
                        <li>Відкрити контекстне меню (права кнопка).</li>
                        <li>Обрати «Створити ZIP/архів».</li>
                        <li>Указати назву та параметри.</li>
                        <li>Отримати один архівний файл.</li>
                    </ol>
                </div>
                <div class="p-3.5 bg-emerald-950/40 border border-emerald-500/30 rounded-2xl text-xs">
                    <div class="font-bold text-emerald-300 text-sm mb-2">📂 Розпакувати архів:</div>
                    <ol class="space-y-1 text-slate-300 list-decimal pl-4">
                        <li>Вибрати архів.</li>
                        <li>Обрати «Видобути» / «Extract».</li>
                        <li>Указати папку призначення.</li>
                        <li>Дочекатися завершення.</li>
                        <li>Перевірити отримані файли.</li>
                    </ol>
                </div>
            </div>
        `
    },
    {
        num: 10,
        title: "Наскільки добре стиснувся файл?",
        content: `
            <p class="text-xs sm:text-sm text-slate-300 mb-3">Порівняємо початковий розмір і розмір після стиснення:</p>
            <div class="bg-indigo-900/40 border border-indigo-400/30 p-4 rounded-2xl my-3">
                <div class="text-xs font-bold text-indigo-300 mb-1">Приклад розрахунку:</div>
                <div class="flex justify-around items-center text-center my-2">
                    <div>
                        <div class="text-xs text-slate-400">Було:</div>
                        <div class="text-lg font-black font-mono text-white">20 МБ</div>
                    </div>
                    <div class="text-xl text-indigo-400">➔</div>
                    <div>
                        <div class="text-xs text-slate-400">Стало:</div>
                        <div class="text-lg font-black font-mono text-emerald-400">8 МБ</div>
                    </div>
                    <div class="text-xl text-indigo-400">=</div>
                    <div>
                        <div class="text-xs text-slate-400">Економія:</div>
                        <div class="text-lg font-black font-mono text-amber-300">60% (12 МБ)</div>
                    </div>
                </div>
                <div class="text-xs text-slate-300 mt-2 font-mono text-center">
                    Різниця: 20 − 8 = 12 МБ. Архів становить 8 / 20 × 100% = 40% від початкового розміру.
                </div>
            </div>
        `
    },
    {
        num: 11,
        title: "Чи всі файли стискаються однаково?",
        content: `
            <div class="space-y-2 my-2 text-xs">
                <div class="p-2.5 bg-emerald-950/40 border border-emerald-500/20 rounded-xl flex items-center justify-between">
                    <span>📄 <strong>TXT / документи:</strong> часто стискаються добре</span>
                    <span class="text-emerald-400 font-bold font-mono">Багато повторень (до 300x)</span>
                </div>
                <div class="p-2.5 bg-blue-950/40 border border-blue-500/20 rounded-xl flex items-center justify-between">
                    <span>🖼️ <strong>BMP:</strong> нестиснене зображення</span>
                    <span class="text-blue-400 font-bold font-mono">Значно зменшується в архіві</span>
                </div>
                <div class="p-2.5 bg-amber-950/40 border border-amber-500/20 rounded-xl flex items-center justify-between">
                    <span>📦 <strong>JPEG / MP3 / MP4 / DOCX:</strong> вже стиснені</span>
                    <span class="text-amber-400 font-bold font-mono">В ZIP зменшуються мало (~1.0x)</span>
                </div>
            </div>
            <p class="text-xs text-slate-400 mt-2">Результат залежить виключно від внутрішнього вмісту файлу.</p>
        `
    },
    {
        num: 12,
        title: "Пароль і безпека архіву",
        content: `
            <div class="p-4 bg-white/5 border border-white/10 rounded-2xl space-y-2 text-xs sm:text-sm text-slate-300 my-2">
                <p>• Деякі архіватори дозволяють захистити архів <strong>паролем і шифруванням</strong>.</p>
                <p>• Пароль потрібно зберігати: без нього відновити доступ може бути неможливо.</p>
                <p>• <strong>Архів із паролем не робить невідомий файл безпечним.</strong></p>
                <p>• Не відкривайте архіви та файли з невідомих або підозрілих джерел.</p>
            </div>
            <div class="p-3 bg-indigo-950/60 border border-indigo-400/40 rounded-xl text-center text-xs font-bold text-indigo-200 mt-3">
                🔒 Пам’ятайте: <span class="text-white">Архівування ≠ Резервна копія ≠ Антивірус</span>
            </div>
        `
    }
];

const slidesData9 = [
    {
        num: 1,
        title: "Формати файлів текстових документів",
        content: `<div class="text-center space-y-4"><div class="text-indigo-300 text-sm font-bold uppercase tracking-wider">Інформатика • 9 клас</div><p class="text-lg sm:text-xl text-white font-semibold">Режими роботи в середовищі текстового процесора</p><div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs"><div class="rounded-2xl bg-white/10 border border-white/10 p-4"><strong class="block text-indigo-300 mb-1">Формати</strong>DOCX • ODT • PDF • TXT • RTF</div><div class="rounded-2xl bg-white/10 border border-white/10 p-4"><strong class="block text-emerald-300 mb-1">Режими</strong>Редагування • Пропонування • Перегляд</div><div class="rounded-2xl bg-white/10 border border-white/10 p-4"><strong class="block text-amber-300 mb-1">Спільна робота</strong>Доступ • Коментарі • Версії</div></div></div>`
    },
    {
        num: 2,
        title: "Що таке формат файлу?",
        content: `<p class="text-sm sm:text-base text-slate-200 leading-relaxed">Формат визначає спосіб збереження даних і програми, які можуть із ними працювати. Його часто впізнають за розширенням у кінці назви.</p><div class="mt-5 rounded-2xl bg-indigo-900/40 border border-indigo-400/30 p-4 text-center font-mono font-black text-indigo-200">referat.docx &nbsp; referat.odt &nbsp; referat.pdf &nbsp; referat.txt</div><p class="mt-4 text-xs text-slate-300">Один текст можна зберегти в різних форматах, але оформлення, зображення й можливості редагування відрізнятимуться.</p>`
    },
    {
        num: 3,
        title: "Основні формати текстових документів",
        content: `<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs"><div class="p-3 rounded-xl bg-white/10"><strong class="text-blue-300">TXT</strong> — простий текст без складного оформлення та зображень.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-amber-300">RTF</strong> — текст із базовим форматуванням, сумісний із багатьма програмами.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-indigo-300">DOCX</strong> — формат Word зі складним оформленням, таблицями й зображеннями.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-emerald-300">ODT</strong> — відкритий формат LibreOffice Writer.</div><div class="p-3 rounded-xl bg-white/10 sm:col-span-2"><strong class="text-rose-300">PDF</strong> — зберігає вигляд сторінок для перегляду, друку й передавання.</div></div>`
    },
    {
        num: 4,
        title: "Який формат обрати?",
        content: `<div class="space-y-2 text-sm"><div class="p-3 rounded-xl bg-white/10"><strong class="text-indigo-300">Продовжити редагування:</strong> DOCX або ODT.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-rose-300">Надіслати готовий документ:</strong> PDF.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-blue-300">Зберегти лише текст:</strong> TXT.</div><div class="p-3 rounded-xl bg-white/10"><strong class="text-emerald-300">Працювати разом онлайн:</strong> Google Docs.</div></div>`
    },
    {
        num: 5,
        title: "Google Docs: документ у хмарі",
        content: `<div class="space-y-3 text-sm text-slate-200"><p>Google Docs — хмарний текстовий процесор, у якому документ створюють і редагують у веббраузері.</p><p>Зміни автоматично зберігаються на Google Drive. Документ можна відкрити з іншого пристрою після входу в обліковий запис.</p><p class="p-3 rounded-xl bg-emerald-950/50 border border-emerald-500/30 text-emerald-200">Іншим користувачам можна надати доступ для перегляду, коментування або редагування.</p></div>`
    },
    {
        num: 6,
        title: "Три режими роботи в Google Docs",
        content: `<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs"><div class="p-4 rounded-2xl bg-indigo-950/50 border border-indigo-500/30"><strong class="block text-indigo-300 text-sm mb-2">✏️ Редагування</strong>Зміни одразу стають частиною документа.</div><div class="p-4 rounded-2xl bg-amber-950/50 border border-amber-500/30"><strong class="block text-amber-300 text-sm mb-2">💬 Пропонування</strong>Правки показуються як пропозиції до прийняття.</div><div class="p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30"><strong class="block text-emerald-300 text-sm mb-2">👁️ Перегляд</strong>Документ можна читати без випадкових змін.</div></div>`
    },
    {
        num: 7,
        title: "Режим «Редагування»",
        content: `<p class="text-sm text-slate-200 leading-relaxed">Усі внесені зміни безпосередньо змінюють документ. Можна додавати й видаляти текст, форматувати його, вставляти таблиці та зображення.</p><div class="mt-4 p-4 rounded-2xl bg-indigo-900/40 border border-indigo-400/30 text-sm"><strong class="text-indigo-300">Приклад:</strong> учень пише реферат і самостійно виправляє помилки.</div>`
    },
    {
        num: 8,
        title: "Режим «Пропонування»",
        content: `<p class="text-sm text-slate-200">Доданий і видалений текст позначаються як запропоновані зміни. Автор документа може:</p><div class="grid grid-cols-2 gap-3 my-4 text-center font-bold"><div class="p-4 rounded-xl bg-emerald-950/50 text-emerald-300">✓ Прийняти</div><div class="p-4 rounded-xl bg-rose-950/50 text-rose-300">✕ Відхилити</div></div><p class="text-xs text-slate-300">Це зручно для перевірки роботи: учень бачить, що й хто пропонує змінити.</p>`
    },
    {
        num: 9,
        title: "Режим «Перегляд»",
        content: `<p class="text-sm sm:text-base text-slate-200 leading-relaxed">Основне завдання цього режиму — читати документ. Він захищає готовий матеріал від випадкових змін під час ознайомлення або демонстрації.</p><div class="mt-4 p-4 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 text-sm text-emerald-200">Можливість перейти до інших режимів залежить від наданих користувачу прав доступу.</div>`
    },
    {
        num: 10,
        title: "Режим роботи ≠ право доступу",
        content: `<div class="space-y-2 text-xs"><div class="p-3 rounded-xl bg-white/10"><strong class="text-slate-100">Читач:</strong> переглядає файл, але не змінює його й не коментує.</div><div class="p-3 rounded-xl bg-blue-950/50"><strong class="text-blue-300">Коментатор:</strong> переглядає, коментує та пропонує зміни, але не редагує текст напряму.</div><div class="p-3 rounded-xl bg-emerald-950/50"><strong class="text-emerald-300">Редактор:</strong> безпосередньо змінює документ і працює з коментарями та пропозиціями.</div></div>`
    },
    {
        num: 11,
        title: "Коментарі: обговорюємо, не змінюючи текст",
        content: `<ul class="space-y-2 text-sm text-slate-200"><li>• Коментар прив’язують до вибраного фрагмента або об’єкта.</li><li>• У ньому можна поставити запитання, пояснити помилку чи дати рекомендацію.</li><li>• Інші учасники можуть відповідати, а вирішене питання — завершити.</li></ul><div class="mt-4 p-3 rounded-xl bg-indigo-900/40 text-indigo-200 text-sm">«Перевір правопис цього слова» — коментар, а не зміна тексту.</div>`
    },
    {
        num: 12,
        title: "Історія версій",
        content: `<p class="text-sm text-slate-200">Google Docs автоматично зберігає зміни, час і авторів. Історія версій допомагає:</p><div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4 text-xs"><div class="p-3 bg-white/10 rounded-xl">знайти попередній варіант</div><div class="p-3 bg-white/10 rounded-xl">побачити внесок учасників</div><div class="p-3 bg-white/10 rounded-xl">відновити попередню версію</div><div class="p-3 bg-white/10 rounded-xl">не створювати безліч копій файлу</div></div>`
    },
    {
        num: 13,
        title: "Спільна робота над документом",
        content: `<div class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs text-center"><div class="p-3 rounded-xl bg-white/10"><strong class="block text-indigo-300 mb-1">1. Поділитися</strong>Надати доступ людям або за посиланням.</div><div class="p-3 rounded-xl bg-white/10"><strong class="block text-amber-300 mb-1">2. Обрати права</strong>Читач, коментатор або редактор.</div><div class="p-3 rounded-xl bg-white/10"><strong class="block text-emerald-300 mb-1">3. Працювати</strong>Спільно змінювати один документ.</div><div class="p-3 rounded-xl bg-white/10"><strong class="block text-rose-300 mb-1">4. Перевірити</strong>Коментарі, пропозиції та версії.</div></div>`
    }
];

let slidesData = slidesData8;

document.addEventListener("DOMContentLoaded", async () => {
    currentUser = getSavedUser();
    if (!currentUser) {
        window.location.href = "/";
        return;
    }

    const pathParts = window.location.pathname.split("/").filter(Boolean);
    currentRoomCode = pathParts[pathParts.length - 1];

    if (!currentRoomCode) {
        window.location.href = "/hierarchy";
        return;
    }

    await loadTopicData();
    setupPresenceTracking();
    renderSlide(0);
});

async function loadTopicData() {
    try {
        const resp = await fetch(`/api/tasks/topic/${currentRoomCode}?user_id=${currentUser.user_id}`);
        if (!resp.ok) {
            alert("Тему або кабінет не знайдено.");
            window.location.href = "/hierarchy";
            return;
        }

        const data = await resp.json();
        currentTopic = data.topic;
        tasksList = data.tasks;

        configureTopicWorkspace();

        // Render Topic Header Info
        document.getElementById("topic-grade-subject").textContent = `${currentTopic.grade_name} • ${currentTopic.subject_name}`;
        document.getElementById("topic-room-code").textContent = currentTopic.room_code;
        document.getElementById("topic-title").textContent = currentTopic.name;
        document.getElementById("topic-desc").textContent = currentTopic.description || "";
        document.getElementById("tab-tasks-count").textContent = tasksList.length;

        // Render Theory Markdown
        renderTheory(currentTopic.theory_content);

        // Find first unsolved task or start from 0
        const firstUnsolved = tasksList.findIndex(t => !t.is_solved);
        currentTaskIndex = firstUnsolved !== -1 ? firstUnsolved : 0;

        renderTaskNavPills();
        renderActiveTask();
        updateProgressBar();
    } catch (err) {
        console.error("Error loading topic:", err);
        alert("Помилка завантаження матеріалів.");
    }
}

function configureTopicWorkspace() {
    const isTextFormatsLesson = currentRoomCode === "info-9-formats";
    const isArchiveOperationsLesson = currentRoomCode === "info-8-archive-operations";
    const isDocumentLayoutLesson = currentRoomCode === "info-9-document-layout";
    slidesData = isTextFormatsLesson ? slidesData9 : slidesData8;
    currentSlideIndex = 0;

    const lab8 = document.getElementById("lab-8-content");
    const lab8Archives = document.getElementById("lab-8-archives-content");
    const lab9 = document.getElementById("lab-9-content");
    const lab9Layout = document.getElementById("lab-9-layout-content");
    const labTitle = document.getElementById("tab-lab-title");
    const downloadBtn = document.getElementById("slide-pptx-download-btn");

    if (lab8) lab8.classList.toggle("hidden", isTextFormatsLesson || isArchiveOperationsLesson || isDocumentLayoutLesson);
    if (lab8Archives) lab8Archives.classList.toggle("hidden", !isArchiveOperationsLesson);
    if (lab9) lab9.classList.toggle("hidden", !isTextFormatsLesson);
    if (lab9Layout) lab9Layout.classList.toggle("hidden", !isDocumentLayoutLesson);
    if (labTitle) labTitle.textContent = (isTextFormatsLesson || isArchiveOperationsLesson || isDocumentLayoutLesson) ? "Практична робота" : "Практична лабораторія";
    if (downloadBtn) {
        downloadBtn.href = isTextFormatsLesson
            ? "/static/materials/9class/text_formats/Informatyka_9_Formaty_faіliv_Rezhymy_Google_Docs_v2.pptx"
            : "/static/materials/8class/compress_archive01/Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx";
    }
    if (isTextFormatsLesson) restoreFormatsSizes();
    if (isArchiveOperationsLesson) restoreArchiveSizes();
}

function renderTheory(markdownText) {
    const el = document.getElementById("theory-markdown-body");
    if (!el) return;
    if (typeof marked !== "undefined" && marked.parse) {
        el.innerHTML = marked.parse(markdownText || "Теоретичний матеріал відсутній.");
    } else {
        el.innerText = markdownText || "Теоретичний матеріал відсутній.";
    }
}

function switchTab(tab) {
    const btnPractice = document.getElementById("tab-btn-practice");
    const btnLab = document.getElementById("tab-btn-lab");
    const btnTheory = document.getElementById("tab-btn-theory");

    const contentPractice = document.getElementById("tab-practice-content");
    const contentLab = document.getElementById("tab-lab-content");
    const contentTheory = document.getElementById("tab-theory-content");

    // Reset all tabs
    [btnPractice, btnLab, btnTheory].forEach(b => {
        if (b) b.className = "flex-1 py-2.5 px-3 rounded-xl text-slate-600 hover:text-slate-900 transition flex items-center justify-center gap-1.5 sm:gap-2";
    });
    [contentPractice, contentLab, contentTheory].forEach(c => {
        if (c) c.classList.add("hidden");
    });

    if (tab === "lab") {
        if (btnLab) btnLab.className = "flex-1 py-2.5 px-3 rounded-xl bg-white text-indigo-700 shadow-sm transition flex items-center justify-center gap-1.5 sm:gap-2 font-bold";
        if (contentLab) contentLab.classList.remove("hidden");
    } else if (tab === "theory") {
        if (btnTheory) btnTheory.className = "flex-1 py-2.5 px-3 rounded-xl bg-white text-indigo-700 shadow-sm transition flex items-center justify-center gap-1.5 sm:gap-2 font-bold";
        if (contentTheory) contentTheory.classList.remove("hidden");
    } else {
        if (btnPractice) btnPractice.className = "flex-1 py-2.5 px-3 rounded-xl bg-white text-brand-700 shadow-sm transition flex items-center justify-center gap-1.5 sm:gap-2 font-bold";
        if (contentPractice) contentPractice.classList.remove("hidden");
    }
}

// SLIDES VIEWER
function renderSlide(index) {
    if (index < 0 || index >= slidesData.length) return;
    currentSlideIndex = index;

    const slide = slidesData[index];
    const counterBadge = document.getElementById("slide-counter-badge");
    const bodyEl = document.getElementById("active-slide-body");
    const prevBtn = document.getElementById("slide-prev-btn");
    const nextBtn = document.getElementById("slide-next-btn");
    const dotsEl = document.getElementById("slide-dots");

    if (counterBadge) counterBadge.textContent = `Слайд ${slide.num} з ${slidesData.length}`;
    if (bodyEl) {
        bodyEl.innerHTML = `
            <div class="mb-2">
                <span class="text-xs font-mono font-bold text-indigo-400"># СЛАЙД ${slide.num}</span>
                <h3 class="text-xl sm:text-2xl font-black text-white mt-0.5">${slide.title}</h3>
            </div>
            ${slide.content}
        `;
    }

    if (prevBtn) prevBtn.disabled = (index === 0);
    if (nextBtn) nextBtn.disabled = (index === slidesData.length - 1);

    if (dotsEl) {
        dotsEl.innerHTML = "";
        slidesData.forEach((_, i) => {
            const dot = document.createElement("button");
            dot.type = "button";
            dot.onclick = () => renderSlide(i);
            dot.className = `w-2 h-2 rounded-full transition-all ${i === currentSlideIndex ? "bg-indigo-400 w-5" : "bg-white/20 hover:bg-white/40"}`;
            dotsEl.appendChild(dot);
        });
    }
}

function nextSlide() {
    if (currentSlideIndex < slidesData.length - 1) {
        renderSlide(currentSlideIndex + 1);
    }
}

function prevSlide() {
    if (currentSlideIndex > 0) {
        renderSlide(currentSlideIndex - 1);
    }
}

// LAB EXPERIMENTS
function runTextArchiveExperiment(type) {
    const origSizeEl = document.getElementById("lab-orig-size");
    const origKbEl = document.getElementById("lab-orig-kb");
    const zipSizeEl = document.getElementById("lab-zip-size");
    const zipKbEl = document.getElementById("lab-zip-kb");
    const savedPctEl = document.getElementById("lab-saved-pct");
    const savedBytesEl = document.getElementById("lab-saved-bytes");
    const ratioEl = document.getElementById("lab-ratio-val");
    const expEl = document.getElementById("lab-exp-explanation");

    const btnTxt = document.getElementById("exp-btn-txt");
    const btnDocx = document.getElementById("exp-btn-docx");
    const btnJpeg = document.getElementById("exp-btn-jpeg");

    [btnTxt, btnDocx, btnJpeg].forEach(b => {
        if (b) b.className = "py-2 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition";
    });

    if (type === "txt") {
        if (btnTxt) btnTxt.className = "py-2 px-4 rounded-xl bg-brand-600 text-white font-bold text-xs transition shadow-sm";
        origSizeEl.textContent = "430 000 байт";
        origKbEl.textContent = "(419.9 КБ)";
        zipSizeEl.textContent = "1 315 байт";
        zipKbEl.textContent = "(1.28 КБ)";
        savedPctEl.textContent = "99.7%";
        savedBytesEl.textContent = "-428 685 байт";
        ratioEl.textContent = "327.00×";
        expEl.innerHTML = `💡 <strong>Висновок:</strong> Текстовий файл містить багаторазове повторення однакових фраз («Інформатика - це цікаво»). Алгоритм Deflate замінив тисячі повторів короткими посиланнями, зменшивши обсяг у <strong>327 разів</strong>!`;
    } else if (type === "docx") {
        if (btnDocx) btnDocx.className = "py-2 px-4 rounded-xl bg-brand-600 text-white font-bold text-xs transition shadow-sm";
        origSizeEl.textContent = "24 318 байт";
        origKbEl.textContent = "(23.7 КБ)";
        zipSizeEl.textContent = "21 536 байт";
        zipKbEl.textContent = "(21.0 КБ)";
        savedPctEl.textContent = "11.4%";
        savedBytesEl.textContent = "-2 782 байт";
        ratioEl.textContent = "1.13×";
        expEl.innerHTML = `💡 <strong>Висновок:</strong> Документ .docx уже є упакованим ZIP-архівом XML-файлів. Повторна архівація вже стиснених даних дає мінімальний ефект (лише у <strong>1.13 раза</strong>).`;
    } else if (type === "jpeg_zip") {
        if (btnJpeg) btnJpeg.className = "py-2 px-4 rounded-xl bg-brand-600 text-white font-bold text-xs transition shadow-sm";
        origSizeEl.textContent = "11 735 063 байт";
        origKbEl.textContent = "(11.74 МБ)";
        zipSizeEl.textContent = "11 680 580 байт";
        zipKbEl.textContent = "(11.68 МБ)";
        savedPctEl.textContent = "0.5%";
        savedBytesEl.textContent = "-54 483 байт";
        ratioEl.textContent = "1.00×";
        expEl.innerHTML = `💡 <strong>Висновок:</strong> Фотографія JPEG уже містить стиснені з втратами піксельні блоки. Архіватор ZIP майже не зміг зменшити її розмір ($K \\approx 1.0\\times$).`;
    }
}

function setImageQualityPreset(quality) {
    const labelEl = document.getElementById("img-comp-label");
    const badgeEl = document.getElementById("img-comp-size-badge");
    const imgEl = document.getElementById("compressed-preview-img");
    const artifactsBadge = document.getElementById("img-artifacts-badge");
    const sizeMetric = document.getElementById("img-metric-size");
    const savedMetric = document.getElementById("img-metric-saved");
    const ratioMetric = document.getElementById("img-metric-ratio");

    document.querySelectorAll(".img-preset-btn").forEach(b => {
        b.className = "img-preset-btn py-1.5 px-3 rounded-lg text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700";
    });

    const activeBtn = document.getElementById(`preset-${quality}`);
    if (activeBtn) {
        activeBtn.className = "img-preset-btn py-1.5 px-3 rounded-lg text-xs font-bold bg-slate-900 text-white shadow-sm";
    }

    if (quality === 100) {
        if (labelEl) labelEl.textContent = "Оригінал (100% якість)";
        if (badgeEl) badgeEl.textContent = "11 735 063 байт (11.74 МБ)";
        if (imgEl) imgEl.src = "/static/materials/8class/compress_archive01/preview_orig.jpg";
        if (artifactsBadge) {
            artifactsBadge.className = "absolute bottom-2 left-2 px-2 py-0.5 rounded bg-emerald-600/90 text-[10px] font-bold text-white";
            artifactsBadge.textContent = "Оригінал без втрат";
        }
        if (sizeMetric) sizeMetric.textContent = "11.74 МБ";
        if (savedMetric) savedMetric.textContent = "0.0%";
        if (ratioMetric) ratioMetric.textContent = "1.0×";
    } else if (quality === 15) {
        if (labelEl) labelEl.textContent = "Помірне стиснення (якість ~15%)";
        if (badgeEl) badgeEl.textContent = "1 173 500 байт (1.17 МБ)";
        if (imgEl) imgEl.src = "/static/materials/8class/compress_archive01/preview_low_quality.jpg";
        if (artifactsBadge) {
            artifactsBadge.className = "absolute bottom-2 left-2 px-2 py-0.5 rounded bg-amber-600/90 text-[10px] font-bold text-white";
            artifactsBadge.textContent = "Помітні втрати дрібних деталей";
        }
        if (sizeMetric) sizeMetric.textContent = "1.17 МБ";
        if (savedMetric) savedMetric.textContent = "90.0%";
        if (ratioMetric) ratioMetric.textContent = "10.0×";
    } else if (quality === 1) {
        if (labelEl) labelEl.textContent = "Екстремальне стиснення (якість 1%)";
        if (badgeEl) badgeEl.textContent = "60 904 байт (60 КБ / 0.06 МБ)";
        if (imgEl) imgEl.src = "/static/materials/8class/compress_archive01/preview_low_quality.jpg";
        if (artifactsBadge) {
            artifactsBadge.className = "absolute bottom-2 left-2 px-2 py-0.5 rounded bg-rose-600/90 text-[10px] font-bold text-white";
            artifactsBadge.textContent = "Сильні артефакти та розмиття";
        }
        if (sizeMetric) sizeMetric.textContent = "0.06 МБ (60 КБ)";
        if (savedMetric) savedMetric.textContent = "99.5%";
        if (ratioMetric) ratioMetric.textContent = "195.6×";
    }
}

function parseFileSize(value) {
    const normalized = String(value || "").trim().toLowerCase().replace(",", ".").replace(/\s+/g, " ");
    const match = normalized.match(/^(\d+(?:\.\d+)?)\s*(кб|kb|мб|mb|байт(?:и|ів)?|bytes?|б)?$/i);
    if (!match) return null;

    const amount = Number(match[1]);
    if (!Number.isFinite(amount) || amount <= 0) return null;
    const unit = match[2] || "кб";
    if (unit === "мб" || unit === "mb") return amount * 1024;
    if (unit.startsWith("байт") || ["byte", "bytes", "б"].includes(unit)) return amount / 1024;
    return amount;
}

function handleArchiveSizesForm(event) {
    event.preventDefault();
    const rows = ["img1", "img2", "kameniari", "texts", "all"];
    const values = {};
    let firstInvalid = null;

    rows.forEach(row => {
        const originalInput = document.getElementById(`archive-original-${row}`);
        const zipInput = document.getElementById(`archive-zip-${row}`);
        const originalKb = parseFileSize(originalInput ? originalInput.value : "");
        const zipKb = parseFileSize(zipInput ? zipInput.value : "");
        [originalInput, zipInput].forEach((input, index) => {
            const invalid = index === 0 ? originalKb === null : zipKb === null;
            if (input) {
                input.classList.toggle("border-rose-500", invalid);
                input.classList.toggle("bg-rose-50", invalid);
            }
            if (invalid && !firstInvalid) firstInvalid = input;
        });
        values[row] = {
            originalLabel: originalInput ? originalInput.value.trim() : "",
            zipLabel: zipInput ? zipInput.value.trim() : "",
            originalKb,
            zipKb
        };
    });

    const feedback = document.getElementById("archive-sizes-feedback");
    if (firstInvalid) {
        if (feedback) {
            feedback.className = "p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-semibold text-rose-800";
            feedback.textContent = "Перевірте всі значення. Приклад правильного запису: 1315 байтів, 21 КБ або 11.7 МБ.";
        }
        firstInvalid.focus();
        return;
    }

    rows.forEach(row => {
        const ratio = values[row].originalKb / values[row].zipKb;
        const saving = (1 - values[row].zipKb / values[row].originalKb) * 100;
        const savingCell = document.getElementById(`archive-saving-${row}`);
        const ratioCell = document.getElementById(`archive-ratio-${row}`);
        if (savingCell) savingCell.textContent = `${saving.toFixed(1)}%`;
        if (ratioCell) ratioCell.textContent = `${ratio.toFixed(2)}×`;
        values[row].saving = saving;
    });

    localStorage.setItem("info-8-archive-sizes", JSON.stringify(
        Object.fromEntries(rows.map(row => [row, {
            original: values[row].originalLabel,
            zip: values[row].zipLabel
        }]))
    ));

    const individualRows = ["img1", "img2", "kameniari", "texts"];
    const labelsMap = {
        img1: "6711626.png",
        img2: "742940.png",
        kameniari: "Каменярі.docx",
        texts: "тексти з малюнками.docx"
    };
    const best = individualRows.sort((a, b) => values[b].saving - values[a].saving)[0];
    if (feedback) {
        feedback.className = "p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-900";
        feedback.textContent = `Результати обчислено й збережено. Найбільшу економію серед окремих файлів показав файл: ${labelsMap[best] || best}.`;
    }
}

function restoreArchiveSizes() {
    let saved = null;
    try {
        saved = JSON.parse(localStorage.getItem("info-8-archive-sizes"));
    } catch (error) {
        saved = null;
    }
    if (!saved) return;
    Object.entries(saved).forEach(([row, measurements]) => {
        const originalInput = document.getElementById(`archive-original-${row}`);
        const zipInput = document.getElementById(`archive-zip-${row}`);
        if (originalInput && measurements.original) originalInput.value = measurements.original;
        if (zipInput && measurements.zip) zipInput.value = measurements.zip;
    });
}

function handleFormatsSizeForm(event) {
    event.preventDefault();
    const formats = ["txt", "odt", "docx", "pdf", "rtf"];
    const values = {};
    let firstInvalid = null;

    formats.forEach(format => {
        const input = document.getElementById(`size-input-${format}`);
        const sizeKb = parseFileSize(input ? input.value : "");
        if (input) {
            input.classList.toggle("border-rose-500", sizeKb === null);
            input.classList.toggle("bg-rose-50", sizeKb === null);
        }
        if (sizeKb === null && !firstInvalid) firstInvalid = input;
        values[format] = { label: input ? input.value.trim() : "", sizeKb };
    });

    const feedback = document.getElementById("formats-form-feedback");
    if (firstInvalid) {
        if (feedback) {
            feedback.className = "mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-semibold text-rose-800";
            feedback.textContent = "Заповніть усі п’ять полів числом та одиницею вимірювання, наприклад 8.2 КБ або 12.8 МБ.";
        }
        firstInvalid.focus();
        return;
    }

    formats.forEach(format => {
        const cell = document.getElementById(`measured-size-${format}`);
        if (cell) cell.textContent = values[format].label;
    });

    const sorted = formats.slice().sort((a, b) => values[a].sizeKb - values[b].sizeKb);
    const smallest = sorted[0].toUpperCase();
    const largest = sorted[sorted.length - 1].toUpperCase();
    const ratio = values[sorted[sorted.length - 1]].sizeKb / values[sorted[0]].sizeKb;
    localStorage.setItem("info-9-formats-file-sizes", JSON.stringify(
        Object.fromEntries(formats.map(format => [format, values[format].label]))
    ));

    if (feedback) {
        feedback.className = "mt-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-900";
        feedback.textContent = `Вимірювання збережено. Найменший файл — ${smallest}, найбільший — ${largest}; різниця приблизно у ${ratio.toFixed(1)} раза.`;
    }
}

function fillExampleFormatsSizes() {
    const examples = { txt: "8.2 КБ", odt: "12.8 МБ", docx: "12.8 МБ", pdf: "14.5 МБ", rtf: "135 МБ" };
    Object.entries(examples).forEach(([format, value]) => {
        const input = document.getElementById(`size-input-${format}`);
        if (input) input.value = value;
    });
}

function restoreFormatsSizes() {
    let saved = null;
    try {
        saved = JSON.parse(localStorage.getItem("info-9-formats-file-sizes"));
    } catch (error) {
        saved = null;
    }
    if (!saved) return;
    Object.entries(saved).forEach(([format, value]) => {
        const input = document.getElementById(`size-input-${format}`);
        const cell = document.getElementById(`measured-size-${format}`);
        if (input) input.value = value;
        if (cell) cell.textContent = value;
    });
}

// TASK RENDERING & SUBMISSION
function renderTaskNavPills() {
    const container = document.getElementById("task-nav-pills");
    if (!container) return;
    container.innerHTML = "";

    tasksList.forEach((task, idx) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.onclick = () => selectTask(idx);

        let statusClass = "bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200";
        let iconHtml = `${idx + 1}`;

        if (task.is_solved) {
            statusClass = "bg-emerald-100 text-emerald-800 border-emerald-300 font-bold";
            iconHtml = `<i class="fa-solid fa-check text-xs"></i> ${idx + 1}`;
        } else if (task.attempts_count > 0 && !task.last_is_correct) {
            statusClass = "bg-rose-100 text-rose-800 border-rose-300 font-bold";
            iconHtml = `<i class="fa-solid fa-xmark text-xs"></i> ${idx + 1}`;
        }

        if (idx === currentTaskIndex) {
            statusClass += " ring-2 ring-brand-500 ring-offset-1 font-black shadow-sm";
        }

        btn.className = `flex-1 min-w-[36px] sm:min-w-0 py-2 px-1 text-center rounded-xl border text-xs sm:text-sm transition flex items-center justify-center gap-1 ${statusClass}`;
        btn.innerHTML = iconHtml;
        container.appendChild(btn);
    });

    document.getElementById("current-task-badge").textContent = `Завдання ${currentTaskIndex + 1} / ${tasksList.length}`;
}

function selectTask(index) {
    if (index < 0 || index >= tasksList.length) return;
    currentTaskIndex = index;
    renderTaskNavPills();
    renderActiveTask();
    sendHeartbeat();
}

function renderActiveTask() {
    const task = tasksList[currentTaskIndex];
    if (!task) return;

    document.getElementById("card-task-number").textContent = `Завдання #${task.task_order}`;
    const promptLabel = document.getElementById("task-prompt-label");
    const questionTextEl = document.getElementById("question-text");
    const input = document.getElementById("answer-input");
    const inputGroupContainer = document.getElementById("input-group-container");
    const signToggleBtn = document.getElementById("sign-toggle-btn");
    const mathKeypad = document.getElementById("math-keypad-container");
    const choiceContainer = document.getElementById("choice-options-container");
    const feedbackBox = document.getElementById("feedback-box");
    const activeCard = document.getElementById("active-task-card");
    const submitBtn = document.getElementById("submit-btn");
    const nextBtn = document.getElementById("next-task-btn");
    const statusBadge = document.getElementById("task-status-badge");
    const attemptsIndicator = document.getElementById("task-attempts-indicator");

    // Set prompt & question
    const isMathTask = task.question.startsWith("Обчисліть: ") || task.question.startsWith("Знайдіть ");
    if (isMathTask) {
        if (promptLabel) promptLabel.textContent = "Обчисліть вираз:";
        questionTextEl.textContent = task.question.replace("Обчисліть: ", "").replace(" = ?", "");
    } else {
        if (promptLabel) promptLabel.textContent = "Умова завдання:";
        questionTextEl.textContent = task.question;
    }

    // Parse options if choice task
    let options = null;
    if (task.options) {
        try {
            options = typeof task.options === "string" ? JSON.parse(task.options) : task.options;
        } catch (e) {
            options = null;
        }
    }

    // Render choice options if available
    if (options && Array.isArray(options) && options.length > 0) {
        choiceContainer.classList.remove("hidden");
        choiceContainer.innerHTML = "";
        if (inputGroupContainer) inputGroupContainer.classList.add("hidden");
        if (mathKeypad) mathKeypad.classList.add("hidden");
        if (signToggleBtn) signToggleBtn.classList.add("hidden");
        
        const currentSelected = (input.value || task.last_answer || "").trim().toUpperCase();

        options.forEach(opt => {
            const optBtn = document.createElement("button");
            optBtn.type = "button";
            optBtn.onclick = () => selectChoiceOption(opt.key);
            
            const isSelected = (currentSelected === opt.key.toUpperCase());
            optBtn.className = `p-4 rounded-2xl border-2 text-left transition-all flex items-start gap-3.5 cursor-pointer ${
                isSelected 
                ? 'border-brand-500 bg-brand-50/90 shadow-md ring-4 ring-brand-500/20 text-brand-950 font-bold scale-[1.01]' 
                : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 text-slate-800'
            }`;
            optBtn.innerHTML = `
                <div class="w-8 h-8 rounded-xl font-black text-sm flex items-center justify-center shrink-0 transition ${
                    isSelected ? 'bg-brand-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700'
                }">
                    ${opt.key}
                </div>
                <div class="text-sm sm:text-base font-semibold leading-relaxed pt-0.5 flex-1">
                    ${opt.text}
                </div>
                ${isSelected ? '<div class="text-brand-600 text-xl pt-0.5 shrink-0"><i class="fa-solid fa-circle-check"></i></div>' : ''}
            `;
            choiceContainer.appendChild(optBtn);
        });
    } else {
        choiceContainer.classList.add("hidden");
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (isMathTask) {
            if (mathKeypad) mathKeypad.classList.remove("hidden");
            if (signToggleBtn) signToggleBtn.classList.remove("hidden");
            input.placeholder = "Ваше число";
        } else {
            if (mathKeypad) mathKeypad.classList.add("hidden");
            if (signToggleBtn) signToggleBtn.classList.add("hidden");
            input.placeholder = "Введіть розраховане число або коефіцієнт (напр. 327)";
        }
    }

    // Reset card classes
    activeCard.className = "bg-white rounded-3xl p-6 sm:p-10 border-2 border-slate-200 shadow-sm transition-all relative overflow-hidden";
    feedbackBox.classList.add("hidden");
    input.value = task.last_answer || "";
    input.disabled = false;
    submitBtn.classList.remove("hidden");
    nextBtn.classList.add("hidden");

    attemptsIndicator.textContent = `Спроб: ${task.attempts_count || 0}`;

    if (task.is_solved) {
        statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200";
        statusBadge.textContent = "✅ Вирішено вірно";
        activeCard.className = "bg-emerald-50/30 rounded-3xl p-6 sm:p-10 border-2 border-emerald-300 shadow-sm transition-all relative overflow-hidden";
        showFeedback(true, "Ви вже успішно розв'язали це завдання! 🎉", null);
        nextBtn.classList.remove("hidden");
    } else if (task.attempts_count > 0 && !task.last_is_correct) {
        statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200";
        statusBadge.textContent = "❌ Помилка в останній спробі";
        activeCard.className = "bg-rose-50/20 rounded-3xl p-6 sm:p-10 border-2 border-rose-300 shadow-sm transition-all relative overflow-hidden";
        showFeedback(false, "Неправильно. Спробуй ще раз! 💡", task.hint);
    } else {
        statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200";
        statusBadge.textContent = "Очікує відповіді";
    }

    // Prev / Next button states
    document.getElementById("prev-task-btn").disabled = (currentTaskIndex === 0);
    document.getElementById("nav-next-btn").disabled = (currentTaskIndex === tasksList.length - 1);
}

function selectChoiceOption(key) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;
    const input = document.getElementById("answer-input");
    input.value = key;
    if (task) {
        task.last_answer = key;
    }
    renderActiveTask();
}

function showFeedback(isCorrect, message, hint) {
    const feedbackBox = document.getElementById("feedback-box");
    const icon = document.getElementById("feedback-icon");
    const title = document.getElementById("feedback-title");
    const hintEl = document.getElementById("feedback-hint");

    feedbackBox.classList.remove("hidden");

    if (isCorrect) {
        feedbackBox.className = "p-4 rounded-2xl border text-sm font-semibold transition-all bg-emerald-50 border-emerald-300 text-emerald-900";
        icon.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-600"></i>`;
        title.textContent = message || "Правильно! Відмінна робота!";
        hintEl.textContent = "";
    } else {
        feedbackBox.className = "p-4 rounded-2xl border text-sm font-semibold transition-all bg-rose-50 border-rose-300 text-rose-900";
        icon.innerHTML = `<i class="fa-solid fa-circle-xmark text-rose-600"></i>`;
        title.textContent = message || "Неправильно. Спробуй ще раз!";
        hintEl.textContent = hint ? `Підказка: ${hint}` : "";
    }
}

async function handleAnswerSubmit(e) {
    if (e) e.preventDefault();
    const task = tasksList[currentTaskIndex];
    if (!task) return;

    const input = document.getElementById("answer-input");
    const answer = (input.value || task.last_answer || "").trim();
    if (!answer) {
        showFeedback(false, "Будь ласка, оберіть один із варіантів відповіді!", null);
        return;
    }

    const submitBtn = document.getElementById("submit-btn");
    submitBtn.disabled = true;

    try {
        const resp = await fetch("/api/tasks/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                task_id: task.id,
                submitted_answer: answer,
                room_code: currentRoomCode
            })
        });

        const result = await resp.json();
        submitBtn.disabled = false;

        task.attempts_count = (task.attempts_count || 0) + 1;
        task.last_answer = answer;
        task.last_is_correct = result.is_correct;
        if (result.is_correct) {
            task.is_solved = true;
        }

        const activeCard = document.getElementById("active-task-card");
        const statusBadge = document.getElementById("task-status-badge");
        const attemptsIndicator = document.getElementById("task-attempts-indicator");
        attemptsIndicator.textContent = `Спроб: ${task.attempts_count}`;

        if (result.is_correct) {
            activeCard.className = "bg-emerald-50/40 rounded-3xl p-6 sm:p-10 border-2 border-emerald-400 shadow-sm transition-all relative overflow-hidden";
            statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200";
            statusBadge.textContent = "✅ Вирішено вірно";
            showFeedback(true, result.message, null);
            document.getElementById("next-task-btn").classList.remove("hidden");

            if (typeof confetti === "function") {
                confetti({
                    particleCount: 40,
                    spread: 60,
                    origin: { y: 0.7 }
                });
            }
        } else {
            activeCard.className = "bg-rose-50/20 rounded-3xl p-6 sm:p-10 border-2 border-rose-400 shadow-sm transition-all relative overflow-hidden animate-shake";
            setTimeout(() => activeCard.classList.remove("animate-shake"), 600);
            statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200";
            statusBadge.textContent = "❌ Помилка в останній спробі";
            showFeedback(false, result.message, result.hint);
        }

        renderTaskNavPills();
        updateProgressBar();
    } catch (err) {
        console.error(err);
        submitBtn.disabled = false;
        alert("Помилка відправки відповіді.");
    }
}

function updateProgressBar() {
    const solvedCount = tasksList.filter(t => t.is_solved).length;
    const total = tasksList.length;
    const pct = total > 0 ? Math.round((solvedCount / total) * 100) : 0;

    document.getElementById("progress-text").textContent = `${solvedCount} з ${total} (${pct}%)`;
    document.getElementById("progress-bar-fill").style.width = `${pct}%`;
}

function goToNextTask() {
    if (currentTaskIndex < tasksList.length - 1) {
        selectTask(currentTaskIndex + 1);
    }
}

function goToPrevTask() {
    if (currentTaskIndex > 0) {
        selectTask(currentTaskIndex - 1);
    }
}

function keypadPress(val) {
    const input = document.getElementById("answer-input");
    input.value += val;
    input.focus();
}

function keypadBackspace() {
    const input = document.getElementById("answer-input");
    input.value = input.value.slice(0, -1);
    input.focus();
}

function toggleMinusSign() {
    const input = document.getElementById("answer-input");
    let val = input.value.trim();
    if (val.startsWith("-")) {
        input.value = val.substring(1);
    } else {
        input.value = "-" + val;
    }
    input.focus();
}

// PRESENCE & VISIBILITY TRACKING
function setupPresenceTracking() {
    sendHeartbeat();
    heartbeatInterval = setInterval(sendHeartbeat, 10000);

    document.addEventListener("visibilitychange", () => {
        sendHeartbeat();
    });

    window.addEventListener("focus", () => sendHeartbeat());
    window.addEventListener("blur", () => sendHeartbeat());
}

async function sendHeartbeat() {
    if (!currentUser || !currentRoomCode) return;
    const isTabActive = (document.visibilityState === "visible") && document.hasFocus();
    const activeTask = tasksList[currentTaskIndex];

    try {
        await fetch("/api/presence/heartbeat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                room_code: currentRoomCode,
                is_tab_active: isTabActive,
                current_task_id: activeTask ? activeTask.id : null
            })
        });
    } catch (e) {
        console.error("Heartbeat fail:", e);
    }
}
