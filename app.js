/* ============================================
   MLN122 Study App - Application Logic
   ============================================ */

// ========== STATE ==========
const state = {
    mode: 'flashcard', // 'quiz' or 'flashcard'

    // Current session
    currentQuestions: [],
    currentIndex: 0,
    answered: false,
    flipped: false,
    correct: 0,
    wrong: 0,
    wrongList: [],

    // Persistent
    mastered: new Set(),
    review: new Set(),
    seen: new Set(),
    wrongHistory: new Set(),
    totalAttempts: 0,
    totalCorrect: 0,
    filterProgress: {},
};

// ========== INIT ==========
function init() {
    loadProgress();

    // Set UI tabs based on restored mode
    document.getElementById('tab-quiz').classList.toggle('active', state.mode === 'quiz');
    document.getElementById('tab-flashcard').classList.toggle('active', state.mode === 'flashcard');

    buildSession();

    render();
    updateStats();
}

// ========== MODE SWITCH ==========
function switchMode(mode) {
    if (state.mode === mode) return;
    
    // Save progress for current mode before switching
    saveProgress();
    
    state.mode = mode;

    document.getElementById('tab-quiz').classList.toggle('active', mode === 'quiz');
    document.getElementById('tab-flashcard').classList.toggle('active', mode === 'flashcard');

    // Reload progress for the new mode
    buildSession();
    render();
}

// ========== SESSION BUILDING ==========
function buildSession() {
    const filterSetEl = document.getElementById('filter-set');
    const filterSet = filterSetEl ? filterSetEl.value : 'all';
    const filterType = document.getElementById('filter-type') ? document.getElementById('filter-type').value : 'all';
    const shuffle = document.getElementById('filter-shuffle') ? document.getElementById('filter-shuffle').checked : false;

    let pool = [...QUESTIONS];

    // Filter by set
    switch (filterSet) {
        case 'wrong':
            pool = pool.filter(q => state.wrongHistory.has(q.id));
            break;
        case 'unseen':
            pool = pool.filter(q => !state.seen.has(q.id));
            break;
        case 'review':
            pool = pool.filter(q => state.review.has(q.id));
            break;
        case 'mastered':
            pool = pool.filter(q => state.mastered.has(q.id));
            break;
    }

    // Filter by question type
    if (filterType !== 'all') {
        pool = pool.filter(q => q.type === filterType);
    }

    if (pool.length === 0) {
        pool = [...QUESTIONS];
        if (document.getElementById('filter-set')) document.getElementById('filter-set').value = 'all';
        if (document.getElementById('filter-type')) document.getElementById('filter-type').value = 'all';
    }

    // Restore or reset progress for this specific filter combination
    const finalFilterSet = document.getElementById('filter-set') ? document.getElementById('filter-set').value : 'all';
    const finalFilterType = document.getElementById('filter-type') ? document.getElementById('filter-type').value : 'all';
    const filterKey = `${state.mode}|${finalFilterSet}|${finalFilterType}|${shuffle}`;
    
    if (!state.filterProgress) state.filterProgress = {};
    const saved = state.filterProgress[filterKey];

    // Shuffle
    if (shuffle) {
        if (saved && saved.shuffledIds && saved.shuffledIds.length === pool.length) {
            const orderMap = new Map(saved.shuffledIds.map((id, i) => [id, i]));
            pool.sort((a, b) => {
                const orderA = orderMap.has(a.id) ? orderMap.get(a.id) : 999999;
                const orderB = orderMap.has(b.id) ? orderMap.get(b.id) : 999999;
                return orderA - orderB;
            });
        } else {
            pool = shuffleArray(pool);
        }
    }

    state.currentQuestions = pool;
    
    if (saved) {
        state.currentIndex = saved.currentIndex || 0;
        state.correct = saved.correct || 0;
        state.wrong = saved.wrong || 0;
        state.wrongList = saved.wrongList || [];
        state.quizAnswers = saved.quizAnswers || {};
        
        if (saved.currentQuestionId) {
            const idx = state.currentQuestions.findIndex(q => q.id === saved.currentQuestionId);
            if (idx !== -1) {
                state.currentIndex = idx;
            } else if (state.currentIndex >= state.currentQuestions.length) {
                state.currentIndex = 0;
            }
        } else if (state.currentIndex >= state.currentQuestions.length) {
            state.currentIndex = 0;
        }
    } else {
        // Fallback to legacy savedQuestionId if first time migrating
        if (state.savedQuestionId && Object.keys(state.filterProgress).length === 0) {
            const idx = state.currentQuestions.findIndex(q => q.id === state.savedQuestionId);
            if (idx !== -1) {
                state.currentIndex = idx;
            } else if (typeof state.savedIndex === 'number' && state.savedIndex < state.currentQuestions.length) {
                state.currentIndex = state.savedIndex;
            } else {
                state.currentIndex = 0;
            }
            delete state.savedQuestionId;
            delete state.savedIndex;
        } else {
            state.currentIndex = 0;
        }
        state.correct = 0;
        state.wrong = 0;
        state.wrongList = [];
        state.quizAnswers = {};
    }

    const currentQ = state.currentQuestions && state.currentQuestions[state.currentIndex];
    state.answered = !!(state.quizAnswers && currentQ && state.quizAnswers[currentQ.id]);
    state.flipped = true; // Always show in flashcard
}

