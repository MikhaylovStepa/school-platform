import json
import random
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Grade, Subject, Topic, Task

def ensure_schema_migrations(db: Session):
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS grade_level INTEGER DEFAULT 6;"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS class_letter VARCHAR(10) DEFAULT 'Б';"))
        db.execute(text("UPDATE users SET grade_level = 6, class_letter = 'Б' WHERE role = 'student';"))
        db.commit()
    except Exception:
        db.rollback()

def generate_validated_examples():
    """
    Generate 20 examples for each topic adhering strictly to:
    - Operands between -20 and 20 (non-zero).
    - If one number is 2-digit (|x| >= 10), the other MUST be 1-digit (|y| < 10). (Or both 1-digit).
    - Combinations: negative & negative, negative & positive / positive & negative, positive & positive.
    """
    def valid_pair(a, b):
        if a == 0 or b == 0:
            return False
        if abs(a) > 20 or abs(b) > 20:
            return False
        if abs(a) >= 10 and abs(b) >= 10:
            return False
        return True

    def format_first(n):
        return f"({n})" if n < 0 else f"{n}"

    def format_second(n):
        return f"({n})" if n < 0 else f"{n}"

    # Addition examples generator
    def get_addition_tasks(seed_val=42):
        neg_neg = []
        for a in range(-20, 0):
            for b in range(-20, 0):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} + {format_second(b)} = ?"
                    ans = a + b
                    hint = "При додаванні двох від'ємних чисел: додаємо їхні модулі та перед результатом ставимо знак мінус (-)."
                    neg_neg.append((q, str(ans), hint))

        neg_pos = []
        for a in range(-20, 21):
            for b in range(-20, 21):
                if valid_pair(a, b) and ((a < 0 and b > 0) or (a > 0 and b < 0)):
                    q = f"Обчисліть: {format_first(a)} + {format_second(b)} = ?"
                    ans = a + b
                    hint = "При додаванні чисел з різними знаками: від більшого модуля віднімаємо менший і ставимо знак числа з більшим модулем."
                    neg_pos.append((q, str(ans), hint))

        pos_pos = []
        for a in range(1, 21):
            for b in range(1, 21):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} + {format_second(b)} = ?"
                    ans = a + b
                    hint = "При додаванні двох додатних чисел отримуємо додатне число."
                    pos_pos.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_neg)
        r.shuffle(neg_pos)
        r.shuffle(pos_pos)

        # 6 neg-neg, 8 neg-pos, 6 pos-pos = 20 total
        selected = neg_neg[:6] + neg_pos[:8] + pos_pos[:6]
        r.shuffle(selected)
        return selected

    # Subtraction examples generator
    def get_subtraction_tasks(seed_val=101):
        neg_neg = []
        for a in range(-20, 0):
            for b in range(-20, 0):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} - {format_second(b)} = ?"
                    ans = a - b
                    hint = "Віднімання можна замінити додаванням протилежного числа: a - (-b) = a + b."
                    neg_neg.append((q, str(ans), hint))

        neg_pos = []
        for a in range(-20, 21):
            for b in range(-20, 21):
                if valid_pair(a, b) and ((a < 0 and b > 0) or (a > 0 and b < 0)):
                    q = f"Обчисліть: {format_first(a)} - {format_second(b)} = ?"
                    ans = a - b
                    hint = "Пам'ятай: a - b = a + (-b), а також a - (-b) = a + b."
                    neg_pos.append((q, str(ans), hint))

        pos_pos = []
        for a in range(1, 21):
            for b in range(1, 21):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} - {format_second(b)} = ?"
                    ans = a - b
                    hint = "Якщо зменшуване менше за від'ємник, у результаті отримаємо від'ємне число."
                    pos_pos.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_neg)
        r.shuffle(neg_pos)
        r.shuffle(pos_pos)

        # 6 neg-neg, 8 neg-pos, 6 pos-pos = 20 total
        selected = neg_neg[:6] + neg_pos[:8] + pos_pos[:6]
        r.shuffle(selected)
        return selected

    # Mixed addition and subtraction
    def get_mixed_tasks(seed_val=303):
        add_pool = get_addition_tasks(seed_val=seed_val)
        sub_pool = get_subtraction_tasks(seed_val=seed_val + 50)
        r = random.Random(seed_val)
        r.shuffle(add_pool)
        r.shuffle(sub_pool)
        selected = add_pool[:10] + sub_pool[:10]
        r.shuffle(selected)
        return selected

    # Multiplication examples generator
    def get_multiplication_tasks(seed_val=404):
        neg_neg = []
        for a in range(-20, 0):
            for b in range(-20, 0):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} · {format_second(b)} = ?"
                    ans = a * b
                    hint = "Добуток двох від'ємних чисел є додатним числом: (-a) · (-b) = a · b."
                    neg_neg.append((q, str(ans), hint))

        neg_pos = []
        for a in range(-20, 21):
            for b in range(-20, 21):
                if valid_pair(a, b) and ((a < 0 and b > 0) or (a > 0 and b < 0)):
                    q = f"Обчисліть: {format_first(a)} · {format_second(b)} = ?"
                    ans = a * b
                    hint = "Добуток чисел з різними знаками є від'ємним числом: (-a) · b = -(a · b)."
                    neg_pos.append((q, str(ans), hint))

        pos_pos = []
        for a in range(1, 21):
            for b in range(1, 21):
                if valid_pair(a, b):
                    q = f"Обчисліть: {format_first(a)} · {format_second(b)} = ?"
                    ans = a * b
                    hint = "Добуток двох додатних чисел є додатним числом: a · b = c."
                    pos_pos.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_neg)
        r.shuffle(neg_pos)
        r.shuffle(pos_pos)

        selected = neg_neg[:6] + neg_pos[:8] + pos_pos[:6]
        r.shuffle(selected)
        return selected

    # Division examples generator
    def get_division_tasks(seed_val=505):
        neg_neg = []
        for a in range(-20, 0):
            for b in range(-20, 0):
                if valid_pair(a, b) and a % b == 0:
                    q = f"Обчисліть: {format_first(a)} : {format_second(b)} = ?"
                    ans = a // b
                    hint = "Частка двох від'ємних чисел є додатним числом: (-a) : (-b) = a : b."
                    neg_neg.append((q, str(ans), hint))

        neg_pos = []
        for a in range(-20, 21):
            for b in range(-20, 21):
                if valid_pair(a, b) and ((a < 0 and b > 0) or (a > 0 and b < 0)) and a % b == 0:
                    q = f"Обчисліть: {format_first(a)} : {format_second(b)} = ?"
                    ans = a // b
                    hint = "Частка чисел з різними знаками є від'ємним числом: (-a) : b = -(a : b)."
                    neg_pos.append((q, str(ans), hint))

        pos_pos = []
        for a in range(1, 21):
            for b in range(1, 21):
                if valid_pair(a, b) and a % b == 0:
                    q = f"Обчисліть: {format_first(a)} : {format_second(b)} = ?"
                    ans = a // b
                    hint = "Частка двох додатних чисел є додатним числом: a : b = c."
                    pos_pos.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_neg)
        r.shuffle(neg_pos)
        r.shuffle(pos_pos)

        selected = neg_neg[:6] + neg_pos[:8] + pos_pos[:6]
        r.shuffle(selected)
        return selected

    # Modulus of a number
    def get_modulus_tasks(seed_val=606):
        neg_list = []
        pos_list = []
        for x in range(-20, 21):
            if x == 0:
                continue
            q = f"Обчисліть: |{x}| = ?"
            ans = abs(x)
            hint = "Модуль числа — це відстань від початку відліку до даного числа. Модуль завжди невід'ємний: |-a| = a, |a| = a."
            if x < 0:
                neg_list.append((q, str(ans), hint))
            else:
                pos_list.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_list)
        r.shuffle(pos_list)

        # 10 negative, 10 positive = 20 total
        selected = neg_list[:10] + pos_list[:10]
        r.shuffle(selected)
        return selected

    # Opposite number
    def get_opposite_tasks(seed_val=707):
        neg_list = []
        pos_list = []
        for x in range(-20, 21):
            if x == 0:
                continue
            q = f"Знайдіть число, протилежне до {format_first(x)}"
            ans = -x
            hint = "Два числа, які відрізняються лише знаками, називають протилежними: протилежним до a є -a, а до -a є a."
            if x < 0:
                neg_list.append((q, str(ans), hint))
            else:
                pos_list.append((q, str(ans), hint))

        r = random.Random(seed_val)
        r.shuffle(neg_list)
        r.shuffle(pos_list)

        # 10 negative, 10 positive = 20 total
        selected = neg_list[:10] + pos_list[:10]
        r.shuffle(selected)
        return selected

    return {
        "addition_1": get_addition_tasks(seed_val=42),
        "addition_2": get_addition_tasks(seed_val=43),
        "addition_3": get_addition_tasks(seed_val=44),
        "subtraction_1": get_subtraction_tasks(seed_val=101),
        "subtraction_2": get_subtraction_tasks(seed_val=102),
        "subtraction_3": get_subtraction_tasks(seed_val=103),
        "mixed_1": get_mixed_tasks(seed_val=301),
        "mixed_2": get_mixed_tasks(seed_val=302),
        "mixed_3": get_mixed_tasks(seed_val=303),
        "multiplication_1": get_multiplication_tasks(seed_val=401),
        "multiplication_2": get_multiplication_tasks(seed_val=402),
        "division_1": get_division_tasks(seed_val=501),
        "division_2": get_division_tasks(seed_val=502),
        "modulus_1": get_modulus_tasks(seed_val=601),
        "opposite_1": get_opposite_tasks(seed_val=701)
    }


