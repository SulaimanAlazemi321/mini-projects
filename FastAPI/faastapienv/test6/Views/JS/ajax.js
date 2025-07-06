const btn   = document.getElementById('loginBtn');
const userI = document.getElementById('user');
const passI = document.getElementById('pwd');

// initial state ─ check if backend sees us as logged‑in
window.addEventListener('DOMContentLoaded', () => {
  fetch('/ecoUser/me', { credentials: 'include' })
    .then(r => { if (r.ok) setLogoutUI(); });
});

btn.addEventListener('click', () => {
  if (btn.dataset.state === 'logout') {
    fetch('/ecoUser/logout', { method: 'POST', credentials: 'include' })
      .then(() => setLoginUI());
    return;
  }

  const body = new URLSearchParams({ username: userI.value, password: passI.value });
  fetch('/ecoUser/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    credentials: 'include',
    body
  })
  .then(r => r.ok ? setLogoutUI() : alert('Login failed'))
  .catch(console.error);
});

function setLogoutUI() {
  btn.textContent = 'Logout';
  btn.dataset.state = 'logout';
  userI.value = passI.value = '';
}
function setLoginUI() {
  btn.textContent = 'Login';
  btn.dataset.state = 'login';
}
