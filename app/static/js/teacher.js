// Teacher Live Monitoring & Dashboard Engine

let currentRoomCode = "";
let currentTeacher = null;
let dashboardData = null;
let ws = null;
let pollingInterval = null;
let currentViewMode = "cards"; // 'cards' or 'table'
let selectedClassFilter = "all";
let currentModalStudentId = null;

document.addEventListener("DOMContentLoaded", async () => {
    currentTeacher = getSavedUser();
    if (!currentTeacher || currentTeacher.role !== "teacher") {
        alert("Для доступу до кабінету потрібна авторизація вчителя.");
        window.location.href = "/";
        return;
    }

    const pathParts = window.location.pathname.split("/").filter(Boolean);
    currentRoomCode = pathParts[pathParts.length - 1];

    if (!currentRoomCode) {
        window.location.href = "/hierarchy";
        return;
    }

    document.getElementById("room-code-badge").textContent = currentRoomCode;
    document.getElementById("empty-room-code").textContent = currentRoomCode;

    await refreshDashboardData();
    connectWebSocket();

    // Background fallback polling every 4 seconds
    pollingInterval = setInterval(refreshDashboardData, 4000);
});

function handleClassFilterChange(val) {
    selectedClassFilter = val;
    renderDashboard();
}

function filterStudents() {
    renderDashboard();
}

async function refreshDashboardData() {
    const refreshIcon = document.getElementById("refresh-icon");
    if (refreshIcon) refreshIcon.classList.add("fa-spin");

    try {
        const resp = await fetch(`/api/teacher/rooms/${currentRoomCode}/dashboard`);
        if (!resp.ok) {
            console.error("Failed to load dashboard data");
            return;
        }

        dashboardData = await resp.json();
        renderDashboard();
    } catch (err) {
        console.error("Dashboard refresh error:", err);
    } finally {
        if (refreshIcon) refreshIcon.classList.remove("fa-spin");
    }
}

function renderDashboard() {
    if (!dashboardData) return;

    // Header info
    document.getElementById("room-topic-title").textContent = dashboardData.room.topic_name;
    document.getElementById("topic-grade-subject").textContent = `${dashboardData.room.grade_name} • ${dashboardData.room.subject_name}`;

    // Filter students
    const searchVal = (document.getElementById("student-search-input")?.value || "").toLowerCase().trim();
    const classVal = selectedClassFilter;

    const filteredStudents = dashboardData.students.filter(s => {
        const matchesSearch = s.name.toLowerCase().includes(searchVal);
        const matchesClass = (classVal === "all" || !classVal) ? true : (s.class_name === classVal);
        return matchesSearch && matchesClass;
    });

    // KPIs based on filtered view
    const totalStudents = filteredStudents.length;
    const onlineActive = filteredStudents.filter(s => s.is_online && s.is_tab_active).length;
    const tabHidden = filteredStudents.filter(s => s.is_online && !s.is_tab_active).length;
    
    let totalSolvedSum = 0;
    filteredStudents.forEach(s => totalSolvedSum += s.solved_count);
    const avgProgress = (totalStudents > 0 && dashboardData.room.total_tasks > 0)
        ? Math.round((totalSolvedSum / (totalStudents * dashboardData.room.total_tasks)) * 100)
        : 0;

    document.getElementById("stat-total-students").textContent = totalStudents;
    document.getElementById("stat-active-online").textContent = onlineActive;
    document.getElementById("stat-tab-hidden").textContent = tabHidden;
    document.getElementById("stat-avg-progress").textContent = `${avgProgress}%`;

    const emptyState = document.getElementById("empty-state");
    const cardsView = document.getElementById("students-cards-view");
    const tableView = document.getElementById("students-table-view");

    if (dashboardData.all_students_count === 0 && dashboardData.students.length === 0) {
        emptyState.classList.remove("hidden");
        cardsView.classList.add("hidden");
        tableView.classList.add("hidden");
        return;
    } else {
        emptyState.classList.add("hidden");
    }

    if (currentViewMode === "cards") {
        cardsView.classList.remove("hidden");
        tableView.classList.add("hidden");
        renderCardsView(filteredStudents);
    } else {
        cardsView.classList.add("hidden");
        tableView.classList.remove("hidden");
        renderTableView(filteredStudents);
    }
}

