// ============================================================
// EXAM ENGINE v2.0
// ------------------------------------------------------------
// This file controls the entire online examination system.
//
// Modules
// --------
// 1. Initialization
// 2. Countdown Timer
// 3. Answer Selection
// 4. Auto Save
// 5. Navigation
// 6. Review Answers
// 7. Submit Exam
// 8. Keyboard Shortcuts
//
// Author:
// Herculyses Piloton
//
// ============================================================

const Exam = {

    // Prevent multiple submissions
    isSubmitting: false,

    // ========================================================
    // Initialize the Exam Engine
    // ========================================================

    init() {

        console.log("Exam Engine Initialized");

        this.timer.start();

        this.answers.restore();

        this.navigator.load();

    },

    // ========================================================
    // Countdown Timer Module
    // ========================================================

    timer: {

        timeLeft: 0,

        timerInterval: null,

        start() {

            this.timeLeft =
                parseInt(document.getElementById("remainingSeconds").value);

            this.update();

            this.interval =
                setInterval(() => this.update(), 1000);

        },

        update() {

            if (this.timeLeft <= 0) {

                document.getElementById("timer").innerText = "00:00";

                clearInterval(this.timerInterval);

                // Prevent duplicate auto-submit
                if (!Exam.isSubmitting) {

                    Exam.isSubmitting = true;

                    Exam.submit.finish(true);

                }

                return;

            }

            const minutes =
                Math.floor(this.timeLeft / 60);

            const seconds =
                this.timeLeft % 60;

            document.getElementById("timer").innerText =
                `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;

            this.timeLeft--;

        }

    },

    // ========================================================
    // Student Answers Module
    // ========================================================

    answers: {

        // ----------------------------------------------
        // Highlight a selected answer
        // ----------------------------------------------

        highlight(button){

            document.querySelectorAll(".option-btn").forEach(btn=>{

                btn.classList.remove("btn-primary");

                btn.classList.add("btn-outline-primary");

            });

            button.classList.remove("btn-outline-primary");

            button.classList.add("btn-primary");

        },

        // ----------------------------------------------
        // Save answer to hidden field
        // ----------------------------------------------

        set(answer){

            document.getElementById("selectedAnswer").value =
                answer;

        },

        // ----------------------------------------------
        // Save answer into database
        // ----------------------------------------------

        async save(answer) {

            try {

                const response = await fetch("/save-answer",{

                    method:"POST",

                    headers:{
                        "Content-Type":"application/json"
                    },

                    body:JSON.stringify({

                        question_id:
                            document.getElementById("questionId").value,

                        answer:answer

                    })

                });

                if (!response.ok) {

                    console.error("Unable to save answer.");

                    return;

                }

                Exam.toast.show("✓ Answer Saved");

            }

            catch (error) {

                console.error(error);

            }

            return {
                question_id: document.getElementById("questionId").value,
                answer: answer
            };

        },

        // ----------------------------------------------
        // Student selected an answer
        // ----------------------------------------------

        async select(answer, button) {

            // Store selected answer locally
            document.getElementById("selectedAnswer").value = answer;

            // Remove previous highlight
            document.querySelectorAll(".option-btn").forEach(btn => {

                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline-primary");

            });

            // Highlight current answer
            button.classList.remove("btn-outline-primary");
            button.classList.add("btn-primary");

            // Save answer automatically
            const result = await this.save(answer);

            Exam.navigator.updateSingle(result.question_id, true);

        },

        // ----------------------------------------------
        // Restore previously saved answer
        // ----------------------------------------------

        restore() {

            const savedAnswer =
                document.getElementById("selectedAnswer").value;

            if (!savedAnswer) return;

            document.querySelectorAll(".option-btn").forEach(btn => {

                if (btn.dataset.answer === savedAnswer) {

                    btn.classList.remove("btn-outline-primary");
                    btn.classList.add("btn-primary");

                }

            });

        }

    },

    // ========================================================
    // Question Navigator Module
    // ========================================================

    navigator: {

        // ----------------------------------------------
        // Load navigator data
        // ----------------------------------------------

        async load() {

            try {

                const response =
                    await fetch(reviewAnswersURL);

                const reviewData =
                    await response.json();

                this.render(reviewData, "questionNavigator");
                this.updateSummary(reviewData);

            }

            catch(error) {

                console.error(error);

            }

        },

        render(reviewData, containerId) {

            let html = "";

            reviewData.forEach(item => {

                let buttonClass =
                    item.answered
                        ? "btn-success"
                        : "btn-outline-danger";

                // Highlight the current question
                let currentClass = "";

                if (item.question_id === currentQuestionId) {

                    currentClass = "current-question";

                }

                html += `

                <button
                    data-id="${item.question_id}"
                    class="btn btn-sm m-100 ${buttonClass} ${currentClass}"
                    onclick="Exam.navigation.go('${item.url}')">
                    ${item.question_number}
                </button>

                `;

            });

            document.getElementById(containerId).innerHTML = html;

        },

        // ----------------------------------------------
        // Live update single question status
        // ----------------------------------------------

        updateSingle(questionId, answered) {

            const buttons =
                document.querySelectorAll("#questionNavigator button");

            buttons.forEach(btn => {

                const match =
                    btn.getAttribute("data-id") == questionId;

                if (!match) return;

                // Remove old state classes
                btn.classList.remove("btn-outline-danger");
                btn.classList.remove("btn-success");

                btn.classList.add("nav-pulse");

                setTimeout(() => {
                    btn.classList.remove("nav-pulse");
                }, 350);

                // Apply new state
                btn.classList.add(
                    answered ? "btn-success" : "btn-outline-danger"
                );

            });

        },

        // ----------------------------------------------
        // Update exam summary panel
        // ----------------------------------------------

        updateSummary(reviewData) {

            let answered = 0;
            let total = reviewData.length;

            reviewData.forEach(item => {
                if (item.answered) answered++;
            });

            let remaining = total - answered;
            let percent = Math.round((answered / total) * 100);

            const summary = `
                Answered: ${answered} |
                Remaining: ${remaining} |
                Progress: ${percent}%
            `;

            const el = document.getElementById("examSummary");

            if (el) {
                el.innerHTML = summary;
            }

        }

    },

    // ========================================================
    // Navigation Module
    // Handles movement between questions.
    // ========================================================

    navigation: {

        // ----------------------------------------------
        // Go to another question
        // ----------------------------------------------

        go(url) {

            const card =
                document.getElementById("questionCard");

            // If no animation target exists, just navigate
            if (!card) {

                window.location.href = url;
                return;

            }

            card.classList.add("fade-out");

            setTimeout(() => {

                window.location.href = url;

            }, 250);

        }

    },

    // ========================================================
    // Review Answers Module
    // ========================================================

    review: {

        // ----------------------------------------------
        // Open Review Answers
        // ----------------------------------------------

        async open() {

            try {

                const response = await fetch(reviewAnswersURL);

                if (!response.ok) {

                    throw new Error("Unable to load review data.");

                }

                const reviewData = await response.json();
                const answered =
                    reviewData.filter(item => item.answered).length;

                const remaining =
                    reviewData.length - answered;

                const completion =
                    Math.round((answered / reviewData.length) * 100);

                let navigator = "";

                reviewData.forEach(item => {

                    navigator += `

                    <button
                        class="btn btn-sm m-1
                            ${item.answered
                                ? "btn-success"
                                : "btn-outline-danger"}"

                        onclick="Exam.review.go('${item.url}')">

                        ${item.question_number}

                    </button>

                    `;

                });

                // Build the review table
                let html = `
                <div class="card border-success mb-3">

                    <div class="card-header fw-bold">

                        📋 Exam Review Summary

                    </div>

                    <div class="card-body">

                        <div class="row text-center">

                            <div class="col">

                                <h4 class="text-success">

                                    ${answered}

                                </h4>

                                <small>Answered</small>

                            </div>

                            <div class="col">

                                <h4 class="text-danger">

                                    ${remaining}

                                </h4>

                                <small>Remaining</small>

                            </div>

                            <div class="col">

                                <h4 class="text-primary">

                                    ${completion}%

                                </h4>

                                <small>Completion</small>

                            </div>

                        </div>

                    </div>

                </div>

                <div class="card mb-3">

                    <div class="card-header fw-bold">

                        🧭 Question Navigator

                    </div>

                    <div class="card-body">

                        ${navigator}

                    </div>

                </div>

                <table class="table table-hover align-middle">

                    <thead>

                        <tr>

                            <th>#</th>

                            <th>Status</th>

                            <th>Your Answer</th>

                        </tr>

                    </thead>

                    <tbody>

                `;

                reviewData.forEach(item => {

                    html += `

                    <tr
                        style="cursor:pointer"
                        onclick="Exam.review.go('${item.url}')">

                        <td>

                            ${item.question_number}

                        </td>

                        <td>

                            ${
                                item.answered
                                    ? '<span class="badge bg-success">Answered</span>'
                                    : '<span class="badge bg-danger">Not Answered</span>'
                            }

                        </td>

                        <td>

                            ${item.selected_answer || "—"}

                        </td>

                    </tr>

                    `;

                });

                html += `

                    </tbody>

                </table>

                `;

                // Insert into the modal
                document.getElementById("reviewContent").innerHTML = html;
                // Open the Bootstrap modal
                const modal = new bootstrap.Modal(

                    document.getElementById("reviewModal")

                );

                modal.show();

            }

            catch(error){

                console.error(error);

                Exam.toast.show("Unable to load review.");

            }

        },

        // ----------------------------------------------
        // Go to a selected question
        // ----------------------------------------------

        go(url) {

            const modalElement =
                document.getElementById("reviewModal");

            const modal =
                bootstrap.Modal.getInstance(modalElement);

            if (modal) {

                modal.hide();

            }

            Exam.navigation.go(url);

        }

    },

    // ========================================================
    // Toast Notifications
    // ========================================================

    toast: {

        show(message) {

            const status =
                document.getElementById("saveStatus");

            if (!status) return;

            status.innerHTML = message;

            status.classList.add("show");

            setTimeout(() => {

                status.classList.remove("show");

            }, 1000);

        }

    },

    // ========================================================
    // Submit Exam Module
    // ========================================================

    submit: {

        finish(auto = false) {

            if (Exam.isSubmitting) {

                return;

            }

            Exam.isSubmitting = true;

            if (!auto) {

                if (!confirm("Are you sure you want to submit your exam?")) {

                    return;

                }

            }

            window.location.href = submitExamURL;

        }

    }

};

// ============================================================
// Start the Exam Engine
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    Exam.init();

});