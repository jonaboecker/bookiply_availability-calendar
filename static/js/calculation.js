const PRICING_CONFIG = {
    // additionalPerson applies to additional adults & children > 15
    2024: {
        perWeek: {
            firstTwoAdults: 330,
            additionalPerson: 140,
            childTo3: 0,
            child3to6: 70,
            child6to15: 90,
        },
        perDay: {
            touristTax: 2.5,
            touristTaxChild: 1.3,
        }
    },
    2025: {
        perWeek: {
            firstTwoAdults: 345,
            additionalPerson: 140,
            childTo3: 0,
            child3to6: 75,
            child6to15: 95,
        },
        perDay: {
            touristTax: 2.5,
            touristTaxChild: 1.3,
        }
    },
    default: { // Applies for 2026 and all following years
        perWeek: {
            firstTwoAdults: 355,
            additionalPerson: 145,
            childTo3: 0,
            child3to6: 75,
            child6to15: 100,
        },
        perDay: {
            touristTax: 2.5,
            touristTaxChild: 1.3,
        }
    }
};

const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24;
const CANCELLATION_WEEKS = 4;

/**
 * Gets the correct price config for the year.
 * @param {number} year - Booking year.
 * @returns {object} Price config for the year.
 */
function getPricingForYear(year) {
    return PRICING_CONFIG[year] || PRICING_CONFIG.default;
}

/**
 * Calculates the overnight flat rate for all persons.
 * @param {object} config - Price config for the year.
 * @param {number} adults - Amount of Adults.
 * @param {number[]} childrenAges - Array with kids age.
 * @param {number} weeks - Booked weeks.
 * @returns {number} Overall flat rate.
 */
function calculateFlatRate(config, adults, childrenAges, weeks) {
    let totalRate = 0;
    const { perWeek } = config;

    // Adults
    for (let i = 1; i <= adults; i++) {
        totalRate += (i <= 2) ? perWeek.firstTwoAdults : perWeek.additionalPerson;
    }

    // Children (and persons > 15)
    for (const age of childrenAges) {
        if (age < 3) totalRate += perWeek.childTo3;
        else if (age < 6) totalRate += perWeek.child3to6;
        else if (age <= 15) totalRate += perWeek.child6to15;
        else totalRate += perWeek.additionalPerson; // children > 15 pay like adults
    }

    return totalRate * weeks;
}

/**
 * Calculates the total tourist tax.
 * @param {object} config - price config for the year.
 * @param {number} adults - amount of Adults.
 * @param {number[]} childrenAges - Array with kids age.
 * @param {number} days - Booked days.
 * @returns {number} Calculated tourist tax.
 */
function calculateTax(config, adults, childrenAges, days) {
    let totalTax = 0;
    const { perDay } = config;

    totalTax += adults * perDay.touristTax;

    for (const age of childrenAges) {
        if (age > 16) totalTax += perDay.touristTax;
        else if (age > 6) totalTax += perDay.touristTaxChild;
    }

    return totalTax * days;
}

/**
 * Calculates the total price based on the booking details.
 * @param {object} data - A Object with all necessary booking information.
 * @returns {object|null} - An object with the price details or null if the duration is invalid.
 */
function calculatePrice(data) {
    const { startDateStr, endDateStr, adults, childrenAges } = data;

    const startDate = new Date(startDateStr);
    const endDate = new Date(endDateStr);
    const days = (endDate - startDate) / MILLISECONDS_PER_DAY;

    if (days <= 0 || days % 7 !== 0) {
        return { validDuration: false };
    }

    const weeks = days / 7;
    const bookingYear = startDate.getFullYear();
    const config = getPricingForYear(bookingYear);

    const flatRate = calculateFlatRate(config, adults, childrenAges, weeks);
    const tax = calculateTax(config, adults, childrenAges, days);

    // Storno logic
    const cancellationDeadline = new Date(startDate.getTime() - (CANCELLATION_WEEKS * 7 * MILLISECONDS_PER_DAY));
    const stornoText = new Date() < cancellationDeadline
        ? "möglich bis " + cancellationDeadline.toLocaleDateString()
        : "nicht mehr möglich";

    return {
        validDuration: true,
        days: days,
        flatRate: flatRate,
        tax: tax,
        total: flatRate + tax,
        stornoText: stornoText,
    };
}