function onFilterChange() {
    buildSession();
    render();
    saveProgress();
}

function restartSession() {
    state.correct = 0;
    state.wrong = 0;
    state.wrongList = [];
    state.quizAnswers = {};
    state.currentIndex = 0;
    state.answered = false;
    state.flipped = state.mode === 'flashcard';

    // Re-shuffle if enabled
    if (document.getElementById('filter-shuffle').checked) {
        state.currentQuestions = shuffleArray(state.currentQuestions);
    }

    render();
    saveProgress();
}

// ========== RENDER ==========
function render() {
    const questions = state.currentQuestions;

    // Remove any existing explanation box
    const existingExpl = document.getElementById('explanation-box');
    if (existingExpl) existingExpl.remove();

    if (questions.length === 0) {
        document.getElementById('q-text').textContent = 'Không có câu hỏi nào phù hợp. Hãy thay đổi bộ lọc.';
        document.getElementById('q-options').innerHTML = '';
        return;
    }

    const q = questions[state.currentIndex];
    const total = questions.length;

    // Progress
    const pct = ((state.currentIndex + 1) / total * 100);
    document.getElementById('progress-bar-fill').style.width = pct + '%';

    if (state.mode === 'flashcard') {
        // Flashcard: show "Câu X/Y" + percentage, hide Đúng/Sai
        document.getElementById('progress-label').textContent = `Câu ${state.currentIndex + 1}/${total}`;
        document.getElementById('stat-correct').innerHTML = `<strong>${Math.round(pct)}%</strong>`;
        document.getElementById('stat-wrong').style.display = 'none';
    } else {
        // Quiz: show Đúng/Sai
        document.getElementById('progress-label').textContent = `Câu ${state.currentIndex + 1}/${total}`;
        document.getElementById('stat-correct').innerHTML = `Đúng <strong>${state.correct}</strong>`;
        document.getElementById('stat-wrong').innerHTML = `Sai <strong>${state.wrong}</strong>`;
        document.getElementById('stat-wrong').style.display = '';
    }

    // Badge
    const filterLabels = {
        'all': 'TẤT CẢ CÂU HỎI',
        'wrong': 'CÂU ĐÃ SAI',
        'unseen': 'CÂU CHƯA LÀM',
        'review': 'CÂU CẦN ÔN LẠI',
        'mastered': 'CÂU ĐÃ THUỘC'
    };
    const typeLabels = {
        'all': '',
        'single': ' · 1 ĐÁP ÁN',
        'multi': ' · NHIỀU ĐÁP ÁN',
        'calc': ' · TÍNH TOÁN',
        'formula': ' · CÔNG THỨC',
        'congress': ' · ĐẠI HỘI ĐẢNG'
    };
    const filterSetEl = document.getElementById('filter-set');
    const filterVal = filterSetEl ? filterSetEl.value : 'all';
    const typeVal = document.getElementById('filter-type') ? document.getElementById('filter-type').value : 'all';
    document.getElementById('q-badge').textContent = `${filterLabels[filterVal] || 'TẤT CẢ'}${typeLabels[typeVal] || ''} (${total} CÂU)`;

    // Question
    document.getElementById('q-text').textContent = q.question;

    // Options
    renderOptions(q);

    // Feedback
    document.getElementById('q-feedback').style.display = 'none';
    document.getElementById('q-feedback').innerHTML = '';


    // Nav buttons
    document.getElementById('btn-prev').disabled = state.currentIndex === 0;

    // In quiz mode, next is disabled until answered
    if (state.mode === 'quiz') {
        const isMulti = q.type === 'multi' || q.answer.length > 1;
        if (!state.answered) {
            if (isMulti) {
                document.getElementById('btn-next').disabled = !(state.currentSelection && state.currentSelection.length > 0);
                document.getElementById('btn-next').textContent = 'Kiểm tra';
            } else {
                document.getElementById('btn-next').disabled = true;
                document.getElementById('btn-next').textContent = 'Câu sau →';
            }
        } else {
            document.getElementById('btn-next').disabled = false;
            document.getElementById('btn-next').textContent = state.currentIndex === total - 1 ? 'Xem kết quả →' : 'Câu sau →';
        }
    } else {
        document.getElementById('btn-next').disabled = state.currentIndex === total - 1;
        document.getElementById('btn-next').textContent = 'Câu sau →';
    }

    // Show/hide quiz vs flashcard elements
    updateModeUI(q);
}