function renderCardsView(students) {
    const container = document.getElementById("students-cards-view");
    container.innerHTML = "";

    if (students.length === 0) {
        container.innerHTML = `<div class="col-span-full py-8 text-center text-slate-400 text-sm">Учнів за обраними критеріями не знайдено.</div>`;
        return;
    }

    students.forEach(s => {
        const card = document.createElement("div");

        // Status badge config
        let statusBadge = "";
        let borderHighlight = "border-slate-200";

        if (s.is_online && s.is_tab_active) {
            statusBadge = `
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Онлайн (працює)
                </span>
            `;
            borderHighlight = "border-emerald-300 ring-1 ring-emerald-400/30";
        } else if (s.is_online && !s.is_tab_active) {
            statusBadge = `
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200" title="Учень згорнув сторінку або перемкнувся на іншу вкладку">
                    <i class="fa-solid fa-triangle-exclamation text-amber-500"></i> Згорнув вкладку (${s.seconds_since_heartbeat}с)
                </span>
            `;
            borderHighlight = "border-amber-300 ring-1 ring-amber-400/30";
        } else {
            statusBadge = `
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-500 border border-slate-200">
                    <span class="w-2 h-2 rounded-full bg-slate-300"></span> Офлайн
                </span>
            `;
        }

        const pct = Math.round((s.solved_count / s.total_tasks) * 100);

        // Render 20 mini progress squares
        let matrixHtml = `<div class="grid grid-cols-10 gap-1 my-3">`;
        s.tasks_progress.forEach(tp => {
            let squareClass = "bg-slate-100 text-slate-400 border-slate-200";
            let tooltip = `Завдання #${tp.task_order}: ще не розв'язував`;

            if (tp.is_solved) {
                squareClass = "bg-emerald-500 text-white border-emerald-600 font-bold shadow-xs";
                tooltip = `Завдання #${tp.task_order}: вирішено вірно (${tp.attempt_count} спр.)`;
            } else if (tp.attempt_count > 0 && !tp.last_is_correct) {
                squareClass = "bg-rose-500 text-white border-rose-600 font-bold animate-pulse shadow-xs";
                const isFactor = tp.last_answer && tp.last_answer.includes("множник");
                tooltip = isFactor 
                    ? `Завдання #${tp.task_order}: ⚠️ Невірний множник! ${tp.last_answer} (${tp.attempt_count} спр.)`
                    : `Завдання #${tp.task_order}: помилка! Остання відповідь: "${tp.last_answer}" (${tp.attempt_count} спр.)`;
            } else if (s.is_online && s.current_task_order === tp.task_order) {
                squareClass = "bg-amber-400 text-slate-900 border-amber-500 font-black ring-2 ring-amber-300";
                tooltip = `Завдання #${tp.task_order}: зараз виконує`;
            }

            matrixHtml += `
                <div class="h-6 rounded-md border flex items-center justify-center text-[10px] cursor-pointer transition-transform hover:scale-125 hover:z-10 ${squareClass}"
                     title="${tooltip}" onclick="openStudentModal(${s.user_id})">
                    ${tp.task_order}
                </div>
            `;
        });
        matrixHtml += `</div>`;

        // Check if student has a current error (e.g. incorrect factor or wrong answer)
        const currentTaskProgress = s.tasks_progress.find(tp => tp.task_order === s.current_task_order) || s.tasks_progress[0];
        let currentTaskErrorBanner = "";
        if (currentTaskProgress && currentTaskProgress.attempt_count > 0 && !currentTaskProgress.last_is_correct) {
            const isFactor = currentTaskProgress.last_answer && currentTaskProgress.last_answer.includes("множник");
            currentTaskErrorBanner = `
                <div class="mt-2.5 p-2 rounded-xl bg-rose-50 border border-rose-200 text-[11px] text-rose-800 flex items-start gap-1.5 font-medium shadow-xs">
                    <i class="fa-solid fa-triangle-exclamation text-rose-600 mt-0.5 shrink-0"></i>
                    <div class="truncate flex-1" title="${currentTaskProgress.last_answer}">
                        <strong>${isFactor ? 'Помилка дільника' : 'Помилка'} у #${currentTaskProgress.task_order}:</strong> ${currentTaskProgress.last_answer}
                    </div>
                </div>
            `;
        }

        card.className = `bg-white rounded-3xl p-5 border ${borderHighlight} shadow-sm hover:shadow-md transition-all flex flex-col justify-between`;
        card.innerHTML = `
            <div>
                <div class="flex items-start justify-between gap-2 mb-2">
                    <div>
                        <div class="flex items-center gap-2">
                            <h4 class="text-base font-bold text-slate-900">${s.name}</h4>
                            <span class="px-2 py-0.5 rounded-lg text-xs font-black bg-indigo-50 text-indigo-700 border border-indigo-200">${s.class_name || "6-А"}</span>
                        </div>
                        <div class="text-[11px] text-slate-400 font-mono mt-0.5">
                            IP: ${s.ip_address || "127.0.0.1"} • ID: ${s.device_id ? s.device_id.substring(0, 8) : "—"}
                        </div>
                    </div>
                    ${statusBadge}
                </div>

                <div class="mt-3">
                    <div class="flex justify-between items-center text-xs font-bold text-slate-700 mb-1">
                        <span>Прогрес:</span>
                        <span class="text-brand-600">${s.solved_count} / ${s.total_tasks} (${pct}%)</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                        <div class="bg-gradient-to-r from-brand-500 to-emerald-600 h-full rounded-full" style="width: ${pct}%"></div>
                    </div>
                </div>

                <div class="text-xs text-slate-500 mt-3 font-medium flex justify-between">
                    <span>Поточне завдання: <strong class="text-slate-800">#${s.current_task_order || 1}</strong></span>
                    <span>Спроб всього: <strong class="text-slate-800">${s.total_attempts}</strong></span>
                </div>

                ${currentTaskErrorBanner}
                ${matrixHtml}
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span class="text-slate-400 text-[11px]">Активність: ${s.last_active || "щойно"}</span>
                <button onclick="openStudentModal(${s.user_id})" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition flex items-center gap-1">
                    <i class="fa-solid fa-list-check text-xs"></i> Детальний звіт
                </button>
            </div>
        `;

        container.appendChild(card);
    });
}

