document.addEventListener("DOMContentLoaded", function() {
    
    // 1. LÓGICA DO GRÁFICO DE STATUS (Rosquinha / Doughnut)
    const canvasStatus = document.getElementById('graficoStatus');
    
    if (canvasStatus) {
        const completos = parseInt(canvasStatus.getAttribute('data-completos') || 0);
        const pendentes = parseInt(canvasStatus.getAttribute('data-pendentes') || 0);
        const manutencao = parseInt(canvasStatus.getAttribute('data-manutencao') || 0);
        const desaparecidos = parseInt(canvasStatus.getAttribute('data-desaparecidos') || 0);

        new Chart(canvasStatus.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Em Dia', 'Atrasados', 'Oficina Externa', 'Não Localizados'],
                datasets: [{
                    data: [completos, pendentes, manutencao, desaparecidos],
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107', '#6c757d'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    // 2. LÓGICA DO GRÁFICO DE MARCAS (Barras / Bar)
    const canvasMarcas = document.getElementById('graficoMarcas');
    
    if (canvasMarcas) {
        const nomesMarcas = JSON.parse(canvasMarcas.getAttribute('data-nomes') || '[]');
        const qtdMarcas = JSON.parse(canvasMarcas.getAttribute('data-qtds') || '[]');

        new Chart(canvasMarcas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: nomesMarcas,
                datasets: [{
                    label: 'Quantidade',
                    data: qtdMarcas,
                    backgroundColor: '#007bff',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                    y: { 
                        beginAtZero: true, 
                        ticks: { stepSize: 1 } 
                    } 
                }
            }
        });
    }

});