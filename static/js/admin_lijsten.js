// static/js/admin_lijsten.js
// Overzichtslijsten in de admin (zie templates/admin/_lijst_macros.html):
// - een keuzelijst in de filterbalk wijzigen filtert meteen
// - het vinkje in de kolomkop selecteert alle rijen van de pagina
// - de bulkknoppen werken pas als er iets geselecteerd is
document.querySelectorAll('[data-filter-auto] select').forEach((select) => {
    select.addEventListener('change', () => select.form.submit());
});

document.querySelectorAll('[data-bulk-form]').forEach((form) => {
    const alles = form.querySelector('[data-alles-selecteren]');
    const vinkjes = Array.from(form.querySelectorAll('input[name="ids"]'));
    const knoppen = Array.from(form.querySelectorAll('[data-bulk-knop]'));
    const teller = form.querySelector('[data-bulk-teller]');

    function bijwerken() {
        const aantal = vinkjes.filter((v) => v.checked).length;
        knoppen.forEach((knop) => { knop.disabled = aantal === 0; });
        if (teller) teller.textContent = aantal ? `${aantal} geselecteerd` : '';
        if (alles) {
            alles.checked = aantal > 0 && aantal === vinkjes.length;
            alles.indeterminate = aantal > 0 && aantal < vinkjes.length;
        }
    }

    if (alles) {
        alles.addEventListener('change', () => {
            vinkjes.forEach((v) => { v.checked = alles.checked; });
            bijwerken();
        });
    }
    vinkjes.forEach((v) => v.addEventListener('change', bijwerken));
    bijwerken();
});
