/**
 * Updates the Price on the UI dependent on booking information.
 */

function updatePriceOnUI() {
    const startDateValue = document.getElementById("start-date").value;
    const endDateValue = document.getElementById("end-date").value;

    // Collect data from form
    const adults = parseInt(document.getElementById("adults").value);
    const childrenCount = parseInt(document.getElementById("children").value);
    let childrenAges = [];
    for (let i = 1; i <= childrenCount; i++) {
        childrenAges.push(parseInt(document.getElementById("age-" + i).value));
    }

    // Create the data object for the calculation function
    const bookingData = {
        startDateStr: startDateValue,
        endDateStr: endDateValue,
        adults: adults,
        childrenAges: childrenAges
    };

    const result = calculatePrice(bookingData);

    // Process the result and update the website
    if (!result.validDuration) {
        hideElem('pricing');
        showElem('pricing-preview');
        return;
    }

    showElem('pricing');
    hideElem('pricing-preview');

    document.getElementById('p_days').textContent = result.days;
    document.getElementById('p_flat').textContent = result.flatRate;
    document.getElementById('p_tourist-tax').textContent = result.tax;
    document.getElementById('p_total').textContent = result.total;
    document.getElementById('p_storno').textContent = result.stornoText;

    // Update form fields for submission
    document.getElementById('price-flat').value = result.flatRate;
    document.getElementById('price-tax').value = result.tax;
    document.getElementById('storno-date').value = result.stornoText;
}

function showElem(id) { document.getElementById(id).style.display = 'block'; }
function hideElem(id) { document.getElementById(id).style.display = 'none'; }