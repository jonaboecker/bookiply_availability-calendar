function price() {
    // prices per week:
    const firstadults = 311.5;
    const person = 140;
    const childTo3 = 0;
    const child3to6 = 70;
    const child6to15 = 87.5;
    // per day:
    const touristTax = 2.5;
    const touristTaxChildren = 1.3;

    const adults = parseInt(document.getElementById("adults").value);
    const children = parseInt(document.getElementById("children").value);
    let childrenAges = [children];
    for (let i = 1; i <= children; i++) {
        childrenAges[i - 1] = document.getElementById("age-" + i).value;
    }
    const startDate = new Date(document.getElementById("start-date").value);
    const endDate = new Date(document.getElementById("end-date").value);
    const days = (endDate - startDate) / (1000 * 60 * 60 * 24);
    if (days <= 0 || days % 7 !== 0) {
        hideElem('pricing');
        return;
    }
    if (startDate === "Invalid Date" || endDate === "Invalid Date") {
        hideElem('pricing');
        return;
    }
    const box = document.getElementById('pricing');
    box.style.display = 'block';
    const currentGuests = parseInt(adults.value) + parseInt(children.value);
    let p_flat = 0;
    let taxAmount = 0;
    let weeks = days / 7;
    for (let i = 1; i <= adults; i++) {
        if(i <= 2) {
            p_flat += firstadults * weeks
        } else {
            p_flat += person * weeks;
        }
        taxAmount += touristTax * 7 * weeks - touristTax;
    }
    for (let i = 0; i < children; i++) {
        if (childrenAges[i] < 3) {
            p_flat += childTo3 * weeks;
        } else if (childrenAges[i] < 6) {
            p_flat += child3to6 * weeks;
        } else if (childrenAges[i] <= 15) {
            p_flat += child6to15 * weeks;
        } else {
            p_flat += person * weeks;
        }
        if(childrenAges[i] > 16) {
            taxAmount += touristTax * 7 * weeks - touristTax;
        } else if (childrenAges[i] > 6) {
            taxAmount += touristTaxChildren * 7 * weeks - touristTaxChildren;
        }
    }
    let elem_p_days = document.getElementById('p_days');
    let elem_p_flat = document.getElementById('p_flat');
    let elem_p_tourist_tax = document.getElementById('p_tourist-tax');
    let elem_p_total = document.getElementById('p_total');
    let input_p_flat = document.getElementById('price-flat');
    let input_p_tax = document.getElementById('price-tax');
    elem_p_days.textContent = String(days);
    elem_p_flat.textContent = String(p_flat);
    elem_p_tourist_tax.textContent = String(taxAmount);
    elem_p_total.textContent = String(p_flat + taxAmount);
    input_p_flat.value = String(p_flat);
    input_p_tax.value = String(taxAmount);
}
