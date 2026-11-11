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

const slidesData8Hardware = [
    {
        num: 1,
        title: "Сучасний персональний комп’ютер",
        content: `
            <div class="text-center mb-4">
                <div class="text-indigo-400 text-sm font-semibold uppercase tracking-wider mb-1">Інформатика • 8 клас</div>
                <h3 class="text-2xl sm:text-3xl font-black text-white">Складові ПК, процесор та пристрої пам'яті</h3>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4 text-xs">
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">🖥️</div>
                    <div class="font-bold text-sm text-indigo-300">Апаратна складова</div>
                    <div class="text-slate-300 mt-1">CPU, RAM, Материнська плата, GPU, БЖ</div>
                </div>
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">⚡</div>
                    <div class="font-bold text-sm text-emerald-300">Процесор (CPU)</div>
                    <div class="text-slate-300 mt-1">Тактова частота, ядра, розрядність</div>
                </div>
                <div class="bg-white/10 p-4 rounded-2xl border border-white/10 text-center">
                    <div class="text-2xl mb-1">💾</div>
                    <div class="font-bold text-sm text-amber-300">Види пам'яті</div>
                    <div class="text-slate-300 mt-1">Внутрішня (RAM/ROM) та зовнішня (SSD/HDD)</div>
                </div>
            </div>
        `
    },
    {
        num: 2,
        title: "Що таке персональний комп’ютер?",
        content: `
            <p class="text-sm sm:text-base text-slate-200 mb-3 leading-relaxed">
                <strong>Персональний комп’ютер (ПК)</strong> — це електронна машина універсального призначення, створена для зручної індивідуальної роботи одного користувача.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-2.5 my-3 text-xs text-center">
                <div class="p-3 bg-white/5 rounded-xl border border-white/10">
                    <div class="text-lg mb-1">🖥️</div>
                    <strong class="text-indigo-300 block">Десктоп</strong>
                    <span class="text-slate-400">Настільний блок</span>
                </div>
                <div class="p-3 bg-white/5 rounded-xl border border-white/10">
                    <div class="text-lg mb-1">💻</div>
                    <strong class="text-emerald-300 block">Ноутбук</strong>
                    <span class="text-slate-400">Мобільний ПК</span>
                </div>
                <div class="p-3 bg-white/5 rounded-xl border border-white/10">
                    <div class="text-lg mb-1">🔲</div>
                    <strong class="text-amber-300 block">Моноблок</strong>
                    <span class="text-slate-400">ПК у моніторі</span>
                </div>
                <div class="p-3 bg-white/5 rounded-xl border border-white/10">
                    <div class="text-lg mb-1">📦</div>
                    <strong class="text-rose-300 block">Міні-ПК</strong>
                    <span class="text-slate-400">Компактний неттоп</span>
                </div>
            </div>
            <p class="text-xs text-slate-300 italic">Для роботи комп'ютера необхідна злагоджена взаємодія апаратного (Hardware) та програмного (Software) забезпечення.</p>
        `
    },
    {
        num: 3,
        title: "Основні складові системного блоку",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs my-2">
                <div class="p-3 bg-indigo-950/50 rounded-xl border border-indigo-400/30">
                    <strong class="text-indigo-300 block text-sm mb-1">⚙️ Центральний процесор (CPU)</strong>
                    Виконує команди програм, здійснює обчислення та керує іншими пристроями.
                </div>
                <div class="p-3 bg-blue-950/50 rounded-xl border border-blue-400/30">
                    <strong class="text-blue-300 block text-sm mb-1">🔌 Материнська плата</strong>
                    Головна плата, що з'єднує всі складові між собою шинами даних і живлення.
                </div>
                <div class="p-3 bg-emerald-950/50 rounded-xl border border-emerald-400/30">
                    <strong class="text-emerald-300 block text-sm mb-1">🧠 Оперативна пам’ять (RAM)</strong>
                    Тимчасово утримує запущені програми й відкриті документи для швидкого доступу CPU.
                </div>
                <div class="p-3 bg-amber-950/50 rounded-xl border border-amber-400/30">
                    <strong class="text-amber-300 block text-sm mb-1">💽 Накопичувач (SSD / HDD)</strong>
                    Забезпечує довготривале зберігання файлів та операційної системи без живлення.
                </div>
            </div>
        `
    },
    {
        num: 4,
        title: "Принцип роботи комп'ютера",
        content: `
            <p class="text-xs sm:text-sm text-slate-200 mb-3">Від введення початкових даних до отримання результату:</p>
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs text-center my-2">
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <div class="font-bold text-indigo-300 mb-1">1. Введення</div>
                    <span class="text-slate-300">Клавіатура, миша, мікрофон</span>
                </div>
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <div class="font-bold text-blue-300 mb-1">2. Пам'ять (RAM)</div>
                    <span class="text-slate-300">Приймає дані відкритої програми</span>
                </div>
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <div class="font-bold text-emerald-300 mb-1">3. Процесор (CPU)</div>
                    <span class="text-slate-300">Виконує обчислення та інструкції</span>
                </div>
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <div class="font-bold text-amber-300 mb-1">4. Виведення</div>
                    <span class="text-slate-300">Монітор, динаміки, принтер</span>
                </div>
            </div>
            <div class="p-3 bg-indigo-900/30 border border-indigo-400/30 rounded-xl text-center text-xs text-indigo-200 mt-3 font-mono">
                Зовнішня пам'ять (SSD/HDD) ⟷ RAM ⟷ Кеш/Регістри ⟷ CPU
            </div>
        `
    },
    {
        num: 5,
        title: "Процесор (CPU) — «мозок» ПК",
        content: `
            <div class="p-4 bg-white/5 border border-white/10 rounded-2xl text-xs sm:text-sm text-slate-200 space-y-2 mb-3">
                <p>• <strong>CPU (Central Processing Unit)</strong> — центральний процесор.</p>
                <p>• Виконує машинні інструкції: арифметичні обчислення, логічні порівняння та керування потоком команд.</p>
                <p>• Опрацьовує дані, завантажені в оперативну пам’ять, взаємодіючи з відеокартою та дисками.</p>
                <p>• Сучасний кремнієвий мікропроцесор містить <strong>мільярди мікроскопічних транзисторів</strong> на кристалі площею в кілька квадратних сантиметрів.</p>
            </div>
        `
    },
    {
        num: 6,
        title: "Основні характеристики процесора",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs my-2">
                <div class="p-3.5 bg-indigo-950/60 rounded-xl border border-indigo-400/30">
                    <strong class="text-indigo-300 block text-sm mb-1">⏱️ Тактова частота</strong>
                    Кількість елементарних тактів за 1 секунду. Одиниця вимірювання — <strong>ГГц</strong> ($1\\text{ ГГц} = 10^9\\text{ тактів/с}$).<br>
                    <span class="text-slate-400 text-[11px]">Приклад: 3.6 ГГц</span>
                </div>
                <div class="p-3.5 bg-emerald-950/60 rounded-xl border border-emerald-400/30">
                    <strong class="text-emerald-300 block text-sm mb-1">🧩 Кількість ядер</strong>
                    Кількість незалежних обчислювальних ядер для паралельної роботи.<br>
                    <span class="text-slate-400 text-[11px]">Приклад: 4, 6, 8, 16 ядер</span>
                </div>
                <div class="p-3.5 bg-amber-950/60 rounded-xl border border-amber-400/30">
                    <strong class="text-amber-300 block text-sm mb-1">🔢 Розрядність</strong>
                    Розмір двійкового слова регістрів у бітах за 1 такт.<br>
                    <span class="text-slate-400 text-[11px]">Сучасні CPU: 64 біти</span>
                </div>
            </div>
        `
    },
    {
        num: 7,
        title: "Внутрішня пам'ять: RAM (Оперативна)",
        content: `
            <p class="text-xs sm:text-sm text-slate-200 leading-relaxed mb-3">
                <strong>RAM (Random Access Memory)</strong> — пам'ять із довільним доступом для поточної роботи системи.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs my-2">
                <div class="p-3.5 bg-emerald-950/50 rounded-xl border border-emerald-400/30">
                    <strong class="text-emerald-300 block text-sm mb-1">⚡ Висока швидкість</strong>
                    Процесор звертається до RAM у тисячі разів швидше, ніж до жорсткого диска.
                </div>
                <div class="p-3.5 bg-rose-950/50 rounded-xl border border-rose-400/30">
                    <strong class="text-rose-300 block text-sm mb-1">⚠️ Енергозалежність</strong>
                    При вимкненні комп'ютера всі дані в RAM повністю зникають!
                </div>
            </div>
            <p class="text-xs text-slate-300 mt-2"><strong>Важливе правило:</strong> Відкрити файл у програмі ≠ зберегти його. Незбережені зміни втрачаються без живлення.</p>
        `
    },
    {
        num: 8,
        title: "Кеш-пам'ять та регістри процесора",
        content: `
            <div class="space-y-3 text-xs sm:text-sm text-slate-200">
                <div class="p-3.5 bg-white/10 rounded-xl border border-white/10">
                    <strong class="text-indigo-300 text-sm block mb-1">🚀 Кеш-пам'ять (Cache L1, L2, L3)</strong>
                    Надшвидка буферна пам'ять безпосередньо в кристалі CPU. Зберігає копії найчастіше затребуваних даних і зменшує затримки звернення до повільнішої RAM.
                </div>
                <div class="p-3.5 bg-white/10 rounded-xl border border-white/10">
                    <strong class="text-emerald-300 text-sm block mb-1">🎯 Регістри процесора</strong>
                    Найшвидші комірки пам'яті всередині обчислювального ядра. Утримують числа, адреси та проміжні результати поточної операції (наприклад: $5 + 3 = 8$).
                </div>
            </div>
        `
    },
    {
        num: 9,
        title: "Постійна пам'ять: UEFI / BIOS (ROM)",
        content: `
            <div class="p-4 bg-white/5 border border-white/10 rounded-2xl text-xs sm:text-sm text-slate-200 space-y-2 mb-3">
                <p>• <strong>ROM / Flash UEFI/BIOS</strong> — мікросхема постійної енергонезалежної пам'яті на материнській платі.</p>
                <p>• <strong>Призначення:</strong> містить мікропрограму первинного запуску ПК, перевірки обладнання (POST) та старту завантажувача ОС.</p>
                <p>• <strong>Енергонезалежність:</strong> зберігає дані навіть при повному знеструмленні комп'ютера.</p>
                <p>• У сучасних ПК прошивку можна безпечно оновлювати за допомогою спеціальних утиліт виробника.</p>
            </div>
        `
    },
    {
        num: 10,
        title: "Зовнішня пам'ять: HDD проти SSD",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs my-2">
                <div class="p-3.5 bg-blue-950/50 rounded-xl border border-blue-400/30">
                    <strong class="text-blue-300 block text-sm mb-1">🧲 HDD (Жорсткий магнітний диск)</strong>
                    • Обертові магнітні пластини + голівки.<br>
                    • <strong>+</strong> Дешевий за 1 ТБ, велика місткість.<br>
                    • <strong>−</strong> Повільний, шумить, боїться падінь і струсів.
                </div>
                <div class="p-3.5 bg-emerald-950/50 rounded-xl border border-emerald-400/30">
                    <strong class="text-emerald-300 block text-sm mb-1">⚡ SSD (Твердотільний накопичувач)</strong>
                    • Flash-мікросхеми без рухомих деталей.<br>
                    • <strong>+</strong> Колосальна швидкість, безшумний, стійкий.<br>
                    • <strong>−</strong> Вища вартість за 1 ГБ обсягу.
                </div>
            </div>
            <p class="text-xs text-slate-300 text-center mt-2 font-semibold">ОС та програми встановлюють на SSD для максимальної швидкодії, а великі архіви зберігають на HDD.</p>
        `
    },
    {
        num: 11,
        title: "Знімні носії та оптичні диски",
        content: `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs my-2">
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <strong class="text-amber-300 block text-sm mb-1">🔌 Flash-носії (USB & SD)</strong>
                    • <strong>USB-флешки:</strong> універсальне перенесення файлів.<br>
                    • <strong>SD / microSD:</strong> карти для камер, смартфонів.<br>
                    • Зручні, компактні та енергонезалежні.
                </div>
                <div class="p-3 bg-white/10 rounded-xl border border-white/10">
                    <strong class="text-rose-300 block text-sm mb-1">💿 Оптичні диски (Laser)</strong>
                    • <strong>CD:</strong> близько $700\\text{ МБ}$.<br>
                    • <strong>DVD:</strong> $4.7\\text{ ГБ}$ (одношаровий).<br>
                    • <strong>Blu-ray:</strong> $25\\text{ ГБ}$ (для відео високої якості).
                </div>
            </div>
        `
    },
    {
        num: 12,
        title: "Ієрархія пам'яті комп'ютера",
        content: `
            <div class="space-y-2 text-xs my-2">
                <div class="p-2.5 bg-emerald-900/60 rounded-xl border border-emerald-400/40 text-center font-bold text-emerald-200">
                    ⚡ 1. Регістри CPU (Найшвидші, обсяг у байтах, усередині ядра)
                </div>
                <div class="p-2.5 bg-teal-900/50 rounded-xl border border-teal-400/30 text-center font-bold text-teal-200">
                    🚀 2. Кеш-пам'ять L1, L2, L3 (Надшвидка, мегабайти)
                </div>
                <div class="p-2.5 bg-blue-900/50 rounded-xl border border-blue-400/30 text-center font-bold text-blue-200">
                    🧠 3. Оперативна пам'ять RAM (Швидка, 8–64 ГБ, енергозалежна)
                </div>
                <div class="p-2.5 bg-indigo-900/50 rounded-xl border border-indigo-400/30 text-center font-bold text-indigo-200">
                    💽 4. Зовнішні накопичувачі SSD / HDD (Місткі, до десятків ТБ, енергонезалежні)
                </div>
            </div>
            <p class="text-xs text-slate-300 text-center mt-2 italic">Чим ближче пам'ять до обчислювального ядра процесора — тим вона швидша і дорожча.</p>
        `
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
    connectStudentWebSocket();
    renderSlide(0);

    const answerInput = document.getElementById("answer-input");
    if (answerInput) {
        answerInput.addEventListener("input", () => {
            updateFactorProductPreview();
        });
    }
});

let studentWs = null;
let currentFactorizationState = {
    taskId: null,
    numbers: [504],
    activeNumberIndex: 0,
    factorMap: {
        504: []
    }
};

function connectStudentWebSocket() {
    if (!currentUser || !currentRoomCode) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/room/${currentRoomCode}/student/${currentUser.user_id}`;

    try {
        studentWs = new WebSocket(wsUrl);

        studentWs.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.event === "student_progress_reset" && msg.data.user_id === currentUser.user_id) {
                    const toastMsg = msg.data.is_full_reset
                        ? "Вчитель скинув ваш прогрес у цьому кабінеті. Ви можете пройти завдання заново! 🔄"
                        : "Вчитель скинув спроби для завдання. Ви можете спробувати знову! 🔄";
                    alert(toastMsg);
                    loadTopicData();
                }
            } catch (e) {
                console.error("Student WS Parse error:", e);
            }
        };

        studentWs.onclose = () => {
            setTimeout(connectStudentWebSocket, 4000);
        };
    } catch (err) {
        console.warn("WS connect failed:", err);
    }
}

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
    const isArchiveOperationsLesson = currentRoomCode === "info-8-archive-operations" || currentRoomCode === "info-8-final-archives";
    const isDocumentLayoutLesson = currentRoomCode === "info-9-document-layout";
    const isStylesLesson = currentRoomCode === "info-9-styles-and-structure";
    const isHardwareLesson = currentRoomCode === "info-8-pc-hardware";
    const isSlideDeckLesson = isTextFormatsLesson || isArchiveOperationsLesson || currentRoomCode === "info-8-compress" || isHardwareLesson;
    const hasLab = isTextFormatsLesson || isArchiveOperationsLesson || isDocumentLayoutLesson || isStylesLesson;

    if (isHardwareLesson) {
        slidesData = slidesData8Hardware;
    } else if (isTextFormatsLesson) {
        slidesData = slidesData9;
    } else {
        slidesData = slidesData8;
    }
    currentSlideIndex = 0;

    const lab8 = document.getElementById("lab-8-content");
    const lab8Archives = document.getElementById("lab-8-archives-content");
    const lab9 = document.getElementById("lab-9-content");
    const lab9Layout = document.getElementById("lab-9-layout-content");
    const lab9Styles = document.getElementById("lab-9-styles-content");
    const labTitle = document.getElementById("tab-lab-title");
    const downloadBtn = document.getElementById("slide-pptx-download-btn");
    const tabBtnLab = document.getElementById("tab-btn-lab");
    const slideDeckViewer = document.getElementById("slide-deck-viewer");

    if (tabBtnLab) tabBtnLab.classList.toggle("hidden", !hasLab);
    if (slideDeckViewer) slideDeckViewer.classList.toggle("hidden", !isSlideDeckLesson);

    if (lab8) lab8.classList.toggle("hidden", isTextFormatsLesson || isArchiveOperationsLesson || isDocumentLayoutLesson || isStylesLesson || !hasLab);
    if (lab8Archives) lab8Archives.classList.toggle("hidden", !isArchiveOperationsLesson);
    if (lab9) lab9.classList.toggle("hidden", !isTextFormatsLesson);
    if (lab9Layout) lab9Layout.classList.toggle("hidden", !isDocumentLayoutLesson);
    if (lab9Styles) lab9Styles.classList.toggle("hidden", !isStylesLesson);
    if (labTitle) labTitle.textContent = (isTextFormatsLesson || isArchiveOperationsLesson || isDocumentLayoutLesson || isStylesLesson) ? "Практична робота" : "Практична лабораторія";
    if (downloadBtn) {
        if (isHardwareLesson) {
            downloadBtn.href = "/static/materials/8class/proc/Informatyka_9_Suchasnyi_PK_Protsesor_Kharakterystyky_v2.pptx";
        } else if (isTextFormatsLesson) {
            downloadBtn.href = "/static/materials/9class/text_formats/Informatyka_9_Formaty_faіliv_Rezhymy_Google_Docs_v2.pptx";
        } else {
            downloadBtn.href = "/static/materials/8class/compress_archive01/Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx";
        }
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

function formatMathFractions(str) {
    if (!str) return "";
    let s = String(str);
    // Replace negative power like 5^{-1}, 5^-1 or $5^{-1}$
    s = s.replace(/\$?(\d+)\^\{?(-1)\}?\$?/g, '$1<sup>-1</sup>');
    // Replace mixed fractions with LaTeX-like format: W \frac{a}{b}
    s = s.replace(/(\d+)\s*\\frac\{([^\}]+)\}\{([^\}]+)\}/g, '<span class="mixed-fraction"><span class="whole-part">$1</span><span class="inline-fraction"><span class="num">$2</span><span class="denom">$3</span></span></span>');
    // Replace simple LaTeX-like fractions: \frac{a}{b}
    s = s.replace(/\\frac\{([^\}]+)\}\{([^\}]+)\}/g, '<span class="inline-fraction"><span class="num">$1</span><span class="denom">$2</span></span>');
    // Replace plain mixed fraction e.g. "3 2/5" or "1 25/100" (preceded by start/space/operator and followed by end/space/operator)
    s = s.replace(/(^|[\s\(\+\-\=\:\·\,\;])(\d+)\s+(\d+)\s*\/\s*(\d+)(?=[\s\)\+\-\=\:\·\,\;\?\.\!]|$)/g, '$1<span class="mixed-fraction"><span class="whole-part">$2</span><span class="inline-fraction"><span class="num">$3</span><span class="denom">$4</span></span></span>');
    // Replace plain fraction e.g. "3/7" or "5/5"
    s = s.replace(/(^|[\s\(\+\-\=\:\·\,\;])(\d+)\s*\/\s*(\d+)(?=[\s\)\+\-\=\:\·\,\;\?\.\!]|$)/g, '$1<span class="inline-fraction"><span class="num">$2</span><span class="denom">$3</span></span>');
    return s;
}

