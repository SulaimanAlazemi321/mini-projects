loginButton = document.getElementById('loginBtn')
submitButton = document.getElementById("idBTN")

async function sendUserPassword() {
const username = document.getElementById('user').value;
  const password = document.getElementById('pwd').value;   

  const r = await fetch('/ecoUser/ecoUserLogin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await r.json();          

  if (!data.detail) 
    {                
       alert('Logged in');
    } 
    else 
    {
       alert(data.detail);      
    }
  
}
loginButton.addEventListener('click', sendUserPassword);


async function getUsers() {
  try {
    const r = await fetch("/ecoUser/getEcoUsers");
    const data = await r.json();

    let output = `
      <div class="row fw-bold border-bottom pb-2">
        <div class="col-4">Username</div>
        <div class="col-4">Password</div>
        <div class="col-4">Role</div>
      </div>
    `;

    data.forEach(user => {
      output += `
        <div class="row py-2 border-bottom">
          <div class="col-4">${user.username}</div>
          <div class="col-4 text-break">${user.password}</div>
          <div class="col-4">${user.role}</div>
        </div>
      `;
    });

    document.getElementById("out").innerHTML = output;
  } catch (error) {
    console.error("Error fetching users:", error);
    document.getElementById("out").textContent = "Error loading users.";
  }
}



addEventListener("DOMContentLoaded", getUsers)




async function addUser(event) {
   event.preventDefault()
   let username = document.getElementById("usrname").value
   let password = document.getElementById("passwd").value
   let role = document.getElementById("role").value

   const body = JSON.stringify({ username, password, role})

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