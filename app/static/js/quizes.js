const editorConfig = {
    skin: 'oxide-dark',
    content_css: 'dark',
    height: 250,
    menubar: false,
    plugins: ['codesample', 'link', 'image', 'lists'],
    toolbar: 'bold italic | codesample | bullist numlist | removeformat',
    content_style: 'body { font-family:Consolas, monospace; background-color: #1a1d24; color: #fff; }'
};

function addQuestion(data = null) {
    const uniqueId = 'editor_' + Date.now() + Math.random().toString(36).substr(2, 9);
    const groupName = 'correct_' + uniqueId;

    const qText = data ? data.text : '';

    const getAnsText = (idx) => (data && data.answers[idx]) ? data.answers[idx].text : '';
    const getAnsCheck = (idx) => (data && data.answers[idx] && data.answers[idx].is_correct) ? 'checked' : '';

    const container = document.getElementById('questionsContainer');

    const questionHtml = `
        <div class="card mb-5 question-block" style="background-color: var(--bg-card); border: 1px solid var(--border);">
            
            <div class="card-header border-0 d-flex justify-content-between align-items-center pt-3 px-4" 
                 style="background: rgba(255,255,255,0.02); border-bottom: 1px solid #333 !important;">
                
                <span class="badge" style="background-color: var(--accent); color: black; font-weight: bold;">QUESTION</span>
                
                <button class="btn btn-sm btn-outline-danger d-flex align-items-center gap-2 w-auto" onclick="removeQuestion(this)" title="Delete Question">
                    <span>Delete</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16">
                      <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5"/>
                    </svg>
                </button>
            </div>
            
            <div class="card-body p-4">
                <div class="mb-4">
                    <label class="text-muted small fw-bold mb-2">QUESTION TEXT</label>
                    <textarea id="${uniqueId}" class="question-editor">${qText}</textarea>
                </div>

                <label class="text-muted small fw-bold mb-2">ANSWERS (MARK THE CORRECT ONE)</label>
                
                <div class="d-flex flex-column gap-3">
                    <div class="input-group answer-row">
                        <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="0" ${getAnsCheck(0)}>
                        </div>
                        <input type="text" class="form-control input-dark answer-text" placeholder="Option A" value="${getAnsText(0)}">
                    </div>

                    <div class="input-group answer-row">
                        <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="1" ${getAnsCheck(1)}>
                        </div>
                        <input type="text" class="form-control input-dark answer-text" placeholder="Option B" value="${getAnsText(1)}">
                    </div>

                    <div class="input-group answer-row">
                        <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="2" ${getAnsCheck(2)}>
                        </div>
                        <input type="text" class="form-control input-dark answer-text" placeholder="Option C" value="${getAnsText(2)}">
                    </div>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', questionHtml);

    tinymce.init({
        ...editorConfig,
        selector: `#${uniqueId}`
    });
}

function removeQuestion(btn) {
    if(confirm("Delete this question?")) {
        const block = btn.closest('.question-block');
        const editorId = block.querySelector('textarea').id;
        tinymce.get(editorId).remove();
        block.remove();
    }
}

async function saveQuiz() {
    const title = document.getElementById('quizTitle').value;
    if (!title.trim()) { alert("Please enter Quiz Title"); return; }

    const questions = [];
    const blocks = document.querySelectorAll('.question-block');

    if (blocks.length === 0) { alert("Add at least one question!"); return; }

    for (let block of blocks) {
        const editorId = block.querySelector('textarea').id;
        const content = tinymce.get(editorId).getContent();

        if (!content.trim()) { alert("Question text cannot be empty"); return; }

        const answers = [];
        let hasCorrect = false;

        block.querySelectorAll('.answer-row').forEach(row => {
            const text = row.querySelector('.answer-text').value;
            const isCorrect = row.querySelector('.answer-correct').checked;
            if(isCorrect) hasCorrect = true;

            answers.push({ text: text, is_correct: isCorrect });
        });

        if (answers.some(a => !a.text.trim())) { alert("Fill all 3 answer options"); return; }
        if (!hasCorrect) { alert("Select correct answer for all questions"); return; }

        questions.push({ text: content, answers: answers });
    }

    const data = { title: title, questions: questions };

    try {
        const res = await fetch(CONFIG.saveUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (res.ok) {
            window.location.href = CONFIG.redirectUrl;
        } else {
            alert("Error saving quiz");
        }
    } catch (e) {
        console.error(e);
        alert("Network error");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const quizData = window.EXISTING_QUIZ || [];
    console.log("Quiz Data loaded:", quizData);

    if (quizData.length > 0) {
        quizData.forEach(question => {
            addQuestion(question);
        });
    } else {
        addQuestion();
    }
});