function renderOptions(q) {
    const container = document.getElementById('q-options');
    container.innerHTML = '';
    
    // Reset selection for this question if not answered
    if (!state.answered) state.currentSelection = [];

    const keys = Object.keys(q.options);

    keys.forEach(key => {
        const div = document.createElement('div');
        div.className = 'option-item';
        div.setAttribute('data-key', key);
        div.innerHTML = `
            <span class="option-letter">${key}</span>
            <span class="option-text">${q.options[key]}</span>
        `;

        if (state.mode === 'quiz') {
            div.addEventListener('click', () => quizSelectAnswer(key, q));
        } else {
            // Flashcard mode: options are view-only
            div.classList.add('fc-readonly');
        }

        container.appendChild(div);
    });

    if (state.mode === 'quiz' && state.answered && state.quizAnswers && state.quizAnswers[q.id]) {
        const ans = state.quizAnswers[q.id];
        
        let correctArr = [];
        if (Array.isArray(q.answer)) correctArr = q.answer;
        else if (q.type === 'multi' || q.answer.length > 1) correctArr = q.answer.split('');
        else correctArr = [q.answer];

        const options = container.querySelectorAll('.option-item');
        options.forEach(opt => {
            const key = opt.getAttribute('data-key');
            opt.classList.add('disabled');
            
            if (correctArr.includes(key)) {
                opt.classList.add('correct');
            }
            
            if (ans.selected.includes(key) && !correctArr.includes(key)) {
                opt.classList.add('wrong');
            }
        });
        showExplanation(q);
    }

    // If flashcard mode and flipped, show answer
    if (state.mode === 'flashcard' && state.flipped) {
        showFlashcardAnswer(q);
    }
}

function updateModeUI(q) {
    if (state.mode === 'flashcard') {
        showFlashcardAnswer(q);
    }
}

// ========== QUIZ MODE ==========
function quizSelectAnswer(selected, q) {
    if (state.answered) return;

    const isMulti = q.type === 'multi' || q.answer.length > 1;

    if (isMulti) {
        const selectedEl = document.querySelector(`.option-item[data-key="${selected}"]`);
        if (!state.currentSelection) state.currentSelection = [];
        
        const idx = state.currentSelection.indexOf(selected);
        if (idx > -1) {
            state.currentSelection.splice(idx, 1);
            selectedEl.classList.remove('selected');
        } else {
            state.currentSelection.push(selected);
            selectedEl.classList.add('selected');
        }
        
        // Re-evaluate the Kiểm tra button
        document.getElementById('btn-next').disabled = state.currentSelection.length === 0;
        return; // Don't check answer yet
    }

    state.answered = true;

    if (!state.quizAnswers) state.quizAnswers = {};
    state.quizAnswers[q.id] = {
        selected: [selected],
        isCorrect: selected === q.answer
    };

    const isCorrect = selected === q.answer;

    // Mark all options
    const options = document.querySelectorAll('.option-item');
    options.forEach(opt => {
        const key = opt.getAttribute('data-key');
        opt.classList.add('disabled');

        // Show correct answer
        if (q.answer.includes(key) && q.answer.length <= 2) {
            opt.classList.add('correct');
        } else if (key === q.answer) {
            opt.classList.add('correct');
        }
    });

    // Mark selected
    const selectedEl = document.querySelector(`.option-item[data-key="${selected}"]`);

    if (isCorrect) {
        selectedEl.classList.add('correct');
        state.correct++;
        state.totalCorrect++;
    } else {
        selectedEl.classList.add('wrong');
        selectedEl.style.animation = 'shake 0.4s ease';
        state.wrong++;
        state.wrongList.push({
            question: q.question,
            yourAnswer: selected + '. ' + (q.options[selected] || selected),
            correctAnswer: q.answer + '. ' + (q.options[q.answer] || q.answer)
        });
        state.wrongHistory.add(q.id);

        // Also highlight correct
        const correctEl = document.querySelector(`.option-item[data-key="${q.answer[0]}"]`);
        if (correctEl) correctEl.classList.add('correct');
    }

    state.totalAttempts++;
    state.seen.add(q.id);

    // Show explanation if available
    showExplanation(q);

    // Enable next
    document.getElementById('btn-next').disabled = false;

    // Update stats
    document.getElementById('stat-correct').innerHTML = `Đúng <strong>${state.correct}</strong>`;
    document.getElementById('stat-wrong').innerHTML = `Sai <strong>${state.wrong}</strong>`;

    saveProgress();
    updateStats();
}