let activeMixedField = "whole";

function selectMixedField(field) {
    activeMixedField = field;
    const wholeInput = document.getElementById("mixed-whole-input");
    const fracInput = document.getElementById("mixed-fraction-input");
    if (!wholeInput || !fracInput) return;
    
    if (field === "whole") {
        wholeInput.className = "w-20 sm:w-24 text-center text-2xl sm:text-3xl font-black py-2.5 px-2 rounded-xl border-2 border-brand-500 bg-brand-50/40 ring-4 ring-brand-500/20 outline-none transition cursor-pointer";
        fracInput.className = "w-28 sm:w-36 text-center text-xl sm:text-2xl font-black py-2.5 px-2 rounded-xl border-2 border-slate-300 bg-white outline-none transition cursor-pointer";
    } else {
        fracInput.className = "w-28 sm:w-36 text-center text-xl sm:text-2xl font-black py-2.5 px-2 rounded-xl border-2 border-brand-500 bg-brand-50/40 ring-4 ring-brand-500/20 outline-none transition cursor-pointer";
        wholeInput.className = "w-20 sm:w-24 text-center text-2xl sm:text-3xl font-black py-2.5 px-2 rounded-xl border-2 border-slate-300 bg-white outline-none transition cursor-pointer";
    }
}

function updateMixedFractionSync() {
    const wholeInput = document.getElementById("mixed-whole-input");
    const fracInput = document.getElementById("mixed-fraction-input");
    const answerInput = document.getElementById("answer-input");
    const previewEl = document.getElementById("mixed-fraction-preview");
    if (!wholeInput || !fracInput || !answerInput) return;

    const w = wholeInput.value.trim();
    const f = fracInput.value.trim();
    let combined = "";

    if (w && w !== "0" && f) {
        combined = `${w} ${f}`;
    } else if (f) {
        combined = f;
    } else if (w) {
        combined = w;
    }

    answerInput.value = combined;
    const task = tasksList[currentTaskIndex];
    if (task) {
        task.last_answer = combined;
    }

    if (previewEl) {
        if (!combined) {
            previewEl.innerHTML = `Ваша відповідь: <span class="text-slate-400 font-normal">порожньо</span>`;
        } else {
            previewEl.innerHTML = `Ваша відповідь: <strong class="text-brand-900">${formatMathFractions(combined)}</strong>`;
        }
    }
}

