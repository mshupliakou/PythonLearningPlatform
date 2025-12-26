    const editorConfig = {
        skin: 'oxide-dark',
        content_css: 'dark',
        height: 250,
        menubar: false,
        plugins: ['codesample', 'link', 'image', 'lists'],
        toolbar: 'bold italic | codesample | bullist numlist | removeformat',
        content_style: 'body { font-family:Consolas, monospace; background-color: #222; color: #fff; }'
    };

    function addQuestion() {
        const uniqueId = 'editor_' + Date.now();
        const groupName = 'correct_' + Date.now();
        const container = document.getElementById('questionsContainer');
        const questionHtml = `
            <div class="card p-4 mb-5 question-block" style="background: #1a1d24; border: 1px solid #333;">
                <div class="d-flex justify-content-between mb-3">
                    <h5 style="color: var(--accent);">Question Editor</h5>
                    <button class="btn btn-sm btn-danger" onclick="removeQuestion(this)">Delete Question</button>
                </div>
                
                <textarea id="${uniqueId}" class="question-editor"></textarea>
                
                <div class="answers-container mt-4">
                    <label class="text-muted small fw-bold mb-2">ANSWERS (Select the correct one):</label>
                    
                    <div class="input-group mb-3 answer-row">
                        <div class="input-group-text" style="background: #333; border-color: #444;">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="0">
                        </div>
                        <input type="text" class="form-control answer-text" placeholder="Option A" style="background: #222; color: white; border-color: #444;">
                    </div>

                    <div class="input-group mb-3 answer-row">
                        <div class="input-group-text" style="background: #333; border-color: #444;">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="1">
                        </div>
                        <input type="text" class="form-control answer-text" placeholder="Option B" style="background: #222; color: white; border-color: #444;">
                    </div>

                    <div class="input-group mb-3 answer-row">
                        <div class="input-group-text" style="background: #333; border-color: #444;">
                            <input class="form-check-input mt-0 answer-correct" type="radio" name="${groupName}" value="2">
                        </div>
                        <input type="text" class="form-control answer-text" placeholder="Option C" style="background: #222; color: white; border-color: #444;">
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
        const block = btn.closest('.question-block');
        const editorId = block.querySelector('textarea').id;
        tinymce.get(editorId).remove();
        block.remove();
    }

    async function saveQuiz() {
        const title = document.getElementById('quizTitle').value;
        if (!title) {
            alert("Please enter a Quiz Title");
            return;
        }

        const questions = [];
        const blocks = document.querySelectorAll('.question-block');

        for (let block of blocks) {
            const editorId = block.querySelector('textarea').id;
            const content = tinymce.get(editorId).getContent();

            if (!content.trim()) {
                alert("Please fill in the question text");
                return;
            }

            const answers = [];
            let hasCorrectAnswer = false;

            block.querySelectorAll('.answer-row').forEach(row => {
                const text = row.querySelector('.answer-text').value;
                const isCorrect = row.querySelector('.answer-correct').checked;

                if (isCorrect) hasCorrectAnswer = true;

                answers.push({
                    text: text,
                    is_correct: isCorrect
                });
            });

            if (answers.some(a => !a.text.trim())) {
                alert("Please fill in all 3 answer options for every question.");
                return;
            }

            if (!hasCorrectAnswer) {
                alert("Please select the correct answer for every question.");
                return;
            }

            questions.push({
                text: content,
                answers: answers
            });
        }

        if (questions.length === 0) {
            alert("Please add at least one question.");
            return;
        }

        const data = {
            title: title,
            questions: questions
        };

        try {
            const response = await fetch("{{ url_for('main.save_quiz', id_lesson=id_lesson) }}", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            if (response.ok) {
                window.location.href = "{{ url_for('main.lessons_list', module_id=module_id) }}";
            } else {
                alert('Error saving quiz. Check console for details.');
            }
        } catch (e) {
            console.error(e);
            alert('Network error');
        }
    }