def seed_database(db: Session):
    ensure_schema_migrations(db)

    # Check if 6th grade exists
    grade6 = db.query(Grade).filter_by(slug="grade-6").first()
    if not grade6:
        grade6 = Grade(
            name="6 Клас",
            slug="grade-6",
            sort_order=1
        )
        db.add(grade6)
        db.commit()
        db.refresh(grade6)

    # Check if 7th grade exists
    grade7 = db.query(Grade).filter_by(slug="grade-7").first()
    if not grade7:
        grade7 = Grade(
            name="7 Клас",
            slug="grade-7",
            sort_order=2
        )
        db.add(grade7)
        db.commit()
        db.refresh(grade7)

    # Check if 8th grade exists
    grade8 = db.query(Grade).filter_by(slug="grade-8").first()
    if not grade8:
        grade8 = Grade(
            name="8 Клас",
            slug="grade-8",
            sort_order=3
        )
        db.add(grade8)
        db.commit()
        db.refresh(grade8)

    # Check if 9th grade exists
    grade9 = db.query(Grade).filter_by(slug="grade-9").first()
    if not grade9:
        grade9 = Grade(
            name="9 Клас",
            slug="grade-9",
            sort_order=4
        )
        db.add(grade9)
        db.commit()
        db.refresh(grade9)

    # Check if Subject exists for 6th grade
    subject = db.query(Subject).filter_by(grade_id=grade6.id, slug="math").first()
    if not subject:
        subject = Subject(
            grade_id=grade6.id,
            name="Математика",
            slug="math",
            icon="calculator",
            sort_order=1
        )
        db.add(subject)
        db.commit()
        db.refresh(subject)

    theory_addition = """### 📖 Теоретичний матеріал: Складання цілих чисел

#### 1. Додавання двох від'ємних чисел:
Щоб додати два від'ємні числа, треба:
1. Додати їхні модулі (абсолютні величини без знака);
2. Перед отриманим результатом поставити знак **мінус (-)**.

> **Формула:** `(-a) + (-b) = -(a + b)`
> **Приклад:** `(-4) + (-5) = -(4 + 5) = -9`
> **Приклад:** `(-14) + (-3) = -(14 + 3) = -17`

---

#### 2. Додавання чисел з різними знаками:
Щоб додати додатне і від'ємне число, треба:
1. Знайти модулі обох чисел;
2. Від більшого модуля відняти менший модуль;
3. Перед отриманим результатом поставити знак числа, модуль якого більший.

> **Приклад 1:** `(-15) + 8 = -(15 - 8) = -7` *(модуль |-15| = 15 більший за |8| = 8, знак мінус)*
> **Приклад 2:** `(-6) + 14 = +(14 - 6) = 8` *(модуль |14| більший за |-6|, знак плюс)*
> **Приклад 3:** `18 + (-5) = 18 - 5 = 13`
> **Приклад 4:** `7 + (-7) = 0` *(сума протилежних чисел завжди дорівнює нулю)*

---

#### 3. Додавання двох додатних чисел:
Це звичайне додавання натуральних чисел:
> **Приклад:** `14 + 5 = 19`
"""

    theory_subtraction = """### 📖 Теоретичний матеріал: Віднімання цілих чисел

#### Основне правило віднімання:
Щоб від одного числа відняти інше, можна до зменшуваного **додати число, протилежне від'ємнику**.

> **Золоте правило:** `a - b = a + (-b)`  
> **Два мінуси дають плюс:** `a - (-b) = a + b`

---

#### Приклади:

1. **Віднімання від'ємного числа:**
   - `8 - (-5) = 8 + 5 = 13`
   - `(-7) - (-4) = (-7) + 4 = -3`
   - `(-12) - (-15) = (-12) + 15 = 3`

2. **Віднімання додатного числа від меншого або від'ємного:**
   - `5 - 12 = 5 + (-12) = -7`
   - `(-6) - 8 = (-6) + (-8) = -14`
   - `(-14) - 5 = -19`

3. **Корисна порада:**
   Завжди перетворюй знак мінус перед дужками ` - (-x) ` на плюс ` + x `!
"""

    theory_mixed = """### 📖 Теоретичний матеріал: Складання і віднімання цілих чисел (Зведений блок)

#### Швидка пам'ятка знаків:

| Дія | Правило | Приклад |
| :--- | :--- | :--- |
| `(-a) + (-b)` | Додай модулі, постав мінус | `(-8) + (-6) = -14` |
| `(-a) + b` | Від більшого модуля відніми менший | `(-15) + 6 = -9` |
| `a + (-b)` | Від більшого модуля відніми менший | `16 + (-7) = 9` |
| `a - (-b)` | Два мінуси = плюс (`a + b`) | `9 - (-4) = 9 + 4 = 13` |
| `(-a) - b` | `(-a) + (-b)` (два мінуси разом) | `(-8) - 5 = -13` |
| `(-a) - (-b)` | `(-a) + b` | `(-14) - (-6) = (-14) + 6 = -8` |

#### Порада для вирішення прикладів:
Уважно дивіться на знаки чисел та операції. Не поспішайте!
"""

    theory_multiplication = """### 📖 Теоретичний матеріал: Множення цілих чисел

#### Правила множення:
1. **Добуток двох чисел з однаковими знаками — число додатне:**
   - `(-a) · (-b) = a · b`
   - `a · b = a · b`
   > **Приклад:** `(-6) · (-7) = 42`, `8 · 5 = 40`

2. **Добуток двох чисел з різними знаками — число від'ємне:**
   - `(-a) · b = -(a · b)`
   - `a · (-b) = -(a · b)`
   > **Приклад:** `(-8) · 4 = -32`, `7 · (-5) = -35`

3. **Множення на нуль:**
   - `a · 0 = 0`
"""

    theory_division = """### 📖 Теоретичний матеріал: Ділення цілих чисел

#### Правила ділення:
1. **Частка двох чисел з однаковими знаками — число додатне:**
   - `(-a) : (-b) = a : b`
   - `a : b = a : b`
   > **Приклад:** `(-18) : (-3) = 6`, `20 : 4 = 5`

2. **Частка двох чисел з різними знаками — число від'ємне:**
   - `(-a) : b = -(a : b)`
   - `a : (-b) = -(a : b)`
   > **Приклад:** `(-16) : 4 = -4`, `15 : (-3) = -5`

3. **Пам'ятай:**
   - На нуль ділити не можна!
"""

    theory_modulus = """### 📖 Теоретичний матеріал: Знаходження модуля числа

#### Що таке модуль числа:
**Модуль числа** — це відстань від початку відліку (точки 0) на координатній прямій до точки, що зображує це число.

#### Властивості модуля:
1. Модуль додатного числа дорівнює самому числу: `|a| = a`
   > **Приклад:** `|12| = 12`, `|7| = 7`
2. Модуль від'ємного числа дорівнює протилежному йому числу: `|-a| = a`
   > **Приклад:** `|-15| = 15`, `|-8| = 8`
3. Модуль нуля дорівнює нулю: `|0| = 0`
4. Модуль **завжди є невід'ємним числом**: `|x| >= 0`
"""

    theory_opposite = """### 📖 Теоретичний матеріал: Знаходження протилежного числа

#### Визначення:
Два числа, які відрізняються одне від одного лише **знаками**, називаються **протилежними числами**.

#### Властивості:
1. Протилежним до числа `a` є число `-a`.
   > **Приклад:** до `14` протилежним є `-14`.
2. Протилежним до від'ємного числа `-a` є додатне число `a`.
   > **Приклад:** до `-9` протилежним є `9` (бо `-(-9) = 9`).
3. Число `0` протилежне самому собі.
4. Сума двох протилежних чисел завжди дорівнює `0`: `a + (-a) = 0`.
"""

    topics_meta = [
        # Addition (3 cabinets)
        {
            "slug": "integers-addition",
            "room_code": "math-6-add",
            "name": "Складання цілих чисел (Кабінет 1)",
            "description": "Базові правила та практика додавання від'ємних і додатних чисел.",
            "sort_order": 1,
            "theory": theory_addition,
            "task_key": "addition_1"
        },
        {
            "slug": "integers-addition-2",
            "room_code": "math-6-add-2",
            "name": "Складання цілих чисел (Кабінет 2)",
            "description": "Тренувальний кабінет 2 з додавання цілих чисел.",
            "sort_order": 2,
            "theory": theory_addition,
            "task_key": "addition_2"
        },
        {
            "slug": "integers-addition-3",
            "room_code": "math-6-add-3",
            "name": "Складання цілих чисел (Кабінет 3)",
            "description": "Тренувальний кабінет 3 з додавання цілих чисел.",
            "sort_order": 3,
            "theory": theory_addition,
            "task_key": "addition_3"
        },

        # Subtraction (3 cabinets)
        {
            "slug": "integers-subtraction",
            "room_code": "math-6-sub",
            "name": "Віднімання цілих чисел (Кабінет 1)",
            "description": "Правила та практика віднімання цілих чисел з різними знаками.",
            "sort_order": 4,
            "theory": theory_subtraction,
            "task_key": "subtraction_1"
        },
        {
            "slug": "integers-subtraction-2",
            "room_code": "math-6-sub-2",
            "name": "Віднімання цілих чисел (Кабінет 2)",
            "description": "Тренувальний кабінет 2 з віднімання цілих чисел.",
            "sort_order": 5,
            "theory": theory_subtraction,
            "task_key": "subtraction_2"
        },
        {
            "slug": "integers-subtraction-3",
            "room_code": "math-6-sub-3",
            "name": "Віднімання цілих чисел (Кабінет 3)",
            "description": "Тренувальний кабінет 3 з віднімання цілих чисел.",
            "sort_order": 6,
            "theory": theory_subtraction,
            "task_key": "subtraction_3"
        },

        # Mixed addition & subtraction (3 cabinets)
        {
            "slug": "integers-addition-subtraction",
            "room_code": "math-6-mixed",
            "name": "Складання і віднімання цілих чисел (Кабінет 1)",
            "description": "Комплексні тренувальні вправи на всі операції додавання і віднімання.",
            "sort_order": 7,
            "theory": theory_mixed,
            "task_key": "mixed_1"
        },
        {
            "slug": "integers-addition-subtraction-2",
            "room_code": "math-6-mixed-2",
            "name": "Складання і віднімання цілих чисел (Кабінет 2)",
            "description": "Тренувальний кабінет 2: складання та віднімання.",
            "sort_order": 8,
            "theory": theory_mixed,
            "task_key": "mixed_2"
        },
        {
            "slug": "integers-addition-subtraction-3",
            "room_code": "math-6-mixed-3",
            "name": "Складання і віднімання цілих чисел (Кабінет 3)",
            "description": "Тренувальний кабінет 3: складання та віднімання.",
            "sort_order": 9,
            "theory": theory_mixed,
            "task_key": "mixed_3"
        },

        # Multiplication (2 cabinets)
        {
            "slug": "integers-multiplication-1",
            "room_code": "math-6-mul-1",
            "name": "Множення цілих чисел (Кабінет 1)",
            "description": "Правила знаків та практика множення додатних і від'ємних чисел.",
            "sort_order": 10,
            "theory": theory_multiplication,
            "task_key": "multiplication_1"
        },
        {
            "slug": "integers-multiplication-2",
            "room_code": "math-6-mul-2",
            "name": "Множення цілих чисел (Кабінет 2)",
            "description": "Тренувальний кабінет 2 з множення цілих чисел.",
            "sort_order": 11,
            "theory": theory_multiplication,
            "task_key": "multiplication_2"
        },

        # Division (2 cabinets)
        {
            "slug": "integers-division-1",
            "room_code": "math-6-div-1",
            "name": "Ділення цілих чисел (Кабінет 1)",
            "description": "Правила та обчислення часток цілих чисел з різними знаками.",
            "sort_order": 12,
            "theory": theory_division,
            "task_key": "division_1"
        },
        {
            "slug": "integers-division-2",
            "room_code": "math-6-div-2",
            "name": "Ділення цілих чисел (Кабінет 2)",
            "description": "Тренувальний кабінет 2 з ділення цілих чисел.",
            "sort_order": 13,
            "theory": theory_division,
            "task_key": "division_2"
        },

        # Modulus (1 cabinet)
        {
            "slug": "integers-modulus",
            "room_code": "math-6-abs",
            "name": "Знаходження модуля числа",
            "description": "Визначення та обчислення абсолютного значення (модуля) чисел.",
            "sort_order": 14,
            "theory": theory_modulus,
            "task_key": "modulus_1"
        },

        # Opposite number (1 cabinet)
        {
            "slug": "integers-opposite",
            "room_code": "math-6-opp",
            "name": "Знаходження протилежного числа",
            "description": "Визначення та запис протилежних чисел для додатних і від'ємних чисел.",
            "sort_order": 15,
            "theory": theory_opposite,
            "task_key": "opposite_1"
        }
    ]

    generated_tasks = generate_validated_examples()

    for t_meta in topics_meta:
        topic = db.query(Topic).filter_by(subject_id=subject.id, slug=t_meta["slug"]).first()
        if not topic:
            topic = Topic(
                subject_id=subject.id,
                name=t_meta["name"],
                slug=t_meta["slug"],
                room_code=t_meta["room_code"],
                description=t_meta["description"],
                theory_content=t_meta["theory"],
                sort_order=t_meta["sort_order"]
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)
        else:
            topic.room_code = t_meta["room_code"]
            topic.name = t_meta["name"]
            topic.description = t_meta["description"]
            topic.theory_content = t_meta["theory"]
            topic.sort_order = t_meta["sort_order"]
            db.commit()

        # Seed 20 tasks for this topic
        task_count = db.query(Task).filter_by(topic_id=topic.id).count()
        if task_count < 20:
            db.query(Task).filter_by(topic_id=topic.id).delete()
            db.commit()

            tasks_data = generated_tasks[t_meta["task_key"]]
            for order, (q_expr, ans, hint) in enumerate(tasks_data, start=1):
                task = Task(
                    topic_id=topic.id,
                    task_order=order,
                    question=q_expr,
                    task_type="input_number",
                    correct_answer=ans,
                    hint=hint
                )
                db.add(task)
            db.commit()
            print(f"Seeded 20 tasks for topic: {t_meta['name']}")

    # ==========================================
    # 8th Grade: Informatics (Subject & Topics)
    # ==========================================
    subject_info = db.query(Subject).filter_by(grade_id=grade8.id, slug="informatics").first()
    if not subject_info:
        subject_info = Subject(
            grade_id=grade8.id,
            name="Інформатика",
            slug="informatics",
            icon="laptop-code",
            sort_order=1
        )
        db.add(subject_info)
        db.commit()
        db.refresh(subject_info)

    theory_informatics = """### 💻 Інформатика 8 клас: Архіви даних. Стиснення даних

---

#### 📂 Навчальні матеріали та файли до уроку:
- 📊 **Презентація уроку (Слайди):** [Завантажити Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx](/static/materials/8class/compress_archive01/Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx)
- 📄 **Текстовий файл для практики 1:** [Завантажити archive_lesson1.txt (420 КБ)](/static/materials/8class/compress_archive01/archive_lesson1.txt)
- 📝 **Документ Word для практики 2:** [Завантажити franko-ivan-iakovych-farbovanyy-lys.docx (24 КБ)](/static/materials/8class/compress_archive01/franko-ivan-iakovych-farbovanyy-lys.docx)
- 🖼️ **Фотографія для практики 3 (Стиснення фото):** [Завантажити vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg (11.7 МБ)](/static/materials/8class/compress_archive01/vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg)

---

#### 📑 Короткий конспект уроку:

1. **Що таке стиснення даних?**
   - **Стиснення даних** — це процес перетворення інформації для зменшення її обсягу (розміру файлу) з метою економії місця на носії та прискорення передачі мережею.

2. **Два основні види стиснення:**
   - 🟢 **Стиснення БЕЗ ВТРАТ (Lossless):** Після розпакування дані відновлюються на 100% точно до кожного байту. Застосовується для: текстів, документів, програм, баз даних. Формати: `ZIP`, `7z`, `RAR`, `PNG`.
   - 🟡 **Стиснення З ВТРАТАМИ (Lossy):** Алгоритм відкидає деталі, які найменш помітні людському оку чи слуху. Дозволяє зменшити обсяг у десятки разів, але оригінал відновити неможливо. Застосовується для: фото, аудіо, відео. Формати: `JPEG`, `MP3`, `MP4`.

3. **Формули розрахунку стиснення:**
   - **Коефіцієнт стиснення ($K$):** $K = \frac{\\text{Початковий розмір}}{\\text{Стиснений розмір}}$ *(показує, у скільки разів зменшився файл)*.
   - **Відсоток економії:** $\\text{Економія (\\%)} = \\left(1 - \\frac{\\text{Стиснений розмір}}{\\text{Початковий розмір}}\\right) \\times 100\\%$.

4. **Чому різні файли стискаються по-різному?**
   - Файли з повторюваною структурою (`.txt`) стискаються у **сотні разів** ($K \\approx 327$).
   - Файли, що вже містять внутрішнє стиснення (`.docx`, `.jpeg`, `.mp3`), під час повторного архівування в ZIP майже не змінюють розмір ($K \\approx 1.0 - 1.1$).

5. **Безпека архівів:**
   - Пароль захищає від несанкціонованого доступу, але не робить невідомий файл безпечним. Пам'ятайте: **Архівування $\\neq$ Резервна копія $\\neq$ Антивірус**.
"""

    info_topic = db.query(Topic).filter_by(subject_id=subject_info.id, slug="info-8-compress").first()
    if not info_topic:
        info_topic = Topic(
            subject_id=subject_info.id,
            name="Архіви даних. Стиснення даних",
            slug="info-8-compress",
            room_code="info-8-compress",
            description="Учбовий матеріал (слайди), практичні дослідження коефіцієнтів стиснення текстових файлів та візуальне стиснення зображень.",
            theory_content=theory_informatics,
            sort_order=1
        )
        db.add(info_topic)
        db.commit()
        db.refresh(info_topic)
    else:
        info_topic.room_code = "info-8-compress"
        info_topic.name = "Архіви даних. Стиснення даних"
        info_topic.description = "Учбовий матеріал (слайди), практичні дослідження коефіцієнтів стиснення текстових файлів та візуальне стиснення зображень."
        info_topic.theory_content = theory_informatics
        info_topic.sort_order = 1
        db.commit()

    # Seed 10 practical and theoretical tasks for informatics
    info_tasks_count = db.query(Task).filter_by(topic_id=info_topic.id).count()
    if info_tasks_count < 10:
        db.query(Task).filter_by(topic_id=info_topic.id).delete()
        db.commit()

        tasks_informatics_data = [
            {
                "task_order": 1,
                "question": "Що є головною метою стиснення даних?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Зменшення обсягу даних для економії пам'яті та прискорення передавання мережею"},
                    {"key": "B", "text": "Збільшення розміру файлу для кращого збереження"},
                    {"key": "C", "text": "Автоматичне видалення вірусів з комп'ютера"},
                    {"key": "D", "text": "Переклад тексту файлу іншими мовами"}
                ], ensure_ascii=False),
                "hint": "Стиснення даних зменшує їх обсяг, щоб файли займали менше місця і швидше завантажувалися."
            },
            {
                "task_order": 2,
                "question": "Який вид стиснення використовується для текстових файлів, програм і баз даних, де неприпустима втрата жодного байта чи символу?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Стиснення без втрат (Lossless) — після розпакування відновлюється 100% точна копія"},
                    {"key": "B", "text": "Стиснення з втратами (Lossy) — відкидається частина символів для економії"},
                    {"key": "C", "text": "Візуальне стиснення з розмиттям тексту"},
                    {"key": "D", "text": "Часткове видалення випадкових слів"}
                ], ensure_ascii=False),
                "hint": "Для програм і документів застосовують тільки стиснення БЕЗ втрат (ZIP, 7z)."
            },
            {
                "task_order": 3,
                "question": "Практика з файлом archive_lesson1.txt: Початковий розмір файлу становить 430 000 байт (~420 КБ). Заархівуйте цей файл у формат ZIP (через архіватор або вбудовану лабораторію). Розмір отриманого архіву становить приблизно 1 315 байт (~1.3 КБ). Обчисліть, у скільки разів зменшився файл (коефіцієнт стиснення K = 430000 / 1315). Введіть округлене ціле число (у скільки разів):",
                "task_type": "input_number",
                "correct_answer": "327|327x|327х|327 разів|320-335",
                "options_json": None,
                "hint": "Поділіть 430 000 на 1 315: 430000 / 1315 ≈ 327 разів!"
            },
            {
                "task_order": 4,
                "question": "Практика з документом franko-ivan-iakovych-farbovanyy-lys.docx: Початковий розмір файлу становить 24 318 байт (~23.7 КБ). Спробуйте заархівувати цей файл у ZIP. Отриманий архів займає приблизно 21 536 байт (~21 КБ). Обчисліть коефіцієнт стиснення K (K = 24318 / 21536). Введіть число з точністю до десятих або сотих (наприклад 1.1 або 1.13):",
                "task_type": "text",
                "correct_answer": "1.13|1.1|1.13x|1.13х|1.1x",
                "options_json": None,
                "hint": "Поділіть 24318 на 21536: вийде приблизно 1.13 (обсяг зменшився лише в 1.13 раза)."
            },
            {
                "task_order": 5,
                "question": "Чому звичайний текстовий файл .txt стиснувся в ~327 разів, а документ .docx — лише в ~1.13 раза?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Файл .docx вже сам по собі є внутрішнім ZIP-архівом XML-документів, тому повторне стиснення майже не дає ефекту"},
                    {"key": "B", "text": "Архіватори не вміють працювати з українським текстом казок"},
                    {"key": "C", "text": "Файл .txt містить віруси, які видаляються при архівації"},
                    {"key": "D", "text": "У документах .docx заборонено зменшення розміру"}
                ], ensure_ascii=False),
                "hint": "Файли .docx, .xlsx, .pptx є архівами ZIP, усередині яких уже запаковано XML-структури та ресурси."
            },
            {
                "task_order": 6,
                "question": "Практика з фотографією vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg: Початковий розмір становить 11 735 063 байт (~11.74 МБ). Стисніть якість зображення (за допомогою лабораторії або графічного редактора) так, щоб на камінцях з'явилися помітні артефакти стиснення, а розмір зменшився приблизно до 1 173 500 байт (~1.17 МБ). У скільки разів було стиснуто зображення (11.74 / 1.17)?",
                "task_type": "input_number",
                "correct_answer": "10|10x|10х|10 разів",
                "options_json": None,
                "hint": "11.74 МБ / 1.17 МБ = 10 разів (розмір зменшився в 10 разів при помітній втраті дрібних деталей)."
            },
            {
                "task_order": 7,
                "question": "Якщо ми стиснемо зображення максимально низькою якістю до розміру 60 КБ (0.06 МБ), воно стане сильно розмитим та пікселізованим. У скільки приблизно разів зменшився розмір від початкових 11 740 КБ до 60 КБ (11740 / 60)?",
                "task_type": "input_number",
                "correct_answer": "195|196|200|190-200|195.6",
                "options_json": None,
                "hint": "11740 КБ / 60 КБ ≈ 195-200 разів!"
            },
            {
                "task_order": 8,
                "question": "Практика: спробуйте заархівувати фотографію JPEG (11.74 МБ) архіватором ZIP. Розмір ZIP-архіву вийшов 11.68 МБ. Який коефіцієнт стиснення (у скільки разів зменшився файл: 11.74 / 11.68)?",
                "task_type": "text",
                "correct_answer": "1|1.0|1.00|1x|1х",
                "options_json": None,
                "hint": "11.74 / 11.68 ≈ 1.0 (файл майже не змінив свій розмір, оскільки JPEG уже містить стиснені дані)."
            },
            {
                "task_order": 9,
                "question": "Для яких типів файлів доцільно застосовувати стиснення З ВТРАТАМИ (Lossy), а для яких — виключно БЕЗ ВТРАТ (Lossless)?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "З втратами — для фото, відео та аудіо; без втрат — для тексту, програм, таблиць та баз даних"},
                    {"key": "B", "text": "З втратами — для програм і коду; без втрат — для фотографій"},
                    {"key": "C", "text": "Для всіх типів даних використовується лише стиснення з втратами"},
                    {"key": "D", "text": "Для всіх файлів завжди використовується однаковий алгоритм"}
                ], ensure_ascii=False),
                "hint": "Людське око чи слух не помічають незначних втрат у фото/аудіо, але в програмі чи тексті втрата навіть одного символу призведе до помилки."
            },
            {
                "task_order": 10,
                "question": "Чи гарантує встановлення пароля на ZIP/7z архів, що файли всередині не містять комп'ютерних вірусів, якщо архів завантажено з ненадійного сайту?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Ні, пароль лише захищає від стороннього перегляду, але не робить невідомий файл безпечним"},
                    {"key": "B", "text": "Так, пароль автоматично знищує всі віруси всередині архіву"},
                    {"key": "C", "text": "Так, антивіруси не потрібні, якщо на файлі є пароль"},
                    {"key": "D", "text": "Пароль змінює тип файлу на безпечний"}
                ], ensure_ascii=False),
                "hint": "Пам'ятайте правило зі слайдів: Архівування ≠ Резервна копія ≠ Антивірус. Пароль захищає від відкриття, а не від вірусів."
            }
        ]

        for t_info in tasks_informatics_data:
            task = Task(
                topic_id=info_topic.id,
                task_order=t_info["task_order"],
                question=t_info["question"],
                task_type=t_info["task_type"],
                correct_answer=t_info["correct_answer"],
                options_json=t_info["options_json"],
                hint=t_info["hint"]
            )
            db.add(task)
        db.commit()
        print(f"Seeded 10 practical tasks for topic: {info_topic.name}")

    theory_archives_8 = """### 💻 Практична робота: «Операції з архівами даних» (8 клас)

**Тема:** Операції з архівами даних (перегляд вмісту, розархівація, створення нових архівів).  
**Мета:** Набути практичних навичок роботи з архівами для оптимізації збереження дискового простору та ефективної передачі даних мережею; навчитися досліджувати вміст стиснених папок, видобувати файли та створювати власні архіви за допомогою сучасних архіваторів (`7-Zip`, `WinRAR`) або системних засобів ОС.  
**Обладнання та програмне забезпечення:** Персональний комп'ютер, файловий менеджер (Провідник), встановлені програми-архіватори (`7-Zip`, `WinRAR` або вбудовані засоби Windows/Linux).

---

#### 📁 Вихідні матеріали для практичної роботи:
- 📦 **Архів для дослідження та розпакування:** [Завантажити compress_archive01.zip (11.7 МБ)](/static/materials/8class/operation_with_archives/compress_archive01.zip)
- 🖼️ **Зображення 1:** [Завантажити 6711626.png (4.4 КБ)](/static/materials/8class/operation_with_archives/6711626.png)
- 🖼️ **Зображення 2:** [Завантажити 742940.png (5.2 КБ)](/static/materials/8class/operation_with_archives/742940.png)
- 📝 **Текстовий документ:** [Завантажити franko-ivan-iakovych-kameniari647.docx (9.5 КБ)](/static/materials/8class/operation_with_archives/franko-ivan-iakovych-kameniari647.docx)
- 📑 **Комплексний документ із малюнками:** [Завантажити тексти з малюнками.docx (16.3 МБ)](/static/materials/8class/operation_with_archives/тексти%20з%20малюнками.docx)

---

#### 📋 Покроковий хід виконання практичної роботи:

##### Етап 1. Підготовка робочого простору
1. На Робочому столі або у своїй робочій папці створіть нову папку з назвою у форматі: `Практична_Архіви_Прізвище_Клас` (наприклад, `Практична_Архіви_Шевченко_8Б`).
2. Завантажте всі 5 вихідних файлів у вашу новостворену робочу папку.

---

##### Етап 2. Дослідження та розпакування архіву `compress_archive01.zip`
1. **Перегляд вмісту без видобування:**
   - Відкрийте файл `compress_archive01.zip` подвійним кліком миші або через контекстне меню за допомогою архіватора (`7-Zip` ➔ `Відкрити архів` або `WinRAR`).
   - Дослідіть перелік файлів, які зберігаються всередині архіву:
     - `franko-ivan-iakovych-farbovanyy-lys.docx`
     - `vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg`
     - `Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx`
     - `archive_lesson1.txt`
   - Зверніть увагу на колонки `Розмір` (початковий) та `Стиснений розмір` у вікні архіватора. Зверніть увагу, як значно скорочується розмір текстових файлів порівняно з уже стисненими зображеннями.
2. **Розпакування (видобування) даних:**
   - Виконайте розпакування архіву:
     - **Через контекстне меню:** Клікніть правою кнопкою миші на `compress_archive01.zip` ➔ виберіть `7-Zip` / `WinRAR` ➔ `Видобути до "compress_archive01\"` (або `Видобути все...`).
     - **З вікна програми:** Натисніть кнопку `Видобути` (`Extract`) на панелі інструментів архіватора та вкажіть вашу робочу папку.
   - Переконайтеся, що всі 4 файли успішно розархівовано та вони доступні для відкриття.

---

##### Етап 3. Створення нового архіву з окремих файлів
1. Поверніться до робочої папки.
2. Виділіть **всі інші 4 вихідні файли** (крім архіву `compress_archive01.zip` та створеної папки з розпакованими файлами):
   - `6711626.png`
   - `742940.png`
   - `franko-ivan-iakovych-kameniari647.docx`
   - `тексти з малюнками.docx`
3. Натисніть правою кнопкою миші на виділених файлах та запакуйте їх в один спільний архів, використовуючи доступний архіватор:
   - **Якщо встановлено 7-Zip:** `7-Zip` ➔ `Додати до архіву...` ➔ задайте ім'я: `Мій_Архів_Прізвище.7z` або `Мій_Архів_Прізвище.zip` ➔ натисніть `OK`.
   - **Якщо встановлено WinRAR:** `Додати до архіву...` (`Add to archive...`) ➔ ім'я: `Мій_Архів_Прізвище.rar` (або `.zip`) ➔ натисніть `OK`.
   - **Вбудовані засоби Windows:** `Надіслати` ➔ `Стиснута ZIP-папка` ➔ перейменуйте створений файл на `Мій_Архів_Прізвище.zip`.

---

##### Етап 4. Аналіз ефективності стиснення (Звіт та тестування)
1. Порівняйте сумарний розмір 4 початкових файлів із розміром створеного вами архіву.
2. Дайте відповіді на контрольні запитання та завдання у вкладці «Завдання».
"""

    archives_topic = db.query(Topic).filter_by(subject_id=subject_info.id, slug="info-8-archive-operations").first()
    if not archives_topic:
        archives_topic = Topic(
            subject_id=subject_info.id,
            name="Практична робота. Операції з архівами",
            slug="info-8-archive-operations",
            room_code="info-8-archive-operations",
            description="Практична робота: завантаження вихідних файлів, перегляд вмісту та розпакування ZIP-архіву, створення власного архіву (WinRAR, 7-Zip, засоби ОС).",
            theory_content=theory_archives_8,
            sort_order=2
        )
        db.add(archives_topic)
        db.commit()
        db.refresh(archives_topic)
    else:
        archives_topic.name = "Практична робота. Операції з архівами"
        archives_topic.room_code = "info-8-archive-operations"
        archives_topic.description = "Практична робота: завантаження вихідних файлів, перегляд вмісту та розпакування ZIP-архіву, створення власного архіву (WinRAR, 7-Zip, засоби ОС)."
        archives_topic.theory_content = theory_archives_8
        archives_topic.sort_order = 2
        db.commit()

    archives_tasks = [
        (1, "Скільки всього вихідних файлів необхідно завантажити для початку практичної роботи з теми «Операції з архівами»?", "choice", "A", [
            {"key": "A", "text": "5 файлів (1 zip-архів, 2 зображення png, 2 документи docx)"},
            {"key": "B", "text": "Тільки 1 файл"},
            {"key": "C", "text": "10 файлів"},
            {"key": "D", "text": "3 файли"}
        ], "У папці матеріалів міститься 5 файлів: compress_archive01.zip, 6711626.png, 742940.png, franko-ivan-iakovych-kameniari647.docx та тексти з малюнками.docx."),

        (2, "Які файли містяться всередині архіву compress_archive01.zip при перегляді без розархівації?", "choice", "A", [
            {"key": "A", "text": "4 файли: презентація pptx, казка «Фарбований лис» docx, фото jpeg та текстовий файл txt"},
            {"key": "B", "text": "Лише один порожній текстовий документ"},
            {"key": "C", "text": "Тільки вірш «Каменярі»"},
            {"key": "D", "text": "Виключно відеофайли"}
        ], "Всередині compress_archive01.zip знаходяться: franko-ivan-iakovych-farbovanyy-lys.docx, vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg, Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx та archive_lesson1.txt."),

        (3, "Яка дія виконує видобування (розпакування) всіх файлів з compress_archive01.zip на комп'ютері?", "choice", "A", [
            {"key": "A", "text": "Контекстне меню ➔ 7-Zip / WinRAR ➔ «Видобути до...» (або «Видобути все...» у Провіднику)"},
            {"key": "B", "text": "Перейменування розширення .zip на .txt"},
            {"key": "C", "text": "Відкриття файлу у Microsoft Word"},
            {"key": "D", "text": "Видалення архіву в Кошик"}
        ], "Для розархівації використовують команди видобування (Extract) в архіваторах 7-Zip/WinRAR або стандартному Провіднику."),

        (4, "Скільки інших окремих файлів (крім compress_archive01.zip) потрібно запакувати в один спільний архів на Етапі 3 практичної роботи?", "choice", "A", [
            {"key": "A", "text": "4 файли (6711626.png, 742940.png, franko-ivan-iakovych-kameniari647.docx та тексти з малюнками.docx)"},
            {"key": "B", "text": "Тільки 2 файли зображень"},
            {"key": "C", "text": "1 файл"},
            {"key": "D", "text": "5 файлів"}
        ], "Потрібно запакувати 4 файли: 6711626.png, 742940.png, franko-ivan-iakovych-kameniari647.docx та тексти з малюнками.docx."),

        (5, "Які програми-архіватори або засоби операційної системи можна використати для створення нового архіву на комп'ютері?", "choice", "A", [
            {"key": "A", "text": "7-Zip, WinRAR або вбудовані засоби Windows («Надіслати ➔ Стиснута ZIP-папка»)"},
            {"key": "B", "text": "Блокнот (Notepad) та Калькулятор"},
            {"key": "C", "text": "Google Chrome або Mozilla Firefox"},
            {"key": "D", "text": "Paint та Фотографії"}
        ], "Для створення архівів призначені спеціалізовані програми-архіватори (7-Zip, WinRAR) або засоби ОС."),

        (6, "Документ «тексти з малюнками.docx» має початковий розмір ~16.3 МБ (16 325 789 байт). Після додавання до ZIP-архіву його розмір зменшився лише до ~16.2 МБ. Чому ступінь стиснення такий малий?", "choice", "A", [
            {"key": "A", "text": "Формат .docx уже сам по собі є ZIP-контейнером зі стисненими малюнками та XML, тому повторне стиснення майже не дає ефекту"},
            {"key": "B", "text": "Архіватори не вміють працювати з документами Word"},
            {"key": "C", "text": "Всі малюнки у документі були автоматично видалені архіватором"},
            {"key": "D", "text": "Це заборонено операційною системою"}
        ], "Сучасні формати MS Office (.docx, .xlsx, .pptx) вже використовують внутрішнє ZIP-стиснення, тому повторна архівація істотно не зменшує їхній розмір."),

        (7, "Два графічні файли (6711626.png ~ 4.4 КБ та 742940.png ~ 5.2 КБ) разом із віршем «Каменярі» (~ 9.5 КБ) мають сумарний розмір близько 19.1 КБ. Скільки це приблизно у байтах? (19.1 × 1024 байт):", "choice", "A", [
            {"key": "A", "text": "Близько 19 558 байт (~19.1 × 1024)"},
            {"key": "B", "text": "Рівно 1 024 байти"},
            {"key": "C", "text": "Близько 1 910 байт"},
            {"key": "D", "text": "Понад 191 000 байт"}
        ], "19.1 КБ × 1024 байт ≈ 19 558 байт (в 1 кілобайті міститься 1024 байти)."),

        (8, "У чому полягає головна перевага створення одного спільного архіву з групи файлів, навіть якщо їхній загальний розмір зменшився незначно?", "choice", "A", [
            {"key": "A", "text": "Об'єднання багатьох різних файлів у єдиний пакет для швидкого надсилання електронною поштою / месенджером та збереження цілісності"},
            {"key": "B", "text": "Автоматичне покращення якості всіх зображень"},
            {"key": "C", "text": "Перетворення всіх файлів на формат PDF"},
            {"key": "D", "text": "Видалення всіх помилок у текстах документів"}
        ], "Архівування дозволяє передавати групу файлів як один зручний файл, зберігаючи їх структуру та назви."),

        (9, "Що обов'язково необхідно перевірити після виконання операції розпакування (видобування) архіву?", "choice", "A", [
            {"key": "A", "text": "Що всі файли успішно видобуто, їхня кількість збігається з вмістом архіву та вони коректно відкриваються"},
            {"key": "B", "text": "Що початковий архів автоматично стерся з диска"},
            {"key": "C", "text": "Що розширення всіх файлів змінилося на .exe"},
            {"key": "D", "text": "Що всі файли стали однакового розміру"}
        ], "Після розпакування завжди перевіряють повноту й працездатність отриманих файлів.")
    ]

    db.query(Task).filter_by(topic_id=archives_topic.id).delete()
    for order, question, task_type, answer, options, hint in archives_tasks:
        db.add(Task(
            topic_id=archives_topic.id,
            task_order=order,
            question=question,
            task_type=task_type,
            correct_answer=answer,
            options_json=json.dumps(options, ensure_ascii=False) if options else None,
            hint=hint
        ))
    db.commit()
    print(f"Seeded {len(archives_tasks)} tasks for topic: {archives_topic.name}")

    # ==========================================
    # 9th Grade: Informatics (Subject & Topics)
    # ==========================================
    subject_info9 = db.query(Subject).filter_by(grade_id=grade9.id, slug="informatics").first()
    if not subject_info9:
        subject_info9 = Subject(
            grade_id=grade9.id,
            name="Інформатика",
            slug="informatics",
            icon="laptop-code",
            sort_order=1
        )
        db.add(subject_info9)
        db.commit()
        db.refresh(subject_info9)

    theory_informatics_9 = """### 💻 Інформатика 9 клас: Формати файлів текстових документів. Режими роботи в середовищі текстового процесора

---

#### 📂 Навчальні матеріали та файли до уроку:
- 📊 **Презентація уроку (Слайди):** [Завантажити Informatyka_9_Formaty_faіliv_Rezhymy_Google_Docs_v2.pptx](/static/materials/9class/text_formats/Informatyka_9_Formaty_faіliv_Rezhymy_Google_Docs_v2.pptx)
- 📝 **Текстовий файл для практичної роботи:** [Завантажити тексти з малюнками.docx (12.8 МБ)](/static/materials/9class/text_formats/тексти%20з%20малюнками.docx)
- 🌐 **Спільний документ Google Docs для онлайн-практики:** [Відкрити спільний Google Документ](https://docs.google.com/document/d/1s-QvJ74JqI3qunfwcdKrfA5jNia4RnxBip7eElOfZ1s/edit?usp=sharing)

---

#### 📋 Покроковий план практичної роботи:
1. **Завантажити вихідний файл:** скачайте файл `тексти з малюнками.docx` (12.8 МБ, містить текст та 110 ілюстрацій).
2. **Завантажити в Google Docs:** відкрийте [Google Диск / Google Docs](https://docs.google.com) та завантажте цей документ.
3. **Вивантажити з Google Docs у 5 різних форматах:** у меню *«Файл» ➔ «Завантажити»* збережіть документ у таких форматах:
   - 📄 **Звичайний текст (.txt)**
   - 📑 **Формат OpenDocument (.odt)**
   - 📝 **Microsoft Word (.docx)**
   - 📕 **Документ PDF (.pdf)**
   - 📄 **Збагачений текст (.rtf)**
4. **Роздивитись отримані файли:**
   - Відкрийте кожен збережений файл і порівняйте: де збереглося повне форматування та всі 110 малюнків, а де залишився виключно текст?
5. **Дослідити розміри файлів та заповнити форму в кабінеті:**
   - Перевірте у провіднику розмір кожного файлу (наприклад: `.txt` ~ 8–12 КБ, `.odt` ~ 12.8 МБ, `.docx` ~ 12.8 МБ, `.pdf` ~ 14–16 МБ, `.rtf` ~ 120–160 МБ).
6. **Спільна онлайн-робота в документі:**
   - Перейдіть за посиланням [Спільний документ Google Docs](https://docs.google.com/document/d/1s-QvJ74JqI3qunfwcdKrfA5jNia4RnxBip7eElOfZ1s/edit?usp=sharing).
   - Ознайомтеся з режимами: **«Редагування»**, **«Пропонування»**, **«Перегляд»**.
   - Додайте коментар до фрагмента тексту та запропонуйте правку в режимі пропозицій.

---

#### 📑 Короткий конспект уроку:
1. **Що таке формат файлу?**
   - Формат визначає структуру кодування даних у файлі та те, які програми можуть коректно відкривати й змінювати його.
2. **Основні формати текстових документів:**
   - 📄 **TXT (.txt):** простий текст без оформлення, таблиць та графіки. Універсальний, займає мінімальний розмір.
   - 📝 **DOCX (.docx):** основний формат MS Word. Внутрішньо є ZIP-архівом з XML-структурою та стисненими медіа.
   - 📑 **ODT (.odt):** відкритий міжнародний формат (LibreOffice Writer / OpenOffice).
   - 📕 **PDF (.pdf):** збереження фіксованого вигляду сторінок, не залежить від встановлених шрифтів на пристрої.
   - 📄 **RTF (.rtf):** Rich Text Format. Зберігає стилі, але вбудовує растрові картинки у нестисненому шістнадцятковому текстовому вигляді.
3. **Три режими роботи в Google Docs:**
   - ✏️ **Редагування (Editing):** пряма зміна документа без підтверджень.
   - 💬 **Пропонування (Suggesting):** зміни пропонуються у вигляді коментарів/виправлень, які автор може прийняти (✓) або відхилити (✕).
   - 👁️ **Перегляд (Viewing):** захист від випадкових змін під час читання.
4. **Права доступу користувачів:**
   - **Читач:** тільки перегляд без коментарів.
   - **Коментатор:** перегляд + коментарі та пропонування змін.
   - **Редактор:** повні права редагування.
5. **Історія версій:** фіксація авторів, часу змін і можливість відкату до попереднього варіанта.
"""

    info9_topic = db.query(Topic).filter_by(subject_id=subject_info9.id, slug="info-9-formats").first()
    if not info9_topic:
        info9_topic = Topic(
            subject_id=subject_info9.id,
            name="Формати файлів текстових документів. Режими роботи в середовищі текстового процесора.",
            slug="info-9-formats",
            room_code="info-9-formats",
            description="Слайди уроку, покроковий план практики з Google Docs, дослідження розмірів 5 форматів файлів та спільна робота.",
            theory_content=theory_informatics_9,
            sort_order=1
        )
        db.add(info9_topic)
        db.commit()
        db.refresh(info9_topic)
    else:
        info9_topic.room_code = "info-9-formats"
        info9_topic.name = "Формати файлів текстових документів. Режими роботи в середовищі текстового процесора."
        info9_topic.description = "Слайди уроку, покроковий план практики з Google Docs, дослідження розмірів 5 форматів файлів та спільна робота."
        info9_topic.theory_content = theory_informatics_9
        info9_topic.sort_order = 1
        db.commit()

    # Seed 10 practical and theoretical tasks for 9th grade informatics
    info9_tasks_count = db.query(Task).filter_by(topic_id=info9_topic.id).count()
    if info9_tasks_count < 10:
        db.query(Task).filter_by(topic_id=info9_topic.id).delete()
        db.commit()

        tasks_informatics_9_data = [
            {
                "task_order": 1,
                "question": "Що визначає формат файлу текстового документа?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Спосіб збереження і кодування даних у файлі та те, які програми можуть із ним працювати"},
                    {"key": "B", "text": "Тільки кількість слів та літер у тексті документа"},
                    {"key": "C", "text": "Колір монітора або яскравість екрана користувача"},
                    {"key": "D", "text": "Швидкість інтернет-з'єднання автора документа"}
                ], ensure_ascii=False),
                "hint": "Формат файлу визначає структуру даних та сумісні програми для його читання й редагування."
            },
            {
                "task_order": 2,
                "question": "Який формат текстового документа зберігає виключно простий неформатований текст без шрифтів, кольорів, таблиць та зображень?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "TXT (.txt) — простий текст"},
                    {"key": "B", "text": "DOCX (.docx) — документ Word"},
                    {"key": "C", "text": "PDF (.pdf) — фіксований макет"},
                    {"key": "D", "text": "ODT (.odt) — документ OpenDocument"}
                ], ensure_ascii=False),
                "hint": "Формат .txt зберігає лише символи тексту без будь-яких елементів оформлення чи картинок."
            },
            {
                "task_order": 3,
                "question": "Практична робота з файлом «тексти з малюнками.docx»: Початковий файл займав ~12.8 МБ і містив 110 малюнків. Ви експортували документ із Google Docs у формат простого тексту (.txt). Оскільки .txt відкидає всі зображення та стилі, розмір файлу різко зменшився. Скільки приблизно кілобайт (КБ) займає отриманий файл .txt? (Введіть значення в КБ, наприклад від 8 до 12):",
                "task_type": "text",
                "correct_answer": "8|8.5|9|10|11|12|8.2|8-12|8-15|8 КБ|8 KB|9 КБ|10 КБ|8-12 КБ|8-12 KB",
                "options_json": None,
                "hint": "Текст без зображень займає близько 8–12 КБ (у понад 1000 разів менше за початковий документ з малюнками!)."
            },
            {
                "task_order": 4,
                "question": "Практика: Чому файл у форматі RTF (.rtf), експортований для документа з 110 малюнками, займає величезний обсяг (понад 120-150 МБ) у порівнянні з .docx (~12.8 МБ)?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Формат RTF зберігає растрові малюнки у нестисненому шістнадцятковому текстовому коді, а DOCX і ODT є внутрішніми ZIP-архівами"},
                    {"key": "B", "text": "RTF автоматично додає комп'ютерні віруси до файлу"},
                    {"key": "C", "text": "У форматі RTF весь текст дублюється 100 разів"},
                    {"key": "D", "text": "Google Docs навмисно збільшує розмір файлів формату RTF"}
                ], ensure_ascii=False),
                "hint": "Формат RTF вбудовує картинки у нестисненому вигляді (hex-текст), тому файли з малюнками стають велетенськими."
            },
            {
                "task_order": 5,
                "question": "Який формат файлу найкраще підходить для надсилання вчителю готового реферату або для друку, коли необхідно гарантувати збереження точного вигляду сторінок на будь-якому пристрої?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "PDF (.pdf) — фіксує точний вигляд сторінок незалежно від пристрою"},
                    {"key": "B", "text": "TXT (.txt) — простий текст"},
                    {"key": "C", "text": "RTF (.rtf) — збагачений текст"},
                    {"key": "D", "text": "CSV (.csv) — табличні дані"}
                ], ensure_ascii=False),
                "hint": "Формат PDF (Portable Document Format) фіксує макет, шрифти та положення об'єктів для друку й перегляду."
            },
            {
                "task_order": 6,
                "question": "Які три режими роботи доступні користувачу в середовищі Google Документів?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Редагування, Пропонування, Перегляд"},
                    {"key": "B", "text": "Друк, Сканування, Форматування"},
                    {"key": "C", "text": "Запуск, Зупинка, Перезавантаження"},
                    {"key": "D", "text": "Аудіо, Відео, Анімація"}
                ], ensure_ascii=False),
                "hint": "Google Docs має 3 режими: Редагування (прямі правки), Пропонування (пропозиції) та Перегляд (читання)."
            },
            {
                "task_order": 7,
                "question": "У якому режимі Google Docs внесені виправлення не змінюють текст остаточно, а відображаються як кольорові пропозиції, які автор може прийняти (✓) або відхилити (✕)?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Режим «Пропонування» (Suggesting)"},
                    {"key": "B", "text": "Режим «Перегляд» (Viewing)"},
                    {"key": "C", "text": "Режим «Редагування» (Editing)"},
                    {"key": "D", "text": "Режим «Автозбереження»"}
                ], ensure_ascii=False),
                "hint": "У режимі «Пропонування» всі зміни зберігаються у вигляді пропозицій для автора документа."
            },
            {
                "task_order": 8,
                "question": "Чим відрізняється право доступу «Коментатор» від права «Редактор» під час надання спільного доступу до Google Документа?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Коментатор може читати, залишати коментарі та пропонувати зміни, але не може безпосередньо змінювати оригінал"},
                    {"key": "B", "text": "Коментатор має право безповоротно видалити файл з Google Диска"},
                    {"key": "C", "text": "Коментатор не має доступу навіть для читання тексту"},
                    {"key": "D", "text": "Коментатор і Редактор мають абсолютно однакові права"}
                ], ensure_ascii=False),
                "hint": "Коментатор може лише обговорювати та пропонувати правки, тоді як Редактор змінює текст напряму."
            },
            {
                "task_order": 9,
                "question": "Практична робота: За яким посиланням організовано спільний документ Google Docs для виконання завдань учнями?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "https://docs.google.com/document/d/1s-QvJ74JqI3qunfwcdKrfA5jNia4RnxBip7eElOfZ1s/edit?usp=sharing"},
                    {"key": "B", "text": "https://www.google.com"},
                    {"key": "C", "text": "https://uk.wikipedia.org"},
                    {"key": "D", "text": "https://mail.google.com"}
                ], ensure_ascii=False),
                "hint": "Посилання на спільний документ доступне на панелі кабінету та в плані практичної роботи."
            },
            {
                "task_order": 10,
                "question": "Яка функція Google Документів дозволяє побачити, хто і коли вносив зміни до спільного файлу, та відновити попередній стан документа без створення багатьох копій («реферат_1», «реферат_фінал»)?",
                "task_type": "choice",
                "correct_answer": "A",
                "options_json": json.dumps([
                    {"key": "A", "text": "Історія версій (Version history)"},
                    {"key": "B", "text": "Буфер обміну (Clipboard)"},
                    {"key": "C", "text": "Перевірка правопису"},
                    {"key": "D", "text": "Лічильник слів"}
                ], ensure_ascii=False),
                "hint": "Історія версій автоматично фіксує хронологію всіх змін документа з авторами."
            }
        ]

        for t_info in tasks_informatics_9_data:
            task = Task(
                topic_id=info9_topic.id,
                task_order=t_info["task_order"],
                question=t_info["question"],
                task_type=t_info["task_type"],
                correct_answer=t_info["correct_answer"],
                options_json=t_info["options_json"],
                hint=t_info["hint"]
            )
            db.add(task)
        db.commit()
        print(f"Seeded 10 practical tasks for topic: {info9_topic.name}")

    print("Database seeding completed successfully.")
