// Add new reflection to list (with user's local time)
function addNewReflection(text, id) {
  const list = document.querySelector('.list-group-flush');
  if (!list) return;

  // Remove "no reflections" message
  const emptyMsg = list.querySelector('li:has(.text-secondary)');
  if (emptyMsg?.textContent.includes('No reflections')) emptyMsg.remove();

  // Format user's local date/time
  const userDateTime = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  // Add new item at top
  list.insertAdjacentHTML('afterbegin', `
    <li class="list-group-item bg-dark text-light border-secondary" id="reflection-item-${id}">
      <div class="small text-secondary">${userDateTime}</div>
      <p id="reflection-text-${id}" class="mb-0">${text}</p>
      <button class="btn btn-sm btn-outline-secondary me-2" onclick="editReflection(${id})">edit</button>
      <button class="btn btn-sm btn-outline-danger" onclick="deleteReflection(${id})">delete</button>
    </li>
  `);
}

// Modified form submission to send user's timestamp
// Helper function to format user's local date/time
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

// Modified form submission (much cleaner)
const form = document.getElementById("reflectionForm");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const reflection = document.getElementById("reflection").value;

    try {
      const response = await fetch("/reflection/add-reflection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          reflection: reflection,
          title: getUserDateTime()
        }),
        credentials: 'include'
      });

      if (response.status === 401) {
        window.location.href = "/login";
        return;
      }

      if (!response.ok) return;

      const data = await response.json();
      // Use the title returned from the server
      addNewReflection(data.reflection, data.id, data.title);
      form.reset();
    } catch (error) {
      console.error("Error:", error);
    }
  });
}

// Updated function to accept the actual saved title
function addNewReflection(text, id, savedTitle) {
  const list = document.querySelector('.list-group-flush');
  if (!list) return;

  // Remove "no reflections" message
  const emptyMsg = list.querySelector('li:has(.text-secondary)');
  if (emptyMsg?.textContent.includes('No reflections')) emptyMsg.remove();

  // Use the actual saved title instead of generating new one
  list.insertAdjacentHTML('afterbegin', `
    <li class="list-group-item bg-dark text-light border-secondary" id="reflection-item-${id}">
      <div class="small text-secondary">${savedTitle}</div>
      <p id="reflection-text-${id}" class="mb-0">${text}</p>
      <button class="btn btn-sm btn-outline-secondary me-2" onclick="editReflection(${id})">edit</button>
      <button class="btn btn-sm btn-outline-danger" onclick="deleteReflection(${id})">delete</button>
    </li>
  `);
}

const delete_reflection = async (reflection_id) => {

  try{
 const response = await fetch("/reflection/delete-reflection-by-id", {
          method: "DELETE",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({"id": reflection_id}),
          credentials: 'include'
        })

        if(!response.ok){
          const error = await response.json()
          console.log({"Failed": error})
          return;
        }
        
        const reflection_item = document.getElementById(`reflection-item-${reflection_id}`)
        reflection_item.remove();
      }
  catch (error) {
    console.error("Network error:", error);
  }
}

// document.getElementById("update_reflection_btn").addEventListener("click", () => {

// })

const update_reflection = async (reflection_id, reflection_reflection) => {
  try{
      const response = await fetch("/reflection/update-reflection-by-id", {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({"reflection": reflection_reflection,
                            "id": reflection_id}),
    credentials: 'include'
    })

    if (!response.ok){
      console.log("error")
      return;
    }
      const textarea = document.getElementById(`reflection-edit-${reflection_id}`)
      const changeBtn = document.getElementById(`reflection-change-${reflection_id}`)
      const newp = document.createElement("p")

      newp.id = `reflection-text-${reflection_id}`
      newp.textContent = reflection_reflection
      newp.className = "mb-0"

      if(changeBtn) changeBtn.remove();
      if(textarea) textarea.replaceWith(newp)

  }catch(error){
    console.error("network error", error)
  } 
}


const edit_reflection = (reflection_id) =>{
  const reflection_text = document.getElementById(`reflection-text-${reflection_id}`)
  const textarea = document.createElement("textarea")
  textarea.id = `reflection-edit-${reflection_id}`
  textarea.value = reflection_text.textContent
  textarea.rows = 6
  textarea.className = "form-control bg-black text-light border-secondary mb-2";

  reflection_text.replaceWith(textarea)

  const changeBtn = document.createElement("button")
  changeBtn.textContent = "Done"
  changeBtn.id = `reflection-change-${reflection_id}`
  changeBtn.className = "btn btn-sm btn-primary";
  
  changeBtn.onclick = () => update_reflection(reflection_id, textarea.value)
  textarea.insertAdjacentElement("afterend", changeBtn)
}

const loginForm = document.getElementById("loginForm");

if (loginForm)
{
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

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
      credentials: 'include' // Important: includes cookies
    });

    if (response.ok) {
      const data = await response.json();
      console.log("✅ Success:", data);
      window.location.href = "/"
    } else {
      console.log("❌ Failed:", response.status, response.statusText);
    }
  } catch (error) {
    console.error("⚠️ Error:", error);
  }
});
}


function logout() {
  fetch('/user/logout', {
    method: 'POST',
    credentials: 'include'
  }).then(() => {
    window.location.href = '/';
  }).catch(() => {
    // If logout endpoint doesn't exist, just redirect
    window.location.href = '/';
  });
}
