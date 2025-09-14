function getUserDateTime() {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

// Toast notification function
const showToast = (message, type = 'info') => {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'position-fixed top-0 end-0 p-3';
    toastContainer.style.zIndex = '1055';
    document.body.appendChild(toastContainer);
  }

  // Create toast
  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  // Show toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, {
    autohide: true,
    delay: 3000
  });
  toast.show();
  
  // Remove toast element after it's hidden
  toastElement.addEventListener('hidden.bs.toast', function() {
    toastElement.remove();
  });
};

// Edit current title function
const edit_current_title = () => {
  const titleElement = document.getElementById('title');
  const titleEditDiv = document.getElementById('current-title-edit');
  const currentTitle = titleElement.textContent;
  
  // Hide title and show edit interface
  titleElement.style.display = 'none';
  titleEditDiv.style.display = 'block';
  
  // Create title edit interface with cancel button
  titleEditDiv.innerHTML = `
    <label class="form-label text-light small">Edit Title:</label>
    <input type="text" id="current-title-input" 
           class="form-control bg-dark text-light border-warning mb-3 text-center" 
           value="${currentTitle}">
    <div class="d-flex gap-2 justify-content-center">
      <button class="btn btn-sm btn-outline-secondary" onclick="cancel_current_title_edit()">Cancel</button>
      <button class="btn btn-sm btn-outline-success" onclick="save_current_title()">OK</button>
    </div>
  `;
  
  // Focus on the input
  const titleInput = document.getElementById('current-title-input');
  titleInput.focus();
  titleInput.select();
};

// Cancel current title edit function
const cancel_current_title_edit = () => {
  const titleElement = document.getElementById('title');
  const titleEditDiv = document.getElementById('current-title-edit');
  
  // Hide edit interface and show title
  titleEditDiv.style.display = 'none';
  titleElement.style.display = 'block';
  titleEditDiv.innerHTML = '';
};

// Save current title function
const save_current_title = () => {
  const titleInput = document.getElementById('current-title-input');
  const newTitle = titleInput.value.trim();
  
  if (!newTitle) {
    showToast("Title cannot be empty!", "warning");
    return;
  }
  
  // Update the title element
  const titleElement = document.getElementById('title');
  const titleEditDiv = document.getElementById('current-title-edit');
  
  titleElement.textContent = newTitle;
  
  // Hide edit interface and show title
  titleEditDiv.style.display = 'none';
  titleElement.style.display = 'block';
  titleEditDiv.innerHTML = '';
};

// Global variable to track if we're editing an expanded reflection
let expandedReflectionData = null;

const form = document.getElementById("reflectionForm");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const reflection = document.getElementById("reflection").value;
    const title = document.getElementById("title").textContent;

    // Basic validation
    if (!reflection.trim()) {
      showToast("Please write your reflection before saving.", "warning");
      return;
    }

    if (!title.trim()) {
      showToast("Please set a title for your reflection.", "warning");
      return;
    }

    try {
      let response;
      
      // Check if we're editing an expanded reflection
      if (expandedReflectionData) {
        // Update existing reflection with original date
        response = await fetch("/reflection/update-reflection-by-id", {
          method: "PUT",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            "reflection": reflection,
            "title": title,
            "id": parseInt(expandedReflectionData.id)
          }),
          credentials: 'include'
        });
        
        if (response.status === 401) {
          showToast("Your session has expired. Please log in again.", "danger");
          setTimeout(() => { window.location.href = "/login"; }, 2000);
          return;
        }

        if (!response.ok) {
          showToast("Failed to update your reflection. Please try again.", "danger");
          return;
        }
        
        // Clear the expanded reflection data
        expandedReflectionData = null;
        form.reset();
        showToast("Reflection updated successfully!", "success");
        
      } else {
        // Create new reflection with current date
        response = await fetch("/reflection/add-reflection", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            reflection: reflection,
            date: getUserDateTime(),
            title: title
          }),
          credentials: 'include'
        });

        if (response.status === 401) {
          showToast("Please log in to save your reflection.", "danger");
          setTimeout(() => { window.location.href = "/login"; }, 2000);
          return;
        }

        if (response.status === 422) {
          showToast("Please check your reflection content and try again.", "warning");
          return;
        }

        if (!response.ok) {
          showToast("Failed to save your reflection. Please try again.", "danger");
          return;
        }

        const data = await response.json();
        addNewReflection(data.date, data.id, data.title);
        form.reset();
        showToast("Reflection saved successfully!", "success");
      }
      
    } catch (error) {
      showToast("Connection error. Please check your internet and try again.", "danger");
    }
  });
}

