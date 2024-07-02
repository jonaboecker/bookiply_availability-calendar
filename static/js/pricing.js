function price() {
    let firstadults, person, childTo3, child3to6, child6to15, touristTax, touristTaxChildren;

    if (new Date(document.getElementById("start-date").value).getFullYear() === 2024) {
        firstadults = 330;
        person = 140;
        childTo3 = 0;
        child3to6 = 70;
        child6to15 = 90;
        touristTax = 2.5;
        touristTaxChildren = 1.3;
    } else {
        firstadults = 345;
        person = 150;
        childTo3 = 0;
        child3to6 = 75;
        child6to15 = 95;
        touristTax = 2.5;
        touristTaxChildren = 1.3;
    }

    const startDate = new Date(document.getElementById("start-date").value);
    const endDate = new Date(document.getElementById("end-date").value);
    const days = (endDate - startDate) / (1000 * 60 * 60 * 24);
    if (days <= 0 || days % 7 !== 0) {
        hideElem('pricing');
        showElem('pricing-preview')
    } else {
        showElem('pricing')
        hideElem('pricing-preview')
    }

    const adults = parseInt(document.getElementById("adults").value);
    const children = parseInt(document.getElementById("children").value);
    let childrenAges = [children];
    for (let i = 1; i <= children; i++) {
        childrenAges[i - 1] = document.getElementById("age-" + i).value;
    }
    let p_flat = 0;
    let taxAmount = 0;
    let weeks = days / 7;
    for (let i = 1; i <= adults; i++) {
        if (i <= 2) {
            p_flat += firstadults * weeks
        } else {
            p_flat += person * weeks;
        }
        taxAmount += touristTax * 7 * weeks;
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
        if (childrenAges[i] > 16) {
            taxAmount += touristTax * 7 * weeks;
        } else if (childrenAges[i] > 6) {
            taxAmount += touristTaxChildren * 7 * weeks;
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