function fractionKeypadPress(val) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const isMixedFraction = (task && (task.task_type === "mixed_fraction"));
    if (isMixedFraction) {
        const targetInput = activeMixedField === "whole" 
            ? document.getElementById("mixed-whole-input") 
            : document.getElementById("mixed-fraction-input");
        if (!targetInput) return;
        
        // If in whole part and user presses '/', automatically switch to fraction part
        if (activeMixedField === "whole" && val === "/") {
            selectMixedField("fraction");
            return;
        }

        // Avoid multiple slashes in fraction field
        if (val === "/" && targetInput.value.includes("/")) return;
        // Avoid comma in mixed fraction integer fields
        if (val === ",") return;

        targetInput.value += val;
        updateMixedFractionSync();
    } else {
        const input = document.getElementById("answer-input");
        if (!input) return;
        if (val === "/" && input.value.includes("/")) return;
        if (val === "," && (input.value.includes(",") || input.value.includes("."))) return;
        input.value += val;
        if (task) task.last_answer = input.value;
    }
}

function fractionKeypadBackspace() {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const isMixedFraction = (task && (task.task_type === "mixed_fraction"));
    if (isMixedFraction) {
        const targetInput = activeMixedField === "whole" 
            ? document.getElementById("mixed-whole-input") 
            : document.getElementById("mixed-fraction-input");
        if (!targetInput) return;
        targetInput.value = targetInput.value.slice(0, -1);
        updateMixedFractionSync();
    } else {
        const input = document.getElementById("answer-input");
        if (!input) return;
        input.value = input.value.slice(0, -1);
        if (task) task.last_answer = input.value;
    }
}

