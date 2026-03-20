document.querySelectorAll(".question-card").forEach(card => {
    const correct = card.dataset.answer;

    card.querySelectorAll(".option").forEach(btn => {
        btn.addEventListener("click", () => {

            card.querySelectorAll(".option").forEach(b => {
                b.disabled = true;
                if (b.dataset.option === correct) {
                    b.classList.add("correct");
                }
            });

            if (btn.dataset.option !== correct) {
                btn.classList.add("wrong");
            }
        });
    });
});
