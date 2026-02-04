
const countryCodeDropdown = document.getElementById("country-codes")


// console.log(JSON.parse(countryCodes))

async function loadCountryCodes() {

    // Immediate default to ensure something is there while fetching
    if (countryCodeDropdown.options.length === 0) {
        const defaultOption = document.createElement("option");
        defaultOption.text = "🇮🇳 +91";
        defaultOption.value = "+91";
        defaultOption.selected = true;
        countryCodeDropdown.appendChild(defaultOption);
    }
    countryCodeDropdown.value = "+91";

    const countryCodes = await fetchCountryCodes()

    if (!countryCodes) {
        toastAlert("failed to fetch country codes")
        return
    }

    // Sort country codes to put India (IN) at the top
    countryCodes.sort((a, b) => {
        if (a.code === 'IN') return -1;
        if (b.code === 'IN') return 1;
        return 0;
    });

    // Clear existing options (including our placeholder)
    countryCodeDropdown.innerHTML = "";

    let indiaOption = null;

    countryCodes.forEach(e => {
        const option = document.createElement("option");
        const dial = e.dial_code.startsWith('+') ? e.dial_code : `+${e.dial_code}`;
        option.innerText = `${e.emoji} ${dial}`;
        option.setAttribute("value", dial);

        // Forced default for India
        if (e.code === "IN" || dial === "+91") {
            option.selected = true;
            option.setAttribute("selected", "selected");
            indiaOption = option;
        }

        countryCodeDropdown.appendChild(option);
    });

    // Final hard set
    if (indiaOption) {
        countryCodeDropdown.value = "+91";
        indiaOption.selected = true;
    }

    // Safety check just in case
    setTimeout(() => {
        if (countryCodeDropdown.value !== "+91") {
            countryCodeDropdown.value = "+91";
        }
    }, 500);

}


loadCountryCodes()


const phone = document.querySelector("input[name='phone']") // full phone number
const countryCode = document.querySelector("select[name='country-codes']")
const phoneNumber = document.querySelector("input[name='phone-number']") // number without country code
const visitorName = document.querySelector("input[name='name']")
const email = document.querySelector("input[name='email']")


setInputFilter(phoneNumber, (value) => {
    return /^[0-9]*$/.test(value)
}, "only numbers are allowed")


function onSubmit(event) {
    // event.preventDefault()

    if (visitorName.value.length < 2) {
        toastAlert(null, "Enter a proper name", "danger")
        event.stopImmediatePropagation()
        return false
    }

    if (!isValidEmail(email.value)) {
        toastAlert(null, "Enter a valid email", "danger")
        event.stopImmediatePropagation()
        return false
    }

    if ((phoneNumber.getAttribute("required") || phoneNumber.value.length > 1) && phoneNumber.value.length < 5) {
        toastAlert(null, "Enter a proper phone number", "danger")
        event.stopImmediatePropagation()

        return false
    }

    phone.value = `${countryCode.value + phoneNumber.value}`

    // console.log("phone number: ", phone.value)

    return true
}