function fractionKeypadClear() {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const isMixedFraction = (task && (task.task_type === "mixed_fraction"));
    if (isMixedFraction) {
        const wholeInput = document.getElementById("mixed-whole-input");
        const fracInput = document.getElementById("mixed-fraction-input");
        if (wholeInput) wholeInput.value = "";
        if (fracInput) fracInput.value = "";
        selectMixedField("whole");
        updateMixedFractionSync();
    } else {
        const input = document.getElementById("answer-input");
        if (!input) return;
        input.value = "";
        if (task) task.last_answer = "";
    }
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
    const fractionKeypad = document.getElementById("fraction-keypad-container");
    const fractionKeypadCommaBtn = document.getElementById("fraction-keypad-comma-btn");
    const fractionKeypadSlashBtn = document.getElementById("fraction-keypad-slash-btn");
    const mixedFractionContainer = document.getElementById("mixed-fraction-container");
    const choiceContainer = document.getElementById("choice-options-container");
    const signSequenceContainer = document.getElementById("sign-sequence-container");
    const primeFactorContainer = document.getElementById("prime-factorization-container");
    const numberLineContainer = document.getElementById("number-line-container");
    const coordinatePlaneContainer = document.getElementById("coordinate-plane-container");
    const feedbackBox = document.getElementById("feedback-box");
    const activeCard = document.getElementById("active-task-card");
    const submitBtn = document.getElementById("submit-btn");
    const nextBtn = document.getElementById("next-task-btn");
    const statusBadge = document.getElementById("task-status-badge");
    const attemptsIndicator = document.getElementById("task-attempts-indicator");

    // Reset default visibility & input attributes
    if (signSequenceContainer) signSequenceContainer.classList.add("hidden");
    if (primeFactorContainer) primeFactorContainer.classList.add("hidden");
    if (numberLineContainer) numberLineContainer.classList.add("hidden");
    if (coordinatePlaneContainer) coordinatePlaneContainer.classList.add("hidden");
    if (choiceContainer) choiceContainer.classList.add("hidden");
    if (mixedFractionContainer) mixedFractionContainer.classList.add("hidden");
    if (fractionKeypad) fractionKeypad.classList.add("hidden");
    if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
    if (mathKeypad) mathKeypad.classList.add("hidden");
    if (signToggleBtn) signToggleBtn.classList.add("hidden");
    input.readOnly = false;
    input.removeAttribute("inputmode");

    // Set prompt & question with horizontal fraction support
    const isMathTask = task.question.startsWith("Обчисліть: ") || task.question.startsWith("Знайдіть ");
    if (isMathTask) {
        if (promptLabel) promptLabel.textContent = "Обчисліть вираз:";
        questionTextEl.innerHTML = formatMathFractions(task.question.replace("Обчисліть: ", "").replace(" = ?", ""));
    } else {
        if (promptLabel) promptLabel.textContent = "Умова завдання:";
        questionTextEl.innerHTML = formatMathFractions(task.question);
    }

    // Parse options if choice / multichoice task
    let options = null;
    if (task.options) {
        try {
            options = typeof task.options === "string" ? JSON.parse(task.options) : task.options;
        } catch (e) {
            options = null;
        }
    }

    const isMultiChoice = (task.task_type === "multichoice");
    const isChoice = (task.task_type === "choice") || (options && Array.isArray(options) && options.length > 0 && !isMultiChoice);
    const isSignSequence = (task.task_type === "sign_sequence") || (currentRoomCode === "math-6-brackets-signs");
    const isPrimeFactor = (task.task_type === "prime_factorization") || (currentRoomCode === "math-6-prime-factorization");
    const isNumberLinePoint = (task.task_type === "number_line_point");
    const isNumberLineRead = (task.task_type === "number_line_read");
    const isNumberLineMidpoint = (task.task_type === "number_line_midpoint");
    const isCoordinatePlaneRect = (task.task_type === "coordinate_plane_rect");
    const isMixedFraction = (task.task_type === "mixed_fraction");
    const isFractionInput = (task.task_type === "fraction_input") || (currentRoomCode === "math-6-fractions-sr1" && task.task_order >= 1 && task.task_order <= 5);
    const isDecimalInput = (task.task_type === "decimal_input") || (currentRoomCode === "math-6-fractions-sr3" && task.task_order >= 1 && task.task_order <= 10);

    if (isChoice || isMultiChoice) {
        choiceContainer.classList.remove("hidden");
        choiceContainer.innerHTML = "";
        if (inputGroupContainer) inputGroupContainer.classList.add("hidden");

        if (options && options.length >= 8) {
            choiceContainer.className = "grid grid-cols-2 sm:grid-cols-5 gap-2.5 mb-6 max-w-2xl mx-auto";
        } else {
            choiceContainer.className = "grid grid-cols-1 gap-2.5 mb-6 max-w-xl mx-auto";
        }

        const rawVal = (input.value || task.last_answer || "").trim().toUpperCase();
        let selectedKeys = [];
        if (isMultiChoice) {
            selectedKeys = rawVal.split(/[\s,]+/).filter(Boolean);
        } else {
            selectedKeys = rawVal ? [rawVal] : [];
        }

        options.forEach(opt => {
            const optBtn = document.createElement("button");
            optBtn.type = "button";
            optBtn.onclick = () => isMultiChoice ? toggleMultiChoiceOption(opt.key) : selectChoiceOption(opt.key);

            const isSelected = selectedKeys.includes(opt.key.toUpperCase());
            optBtn.className = `p-3.5 sm:p-4 rounded-2xl border-2 text-left transition-all flex items-start gap-3 cursor-pointer ${
                isSelected 
                ? 'border-brand-500 bg-brand-50/90 shadow-md ring-4 ring-brand-500/20 text-brand-950 font-bold scale-[1.01]' 
                : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 text-slate-800'
            }`;
            optBtn.innerHTML = `
                <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl font-black text-xs sm:text-sm flex items-center justify-center shrink-0 transition ${
                    isSelected ? 'bg-brand-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700'
                }">
                    ${opt.key}
                </div>
                <div class="text-sm sm:text-base font-semibold leading-relaxed pt-0.5 flex-1">
                    ${formatMathFractions(opt.text)}
                </div>
                ${isSelected ? '<div class="text-brand-600 text-lg pt-0.5 shrink-0"><i class="fa-solid fa-circle-check"></i></div>' : ''}
            `;
            choiceContainer.appendChild(optBtn);
        });

        if (isMultiChoice) {
            const multiHint = document.createElement("div");
            multiHint.className = "col-span-full text-center text-xs font-semibold text-slate-500 pt-1";
            multiHint.innerHTML = `💡 <em>Можна обрати декілька правильних відповідей. Обрано: <strong>${selectedKeys.length > 0 ? selectedKeys.join(", ") : "жодної"}</strong></em>`;
            choiceContainer.appendChild(multiHint);
        }
    } else if (isMixedFraction) {
        if (inputGroupContainer) inputGroupContainer.classList.add("hidden");
        if (mixedFractionContainer) mixedFractionContainer.classList.remove("hidden");
        if (fractionKeypad) fractionKeypad.classList.remove("hidden");
        if (fractionKeypadCommaBtn) fractionKeypadCommaBtn.classList.add("hidden");
        if (fractionKeypadSlashBtn) fractionKeypadSlashBtn.classList.remove("hidden");

        const wholeInput = document.getElementById("mixed-whole-input");
        const fracInput = document.getElementById("mixed-fraction-input");
        const initialAns = (task.last_answer || input.value || "").trim();
        
        let initialWhole = "";
        let initialFrac = "";
        if (initialAns) {
            const parts = initialAns.split(/\s+/);
            if (parts.length === 2) {
                initialWhole = parts[0];
                initialFrac = parts[1];
            } else if (parts.length === 1) {
                if (parts[0].includes("/")) {
                    initialFrac = parts[0];
                } else {
                    initialWhole = parts[0];
                }
            }
        }
        if (wholeInput) wholeInput.value = initialWhole;
        if (fracInput) fracInput.value = initialFrac;
        selectMixedField(initialWhole ? "fraction" : "whole");
        updateMixedFractionSync();
    } else if (isFractionInput) {
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (fractionKeypad) fractionKeypad.classList.remove("hidden");
        if (fractionKeypadCommaBtn) fractionKeypadCommaBtn.classList.add("hidden");
        if (fractionKeypadSlashBtn) fractionKeypadSlashBtn.classList.remove("hidden");
        input.placeholder = "напр. 1/5";
        input.readOnly = true;
        input.setAttribute("inputmode", "none");
    } else if (isDecimalInput) {
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (fractionKeypad) fractionKeypad.classList.remove("hidden");
        if (fractionKeypadCommaBtn) fractionKeypadCommaBtn.classList.remove("hidden");
        if (fractionKeypadSlashBtn) fractionKeypadSlashBtn.classList.add("hidden");
        input.placeholder = "напр. 0.7 або 3.25";
        input.readOnly = true;
        input.setAttribute("inputmode", "none");
    } else if (isNumberLinePoint) {
        if (numberLineContainer) numberLineContainer.classList.remove("hidden");
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (signToggleBtn) signToggleBtn.classList.remove("hidden");
        input.placeholder = "Координата точки (напр. -4)";
        setupNumberLineWidget(task, "point");
    } else if (isNumberLineRead) {
        if (numberLineContainer) numberLineContainer.classList.remove("hidden");
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (mathKeypad) mathKeypad.classList.remove("hidden");
        if (signToggleBtn) signToggleBtn.classList.remove("hidden");
        input.placeholder = "Введіть координату точки (напр. -5)";
        setupNumberLineWidget(task, "read");
    } else if (isNumberLineMidpoint) {
        if (numberLineContainer) numberLineContainer.classList.remove("hidden");
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (mathKeypad) mathKeypad.classList.remove("hidden");
        if (signToggleBtn) signToggleBtn.classList.remove("hidden");
        input.placeholder = "Координата середини (напр. -2)";
        setupNumberLineWidget(task, "midpoint");
    } else if (isCoordinatePlaneRect) {
        if (coordinatePlaneContainer) coordinatePlaneContainer.classList.remove("hidden");
        if (inputGroupContainer) inputGroupContainer.classList.add("hidden");
        setupCoordinatePlaneWidget(task);
    } else if (isSignSequence) {
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (signSequenceContainer) signSequenceContainer.classList.remove("hidden");
        input.placeholder = "Послідовність знаків (напр. ---)";
        input.readOnly = true;
        input.setAttribute("inputmode", "none");
    } else if (isPrimeFactor) {
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (primeFactorContainer) primeFactorContainer.classList.remove("hidden");
        if (mathKeypad) mathKeypad.classList.remove("hidden");
        if (signToggleBtn) signToggleBtn.classList.remove("hidden");
        if (task.question.includes("НСД") || task.question.includes("найбільший спільний дільник")) {
            input.placeholder = "НСД або спільні множники (напр. 24 або 2, 2, 2, 3)";
        } else if (task.question.includes("НСК") || task.question.includes("найменше спільне кратне")) {
            input.placeholder = "НСК або множники (напр. 84 або 2, 2, 3, 7)";
        } else {
            input.placeholder = "Прості множники (напр. 2, 2, 2, 3, 3, 7)";
        }
        setupPrimeFactorizationState(task);
    } else {
        if (inputGroupContainer) inputGroupContainer.classList.remove("hidden");
        if (currentRoomCode === "math-6-control-2") {
            if (mathKeypad) mathKeypad.classList.remove("hidden");
            if (signToggleBtn) signToggleBtn.classList.remove("hidden");
            if (task.task_order === 21 || task.task_order === 22) {
                input.placeholder = "-10;-20";
            } else {
                input.placeholder = "-10";
            }
        } else if (isMathTask) {
            if (mathKeypad) mathKeypad.classList.remove("hidden");
            if (signToggleBtn) signToggleBtn.classList.remove("hidden");
            input.placeholder = "Ваше число";
        } else {
            input.placeholder = "Введіть розраховану відповідь (напр. -7a або -5)";
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

function toggleMultiChoiceOption(key) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const input = document.getElementById("answer-input");
    let currentSelected = (input.value || task?.last_answer || "").split(/[\s,]+/).map(s => s.trim().toUpperCase()).filter(Boolean);

    if (currentSelected.includes(key.toUpperCase())) {
        currentSelected = currentSelected.filter(k => k !== key.toUpperCase());
    } else {
        currentSelected.push(key.toUpperCase());
    }

    currentSelected.sort();
    const formatted = currentSelected.join(", ");
    input.value = formatted;
    if (task) {
        task.last_answer = formatted;
    }
    renderActiveTask();
}

function appendSign(sign) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;
    const input = document.getElementById("answer-input");
    input.value += sign;
    if (task) {
        task.last_answer = input.value;
    }
}

function setupPrimeFactorizationState(task) {
    let numbers = [];

    // 1. Check known specific task orders in math-6-gcd-lcm
    if (currentRoomCode === "math-6-gcd-lcm" || (task.question && (task.question.includes("НСД") || task.question.includes("НСК")))) {
        if (task.task_order === 11 || (task.question.includes("72") && task.question.includes("96"))) {
            numbers = [72, 96];
        } else if (task.task_order === 12 || (task.question.includes("36") && task.question.includes("54") && task.question.includes("72"))) {
            numbers = [36, 54, 72];
        } else if (task.task_order === 13 || (task.question.includes("28") && task.question.includes("42"))) {
            numbers = [28, 42];
        } else if (task.task_order === 14 || (task.question.includes("12") && task.question.includes("15") && task.question.includes("18"))) {
            numbers = [12, 15, 18];
        }
    }

    // 2. Parse from task.options if not already determined
    if (numbers.length === 0 && task.options) {
        try {
            const opts = typeof task.options === "string" ? JSON.parse(task.options) : task.options;
            if (opts && typeof opts === "object") {
                if (Array.isArray(opts.numbers) && opts.numbers.length > 0) {
                    numbers = opts.numbers.map(n => parseInt(n, 10)).filter(n => !isNaN(n) && n > 1);
                } else if (opts.start_number || opts.number) {
                    numbers = [parseInt(opts.start_number || opts.number, 10)];
                }
            } else if (typeof opts === "number") {
                numbers = [opts];
            }
        } catch (e) {}
    }

    // 3. Fallback extraction from question text (extract all unique numbers in first line)
    if (!numbers || numbers.length === 0) {
        const firstLine = (task.question || "").split("\n")[0];
        const matches = firstLine.match(/\b(\d+)\b/g);
        if (matches && matches.length > 0) {
            const rawNums = matches.map(n => parseInt(n, 10)).filter(n => !isNaN(n) && n > 1);
            numbers = [...new Set(rawNums)];
        }
    }

    if (!numbers || numbers.length === 0) {
        numbers = [504];
    }

    if (currentFactorizationState.taskId !== task.id) {
        currentFactorizationState.taskId = task.id;
        currentFactorizationState.numbers = numbers;
        currentFactorizationState.activeNumberIndex = 0;
        currentFactorizationState.factorMap = {};
        numbers.forEach(num => {
            currentFactorizationState.factorMap[num] = [];
        });

        // For single number tasks, if task has prior answer, load it
        if (numbers.length === 1 && task.last_answer && !task.last_answer.includes("множник") && !task.last_answer.includes("помилка") && !task.last_answer.includes("Невірний")) {
            const parsed = task.last_answer.split(/[\s,·*xX×]+/).map(n => parseInt(n, 10)).filter(n => !isNaN(n) && n > 1);
            currentFactorizationState.factorMap[numbers[0]] = parsed;
        }
    }

    renderPrimeFactorLadder();
    updateFactorProductPreview();
}

function setActiveFactorizationNumber(idx) {
    if (idx < 0 || idx >= currentFactorizationState.numbers.length) return;
    currentFactorizationState.activeNumberIndex = idx;
    renderPrimeFactorLadder();
}

function updateFactorProductPreview() {
    const previewEls = document.querySelectorAll(".factor-product-preview-target, #factor-product-preview");
    if (!previewEls || previewEls.length === 0) return;

    const task = tasksList[currentTaskIndex];
    const isPrimeFactor = task && (task.task_type === "prime_factorization" || currentRoomCode === "math-6-prime-factorization");
    const input = document.getElementById("answer-input");
    const val = input ? input.value.trim() : "";

    if (!isPrimeFactor || !val) {
        previewEls.forEach(el => {
            el.classList.add("hidden");
            el.innerHTML = "";
        });
        return;
    }

    const nums = val.split(/[\s,·*xX×]+/).map(s => parseInt(s, 10)).filter(n => !isNaN(n) && n > 0);
    if (nums.length >= 1) {
        let product = 1;
        nums.forEach(n => { product *= n; });
        const expression = nums.join(" · ");
        previewEls.forEach(el => {
            el.innerHTML = `<span class="opacity-80">Результат множення:</span> <strong class="font-mono text-indigo-950 font-black ml-1">${expression} = ${product}</strong>`;
            el.classList.remove("hidden");
        });
    } else {
        previewEls.forEach(el => {
            el.classList.add("hidden");
            el.innerHTML = "";
        });
    }
}

function renderPrimeFactorLadder() {
    const container = document.getElementById("factorization-ladders-container");
    const tabsContainer = document.getElementById("factorization-number-tabs");
    const summaryEl = document.getElementById("factorization-summary");
    if (!container) return;
    container.innerHTML = "";

    const numbers = currentFactorizationState.numbers || [504];
    const activeIdx = currentFactorizationState.activeNumberIndex || 0;
    const factorMap = currentFactorizationState.factorMap || {};

    // Render tabs if multiple numbers
    if (tabsContainer) {
        if (numbers.length > 1) {
            tabsContainer.classList.remove("hidden");
            tabsContainer.innerHTML = "";
            numbers.forEach((num, idx) => {
                const factors = factorMap[num] || [];
                let cur = num;
                factors.forEach(f => { cur = Math.floor(cur / f); });
                const isDone = (cur === 1);
                const isActive = (idx === activeIdx);

                const tabBtn = document.createElement("button");
                tabBtn.type = "button";
                tabBtn.onclick = () => setActiveFactorizationNumber(idx);
                tabBtn.className = `px-3.5 py-1.5 rounded-xl font-bold text-xs sm:text-sm transition flex items-center gap-1.5 ${
                    isActive 
                        ? 'bg-brand-600 text-white shadow-md ring-2 ring-brand-400 ring-offset-1' 
                        : (isDone ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-slate-200 text-slate-700 hover:bg-slate-300')
                }`;
                tabBtn.innerHTML = `<span>Число ${num}</span> ${isDone ? '<i class="fa-solid fa-check text-xs"></i>' : ''}`;
                tabsContainer.appendChild(tabBtn);
            });
        } else {
            tabsContainer.classList.add("hidden");
        }
    }

    // Render ladders
    numbers.forEach((num, idx) => {
        const factors = factorMap[num] || [];
        const isActive = (idx === activeIdx);
        let cur = num;

        const card = document.createElement("div");
        card.className = `bg-white rounded-2xl p-3 sm:p-4 border transition-all min-w-[140px] sm:min-w-[170px] max-w-xs font-mono font-bold text-base sm:text-lg flex-1 ${
            isActive && numbers.length > 1
                ? 'border-brand-500 ring-2 ring-brand-500/30 bg-brand-50/10 shadow-md' 
                : 'border-slate-200 shadow-sm'
        } ${numbers.length > 1 ? 'cursor-pointer' : ''}`;
        
        if (numbers.length > 1) {
            card.onclick = (e) => {
                if (!e.target.closest("button")) {
                    setActiveFactorizationNumber(idx);
                }
            };
        }

        let headerHtml = "";
        if (numbers.length > 1) {
            headerHtml = `
                <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-xs font-sans font-bold text-slate-500">
                    <span>Число <strong class="text-slate-800">${num}</strong></span>
                    ${isActive ? '<span class="text-brand-600 bg-brand-50 px-2 py-0.5 rounded-lg border border-brand-200">Активне</span>' : '<span class="text-slate-400">Обрати</span>'}
                </div>
            `;
        }

        let rowsHtml = "";
        factors.forEach(f => {
            rowsHtml += `
                <div class="flex items-center justify-between py-1 px-1 sm:px-2">
                    <span class="text-slate-900 w-16 sm:w-20 text-right pr-2 sm:pr-3 font-mono">${cur}</span>
                    <span class="text-slate-300 font-normal">|</span>
                    <span class="text-indigo-600 w-12 sm:w-16 text-left pl-2 sm:pl-3 font-mono font-black">${f}</span>
                </div>
            `;
            cur = Math.floor(cur / f);
        });

        if (cur === 1) {
            rowsHtml += `
                <div class="flex items-center justify-between py-1 px-1 sm:px-2">
                    <span class="text-emerald-600 font-black w-16 sm:w-20 text-right pr-2 sm:pr-3 font-mono">1</span>
                    <span class="text-slate-300 font-normal">|</span>
                    <span class="text-emerald-600 text-[11px] sm:text-xs w-12 sm:w-16 text-left pl-2 sm:pl-3 font-sans font-bold">Готово ✅</span>
                </div>
            `;
        } else {
            rowsHtml += `
                <div class="flex items-center justify-between py-1 px-1 sm:px-2">
                    <span class="text-slate-900 w-16 sm:w-20 text-right pr-2 sm:pr-3 font-mono">${cur}</span>
                    <span class="text-slate-300 font-normal">|</span>
                    <span class="text-slate-300 w-12 sm:w-16 text-left pl-2 sm:pl-3 font-mono">?</span>
                </div>
            `;
        }

        card.innerHTML = `${headerHtml}<div class="space-y-1 divide-y divide-slate-100">${rowsHtml}</div>`;
        container.appendChild(card);
    });

    // Summary of factorized numbers
    if (summaryEl) {
        const completed = numbers.filter(n => {
            const factors = factorMap[n] || [];
            let cur = n;
            factors.forEach(f => { cur = Math.floor(cur / f); });
            return cur === 1;
        });

        if (completed.length > 0 && numbers.length > 1) {
            summaryEl.classList.remove("hidden");
            summaryEl.innerHTML = completed.map(n => {
                const facs = factorMap[n] || [];
                return `<div>${n} = ${facs.join(" · ")}</div>`;
            }).join("");
        } else {
            summaryEl.classList.add("hidden");
            summaryEl.innerHTML = "";
        }
    }

    // Auto-update answer input only for single number factorization topic
    const input = document.getElementById("answer-input");
    if (input && numbers.length === 1) {
        const singleFactors = factorMap[numbers[0]] || [];
        input.value = singleFactors.join(", ");
        const task = tasksList[currentTaskIndex];
        if (task && singleFactors.length > 0) task.last_answer = input.value;
    }
    updateFactorProductPreview();
}

async function addPrimeFactor(prime) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const numbers = currentFactorizationState.numbers || [504];
    let activeIdx = currentFactorizationState.activeNumberIndex || 0;
    let activeNum = numbers[activeIdx] || numbers[0];
    let factors = currentFactorizationState.factorMap[activeNum] || [];

    let cur = activeNum;
    factors.forEach(f => {
        cur = Math.floor(cur / f);
    });

    // If active number is already finished, try to find next unfinished number
    if (cur <= 1) {
        const nextUnfinishedIdx = numbers.findIndex((n, i) => {
            const facs = currentFactorizationState.factorMap[n] || [];
            let c = n;
            facs.forEach(f => { c = Math.floor(c / f); });
            return c > 1;
        });
        if (nextUnfinishedIdx !== -1) {
            currentFactorizationState.activeNumberIndex = nextUnfinishedIdx;
            activeIdx = nextUnfinishedIdx;
            activeNum = numbers[activeIdx];
            factors = currentFactorizationState.factorMap[activeNum] || [];
            cur = activeNum;
            factors.forEach(f => { cur = Math.floor(cur / f); });
        } else {
            return;
        }
    }

    if (cur % prime !== 0) {
        const errorMsg = `Число ${cur} не ділиться націло на ${prime}. Спробуйте інший дільник!`;
        showFeedback(false, errorMsg, null);
        const errDetail = `Невірний множник: ${prime} для числа ${cur} (не ділиться націло)`;
        await reportFactorError(task, prime, cur, errDetail, errorMsg);
        return;
    }

    // Check prime ordering (from smallest prime factor to largest)
    const primeCheckList = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47];
    const smallerPrime = primeCheckList.find(p => p < prime && (cur % p === 0));
    if (smallerPrime) {
        const errorMsg = `Число ${cur} ще ділиться на менший простий множник (${smallerPrime}). Дотримуйтесь порядку від меншого до більшого!`;
        showFeedback(false, errorMsg, `Спробуйте спочатку ${smallerPrime}`);
        const errDetail = `Невірний порядок: обрано множник ${prime} для числа ${cur} (найменший дільник: ${smallerPrime})`;
        await reportFactorError(task, prime, cur, errDetail, errorMsg);
        return;
    }

    factors.push(prime);
    currentFactorizationState.factorMap[activeNum] = factors;

    const feedbackBox = document.getElementById("feedback-box");
    if (feedbackBox) feedbackBox.classList.add("hidden");

    let newCur = cur / prime;
    if (newCur === 1) {
        // Number is finished!
        const nextUnfinishedIdx = numbers.findIndex((n, i) => {
            const facs = currentFactorizationState.factorMap[n] || [];
            let c = n;
            facs.forEach(f => { c = Math.floor(c / f); });
            return c > 1;
        });
        if (nextUnfinishedIdx !== -1) {
            currentFactorizationState.activeNumberIndex = nextUnfinishedIdx;
            showFeedback(true, `Число ${activeNum} успішно розкладено! Перейдіть до розкладання числа ${numbers[nextUnfinishedIdx]}.`, null);
        } else {
            if (numbers.length > 1) {
                showFeedback(true, `Усі числа успішно розкладено на прості множники! Запишіть у поле відповіді шуканий результат.`, null);
            } else {
                showFeedback(true, `Усі прості множники внесено! Натисніть кнопку 'Відповісти' для збереження результату.`, null);
            }
        }
    }

    renderPrimeFactorLadder();
}