// ========== FLASHCARD MODE ==========

function showFlashcardAnswer(q) {
    // Highlight correct option
    document.querySelectorAll('.option-item').forEach(opt => {
        const key = opt.getAttribute('data-key');
        if (q.answer.includes(key)) {
            opt.classList.add('correct');
        }
    });

    // Show explanation if available
    showExplanation(q);
}

function showExplanation(q) {
    if (!q.explanation) return;

    // Remove any existing explanation box
    const existing = document.getElementById('explanation-box');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.id = 'explanation-box';
    box.className = 'explanation-box';
    box.innerHTML = `<div class="explanation-title">📐 Giải thích</div><pre class="explanation-text">${q.explanation}</pre>`;

    // Insert after options
    const optionsEl = document.getElementById('q-options');
    if (optionsEl && optionsEl.parentNode) {
        optionsEl.parentNode.insertBefore(box, optionsEl.nextSibling);
    }
}

// ========== NAVIGATION ==========
function goNext() {
    const total = state.currentQuestions.length;
    const q = state.currentQuestions[state.currentIndex];
    const isMulti = q && (q.type === 'multi' || q.answer.length > 1);

    // If quiz mode, multi-select, and not answered -> check answer instead of going next
    if (state.mode === 'quiz' && !state.answered && isMulti) {
        if (!state.currentSelection || state.currentSelection.length === 0) return;
        
        state.answered = true;
        
        let correctAnswers = Array.isArray(q.answer) ? q.answer : q.answer.split('');
        let selectedSorted = [...state.currentSelection].sort().join('');
        let correctSorted = [...correctAnswers].sort().join('');
        const isCorrect = selectedSorted === correctSorted;
        
        if (!state.quizAnswers) state.quizAnswers = {};
        state.quizAnswers[q.id] = {
            selected: [...state.currentSelection],
            isCorrect: isCorrect
        };
        
        const options = document.querySelectorAll('.option-item');
        options.forEach(opt => {
            const key = opt.getAttribute('data-key');
            opt.classList.add('disabled');
            if (correctAnswers.includes(key)) {
                opt.classList.add('correct');
            }
        });
        
        if (isCorrect) {
            state.correct++;
            state.totalCorrect++;
        } else {
            state.currentSelection.forEach(key => {
                if (!correctAnswers.includes(key)) {
                    const el = document.querySelector(`.option-item[data-key="${key}"]`);
                    if (el) {
                        el.classList.add('wrong');
                        el.style.animation = 'shake 0.4s ease';
                    }
                }
            });
            
            state.wrong++;
            state.wrongList.push({
                question: q.question,
                yourAnswer: state.currentSelection.sort().map(k => k + '. ' + (q.options[k] || k)).join('<br>'),
                correctAnswer: correctAnswers.sort().map(k => k + '. ' + (q.options[k] || k)).join('<br>')
            });
            state.wrongHistory.add(q.id);
        }
        
        state.totalAttempts++;
        state.seen.add(q.id);
        showExplanation(q);
        
        document.getElementById('btn-next').textContent = state.currentIndex === total - 1 ? 'Xem kết quả →' : 'Câu sau →';
        document.getElementById('stat-correct').innerHTML = `Đúng <strong>${state.correct}</strong>`;
        document.getElementById('stat-wrong').innerHTML = `Sai <strong>${state.wrong}</strong>`;
        
        saveProgress();
        updateStats();
        return;
    }

    // In quiz mode, check if this is the last question
    if (state.mode === 'quiz' && state.currentIndex === total - 1 && state.answered) {
        showQuizResults();
        saveProgress();
        return;
    }

    if (state.currentIndex < total - 1) {
        state.currentIndex++;
        const nextQ = state.currentQuestions[state.currentIndex];
        state.answered = !!(state.quizAnswers && state.quizAnswers[nextQ.id]);
        state.flipped = state.mode === 'flashcard';
        render();
        saveProgress();
    }
}

