   const editorConfig = {
        skin: 'oxide-dark',
        content_css: 'dark',
        height: 250,
        menubar: false,
        plugins: ['codesample', 'link', 'image', 'lists'],
        toolbar: 'bold italic | codesample | bullist numlist | removeformat',
        content_style: 'body { font-family:Consolas, monospace; background-color: #1a1d24; color: #fff; }'
    };



    function addQuestion(existingData = null) {
        const uniqueId = 'editor_' + Date.now() + Math.random().toString(36).substr(2, 9);
        const groupName = 'correct_' + uniqueId; // Группировка радио-кнопок для этого вопроса

        const container = document.getElementById('questionsContainer');

        const questionHtml = `
            <div class="card mb-5 question-block" style="background-color: var(--bg-card); border: 1px solid var(--border);">
                <div class="card-header border-0 d-flex justify-content-between align-items-center pt-3 px-4" style="background: transparent;">
                    <span class="badge bg-secondary">QUESTION</span>
                    <button class="btn btn-sm text-danger fw-bold" onclick="removeQuestion(this)">DELETE</button>
                </div>
                
                <div class="card-body p-4">
                    <div class="mb-4">
                        <label class="text-muted small fw-bold mb-2">QUESTION TEXT (CODE & IMAGE SUPPORTED)</label>
                        <textarea id="${uniqueId}" class="question-editor"></textarea>
                    </div>

                    <label class="text-muted small fw-bold mb-2">ANSWERS (MARK THE CORRECT ONE)</label>
                    
                    <div class="d-flex flex-column gap-3">
                        <div class="input-group answer-row">
                            <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                                <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="0">
                            </div>
                            <input type="text" class="form-control input-dark answer-text" placeholder="Option A">
                        </div>

                        <div class="input-group answer-row">
                            <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                                <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="1">
                            </div>
                            <input type="text" class="form-control input-dark answer-text" placeholder="Option B">
                        </div>

                        <div class="input-group answer-row">
                            <div class="input-group-text" style="background: #2a2f3a; border: 1px solid var(--border);">
                                <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="2">
                            </div>
                            <input type="text" class="form-control input-dark answer-text" placeholder="Option C">
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
        if(confirm("Remove this question?")) {
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
            const res = await fetch("{{ url_for('main.save_quiz', id_lesson=lesson.id_lesson) }}", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            if (res.ok) {
                window.location.href = "{{ url_for('main.view_lesson', id_lesson=lesson.id_lesson) }}";
            } else {
                alert("Error saving quiz");
            }
        } catch (e) {
            console.error(e);
            alert("Network error");
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        addQuestion();
    });