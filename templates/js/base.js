// initialization

const RESPONSIVE_WIDTH = 1024


function initializePasswordInputs() {

    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach((passwordInput) => {
        // Create a container div 
        const container = passwordInput.parentElement
        // Create a toggle button
        const toggleButton = document.createElement('button');

        toggleButton.classList.add("btn", "toggle-password");
        toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';

        // Append the elements to the container
        container.appendChild(toggleButton);

        toggleButton.addEventListener('click', (e) => {
            e.preventDefault()
            togglePasswordVisibility(toggleButton, passwordInput);
        });
    })
}



function togglePasswordVisibility(toggleButton, inputElement) {
    if (inputElement.type === "password") {
        inputElement.type = "text";
        toggleButton.innerHTML = '<i class="bi bi-eye"></i>';
    } else {
        inputElement.type = "password";
        toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    }
}

initializePasswordInputs()

// mobile state detection

let headerWhiteBg = false
let isHeaderCollapsed = window.innerWidth < RESPONSIVE_WIDTH
const collapseBtn = document.getElementById("collapse-btn")
const collapseHeaderItems = document.getElementById("collapsed-header-items")



function onHeaderClickOutside(e) {

    if (!collapseHeaderItems.contains(e.target)) {
        toggleHeader()
    }

}

// mobile menu open logic
function toggleHeader() {
    if (isHeaderCollapsed) {
        // collapseHeaderItems.classList.remove("max-md:tw-opacity-0")
        collapseHeaderItems.classList.add("opacity-100",)
        collapseHeaderItems.style.width = "60vw"
        collapseBtn.classList.remove("bi-list")
        collapseBtn.classList.add("bi-x", "max-lg:tw-fixed")
        isHeaderCollapsed = false

        setTimeout(() => window.addEventListener("click", onHeaderClickOutside), 1)

    } else {
        collapseHeaderItems.classList.remove("opacity-100")
        collapseHeaderItems.style.width = "0vw"
        collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed")
        collapseBtn.classList.add("bi-list")
        isHeaderCollapsed = true
        window.removeEventListener("click", onHeaderClickOutside)

    }
}

function responsive() {
    if (window.innerWidth > RESPONSIVE_WIDTH) {
        collapseHeaderItems.style.width = ""

    } else {
        isHeaderCollapsed = true
    }
}

window.addEventListener("resize", responsive)

// Dropdown functionality - Chrome compatible
function initDropdowns() {
    var servicesDropdown = document.getElementById('services-dropdown');
    var awardsDropdown = document.getElementById('awards-dropdown');
    var servicesTrigger = document.getElementById('services-dropdown-trigger');
    var awardsTrigger = document.getElementById('awards-dropdown-trigger');
    var isMobile = window.innerWidth < 1024;

    function checkIfMobile() {
        isMobile = window.innerWidth < 1024;
    }

    window.addEventListener('resize', checkIfMobile);

    if (servicesDropdown && servicesTrigger) {
        var servicesContainer = servicesTrigger.parentElement;

        // Desktop hover functionality
        if (servicesContainer) {
            servicesContainer.addEventListener('mouseenter', function () {
                if (!isMobile) {
                    servicesDropdown.classList.add('show');
                }
            });

            servicesContainer.addEventListener('mouseleave', function () {
                if (!isMobile) {
                    servicesDropdown.classList.remove('show');
                }
            });
        }

        // Mobile click functionality
        servicesTrigger.addEventListener('click', function (e) {
            if (isMobile) {
                e.preventDefault();
                e.stopPropagation();
                servicesDropdown.classList.toggle('show');
            }
        });
    }

    if (awardsDropdown && awardsTrigger) {
        var awardsContainer = awardsTrigger.parentElement;

        // Desktop hover functionality
        if (awardsContainer) {
            awardsContainer.addEventListener('mouseenter', function () {
                if (!isMobile) {
                    awardsDropdown.classList.add('show');
                }
            });

            awardsContainer.addEventListener('mouseleave', function () {
                if (!isMobile) {
                    awardsDropdown.classList.remove('show');
                }
            });
        }

        // Mobile click functionality
        awardsTrigger.addEventListener('click', function (e) {
            if (isMobile) {
                e.preventDefault();
                e.stopPropagation();
                awardsDropdown.classList.toggle('show');
            }
        });
    }

    // Close dropdowns on click outside (mobile only)
    document.addEventListener('click', function (e) {
        if (isMobile) {
            if (servicesDropdown && servicesTrigger) {
                var servicesContainer = servicesTrigger.parentElement;
                if (servicesContainer && !servicesContainer.contains(e.target)) {
                    servicesDropdown.classList.remove('show');
                }
            }
            if (awardsDropdown && awardsTrigger) {
                var awardsContainer = awardsTrigger.parentElement;
                if (awardsContainer && !awardsContainer.contains(e.target)) {
                    awardsDropdown.classList.remove('show');
                }
            }
        }
    });
}

// Initialize dropdowns when DOM is ready
(function () {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDropdowns);
    } else {
        initDropdowns();
    }
})();