function goPrev() {
    if (state.currentIndex > 0) {
        state.currentIndex--;
        const prevQ = state.currentQuestions[state.currentIndex];
        state.answered = !!(state.quizAnswers && state.quizAnswers[prevQ.id]);
        state.flipped = state.mode === 'flashcard';
        render();
        saveProgress();
    }
}

function showQuizResults() {
    const total = state.currentQuestions.length;
    const pct = Math.round((state.correct / total) * 100);

    let emoji, title;
    if (pct >= 90) { emoji = '🎉'; title = 'Xuất sắc!'; }
    else if (pct >= 70) { emoji = '😊'; title = 'Tốt lắm!'; }
    else if (pct >= 50) { emoji = '💪'; title = 'Cần cố gắng thêm!'; }
    else { emoji = '📚'; title = 'Hãy ôn tập thêm nhé!'; }

    const card = document.getElementById('question-card');
    card.innerHTML = `
        <div style="text-align:center;padding:32px 0;">
            <div style="font-size:56px;margin-bottom:12px;">${emoji}</div>
            <h2 style="font-size:24px;font-weight:800;color:var(--text-primary);margin-bottom:8px;">${title}</h2>
            <p style="font-size:36px;font-weight:800;color:var(--primary);margin-bottom:24px;">${pct}%</p>
            <div style="display:flex;justify-content:center;gap:32px;margin-bottom:24px;">
                <div>
                    <div style="font-size:24px;font-weight:700;color:var(--success);">${state.correct}</div>
                    <div style="font-size:13px;color:var(--text-muted);">Đúng</div>
                </div>
                <div>
                    <div style="font-size:24px;font-weight:700;color:var(--error);">${state.wrong}</div>
                    <div style="font-size:13px;color:var(--text-muted);">Sai</div>
                </div>
                <div>
                    <div style="font-size:24px;font-weight:700;color:var(--text-primary);">${total}</div>
                    <div style="font-size:13px;color:var(--text-muted);">Tổng</div>
                </div>
            </div>
            <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
                <button class="btn-action primary" onclick="restartSession()">🔄 Làm lại</button>
                <button class="btn-action" onclick="showWrongReview()">📝 Xem câu sai (${state.wrongList.length})</button>
            </div>
            <div id="wrong-review-container"></div>
        </div>
    `;

    // Update progress bar to 100%
    document.getElementById('progress-bar-fill').style.width = '100%';
    document.getElementById('progress-label').textContent = `Hoàn thành!`;
}

