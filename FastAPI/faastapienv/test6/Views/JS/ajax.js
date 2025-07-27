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

async function showFacilityID(facilityId) {
  try {
    const r = await fetch("/ecoUser/deleteUser", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({"id": facilityId})
    });

    if (r.ok) {
      // Remove the facility from the page
      const facilityRows = document.querySelectorAll(`[data-facility-id="${facilityId}"]`);
      facilityRows.forEach(row => row.remove());
      
      if (testing) {
        testing.textContent = `Facility ${facilityId} deleted successfully!`;
      }
      
      showNotification('Facility deleted successfully!', 'success');
    } else {
      if (testing) {
        testing.textContent = `Error deleting facility ${facilityId}`;
      }
      showNotification('Error deleting facility', 'error');
    }
  } catch (error) {
    if (testing) {
      testing.textContent = `Error: ${error.message}`;
    }
    showNotification('Error deleting facility', 'error');
  }
  
}



// Edit facility function
async function updateEcoFacility(event) {
  event.preventDefault();
  
  const facilityId = document.getElementById("facilityId").value;
  const facilityTitle = document.getElementById("facilityTitle").value;
  const facilityCategory = document.getElementById("facilityCategory").value;
  const facilityDescription = document.getElementById("facilityDescription").value;
  const houseNumber = document.getElementById("houseNumber").value;
  const streetName = document.getElementById("streetName").value;
  const county = document.getElementById("county").value;
  const town = document.getElementById("town").value;
  const postcode = document.getElementById("postcode").value;
  const latitude = parseFloat(document.getElementById("latitude").value);
  const longitude = parseFloat(document.getElementById("longitude").value);

  const facilityData = {
    id: parseInt(facilityId),
    title: facilityTitle,
    category: parseInt(facilityCategory),
    description: facilityDescription,
    houseNumber: houseNumber,
    streetName: streetName,
    county: county,
    town: town,
    postcode: postcode,
    lat: latitude,
    lng: longitude
  };

  try {
    const response = await fetch("/ecoUser/updateFacility", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(facilityData),
    });

    if (response.ok) {
      const result = await response.json();
      showNotification("Facility updated successfully!", "success");
      
      // Redirect to home page after successful update
      setTimeout(() => {
        window.location.href = "/";
      }, 1500);
      
    } else {
      const errorData = await response.json();
      showNotification(`Error: ${errorData.detail}`, "error");
    }
  } catch (error) {
    console.error("Error:", error);
    showNotification("An error occurred while updating the facility", "error");
  }
}

// Add event listener for edit form
const editFacilityForm = document.getElementById("editFacilityForm");
if (editFacilityForm) {
  editFacilityForm.addEventListener("submit", updateEcoFacility);
}