async function reportFactorError(task, prime, cur, errDetail, uiMessage) {
    if (!task || !currentUser) return;
    
    try {
        const resp = await fetch("/api/tasks/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                task_id: task.id,
                submitted_answer: errDetail,
                room_code: currentRoomCode
            })
        });
        if (resp.ok) {
            const data = await resp.json();
            task.attempts_count = data.attempt_number;
            task.last_answer = errDetail;
            task.last_is_correct = false;
            
            const attemptsIndicator = document.getElementById("task-attempts-indicator");
            if (attemptsIndicator) {
                attemptsIndicator.textContent = `Спроб: ${task.attempts_count}`;
            }
            const statusBadge = document.getElementById("task-status-badge");
            if (statusBadge) {
                statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200";
                statusBadge.textContent = "❌ Невірний множник";
            }
            renderTaskNavPills();
        }
    } catch (err) {
        console.error("Failed to report factor error:", err);
    }
}

function undoPrimeFactor() {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const numbers = currentFactorizationState.numbers || [504];
    let activeIdx = currentFactorizationState.activeNumberIndex || 0;
    let activeNum = numbers[activeIdx] || numbers[0];
    let factors = currentFactorizationState.factorMap[activeNum] || [];

    if (factors.length > 0) {
        factors.pop();
        currentFactorizationState.factorMap[activeNum] = factors;
    } else if (activeIdx > 0) {
        // Switch to previous number and pop its factor
        currentFactorizationState.activeNumberIndex = activeIdx - 1;
        activeNum = numbers[currentFactorizationState.activeNumberIndex];
        factors = currentFactorizationState.factorMap[activeNum] || [];
        if (factors.length > 0) {
            factors.pop();
            currentFactorizationState.factorMap[activeNum] = factors;
        }
    }
    renderPrimeFactorLadder();
}