function showWrongReview() {
    const container = document.getElementById('wrong-review-container');
    if (!container) return;

    if (state.wrongList.length === 0) {
        container.innerHTML = '<p style="margin-top:20px;color:var(--text-muted);text-align:center;">Không có câu sai! 🎉</p>';
        return;
    }

    container.innerHTML = `
        <div class="wrong-review-section">
            <h3>📝 Các câu trả lời sai</h3>
            ${state.wrongList.map((item, i) => `
                <div class="wrong-item">
                    <div class="wi-q">${i + 1}. ${item.question}</div>
                    <div class="wi-your">❌ Bạn chọn: ${item.yourAnswer}</div>
                    <div class="wi-correct">✅ Đáp án: ${item.correctAnswer}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function reviewWrongQuestions() {
    document.getElementById('filter-set').value = 'wrong';
    onFilterChange();
}

// ========== STATS ==========
function updateStats() {
    // Stats bar and header were removed - no-op
}

// ========== PERSISTENCE ==========
function saveProgress() {
    const q = state.currentQuestions[state.currentIndex];
    
    const filterSet = document.getElementById('filter-set') ? document.getElementById('filter-set').value : 'all';
    const filterType = document.getElementById('filter-type') ? document.getElementById('filter-type').value : 'all';
    const filterShuffle = document.getElementById('filter-shuffle') ? document.getElementById('filter-shuffle').checked : false;
    
    const filterKey = `${state.mode}|${filterSet}|${filterType}|${filterShuffle}`;
    
    if (!state.filterProgress) state.filterProgress = {};
    state.filterProgress[filterKey] = {
        currentIndex: state.currentIndex,
        currentQuestionId: q ? q.id : null,
        correct: state.correct,
        wrong: state.wrong,
        wrongList: state.wrongList,
        quizAnswers: state.quizAnswers,
        shuffledIds: state.currentQuestions.map(question => question.id)
    };

    const data = {
        mode: state.mode,
        filterSet: filterSet,
        filterType: filterType,
        filterShuffle: filterShuffle,
        seen: [...state.seen],
        wrongHistory: [...state.wrongHistory],
        totalAttempts: state.totalAttempts,
        totalCorrect: state.totalCorrect,
        filterProgress: state.filterProgress
    };
    localStorage.setItem('mln122_progress', JSON.stringify(data));
}

function loadProgress() {
    try {
        const raw = localStorage.getItem('mln122_progress');
        if (raw) {
            const data = JSON.parse(raw);
            state.seen = new Set(data.seen || []);
            state.wrongHistory = new Set(data.wrongHistory || []);
            state.totalAttempts = data.totalAttempts || 0;
            state.totalCorrect = data.totalCorrect || 0;
            state.filterProgress = data.filterProgress || {};

            if (data.mode) state.mode = data.mode;

            if (data.filterSet && document.getElementById('filter-set')) {
                document.getElementById('filter-set').value = data.filterSet;
            }
            if (data.filterType && document.getElementById('filter-type')) {
                document.getElementById('filter-type').value = data.filterType;
            }
            if (typeof data.filterShuffle === 'boolean' && document.getElementById('filter-shuffle')) {
                document.getElementById('filter-shuffle').checked = data.filterShuffle;
            }

            if (typeof data.currentIndex === 'number') {
                state.savedIndex = data.currentIndex;
            }
            if (data.currentQuestionId) {
                state.savedQuestionId = data.currentQuestionId;
            }
        }
    } catch (e) {
        console.warn('Failed to load progress:', e);
    }
}

function resetProgress() {
    if (!confirm('Bạn có chắc muốn reset toàn bộ tiến trình? Hành động này không thể hoàn tác.')) return;
    localStorage.removeItem('mln122_progress');
    state.seen = new Set();
    state.wrongHistory = new Set();
    state.totalAttempts = 0;
    state.totalCorrect = 0;
    state.correct = 0;
    state.wrong = 0;
    state.wrongList = [];
    state.currentIndex = 0;
    state.filterProgress = {};
    delete state.savedIndex;
    delete state.savedQuestionId;
    buildSession();
    render();
}

// ========== KEYBOARD SHORTCUTS ==========
document.addEventListener('keydown', (e) => {
    // Navigation
    if (e.key === 'ArrowRight') goNext();
    else if (e.key === 'ArrowLeft') goPrev();

    // Flashcard: Space or Enter goes to next question
    if (state.mode === 'flashcard' && (e.key === ' ' || e.key === 'Enter')) {
        e.preventDefault();
        goNext();
    }

    // Quiz answer with keyboard
    if (state.mode === 'quiz' && !state.answered) {
        const keyMap = { 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', '1': 'A', '2': 'B', '3': 'C', '4': 'D' };
        const letter = keyMap[e.key.toLowerCase()];
        if (letter) {
            const q = state.currentQuestions[state.currentIndex];
            if (q && q.options[letter]) {
                quizSelectAnswer(letter, q);
            }
        }
    }

    // Quiz next with Enter/Space after answering
    if (state.mode === 'quiz' && state.answered && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        goNext();
    }

    // Flashcard marks
    if (state.mode === 'flashcard' && state.flipped) {
        const q = state.currentQuestions[state.currentIndex];
        if (q) {
            if (e.key === 'm' || e.key === 'M') toggleMastered(q.id);
            if (e.key === 'r' || e.key === 'R') toggleReview(q.id);
        }
    }
});

// ========== UTILS ==========
function shuffleArray(arr) {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// ========== START ==========
window.addEventListener('beforeunload', () => saveProgress());
document.addEventListener('DOMContentLoaded', init);
