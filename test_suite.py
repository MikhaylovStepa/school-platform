import unittest
import uuid
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database
from app.models import Grade, Subject, Topic, Task, User, TaskAttempt, StudentPresence

class TestSchoolPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        seed_database(db)
        db.close()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        db = SessionLocal()
        try:
            db.query(User).filter(User.device_id.like("test-%")).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

    def test_01_hierarchy_and_tasks_count(self):
        resp = self.client.get("/api/hierarchy")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        grades = data["grades"]
        self.assertGreaterEqual(len(grades), 2)

        grade6 = next((g for g in grades if "6" in g["name"]), None)
        self.assertIsNotNone(grade6)
        
        math = next((s for s in grade6["subjects"] if s["slug"] == "math"), None)
        self.assertIsNotNone(math)
        self.assertEqual(len(math["topics"]), 22)

        expected_room_codes = {
            "math-6-add", "math-6-add-2", "math-6-add-3",
            "math-6-sub", "math-6-sub-2", "math-6-sub-3",
            "math-6-mixed", "math-6-mixed-2", "math-6-mixed-3",
            "math-6-mul-1", "math-6-mul-2",
            "math-6-div-1", "math-6-div-2",
            "math-6-abs", "math-6-opp",
            "math-6-coefficient", "math-6-brackets-signs",
            "math-6-combining-like-terms", "math-6-divisibility",
            "math-6-prime-factorization", "math-6-control-1", "math-6-control-2"
        }
        actual_room_codes = {t["room_code"] for t in math["topics"]}
        self.assertTrue(expected_room_codes.issubset(actual_room_codes))

        for topic in math["topics"]:
            if topic["room_code"] == "math-6-prime-factorization":
                self.assertEqual(topic["tasks_count"], 5)
            elif topic["room_code"] == "math-6-control-1":
                self.assertEqual(topic["tasks_count"], 17)
            elif topic["room_code"] == "math-6-control-2":
                self.assertEqual(topic["tasks_count"], 23)
            else:
                self.assertEqual(topic["tasks_count"], 20)

    def test_02_task_constraints_and_correctness(self):
        db = SessionLocal()
        math_subject = db.query(Subject).filter_by(slug="math").first()
        arithmetic_topics = [
            "math-6-add", "math-6-add-2", "math-6-add-3",
            "math-6-sub", "math-6-sub-2", "math-6-sub-3",
            "math-6-mixed", "math-6-mixed-2", "math-6-mixed-3",
            "math-6-mul-1", "math-6-mul-2",
            "math-6-div-1", "math-6-div-2",
            "math-6-abs", "math-6-opp"
        ]
        tasks = db.query(Task).join(Topic).filter(Topic.subject_id == math_subject.id, Topic.room_code.in_(arithmetic_topics)).all()
        self.assertEqual(len(tasks), 300)

        for t in tasks:
            correct_ans = int(t.correct_answer)
            q = t.question

            if "Знайдіть число, протилежне до" in q:
                num_str = q.replace("Знайдіть число, протилежне до ", "").replace("(", "").replace(")", "").strip()
                val = int(num_str)
                self.assertTrue(-20 <= val <= 20 and val != 0)
                self.assertEqual(correct_ans, -val)
            elif "|" in q:
                num_str = q.replace("Обчисліть: |", "").replace("| = ?", "").strip()
                val = int(num_str)
                self.assertTrue(-20 <= val <= 20 and val != 0)
                self.assertEqual(correct_ans, abs(val))
            elif "·" in q:
                expr = q.replace("Обчисліть: ", "").replace(" = ?", "").replace("·", "*")
                eval_ans = eval(expr)
                self.assertEqual(correct_ans, eval_ans)
            elif ":" in q:
                expr = q.replace("Обчисліть: ", "").replace(" = ?", "").replace(":", "//")
                eval_ans = eval(expr)
                self.assertEqual(correct_ans, eval_ans)
            else:
                expr = q.replace("Обчисліть: ", "").replace(" = ?", "")
                eval_ans = eval(expr)
                self.assertEqual(correct_ans, eval_ans, f"Answer mismatch for {expr}: expected {correct_ans}, calculated {eval_ans}")
        db.close()

    def test_03_student_auth_and_flow(self):
        device_id = f"test-dev-{uuid.uuid4()}"
        # 1. Student login with grade and letter
        resp = self.client.post("/api/auth/student-session", json={
            "name": "Тестовий Учень",
            "device_id": device_id,
            "grade_level": 6,
            "class_letter": "Б"
        })
        self.assertEqual(resp.status_code, 200)
        student = resp.json()
        self.assertEqual(student["name"], "Тестовий Учень")
        self.assertEqual(student["role"], "student")
        self.assertEqual(student["grade_level"], 6)
        self.assertEqual(student["class_letter"], "Б")
        self.assertEqual(student["class_name"], "6-Б")
        user_id = student["user_id"]

        # 2. Get tasks for student in new room
        resp = self.client.get(f"/api/tasks/topic/math-6-mul-1?user_id={user_id}")
        self.assertEqual(resp.status_code, 200)
        topic_data = resp.json()
        tasks = topic_data["tasks"]
        self.assertEqual(len(tasks), 20)
        first_task = tasks[0]

        # 3. Submit wrong answer
        resp = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": first_task["id"],
            "submitted_answer": "9999", # definitely wrong
            "room_code": "math-6-mul-1"
        })
        self.assertEqual(resp.status_code, 200)
        wrong_res = resp.json()
        self.assertFalse(wrong_res["is_correct"])
        self.assertEqual(wrong_res["attempt_number"], 1)
        self.assertIsNotNone(wrong_res["hint"])

        # 4. Submit correct answer
        db = SessionLocal()
        task_in_db = db.query(Task).filter_by(id=first_task["id"]).first()
        actual_ans = task_in_db.correct_answer
        db.close()

        resp = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": first_task["id"],
            "submitted_answer": actual_ans,
            "room_code": "math-6-mul-1"
        })
        self.assertEqual(resp.status_code, 200)
        correct_res = resp.json()
        self.assertTrue(correct_res["is_correct"])
        self.assertEqual(correct_res["attempt_number"], 2)

    def test_04_teacher_auth_and_dashboard(self):
        # 1. Wrong teacher password
        resp = self.client.post("/api/auth/teacher-login", json={
            "name": "Вчитель",
            "password": "wrong-password",
            "device_id": "teacher-dev-1"
        })
        self.assertEqual(resp.status_code, 401)

        # 2. Correct teacher password
        resp = self.client.post("/api/auth/teacher-login", json={
            "name": "Марія Іванівна",
            "password": "123456",
            "device_id": "teacher-dev-1"
        })
        self.assertEqual(resp.status_code, 200)
        teacher_data = resp.json()
        self.assertEqual(teacher_data["role"], "teacher")

        # 3. Create students with different classes for monitoring
        student_a_resp = self.client.post("/api/auth/student-session", json={
            "name": "Учень 6-А Класу",
            "device_id": f"test-monitor-a-{uuid.uuid4()}",
            "grade_level": 6,
            "class_letter": "А"
        })
        self.assertEqual(student_a_resp.status_code, 200)
        student_a_id = student_a_resp.json()["user_id"]

        student_b_resp = self.client.post("/api/auth/student-session", json={
            "name": "Учень 6-Б Класу",
            "device_id": f"test-monitor-b-{uuid.uuid4()}",
            "grade_level": 6,
            "class_letter": "Б"
        })
        self.assertEqual(student_b_resp.status_code, 200)
        student_b_id = student_b_resp.json()["user_id"]

        # 4. Heartbeat student presences in math-6-mul-1
        self.client.post("/api/presence/heartbeat", json={
            "user_id": student_a_id,
            "room_code": "math-6-mul-1",
            "is_tab_active": True,
            "is_online": True,
            "current_task_order": 1
        })
        self.client.post("/api/presence/heartbeat", json={
            "user_id": student_b_id,
            "room_code": "math-6-mul-1",
            "is_tab_active": True,
            "is_online": True,
            "current_task_order": 1
        })

        # 5. Check Teacher Dashboard (all classes)
        resp = self.client.get("/api/teacher/rooms/math-6-mul-1/dashboard")
        self.assertEqual(resp.status_code, 200)
        dash = resp.json()
        self.assertEqual(dash["room"]["room_code"], "math-6-mul-1")
        self.assertGreaterEqual(len(dash["students"]), 2)

        # 6. Check Teacher Dashboard filtered by 6-А
        resp_6a = self.client.get("/api/teacher/rooms/math-6-mul-1/dashboard?class_name=6-А")
        self.assertEqual(resp_6a.status_code, 200)
        dash_6a = resp_6a.json()
        student_names_6a = [s["name"] for s in dash_6a["students"]]
        self.assertIn("Учень 6-А Класу", student_names_6a)
        self.assertNotIn("Учень 6-Б Класу", student_names_6a)

    def test_05_html_routes(self):
        routes = ["/", "/hierarchy", "/room/math-6-add", "/teacher/room/math-6-add"]
        for r in routes:
            resp = self.client.get(r)
            self.assertEqual(resp.status_code, 200, f"Route {r} failed with status {resp.status_code}")

    def test_06_student_frontend_uses_api_user_id(self):
        student_js = Path("app/static/js/student.js").read_text(encoding="utf-8")
        self.assertIn("currentUser.user_id", student_js)
        self.assertNotIn("currentUser.id", student_js)

    def test_07_informatics_8class_topic_and_tasks(self):
        # 1. Check Grade 8 in hierarchy
        resp = self.client.get("/api/hierarchy")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        grade8 = next((g for g in data["grades"] if "8" in g["name"]), None)
        self.assertIsNotNone(grade8)

        info_subject = next((s for s in grade8["subjects"] if s["slug"] == "informatics"), None)
        self.assertIsNotNone(info_subject)
        self.assertGreaterEqual(len(info_subject["topics"]), 2)

        info_topic = next(t for t in info_subject["topics"] if t["room_code"] == "info-8-compress")
        self.assertEqual(info_topic["room_code"], "info-8-compress")
        self.assertEqual(info_topic["tasks_count"], 10)

        # 2. Check Static Files Downloadability
        materials = [
            "/static/materials/8class/compress_archive01/Informatyka_8_Stysnennia_danykh_i_arkhivuvannia.pptx",
            "/static/materials/8class/compress_archive01/archive_lesson1.txt",
            "/static/materials/8class/compress_archive01/franko-ivan-iakovych-farbovanyy-lys.docx",
            "/static/materials/8class/compress_archive01/vecteezy_background-of-pebbles-and-tree-branches_25771406.jpeg",
            "/static/materials/8class/compress_archive01/preview_orig.jpg",
            "/static/materials/8class/compress_archive01/preview_low_quality.jpg"
        ]
        for m in materials:
            file_resp = self.client.get(m)
            self.assertEqual(file_resp.status_code, 200, f"Static material {m} returned {file_resp.status_code}")

        # 3. Student 8th Grade login and room join
        dev_id = f"test-info8-{uuid.uuid4()}"
        login_resp = self.client.post("/api/auth/student-session", json={
            "name": "Олексій 8-А",
            "device_id": dev_id,
            "grade_level": 8,
            "class_letter": "А"
        })
        self.assertEqual(login_resp.status_code, 200)
        st_data = login_resp.json()
        self.assertEqual(st_data["grade_level"], 8)
        self.assertEqual(st_data["class_name"], "8-А")
        user_id = st_data["user_id"]

        # 4. Fetch tasks
        topic_resp = self.client.get(f"/api/tasks/topic/info-8-compress?user_id={user_id}")
        self.assertEqual(topic_resp.status_code, 200)
        t_data = topic_resp.json()
        tasks = t_data["tasks"]
        self.assertEqual(len(tasks), 10)

        # 5. Test Practical Answers Submission
        # Task 3: archive_lesson1.txt compression ratio: 327
        task_3 = next(t for t in tasks if t["task_order"] == 3)
        sub_3 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_3["id"],
            "submitted_answer": "327",
            "room_code": "info-8-compress"
        })
        self.assertEqual(sub_3.status_code, 200)
        self.assertTrue(sub_3.json()["is_correct"])

        # Task 4: docx ratio: 1.13
        task_4 = next(t for t in tasks if t["task_order"] == 4)
        sub_4 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_4["id"],
            "submitted_answer": "1,13", # test comma support
            "room_code": "info-8-compress"
        })
        self.assertEqual(sub_4.status_code, 200)
        self.assertTrue(sub_4.json()["is_correct"])

        # Task 6: image compression ratio: 10
        task_6 = next(t for t in tasks if t["task_order"] == 6)
        sub_6 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_6["id"],
            "submitted_answer": "10 разів",
            "room_code": "info-8-compress"
        })
        self.assertEqual(sub_6.status_code, 200)
        self.assertTrue(sub_6.json()["is_correct"])

        # Task 1: choice A
        task_1 = next(t for t in tasks if t["task_order"] == 1)
        sub_1 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_1["id"],
            "submitted_answer": "A",
            "room_code": "info-8-compress"
        })
        self.assertEqual(sub_1.status_code, 200)
        self.assertTrue(sub_1.json()["is_correct"])

        # 6. Verify HTML Room page for Informatics
        room_page = self.client.get("/room/info-8-compress")
        self.assertEqual(room_page.status_code, 200)

        teacher_room_page = self.client.get("/teacher/room/info-8-compress")
        self.assertEqual(teacher_room_page.status_code, 200)

    def test_08_archive_operations_cabinet(self):
        response = self.client.get("/api/hierarchy")
        self.assertEqual(response.status_code, 200)
        grade8 = next(g for g in response.json()["grades"] if g["slug"] == "grade-8")
        informatics = next(s for s in grade8["subjects"] if s["slug"] == "informatics")
        topic = next((t for t in informatics["topics"] if t["room_code"] == "info-8-archive-operations"), None)
        self.assertIsNotNone(topic)
        self.assertEqual(topic["tasks_count"], 9)

        for material in (
            "/static/materials/8class/operation_with_archives/compress_archive01.zip",
            "/static/materials/8class/operation_with_archives/6711626.png",
            "/static/materials/8class/operation_with_archives/742940.png",
            "/static/materials/8class/operation_with_archives/franko-ivan-iakovych-kameniari647.docx",
            "/static/materials/8class/operation_with_archives/тексти%20з%20малюнками.docx",
        ):
            resp = self.client.get(material)
            self.assertEqual(resp.status_code, 200)
            self.assertGreater(len(resp.content), 0)

        room_page = self.client.get("/room/info-8-archive-operations")
        self.assertEqual(room_page.status_code, 200)
        self.assertIn("archive-sizes-form", room_page.text)
        self.assertIn("compress_archive01.zip", room_page.text)
        self.assertIn("Каменярі", room_page.text)

        student_js = Path("app/static/js/student.js").read_text(encoding="utf-8")
        self.assertIn("function handleArchiveSizesForm", student_js)
        self.assertIn("info-8-archive-sizes", student_js)

    def test_09_informatics_9class_text_formats_cabinet(self):
        hierarchy = self.client.get("/api/hierarchy")
        self.assertEqual(hierarchy.status_code, 200)
        grade9 = next((g for g in hierarchy.json()["grades"] if g["slug"] == "grade-9"), None)
        self.assertIsNotNone(grade9)

        informatics = next((s for s in grade9["subjects"] if s["slug"] == "informatics"), None)
        self.assertIsNotNone(informatics)
        topic = next((t for t in informatics["topics"] if t["room_code"] == "info-9-formats"), None)
        self.assertIsNotNone(topic)
        self.assertEqual(topic["tasks_count"], 10)

        for material in (
            "/static/materials/9class/text_formats/Informatyka_9_Formaty_faіliv_Rezhymy_Google_Docs_v2.pptx",
            "/static/materials/9class/text_formats/тексти%20з%20малюнками.docx",
        ):
            response = self.client.get(material)
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.content), 0)

        room_page = self.client.get("/room/info-9-formats")
        self.assertEqual(room_page.status_code, 200)
        html = room_page.text
        self.assertIn("file-formats-size-form", html)
        self.assertIn("1s-QvJ74JqI3qunfwcdKrfA5jNia4RnxBip7eElOfZ1s", html)

        student_js = Path("app/static/js/student.js").read_text(encoding="utf-8")
        self.assertIn("const slidesData9", student_js)
        self.assertIn("function handleFormatsSizeForm", student_js)
        self.assertIn("info-9-formats-file-sizes", student_js)

    def test_10_offline_vendor_assets(self):
        # 1. Verify all vendor files are served locally
        vendor_assets = [
            "/static/vendor/tailwindcss/tailwind.js",
            "/static/vendor/fontawesome/css/all.min.css",
            "/static/vendor/fontawesome/webfonts/fa-solid-900.woff2",
            "/static/vendor/fontawesome/webfonts/fa-brands-400.woff2",
            "/static/vendor/fontawesome/webfonts/fa-regular-400.woff2",
            "/static/vendor/marked/marked.min.js",
            "/static/vendor/confetti/confetti.browser.min.js",
        ]
        for asset in vendor_assets:
            resp = self.client.get(asset)
            self.assertEqual(resp.status_code, 200, f"Asset failed to load: {asset}")
            self.assertGreater(len(resp.content), 0, f"Asset empty: {asset}")

        # 2. Verify base.html and topic_student.html do not use external CDN scripts/styles
        home_page = self.client.get("/")
        self.assertEqual(home_page.status_code, 200)
        self.assertIn("/static/vendor/tailwindcss/tailwind.js", home_page.text)
        self.assertIn("/static/vendor/fontawesome/css/all.min.css", home_page.text)
        self.assertNotIn("cdn.tailwindcss.com", home_page.text)
        self.assertNotIn("cdnjs.cloudflare.com", home_page.text)

        room_page = self.client.get("/room/info-8-archive-operations")
        self.assertEqual(room_page.status_code, 200)
        self.assertIn("/static/vendor/marked/marked.min.js", room_page.text)
        self.assertIn("/static/vendor/confetti/confetti.browser.min.js", room_page.text)
        self.assertNotIn("cdn.jsdelivr.net", room_page.text)

    def test_11_informatics_9class_document_layout_cabinet(self):
        # 1. Verify Hierarchy API has Grade 9 -> Informatics -> Document Layout topic
        hierarchy = self.client.get("/api/hierarchy")
        self.assertEqual(hierarchy.status_code, 200)
        grade9 = next((g for g in hierarchy.json()["grades"] if g["slug"] == "grade-9"), None)
        self.assertIsNotNone(grade9)

        informatics = next((s for s in grade9["subjects"] if s["slug"] == "informatics"), None)
        self.assertIsNotNone(informatics)
        topic = next((t for t in informatics["topics"] if t["room_code"] == "info-9-document-layout"), None)
        self.assertIsNotNone(topic)
        self.assertEqual(topic["tasks_count"], 10)

        # 2. Verify static materials are served correctly
        for material in (
            "/static/materials/9class/document_layout/franko-ivan-iakovych-farbovanyy-lys.docx",
            "/static/materials/9class/document_layout/franko_logo.png",
            "/static/materials/9class/document_layout/header_icon.png",
        ):
            resp = self.client.get(material)
            self.assertEqual(resp.status_code, 200)
            self.assertGreater(len(resp.content), 0)

        # 3. Verify HTML Room page
        room_page = self.client.get("/room/info-9-document-layout")
        self.assertEqual(room_page.status_code, 200)
        html = room_page.text
        self.assertIn("lab-9-layout-content", html)
        self.assertIn("franko-...farbovanyy-lys.docx", html)
        self.assertIn("Іван Франко", html)

        # 4. Verify JS handles topic room
        student_js = Path("app/static/js/student.js").read_text(encoding="utf-8")
        self.assertIn("info-9-document-layout", student_js)
        self.assertIn("lab9Layout", student_js)

        # 5. Verify Student can fetch and answer tasks
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Учень 9 класу",
            "device_id": device_id,
            "grade_level": 9,
            "class_letter": "А"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        tasks_resp = self.client.get(f"/api/tasks/topic/info-9-document-layout?user_id={user_id}")
        self.assertEqual(tasks_resp.status_code, 200)
        tasks = tasks_resp.json()["tasks"]
        self.assertEqual(len(tasks), 10)

        # Submit answer to Task 1 (A)
        task_1 = next(t for t in tasks if t["task_order"] == 1)
        sub_resp = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_1["id"],
            "submitted_answer": "A",
            "room_code": "info-9-document-layout"
        })
        self.assertEqual(sub_resp.status_code, 200)
        self.assertTrue(sub_resp.json()["is_correct"])

    def test_12_grade_8_final_archives_and_reset_progress(self):
        # 1. Verify Topic & 20 tasks exist for info-8-final-archives
        hierarchy = self.client.get("/api/hierarchy")
        self.assertEqual(hierarchy.status_code, 200)
        grade8 = next((g for g in hierarchy.json()["grades"] if g["slug"] == "grade-8"), None)
        self.assertIsNotNone(grade8)
        informatics = next((s for s in grade8["subjects"] if s["slug"] == "informatics"), None)
        self.assertIsNotNone(informatics)
        topic = next((t for t in informatics["topics"] if t["room_code"] == "info-8-final-archives"), None)
        self.assertIsNotNone(topic)
        self.assertEqual(topic["tasks_count"], 20)

        # 2. Authenticate student
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Учень 8 класу (Підсумковий)",
            "device_id": device_id,
            "grade_level": 8,
            "class_letter": "А"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        # 3. Fetch topic tasks
        tasks_resp = self.client.get(f"/api/tasks/topic/info-8-final-archives?user_id={user_id}")
        self.assertEqual(tasks_resp.status_code, 200)
        tasks = tasks_resp.json()["tasks"]
        self.assertEqual(len(tasks), 20)

        # 4. Submit answers for first 3 tasks
        for t in tasks[:3]:
            sub_resp = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": "A",
                "room_code": "info-8-final-archives"
            })
            self.assertEqual(sub_resp.status_code, 200)
            self.assertTrue(sub_resp.json()["is_correct"])

        # Check dashboard shows solved_count = 3
        dash_resp = self.client.get("/api/teacher/rooms/info-8-final-archives/dashboard")
        self.assertEqual(dash_resp.status_code, 200)
        student_data = next((s for s in dash_resp.json()["students"] if s["user_id"] == user_id), None)
        self.assertIsNotNone(student_data)
        self.assertEqual(student_data["solved_count"], 3)

        # 5. Teacher resets progress for this student
        reset_resp = self.client.post(f"/api/teacher/rooms/info-8-final-archives/students/{user_id}/reset")
        self.assertEqual(reset_resp.status_code, 200)
        self.assertTrue(reset_resp.json()["success"])
        self.assertEqual(reset_resp.json()["deleted_attempts"], 3)

        # 6. Verify dashboard and student task list are reset
        dash_resp_after = self.client.get("/api/teacher/rooms/info-8-final-archives/dashboard")
        student_data_after = next((s for s in dash_resp_after.json()["students"] if s["user_id"] == user_id), None)
        self.assertIsNotNone(student_data_after)
        self.assertEqual(student_data_after["solved_count"], 0)
        self.assertEqual(student_data_after["total_attempts"], 0)

        tasks_resp_after = self.client.get(f"/api/tasks/topic/info-8-final-archives?user_id={user_id}")
        self.assertFalse(any(t["is_solved"] for t in tasks_resp_after.json()["tasks"]))

    def test_13_grade_6_advanced_math_cabinets(self):
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Учень 6 класу (Математика)",
            "device_id": device_id,
            "grade_level": 6,
            "class_letter": "В"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        # 1. Topic: Coefficient of Expression (math-6-coefficient)
        t1_resp = self.client.get(f"/api/tasks/topic/math-6-coefficient?user_id={user_id}")
        self.assertEqual(t1_resp.status_code, 200)
        t1_tasks = t1_resp.json()["tasks"]
        self.assertEqual(len(t1_tasks), 20)
        sub1 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t1_tasks[0]["id"],
            "submitted_answer": "-5",
            "room_code": "math-6-coefficient"
        })
        self.assertTrue(sub1.json()["is_correct"])

        # 2. Topic: Opening Brackets Signs (math-6-brackets-signs)
        t2_resp = self.client.get(f"/api/tasks/topic/math-6-brackets-signs?user_id={user_id}")
        self.assertEqual(t2_resp.status_code, 200)
        t2_tasks = t2_resp.json()["tasks"]
        self.assertEqual(len(t2_tasks), 20)
        sub2 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t2_tasks[0]["id"],
            "submitted_answer": "---",
            "room_code": "math-6-brackets-signs"
        })
        self.assertTrue(sub2.json()["is_correct"])

        # 3. Topic: Combining Like Terms (math-6-combining-like-terms)
        t3_resp = self.client.get(f"/api/tasks/topic/math-6-combining-like-terms?user_id={user_id}")
        self.assertEqual(t3_resp.status_code, 200)
        t3_tasks = t3_resp.json()["tasks"]
        self.assertEqual(len(t3_tasks), 20)
        sub3 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t3_tasks[0]["id"],
            "submitted_answer": "-7a",
            "room_code": "math-6-combining-like-terms"
        })
        self.assertTrue(sub3.json()["is_correct"])

        # 4. Topic: Divisibility Rules (math-6-divisibility)
        t4_resp = self.client.get(f"/api/tasks/topic/math-6-divisibility?user_id={user_id}")
        self.assertEqual(t4_resp.status_code, 200)
        t4_tasks = t4_resp.json()["tasks"]
        self.assertEqual(len(t4_tasks), 20)
        sub4 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t4_tasks[0]["id"],
            "submitted_answer": "A, C",
            "room_code": "math-6-divisibility"
        })
        self.assertTrue(sub4.json()["is_correct"])

        # 5. Topic: Prime Factorization (math-6-prime-factorization)
        t5_resp = self.client.get(f"/api/tasks/topic/math-6-prime-factorization?user_id={user_id}")
        self.assertEqual(t5_resp.status_code, 200)
        t5_tasks = t5_resp.json()["tasks"]
        self.assertEqual(len(t5_tasks), 5)
        sub5 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t5_tasks[0]["id"],
            "submitted_answer": "2, 2, 2, 3, 3, 7",
            "room_code": "math-6-prime-factorization"
        })
        self.assertTrue(sub5.json()["is_correct"])

    def test_14_prime_factorization_incorrect_factor_monitoring(self):
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Петрик П'яточкин",
            "device_id": device_id,
            "grade_level": 6,
            "class_letter": "А"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        # Fetch prime factorization tasks
        tasks_resp = self.client.get(f"/api/tasks/topic/math-6-prime-factorization?user_id={user_id}")
        self.assertEqual(tasks_resp.status_code, 200)
        task_504 = tasks_resp.json()["tasks"][0]

        # 1. Student selects an incorrect prime factor (e.g. 5 for 504 or 5 for 63)
        err_msg = "Невірний множник: 5 для числа 63 (не ділиться націло)"
        err_sub = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_504["id"],
            "submitted_answer": err_msg,
            "room_code": "math-6-prime-factorization"
        })
        self.assertEqual(err_sub.status_code, 200)
        self.assertFalse(err_sub.json()["is_correct"])
        self.assertEqual(err_sub.json()["attempt_number"], 1)

        # 2. Check that teacher dashboard reflects the incorrect factor attempt immediately
        dash_resp = self.client.get("/api/teacher/rooms/math-6-prime-factorization/dashboard")
        self.assertEqual(dash_resp.status_code, 200)
        dash_data = dash_resp.json()
        student_entry = next((s for s in dash_data["students"] if s["user_id"] == user_id), None)
        self.assertIsNotNone(student_entry)
        self.assertEqual(student_entry["total_attempts"], 1)
        self.assertEqual(student_entry["solved_count"], 0)

        task_progress = next((tp for tp in student_entry["tasks_progress"] if tp["task_id"] == task_504["id"]), None)
        self.assertIsNotNone(task_progress)
        self.assertFalse(task_progress["is_solved"])
        self.assertEqual(task_progress["attempt_count"], 1)
        self.assertFalse(task_progress["last_is_correct"])
        self.assertEqual(task_progress["last_answer"], err_msg)
        self.assertEqual(len(task_progress["history"]), 1)
        self.assertEqual(task_progress["history"][0]["submitted_answer"], err_msg)
        self.assertFalse(task_progress["history"][0]["is_correct"])

        # 3. Student selects another factor violating order (e.g. 7 before 3)
        err_order_msg = "Невірний порядок: обрано множник 7 для числа 63 (найменший дільник: 3)"
        err_order_sub = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_504["id"],
            "submitted_answer": err_order_msg,
            "room_code": "math-6-prime-factorization"
        })
        self.assertEqual(err_order_sub.status_code, 200)
        self.assertFalse(err_order_sub.json()["is_correct"])
        self.assertEqual(err_order_sub.json()["attempt_number"], 2)

        # 4. Student now provides the correct full factorization
        correct_sub = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": task_504["id"],
            "submitted_answer": "2, 2, 2, 3, 3, 7",
            "room_code": "math-6-prime-factorization"
        })
        self.assertEqual(correct_sub.status_code, 200)
        self.assertTrue(correct_sub.json()["is_correct"])
        self.assertEqual(correct_sub.json()["attempt_number"], 3)

        # 5. Teacher dashboard shows solved task with full attempt history
        dash_resp2 = self.client.get("/api/teacher/rooms/math-6-prime-factorization/dashboard")
        student_entry2 = next((s for s in dash_resp2.json()["students"] if s["user_id"] == user_id), None)
        self.assertEqual(student_entry2["solved_count"], 1)
        self.assertEqual(student_entry2["total_attempts"], 3)
        tp2 = next((tp for tp in student_entry2["tasks_progress"] if tp["task_id"] == task_504["id"]), None)
        self.assertTrue(tp2["is_solved"])
        self.assertEqual(len(tp2["history"]), 3)
        self.assertEqual(tp2["history"][0]["submitted_answer"], err_msg)
        self.assertEqual(tp2["history"][1]["submitted_answer"], err_order_msg)
        self.assertEqual(tp2["history"][2]["submitted_answer"], "2, 2, 2, 3, 3, 7")

    def test_15_math_6_control_work_flow(self):
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Оксана Коваленко",
            "device_id": device_id,
            "grade_level": 6,
            "class_letter": "А"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        # Fetch control work tasks
        tasks_resp = self.client.get(f"/api/tasks/topic/math-6-control-1?user_id={user_id}")
        self.assertEqual(tasks_resp.status_code, 200)
        tasks = tasks_resp.json()["tasks"]
        self.assertEqual(len(tasks), 17)

        # Task 1: Multichoice integers (10 options)
        t1 = tasks[0]
        self.assertEqual(t1["task_type"], "multichoice")
        sub1 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t1["id"],
            "submitted_answer": "A, C, D, F, H, J",
            "room_code": "math-6-control-1"
        })
        self.assertTrue(sub1.json()["is_correct"])

        # Tasks 2-4: Number line point placement (3 tasks: -4, 3, -6)
        t2, t3, t4 = tasks[1], tasks[2], tasks[3]
        for t, expected in [(t2, "-4"), (t3, "3"), (t4, "-6")]:
            self.assertEqual(t["task_type"], "number_line_point")
            sub = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": expected,
                "room_code": "math-6-control-1"
            })
            self.assertTrue(sub.json()["is_correct"])

        # Tasks 5-7: What is the coordinate of point (3 tasks: -5, 4, -2)
        t5, t6, t7 = tasks[4], tasks[5], tasks[6]
        for t, expected in [(t5, "-5"), (t6, "4"), (t7, "-2")]:
            self.assertEqual(t["task_type"], "number_line_read")
            sub = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": expected,
                "room_code": "math-6-control-1"
            })
            self.assertTrue(sub.json()["is_correct"])

        # Task 8: Midpoint of segment on number line (midpoint of -7 and 3 is -2)
        t8 = tasks[7]
        self.assertEqual(t8["task_type"], "number_line_midpoint")
        sub8 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t8["id"],
            "submitted_answer": "-2",
            "room_code": "math-6-control-1"
        })
        self.assertTrue(sub8.json()["is_correct"])

        # Tasks 9-16: 8 arithmetic tasks with integers (-10..10 / addition-subtraction -20..20, one modulo)
        arith_answers = ["-19", "7", "-13", "5", "-56", "54", "-9", "24"]
        for idx, expected in enumerate(arith_answers, start=8):
            t = tasks[idx]
            self.assertEqual(t["task_type"], "input_number")
            sub = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": expected,
                "room_code": "math-6-control-1"
            })
            self.assertTrue(sub.json()["is_correct"], f"Failed on arithmetic task {idx+1}: expected {expected}, got {sub.json()}")

        # Task 17: Rectangle on coordinate plane, perimeter and area
        t17 = tasks[16]
        self.assertEqual(t17["task_type"], "coordinate_plane_rect")
        sub17 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t17["id"],
            "submitted_answer": "P=20, S=24",
            "room_code": "math-6-control-1"
        })
        self.assertTrue(sub17.json()["is_correct"])

        # Verify teacher dashboard reflects 17 solved tasks for this student
        dash_resp = self.client.get("/api/teacher/rooms/math-6-control-1/dashboard")
        self.assertEqual(dash_resp.status_code, 200)
        dash_data = dash_resp.json()
        student_entry = next((s for s in dash_data["students"] if s["user_id"] == user_id), None)
        self.assertIsNotNone(student_entry)
        self.assertEqual(student_entry["solved_count"], 17)
        self.assertEqual(student_entry["total_attempts"], 17)

    def test_16_math_6_control_work_2_flow(self):
        # 1. Verify Topic exists in Hierarchy API
        hierarchy = self.client.get("/api/hierarchy")
        self.assertEqual(hierarchy.status_code, 200)
        grade6 = next((g for g in hierarchy.json()["grades"] if g["slug"] == "grade-6"), None)
        self.assertIsNotNone(grade6)
        math_subj = next((s for s in grade6["subjects"] if s["slug"] == "math"), None)
        self.assertIsNotNone(math_subj)
        topic = next((t for t in math_subj["topics"] if t["room_code"] == "math-6-control-2"), None)
        self.assertIsNotNone(topic)
        self.assertEqual(topic["tasks_count"], 23)

        # 2. Authenticate student
        device_id = f"test-dev-{uuid.uuid4()}"
        auth_resp = self.client.post("/api/auth/student-session", json={
            "name": "Богдан Шевченко",
            "device_id": device_id,
            "grade_level": 6,
            "class_letter": "Б"
        })
        self.assertEqual(auth_resp.status_code, 200)
        user_id = auth_resp.json()["user_id"]

        # 3. Fetch control work 2 tasks
        tasks_resp = self.client.get(f"/api/tasks/topic/math-6-control-2?user_id={user_id}")
        self.assertEqual(tasks_resp.status_code, 200)
        tasks = tasks_resp.json()["tasks"]
        self.assertEqual(len(tasks), 23)

        # 4. Tasks 1-20: Arithmetic with integers (verify correct and incorrect answers)
        arithmetic_expected = [
            "-18", "-5", "-11", "9", "-20", "7", "-11", "5", "-19", "17",
            "-7", "-20", "-42", "-40", "36", "56", "-4", "5", "-7", "-8"
        ]
        for i in range(20):
            t = tasks[i]
            expected = arithmetic_expected[i]
            # Verify incorrect answer is rejected
            wrong_sub = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": "999",
                "room_code": "math-6-control-2"
            })
            self.assertFalse(wrong_sub.json()["is_correct"], f"Task {i+1} incorrectly accepted '999'")

            # Verify correct answer is accepted
            sub = self.client.post("/api/tasks/submit", json={
                "user_id": user_id,
                "task_id": t["id"],
                "submitted_answer": expected,
                "room_code": "math-6-control-2"
            })
            self.assertTrue(sub.json()["is_correct"], f"Task {i+1} failed for answer {expected}: {sub.json()}")

        # 5. Task 21: Equation with module |3x - 3| = 9 -> roots 4 and -2 (test order independence: "-2; 4")
        t21 = tasks[20]
        self.assertEqual(t21["task_order"], 21)
        wrong_sub21 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t21["id"],
            "submitted_answer": "4; 2",
            "room_code": "math-6-control-2"
        })
        self.assertFalse(wrong_sub21.json()["is_correct"])

        sub21 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t21["id"],
            "submitted_answer": "-2; 4",
            "room_code": "math-6-control-2"
        })
        self.assertTrue(sub21.json()["is_correct"])

        # 6. Task 22: Equation (x + 3) * (2x + 6) = 0 -> root -3
        t22 = tasks[21]
        self.assertEqual(t22["task_order"], 22)
        wrong_sub22 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t22["id"],
            "submitted_answer": "3",
            "room_code": "math-6-control-2"
        })
        self.assertFalse(wrong_sub22.json()["is_correct"])

        sub22 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t22["id"],
            "submitted_answer": "-3",
            "room_code": "math-6-control-2"
        })
        self.assertTrue(sub22.json()["is_correct"])

        # 7. Task 23: Practical problem -> -10
        t23 = tasks[22]
        self.assertEqual(t23["task_order"], 23)
        wrong_sub23 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t23["id"],
            "submitted_answer": "10",
            "room_code": "math-6-control-2"
        })
        self.assertFalse(wrong_sub23.json()["is_correct"])

        sub23 = self.client.post("/api/tasks/submit", json={
            "user_id": user_id,
            "task_id": t23["id"],
            "submitted_answer": "-10",
            "room_code": "math-6-control-2"
        })
        self.assertTrue(sub23.json()["is_correct"])

        # 8. Check Teacher Dashboard
        dash_resp = self.client.get("/api/teacher/rooms/math-6-control-2/dashboard")
        self.assertEqual(dash_resp.status_code, 200)
        dash_data = dash_resp.json()
        student_entry = next((s for s in dash_data["students"] if s["user_id"] == user_id), None)
        self.assertIsNotNone(student_entry)
        self.assertEqual(student_entry["solved_count"], 23)
        self.assertEqual(student_entry["total_attempts"], 46)

if __name__ == "__main__":
    unittest.main()
