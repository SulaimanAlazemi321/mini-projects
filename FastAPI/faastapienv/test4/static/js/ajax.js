// const loginFormData = document.getElementById("loginFormData");


// if (loginFormData)
// {
// async function authenticate(e) {
//     e.preventDefault();

//     const username = document.getElementById("username").value;
//     const password = document.getElementById("password").value;

//     const body = JSON.stringify({ username, password });
//     try{
//          const r = await fetch("/person/authenticateUser", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: body,
//     });
//     const data = await r.json();
//     alert(JSON.stringify(data))
    
//     }catch(error){
//         alert("error" + er)
//     }
   
//     alert(JSON.stringify(data));
// }


// loginFormData.addEventListener("submit", authenticate);

// }


const nameByID = document.getElementById("nameByIDForm")

if (nameByID)
{
    async function getName(e) {
        e.preventDefault()
    let ID = document.getElementById("ID").value

    let result = document.getElementById("nameByIdResualt")

    req = await fetch("/person/getNameByID",{
        method: "POST",
        headers: {"Content-Type": "Application/json"},
        body: JSON.stringify({ID})
    })

    data = await req.json() 
    
    if (req.status == 200)
    {
        result.textContent = data.name
    }else{
        result.textContent = "Invalid ID"
    }
    
    
 } 
    nameByID.addEventListener("submit", getName)
 
}

// alert("test")













const reverseNameForm = document.getElementById("reverseNameForm")

if (reverseNameForm){
    async function reverseName(e) {
        e.preventDefault()
        nameToReveser = document.getElementById("reverseNameInput").value
        body = JSON.stringify({"name": nameToReveser})

        const r = await fetch("/person/api/reverse",{
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body
        })
        const data = await r.json()
        output = document.getElementById("outputReverseName")
        output.textContent = `your name in reverse is ${data.reverseName}`
    }
    
    reverseNameForm.addEventListener("submit", reverseName)
}