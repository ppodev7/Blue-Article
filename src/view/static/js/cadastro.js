const formCadastro = document.getElementById("cadastroForm");
formCadastro.addEventListener("submit", e => {
    e.preventDefault();
    const nome = document.getElementById("nome").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    fetch("/auth/register", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({nome,email,senha})
    })
    .then(res => res.json())
    .then(data => alert(data.message || data.error));
});