// NUMBER LINE & COORDINATE PLANE WIDGET STATES
let currentNumberLineState = {
    mode: "point",
    selectedCoord: null,
    targetPoint: "A",
    pointsToDisplay: [],
    minX: -8,
    maxX: 8
};

let currentCoordinatePlaneState = {
    targetVertices: [
        { name: "A", x: -3, y: -2 },
        { name: "B", x: 3, y: -2 },
        { name: "C", x: 3, y: 2 },
        { name: "D", x: -3, y: 2 }
    ],
    points: [],
    perimeter: "",
    area: ""
};

function setupNumberLineWidget(task, mode) {
    currentNumberLineState.mode = mode;
    currentNumberLineState.minX = -8;
    currentNumberLineState.maxX = 8;
    currentNumberLineState.pointsToDisplay = [];

    let opts = null;
    if (task.options) {
        try {
            opts = typeof task.options === "string" ? JSON.parse(task.options) : task.options;
        } catch (e) {
            opts = null;
        }
    }
    opts = opts || {};

    const badgeEl = document.getElementById("number-line-badge");
    const instrEl = document.getElementById("number-line-instruction");
    const selBar = document.getElementById("number-line-selection-bar");
    const selVal = document.getElementById("number-line-selected-val");

    if (mode === "point") {
        if (badgeEl) badgeEl.textContent = "Позначення точки на прямій";
        if (instrEl) instrEl.textContent = "Натисніть на координатній прямій точку або поділку, щоб позначити координату:";
        if (selBar) selBar.classList.remove("hidden");
        currentNumberLineState.targetPoint = opts.target_point || "A";
        const val = (task.last_answer !== undefined && task.last_answer !== null && task.last_answer !== "") ? parseInt(task.last_answer, 10) : null;
        currentNumberLineState.selectedCoord = Number.isInteger(val) ? val : null;
        if (selVal) {
            selVal.textContent = currentNumberLineState.selectedCoord !== null ? `Точка ${currentNumberLineState.targetPoint}(${currentNumberLineState.selectedCoord})` : "не обрано";
        }
    } else if (mode === "read") {
        if (badgeEl) badgeEl.textContent = "Визначення координати точки";
        if (instrEl) instrEl.textContent = "Визначте координату позначеної точки на прямій та запишіть її значення в поле нижче:";
        if (selBar) selBar.classList.add("hidden");
        const ptName = opts.point_name || "K";
        const ptCoord = (opts.point_coord !== undefined) ? opts.point_coord : -5;
        currentNumberLineState.pointsToDisplay = [{ name: ptName, coord: ptCoord, color: "#e11d48" }];
        currentNumberLineState.selectedCoord = null;
    } else if (mode === "midpoint") {
        if (badgeEl) badgeEl.textContent = "Середина відрізка на прямій";
        if (instrEl) instrEl.textContent = "Знайдіть координату середини відрізка AB на прямій та введіть її значення в поле нижче:";
        if (selBar) selBar.classList.add("hidden");
        const ptA = opts.pointA || { name: "A", coord: -7 };
        const ptB = opts.pointB || { name: "B", coord: 3 };
        currentNumberLineState.pointsToDisplay = [
            { name: ptA.name, coord: ptA.coord, color: "#4f46e5" },
            { name: ptB.name, coord: ptB.coord, color: "#4f46e5" }
        ];
        currentNumberLineState.selectedCoord = null;
    }

    renderNumberLineSvg();
}

