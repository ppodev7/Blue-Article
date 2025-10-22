document.addEventListener("DOMContentLoaded", () => {
    fetch("/works/list")
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("works-list");
        if(container) {
            container.innerHTML = data.map(w => `
                <div class="work-card">
                    <h3>${w.titulo}</h3>
                    <p>Autor: ${w.autor}</p>
                    <p>Curso: ${w.curso} - Ano: ${w.ano}</p>
                    <p>Downloads: ${w.downloads}</p>
                    <a href="/works/download/${w.id}">Baixar PDF</a>
                </div>
            `).join("");
        }
    });
});
