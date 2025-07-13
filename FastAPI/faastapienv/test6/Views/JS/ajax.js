// Simple notification function
function showNotification(message, type = 'info') {
  alert(message);
}

// Search functionality
function initializeSearch() {
  const searchInput = document.getElementById("search");
  const resultsDiv = document.getElementById("searchResults");
  
  if (!searchInput || !resultsDiv) return;

  searchInput.addEventListener("input", async function() {
    const q = this.value.trim();
    
    if (!q) {
      resultsDiv.classList.add("d-none");
      return;
    }

    try {
      const response = await fetch("/ecoUser/liveSearch", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query: q})
      });
      
      const data = await response.json();
      let html = "";
      
      if (data.length > 0) {
        data.forEach(facility => {
          html += `
            <div class="p-3 border-bottom">
              <h6 class="mb-1">${facility.ecoTitle}</h6>
              <small class="text-muted">Category: ${facility.categoryName} | By: ${facility.contributorName}</small>
              <p class="mb-0 small">${facility.ecoDescription}</p>
            </div>`;
        });
      } else {
        html = `<div class="p-3 text-center text-muted">No results found for "${q}"</div>`;
      }
      
      resultsDiv.innerHTML = html;
      resultsDiv.classList.remove("d-none");
      
    } catch (error) {
      console.error("Search error:", error);
    }
  });

  // Hide search results when clicking outside
  document.addEventListener("click", function(e) {
    if (!e.target.closest("#search") && !e.target.closest("#searchResults")) {
      resultsDiv.classList.add("d-none");
    }
  });
}

// Login function
async function sendUserPassword(event) {
  event.preventDefault();
  const username = document.getElementById('usrname').value;
  const password = document.getElementById('passwd').value;

  try {
    const response = await fetch('/ecoUser/ecoUserLogin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "username": username, "password": password })
    });

    const data = await response.json();

    if (response.ok) {
      showNotification('Logged in successfully!');
      setTimeout(() => window.location.href = '/', 1500);
    } else {
      showNotification('Login failed: ' + (data.detail || 'Please try again'));
    }
  } catch (error) {
    showNotification('Network error. Please try again.');
  }
}

// Add facility function
async function addEcoFacility(event) {
  event.preventDefault();

  const facilityData = {
    title: document.getElementById("facilityTitle").value,
    category: parseInt(document.getElementById("facilityCategory").value),
    description: document.getElementById("facilityDescription").value,
    houseNumber: document.getElementById("houseNumber").value,
    streetName: document.getElementById("streetName").value,
    county: document.getElementById("county").value,
    town: document.getElementById("town").value,
    postcode: document.getElementById("postcode").value,
    lng: parseFloat(document.getElementById("longitude").value),
    lat: parseFloat(document.getElementById("latitude").value)
  };

  try {
    const response = await fetch("/ecoUser/addEcoFacility", {
      method: 'POST',
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(facilityData)
    });userFormlogin

    if (response.status === 201) {
      showNotification('EcoFacility added successfully!');
      setTimeout(() => window.location.href = '/', 1500);
    } else {
      showNotification('Failed to add EcoFacility.');
    }
  } catch (error) {
    showNotification('Error adding facility.');
  }
}

// Initialize search functionality
initializeSearch();

// Initialize form event listeners
const userFormlogin = document.getElementById('userFormlogin');
const facilityForm = document.getElementById("facilityForm");

if (userFormlogin) {
  userFormlogin.addEventListener("submit", sendUserPassword);
}

if (facilityForm) {
  facilityForm.addEventListener("submit", addEcoFacility);
}

