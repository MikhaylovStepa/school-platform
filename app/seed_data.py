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

    try:
        db.execute(text("""
            UPDATE tasks 
            SET task_type = 'prime_factorization', options_json = '{"numbers": [72, 96]}' 
            WHERE task_order = 11 AND topic_id IN (SELECT id FROM topics WHERE slug = 'math-6-gcd-lcm');
        """))
        db.execute(text("""
            UPDATE tasks 
            SET task_type = 'prime_factorization', options_json = '{"numbers": [36, 54, 72]}' 
            WHERE task_order = 12 AND topic_id IN (SELECT id FROM topics WHERE slug = 'math-6-gcd-lcm');
        """))
        db.execute(text("""
            UPDATE tasks 
            SET task_type = 'prime_factorization', options_json = '{"numbers": [28, 42]}' 
            WHERE task_order = 13 AND topic_id IN (SELECT id FROM topics WHERE slug = 'math-6-gcd-lcm');
        """))
        db.execute(text("""
            UPDATE tasks 
            SET task_type = 'prime_factorization', options_json = '{"numbers": [12, 15, 18]}' 
            WHERE task_order = 14 AND topic_id IN (SELECT id FROM topics WHERE slug = 'math-6-gcd-lcm');
        """))
        db.commit()
    except Exception:
        db.rollback()

