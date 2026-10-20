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
        self.assertEqual(len(math["topics"]), 15)

        expected_room_codes = {
            "math-6-add", "math-6-add-2", "math-6-add-3",
            "math-6-sub", "math-6-sub-2", "math-6-sub-3",
            "math-6-mixed", "math-6-mixed-2", "math-6-mixed-3",
            "math-6-mul-1", "math-6-mul-2",
            "math-6-div-1", "math-6-div-2",
            "math-6-abs", "math-6-opp"
        }
        actual_room_codes = {t["room_code"] for t in math["topics"]}
        self.assertTrue(expected_room_codes.issubset(actual_room_codes))

        # Check each topic has exactly 20 tasks
        for topic in math["topics"]:
            self.assertEqual(topic["tasks_count"], 20)

    def test_02_task_constraints_and_correctness(self):
        db = SessionLocal()
        math_subject = db.query(Subject).filter_by(slug="math").first()
        tasks = db.query(Task).join(Topic).filter(Topic.subject_id == math_subject.id).all()
        self.assertGreaterEqual(len(tasks), 300)

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

if __name__ == "__main__":
    unittest.main()
