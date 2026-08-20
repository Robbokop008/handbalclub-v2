// static/js/home_slider.js
// Kleine, afhankelijkheidsloze slider voor het "Laatste nieuws"-kaartje op
// de homepage: één nieuwsitem tegelijk zichtbaar, bediend via de puntjes
// onderaan en automatisch doorschuivend.
document.querySelectorAll('[data-nieuws-slider]').forEach((slider) => {
    const track = slider.querySelector('.nieuws-slider-track');
    const slides = Array.from(track.children);
    const dots = Array.from(slider.querySelectorAll('.nieuws-slider-dot'));
    let index = 0;
    let timer = null;

    function show(i) {
        index = (i + slides.length) % slides.length;
        track.style.transform = `translateX(-${index * 100}%)`;
        dots.forEach((dot, j) => dot.classList.toggle('active', j === index));
    }

    function restartAutoplay() {
        if (timer) clearInterval(timer);
        if (slides.length > 1) {
            timer = setInterval(() => show(index + 1), 6000); //tijd per item in miliseconden: standaard 6000 (=6s)
        }
    }

    dots.forEach((dot, i) => {
        dot.addEventListener('click', () => {
            show(i);
            restartAutoplay();
        });
    });

    show(0);
    restartAutoplay();
});
