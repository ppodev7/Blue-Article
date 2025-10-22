document.addEventListener("DOMContentLoaded", () => {
    fetch("/admin/stats")
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("stats");
        if(container){
            container.innerHTML = `
            <div class="stat-card">
                <h3>Total Trabalhos</h3>
                <p>${data.total_trabalhos}</p>
            </div>
            <div class="stat-card">
                <h3>Total Downloads</h3>
                <p>${data.total_downloads}</p>
            </div>
            <div class="stat-card">
                <h3>Autores Populares</h3>
                <ul>${data.autores_populares.map(a=>`<li>${a}</li>`).join('')}</ul>
            </div>`;
        }
    });
});