function addNewReflection(date, id, title) {
  const list = document.querySelector('.list-group-flush');
  if (!list) return;

  const emptyMsg = list.querySelector('li:has(.text-secondary)');
  if (emptyMsg?.textContent.includes('No reflections')) emptyMsg.remove();

  list.insertAdjacentHTML('afterbegin', `
    <li class="list-group-item bg-dark text-light border-secondary" id="reflection-item-${id}">
      <div class="reflection-summary" id="summary-${id}">
        <div class="small text-secondary mb-1">${date}</div>
        <h6 class="mb-2 text-light" style="cursor: pointer;" onclick="edit_title('${id}')" title="Click to edit title">${title}</h6>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-info" onclick="view_reflection('${id}')">View</button>
          <button class="btn btn-sm btn-outline-danger" onclick="delete_reflection('${id}')">Delete</button>
        </div>
      </div>
      <div class="reflection-content" id="content-${id}" style="display: none;">
        <!-- Textarea will be inserted here -->
      </div>
      <div class="title-edit" id="title-edit-${id}" style="display: none;">
        <!-- Title edit will be inserted here -->
      </div>
    </li>
  `);
}

// Global variable to store current reflection data
let currentReflectionData = {};

// View reflection function - shows editable textarea immediately
const view_reflection = async (reflection_id) => {
  try {
    const summaryDiv = document.getElementById(`summary-${reflection_id}`);
    const contentDiv = document.getElementById(`content-${reflection_id}`);
    
    // If already viewing, hide the content and show summary
    if (contentDiv.style.display === 'block') {
      contentDiv.style.display = 'none';
      summaryDiv.style.display = 'block';
      contentDiv.innerHTML = ''; // Clear the textarea
      return;
    }

    const response = await fetch("/reflection/get-reflection-by-id", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({"id": parseInt(reflection_id)}),
      credentials: 'include'
    });

    if (!response.ok) {
      showToast("Failed to fetch reflection", "danger");
      return;
    }

    const data = await response.json();
    
    // Store the current reflection data
    currentReflectionData[reflection_id] = data;
    
    // Hide summary and show content
    summaryDiv.style.display = 'none';
    contentDiv.style.display = 'block';
    
    // Create editable textarea with cancel, expand, and OK buttons
    contentDiv.innerHTML = `
      <div class="small text-secondary mb-1">${data.date}</div>
      <h6 class="mb-2 text-light">${data.title}</h6>
      <textarea id="textarea-${reflection_id}" 
                class="form-control bg-dark text-light border-warning mb-3" 
                rows="8">${data.reflection}</textarea>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-secondary" onclick="cancel_reflection_edit('${reflection_id}')">Cancel</button>
        <button class="btn btn-sm btn-outline-info" onclick="expand_to_main('${reflection_id}')">Expand</button>
        <button class="btn btn-sm btn-outline-success" onclick="save_reflection('${reflection_id}')">OK</button>
      </div>
    `;
    
    // Focus on the textarea
    const textarea = document.getElementById(`textarea-${reflection_id}`);
    textarea.focus();
    
  } catch (error) {
    showToast("Error viewing reflection", "danger");
  }
};

// Cancel reflection edit function
const cancel_reflection_edit = (reflection_id) => {
  const summaryDiv = document.getElementById(`summary-${reflection_id}`);
  const contentDiv = document.getElementById(`content-${reflection_id}`);
  
  contentDiv.style.display = 'none';
  summaryDiv.style.display = 'block';
  contentDiv.innerHTML = '';
};