function renderNumberLineSvg() {
    const wrapper = document.getElementById("number-line-svg-wrapper");
    if (!wrapper) return;

    const minX = currentNumberLineState.minX || -8;
    const maxX = currentNumberLineState.maxX || 8;
    const mode = currentNumberLineState.mode;
    const selCoord = currentNumberLineState.selectedCoord;
    const pts = currentNumberLineState.pointsToDisplay || [];

    const totalWidth = 620;
    const totalHeight = 100;
    const xMargin = 45;
    const width = totalWidth - 2 * xMargin;
    const yBase = 52;
    const dx = width / (maxX - minX);

    function xToPx(x) {
        return xMargin + (x - minX) * dx;
    }

    let svgHtml = `<svg viewBox="0 0 ${totalWidth} ${totalHeight}" class="w-full h-auto select-none overflow-visible" style="max-width: ${totalWidth}px;">`;

    // Midpoint segment line if midpoint mode
    if (mode === "midpoint" && pts.length >= 2) {
        const x1 = xToPx(pts[0].coord);
        const x2 = xToPx(pts[1].coord);
        const segMin = Math.min(x1, x2);
        const segMax = Math.max(x1, x2);
        svgHtml += `
            <line x1="${segMin}" y1="${yBase - 18}" x2="${segMax}" y2="${yBase - 18}" stroke="#6366f1" stroke-width="3.5" stroke-linecap="round" />
            <line x1="${segMin}" y1="${yBase - 24}" x2="${segMin}" y2="${yBase - 12}" stroke="#6366f1" stroke-width="2.5" />
            <line x1="${segMax}" y1="${yBase - 24}" x2="${segMax}" y2="${yBase - 12}" stroke="#6366f1" stroke-width="2.5" />
            <rect x="${(segMin + segMax)/2 - 42}" y="${yBase - 36}" width="84" height="18" rx="5" fill="#eef2ff" stroke="#c7d2fe" />
            <text x="${(segMin + segMax)/2}" y="${yBase - 23}" text-anchor="middle" font-size="11" font-weight="bold" fill="#4338ca">Відрізок AB</text>
        `;
    }

    // Main axis line
    svgHtml += `
        <line x1="${xMargin - 20}" y1="${yBase}" x2="${totalWidth - xMargin + 25}" y2="${yBase}" stroke="#1e293b" stroke-width="2.5" />
        <polygon points="${totalWidth - xMargin + 25},${yBase} ${totalWidth - xMargin + 14},${yBase - 5} ${totalWidth - xMargin + 14},${yBase + 5}" fill="#1e293b" />
        <text x="${totalWidth - xMargin + 32}" y="${yBase + 5}" font-size="14" font-weight="bold" fill="#0f172a" font-family="sans-serif">x</text>
    `;

    // Draw ticks & labels
    for (let i = minX; i <= maxX; i++) {
        const px = xToPx(i);
        const isZero = (i === 0);
        const tickH = isZero ? 20 : 10;
        const tickColor = isZero ? "#2563eb" : "#64748b";
        const strokeW = isZero ? "2.5" : "1.5";

        svgHtml += `<line x1="${px}" y1="${yBase - tickH/2}" x2="${px}" y2="${yBase + tickH/2}" stroke="${tickColor}" stroke-width="${strokeW}" />`;
        svgHtml += `<text x="${px}" y="${yBase + 24}" text-anchor="middle" font-size="${isZero ? '14' : '11.5'}" font-weight="${isZero ? '900' : 'bold'}" fill="${isZero ? '#1d4ed8' : '#475569'}" font-family="monospace">${i}</text>`;

        if (isZero) {
            svgHtml += `<text x="${px}" y="${yBase - 14}" text-anchor="middle" font-size="11" font-weight="900" fill="#2563eb" font-family="sans-serif">O(0)</text>`;
        }

        // Clickable hotspot if mode === "point"
        if (mode === "point") {
            svgHtml += `
                <circle cx="${px}" cy="${yBase}" r="15" fill="transparent" class="cursor-pointer" onclick="handleNumberLineClick(${i})" style="cursor:pointer;" />
            `;
        }
    }

    // Selected active point for point mode
    if (mode === "point" && selCoord !== null) {
        const px = xToPx(selCoord);
        const ptLabel = currentNumberLineState.targetPoint || "A";
        svgHtml += `
            <circle cx="${px}" cy="${yBase}" r="14" fill="#3b82f6" fill-opacity="0.3" class="animate-pulse" />
            <circle cx="${px}" cy="${yBase}" r="6.5" fill="#2563eb" stroke="#ffffff" stroke-width="2.5" />
            <rect x="${px - 22}" y="${yBase - 36}" width="44" height="20" rx="6" fill="#1d4ed8" />
            <text x="${px}" y="${yBase - 22}" text-anchor="middle" font-size="11.5" font-weight="900" fill="#ffffff" font-family="sans-serif">${ptLabel}(${selCoord})</text>
        `;
    }

    // Read / Midpoint displayed points
    pts.forEach(pt => {
        const px = xToPx(pt.coord);
        const col = pt.color || "#4f46e5";
        svgHtml += `
            <line x1="${px}" y1="${yBase - 26}" x2="${px}" y2="${yBase}" stroke="${col}" stroke-width="2" stroke-dasharray="3,2" />
            <circle cx="${px}" cy="${yBase}" r="7" fill="${col}" stroke="#ffffff" stroke-width="2.5" />
            <rect x="${px - 15}" y="${yBase - 40}" width="30" height="20" rx="6" fill="${col}" />
            <text x="${px}" y="${yBase - 26}" text-anchor="middle" font-size="12" font-weight="900" fill="#ffffff" font-family="sans-serif">${pt.name}</text>
        `;
    });

    svgHtml += `</svg>`;
    wrapper.innerHTML = svgHtml;
}

function handleNumberLineClick(coord) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    currentNumberLineState.selectedCoord = coord;
    const input = document.getElementById("answer-input");
    if (input) {
        input.value = String(coord);
    }
    if (task) {
        task.last_answer = String(coord);
    }
    const selVal = document.getElementById("number-line-selected-val");
    if (selVal) {
        selVal.textContent = `Точка ${currentNumberLineState.targetPoint}(${coord})`;
    }
    renderNumberLineSvg();
}

function setupCoordinatePlaneWidget(task) {
    let opts = null;
    if (task.options) {
        try {
            opts = typeof task.options === "string" ? JSON.parse(task.options) : task.options;
        } catch (e) {
            opts = null;
        }
    }
    opts = opts || {};

    currentCoordinatePlaneState.targetVertices = opts.vertices || [
        { name: "A", x: -3, y: -2 },
        { name: "B", x: 3, y: -2 },
        { name: "C", x: 3, y: 2 },
        { name: "D", x: -3, y: 2 }
    ];

    currentCoordinatePlaneState.points = [];
    currentCoordinatePlaneState.perimeter = "";
    currentCoordinatePlaneState.area = "";

    const pInput = document.getElementById("rect-perimeter-input");
    const sInput = document.getElementById("rect-area-input");

    // Restore answers if available
    const rawAns = task.last_answer || "";
    if (rawAns) {
        const pMatch = rawAns.match(/P[=:\s]*(\d+)/i) || rawAns.match(/^(\d+)[\s,;]+(\d+)/);
        const sMatch = rawAns.match(/S[=:\s]*(\d+)/i);
        if (pMatch && sMatch) {
            if (pInput) pInput.value = pMatch[1];
            if (sInput) sInput.value = sMatch[1];
        } else if (pMatch && pMatch[2]) {
            if (pInput) pInput.value = pMatch[1];
            if (sInput) sInput.value = pMatch[2];
        }
    } else {
        if (pInput) pInput.value = "";
        if (sInput) sInput.value = "";
    }

    renderCoordinatePlaneSvg();
}