function renderTableView(students) {
    const tbody = document.getElementById("students-table-body");
    tbody.innerHTML = "";

    students.forEach(s => {
        const pct = Math.round((s.solved_count / s.total_tasks) * 100);
        let statusBadge = "";
        if (s.is_online && s.is_tab_active) {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">🟢 Онлайн</span>`;
        } else if (s.is_online && !s.is_tab_active) {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">🟡 Згорнув (${s.seconds_since_heartbeat}с)</span>`;
        } else {
            statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-500 border border-slate-200">⚪ Офлайн</span>`;
        }

        const curTask = s.tasks_progress.find(tp => tp.task_order === s.current_task_order);
        let taskAlert = "";
        if (curTask && curTask.attempt_count > 0 && !curTask.last_is_correct) {
            const isFactor = curTask.last_answer && curTask.last_answer.includes("множник");
            taskAlert = `<span class="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700 border border-rose-200" title="${curTask.last_answer}">${isFactor ? '⚠️ Невірний множник' : '❌ Помилка'}</span>`;
        }

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50/80 transition";
        tr.innerHTML = `
            <td class="py-3 px-4 font-bold text-slate-900">
                <div class="flex items-center gap-2">
                    <span>${s.name}</span>
                    <span class="px-1.5 py-0.5 rounded text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">${s.class_name || "6-А"}</span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono font-normal">IP: ${s.ip_address || "127.0.0.1"}</div>
            </td>
            <td class="py-3 px-4">${statusBadge}</td>
            <td class="py-3 px-4 font-semibold text-slate-800">Завдання #${s.current_task_order || 1} ${taskAlert}</td>
            <td class="py-3 px-4">
                <div class="flex items-center gap-2">
                    <div class="w-20 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                        <div class="bg-brand-500 h-full rounded-full" style="width: ${pct}%"></div>
                    </div>
                    <span class="font-bold text-slate-800">${s.solved_count}/${s.total_tasks}</span>
                </div>
            </td>
            <td class="py-3 px-4 text-slate-600">${s.total_attempts}</td>
            <td class="py-3 px-4 text-right">
                <button onclick="openStudentModal(${s.user_id})" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
                    Деталі
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setViewMode(mode) {
    currentViewMode = mode;
    const cardsBtn = document.getElementById("view-mode-cards-btn");
    const tableBtn = document.getElementById("view-mode-table-btn");

    if (mode === "cards") {
        cardsBtn.className = "px-3 py-1.5 rounded-lg bg-white text-indigo-700 shadow-sm transition";
        tableBtn.className = "px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition";
    } else {
        tableBtn.className = "px-3 py-1.5 rounded-lg bg-white text-indigo-700 shadow-sm transition";
        cardsBtn.className = "px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition";
    }
    renderDashboard();
}

function filterStudents() {
    renderDashboard();
}

function openStudentModal(userId) {
    if (!dashboardData) return;
    const student = dashboardData.students.find(s => s.user_id === userId);
    if (!student) return;

    currentModalStudentId = userId;
    const classLabel = student.class_name ? ` (${student.class_name})` : "";
    document.getElementById("modal-student-name").textContent = `${student.name}${classLabel}`;
    document.getElementById("modal-student-meta").textContent = `Клас: ${student.class_name || "6-А"} • IP: ${student.ip_address || "127.0.0.1"} • ID: ${student.device_id}`;
    
    const statusBadge = document.getElementById("modal-student-status-badge");
    if (student.is_online && student.is_tab_active) {
        statusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800";
        statusBadge.textContent = "🟢 Онлайн (активний)";
    } else if (student.is_online && !student.is_tab_active) {
        statusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800";
        statusBadge.textContent = "🟡 Згорнув сторінку";
    } else {
        statusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600";
        statusBadge.textContent = "⚪ Офлайн";
    }

    document.getElementById("modal-summary-text").textContent = `Вирішено: ${student.solved_count} з ${student.total_tasks} • Всього спроб: ${student.total_attempts}`;

    const list = document.getElementById("modal-tasks-list");
    list.innerHTML = "";

    student.tasks_progress.forEach(tp => {
        const item = document.createElement("div");
        let itemClass = "bg-slate-50 border-slate-200 text-slate-700";
        let statusText = "Не розв'язано";

        if (tp.is_solved) {
            itemClass = "bg-emerald-50/60 border-emerald-300 text-emerald-900";
            statusText = `✅ Вирішено вірно (${tp.attempt_count} спр.)`;
        } else if (tp.attempt_count > 0 && !tp.last_is_correct) {
            itemClass = "bg-rose-50/60 border-rose-300 text-rose-900";
            statusText = `❌ Помилка в останній спробі (${tp.attempt_count} спр.)`;
        }

        let historyHtml = "";
        if (tp.history && tp.history.length > 0) {
            historyHtml = `<div class="mt-2 pt-2 border-t border-slate-200/60 space-y-1 text-xs">`;
            tp.history.forEach(h => {
                const mark = h.is_correct ? "✅ Вірно" : "❌ Помилка";
                const badgeColor = h.is_correct ? "text-emerald-700 bg-emerald-100" : "text-rose-700 bg-rose-100";
                const isFactorErr = h.submitted_answer && h.submitted_answer.includes("множник");
                const rowClass = isFactorErr ? "bg-rose-50/80 p-2 rounded-xl border border-rose-200 text-rose-900" : "";
                historyHtml += `
                    <div class="flex items-center justify-between text-[11px] ${rowClass}">
                        <span>Спроба #${h.attempt_number}: ${isFactorErr ? '⚠️ ' : ''}введено <strong>"${h.submitted_answer}"</strong> (<span class="font-bold ${badgeColor} px-1.5 py-0.5 rounded">${mark}</span>)</span>
                        <span class="text-slate-400 font-mono">${h.created_at}</span>
                    </div>
                `;
            });
            historyHtml += `</div>`;
        }

        const hasAttempts = tp.attempt_count > 0 || tp.is_solved;
        const taskResetBtn = hasAttempts ? `
            <button onclick="resetStudentTaskProgress(${student.user_id}, ${tp.task_id})" title="Скинути спроби тільки для цього завдання" class="px-2 py-1 rounded-lg bg-rose-100/80 hover:bg-rose-200 text-rose-800 text-[11px] font-bold transition flex items-center gap-1">
                <i class="fa-solid fa-rotate-left"></i> Скинути
            </button>
        ` : "";

        item.className = `p-4 rounded-2xl border ${itemClass} transition`;
        item.innerHTML = `
            <div class="flex items-center justify-between gap-2">
                <div>
                    <span class="font-black text-xs uppercase tracking-wider text-slate-500">Завдання #${tp.task_order}</span>
                    <div class="font-mono font-bold text-base text-slate-900">${tp.question}</div>
                </div>
                <div class="text-right flex flex-col items-end gap-1">
                    <span class="text-xs font-bold">${statusText}</span>
                    <div class="text-[11px] text-slate-500 font-mono">Правильна відп.: <strong>${tp.correct_answer}</strong></div>
                    ${taskResetBtn}
                </div>
            </div>
            ${historyHtml}
        `;
        list.appendChild(item);
    });

    document.getElementById("student-modal").classList.remove("hidden");
}

function closeStudentModal() {
    currentModalStudentId = null;
    document.getElementById("student-modal").classList.add("hidden");
}

async function confirmResetStudentProgress() {
    if (!currentModalStudentId) return;
    const student = dashboardData?.students.find(s => s.user_id === currentModalStudentId);
    const studentName = student ? student.name : "учня";

    if (!confirm(`Ви впевнені, що хочете повністю скинути весь прогрес і всі спроби учня "${studentName}"?\nУчень зможе пройти тест заново з першого завдання.`)) {
        return;
    }

    try {
        const resp = await fetch(`/api/teacher/rooms/${currentRoomCode}/students/${currentModalStudentId}/reset`, {
            method: "POST"
        });
        if (resp.ok) {
            showLiveToast(`Прогрес учня <strong>${studentName}</strong> успішно скинуто 🔄`);
            await refreshDashboardData();
            if (currentModalStudentId) {
                openStudentModal(currentModalStudentId);
            }
        } else {
            alert("Помилка під час скидання прогресу.");
        }
    } catch (e) {
        console.error("Reset error:", e);
        alert("Помилка сервера під час скидання.");
    }
}

async function resetStudentTaskProgress(userId, taskId) {
    const student = dashboardData?.students.find(s => s.user_id === userId);
    const studentName = student ? student.name : "учня";

    if (!confirm(`Скинути спроби для завдання учень "${studentName}"?`)) {
        return;
    }

    try {
        const resp = await fetch(`/api/teacher/rooms/${currentRoomCode}/students/${userId}/reset?task_id=${taskId}`, {
            method: "POST"
        });
        if (resp.ok) {
            showLiveToast(`Спроби для завдання учня <strong>${studentName}</strong> скинуто 🔄`);
            await refreshDashboardData();
            if (currentModalStudentId === userId) {
                openStudentModal(userId);
            }
        } else {
            alert("Помилка під час скидання спроб завдання.");
        }
    } catch (e) {
        console.error("Task reset error:", e);
        alert("Помилка сервера під час скидання завдання.");
    }
}

function copyRoomLink() {
    const studentUrl = window.location.origin + "/room/" + currentRoomCode;
    navigator.clipboard.writeText(studentUrl).then(() => {
        alert("Посилання для учнів скопійовано у буфер обміну:\n" + studentUrl);
    }).catch(() => {
        prompt("Скопіюйте посилання:", studentUrl);
    });
}

function showLiveToast(text) {
    const bar = document.getElementById("live-activity-bar");
    const textEl = document.getElementById("live-activity-text");
    const timeEl = document.getElementById("live-activity-time");

    if (bar && textEl) {
        textEl.innerHTML = text;
        const now = new Date();
        timeEl.textContent = now.toLocaleTimeString();
        bar.classList.remove("hidden");
    }
}

// WebSocket Connection
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const teacherId = currentTeacher.user_id || currentTeacher.id || 0;
    const wsUrl = `${protocol}//${window.location.host}/ws/room/${currentRoomCode}/teacher/${teacherId}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById("ws-status-text").textContent = "Live підключено";
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            handleLiveEvent(msg);
        } catch (e) {
            console.error("WS Parse error:", e);
        }
    };

    ws.onclose = () => {
        document.getElementById("ws-status-text").textContent = "Перепідключення...";
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (err) => {
        console.warn("WebSocket error:", err);
    };
}

function handleLiveEvent(msg) {
    if (msg.event === "task_attempt") {
        const d = msg.data;
        if (d.submitted_answer && d.submitted_answer.includes("множник")) {
            showLiveToast(`⚠️ Учень <strong>${d.student_name}</strong> у завданні #${d.task_order}: <span class='text-rose-400 font-bold'>${d.submitted_answer} ❌</span>`);
        } else {
            const resultText = d.is_correct ? "<span class='text-emerald-400 font-bold'>Вірно ✅</span>" : "<span class='text-rose-400 font-bold'>Помилка ❌</span>";
            showLiveToast(`Учень <strong>${d.student_name}</strong> відповів на завдання #${d.task_order} (${resultText})`);
        }
        refreshDashboardData();
        if (currentModalStudentId === d.user_id) {
            openStudentModal(d.user_id);
        }
    } else if (msg.event === "presence_update") {
        const d = msg.data;
        if (!d.is_tab_active) {
            showLiveToast(`Учень <strong>${d.student_name}</strong> згорнув вкладку або відволікся ⚠️`);
        }
        refreshDashboardData();
    } else if (msg.event === "student_progress_reset") {
        const d = msg.data;
        showLiveToast(`Прогрес учня <strong>${d.student_name}</strong> скинуто вчителем 🔄`);
        refreshDashboardData();
        if (currentModalStudentId === d.user_id) {
            openStudentModal(d.user_id);
        }
    }
}