// Expand to main page function
const expand_to_main = (reflection_id) => {
  const textarea = document.getElementById(`textarea-${reflection_id}`);
  const data = currentReflectionData[reflection_id];
  
  if (!textarea || !data) return;
  
  // Get current content from textarea (in case user made changes)
  const currentReflectionContent = textarea.value;
  
  // Store the expanded reflection data (including original date and ID)
  expandedReflectionData = {
    id: reflection_id,
    title: data.title,
    date: data.date,
    reflection: currentReflectionContent
  };
  
  // Update main page title
  const mainTitle = document.getElementById('title');
  if (mainTitle) {
    mainTitle.textContent = data.title;
  }
  
  // Update main page reflection textarea
  const mainReflection = document.getElementById('reflection');
  if (mainReflection) {
    mainReflection.value = currentReflectionContent;
  }
  
  // Close the offcanvas
  const offcanvas = document.getElementById('historyOffcanvas');
  if (offcanvas) {
    const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvas);
    if (bsOffcanvas) {
      bsOffcanvas.hide();
    }
  }
  
  // Close the current edit view
  cancel_reflection_edit(reflection_id);
  
  // Focus on the main reflection textarea
  if (mainReflection) {
    mainReflection.focus();
  }
};

// Save reflection function - updates the reflection content
const save_reflection = async (reflection_id) => {
  const textarea = document.getElementById(`textarea-${reflection_id}`);
  const newContent = textarea.value.trim();
  
  if (!newContent) {
    showToast("Reflection content cannot be empty.", "warning");
    return;
  }
  
  try {
    const response = await fetch("/reflection/update-reflection-by-id", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        "reflection": newContent,
        "id": parseInt(reflection_id)
      }),
      credentials: 'include'
    });

    if (response.status === 401) {
      showToast("Your session has expired. Please log in again.", "danger");
      return;
    }

    if (!response.ok) {
      showToast("Failed to save changes. Please try again.", "danger");
      return;
    }
    
    // Update the stored data
    currentReflectionData[reflection_id].reflection = newContent;
    
    // Close the edit view
    cancel_reflection_edit(reflection_id);
    showToast("Reflection updated successfully!", "success");
    
  } catch (error) {
    showToast("Connection error. Please try again.", "danger");
  }
};

// Edit title function
const edit_title = async (reflection_id) => {
  try {
    // First fetch the current data if not already loaded
    if (!currentReflectionData[reflection_id]) {
      const response = await fetch("/reflection/get-reflection-by-id", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"id": parseInt(reflection_id)}),
        credentials: 'include'
      });

      if (!response.ok) {
        showToast("Failed to fetch reflection", "danger");
        return;
      }

      const data = await response.json();
      currentReflectionData[reflection_id] = data;
    }

    const summaryDiv = document.getElementById(`summary-${reflection_id}`);
    const titleEditDiv = document.getElementById(`title-edit-${reflection_id}`);
    const data = currentReflectionData[reflection_id];
    
    // Hide summary and show title edit
    summaryDiv.style.display = 'none';
    titleEditDiv.style.display = 'block';
    
    // Create title edit interface with cancel button
    titleEditDiv.innerHTML = `
      <div class="small text-secondary mb-1">${data.date}</div>
      <label class="form-label text-light small">Edit Title:</label>
      <input type="text" id="title-input-${reflection_id}" 
             class="form-control bg-dark text-light border-warning mb-3" 
             value="${data.title}">
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-secondary" onclick="cancel_title_edit('${reflection_id}')">Cancel</button>
        <button class="btn btn-sm btn-outline-success" onclick="save_title('${reflection_id}')">OK</button>
      </div>
    `;
    
    // Focus on the input
    const titleInput = document.getElementById(`title-input-${reflection_id}`);
    titleInput.focus();
    titleInput.select();
    
  } catch (error) {
    showToast("Error editing title", "danger");
  }
};