function renderCoordinatePlaneSvg() {
    const wrapper = document.getElementById("coordinate-plane-svg-wrapper");
    if (!wrapper) return;

    const totalWidth = 440;
    const totalHeight = 380;
    const cx = 220;
    const cy = 190;
    const step = 28;
    const minX = -6, maxX = 6, minY = -5, maxY = 5;

    function toSvgX(gx) { return cx + gx * step; }
    function toSvgY(gy) { return cy - gy * step; }

    let svgHtml = `<svg id="coord-plane-svg" viewBox="0 0 ${totalWidth} ${totalHeight}" class="w-full h-auto select-none" style="max-width: 440px; cursor: crosshair;" onclick="handleCoordinatePlaneClick(event)">`;

    // Background Grid lines
    for (let x = minX; x <= maxX; x++) {
        const px = toSvgX(x);
        svgHtml += `<line x1="${px}" y1="${toSvgY(maxY)}" x2="${px}" y2="${toSvgY(minY)}" stroke="#e2e8f0" stroke-width="1" />`;
    }
    for (let y = minY; y <= maxY; y++) {
        const py = toSvgY(y);
        svgHtml += `<line x1="${toSvgX(minX)}" y1="${py}" x2="${toSvgX(maxX)}" y2="${py}" stroke="#e2e8f0" stroke-width="1" />`;
    }

    // Axes
    svgHtml += `
        <!-- X Axis -->
        <line x1="20" y1="${cy}" x2="${totalWidth - 15}" y2="${cy}" stroke="#334155" stroke-width="2.5" />
        <polygon points="${totalWidth - 15},${cy} ${totalWidth - 25},${cy - 5} ${totalWidth - 25},${cy + 5}" fill="#334155" />
        <text x="${totalWidth - 12}" y="${cy + 4}" font-size="13" font-weight="900" fill="#0f172a" font-family="sans-serif">x</text>

        <!-- Y Axis -->
        <line x1="${cx}" y1="${totalHeight - 20}" x2="${cx}" y2="15" stroke="#334155" stroke-width="2.5" />
        <polygon points="${cx},15 ${cx - 5},25 ${cx + 5},25" fill="#334155" />
        <text x="${cx + 8}" y="18" font-size="13" font-weight="900" fill="#0f172a" font-family="sans-serif">y</text>
    `;

    // X Axis Ticks and Labels
    for (let x = minX; x <= maxX; x++) {
        if (x === 0) continue;
        const px = toSvgX(x);
        svgHtml += `<line x1="${px}" y1="${cy - 4}" x2="${px}" y2="${cy + 4}" stroke="#64748b" stroke-width="1.5" />`;
        svgHtml += `<text x="${px}" y="${cy + 16}" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#64748b" font-family="monospace">${x}</text>`;
    }

    // Y Axis Ticks and Labels
    for (let y = minY; y <= maxY; y++) {
        if (y === 0) continue;
        const py = toSvgY(y);
        svgHtml += `<line x1="${cx - 4}" y1="${py}" x2="${cx + 4}" stroke="#64748b" stroke-width="1.5" />`;
        svgHtml += `<text x="${cx - 9}" y="${py + 3.5}" text-anchor="end" font-size="10.5" font-weight="bold" fill="#64748b" font-family="monospace">${y}</text>`;
    }

    // Origin 0
    svgHtml += `<text x="${cx - 7}" y="${cy + 14}" text-anchor="end" font-size="11" font-weight="bold" fill="#64748b" font-family="monospace">0</text>`;

    // If 4 points placed, draw polygon connecting them
    const pts = currentCoordinatePlaneState.points || [];
    if (pts.length === 4) {
        // Sort points geometrically in clockwise order around centroid
        const avgX = pts.reduce((acc, p) => acc + p.x, 0) / 4;
        const avgY = pts.reduce((acc, p) => acc + p.y, 0) / 4;
        const sorted = pts.slice().sort((a, b) => Math.atan2(a.y - avgY, a.x - avgX) - Math.atan2(b.y - avgY, b.x - avgX));
        const polyPoints = sorted.map(p => `${toSvgX(p.x)},${toSvgY(p.y)}`).join(" ");

        svgHtml += `
            <polygon points="${polyPoints}" fill="rgba(16, 185, 129, 0.25)" stroke="#059669" stroke-width="3" stroke-linejoin="round" />
        `;
    }

    // Draw points
    pts.forEach(p => {
        const px = toSvgX(p.x);
        const py = toSvgY(p.y);
        svgHtml += `
            <circle cx="${px}" cy="${py}" r="11" fill="#10b981" fill-opacity="0.3" class="animate-pulse" />
            <circle cx="${px}" cy="${py}" r="6.5" fill="#059669" stroke="#ffffff" stroke-width="2.5" />
            <rect x="${px + 8}" y="${py - 20}" width="54" height="18" rx="4" fill="#047857" />
            <text x="${px + 35}" y="${py - 7}" text-anchor="middle" font-size="10.5" font-weight="900" fill="#ffffff" font-family="sans-serif">${p.name}(${p.x},${p.y})</text>
        `;
    });

    svgHtml += `</svg>`;
    wrapper.innerHTML = svgHtml;

    // Update target badges
    const targetVerts = currentCoordinatePlaneState.targetVertices || [];
    ["A", "B", "C", "D"].forEach(name => {
        const badge = document.getElementById(`vtx-badge-${name}`);
        const target = targetVerts.find(v => v.name === name);
        if (!badge || !target) return;

        const isPlaced = pts.some(p => p.x === target.x && p.y === target.y);
        if (isPlaced) {
            badge.className = "px-2.5 py-1 rounded-xl bg-emerald-100 border border-emerald-300 text-xs font-bold text-emerald-800 flex items-center gap-1.5";
            badge.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-600"></i> ${target.name}(${target.x}, ${target.y})`;
        } else {
            badge.className = "px-2.5 py-1 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 flex items-center gap-1.5";
            badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-300"></span> ${target.name}(${target.x}, ${target.y})`;
        }
    });
}

function handleCoordinatePlaneClick(e) {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    const svg = document.getElementById("coord-plane-svg");
    if (!svg) return;

    const rect = svg.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;

    const totalWidth = 440;
    const totalHeight = 380;
    const scaleX = totalWidth / rect.width;
    const scaleY = totalHeight / rect.height;

    const svgX = px * scaleX;
    const svgY = py * scaleY;
    const cx = 220;
    const cy = 190;
    const step = 28;

    const gx = Math.round((svgX - cx) / step);
    const gy = Math.round((cy - svgY) / step);

    if (gx < -6 || gx > 6 || gy < -5 || gy > 5) return;

    const existingIndex = currentCoordinatePlaneState.points.findIndex(p => p.x === gx && p.y === gy);
    if (existingIndex >= 0) {
        currentCoordinatePlaneState.points.splice(existingIndex, 1);
    } else {
        if (currentCoordinatePlaneState.points.length < 4) {
            const names = ["A", "B", "C", "D"];
            const used = currentCoordinatePlaneState.points.map(p => p.name);
            const nextName = names.find(n => !used.includes(n)) || "P";
            currentCoordinatePlaneState.points.push({ x: gx, y: gy, name: nextName });
        }
    }

    renderCoordinatePlaneSvg();
    updateRectangleInputs();
}

function resetCoordinatePlanePoints() {
    const task = tasksList[currentTaskIndex];
    if (task && task.is_solved) return;

    currentCoordinatePlaneState.points = [];
    renderCoordinatePlaneSvg();
    updateRectangleInputs();
}

function updateRectangleInputs() {
    const pInput = document.getElementById("rect-perimeter-input");
    const sInput = document.getElementById("rect-area-input");
    const mainInput = document.getElementById("answer-input");
    const task = tasksList[currentTaskIndex];

    const pVal = pInput ? pInput.value.trim() : "";
    const sVal = sInput ? sInput.value.trim() : "";

    if (pVal && sVal) {
        mainInput.value = `P=${pVal}, S=${sVal}`;
        if (task) task.last_answer = mainInput.value;
    } else if (pVal) {
        mainInput.value = `P=${pVal}`;
        if (task) task.last_answer = mainInput.value;
    } else if (sVal) {
        mainInput.value = `S=${sVal}`;
        if (task) task.last_answer = mainInput.value;
    } else {
        mainInput.value = "";
    }
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

    if (task.task_type === "coordinate_plane_rect") {
        if (currentCoordinatePlaneState.points.length < 4) {
            showFeedback(false, "Будь ласка, позначте всі 4 вершини прямокутника на координатній площині!", "Клацніть на площині по черзі по точках A, B, C, D");
            return;
        }
        const pInput = document.getElementById("rect-perimeter-input");
        const sInput = document.getElementById("rect-area-input");
        if (!pInput || !sInput || !pInput.value.trim() || !sInput.value.trim()) {
            showFeedback(false, "Будь ласка, введіть значення для периметра (P) та площі (S)!", "Обчисліть довжини сторін і внесіть P та S");
            return;
        }
        updateRectangleInputs();
    }

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
    updateFactorProductPreview();
}

function keypadBackspace() {
    const input = document.getElementById("answer-input");
    input.value = input.value.slice(0, -1);
    input.focus();
    updateFactorProductPreview();
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
    updateFactorProductPreview();
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
