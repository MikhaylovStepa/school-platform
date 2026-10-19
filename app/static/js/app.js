// Global App Utility & Authentication Helper

function getDeviceId() {
    let deviceId = localStorage.getItem("school_device_id");
    if (!deviceId) {
        deviceId = "dev-" + Math.random().toString(36).substring(2, 12) + "-" + Date.now().toString(36);
        localStorage.setItem("school_device_id", deviceId);
    }
    return deviceId;
}

function getSavedUser() {
    const raw = localStorage.getItem("school_user");
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

function saveUser(userData) {
    localStorage.setItem("school_user", JSON.stringify(userData));
    updateNavUserBadge();
}

function appLogout() {
    localStorage.removeItem("school_user");
    window.location.href = "/";
}

function updateNavUserBadge() {
    const user = getSavedUser();
    const badge = document.getElementById("nav-user-badge");
    const nameEl = document.getElementById("nav-user-name");
    const iconEl = document.getElementById("nav-user-role-icon");
    const logoutBtn = document.getElementById("nav-logout-btn");

    if (user && badge && nameEl) {
        if (user.role === "teacher") {
            nameEl.textContent = user.name;
            iconEl.innerHTML = `<i class="fa-solid fa-chalkboard-user text-indigo-600"></i>`;
            badge.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-200 text-xs sm:text-sm font-medium text-indigo-900";
        } else {
            const classInfo = user.class_name || (user.grade_level ? `${user.grade_level}-${user.class_letter || 'Б'}` : "");
            nameEl.textContent = classInfo ? `${user.name} (${classInfo})` : user.name;
            iconEl.innerHTML = `<i class="fa-solid fa-user-graduate text-emerald-600"></i>`;
            badge.className = "flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs sm:text-sm font-medium text-emerald-900";
        }
        badge.classList.remove("hidden");
        badge.classList.add("flex");
        if (logoutBtn) logoutBtn.classList.remove("hidden");
    } else if (badge) {
        badge.classList.add("hidden");
        if (logoutBtn) logoutBtn.classList.add("hidden");
    }
}

async function handleStudentLogin(e) {
    e.preventDefault();
    const name = document.getElementById("student-name-input").value.trim();
    if (!name) return;

    const gradeLevel = parseInt(document.getElementById("student-grade-select")?.value || "6", 10);
    const classLetter = document.getElementById("student-letter-select")?.value || "Б";

    const deviceId = getDeviceId();
    try {
        const resp = await fetch("/api/auth/student-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                device_id: deviceId,
                grade_level: gradeLevel,
                class_letter: classLetter
            })
        });
        const data = await resp.json();
        if (resp.ok) {
            saveUser(data);
            window.location.href = "/hierarchy";
        } else {
            alert(data.detail || "Помилка входу");
        }
    } catch (err) {
        console.error(err);
        alert("Помилка з'єднання з сервером.");
    }
}

async function handleTeacherLogin(e) {
    e.preventDefault();
    const name = document.getElementById("teacher-name-input").value.trim();
    const password = document.getElementById("teacher-password-input").value.trim();
    const errBox = document.getElementById("teacher-error");
    if (errBox) errBox.classList.add("hidden");

    const deviceId = getDeviceId();
    try {
        const resp = await fetch("/api/auth/teacher-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, password, device_id: deviceId })
        });
        const data = await resp.json();
        if (resp.ok) {
            saveUser(data);
            window.location.href = "/hierarchy";
        } else {
            if (errBox) {
                errBox.textContent = data.detail || "Невірний пароль вчителя";
                errBox.classList.remove("hidden");
            } else {
                alert(data.detail || "Невірний пароль");
            }
        }
    } catch (err) {
        console.error(err);
        alert("Помилка з'єднання з сервером.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    updateNavUserBadge();
    // Prefill name and class if exists on login page
    const user = getSavedUser();
    if (user) {
        const sInput = document.getElementById("student-name-input");
        const tInput = document.getElementById("teacher-name-input");
        const gradeSelect = document.getElementById("student-grade-select");
        const letterSelect = document.getElementById("student-letter-select");

        if (sInput && user.role === "student") sInput.value = user.name;
        if (tInput && user.role === "teacher") tInput.value = user.name;
        if (gradeSelect && user.grade_level) gradeSelect.value = user.grade_level;
        if (letterSelect && user.class_letter) letterSelect.value = user.class_letter;
    }
});