// Cancel title edit function
const cancel_title_edit = (reflection_id) => {
  const summaryDiv = document.getElementById(`summary-${reflection_id}`);
  const titleEditDiv = document.getElementById(`title-edit-${reflection_id}`);
  
  titleEditDiv.style.display = 'none';
  summaryDiv.style.display = 'block';
  titleEditDiv.innerHTML = '';
};

// Save title function
const save_title = async (reflection_id) => {
  const titleInput = document.getElementById(`title-input-${reflection_id}`);
  const newTitle = titleInput.value.trim();
  
  if (!newTitle) {
    showToast("Title cannot be empty.", "warning");
    return;
  }
  
  try {
    const currentData = currentReflectionData[reflection_id];
    
    const response = await fetch("/reflection/update-reflection-by-id", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        "reflection": currentData.reflection,
        "title": newTitle,
        "id": parseInt(reflection_id)
      }),
      credentials: 'include'
    });

    if (response.status === 401) {
      showToast("Your session has expired. Please log in again.", "danger");
      return;
    }

    if (!response.ok) {
      showToast("Failed to save title. Please try again.", "danger");
      return;
    }
    
    // Update the stored data and UI
    currentReflectionData[reflection_id].title = newTitle;
    const summaryDiv = document.getElementById(`summary-${reflection_id}`);
    const titleEditDiv = document.getElementById(`title-edit-${reflection_id}`);
    const titleElement = summaryDiv.querySelector('h6');
    
    titleElement.textContent = newTitle;
    titleEditDiv.style.display = 'none';
    summaryDiv.style.display = 'block';
    titleEditDiv.innerHTML = '';
    
    showToast("Title updated successfully!", "success");
    
  } catch (error) {
    showToast("Connection error. Please try again.", "danger");
  }
};

// Global variable to store reflection ID for deletion
let reflectionToDelete = null;

// Modified delete function to use HTML confirmation
const delete_reflection = (reflection_id) => {
  // Store the reflection ID for deletion
  reflectionToDelete = reflection_id;
  
  // Show confirmation modal
  const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
  modal.show();
};

// Handle the actual deletion when confirmed
document.addEventListener('DOMContentLoaded', function() {
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', async function() {
      if (reflectionToDelete) {
        await performDelete(reflectionToDelete);
        reflectionToDelete = null;
        
        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        modal.hide();
      }
    });
  }
});

// Actual deletion function
const performDelete = async (reflection_id) => {
  try{
    const response = await fetch("/reflection/delete-reflection-by-id", {
      method: "DELETE",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({"id": parseInt(reflection_id)}),
      credentials: 'include'
    });

    if (response.status === 401) {
      showToast("Your session has expired. Please log in again.", "danger");
      return;
    }

    if(!response.ok){
      showToast("Failed to delete reflection. Please try again.", "danger");
      return;
    }
    
    const reflection_item = document.getElementById(`reflection-item-${reflection_id}`);
    reflection_item.remove();
    
    // Clean up stored data
    delete currentReflectionData[reflection_id];
    
    showToast("Reflection deleted successfully!", "success");
    
  }
  catch (error) {
    showToast("Connection error. Please try again.", "danger");
  }
};

const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    // Basic validation
    if (!username) {
      showToast("Please enter your username.", "warning");
      return;
    }

    if (!password) {
      showToast("Please enter your password.", "warning");
      return;
    }

    try {
      const response = await fetch("/user/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          username: username,
          password: password
        }),
        credentials: 'include' 
      });

      if (response.ok) {
        const data = await response.json();
        showToast("Login successful! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "/";
        }, 1000);
      } else if (response.status === 401) {
        showToast("Incorrect username or password. Please try again.", "danger");
      } else if (response.status === 422) {
        showToast("Invalid login details. Please check your input.", "warning");
      } else {
        showToast("Login failed. Please try again.", "danger");
      }
    } catch (error) {
      showToast("Connection error. Please check your internet and try again.", "danger");
    }
  });
}

function logout() {
  fetch('/user/logout', {
    method: 'Post',
    credentials: 'include'
  }).then(() => {
    window.location.href = '/';
  }).catch(() => {    
    window.location.href = '/';
  });
}


