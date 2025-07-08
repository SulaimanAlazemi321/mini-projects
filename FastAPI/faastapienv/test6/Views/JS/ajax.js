loginButton = document.getElementById('loginBtn')
submitButton = document.getElementById("idBTN")

async function sendUserPassword() {
  const username = document.getElementById('user').value;
  const password = document.getElementById('pwd').value;   

  try {
    const r = await fetch('/ecoUser/ecoUserLogin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "username": username, "password": password })
    });

    const data = await r.json();          

    if (r.ok) {
      // Success (status 200)
      alert('Logged in successfully!');
    } else {
      // Error (status 4xx, 5xx)
      if (typeof data.detail === 'string') {
        // Simple error message
        alert(data.detail);
      } else if (Array.isArray(data.detail)) {
        // Validation errors
        const errorMessages = data.detail.map(err => err.msg).join('\n');
        alert('Validation errors:\n' + errorMessages);
      } else {
        alert('Login failed. Please try again.');
      }
    }
  } catch (error) {
    console.error('Login error:', error);
    alert('Network error. Please try again.');
  }
}

loginButton.addEventListener('click', sendUserPassword);


// async function getUsers() {
//   try {
//     const r = await fetch("/ecoUser/getEcoUsers");
//     const data = await r.json();

//     let output = `
//       <div class="row fw-bold border-bottom pb-2">
//         <div class="col-4">Username</div>
//         <div class="col-4">Password</div>
//         <div class="col-4">Role</div>
//       </div>
//     `;

//     data.forEach(user => {
//       output += `
//         <div class="row py-2 border-bottom">
//           <div class="col-4">${user.username}</div>
//           <div class="col-4 text-break">${user.password}</div>
//           <div class="col-4">${user.role}</div>
//         </div>
//       `;
//     });

//     document.getElementById("out").innerHTML = output;
//   } catch (error) {
//     console.error("Error fetching users:", error);
//     document.getElementById("out").textContent = "Error loading users.";
//   }
// }



// addEventListener("DOMContentLoaded", getUsers)




async function addUser(event) {
   event.preventDefault()
   let username = document.getElementById("usrname").value
   let password = document.getElementById("passwd").value
   let userType = parseInt(document.getElementById("userType").value)  // CHANGED: role -> userType (convert to int)

   const body = JSON.stringify({ username, password, userType})  // CHANGED: role -> userType

   const r = await fetch("/ecoUser/addEcoUser",{
      method: 'POST',
      headers: {"Content-Type": "application/json"},
      body 
   })

   if (r.status == 201)
   {
      alert("user is created")
   }else
   {
      alert("user is not created")
   }  
}

document.getElementById("userForm").addEventListener("submit", addUser)


async function liveSearch () {
  const q = document.getElementById("search").value;

  const r   = await fetch("/ecoUser/liveSearch", {
    method : "POST",
    headers: {"Content-Type": "application/json"},
    body   : JSON.stringify({query: q})
  });
  const data = await r.json();

  const box = document.getElementById("searchResults");
  let html  = "";

  if (data.length) {         
    html += `
      <div class="row fw-bold border-bottom pb-2">
        <div class="col-4">Username</div>
        <div class="col-4">User Type</div>
      </div>`;
    data.forEach(u => {
      html += `
        <div class="row py-2 border-bottom">
          <div class="col-4">${u.username}</div>
          <div class="col-4">${u.userType}</div>
        </div>`;  // CHANGED: role -> userType
    });
    box.classList.remove("d-none");   
  } else {
    box.classList.add("d-none");      
  }
  box.innerHTML = html;              
}
document.getElementById("search").addEventListener("input", liveSearch);


document.addEventListener("click", e => {
  const input = document.getElementById("search");
  const box   = document.getElementById("searchResults");

  if (!input.contains(e.target) && !box.contains(e.target)) {
    box.innerHTML = "";      
    box.classList.add("d-none"); 
  }
});