def upsert_topic_tasks(db: Session, topic_id: int, tasks_data: list):
    """
    Safely seeds or updates tasks for a topic without deleting tasks,
    preserving Task IDs and existing student progress / TaskAttempt history.
    """
    existing_tasks = {t.task_order: t for t in db.query(Task).filter_by(topic_id=topic_id).all()}
    
    for item in tasks_data:
        order = item["task_order"]
        if order in existing_tasks:
            t = existing_tasks[order]
            t.question = item["question"]
            t.task_type = item["task_type"]
            t.correct_answer = item["correct_answer"]
            t.options_json = item.get("options_json")
            t.hint = item.get("hint")
        else:
            t = Task(
                topic_id=topic_id,
                task_order=order,
                question=item["question"],
                task_type=item["task_type"],
                correct_answer=item["correct_answer"],
                options_json=item.get("options_json"),
                hint=item.get("hint")
            )
            db.add(t)
    
    max_order = max([item["task_order"] for item in tasks_data]) if tasks_data else 0
    for order, t in existing_tasks.items():
        if order > max_order:
            db.delete(t)
            
    db.commit()

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

        # Seed/update 20 tasks for this topic safely
        tasks_data = generated_tasks[t_meta["task_key"]]
        topic_tasks = [
            {
                "task_order": order,
                "question": q_expr,
                "task_type": "input_number",
                "correct_answer": ans,
                "options_json": None,
                "hint": hint
            }
            for order, (q_expr, ans, hint) in enumerate(tasks_data, start=1)
        ]
        upsert_topic_tasks(db, topic.id, topic_tasks)

    # =========================================================================
    # 6th Grade Math: Advanced Topics (Coefficients, Brackets, Like Terms, etc.)
    # =========================================================================

    # 1. Coefficient of Expression
    theory_coefficient = """### 📖 Теоретичний матеріал: Коефіцієнт виразу

#### Що таке числовий коефіцієнт?
Числовий множник у добутку числа і однієї або кількох букв називають **числовим коефіцієнтом** (або просто **коефіцієнтом**).

---

#### Основні правила:
1. Зазвичай числовий множник записують на **першому місці**:
   - У виразі `-5a` коефіцієнт дорівнює **`-5`**.
   - У виразі `7x` коефіцієнт дорівнює **`7`**.
   - У виразі `-12xy` коефіцієнт дорівнює **`-12`**.
   - У виразі `0.4m` коефіцієнт дорівнює **`0.4`**.
   - У виразі `-3.5ab` коефіцієнт дорівнює **`-3.5`**.

2. **Особливі випадки (коефіцієнти 1 та -1):**
   - Якщо перед буквою немає числового множника (наприклад, `x` або `y`), коефіцієнт дорівнює **`1`** (бо `1 · x = x`).
   - Якщо перед буквою стоїть тільки знак мінус (наприклад, `-a` або `-x`), коефіцієнт дорівнює **`-1`** (бо `-1 · a = -a`).
"""

    coeff_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-coefficient").first()
    if not coeff_topic:
        coeff_topic = Topic(
            subject_id=subject.id,
            name="Визначення коефіцієнта виразу",
            slug="math-6-coefficient",
            room_code="math-6-coefficient",
            description="Визначення числового коефіцієнта буквеного виразу (наприклад, -5a -> -5, -a -> -1, y -> 1).",
            theory_content=theory_coefficient,
            sort_order=16
        )
        db.add(coeff_topic)
        db.commit()
        db.refresh(coeff_topic)
    else:
        coeff_topic.name = "Визначення коефіцієнта виразу"
        coeff_topic.room_code = "math-6-coefficient"
        coeff_topic.description = "Визначення числового коефіцієнта буквеного виразу (наприклад, -5a -> -5, -a -> -1, y -> 1)."
        coeff_topic.theory_content = theory_coefficient
        coeff_topic.sort_order = 16
        db.commit()

    coeff_tasks_data = [
        ("Визначте коефіцієнт виразу: -5a", "-5", "Числовий множник перед буквою 'a' дорівнює -5."),
        ("Визначте коефіцієнт виразу: -a", "-1", "Якщо перед буквою стоїть лише знак мінус, коефіцієнт дорівнює -1."),
        ("Визначте коефіцієнт виразу: 7x", "7", "Числовий множник перед буквою 'x' дорівнює 7."),
        ("Визначте коефіцієнт виразу: y", "1", "Якщо перед буквою немає явного числа, коефіцієнт дорівнює 1 (1 · y = y)."),
        ("Визначте коефіцієнт виразу: -12xy", "-12", "Числовий множник перед буквеною частиною 'xy' дорівнює -12."),
        ("Визначте коефіцієнт виразу: 0.4m", "0.4", "Числовий множник дорівнює 0.4."),
        ("Визначте коефіцієнт виразу: -3.5ab", "-3.5", "Числовий множник дорівнює -3.5."),
        ("Визначте коефіцієнт виразу: 15k", "15", "Числовий множник перед буквою 'k' дорівнює 15."),
        ("Визначте коефіцієнт виразу: -b", "-1", "Коефіцієнт перед -b дорівнює -1."),
        ("Визначте коефіцієнт виразу: 2.5c", "2.5", "Числовий множник дорівнює 2.5."),
        ("Визначте коефіцієнт виразу: -18c", "-18", "Числовий множник перед буквою 'c' дорівнює -18."),
        ("Визначте коефіцієнт виразу: 100n", "100", "Числовий множник перед буквою 'n' дорівнює 100."),
        ("Визначте коефіцієнт виразу: -x", "-1", "Коефіцієнт перед -x дорівнює -1."),
        ("Визначте коефіцієнт виразу: 8mn", "8", "Числовий множник перед 'mn' дорівнює 8."),
        ("Визначте коефіцієнт виразу: -13a", "-13", "Числовий множник перед 'a' дорівнює -13."),
        ("Визначте коефіцієнт виразу: 4p", "4", "Числовий множник перед 'p' дорівнює 4."),
        ("Визначте коефіцієнт виразу: -0.7d", "-0.7", "Числовий множник дорівнює -0.7."),
        ("Визначте коефіцієнт виразу: 12xyz", "12", "Числовий множник перед 'xyz' дорівнює 12."),
        ("Визначте коефіцієнт виразу: -k", "-1", "Коефіцієнт перед -k дорівнює -1."),
        ("Визначте коефіцієнт виразу: 3.2ab", "3.2", "Числовий множник дорівнює 3.2.")
    ]

    coeff_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": "input_number",
            "correct_answer": ans,
            "options_json": None,
            "hint": hint
        }
        for order, (q_text, ans, hint) in enumerate(coeff_tasks_data, start=1)
    ]
    upsert_topic_tasks(db, coeff_topic.id, coeff_tasks)

    # 2. Opening Brackets Signs
    theory_brackets_signs = """### 📖 Теоретичний матеріал: Розкриття дужок (знаки доданків)

#### 1. Якщо перед дужками стоїть знак «+»:
Дужки та знак «+» опускають, а всі знаки доданків, що були всередині дужок, **залишають без змін**.
> **Приклад 1:** `+(-4a - c - ab) = -4a - c - ab` *(послідовність знаків: `---`)*
> **Приклад 2:** `+(a - b + c) = +a - b + c` *(послідовність знаків: `+-+`)*

---

#### 2. Якщо перед дужками стоїть знак «−»:
Дужки та знак «−» опускають, а знаки **всіх доданків у дужках змінюють на протилежні**:
- плюс змінюється на мінус;
- мінус змінюється на плюс.
> **Приклад 1:** `-(3x - 5y + 2z) = -3x + 5y - 2z` *(послідовність знаків: `-+-`)*
> **Приклад 2:** `-(-2a + b - 3c) = +2a - b + 3c` *(послідовність знаків: `+-+`)*
> **Приклад 3:** `-(a + b + c) = -a - b - c` *(послідовність знаків: `---`)*
"""

    brackets_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-brackets-signs").first()
    if not brackets_topic:
        brackets_topic = Topic(
            subject_id=subject.id,
            name="Розкриття дужок: знаки доданків",
            slug="math-6-brackets-signs",
            room_code="math-6-brackets-signs",
            description="Визначення послідовності знаків (+ та -) при розкритті дужок, перед якими стоїть плюс або мінус.",
            theory_content=theory_brackets_signs,
            sort_order=17
        )
        db.add(brackets_topic)
        db.commit()
        db.refresh(brackets_topic)
    else:
        brackets_topic.name = "Розкриття дужок: знаки доданків"
        brackets_topic.room_code = "math-6-brackets-signs"
        brackets_topic.description = "Визначення послідовності знаків (+ та -) при розкритті дужок, перед якими стоїть плюс або мінус."
        brackets_topic.theory_content = theory_brackets_signs
        brackets_topic.sort_order = 17
        db.commit()

    brackets_tasks_data = [
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(-4a - c - ab)", "---", "Перед дужками стоїть плюс, тому всі знаки зберігаються: -4a (-), -c (-), -ab (-) -> ---"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(3x - 5y + 2z)", "-+-", "Перед дужками стоїть мінус, тому всі знаки змінюються на протилежні: +3x -> -, -5y -> +, +2z -> - -> -+-"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(-2a + b - 3c)", "+-+", "Перед дужками стоїть мінус: -2a -> +, +b -> -, -3c -> + -> +-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(a - b + c)", "+-+", "Перед дужками стоїть плюс, знаки не змінюються: +a (+), -b (-), +c (+) -> +-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(a + b + c)", "---", "Перед дужками стоїть мінус, всі плюси змінюються на мінуси: -a, -b, -c -> ---"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(-x + y - z + t)", "-+-+", "Перед дужками плюс, знаки залишаються: -x (-), +y (+), -z (-), +t (+) -> -+-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(-x - y - z)", "+++", "Перед дужками мінус, усі мінуси змінюються на плюси: +x, +y, +z -> +++"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(2a - 3b - 4c)", "-++", "Перед дужками мінус: +2a -> -, -3b -> +, -4c -> + -> -++"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(5m - 2n + k)", "+-+", "Перед дужками плюс, знаки без змін: +5m (+), -2n (-), +k (+) -> +-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(-p - q + r)", "++-", "Перед дужками мінус: -p -> +, -q -> +, +r -> - -> ++-"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(x + y - z)", "++-", "Перед дужками плюс, знаки без змін: +x (+), +y (+), -z (-) -> ++-"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(m - n - k)", "-++", "Перед дужками мінус: +m -> -, -n -> +, -k -> + -> -++"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(-a + b + c)", "-++", "Перед дужками плюс: -a (-), +b (+), +c (+) -> -++"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(-3x + 2y - z)", "+-+", "Перед дужками мінус: -3x -> +, +2y -> -, -z -> + -> +-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(4p + 3q - 2r)", "++-", "Перед дужками плюс: +4p (+), +3q (+), -2r (-) -> ++-"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(a - b - c - d)", "-+++", "Перед дужками мінус: +a -> -, -b -> +, -c -> +, -d -> + -> -+++"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(-x - y + z)", "--+", "Перед дужками плюс: -x (-), -y (-), +z (+) -> --+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(-m + n - k)", "+-+", "Перед дужками мінус: -m -> +, +n -> -, -k -> + -> +-+"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n+(2a - b - c)", "+--", "Перед дужками плюс: +2a (+), -b (-), -c (-) -> +--"),
        ("Визначте послідовність знаків доданків при розкритті дужок:\n-(3x + 4y - 5z)", "--+", "Перед дужками мінус: +3x -> -, +4y -> -, -5z -> + -> --+")
    ]

    brackets_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": "sign_sequence",
            "correct_answer": ans,
            "options_json": None,
            "hint": hint
        }
        for order, (q_text, ans, hint) in enumerate(brackets_tasks_data, start=1)
    ]
    upsert_topic_tasks(db, brackets_topic.id, brackets_tasks)

    # 3. Combining Like Terms
    theory_combining_like_terms = """### 📖 Теоретичний матеріал: Зведення подібних доданків

#### Що таке подібні доданки?
Доданки, які мають **однакову буквену частину**, називаються **подібними доданками**.
> **Приклади:** `-4a` і `-3a`; `5x` і `-8x`; `12y` і `-15y`.

---

#### Правило зведення подібних доданків:
Щоб звести подібні доданки, треба:
1. **Додати їхні коефіцієнти**;
2. Результат помножити на спільну буквену частину.

> **Приклад 1:** `-4a - 3a = (-4 - 3)a = -7a`
> **Приклад 2:** `5x - 8x = (5 - 8)x = -3x`
> **Приклад 3:** `-2b + 9b = (-2 + 9)b = 7b`
> **Приклад 4:** `-a - a = (-1 - 1)a = -2a`
> **Приклад 5:** `-6c + 6c = (-6 + 6)c = 0`
"""

    terms_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-combining-like-terms").first()
    if not terms_topic:
        terms_topic = Topic(
            subject_id=subject.id,
            name="Зведення подібних доданків",
            slug="math-6-combining-like-terms",
            room_code="math-6-combining-like-terms",
            description="Спрощення буквених виразів шляхом зведення подібних доданків (наприклад, -4a - 3a = -7a).",
            theory_content=theory_combining_like_terms,
            sort_order=18
        )
        db.add(terms_topic)
        db.commit()
        db.refresh(terms_topic)
    else:
        terms_topic.name = "Зведення подібних доданків"
        terms_topic.room_code = "math-6-combining-like-terms"
        terms_topic.description = "Спрощення буквених виразів шляхом зведення подібних доданків (наприклад, -4a - 3a = -7a)."
        terms_topic.theory_content = theory_combining_like_terms
        terms_topic.sort_order = 18
        db.commit()

    terms_tasks_data = [
        ("Зведіть подібні доданки:\n-4a - 3a", "-7a", "Додайте коефіцієнти: (-4 - 3)a = -7a."),
        ("Зведіть подібні доданки:\n5x - 8x", "-3x", "Додайте коефіцієнти: (5 - 8)x = -3x."),
        ("Зведіть подібні доданки:\n-2b + 9b", "7b", "Додайте коефіцієнти: (-2 + 9)b = 7b."),
        ("Зведіть подібні доданки:\n-a - a", "-2a", "Додайте коефіцієнти: (-1 - 1)a = -2a."),
        ("Зведіть подібні доданки:\n12y - 15y", "-3y", "Додайте коефіцієнти: (12 - 15)y = -3y."),
        ("Зведіть подібні доданки:\n-6c + 6c", "0", "Сума протилежних коефіцієнтів (-6 + 6) дорівнює 0."),
        ("Зведіть подібні доданки:\n-10m - 4m", "-14m", "Додайте коефіцієнти: (-10 - 4)m = -14m."),
        ("Зведіть подібні доданки:\n7k - k", "6k", "Додайте коефіцієнти: (7 - 1)k = 6k."),
        ("Зведіть подібні доданки:\n-8p + 3p", "-5p", "Додайте коефіцієнти: (-8 + 3)p = -5p."),
        ("Зведіть подібні доданки:\n-3x + 3x", "0", "Сума протилежних коефіцієнтів (-3 + 3) дорівнює 0."),
        ("Зведіть подібні доданки:\n14a - 20a", "-6a", "Додайте коефіцієнти: (14 - 20)a = -6a."),
        ("Зведіть подібні доданки:\n-9b - b", "-10b", "Додайте коефіцієнти: (-9 - 1)b = -10b."),
        ("Зведіть подібні доданки:\n4c - 11c", "-7c", "Додайте коефіцієнти: (4 - 11)c = -7c."),
        ("Зведіть подібні доданки:\n-5y + 12y", "7y", "Додайте коефіцієнти: (-5 + 12)y = 7y."),
        ("Зведіть подібні доданки:\n-2n - 7n", "-9n", "Додайте коефіцієнти: (-2 - 7)n = -9n."),
        ("Зведіть подібні доданки:\n8x - 13x", "-5x", "Додайте коефіцієнти: (8 - 13)x = -5x."),
        ("Зведіть подібні доданки:\n-6a - 6a", "-12a", "Додайте коефіцієнти: (-6 - 6)a = -12a."),
        ("Зведіть подібні доданки:\n15m - 9m", "6m", "Додайте коефіцієнти: (15 - 9)m = 6m."),
        ("Зведіть подібні доданки:\n-t + 8t", "7t", "Додайте коефіцієнти: (-1 + 8)t = 7t."),
        ("Зведіть подібні доданки:\n-11z - 4z", "-15z", "Додайте коефіцієнти: (-11 - 4)z = -15z.")
    ]

    terms_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": "input_text",
            "correct_answer": ans,
            "options_json": None,
            "hint": hint
        }
        for order, (q_text, ans, hint) in enumerate(terms_tasks_data, start=1)
    ]
    upsert_topic_tasks(db, terms_topic.id, terms_tasks)

    # 4. Divisibility Rules (2, 3, 5, 9, 10)
    theory_divisibility = """### 📖 Теоретичний матеріал: Ознаки подільності чисел (на 2, 3, 5, 9, 10)

#### 1. Ознака подільності на 2:
На **2** діляться всі числа, запис яких закінчується **парною цифрою** (`0`, `2`, `4`, `6`, `8`).

#### 2. Ознака подільності на 5:
На **5** діляться всі числа, запис яких закінчується цифрою **`0`** або **`5`**.

#### 3. Ознака подільності на 10:
На **10** діляться всі числа, запис яких закінчується цифрою **`0`**.

#### 4. Ознака подільності на 3:
На **3** діляться тільки ті числа, **сума цифр** яких ділиться на 3.
> **Приклад:** число `123` ($1 + 2 + 3 = 6$, ділиться на 3) $\rightarrow$ ділиться на 3.

#### 5. Ознака подільності на 9:
На **9** діляться тільки ті числа, **сума цифр** яких ділиться на 9.
> **Приклад:** число `279` ($2 + 7 + 9 = 18$, ділиться на 9) $\rightarrow$ ділиться на 9.
"""

    div_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-divisibility").first()
    if not div_topic:
        div_topic = Topic(
            subject_id=subject.id,
            name="Ознаки подільності чисел (на 2, 3, 5, 9, 10)",
            slug="math-6-divisibility",
            room_code="math-6-divisibility",
            description="Застосування ознак подільності на 2, 3, 5, 9, 10 (тестові завдання з мультивибором варіантів).",
            theory_content=theory_divisibility,
            sort_order=19
        )
        db.add(div_topic)
        db.commit()
        db.refresh(div_topic)
    else:
        div_topic.name = "Ознаки подільності чисел (на 2, 3, 5, 9, 10)"
        div_topic.room_code = "math-6-divisibility"
        div_topic.description = "Застосування ознак подільності на 2, 3, 5, 9, 10 (тестові завдання з мультивибором варіантів)."
        div_topic.theory_content = theory_divisibility
        div_topic.sort_order = 19
        db.commit()

    div_tasks_data = [
        (1, "Виберіть усі числа, які діляться на 2 (закінчуються парною цифрою):", "A, C", [
            {"key": "A", "text": "148"}, {"key": "B", "text": "325"}, {"key": "C", "text": "710"}, {"key": "D", "text": "503"}
        ], "Числа 148 та 710 закінчуються парними цифрами 8 і 0."),

        (2, "Виберіть усі числа, які діляться на 5 (закінчуються на 0 або 5):", "A, B", [
            {"key": "A", "text": "230"}, {"key": "B", "text": "415"}, {"key": "C", "text": "612"}, {"key": "D", "text": "784"}
        ], "Числа 230 і 415 закінчуються на 0 та 5."),

        (3, "Виберіть усі числа, які діляться на 10 (закінчуються цифрою 0):", "A, C", [
            {"key": "A", "text": "450"}, {"key": "B", "text": "525"}, {"key": "C", "text": "1000"}, {"key": "D", "text": "304"}
        ], "Числа 450 і 1000 закінчуються на 0."),

        (4, "Виберіть усі числа, які діляться на 3 (сума цифр ділиться на 3):", "A, C", [
            {"key": "A", "text": "123 (1+2+3 = 6)"}, {"key": "B", "text": "241 (2+4+1 = 7)"}, {"key": "C", "text": "516 (5+1+6 = 12)"}, {"key": "D", "text": "305 (3+0+5 = 8)"}
        ], "Суми цифр чисел 123 (6) та 516 (12) діляться на 3."),

        (5, "Виберіть усі числа, які діляться на 9 (сума цифр ділиться на 9):", "A, B", [
            {"key": "A", "text": "279 (2+7+9 = 18)"}, {"key": "B", "text": "432 (4+3+2 = 9)"}, {"key": "C", "text": "502 (5+0+2 = 7)"}, {"key": "D", "text": "813 (8+1+3 = 12)"}
        ], "Суми цифр чисел 279 (18) та 432 (9) діляться на 9."),

        (6, "Які з чисел діляться і на 2, і на 5 (тобто діляться на 10 і закінчуються на 0)?", "A, C", [
            {"key": "A", "text": "340"}, {"key": "B", "text": "125"}, {"key": "C", "text": "890"}, {"key": "D", "text": "642"}
        ], "Числа 340 і 890 закінчуються на 0, тому діляться на 2 і на 5."),

        (7, "Які з чисел діляться на 3, але НЕ діляться на 9?", "A, C", [
            {"key": "A", "text": "111 (сума 3)"}, {"key": "B", "text": "234 (сума 9)"}, {"key": "C", "text": "312 (сума 6)"}, {"key": "D", "text": "414 (сума 9)"}
        ], "Числа 111 (сума 3) та 312 (сума 6) діляться на 3, але не діляться на 9."),

        (8, "Виберіть усі парні числа (діляться на 2):", "A, C", [
            {"key": "A", "text": "1024"}, {"key": "B", "text": "3117"}, {"key": "C", "text": "5688"}, {"key": "D", "text": "9001"}
        ], "Числа 1024 (зак. на 4) та 5688 (зак. на 8) є парними."),

        (9, "Виберіть усі числа, які діляться на 5, але НЕ діляться на 10 (закінчуються саме на 5):", "A, C", [
            {"key": "A", "text": "175"}, {"key": "B", "text": "420"}, {"key": "C", "text": "865"}, {"key": "D", "text": "900"}
        ], "Числа 175 та 865 закінчуються на 5, тому діляться на 5 і не діляться на 10."),

        (10, "Які з поданих чисел діляться на 3?", "A, C", [
            {"key": "A", "text": "702 (7+0+2 = 9)"}, {"key": "B", "text": "814 (8+1+4 = 13)"}, {"key": "C", "text": "945 (9+4+5 = 18)"}, {"key": "D", "text": "521 (5+2+1 = 8)"}
        ], "Суми цифр чисел 702 (9) і 945 (18) діляться на 3."),

        (11, "Які з поданих чисел діляться на 9?", "A, B, D", [
            {"key": "A", "text": "567 (5+6+7 = 18)"}, {"key": "B", "text": "189 (1+8+9 = 18)"}, {"key": "C", "text": "246 (2+4+6 = 12)"}, {"key": "D", "text": "333 (3+3+3 = 9)"}
        ], "Суми цифр чисел 567 (18), 189 (18) та 333 (9) діляться на 9."),

        (12, "Які з чисел одночасно діляться на 2 і на 3 (тобто діляться на 6):", "A, C", [
            {"key": "A", "text": "114 (парне, сума 6)"}, {"key": "B", "text": "225 (непарне)"}, {"key": "C", "text": "438 (парне, сума 15)"}, {"key": "D", "text": "502 (парне, сума 7)"}
        ], "Числа 114 і 438 є парними і їхні суми цифр діляться на 3."),

        (13, "Виберіть числа, остання цифра яких свідчить про подільність на 5:", "A, B, D", [
            {"key": "A", "text": "1205"}, {"key": "B", "text": "3410"}, {"key": "C", "text": "5678"}, {"key": "D", "text": "9025"}
        ], "Числа 1205, 3410 та 9025 закінчуються на 5 або 0."),

        (14, "Виберіть числа, сума цифр яких ділиться на 9:", "A, B", [
            {"key": "A", "text": "918 (9+1+8 = 18)"}, {"key": "B", "text": "738 (7+3+8 = 18)"}, {"key": "C", "text": "456 (4+5+6 = 15)"}, {"key": "D", "text": "129 (1+2+9 = 12)"}
        ], "Числа 918 та 738 мають суму цифр 18, яка ділиться на 9."),

        (15, "Які з чисел НЕ діляться на 2 (непарні числа):", "A, C", [
            {"key": "A", "text": "311"}, {"key": "B", "text": "428"}, {"key": "C", "text": "579"}, {"key": "D", "text": "640"}
        ], "Числа 311 (зак. на 1) та 579 (зак. на 9) є непарними."),

        (16, "Виберіть усі числа, що діляться на 10:", "A, C, D", [
            {"key": "A", "text": "2030"}, {"key": "B", "text": "4505"}, {"key": "C", "text": "7890"}, {"key": "D", "text": "1110"}
        ], "Числа 2030, 7890 та 1110 закінчуються цифрою 0."),

        (17, "Які з поданих чисел мають суму цифр, що ділиться на 3:", "A, B, D", [
            {"key": "A", "text": "321 (3+2+1 = 6)"}, {"key": "B", "text": "654 (6+5+4 = 15)"}, {"key": "C", "text": "112 (1+1+2 = 4)"}, {"key": "D", "text": "987 (9+8+7 = 24)"}
        ], "Суми цифр чисел 321 (6), 654 (15) та 987 (24) діляться на 3."),

        (18, "Які з чисел діляться на 5 і мають парну передостанню цифру:", "A, B, D", [
            {"key": "A", "text": "245 (передостання 4 - парна)"}, {"key": "B", "text": "360 (передостання 6 - парна)"}, {"key": "C", "text": "135 (передостання 3 - непарна)"}, {"key": "D", "text": "825 (передостання 2 - парна)"}
        ], "У числах 245 (4), 360 (6) та 825 (2) передостанні цифри є парними."),

        (19, "Виберіть числа, що діляться і на 3, і на 5 (тобто діляться на 15):", "A, B, D", [
            {"key": "A", "text": "135 (зак. на 5, сума 9)"}, {"key": "B", "text": "240 (зак. на 0, сума 6)"}, {"key": "C", "text": "305 (зак. на 5, сума 8)"}, {"key": "D", "text": "450 (зак. на 0, сума 9)"}
        ], "Числа 135, 240 та 450 закінчуються на 0 або 5 і їхні суми цифр діляться на 3."),

        (20, "Які з поданих чотирицифрових чисел діляться на 9:", "A, B, C", [
            {"key": "A", "text": "1233 (сума 9)"}, {"key": "B", "text": "5418 (сума 18)"}, {"key": "C", "text": "2007 (сума 9)"}, {"key": "D", "text": "1111 (сума 4)"}
        ], "Числа 1233 (9), 5418 (18) та 2007 (9) мають суми цифр, що діляться на 9.")
    ]

    div_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": "multichoice",
            "correct_answer": ans,
            "options_json": json.dumps(opts, ensure_ascii=False) if opts else None,
            "hint": hint
        }
        for order, q_text, ans, opts, hint in div_tasks_data
    ]
    upsert_topic_tasks(db, div_topic.id, div_tasks)

    # 5. Prime Factorization
    theory_prime_factorization = """### 📖 Теоретичний матеріал: Розкладання складених чисел на прості множники

#### Що таке прості та складені числа?
- **Просте число** — число, яке має рівно два дільники: одиницю і саме себе (`2, 3, 5, 7, 11, 13, 17, 19, 23...`).
- **Складене число** — число, яке має більше ніж два дільники.

---

#### Схема розкладання у стовпчик (від найменшого дільника до найбільшого):
Записують число, праворуч проводять вертикальну риску. Праворуч записують найменший простий дільник, а під числом — частку від ділення. Процес повторюють, поки не отримають 1:

```text
504 | 2   (504 : 2 = 252)
252 | 2   (252 : 2 = 126)
126 | 2   (126 : 2 = 63)
 63 | 3   (63 : 3 = 21)
 21 | 3   (21 : 3 = 7)
  7 | 7   (7 : 7 = 1)
  1
```
> **Канонічний розклад:** $504 = 2 \\times 2 \\times 2 \\times 3 \\times 3 \\times 7 = 2^3 \\times 3^2 \\times 7$.
"""

    factor_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-prime-factorization").first()
    if not factor_topic:
        factor_topic = Topic(
            subject_id=subject.id,
            name="Розкладання складених чисел на прості множники",
            slug="math-6-prime-factorization",
            room_code="math-6-prime-factorization",
            description="Розкладання складених чисел на прості множники у вигляді вертикальної схеми (наприклад, 504 = 2 * 2 * 2 * 3 * 3 * 7).",
            theory_content=theory_prime_factorization,
            sort_order=20
        )
        db.add(factor_topic)
        db.commit()
        db.refresh(factor_topic)
    else:
        factor_topic.name = "Розкладання складених чисел на прості множники"
        factor_topic.room_code = "math-6-prime-factorization"
        factor_topic.description = "Розкладання складених чисел на прості множники у вигляді вертикальної схеми (наприклад, 504 = 2 * 2 * 2 * 3 * 3 * 7)."
        factor_topic.theory_content = theory_prime_factorization
        factor_topic.sort_order = 20
        db.commit()

    factor_tasks_data = [
        (1, "Розкладіть складене число 504 на прості множники у стовпчик (вносьте прості дільники від меншого до більшого):\n504", "2, 2, 2, 3, 3, 7", "504 : 2 = 252; 252 : 2 = 126; 126 : 2 = 63; 63 : 3 = 21; 21 : 3 = 7; 7 : 7 = 1. Множники: 2, 2, 2, 3, 3, 7."),
        (2, "Розкладіть складене число 360 на прості множники у стовпчик (вносьте прості дільники від меншого до більшого):\n360", "2, 2, 2, 3, 3, 5", "360 : 2 = 180; 180 : 2 = 90; 90 : 2 = 45; 45 : 3 = 15; 15 : 3 = 5; 5 : 5 = 1. Множники: 2, 2, 2, 3, 3, 5."),
        (3, "Розкладіть складене число 420 на прості множники у стовпчик (вносьте прості дільники від меншого до більшого):\n420", "2, 2, 3, 5, 7", "420 : 2 = 210; 210 : 2 = 105; 105 : 3 = 35; 35 : 5 = 7; 7 : 7 = 1. Множники: 2, 2, 3, 5, 7."),
        (4, "Розкладіть складене число 210 на прості множники у стовпчик (вносьте прості дільники від меншого до більшого):\n210", "2, 3, 5, 7", "210 : 2 = 105; 105 : 3 = 35; 35 : 5 = 7; 7 : 7 = 1. Множники: 2, 3, 5, 7."),
        (5, "Розкладіть складене число 180 на прості множники у стовпчик (вносьте прості дільники від меншого до більшого):\n180", "2, 2, 3, 3, 5", "180 : 2 = 90; 90 : 2 = 45; 45 : 3 = 15; 15 : 3 = 5; 5 : 5 = 1. Множники: 2, 2, 3, 3, 5.")
    ]

    factor_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": "prime_factorization",
            "correct_answer": ans,
            "options_json": None,
            "hint": hint
        }
        for order, q_text, ans, hint in factor_tasks_data
    ]
    upsert_topic_tasks(db, factor_topic.id, factor_tasks)

    # 5.1. GCD and LCM (НСД та НСК)
    theory_gcd_lcm = """### 📖 Теоретичний матеріал: Найбільший спільний дільник (НСД) та найменше спільне кратне (НСК)

#### 1. Дільники та спільні дільники
- **Дільник** числа $a$ — це натуральне число, на яке число $a$ ділиться без остачі.
- **Спільний дільник** кількох чисел — це число, яке є дільником кожного з цих чисел.
> **Приклад:** для чисел $18$ і $24$:
> - Дільники $18$: $\{1, 2, 3, 6, 9, 18\}$
> - Дільники $24$: $\{1, 2, 3, 4, 6, 8, 12, 24\}$
> - **Спільні дільники:** $\{1, 2, 3, 6\}$.

---

#### 2. Найбільший спільний дільник (НСД)
- **НСД** кількох чисел — це найбільше натуральне число, на яке ділиться кожне з даних чисел.
- **Правило знаходження НСД за допомогою розкладання на прості множники:**
  1. Розкласти дані числа на прості множники.
  2. Знайти спільні прості множники в усіх розкладах.
  3. Перемножити ці спільні прості множники.
> **Приклад:** Знайти $\\text{НСД}(72, 96)$:
> - $72 = 2 \\times 2 \\times 2 \\times 3 \\times 3 = 2^3 \\times 3^2$
> - $96 = 2 \\times 2 \\times 2 \\times 2 \\times 2 \\times 3 = 2^5 \\times 3$
> - Спільні множники: $2, 2, 2, 3$.
> - $\\text{НСД}(72, 96) = 2 \\times 2 \\times 2 \\times 3 = 24$.

---

#### 3. Взаємно прості числа
- Два натуральних числа називають **взаємно простими**, якщо їхній найбільший спільний дільник дорівнює $1$:
  $$\\text{НСД}(a, b) = 1$$
- Будь-які два послідовні натуральні числа $n$ та $n+1$ є взаємно простими (наприклад, $14$ і $15$, $35$ і $36$).
- Приклади: $\\text{НСД}(8, 9) = 1$, $\\text{НСД}(10, 21) = 1$, $\\text{НСД}(21, 25) = 1$.

---

#### 4. Кратні числа та найменше спільне кратне (НСК)
- **Кратним** до числа $a$ називають число, яке ділиться на $a$ націло.
- **НСК** кількох чисел — це найменше натуральне число, яке ділиться на кожне з даних чисел.
- **Правило знаходження НСК:**
  1. Розкласти кожне число на прості множники.
  2. Записати розклад одного з чисел (найкраще найбільшого).
  3. Дописати до нього ті прості множники з розкладів інших чисел, яких немає у виписаному розкладі.
  4. Обчислити добуток отриманих множників.
> **Приклад 1 (два числа):** Знайти $\\text{НСК}(28, 42)$:
> - $28 = 2 \\times 2 \\times 7$
> - $42 = 2 \\times 3 \\times 7$
> - $\\text{НСК}(28, 42) = (2 \\times 2 \\times 7) \\times 3 = 28 \\times 3 = 84$.
>
> **Приклад 2 (три числа):** Знайти $\\text{НСК}(12, 15, 18)$:
> - $12 = 2^2 \\times 3$
> - $15 = 3 \\times 5$
> - $18 = 2 \\times 3^2$
> - $\\text{НСК}(12, 15, 18) = 2^2 \\times 3^2 \\times 5 = 4 \\times 9 \\times 5 = 180$.
"""

    gcd_lcm_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-gcd-lcm").first()
    if not gcd_lcm_topic:
        gcd_lcm_topic = Topic(
            subject_id=subject.id,
            name="Найбільший спільний дільник (НСД) та найменше спільне кратне (НСК)",
            slug="math-6-gcd-lcm",
            room_code="math-6-gcd-lcm",
            description="Спільні дільники, кратні чисел, взаємно прості числа, знаходження НСД та НСК для двох і трьох чисел.",
            theory_content=theory_gcd_lcm,
            sort_order=21
        )
        db.add(gcd_lcm_topic)
        db.commit()
        db.refresh(gcd_lcm_topic)
    else:
        gcd_lcm_topic.name = "Найбільший спільний дільник (НСД) та найменше спільне кратне (НСК)"
        gcd_lcm_topic.room_code = "math-6-gcd-lcm"
        gcd_lcm_topic.description = "Спільні дільники, кратні чисел, взаємно прості числа, знаходження НСД та НСК для двох і трьох чисел."
        gcd_lcm_topic.theory_content = theory_gcd_lcm
        gcd_lcm_topic.sort_order = 21
        db.commit()

    gcd_lcm_tasks_data = [
        # 1 - 3. Обрати спільні дільники для двох чисел (мультиопція)
        {
            "task_order": 1,
            "question": "Оберіть усі спільні дільники для чисел 18 і 24:",
            "task_type": "multichoice",
            "correct_answer": "A, B, D",
            "options_json": json.dumps([
                {"key": "A", "text": "2"},
                {"key": "B", "text": "3"},
                {"key": "C", "text": "4"},
                {"key": "D", "text": "6"},
                {"key": "E", "text": "9"}
            ], ensure_ascii=False),
            "hint": "Дільники 18: {1, 2, 3, 6, 9, 18}. Дільники 24: {1, 2, 3, 4, 6, 8, 12, 24}. Спільними дільниками серед варіантів є 2, 3 та 6."
        },
        {
            "task_order": 2,
            "question": "Оберіть усі спільні дільники для чисел 30 і 45:",
            "task_type": "multichoice",
            "correct_answer": "A, B, E",
            "options_json": json.dumps([
                {"key": "A", "text": "3"},
                {"key": "B", "text": "5"},
                {"key": "C", "text": "6"},
                {"key": "D", "text": "9"},
                {"key": "E", "text": "15"}
            ], ensure_ascii=False),
            "hint": "Дільники 30: {1, 2, 3, 5, 6, 10, 15, 30}. Дільники 45: {1, 3, 5, 9, 15, 45}. Спільними є 3, 5 та 15."
        },
        {
            "task_order": 3,
            "question": "Оберіть усі спільні дільники для чисел 48 і 72:",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, E",
            "options_json": json.dumps([
                {"key": "A", "text": "4"},
                {"key": "B", "text": "6"},
                {"key": "C", "text": "8"},
                {"key": "D", "text": "16"},
                {"key": "E", "text": "24"}
            ], ensure_ascii=False),
            "hint": "Спільні дільники чисел 48 і 72: 1, 2, 3, 4, 6, 8, 12, 24. Число 16 ділить 48, але не ділить 72."
        },

        # 4. Обрати спільні дільники для трьох чисел (мультиопція)
        {
            "task_order": 4,
            "question": "Оберіть усі спільні дільники для трьох чисел 24, 36 і 60:",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, E",
            "options_json": json.dumps([
                {"key": "A", "text": "2"},
                {"key": "B", "text": "3"},
                {"key": "C", "text": "4"},
                {"key": "D", "text": "8"},
                {"key": "E", "text": "12"}
            ], ensure_ascii=False),
            "hint": "Спільні дільники чисел 24, 36 і 60 — це числа, на які діляться всі три числа одночасно: 1, 2, 3, 4, 6, 12."
        },

        # 5 - 8. Обрати кратні до числа (мультиопція)
        {
            "task_order": 5,
            "question": "Оберіть усі числа, які є кратними до числа 6:",
            "task_type": "multichoice",
            "correct_answer": "A, B, D",
            "options_json": json.dumps([
                {"key": "A", "text": "18"},
                {"key": "B", "text": "24"},
                {"key": "C", "text": "32"},
                {"key": "D", "text": "42"},
                {"key": "E", "text": "56"}
            ], ensure_ascii=False),
            "hint": "Число є кратним до 6, якщо воно ділиться на 6 без остачі. 18 : 6 = 3, 24 : 6 = 4, 42 : 6 = 7."
        },
        {
            "task_order": 6,
            "question": "Оберіть усі числа, які є кратними до числа 8:",
            "task_type": "multichoice",
            "correct_answer": "A, C, D",
            "options_json": json.dumps([
                {"key": "A", "text": "16"},
                {"key": "B", "text": "28"},
                {"key": "C", "text": "40"},
                {"key": "D", "text": "56"},
                {"key": "E", "text": "68"}
            ], ensure_ascii=False),
            "hint": "Кратні числа 8 діляться на 8 націло: 16 (8·2), 40 (8·5), 56 (8·7)."
        },
        {
            "task_order": 7,
            "question": "Оберіть усі числа, які є кратними до числа 12:",
            "task_type": "multichoice",
            "correct_answer": "A, B, D",
            "options_json": json.dumps([
                {"key": "A", "text": "24"},
                {"key": "B", "text": "36"},
                {"key": "C", "text": "44"},
                {"key": "D", "text": "60"},
                {"key": "E", "text": "80"}
            ], ensure_ascii=False),
            "hint": "Числа 24 (12·2), 36 (12·3) та 60 (12·5) діляться на 12 без остачі."
        },
        {
            "task_order": 8,
            "question": "Оберіть усі числа, які є кратними до числа 15:",
            "task_type": "multichoice",
            "correct_answer": "A, B, D, E",
            "options_json": json.dumps([
                {"key": "A", "text": "30"},
                {"key": "B", "text": "45"},
                {"key": "C", "text": "55"},
                {"key": "D", "text": "75"},
                {"key": "E", "text": "90"}
            ], ensure_ascii=False),
            "hint": "Кратні до 15 діляться на 15 без остачі: 30, 45, 75, 90. Число 55 на 15 не ділиться націло."
        },

        # 9 - 10. Знайди всі взаємно прості числа (для кожної пари НСД = 1)
        {
            "task_order": 9,
            "question": "Серед поданих пар чисел оберіть усі пари взаємно простих чисел (у яких НСД = 1):",
            "task_type": "multichoice",
            "correct_answer": "A, B, D",
            "options_json": json.dumps([
                {"key": "A", "text": "14 і 15"},
                {"key": "B", "text": "8 і 9"},
                {"key": "C", "text": "12 і 18"},
                {"key": "D", "text": "21 і 25"},
                {"key": "E", "text": "15 і 35"}
            ], ensure_ascii=False),
            "hint": "Взаємно прості числа не мають спільних дільників, крім 1:\n- НСД(14, 15) = 1 (взаємно прості)\n- НСД(8, 9) = 1 (взаємно прості)\n- НСД(12, 18) = 6\n- НСД(21, 25) = 1 (взаємно прості)\n- НСД(15, 35) = 5"
        },
        {
            "task_order": 10,
            "question": "Серед поданих пар чисел оберіть усі пари взаємно простих чисел (у яких НСД = 1):",
            "task_type": "multichoice",
            "correct_answer": "A, B, D",
            "options_json": json.dumps([
                {"key": "A", "text": "10 і 21"},
                {"key": "B", "text": "16 і 27"},
                {"key": "C", "text": "14 і 49"},
                {"key": "D", "text": "35 і 36"},
                {"key": "E", "text": "22 і 33"}
            ], ensure_ascii=False),
            "hint": "Перевіримо НСД для кожної пари:\n- НСД(10, 21) = 1 (взаємно прості)\n- НСД(16, 27) = 1 (взаємно прості)\n- НСД(14, 49) = 7\n- НСД(35, 36) = 1 (два послідовні числа завжди взаємно прості)\n- НСД(22, 33) = 11"
        },

        # 11. Знайди НСД двох чисел (зі схемами розкладання для всіх чисел)
        {
            "task_order": 11,
            "question": "Знайдіть найбільший спільний дільник (НСД) чисел 72 і 96.\nРозкладіть кожне число на прості множники за допомогою схеми та введіть спільні множники або значення НСД(72, 96):",
            "task_type": "prime_factorization",
            "correct_answer": "24 | 2, 2, 2, 3 | 2*2*2*3 | 24",
            "options_json": json.dumps({"numbers": [72, 96]}, ensure_ascii=False),
            "hint": "Розклади чисел:\n72 = 2 · 2 · 2 · 3 · 3\n96 = 2 · 2 · 2 · 2 · 2 · 3\nСпільні прості множники: 2, 2, 2, 3. НСД(72, 96) = 2 · 2 · 2 · 3 = 24."
        },

        # 12. Знайди НСД трьох чисел (зі схемами розкладання для всіх чисел)
        {
            "task_order": 12,
            "question": "Знайдіть найбільший спільний дільник (НСД) трьох чисел: 36, 54 і 72.\nРозкладіть кожне число на прості множники за допомогою схеми та введіть спільні множники або значення НСД(36, 54, 72):",
            "task_type": "prime_factorization",
            "correct_answer": "18 | 2, 3, 3 | 2*3*3 | 18",
            "options_json": json.dumps({"numbers": [36, 54, 72]}, ensure_ascii=False),
            "hint": "Розкладемо числа на прості множники:\n36 = 2 · 2 · 3 · 3\n54 = 2 · 3 · 3 · 3\n72 = 2 · 2 · 2 · 3 · 3\nСпільні прості множники для всіх трьох чисел: 2, 3, 3. Отже, НСД(36, 54, 72) = 2 · 3 · 3 = 18."
        },

        # 13. Знайди НСК двох чисел (зі схемами розкладання для всіх чисел)
        {
            "task_order": 13,
            "question": "Знайдіть найменше спільне кратне (НСК) двох чисел: 28 і 42.\nРозкладіть кожне число на прості множники за допомогою схеми та введіть множники або значення НСК(28, 42):",
            "task_type": "prime_factorization",
            "correct_answer": "84 | 2, 2, 3, 7 | 2*2*3*7 | 84",
            "options_json": json.dumps({"numbers": [28, 42]}, ensure_ascii=False),
            "hint": "Розклади:\n28 = 2 · 2 · 7\n42 = 2 · 3 · 7\nБеремо розклад 28 (2 · 2 · 7) і додаємо множник 3 з розкладу 42: НСК(28, 42) = 2 · 2 · 7 · 3 = 84."
        },

        # 14. Знайди НСК трьох чисел (зі схемами розкладання для всіх чисел)
        {
            "task_order": 14,
            "question": "Знайдіть найменше спільне кратне (НСК) трьох чисел: 12, 15 і 18.\nРозкладіть кожне число на прості множники за допомогою схеми та введіть множники або значення НСК(12, 15, 18):",
            "task_type": "prime_factorization",
            "correct_answer": "180 | 2, 2, 3, 3, 5 | 2*2*3*3*5 | 180",
            "options_json": json.dumps({"numbers": [12, 15, 18]}, ensure_ascii=False),
            "hint": "Розклади:\n12 = 2 · 2 · 3 = 2² · 3\n15 = 3 · 5\n18 = 2 · 3 · 3 = 2 · 3²\nБеремо кожен простий множник з найбільшим показником: 2² · 3² · 5 = 4 · 9 · 5 = 180. Отже, НСК(12, 15, 18) = 180."
        }
    ]

    upsert_topic_tasks(db, gcd_lcm_topic.id, gcd_lcm_tasks_data)

    # 6. 6th Grade Math Control Work (Підсумкова контрольна робота за 6 клас)
    theory_control_work = """### 📝 Підсумкова контрольна робота з математики (6 клас)

---

#### 1. Цілі числа та їх класифікація:
- **Множина цілих чисел ($\mathbb{Z}$)** складається з натуральних (додатних) чисел ($1, 2, 3...$), протилежних їм чисел ($-1, -2, -3...$) та числа $0$.
- **Дробові числа** (десяткові дроби $3.4, -2.8$ або звичайні дроби $\\frac{5}{9}$) **не є цілими числами**.

---

#### 2. Модуль числа:
- **Модуль числа $|a|$** — це відстань від початку відліку до точки $a$ на координатній прямій.
- $|a| = a$, якщо $a \\ge 0$; $|-a| = a$, якщо $a < 0$.
- **Приклад:** $|-15| = 15$, $|9| = 9$, $|0| = 0$.

---

#### 3. Координатна пряма:
- **Координатна пряма** — це пряма з вибраним на ній початком відліку $O(0)$, одиничним відрізком і вказаним додатним напрямком (стрілкою праворуч).
- **Координата точки** показує положення точки на прямій. Додатні числа розташовані праворуч від $0$, від'ємні — ліворуч.
- **Середина відрізка:** Якщо кінці відрізка мають координати $x_A$ та $x_B$, то координата середини $C$ обчислюється як півсума:
  $$x_C = \\frac{x_A + x_B}{2}$$

---

#### 4. Правила дій з цілими числами:
- **Додавання чисел з однаковими знаками:** додати їх модулі й поставити їх спільний знак:
  $$(-14) + (-5) = -(14 + 5) = -19$$
- **Додавання чисел з різними знаками:** від більшого модуля відняти менший і поставити знак доданка з більшим модулем:
  $$(-8) + 15 = +(15 - 8) = 7$$
- **Віднімання:** до зменшуваного додати число, протилежне від'ємнику:
  $$a - b = a + (-b) \\implies 6 - 19 = 6 + (-19) = -13$$
  $$(-11) - (-16) = (-11) + 16 = 5$$
- **Множення та ділення:**
  - Добуток/частка чисел з однаковими знаками є додатним ($+ \\cdot + = +$, $- \\cdot - = +$):
    $$(-6) \\cdot (-9) = 54$$
  - Добуток/частка чисел з різними знаками є від'ємним ($+ \\cdot - = -$, $- \\cdot + = -$):
    $$(-7) \\cdot 8 = -56, \\quad (-45) : 5 = -9$$

---

#### 5. Прямокутник на координатній площині:
- Кожна точка на площині задається парою координат $(x, y)$, де $x$ — абсциса (по горизонталі), $y$ — ордината (по вертикалі).
- Для прямокутника зі сторонами, паралельними осям, довжина сторони дорівнює модулю різниці відповідних координат:
  $$a = |x_2 - x_1|, \\quad b = |y_2 - y_1|$$
- **Периметр:** $P = 2 \\cdot (a + b)$
- **Площа:** $S = a \\cdot b$
"""

    control_topic = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-control-1").first()
    if not control_topic:
        control_topic = Topic(
            subject_id=subject.id,
            name="Контрольна робота. Раціональні числа, координатна пряма та площина",
            slug="math-6-control-1",
            room_code="math-6-control-1",
            description="Підсумкова контрольна робота за 6 клас: вибір цілих чисел, робота з координатною прямою (позначення точок, визначення координат, середина відрізка), дії з цілими числами та модулем, побудова прямокутника на координатній площині (периметр і площа).",
            theory_content=theory_control_work,
            sort_order=21
        )
        db.add(control_topic)
        db.commit()
        db.refresh(control_topic)
    else:
        control_topic.name = "Контрольна робота. Раціональні числа, координатна пряма та площина"
        control_topic.room_code = "math-6-control-1"
        control_topic.description = "Підсумкова контрольна робота за 6 клас: вибір цілих чисел, робота з координатною прямою (позначення точок, визначення координат, середина відрізка), дії з цілими числами та модулем, побудова прямокутника на координатній площині (периметр і площа)."
        control_topic.theory_content = theory_control_work
        control_topic.sort_order = 21
        db.commit()

    control_tasks_data = [
        # 1. Choose integers (multichoice with 10 options)
        {
            "task_order": 1,
            "question": "Виберіть усі цілі числа серед наведених 10 варіантів (можна обрати декілька):",
            "task_type": "multichoice",
            "correct_answer": "A, C, D, F, H, J",
            "options_json": json.dumps([
                {"key": "A", "text": "-7"},
                {"key": "B", "text": "3.4"},
                {"key": "C", "text": "0"},
                {"key": "D", "text": "-15"},
                {"key": "E", "text": "5/9"},
                {"key": "F", "text": "18"},
                {"key": "G", "text": "-2.8"},
                {"key": "H", "text": "-40"},
                {"key": "I", "text": "6.12"},
                {"key": "J", "text": "9"}
            ], ensure_ascii=False),
            "hint": "Цілі числа — це натуральні числа (додатні), протилежні їм від'ємні числа та число 0. Дробові числа (3.4, 5/9, -2.8, 6.12) не є цілими."
        },
        # 2-4. Indicate coordinate on number line (3 tasks)
        {
            "task_order": 2,
            "question": "Позначте на координатній прямій точку A з координатою -4. Натисніть на відповідну точку на прямій та підтвердіть вибір:",
            "task_type": "number_line_point",
            "correct_answer": "-4",
            "options_json": json.dumps({"target_point": "A", "target_coord": -4}, ensure_ascii=False),
            "hint": "Знайдіть позначку -4 (ліворуч від 0 на 4 одиничних відрізки) та натисніть на неї."
        },
        {
            "task_order": 3,
            "question": "Позначте на координатній прямій точку B з координатою 3. Натисніть на відповідну точку на прямій та підтвердіть вибір:",
            "task_type": "number_line_point",
            "correct_answer": "3",
            "options_json": json.dumps({"target_point": "B", "target_coord": 3}, ensure_ascii=False),
            "hint": "Знайдіть позначку +3 (праворуч від 0 на 3 одиничних відрізки) та натисніть на неї."
        },
        {
            "task_order": 4,
            "question": "Позначте на координатній прямій точку C з координатою -6. Натисніть на відповідну точку на прямій та підтвердіть вибір:",
            "task_type": "number_line_point",
            "correct_answer": "-6",
            "options_json": json.dumps({"target_point": "C", "target_coord": -6}, ensure_ascii=False),
            "hint": "Знайдіть позначку -6 (ліворуч від 0 на 6 одиничних відрізків) та натисніть на неї."
        },
        # 5-7. What is the coordinate of point (3 tasks)
        {
            "task_order": 5,
            "question": "Яка координата точки K, позначеної на координатній прямій? Введіть її числове значення:",
            "task_type": "number_line_read",
            "correct_answer": "-5",
            "options_json": json.dumps({"point_name": "K", "point_coord": -5}, ensure_ascii=False),
            "hint": "Точка K розташована ліворуч від початку відліку 0 на 5 одиниць, отже її координата дорівнює -5."
        },
        {
            "task_order": 6,
            "question": "Яка координата точки M, позначеної на координатній прямій? Введіть її числове значення:",
            "task_type": "number_line_read",
            "correct_answer": "4",
            "options_json": json.dumps({"point_name": "M", "point_coord": 4}, ensure_ascii=False),
            "hint": "Точка M розташована праворуч від початку відліку 0 на 4 одиниці, отже її координата дорівнює 4."
        },
        {
            "task_order": 7,
            "question": "Яка координата точки P, позначеної на координатній прямій? Введіть її числове значення:",
            "task_type": "number_line_read",
            "correct_answer": "-2",
            "options_json": json.dumps({"point_name": "P", "point_coord": -2}, ensure_ascii=False),
            "hint": "Точка P розташована ліворуч від початку відліку 0 на 2 одиниці, отже її координата дорівнює -2."
        },
        # 8. Midpoint of segment on number line
        {
            "task_order": 8,
            "question": "Знайдіть координату середини відрізка AB на координатній прямій, якщо A(-7) і B(3). Введіть координату середини:",
            "task_type": "number_line_midpoint",
            "correct_answer": "-2",
            "options_json": json.dumps({"pointA": {"name": "A", "coord": -7}, "pointB": {"name": "B", "coord": 3}}, ensure_ascii=False),
            "hint": "Координата середини відрізка дорівнює півсумі координат його кінців: (-7 + 3) / 2 = -4 / 2 = -2."
        },
        # 9-16. 8 arithmetic tasks with integers (-10..10 / addition-subtraction -20..20, one module)
        {
            "task_order": 9,
            "question": "Обчисліть: (-14) + (-5) = ?",
            "task_type": "input_number",
            "correct_answer": "-19",
            "options_json": None,
            "hint": "Щоб додати два від'ємних числа, додайте їх модулі та поставте знак мінус: -(14 + 5) = -19."
        },
        {
            "task_order": 10,
            "question": "Обчисліть: (-8) + 15 = ?",
            "task_type": "input_number",
            "correct_answer": "7",
            "options_json": None,
            "hint": "Додавання чисел з різними знаками: від більшого модуля віднімаємо менший: +(15 - 8) = 7."
        },
        {
            "task_order": 11,
            "question": "Обчисліть: 6 - 19 = ?",
            "task_type": "input_number",
            "correct_answer": "-13",
            "options_json": None,
            "hint": "6 - 19 = 6 + (-19) = -(19 - 6) = -13."
        },
        {
            "task_order": 12,
            "question": "Обчисліть: (-11) - (-16) = ?",
            "task_type": "input_number",
            "correct_answer": "5",
            "options_json": None,
            "hint": "Віднімання замінюємо додаванням протилежного: (-11) + 16 = 16 - 11 = 5."
        },
        {
            "task_order": 13,
            "question": "Обчисліть: (-7) · 8 = ?",
            "task_type": "input_number",
            "correct_answer": "-56",
            "options_json": None,
            "hint": "Добуток чисел з різними знаками є від'ємним: -(7 · 8) = -56."
        },
        {
            "task_order": 14,
            "question": "Обчисліть: (-6) · (-9) = ?",
            "task_type": "input_number",
            "correct_answer": "54",
            "options_json": None,
            "hint": "Добуток двох від'ємних чисел є додатним: + (6 · 9) = 54."
        },
        {
            "task_order": 15,
            "question": "Обчисліть: (-45) : 5 = ?",
            "task_type": "input_number",
            "correct_answer": "-9",
            "options_json": None,
            "hint": "Частка чисел з різними знаками є від'ємною: -(45 : 5) = -9."
        },
        {
            "task_order": 16,
            "question": "Обчисліть значення виразу з модулем: |-15| + |-9| = ?",
            "task_type": "input_number",
            "correct_answer": "24",
            "options_json": None,
            "hint": "Модуль від'ємного числа є числом додатним: |-15| = 15, |-9| = 9. 15 + 9 = 24."
        },
        # 17. Rectangle on coordinate plane, plot points, enter perimeter and area
        {
            "task_order": 17,
            "question": "Побудуйте на координатній площині прямокутник ABCD за координатами його вершин: A(-3, -2), B(3, -2), C(3, 2), D(-3, 2). Поставте 4 точки на координатній площині, після чого обчисліть і введіть периметр (P) та площу (S) прямокутника:",
            "task_type": "coordinate_plane_rect",
            "correct_answer": "P=20, S=24|P=20; S=24|20, 24|20; 24|P:20, S:24|P=20 S=24|20 24",
            "options_json": json.dumps({
                "vertices": [
                    {"name": "A", "x": -3, "y": -2},
                    {"name": "B", "x": 3, "y": -2},
                    {"name": "C", "x": 3, "y": 2},
                    {"name": "D", "x": -3, "y": 2}
                ],
                "expected_perimeter": 20,
                "expected_area": 24
            }, ensure_ascii=False),
            "hint": "Довжини сторін прямокутника: ширина AB = 3 - (-3) = 6, висота BC = 2 - (-2) = 4. Периметр P = 2 · (6 + 4) = 20, площа S = 6 · 4 = 24."
        }
    ]

    upsert_topic_tasks(db, control_topic.id, control_tasks_data)

    # 7. 6th Grade Math Control Work 2 (Контрольна робота №2 з математики для 6 класу)
    theory_control_work_2 = """### 📝 Контрольна робота №2 з математики (6 клас)

---

#### 1. Арифметичні дії з цілими числами:
- **Додавання з однаковими знаками:** додаємо модулі і зберігаємо спільний знак.
  $$(-11) + (-7) = -(11 + 7) = -18$$
- **Додавання з різними знаками:** від більшого модуля віднімаємо менший і ставимо знак доданка з більшим модулем.
  $$(-14) + 9 = -(14 - 9) = -5, \\quad (-6) + 15 = +(15 - 6) = 9$$
- **Віднімання:** додаємо число, протилежне від'ємнику ($a - b = a + (-b)$).
  $$7 - 18 = 7 + (-18) = -11, \\quad (-9) - (-14) = (-9) + 14 = 5$$
- **Множення та ділення:**
  - Однаковий знак ($+ \\cdot +$, $- \\cdot -$, $- : -$): результат **додатний**.
    $$(-9) \\cdot (-4) = 36, \\quad (-45) : (-9) = 5$$
  - Різні знаки ($+ \\cdot -$, $- \\cdot +$, $+ : -$, $- : +$): результат **від'ємний**.
    $$(-6) \\cdot 7 = -42, \\quad 42 : (-6) = -7$$

---

#### 2. Рівняння з модулем виду $|ax + b| = c$:
Модуль числа — це відстань на координатній прямій, тому якщо $c > 0$, рівняння розпадається на два лінійних рівняння:
$$ax + b = c \\quad \\text{або} \\quad ax + b = -c$$

**Приклад розв'язання:**
Розв'язати рівняння: $|2x - 4| = 8$
1) Перший випадок:
   $$2x - 4 = 8 \\implies 2x = 8 + 4 \\implies 2x = 12 \\implies x = 6$$
2) Другий випадок:
   $$2x - 4 = -8 \\implies 2x = -8 + 4 \\implies 2x = -4 \\implies x = -2$$
**Відповідь:** $6; -2$ (або $-2; 6$).

---

#### 3. Рівняння, в яких добуток дорівнює нулю виду $(ax + b)(cx + d) = 0$:
Добуток двох або кількох множників дорівнює нулю тоді і тільки тоді, коли **хоча б один із множників дорівнює нулю**:
$$ax + b = 0 \\quad \\text{або} \\quad cx + d = 0$$

**Приклад розв'язання:**
Розв'язати рівняння: $(x - 5)(3x + 9) = 0$
1) Перший множник дорівнює нулю:
   $$x - 5 = 0 \\implies x = 5$$
2) Другий множник дорівнює нулю:
   $$3x + 9 = 0 \\implies 3x = -9 \\implies x = -3$$
**Відповідь:** $5; -3$ (або $-3; 5$).

---

#### 4. Практичні задачі з від'ємними числами (температура, баланс рахунку):
- Зниження температури або витрати грошей позначаються зі знаком «мінус» (віднімання).
- Підвищення температури або поповнення рахунку позначаються зі знаком «плюс» (додавання).
"""

    control_topic_2 = db.query(Topic).filter_by(subject_id=subject.id, slug="math-6-control-2").first()
    if not control_topic_2:
        control_topic_2 = Topic(
            subject_id=subject.id,
            name="Контрольна робота №2. Раціональні числа та рівняння",
            slug="math-6-control-2",
            room_code="math-6-control-2",
            description="Контрольна робота №2 для 6 класу: 20 завдань на додавання, віднімання, множення та ділення цілих чисел, рівняння з модулем, рівняння де добуток дорівнює 0, та практична задача з від'ємними числами.",
            theory_content=theory_control_work_2,
            sort_order=22
        )
        db.add(control_topic_2)
        db.commit()
        db.refresh(control_topic_2)
    else:
        control_topic_2.name = "Контрольна робота №2. Раціональні числа та рівняння"
        control_topic_2.room_code = "math-6-control-2"
        control_topic_2.description = "Контрольна робота №2 для 6 класу: 20 завдань на додавання, віднімання, множення та ділення цілих чисел, рівняння з модулем, рівняння де добуток дорівнює 0, та практична задача з від'ємними числами."
        control_topic_2.theory_content = theory_control_work_2
        control_topic_2.sort_order = 22
        db.commit()

    control_2_tasks_data = [
        # Tasks 1-20: Simple arithmetic operations on integers (-10..10 / addition-subtraction -20..20)
        {
            "task_order": 1,
            "question": "Обчисліть: (-11) + (-7) = ?",
            "task_type": "input_number",
            "correct_answer": "-18",
            "options_json": None,
            "hint": "Щоб додати два від'ємних числа, додайте їх модулі і поставте знак мінус: -(11 + 7) = -18."
        },
        {
            "task_order": 2,
            "question": "Обчисліть: (-14) + 9 = ?",
            "task_type": "input_number",
            "correct_answer": "-5",
            "options_json": None,
            "hint": "Додавання чисел з різними знаками: від більшого модуля віднімаємо менший: -(14 - 9) = -5."
        },
        {
            "task_order": 3,
            "question": "Обчисліть: 8 + (-19) = ?",
            "task_type": "input_number",
            "correct_answer": "-11",
            "options_json": None,
            "hint": "8 + (-19) = -(19 - 8) = -11."
        },
        {
            "task_order": 4,
            "question": "Обчисліть: (-6) + 15 = ?",
            "task_type": "input_number",
            "correct_answer": "9",
            "options_json": None,
            "hint": "(-6) + 15 = +(15 - 6) = 9."
        },
        {
            "task_order": 5,
            "question": "Обчисліть: (-12) + (-8) = ?",
            "task_type": "input_number",
            "correct_answer": "-20",
            "options_json": None,
            "hint": "-(12 + 8) = -20."
        },
        {
            "task_order": 6,
            "question": "Обчисліть: 13 + (-6) = ?",
            "task_type": "input_number",
            "correct_answer": "7",
            "options_json": None,
            "hint": "13 + (-6) = 13 - 6 = 7."
        },
        {
            "task_order": 7,
            "question": "Обчисліть: 7 - 18 = ?",
            "task_type": "input_number",
            "correct_answer": "-11",
            "options_json": None,
            "hint": "7 - 18 = 7 + (-18) = -(18 - 7) = -11."
        },
        {
            "task_order": 8,
            "question": "Обчисліть: (-9) - (-14) = ?",
            "task_type": "input_number",
            "correct_answer": "5",
            "options_json": None,
            "hint": "Віднімання замінюємо додаванням протилежного: (-9) + 14 = 14 - 9 = 5."
        },
        {
            "task_order": 9,
            "question": "Обчисліть: (-13) - 6 = ?",
            "task_type": "input_number",
            "correct_answer": "-19",
            "options_json": None,
            "hint": "(-13) - 6 = (-13) + (-6) = -19."
        },
        {
            "task_order": 10,
            "question": "Обчисліть: 5 - (-12) = ?",
            "task_type": "input_number",
            "correct_answer": "17",
            "options_json": None,
            "hint": "5 - (-12) = 5 + 12 = 17."
        },
        {
            "task_order": 11,
            "question": "Обчисліть: (-15) - (-8) = ?",
            "task_type": "input_number",
            "correct_answer": "-7",
            "options_json": None,
            "hint": "(-15) - (-8) = (-15) + 8 = -(15 - 8) = -7."
        },
        {
            "task_order": 12,
            "question": "Обчисліть: (-4) - 16 = ?",
            "task_type": "input_number",
            "correct_answer": "-20",
            "options_json": None,
            "hint": "(-4) - 16 = (-4) + (-16) = -20."
        },
        {
            "task_order": 13,
            "question": "Обчисліть: (-6) · 7 = ?",
            "task_type": "input_number",
            "correct_answer": "-42",
            "options_json": None,
            "hint": "Добуток чисел з різними знаками є від'ємним: -(6 · 7) = -42."
        },
        {
            "task_order": 14,
            "question": "Обчисліть: 8 · (-5) = ?",
            "task_type": "input_number",
            "correct_answer": "-40",
            "options_json": None,
            "hint": "Добуток чисел з різними знаками є від'ємним: -(8 · 5) = -40."
        },
        {
            "task_order": 15,
            "question": "Обчисліть: (-9) · (-4) = ?",
            "task_type": "input_number",
            "correct_answer": "36",
            "options_json": None,
            "hint": "Добуток двох від'ємних чисел є додатним: +(9 · 4) = 36."
        },
        {
            "task_order": 16,
            "question": "Обчисліть: (-7) · (-8) = ?",
            "task_type": "input_number",
            "correct_answer": "56",
            "options_json": None,
            "hint": "Добуток двох від'ємних чисел є додатним: +(7 · 8) = 56."
        },
        {
            "task_order": 17,
            "question": "Обчисліть: (-32) : 8 = ?",
            "task_type": "input_number",
            "correct_answer": "-4",
            "options_json": None,
            "hint": "Частка чисел з різними знаками є від'ємною: -(32 : 8) = -4."
        },
        {
            "task_order": 18,
            "question": "Обчисліть: (-45) : (-9) = ?",
            "task_type": "input_number",
            "correct_answer": "5",
            "options_json": None,
            "hint": "Частка двох від'ємних чисел є додатним числом: +(45 : 9) = 5."
        },
        {
            "task_order": 19,
            "question": "Обчисліть: 42 : (-6) = ?",
            "task_type": "input_number",
            "correct_answer": "-7",
            "options_json": None,
            "hint": "Частка чисел з різними знаками є від'ємною: -(42 : 6) = -7."
        },
        {
            "task_order": 20,
            "question": "Обчисліть: (-56) : 7 = ?",
            "task_type": "input_number",
            "correct_answer": "-8",
            "options_json": None,
            "hint": "Частка чисел з різними знаками є від'ємною: -(56 : 7) = -8."
        },
        # Task 21: Equation with module |3x - 3| = 9
        {
            "task_order": 21,
            "question": "📘 Приклад: |2x - 4| = 8 розпадається на 2x - 4 = 8 (x = 6) або 2x - 4 = -8 (x = -2), відповідь записується: 6; -2.\n\nРозв'яжіть рівняння з модулем:\n|3x - 3| = 9\nЯкщо рівняння має два розв'язки, запишіть їх через крапку з комою (наприклад: -10;-20):",
            "task_type": "input_number",
            "correct_answer": "4; -2|-2; 4|4;-2|-2;4|4, -2|-2, 4|x=4; x=-2|x=-2; x=4|x=4;x=-2|x=-2;x=4",
            "options_json": None,
            "hint": "Рівняння |3x - 3| = 9 розпадається на два випадки: 1) 3x - 3 = 9 => 3x = 12 => x = 4; 2) 3x - 3 = -9 => 3x = -6 => x = -2. Відповідь: 4; -2 (або -2; 4)."
        },
        # Task 22: Equation where product is zero (x + 3) * (2x + 6) = 0
        {
            "task_order": 22,
            "question": "📘 Приклад: (x - 5) · (3x + 9) = 0 розпадається на x - 5 = 0 (x = 5) або 3x + 9 = 0 (x = -3), відповідь записується: 5; -3.\n\nРозв'яжіть рівняння:\n(x + 3) · (2x + 6) = 0\nЗапишіть знайдені розв'язки (якщо два розв'язки — через крапку з комою):",
            "task_type": "input_number",
            "correct_answer": "-3|-3; -3|-3;-3|x=-3|x1=-3; x2=-3|-3, -3|x=-3; x=-3|x=-3;x=-3",
            "options_json": None,
            "hint": "Добуток дорівнює 0, коли хоча б один із множників дорівнює 0: 1) x + 3 = 0 => x = -3; 2) 2x + 6 = 0 => 2x = -6 => x = -3. Обидва множники дають розв'язок x = -3."
        },
        # Task 23: Practical problem with negative numbers
        {
            "task_order": 23,
            "question": "О 18:00 термометр показував температуру повітря +2 °C. До опівночі температура впала на 9 °C, а до ранку знизилася ще на 3 °C. Яку температуру показував термометр уранці? (У відповідь запишіть лише число у °C, наприклад: -10)",
            "task_type": "input_number",
            "correct_answer": "-10|-10°C|-10 C|-10 град|-10 градусів|-10°",
            "options_json": None,
            "hint": "Обчислюємо послідовно: початкова температура 2 °C, впала на 9 °C: 2 - 9 = -7 °C. Знизилася ще на 3 °C: -7 - 3 = -10 °C."
        }
    ]

    upsert_topic_tasks(db, control_topic_2.id, control_2_tasks_data)

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

    upsert_topic_tasks(db, info_topic.id, tasks_informatics_data)

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

    arch_tasks = [
        {
            "task_order": order,
            "question": question,
            "task_type": task_type,
            "correct_answer": answer,
            "options_json": json.dumps(options, ensure_ascii=False) if options else None,
            "hint": hint
        }
        for order, question, task_type, answer, options, hint in archives_tasks
    ]
    upsert_topic_tasks(db, archives_topic.id, arch_tasks)

    # =========================================================================
    # 8th Grade: Informatics Topic 3 - Final Lesson on Compression & Archives
    # =========================================================================
    theory_final_archives_8 = """### 💻 Підсумковий урок: Стиснення даних і операції з архівами (8 клас)

**Тема:** Узагальнення та систематизація знань з теми «Стиснення даних та операції з архівами».  
**Мета:** Закріпити теоретичні поняття стиснення без втрат і з втратами, формули розрахунку коефіцієнта стиснення $K$ та відсотка економії, практичні навички дослідження, розпакування та створення архівів у програмах 7-Zip, WinRAR і засобах операційної системи.

---

#### 📂 Вихідні матеріали для практичного блоку:
Вихідні файли практичної роботи доступні для завантаження:
- 📦 **Початковий архів:** [Завантажити compress_archive01.zip (11.7 МБ)](/static/materials/8class/operation_with_archives/compress_archive01.zip)
- 🖼️ **Зображення 1:** [Завантажити 6711626.png (4.4 КБ)](/static/materials/8class/operation_with_archives/6711626.png)
- 🖼️ **Зображення 2:** [Завантажити 742940.png (5.2 КБ)](/static/materials/8class/operation_with_archives/742940.png)
- 📝 **Документ «Каменярі»:** [Завантажити franko-ivan-iakovych-kameniari647.docx (9.5 КБ)](/static/materials/8class/operation_with_archives/franko-ivan-iakovych-kameniari647.docx)
- 📑 **Комплексний документ:** [Завантажити тексти з малюнками.docx (16.3 МБ)](/static/materials/8class/operation_with_archives/тексти%20з%20малюнками.docx)

---

#### 📋 Покроковий практичний план:
1. **Перегляд вмісту архіву:** Відкрийте `compress_archive01.zip` без видобування та перегляньте його вміст (містить 4 файли: презентацію `Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx`, казку `franko-ivan-iakovych-farbovanyy-lys.docx`, фото `vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg` та текстовий файл `archive_lesson1.txt`).
2. **Розпакування:** Видобудьте всі файли з архіву в окрему робочу папку (`Видобути до...`).
3. **Створення власного архіву:** Виділіть інші 4 окремі файли (`6711626.png`, `742940.png`, `franko-ivan-iakovych-kameniari647.docx`, `тексти з малюнками.docx`) та запакуйте їх в один спільний архів (`Мій_Архів_Прізвище.zip` або `.7z` / `.rar`).
4. **Аналіз ефективності:** Порівняйте початковий сумарний розмір файлів і розмір створеного архіву.

---

#### 📑 Підсумковий теоретичний довідник:
1. **Стиснення БЕЗ втрат (Lossless):** Забезпечує 100% точне відновлення даних байт у байт. Застосовується для програм, текстів, баз даних. Формати: `ZIP`, `7z`, `RAR`, `PNG`.
2. **Стиснення З втратами (Lossy):** Відкидає малопомітні для ока/слуху деталі задля зменшення обсягу в 10–50 разів. Оригінал відновити неможливо. Формати: `JPEG`, `MP3`, `MP4`.
3. **Формули:**
   - Коефіцієнт стиснення: $K = \\frac{\\text{Початковий розмір}}{\\text{Стиснений розмір}}$.
   - Відсоток економії: $\\text{Економія (\\%)} = \\left(1 - \\frac{\\text{Стиснений розмір}}{\\text{Початковий розмір}}\\right) \\times 100\\%$.
4. **Ступінь стиснення файлів:**
   - Чистий текст (`.txt`) стискається у сотні разів ($K \\approx 300+$).
   - Файли, що вже містять внутрішнє стиснення (`.docx`, `.xlsx`, `.jpeg`), під час повторного архівування майже не змінюють розмір ($K \\approx 1.0 - 1.1$).
5. **Безпека та паролі:** Пароль захищає вміст від сторонніх осіб (шифрування AES-256), але не захищає комп'ютер від вірусів усередині невідомих архівів.
"""

    final_archives_topic = db.query(Topic).filter_by(subject_id=subject_info.id, slug="info-8-final-archives").first()
    if not final_archives_topic:
        final_archives_topic = Topic(
            subject_id=subject_info.id,
            name="Підсумковий урок по стисненню даних і операціях з архівами",
            slug="info-8-final-archives",
            room_code="info-8-final-archives",
            description="Підсумковий урок для 8 класу: теоретичні основи стиснення даних без втрат і з втратами, практичний блок операцій з архівами (розпакування та створення архівів WinRAR/7-Zip), виконання 20 контрольних тестових завдань.",
            theory_content=theory_final_archives_8,
            sort_order=3
        )
        db.add(final_archives_topic)
        db.commit()
        db.refresh(final_archives_topic)
    else:
        final_archives_topic.name = "Підсумковий урок по стисненню даних і операціях з архівами"
        final_archives_topic.room_code = "info-8-final-archives"
        final_archives_topic.description = "Підсумковий урок для 8 класу: теоретичні основи стиснення даних без втрат і з втратами, практичний блок операцій з архівами (розпакування та створення архівів WinRAR/7-Zip), виконання 20 контрольних тестових завдань."
        final_archives_topic.theory_content = theory_final_archives_8
        final_archives_topic.sort_order = 3
        db.commit()

    final_archives_tasks = [
        (1, "Що являє собою процес стиснення (компресії) даних у комп'ютерній системі?", "choice", "A", [
            {"key": "A", "text": "Перетворення даних за спеціальними алгоритмами для зменшення обсягу їхнього збереження та передачі мережею"},
            {"key": "B", "text": "Фізичне стиснення пластин жорсткого диска або мікросхем пам'яті"},
            {"key": "C", "text": "Видалення половини тексту та графіки з документа без можливості відновлення"},
            {"key": "D", "text": "Зміна розширення файлу без зміни його внутрішнього вмісту"}
        ], "Стиснення даних — це алгоритмічне зменшення розміру файлу для економії простору та прискорення передачі."),

        (2, "У чому полягає принципова відмінність стиснення БЕЗ втрат (Lossless) від стиснення З втратами (Lossy)?", "choice", "A", [
            {"key": "A", "text": "Стиснення без втрат дозволяє відновити початкові дані на 100% точно до кожного біта, тоді як стиснення з втратами необоротно відкидає частину інформації"},
            {"key": "B", "text": "Стиснення без втрат працює тільки на операційній системі Windows, а з втратами — на macOS"},
            {"key": "C", "text": "Стиснення без втрат завжди зменшує файл рівно в 100 разів, а з втратами — в 2 рази"},
            {"key": "D", "text": "Різниці немає, це синоніми одного і того ж методу архівації"}
        ], "Метод без втрат гарантує абсолютну точність відновлення оригінального файлу."),

        (3, "Для яких типів комп'ютерних файлів допустимо використовувати ВИКЛЮЧНО стиснення без втрат?", "choice", "A", [
            {"key": "A", "text": "Програмний виконуваний код (.exe), текстові документи (.docx, .txt), бази даних та вихідні тексти програм"},
            {"key": "B", "text": "Тільки для фотографій JPEG високої роздільної здатності"},
            {"key": "C", "text": "Виключно для звукових файлів формату MP3"},
            {"key": "D", "text": "Для потокового відео на YouTube"}
        ], "У програмах, документах та базах даних втрата навіть одного біта робить файл непрацездатним."),

        (4, "Які з наведених форматів належать до алгоритмів стиснення З ВТРАТАМИ даних?", "choice", "A", [
            {"key": "A", "text": "JPEG, MP3, AAC, MP4, WebP"},
            {"key": "B", "text": "ZIP, RAR, 7z, GZ, TAR"},
            {"key": "C", "text": "DOCX, XLSX, PPTX, ODT"},
            {"key": "D", "text": "TXT, PNG, FLAC, BMP"}
        ], "Мультимедійні формати JPEG, MP3 та MP4 використовують стиснення з втратами, видаляючи непомітні для очей/вух деталі."),

        (5, "Які формати файлів є найпопулярнішими архівами стиснення БЕЗ втрат?", "choice", "A", [
            {"key": "A", "text": ".zip, .7z, .rar, .tar.gz"},
            {"key": "B", "text": ".mp3, .aac, .ogg"},
            {"key": "C", "text": ".jpg, .jpeg, .webp"},
            {"key": "D", "text": ".mp4, .avi, .mkv"}
        ], "Стандартними форматами стиснених архівів є ZIP, 7z, RAR."),

        (6, "За якою формулою розраховується коефіцієнт стиснення даних (K)?", "choice", "A", [
            {"key": "A", "text": "K = Початковий розмір файлу / Стиснений розмір файлу"},
            {"key": "B", "text": "K = Початковий розмір файлу + Стиснений розмір файлу"},
            {"key": "C", "text": "K = Стиснений розмір файлу / Початковий розмір файлу"},
            {"key": "D", "text": "K = Початковий розмір файлу × 100%"}
        ], "Коефіцієнт K показує, у скільки разів початковий розмір більший за стиснений."),

        (7, "Текстовий файл розміром 400 КБ після архівації у ZIP зменшився до 100 КБ. Який коефіцієнт стиснення K та відсоток економії місця?", "choice", "A", [
            {"key": "A", "text": "K = 4.0×, економія = 75%"},
            {"key": "B", "text": "K = 2.0×, економія = 50%"},
            {"key": "C", "text": "K = 0.25×, економія = 25%"},
            {"key": "D", "text": "K = 10.0×, економія = 90%"}
        ], "400 / 100 = 4.0; економія = (1 - 100/400) * 100% = 75%."),

        (8, "Чому чистий текстовий файл (.txt) стискається архіватором ZIP у сотні разів краще, ніж документ Word (.docx) чи фотографія (.jpeg)?", "choice", "A", [
            {"key": "A", "text": "Текстовий файл містить багато повторюваних символів і слів, тоді як .docx уже стиснений ZIP-контейнер, а .jpeg — уже стиснене зображення"},
            {"key": "B", "text": "Текстові файли мають меншу кількість літер"},
            {"key": "C", "text": "Архіватори спеціально видаляють текст з файлу .txt"},
            {"key": "D", "text": "Формати docx та jpeg заборонено стискати законом"}
        ], "Повторювані текстові фрагменти легко замінюються короткими словниковими посиланнями за алгоритмом Deflate."),

        (9, "Що відбудеться з розміром файлу, якщо вже стиснений ZIP-архів повторно заархівувати в інший ZIP або RAR архів?", "choice", "A", [
            {"key": "A", "text": "Розмір практично не зміниться або навіть трохи збільшиться через службові заголовки нового архіву"},
            {"key": "B", "text": "Розмір зменшиться ще рівно вдвічі"},
            {"key": "C", "text": "Архів стиснеться до 1 байта"},
            {"key": "D", "text": "Файл автоматично розпакується"}
        ], "Дані в архіві вже мають високу ентропію (не містять простих повторів), тому повторне стиснення неефективне."),

        (10, "У чому полягає головна практична користь від створення одного спільного архіву з 50 окремих файлів, навіть якщо їхній загальний розмір зменшився лише на 2%?", "choice", "A", [
            {"key": "A", "text": "Зручність передавання єдиним пакетом електронною поштою чи месенджером, збереження структури папок і цілісності файлів"},
            {"key": "B", "text": "Автоматичне підвищення роздільної здатності графічних файлів"},
            {"key": "C", "text": "Конвертація всіх документів у формат PDF"},
            {"key": "D", "text": "Збільшення швидкості роботи монітора"}
        ], "Головна перевага архівування — пакетування та зручність транспортування множини файлів."),

        (11, "Які програми-архіватори є найвідомішими та підтримують роботу з різними форматами архівів (ZIP, 7z, RAR)?", "choice", "A", [
            {"key": "A", "text": "7-Zip, WinRAR, WinZip"},
            {"key": "B", "text": "Microsoft Word, Google Docs, LibreOffice"},
            {"key": "C", "text": "Paint, Adobe Photoshop, GIMP"},
            {"key": "D", "text": "VLC Player, Windows Media Player"}
        ], "7-Zip і WinRAR — класичні потужні програми-архіватори."),

        (12, "Як переглянути список файлів усередині ZIP-архіву без їх попереднього видобування на жорсткий диск?", "choice", "A", [
            {"key": "A", "text": "Відкрити файл архіву подвійним кліком у Провіднику або через програму 7-Zip / WinRAR"},
            {"key": "B", "text": "Перейменувати файл архіву з .zip на .txt"},
            {"key": "C", "text": "Запустити файл як виконувану програму"},
            {"key": "D", "text": "Роздрукувати файл архіву на принтері"}
        ], "Архіватори дозволяють переглядати дерево файлів і їх параметри безпосередньо у вікні програми."),

        (13, "Яка команда контекстного меню найшвидше розпаковує архів в окрему однойменну папку поруч із архівом?", "choice", "A", [
            {"key": "A", "text": "7-Zip / WinRAR ➔ «Видобути до \"назва_архіву\\\"»"},
            {"key": "B", "text": "«Надіслати ➔ Стиснута ZIP-папка»"},
            {"key": "C", "text": "«Видалити в Кошик»"},
            {"key": "D", "text": "«Створити ярлик»"}
        ], "Команда «Видобути до [папка]\\» створює нову папку з іменем архіву та складає всі видобуті файли туди."),

        (14, "Що забезпечує опція «Встановити пароль» під час створення нового архіву в 7-Zip чи WinRAR?", "choice", "A", [
            {"key": "A", "text": "Шифрування вмісту архіву, щоб доступ до файлів мали лише користувачі, які знають пароль"},
            {"key": "B", "text": "Збільшення швидкості завантаження файлів з інтернету в 10 разів"},
            {"key": "C", "text": "Автоматичний переклад тексту архіву українською мовою"},
            {"key": "D", "text": "Автоматичне видалення вірусів з комп'ютера"}
        ], "Пароль активує криптографічний захист (наприклад, AES-256), унеможливлюючи несанкціоноване відкриття."),

        (15, "Чи гарантує завантаження ZIP-архіву з невідомого джерела в інтернеті безпеку комп'ютера від вірусів?", "choice", "A", [
            {"key": "A", "text": "Ні, файли всередині архіву можуть містити шкідливі програми, тому їх обов'язково треба перевіряти антивірусом перед відкриттям"},
            {"key": "B", "text": "Так, архівування автоматично знищує всі можливі комп'ютерні віруси"},
            {"key": "C", "text": "Так, якщо архів має формат .7z"},
            {"key": "D", "text": "Так, тому що архіви ніколи не містять шкідливого коду"}
        ], "Архівація лише стискає байти і не перевіряє файли на наявність загроз."),

        (16, "Що таке саморозпаковуваний архів (SFX-архів, файл з розширенням .exe)?", "choice", "A", [
            {"key": "A", "text": "Архів, який містить невеликий вбудований програмний модуль розпакування, завдяки чому його можна розархівувати на комп'ютері без встановленого архіватора"},
            {"key": "B", "text": "Архів, який видаляє себе після першого перегляду"},
            {"key": "C", "text": "Архів, призначений виключно для смартфонів Android"},
            {"key": "D", "text": "Архів, що працює лише за наявності доступу до інтернету"}
        ], "SFX (SelF-eXtracting) архів є виконуваним файлом, якому для розпакування не потрібні сторонні програми."),

        (17, "Які вихідні матеріали використовувалися у практичному блоці уроку з теми «Операції з архівами»?", "choice", "A", [
            {"key": "A", "text": "5 файлів: compress_archive01.zip, 2 зображення (6711626.png, 742940.png) та 2 документи Word"},
            {"key": "B", "text": "Тільки один відеофайл MP4"},
            {"key": "C", "text": "100 музичних файлів"},
            {"key": "D", "text": "Жодного файлу, робота виконувалася тільки на папері"}
        ], "У практичній роботі учні опрацьовують архів compress_archive01.zip та 4 окремі файли (2 png та 2 docx)."),

        (18, "Які 4 файли з вихідних матеріалів практичної роботи потрібно було об'єднати в один спільний архів на Етапі 3?", "choice", "A", [
            {"key": "A", "text": "6711626.png, 742940.png, franko-ivan-iakovych-kameniari647.docx та тексти з малюнками.docx"},
            {"key": "B", "text": "Тільки архів compress_archive01.zip"},
            {"key": "C", "text": "Тільки текстовий файл з віршем «Каменярі»"},
            {"key": "D", "text": "Всі ярлики з Робочого столу"}
        ], "Всі вихідні файли, крім початкового zip-архіву, пакуються в новий архів учня."),

        (19, "Що являє собою багатотомний архів у програмах 7-Zip та WinRAR?", "choice", "A", [
            {"key": "A", "text": "Розбиття одного великого архіву на кілька частин фіксованого розміру (наприклад, по 100 МБ) для зручності перенесення чи надсилання"},
            {"key": "B", "text": "Архів, який містить більше ніж 1000 томів художньої літератури"},
            {"key": "C", "text": "Архів, який можна відкрити лише одночасно на трьох моніторах"},
            {"key": "D", "text": "Звичайний текстовий документ Word"}
        ], "Багатотомні архіви (.part1.rar, .z01, .001) дозволяють ділити гігабайтні файли на частини."),

        (20, "Чому під час архівації документа «тексти з малюнками.docx» розміром ~16.3 МБ розмір отриманого ZIP-архіву становить близько ~16.2 МБ?", "choice", "A", [
            {"key": "A", "text": "Сучасні формати MS Office (.docx, .xlsx, .pptx) самі є контейнерами зі стисненими XML-файлами та упакованими зображеннями, тому повторне стиснення дає незначний ефект (~0.5-1%)"},
            {"key": "B", "text": "Архіватор ZIP пошкодив документ під час обробки"},
            {"key": "C", "text": "Документ містить помилки в орфографії"},
            {"key": "D", "text": "Операційна система заблокувала запис файлу на диск"}
        ], "Формат docx — це вже внутрішньо стиснений zip-контейнер, тому його повторне стиснення майже не зменшує обсяг.")
    ]

    final_arch_tasks = [
        {
            "task_order": order,
            "question": question,
            "task_type": task_type,
            "correct_answer": answer,
            "options_json": json.dumps(options, ensure_ascii=False) if options else None,
            "hint": hint
        }
        for order, question, task_type, answer, options, hint in final_archives_tasks
    ]
    upsert_topic_tasks(db, final_archives_topic.id, final_arch_tasks)

    # =========================================================================
    # 8th Grade: Informatics Topic 4 - Coding and Decoding, Units of Information
    # =========================================================================
    theory_coding_8 = """### 💻 Інформатика 8 клас: Кодування та декодування даних. Двійкове кодування та одиниці інформації

---

#### 📑 Теоретичний довідник до уроку:

1. **Кодування та декодування повідомлень:**
   - **Кодування** — це процес подання повідомлення (інформації) за допомогою певної системи знаків (коду) за встановленими правилами для зручності збереження, передавання чи автоматизованого опрацювання.
   - **Декодування** — це зворотний процес перетворення закодованого повідомлення у форму, зрозумілу адресату або системі (наприклад: читання азбуки Морзе, сканування QR-коду камерою смартфона, перетворення двійкового коду у графічне зображення на екрані).
   - Вибір способу кодування визначається технічними засобами передавання та опрацювання, вимогами до швидкості, надійності зв'язку та захисту даних від несанкціонованого доступу.

2. **Кодування текстових, графічних і звукових даних. Колірні моделі:**
   - **Текстові дані:**
     - **ASCII** — стандартна 8-бітна таблиця кодів (256 символів), призначена переважно для латиниці, цифр та керуючих символів.
     - **Unicode (UTF-8, UTF-16)** — універсальний стандарт кодування, що використовує більше бітів на символ (до 4 байтів) і дозволяє закодувати знаки практично всіх писемностей світу.
   - **Колірні моделі та растрова графіка:**
     - **RGB (Red, Green, Blue)** — адитивна модель кольору, побудована на випромінюванні світла (використовується в моніторах, екранах смартфонів, телевізорах). Змішування трьох базових кольорів максимальної яскравості утворює білий колір.
     - **CMYK (Cyan, Magenta, Yellow, Key/Black)** — субтрактивна модель кольору, яка використовується переважно у поліграфії для друку на папері.
     - **Глибина кольору ($I$):** кількість бітів, що виділяється на кодування кольору одного пікселя. Кількість можливих кольорів: $N = 2^I$. (Наприклад, при $8\\text{ бітах}$ $N = 2^8 = 256$ кольорів; при 24 бітах True Color — $2^{24} = 16\\,777\\,216$ кольорів).
   - **Мультимедійні (звукові) дані:**
     - Цифрове кодування звуку базується на **дискретизації** неперервного аналогового сигналу за часом та **квантуванні** амплітуди коливань за рівнем.

3. **Двійкове кодування та одиниці вимірювання:**
   - **Біт (bit)** — мінімальна неподільна одиниця інформації (один двійковий розряд `0` або `1`).
   - $1\\text{ байт} = 8\\text{ бітів}$.
   - $1\\text{ Кбайт (кілобайт)} = 1024\\text{ байти} = 2^{10}\\text{ байтів}$.
   - $1\\text{ Мбайт (мегабайт)} = 1024\\text{ Кбайти} = 2^{20}\\text{ байтів}$.
   - $1\\text{ Гбайт (гігабайт)} = 1024\\text{ Мбайти} = 2^{30}\\text{ байтів}$.
   - **Обчислення обсягу текстового повідомлення:** $V = K \\times i$, де $K$ — кількість символів, $i$ — інформаційна вага одного символу в бітах або байтах (наприклад: $512\\text{ символів} \\times 16\\text{ біт (2 байти)} = 1024\\text{ байти} = 1\\text{ Кбайт}$).
   - **Обчислення обсягу растрового зображення:** $V = X \\times Y \\times i$, де $X \\times Y$ — загальна кількість пікселів, $i$ — глибина кольору в байтах (наприклад: $100 \\times 100 = 10\\,000\\text{ пікселів} \\times 3\\text{ байти (24 біти)} = 30\\,000\\text{ байтів}$).
"""

    coding_topic = db.query(Topic).filter_by(subject_id=subject_info.id, slug="info-8-data-coding").first()
    if not coding_topic:
        coding_topic = Topic(
            subject_id=subject_info.id,
            name="Кодування та декодування повідомлень. Одиниці інформації",
            slug="info-8-data-coding",
            room_code="info-8-data-coding",
            description="Тестовий контроль знань для 8 класу: кодування/декодування повідомлень, кодування тексту (ASCII, Unicode), графіки (RGB, CMYK, глибина кольору), звуку та двійкові одиниці вимірювання довжини коду.",
            theory_content=theory_coding_8,
            sort_order=4
        )
        db.add(coding_topic)
        db.commit()
        db.refresh(coding_topic)
    else:
        coding_topic.name = "Кодування та декодування повідомлень. Одиниці інформації"
        coding_topic.room_code = "info-8-data-coding"
        coding_topic.description = "Тестовий контроль знань для 8 класу: кодування/декодування повідомлень, кодування тексту (ASCII, Unicode), графіки (RGB, CMYK, глибина кольору), звуку та двійкові одиниці вимірювання довжини коду."
        coding_topic.theory_content = theory_coding_8
        coding_topic.sort_order = 4
        db.commit()

    coding_tasks = [
        (1, "Що є головною метою процесу кодування повідомлення?", "choice", "B", [
            {"key": "A", "text": "Повне знищення первинного змісту інформації"},
            {"key": "B", "text": "Подання повідомлення у формі, зручній для його збереження, передавання або опрацювання"},
            {"key": "C", "text": "Виправлення граматичних помилок у тексті"},
            {"key": "D", "text": "Виключно зменшення фізичного розміру носія даних"}
        ], "Кодування оптимізує форму подання інформації для ефективної взаємодії технічних систем або користувачів."),

        (2, "Які дії належать до процесу декодування? (Оберіть усі правильні варіанти)", "multichoice", "A, C, D", [
            {"key": "A", "text": "Читання закодованого азбукою Морзе повідомлення"},
            {"key": "B", "text": "Переклад тексту на мову жестів для сприйняття людиною з порушенням слуху"},
            {"key": "C", "text": "Перетворення двійкового коду у зображення на екрані монітора"},
            {"key": "D", "text": "Розпізнавання QR-коду за допомогою камери смартфона"}
        ], "Декодування — це відновлення повідомлення у форму, зрозумілу для адресата чи системи (варіант B є процесом кодування/перекодування)."),

        (3, "Учень закодував слово за правилом: кожна літера замінюється наступною за алфавітом (для останньої — першою). Отримано код: К П М П (в українському алфавіті). Яке вихідне слово було закодовано?", "choice", "C", [
            {"key": "A", "text": "КОЛО"},
            {"key": "B", "text": "КЛАС"},
            {"key": "C", "text": "ЙОЛО"},
            {"key": "D", "text": "ЛРНР"}
        ], "Зворотний процес декодування вимагає зсуву на одну позицію назад в українському алфавіті: перед К — Й, перед П — О, перед М — Л, перед П — О → ЙОЛО."),

        (4, "Які фактори визначають вибір способу кодування повідомлення? (Оберіть усі правильні варіанти)", "multichoice", "A, B, C", [
            {"key": "A", "text": "Технічні засоби, якими планується передавати або опрацьовувати дані"},
            {"key": "B", "text": "Необхідність захисту даних від несанкціонованого доступу"},
            {"key": "C", "text": "Швидкість та надійність передавання каналом зв'язку"},
            {"key": "D", "text": "Особисті художні вподобання розробника комп'ютерного кабелю"}
        ], "Спосіб кодування обирається з огляду на максимальну продуктивність, безпеку та сумісність пристроїв."),

        (5, "Чому кодова таблиця Unicode є ефективнішою та більш універсальною за стандартну таблицю ASCII?", "choice", "B", [
            {"key": "A", "text": "ASCII не підтримує англійські літери"},
            {"key": "B", "text": "Unicode використовує більше бітів на символ і дозволяє закодувати знаки майже всіх писемностей світу"},
            {"key": "C", "text": "Unicode зменшує розмір файлів у 10 разів порівняно з ASCII"},
            {"key": "D", "text": "ASCII застосовується лише для кодування графічних файлів"}
        ], "8-бітна таблиця ASCII обмежена 256 символами, тоді як стандарти Unicode (UTF-8, UTF-16 тощо) усувають інформаційні бар'єри між різними мовами."),

        (6, "Які твердження щодо колірної моделі RGB є правильними? (Оберіть усі правильні варіанти)", "multichoice", "A, B, D", [
            {"key": "A", "text": "Базовими кольорами є червоний (Red), зелений (Green), синій (Blue)"},
            {"key": "B", "text": "Це адитивна модель: змішування всіх трьох компонентів максимальної яскравості утворює білий колір"},
            {"key": "C", "text": "Вона використовується переважно у поліграфії для друку на папері"},
            {"key": "D", "text": "Вона використовується в моніторах, екранах смартфонів і телевізорах"}
        ], "RGB генерує світлові промені (екрани). Для друку на матеріалах застосовується субтрактивна модель CMYK."),

        (7, "Скільки різних кольорів можна закодувати за глибини кольору 8 біт на один піксель?", "choice", "C", [
            {"key": "A", "text": "8"},
            {"key": "B", "text": "16"},
            {"key": "C", "text": "256"},
            {"key": "D", "text": "65536"}
        ], "Кількість можливих станів обчислюється за формулою N = 2^I, отже N = 2^8 = 256."),

        (8, "Що лежить в основі цифрового кодування звукових коливань (аудіо)?", "choice", "B", [
            {"key": "A", "text": "Вимірювання кількості символів у тексті пісні"},
            {"key": "B", "text": "Дискретизація аналогового сигналу за часом та квантування за амплітудою"},
            {"key": "C", "text": "Заміна високих частот кольоровими точками моделі CMYK"},
            {"key": "D", "text": "Запис виключно тривалості звучання у байтах"}
        ], "Неперервний звуковий сигнал перетворюється на дискретну послідовність двійкових чисел через фіксацію значень амплітуди через рівні проміжки часу."),

        (9, "Який мінімальний обсяг інформації несе один розряд двійкового коду (0 або 1)?", "choice", "C", [
            {"key": "A", "text": "1 байт"},
            {"key": "B", "text": "1 бод"},
            {"key": "C", "text": "1 біт"},
            {"key": "D", "text": "1 кілобіт"}
        ], "Біт (binary digit) — найменша базова неподільна одиниця вимірювання двійкових даних."),

        (10, "Які співвідношення між одиницями інформації є правильними? (Оберіть усі правильні варіанти)", "multichoice", "A, B, D", [
            {"key": "A", "text": "1 байт = 8 бітів"},
            {"key": "B", "text": "1 Кбайт = 1024 байти"},
            {"key": "C", "text": "1 Мбайт = 1000 Кбайтів"},
            {"key": "D", "text": "1 Гбайт = 1024 Мбайти"}
        ], "У двійковій системі кратні префікси базуються на степенях двійки (2^10 = 1024)."),

        (11, "Текстове повідомлення містить 512 символів. Кожен символ закодовано за допомогою 16-бітного кодування (UTF-16). Який інформаційний обсяг цього повідомлення в байтах?", "choice", "B", [
            {"key": "A", "text": "512 байтів"},
            {"key": "B", "text": "1024 байти"},
            {"key": "C", "text": "2048 байтів"},
            {"key": "D", "text": "8192 байти"}
        ], "16 бітів = 2 байти. Загальний обсяг: 512 × 2 = 1024 байти (або 1 Кбайт)."),

        (12, "Растрове зображення розміром 100 × 100 пікселів збережено у 24-бітному кольорі (True Color). Скільки байтів становить інформаційний обсяг цього зображення без урахування стиснення?", "choice", "B", [
            {"key": "A", "text": "24 000 байтів"},
            {"key": "B", "text": "30 000 байтів"},
            {"key": "C", "text": "10 000 байтів"},
            {"key": "D", "text": "240 000 байтів"}
        ], "1. Кількість пікселів: 100 × 100 = 10 000. 2. Глибина кольору: 24 біти = 3 байти. 3. Обсяг: 10 000 × 3 = 30 000 байтів.")
    ]

    coding_tasks_data = [
        {
            "task_order": order,
            "question": question,
            "task_type": task_type,
            "correct_answer": answer,
            "options_json": json.dumps(options, ensure_ascii=False) if options else None,
            "hint": hint
        }
        for order, question, task_type, answer, options, hint in coding_tasks
    ]
    upsert_topic_tasks(db, coding_topic.id, coding_tasks_data)

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

    # =========================================================================
    # 9th Grade: Informatics Topic 2 - Document Layout, Columns & Headers
    # =========================================================================
    theory_document_layout_9 = """### 📄 Практична робота: Макети та структура текстового документа (розриви, колонки, колонтитули)

**Тема:** Форматування сторінок текстового документа: розриви сторінок та стовпців, багатошпальтовий текст (колонки) з розділювачем, нумерація сторінок, налаштування верхнього колонтитула з текстом та графічними елементами.  
**Мета:** Навчитися керувати структурою та композицією багатосторінкового текстового документа в сучасних текстових процесорах (Microsoft Word, Google Docs / LibreOffice Writer).

---

#### 📂 Вихідні навчальні матеріали:
- 📝 **Вихідний текстовий документ (Казка «Фарбований лис»):** [Завантажити franko-ivan-iakovych-farbovanyy-lys.docx (24.3 КБ)](/static/materials/9class/document_layout/franko-ivan-iakovych-farbovanyy-lys.docx)  
  *(Резервне посилання: [/static/materials/8class/compress_archive01/franko-ivan-iakovych-farbovanyy-lys.docx](/static/materials/8class/compress_archive01/franko-ivan-iakovych-farbovanyy-lys.docx))*
- 🖼️ **Графічний елемент для колонтитула:** [Завантажити franko_logo.png (4.4 КБ)](/static/materials/9class/document_layout/franko_logo.png) або [header_icon.png (5.2 КБ)](/static/materials/9class/document_layout/header_icon.png)

---

#### 📋 Покроковий план виконання практичного завдання:

##### Крок 1. Завантаження та відкриття документа
1. Завантажте вихідний файл `franko-ivan-iakovych-farbovanyy-lys.docx`.
2. Відкрийте його у встановленій програмі **Microsoft Word** або завантажте на Google Диск і відкрийте в **Google Docs**.

---

##### Крок 2. Перенесення тексту після першого абзацу на наступну сторінку
1. Знайдіть у тексті кінець першого абзацу (закінчується словами: *«...не було смілішого, вигадливішого та спритнішого злодія над нього.»*).
2. Встановіть текстовий курсор безпосередньо після крапки першого абзацу (перед другим абзацом).
3. Вставте **розрив сторінки**:
   - **У Microsoft Word:** вкладка **«Вставлення»** ➔ **«Розрив сторінки»** (або комбінація клавіш `Ctrl + Enter` / вкладка *«Макет»* ➔ *«Розриви»* ➔ *«Сторінка»*).
   - **У Google Docs:** меню **«Вставити»** ➔ **«Розрив»** ➔ **«Розрив сторінки»** (або `Ctrl + Enter`).
4. *Результат:* перший абзац залишається на 1-й сторінці, а весь подальший текст автоматично переходить на початок 2-ї сторінки.

---

##### Крок 3. Розбиття тексту на сторінках від 2-ї до кінця на 3 стовпці з розділювачем
1. Перейдіть на 2-гу сторінку та виділіть весь текст від початку 2-ї сторінки до самого кінця документа (1-шу сторінку не виділяємо!).
2. Розбийте виділений фрагмент на **3 стовпці з лінією-розділювачем**:
   - **У Microsoft Word:** вкладка **«Макет»** (Layout) ➔ кнопка **«Стовпці»** (Columns) ➔ пункт **«Інші стовпці...»** ➔ оберіть шаблон **«Три»** (3 стовпці) ➔ встановіть прапорець **«Розділювач»** (Line between) ➔ переконайтеся, що в полі *«Застосувати»* обрано *«до виділеного тексту»* ➔ натисніть **OK**.
   - **У Google Docs:** меню **«Формат»** ➔ **«Стовпці»** ➔ **«Інші параметри»** ➔ Кількість стовпців: **3**, поставте прапорець **«Лінія між стовпцями»** ➔ натисніть **«Застосувати»**.

---

##### Крок 4. Перенесення тексту на 2-й сторінці у 3-й стовпчик (1-й і 2-й стовпчики залишаються порожніми)
1. Встановіть курсор на самому початку тексту на 2-й сторінці (в першому стовпчику).
2. Вставте перший **розрив стовпця**:
   - **У Microsoft Word:** вкладка **«Макет»** ➔ **«Розриви»** ➔ **«Стовпець»** (або комбінація `Ctrl + Shift + Enter`).
   - **У Google Docs:** меню **«Вставити»** ➔ **«Розрив»** ➔ **«Розрив стовпця»**.
   - *Результат:* текст перейшов у 2-й стовпчик, 1-й стовпчик став порожнім.
3. Встановіть курсор на початку тексту у 2-му стовпчику та знову вставте **розрив стовпця**:
   - *Результат:* текст перемістився у 3-й стовпчик, а перший та другий стовпчики на 2-й сторінці залишилися порожніми.

---

##### Крок 5. Додавання нумерації сторінок внизу посередині
1. Додайте номери сторінок:
   - **У Microsoft Word:** вкладка **«Вставлення»** ➔ **«Номер сторінки»** ➔ **«Унизу сторінки»** ➔ оберіть **«Простий номер 2»** (по центру).
   - **У Google Docs:** меню **«Вставити»** ➔ **«Номери сторінок»** ➔ оберіть варіант із розміщенням номера внизу сторінки (або двічі клацніть у зоні нижнього колонтитула і вирівняйте номер по центру).

---

##### Крок 6. Додавання верхнього колонтитула з текстом «Іван Франко» та закріпленим зображенням
1. Відкрийте режим редагування верхнього колонтитула (подвійний клік мишею у верхньому полі сторінки або меню *«Вставлення» ➔ «Верхній колонтитул»*).
2. Введіть текст: **`Іван Франко`**.
3. Вирівняйте текст по центру (комбінація клавіш `Ctrl + E` або кнопка «По центру» на панелі інструментів).
4. Вставте графічне зображення в колонтитул:
   - Меню **«Вставлення»** ➔ **«Зображення»** (оберіть файл `franko_logo.png` або інше зображення).
   - Налаштуйте обтікання / закріплення зображення:
     - *У Word:* виберіть макет обтікання **«Перед текстом»** / **«У тексті»** і закріпіть розташування у верхній зоні.
     - *У Google Docs:* оберіть **«Обтікання текстом»** або **«Перед текстом»** (Закріпити положення на сторінці).
5. Закрийте редагування колонтитулів (подвійний клік на основному тексті).

---

#### 💡 Корисні комбінації клавіш:
- `Ctrl + Enter` — Швидкий розрив сторінки.
- `Ctrl + Shift + Enter` — Швидкий розрив стовпця (у MS Word).
- `Ctrl + E` — Вирівнювання абзацу / тексту по центру.
"""

    layout_topic = db.query(Topic).filter_by(subject_id=subject_info9.id, slug="info-9-document-layout").first()
    if not layout_topic:
        layout_topic = Topic(
            subject_id=subject_info9.id,
            name="Практична робота. Структура та макет текстового документа (розриви, колонки, колонтитули)",
            slug="info-9-document-layout",
            room_code="info-9-document-layout",
            description="Практична робота для 9 класу: скачування документа «Фарбований лис», розрив сторінки, 3 стовпці з розділювачем, розриви стовпців, нумерація та колонтитул із зображенням і назвою.",
            theory_content=theory_document_layout_9,
            sort_order=2
        )
        db.add(layout_topic)
        db.commit()
        db.refresh(layout_topic)
    else:
        layout_topic.name = "Практична робота. Структура та макет текстового документа (розриви, колонки, колонтитули)"
        layout_topic.room_code = "info-9-document-layout"
        layout_topic.description = "Практична робота для 9 класу: скачування документа «Фарбований лис», розрив сторінки, 3 стовпці з розділювачем, розриви стовпців, нумерація та колонтитул із зображенням і назвою."
        layout_topic.theory_content = theory_document_layout_9
        layout_topic.sort_order = 2
        db.commit()

    # Seed interactive check tasks for layout_topic
    tasks_document_layout_9 = [
        (1, "Який текстовий документ використовується як вихідний матеріал для виконання практичної роботи?", "choice", "A", [
            {"key": "A", "text": "franko-ivan-iakovych-farbovanyy-lys.docx (Казка «Фарбований лис»)"},
            {"key": "B", "text": "archive_lesson1.txt"},
            {"key": "C", "text": "trade-object.pdf"},
            {"key": "D", "text": "blank_empty.docx"}
        ], "Вихідним документом є файл «franko-ivan-iakovych-farbovanyy-lys.docx»."),

        (2, "Яку комбінацію клавіш найшвидше використати для вставки розриву сторінки після першого абзацу?", "choice", "A", [
            {"key": "A", "text": "Ctrl + Enter"},
            {"key": "B", "text": "Ctrl + C"},
            {"key": "C", "text": "Shift + Delete"},
            {"key": "D", "text": "Alt + F4"}
        ], "Комбінація Ctrl + Enter миттєво вставляє розрив сторінки в MS Word та Google Docs."),

        (3, "Де в інтерфейсі Microsoft Word знаходиться команда для вставки розриву сторінки через панель інструментів?", "choice", "A", [
            {"key": "A", "text": "Вкладка «Вставлення» ➔ «Розрив сторінки» (або вкладка «Макет» ➔ «Розриви» ➔ «Сторінка»)"},
            {"key": "B", "text": "Вкладка «Файл» ➔ «Друк»"},
            {"key": "C", "text": "Вкладка «Рецензування» ➔ «Правопис»"},
            {"key": "D", "text": "Вкладка «Вигляд» ➔ «Масштаб»"}
        ], "Розрив сторінки розташований на вкладці «Вставлення» або на вкладці «Макет» (Розриви)."),

        (4, "Як розбити текст на сторінках від 2-ї до кінця саме на 3 стовпці з лінією-розділювачем у Microsoft Word?", "choice", "A", [
            {"key": "A", "text": "Виділити потрібний текст ➔ вкладка «Макет» ➔ «Стовпці» ➔ «Інші стовпці...» ➔ обрати 3 стовпці та встановити прапорець «Розділювач»"},
            {"key": "B", "text": "Намалювати 3 таблиці за допомогою олівця"},
            {"key": "C", "text": "Збільшити розмір шрифту втричі"},
            {"key": "D", "text": "Натиснути клавішу Tab тричі на кожному рядку"}
        ], "Для налаштування стовпців з розділювачем використовують вікно «Макет» ➔ «Стовпці» ➔ «Інші стовпці...» з прапорцем «Розділювач»."),

        (5, "Яку дію потрібно виконати двічі, щоб на 2-й сторінці текст перемістився у 3-й стовпчик, залишивши 1-й та 2-й стовпчики порожніми?", "choice", "A", [
            {"key": "A", "text": "Вставити послідовно два розриви стовпця («Вставити» / «Макет» ➔ «Розриви» ➔ «Стовпець» або Ctrl + Shift + Enter)"},
            {"key": "B", "text": "Натиснути клавішу Enter 100 разів"},
            {"key": "C", "text": "Видалити перші дві сторінки документа"},
            {"key": "D", "text": "Змінити колір фону сторінки на білий"}
        ], "Кожен розрив стовпця (Column Break) переносить наступний текст у наступну шпальту, тому два розриви стовпця звільняють перші два стовпчики."),

        (6, "Де в документі згідно із завданням потрібно розмістити нумерацію сторінок?", "choice", "A", [
            {"key": "A", "text": "Унизу сторінки посередині"},
            {"key": "B", "text": "Угорі сторінки праворуч"},
            {"key": "C", "text": "У лівому полі вертикально"},
            {"key": "D", "text": "По діагоналі по центру сторінки"}
        ], "Завдання вимагає додати нумерацію сторінок унизу посередині сторінки."),

        (7, "Який текст необхідно розмістити по центру у верхньому колонтитулі документа?", "choice", "A", [
            {"key": "A", "text": "Іван Франко"},
            {"key": "B", "text": "Тарас Шевченко"},
            {"key": "C", "text": "Леся Українка"},
            {"key": "D", "text": "Фарбований лис"}
        ], "Згідно з 6-м пунктом завдання у верхній колонтитул додається текст «Іван Франко» по центру."),

        (8, "Що являє собою колонтитул (Header / Footer) у текстовому документі?", "choice", "A", [
            {"key": "A", "text": "Спеціальна область у верхньому або нижньому полі сторінки, інформація з якої автоматично повторюється на сторінках документа"},
            {"key": "B", "text": "Звичайна таблиця з одним рядком і двома клітинками"},
            {"key": "C", "text": "Спливаюча підказка під час наведення курсору миші"},
            {"key": "D", "text": "Звуковий файл, прикріплений до тексту"}
        ], "Колонтитул — це постійний заголовок або елемент оформлення на полях сторінки, що дублюється по всьому документу."),

        (9, "Як відкрити режим редагування верхнього колонтитула на сторінці?", "choice", "A", [
            {"key": "A", "text": "Подвійним кліком лівою кнопкою миші у верхньому полі сторінки (або меню «Вставлення» ➔ «Верхній колонтитул»)"},
            {"key": "B", "text": "Натиснути клавішу Escape п'ять разів"},
            {"key": "C", "text": "Перезавантажити комп'ютер"},
            {"key": "D", "text": "Зберегти файл як простий текст .txt"}
        ], "Для входу в колонтитул достатньо двічі клацнути на верхньому полі аркуша або вибрати команду на вкладці «Вставлення»."),

        (10, "Як закріпити вставлене зображення у верхньому колонтитулі, щоб воно коректно розташовувалося разом із текстом заголовка?", "choice", "A", [
            {"key": "A", "text": "У параметрах макета / обтікання зображення обрати «Перед текстом» або «Обтікання текстом» і виставити його по центру поряд із назвою"},
            {"key": "B", "text": "Склеїти зображення з монітором"},
            {"key": "C", "text": "Перевести документ у формат без малюнків (.txt)"},
            {"key": "D", "text": "Зменшити яскравість екрана"}
        ], "Налаштування обтікання («Перед текстом» / «Обтікання») дозволяє вільно закріплювати та позиціонувати малюнок у колонтитулі.")
    ]

    layout_tasks = [
        {
            "task_order": order,
            "question": q_text,
            "task_type": t_type,
            "correct_answer": ans,
            "options_json": json.dumps(opts, ensure_ascii=False) if opts else None,
            "hint": h_text
        }
        for order, q_text, t_type, ans, opts, h_text in tasks_document_layout_9
    ]
    upsert_topic_tasks(db, layout_topic.id, layout_tasks)

    # =========================================================================
    # 9th Grade: Informatics Topic 3 - Comprehensive Test: Text Processing Systems
    # =========================================================================
    theory_text_processing_test_9 = """### 💻 Інформатика 9 клас: Системи опрацювання текстів (Тематичне тестування)

---

#### 📑 Короткий конспект для підготовки до тесту:

1. **Системи опрацювання текстів. Об’єкти текстового документа та їх властивості:**
   - **Текстовий процесор** — прикладна програма для створення, редагування, форматування, збереження та друку складних текстових документів (Microsoft Word, Google Документи, LibreOffice Writer).
   - **Основні об'єкти документа:**
     - **Символ:** мінімальна одиниця тексту. *Властивості:* гарнітура (шрифт), розмір (кегль), накреслення (прямий, напівжирний, курсив, підкреслений), колір тексту, колір виділення, видозміна (індекси, закреслення).
     - **Слово, речення, рядок.**
     - **Абзац:** фрагмент тексту між двома натисканнями клавіші `Enter`. *Властивості:* вирівнювання (за лівим/правим краєм, по центру, за шириною), відступи зліва і справа, відступ першого рядка («червоний рядок»), міжрядковий інтервал, інтервали перед та після абзацу.
     - **Сторінка:** *Властивості:* розмір аркуша (A4, A5, Letter), орієнтація (книжкова, альбомна), розміри полів (верхнє, нижнє, ліве, праве).
     - **Розділ, таблиця, графічні об'єкти** (малюнки, схеми SmartArt, фігури).

2. **Формати файлів текстових документів та режими роботи:**
   - 📄 **TXT (.txt):** простий неформатований текст, мінімальний розмір, максимальна сумісність.
   - 📝 **DOCX (.docx):** відкритий формат XML/ZIP Microsoft Word з підтримкою повного форматування, таблиць і медіа.
   - 📑 **ODT (.odt):** міжнародний відкритий стандарт OpenDocument (LibreOffice Writer).
   - 📕 **PDF (.pdf):** збереження фіксованого макета сторінок для перегляду та друку на будь-яких пристроях.
   - 📄 **RTF (.rtf):** Rich Text Format (растрові малюнки зберігаються у шістнадцятковому текстовому вигляді без стиснення).
   - **Режими роботи в середовищі:**
     - *Редагування (Editing)* — безпосередня зміна вмісту документа.
     - *Пропонування (Suggesting / Відстеження виправлень)* — зміни фіксуються як пропозиції з коментарями, які автор може затвердити (✓) або відхилити (✕).
     - *Перегляд (Viewing / Тільки читання)* — захист від випадкових змін під час читання.
     - *Режими перегляду в MS Word:* «Розмітка сторінки», «Режим читання», «Веб-документ», «Структура».

3. **Робота з кількома документами:**
   - Перемикання між відкритими вікнами: `Alt + Tab`, `Ctrl + F6` або меню *«Вигляд» ➔ «Перейти до іншого вікна»*.
   - Інструмент **«Розділити» (Split):** розбиває вікно поточного документа на дві панелі для одночасного перегляду різних частин одного довгого тексту.
   - Режим **«Поруч» (View Side by Side):** розміщує два різні документи на екрані поруч із підтримкою синхронного прокручування для порівняння.
   - Обмін даними між документами здійснюється через системний **буфер обміну** (`Ctrl + C`, `Ctrl + X`, `Ctrl + V`).

4. **Створення багаторівневих списків:**
   - **Багаторівневий список** — список з ієрархічною структурою підпорядкування (наприклад: 1 ➔ 1.1 ➔ 1.1.1 або A ➔ a) ➔ •).
   - **Знизити рівень (перейти на рівень глибше / збільшити відступ):** клавіша `Tab` або кнопка *«Збільшити відступ»*.
   - **Підвищити рівень (повернутися на вищий рівень / зменшити відступ):** комбінація `Shift + Tab`, клавіша `Backspace` на початку рядка або кнопка *«Зменшити відступ»*.

5. **Спеціальні символи та формули:**
   - **Спеціальні символи:** вкладка *«Вставлення» ➔ «Символи» ➔ «Символ»* (знаки копірайту ©, торговельної марки ™, валют €, грецькі літери $\alpha, \beta, \pi$, математичні стрілки).
   - **Редактор формул (Equation Editor):** вкладка *«Вставлення» ➔ «Рівняння» (або «Формула»)*.
   - Дозволяє конструювати звичайні дроби, степені, індекси, радикали ($\sqrt{x}$, $\sqrt[n]{x}$), інтеграли ($\int$), знаки сум ($\sum$), матриці та дужки.

6. **Стовпці, розділи та колонтитули:**
   - **Колонки (шпальти):** вкладка *«Макет» ➔ «Стовпці»* (можливість розбиття тексту на 2, 3 стовпці та встановлення розділювача між ними).
   - **Розриви розділів (Section Breaks):** дозволяють розділити документ на автономні частини з різними параметрами сторінок (різна орієнтація аркуша, інша кількість колонок, незалежні колонтитули).
   - **Колонтитули (Header & Footer):** спеціальні області на верхньому чи нижньому полі аркуша, що повторюються на сторінках.
   - **Особливий колонтитул для першої сторінки (Different First Page):** дозволяє приховати колонтитул та номер сторінки на титульному аркуші.
"""

    text_test_topic = db.query(Topic).filter_by(subject_id=subject_info9.id, slug="info-9-text-processing-test").first()
    if not text_test_topic:
        text_test_topic = Topic(
            subject_id=subject_info9.id,
            name="Тестування. Системи опрацювання текстів",
            slug="info-9-text-processing-test",
            room_code="info-9-text-processing-test",
            description="Підсумковий тематичний тест для 9 класу (20 завдань): об'єкти документа, формати файлів, режими роботи, багаторівневі списки, символи та формули, стовпці, розділи й колонтитули.",
            theory_content=theory_text_processing_test_9,
            sort_order=3
        )
        db.add(text_test_topic)
        db.commit()
        db.refresh(text_test_topic)
    else:
        text_test_topic.name = "Тестування. Системи опрацювання текстів"
        text_test_topic.room_code = "info-9-text-processing-test"
        text_test_topic.description = "Підсумковий тематичний тест для 9 класу (20 завдань): об'єкти документа, формати файлів, режими роботи, багаторівневі списки, символи та формули, стовпці, розділи й колонтитули."
        text_test_topic.theory_content = theory_text_processing_test_9
        text_test_topic.sort_order = 3
        db.commit()

    test_20_tasks_data = [
        # Theme 1: Системи опрацювання текстів. Об’єкти текстового документа та їх властивості (1-4)
        {
            "task_order": 1,
            "question": "Яке основне призначення систем опрацювання текстів (текстових процесорів, таких як Microsoft Word, Google Документи, LibreOffice Writer)?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Створення, введення, редагування, комплексне форматування, збереження та друк текстових документів"},
                {"key": "B", "text": "Розробка 3D-ігор та низькорівнева компіляція програмного коду"},
                {"key": "C", "text": "Автоматичне сканування мережі та видалення комп'ютерних вірусів"},
                {"key": "D", "text": "Багатоканальний монтаж аудіо та рендеринг відеороликів"}
            ], ensure_ascii=False),
            "hint": "Текстові процесори призначені для створення, редагування, комплексного форматування та друку документів."
        },
        {
            "task_order": 2,
            "question": "Які з наведених елементів є основними об’єктами текстового документа? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D, E",
            "options_json": json.dumps([
                {"key": "A", "text": "Символ"},
                {"key": "B", "text": "Слово та речення"},
                {"key": "C", "text": "Абзац"},
                {"key": "D", "text": "Сторінка та розділ"},
                {"key": "E", "text": "Графічний об'єкт (малюнок, фігура, таблиця)"},
                {"key": "F", "text": "Системний реєстр Windows"}
            ], ensure_ascii=False),
            "hint": "Об'єктами текстового документа є: символ, слово, речення, абзац, сторінка, розділ, а також вбудовані таблиці й графічні об'єкти."
        },
        {
            "task_order": 3,
            "question": "Які властивості характеризують об'єкт текстового документа «Символ»?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Шрифт (гарнітура), розмір (кегль), накреслення (прямий, напівжирний, курсив), колір тексту та виділення"},
                {"key": "B", "text": "Вирівнювання (за лівим краєм, по центру, за шириною) та міжрядковий інтервал"},
                {"key": "C", "text": "Розміри полів сторінки та орієнтація аркуша (книжкова / альбомна)"},
                {"key": "D", "text": "Кількість колонок у розділі та лінія-розділювач між ними"}
            ], ensure_ascii=False),
            "hint": "Шрифт, розмір (кегль), накреслення та колір є властивостями символу. Вирівнювання та міжрядковий інтервал належать абзацу."
        },
        {
            "task_order": 4,
            "question": "Які з перелічених параметрів є властивостями об'єкта «Абзац»? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D",
            "options_json": json.dumps([
                {"key": "A", "text": "Спосіб вирівнювання тексту (за лівим краєм, по центру, за правим краєм, за шириною)"},
                {"key": "B", "text": "Міжрядковий інтервал (одинарний, 1.15, полуторний, подвійний)"},
                {"key": "C", "text": "Відступ першого рядка («червоний рядок» / відступ абзацу)"},
                {"key": "D", "text": "Інтервали перед абзацом та після абзацу (відбивка)"},
                {"key": "E", "text": "Роздільна здатність матриці дисплея (DPI)"}
            ], ensure_ascii=False),
            "hint": "До властивостей абзацу належать: вирівнювання, відступи зліва/справа, відступ першого рядка, міжрядковий інтервал та інтервали перед/після абзацу."
        },

        # Theme 2: Формати файлів текстових документів. Режими роботи в середовищі текстового процесора (5-8)
        {
            "task_order": 5,
            "question": "Які розширення файлів належать до форматів текстових документів? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D, E",
            "options_json": json.dumps([
                {"key": "A", "text": ".docx (документ Microsoft Word)"},
                {"key": "B", "text": ".odt (документ OpenDocument Text)"},
                {"key": "C", "text": ".txt (звичайний простий текст)"},
                {"key": "D", "text": ".pdf (Portable Document Format)"},
                {"key": "E", "text": ".rtf (Rich Text Format)"},
                {"key": "F", "text": ".mp3 (звуковий файл)"}
            ], ensure_ascii=False),
            "hint": ".docx, .odt, .txt, .pdf, .rtf — це формати текстових документів. .mp3 є аудіоформатом."
        },
        {
            "task_order": 6,
            "question": "У чому полягає головна особливість формату простого тексту (.txt)?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Зберігає виключно послідовність символів кодування без шрифтів, кольорів, таблиць та малюнків, завдяки чому має мінімальний розмір"},
                {"key": "B", "text": "Автоматично шифрує документ паролем при збереженні"},
                {"key": "C", "text": "Займає значно більше пам'яті, ніж документ .docx з малюнками"},
                {"key": "D", "text": "Може відкриватися виключно на комп'ютерах компанії Apple"}
            ], ensure_ascii=False),
            "hint": "Формат .txt не зберігає жодного оформлення чи графіки, тому є універсальним і займає мінімальний обсяг пам'яті."
        },
        {
            "task_order": 7,
            "question": "У якому режимі роботи в Google Docs внесені правки не змінюють текст остаточно, а відображаються у вигляді кольорових пропозицій для підтвердження автором?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Режим «Пропонування» (Suggesting)"},
                {"key": "B", "text": "Режим «Редагування» (Editing)"},
                {"key": "C", "text": "Режим «Перегляд» (Viewing)"},
                {"key": "D", "text": "Режим «Друк»"}
            ], ensure_ascii=False),
            "hint": "У режимі «Пропонування» всі зміни зберігаються як пропозиції, які власник документа може прийняти (✓) або відхилити (✕)."
        },
        {
            "task_order": 8,
            "question": "Які режими перегляду документа доступні в середовищі Microsoft Word на вкладці «Вигляд»? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D",
            "options_json": json.dumps([
                {"key": "A", "text": "Розмітка сторінки (Print Layout) — відображення документа у вигляді друкованих аркушів"},
                {"key": "B", "text": "Режим читання (Read Mode) — оптимізований вигляд для зручного читання тексту"},
                {"key": "C", "text": "Веб-документ (Web Layout) — вигляд сторінки як у веб-браузері без поділу на аркуші"},
                {"key": "D", "text": "Структура (Outline) — перегляд ієрархічної структури заголовків документа"},
                {"key": "E", "text": "Режим дефрагментації диска"}
            ], ensure_ascii=False),
            "hint": "Microsoft Word підтримує режими: Розмітка сторінки, Режим читання, Веб-документ, Структура та Чернетка."
        },

        # Theme 3: Робота з кількома документами (9-11)
        {
            "task_order": 9,
            "question": "Яку комбінацію клавіш або команду меню найзручніше використати для швидкого перемикання між кількома відкритими вікнами документів Microsoft Word?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Комбінацію Ctrl + F6 (або Alt + Tab) чи меню «Вигляд» ➔ «Перейти до іншого вікна»"},
                {"key": "B", "text": "Закрити текстовий процесор та відкрити його знову"},
                {"key": "C", "text": "Комбінацію Ctrl + Shift + Esc"},
                {"key": "D", "text": "Натиснути клавішу живлення комп'ютера"}
            ], ensure_ascii=False),
            "hint": "Швидке перемикання між відкритими вікнами Word виконується через Ctrl + F6 або меню «Вигляд» ➔ «Перейти до іншого вікна»."
        },
        {
            "task_order": 10,
            "question": "Які можливості надає користувачеві режим одночасної роботи з кількома документами чи вікнами в текстовому процесорі? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C",
            "options_json": json.dumps([
                {"key": "A", "text": "Перегляд двох документів поруч на екрані для їх візуального порівняння («Поруч» / View Side by Side)"},
                {"key": "B", "text": "Швидке копіювання або переміщення фрагментів тексту й таблиць між документами через буфер обміну"},
                {"key": "C", "text": "Синхронне прокручування двох документів одночасно для зіставлення тексту"},
                {"key": "D", "text": "Автоматичний переклад тексту на всі мови світу без інтернету"}
            ], ensure_ascii=False),
            "hint": "Робота з кількома вікнами дозволяє копіювати дані, розташовувати вікна поруч та синхронно їх прокручувати для порівняння."
        },
        {
            "task_order": 11,
            "question": "Яке призначення має інструмент «Розділити» (Split) на вкладці «Вигляд» у текстовому процесорі?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Розділяє вікно поточного документа на дві робочі області для одночасного перегляду та редагування різних сторінок того самого файлу"},
                {"key": "B", "text": "Фізично розрізає файл на два окремі файли на диску"},
                {"key": "C", "text": "Видаляє всі парні сторінки з документа"},
                {"key": "D", "text": "Перетворює текстовий документ на слайди презентації PowerPoint"}
            ], ensure_ascii=False),
            "hint": "Команда «Розділити» (Split) розбиває одне вікно документа на дві частини, щоб бачити, наприклад, початок і кінець великого тексту одночасно."
        },

        # Theme 4: Створення в текстовому документі багаторівневих списків (12-14)
        {
            "task_order": 12,
            "question": "Що являє собою багаторівневий список у текстовому документі?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Список із деревоподібною ієрархічною структурою, де елементи підпорядковані один одному з різними рівнями вкладеності (наприклад: 1 ➔ 1.1 ➔ 1.1.1)"},
                {"key": "B", "text": "Звичайний список, де кожен рядок розфарбовано іншим кольором шрифту"},
                {"key": "C", "text": "Таблиця з двома стовпцями без видимих меж"},
                {"key": "D", "text": "Текст, розміщений у п'ять вузьких колонок на сторінці"}
            ], ensure_ascii=False),
            "hint": "Багаторівневий список організовує пункти за рівнями підпорядкування та ієрархії."
        },
        {
            "task_order": 13,
            "question": "Яку клавішу найшвидше натиснути на початку рядка елемента списку, щоб понизити його рівень (збільшити відступ / перевести в підпункт)?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Клавішу Tab"},
                {"key": "B", "text": "Клавішу Esc"},
                {"key": "C", "text": "Клавішу Caps Lock"},
                {"key": "D", "text": "Клавішу Delete"}
            ], ensure_ascii=False),
            "hint": "Натискання клавіші Tab на початку рядка списку збільшує відступ і переводить пункт на один рівень глибше (понижує рівень)."
        },
        {
            "task_order": 14,
            "question": "Якими способами можна підвищити рівень елемента в багаторівневому списку (зменшити відступ / повернути на вищий рівень ієрархії)? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C",
            "options_json": json.dumps([
                {"key": "A", "text": "Натиснути комбінацію клавіш Shift + Tab"},
                {"key": "B", "text": "Натиснути клавішу Backspace на початку рядка пункту списку"},
                {"key": "C", "text": "Натиснути кнопку «Зменшити відступ» (Decrease Indent) на вкладці «Основне»"},
                {"key": "D", "text": "Натиснути комбінацію Ctrl + Alt + Delete"}
            ], ensure_ascii=False),
            "hint": "Підвищити рівень пункту списку можна за допомогою Shift + Tab, Backspace або кнопки «Зменшити відступ»."
        },

        # Theme 5: Створення в текстовому документі спеціальних символів та формул (15-17)
        {
            "task_order": 15,
            "question": "За допомогою якого інструмента у текстових процесорах (Word, Google Docs) створюють складні математичні формули з дробами, радикалами, матрицями та інтегралами?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Вбудованого редактора формул (вкладка «Вставлення» ➔ «Рівняння» / «Формула»)"},
                {"key": "B", "text": "Стандартної програми Блокнот"},
                {"key": "C", "text": "Графічного редактора Paint шляхом малювання формули олівцем"},
                {"key": "D", "text": "Інструмента фігурного тексту «WordArt»"}
            ], ensure_ascii=False),
            "hint": "Для математичних виразів використовується вбудований конструктор/редактор формул (Equation Editor)."
        },
        {
            "task_order": 16,
            "question": "Де в меню Microsoft Word знаходиться команда для вставки спеціальних символів, відсутніх на клавіатурі (наприклад: ©, ®, €, ™, грецькі літери α, β, π, стрілки →)?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Вкладка «Вставлення» ➔ група «Символи» ➔ кнопка «Символ» (пункт «Інші символи...»)"},
                {"key": "B", "text": "Вкладка «Файл» ➔ «Друк»"},
                {"key": "C", "text": "Вкладка «Макет» ➔ «Поля»"},
                {"key": "D", "text": "Вкладка «Вигляд» ➔ «Масштаб»"}
            ], ensure_ascii=False),
            "hint": "Спеціальні символи вставляються через вкладку «Вставлення» ➔ «Символ»."
        },
        {
            "task_order": 17,
            "question": "Які типи математичних конструкцій можна створити за допомогою панелі конструктора формул (Equation Tools)? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D",
            "options_json": json.dumps([
                {"key": "A", "text": "Звичайні дроби (вертикальні, косі)"},
                {"key": "B", "text": "Верхні та нижні індекси (степені x², індекси aₙ)"},
                {"key": "C", "text": "Радикали (квадратні √x та корені довільного степеня ⁿ√x)"},
                {"key": "D", "text": "Знаки інтегралів (∫), сум (∑) та математичні дужки різних типів"},
                {"key": "E", "text": "Автоматичний звуковий супровід виразу"}
            ], ensure_ascii=False),
            "hint": "Редактор формул містить шаблони дробів, індексів, коренів, інтегралів, сум, тригонометричних функцій та дужок."
        },

        # Theme 6: Створення в текстовому документі стовпців, розділів, колонтитулів (18-20)
        {
            "task_order": 18,
            "question": "Для чого в текстовому процесорі використовують розриви розділів («З наступної сторінки», «Поточний/неперервний»)?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Щоб застосувати різні параметри форматування (орієнтацію сторінки, поля, колонтитули, кількість шпальт) до окремих частин одного документа"},
                {"key": "B", "text": "Щоб автоматично виправити всі граматичні помилки в тексті"},
                {"key": "C", "text": "Щоб видалити весь текст документа"},
                {"key": "D", "text": "Щоб змінити колір корпусу монітора"}
            ], ensure_ascii=False),
            "hint": "Розриви розділів дозволяють задавати різні параметри сторінок (наприклад, альбомну орієнтацію для однієї сторінки, різні колонтитули або стовпці) у межах одного файлу."
        },
        {
            "task_order": 19,
            "question": "Яку інформацію традиційно розміщують у верхньому або нижньому колонтитулі сторінок документа? (Оберіть усі правильні варіанти)",
            "task_type": "multichoice",
            "correct_answer": "A, B, C, D, E",
            "options_json": json.dumps([
                {"key": "A", "text": "Номери сторінок (автоматична нумерація)"},
                {"key": "B", "text": "Назву книги, документа або поточного розділу"},
                {"key": "C", "text": "Прізвище та ініціали автора чи назву організації"},
                {"key": "D", "text": "Логотип навчального закладу або герб"},
                {"key": "E", "text": "Поточну дату чи версію документа"}
            ], ensure_ascii=False),
            "hint": "У колонтитулах розміщують номери сторінок, заголовки, автора, дату, логотипи тощо."
        },
        {
            "task_order": 20,
            "question": "Як налаштувати колонтитули так, щоб на першій (титульній) сторінці документа не відображалися верхній колонтитул та номер сторінки?",
            "task_type": "choice",
            "correct_answer": "A",
            "options_json": json.dumps([
                {"key": "A", "text": "Увімкнути параметр «Особливий для першої сторінки» (Different First Page) на вкладці «Конструктор колонтитулів»"},
                {"key": "B", "text": "Стерти перший аркуш гумкою"},
                {"key": "C", "text": "Закрити вкладку «Вставлення»"},
                {"key": "D", "text": "Зберегти документ як файл без оформлення .txt"}
            ], ensure_ascii=False),
            "hint": "Опція «Особливий для першої сторінки» (Different First Page) робить колонтитул титульної сторінки незалежним (порожнім)."
        }
    ]

    upsert_topic_tasks(db, text_test_topic.id, test_20_tasks_data)

    print("Database seeding completed successfully.")
