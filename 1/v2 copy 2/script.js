// script.js

document.addEventListener('DOMContentLoaded', () => {
    const notificationButton = document.getElementById('notificationButton');
    const notificationDropdown = document.getElementById('notificationDropdown');

    notificationButton.addEventListener('click', (e) => {
        e.stopPropagation(); // Mencegah event bubbling
        notificationDropdown.classList.toggle('hidden');
    });

    // Klik di luar dropdown akan menutupnya
    window.addEventListener('click', (e) => {
        if (!notificationButton.contains(e.target) && !notificationDropdown.contains(e.target)) {
            notificationDropdown.classList.add('hidden');
        }
    });

    // Inisialisasi Chart.js untuk TDS
    const ctxTDS = document.getElementById('tdsChart').getContext('2d');
    const tdsChart = new Chart(ctxTDS, {
        type: 'line',
        data: {
            labels: generateLabels(10), // 10 data poin
            datasets: [{
                label: 'TDS (ppm)',
                data: generateRandomData(300, 400, 10), // Data dummy antara 300-400
                backgroundColor: 'rgba(59, 130, 246, 0.2)', // Biru muda
                borderColor: 'rgba(59, 130, 246, 1)', // Biru
                borderWidth: 1,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: 200,
                    suggestedMax: 500
                }
            }
        }
    });

    // Inisialisasi Chart.js untuk pH
    const ctxPH = document.getElementById('phChart').getContext('2d');
    const phChart = new Chart(ctxPH, {
        type: 'line',
        data: {
            labels: generateLabels(10), // 10 data poin
            datasets: [{
                label: 'pH',
                data: generateRandomData(6, 8, 10), // Data dummy antara 6-8
                backgroundColor: 'rgba(34, 197, 94, 0.2)', // Hijau muda
                borderColor: 'rgba(34, 197, 94, 1)', // Hijau
                borderWidth: 1,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: 4,
                    suggestedMax: 10
                }
            }
        }
    });

    // Fungsi untuk menghasilkan label waktu
    function generateLabels(count) {
        const labels = [];
        const now = new Date();
        for (let i = count - 1; i >= 0; i--) {
            const past = new Date(now.getTime() - i * 60000); // Mengurangi 1 menit per label
            labels.push(past.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }
        return labels;
    }

    // Fungsi untuk menghasilkan data random
    function generateRandomData(min, max, count) {
        const data = [];
        for (let i = 0; i < count; i++) {
            data.push(Math.floor(Math.random() * (max - min + 1)) + min);
        }
        return data;
    }

    // (Opsional) Update grafik secara periodik dengan data baru
    // setInterval(() => {
    //     const now = new Date();
    //     const timeLabel = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    //     // Update TDS Chart
    //     tdsChart.data.labels.push(timeLabel);
    //     tdsChart.data.labels.shift();
    //     tdsChart.data.datasets[0].data.push(Math.floor(Math.random() * (400 - 300 + 1)) + 300);
    //     tdsChart.data.datasets[0].data.shift();
    //     tdsChart.update();

    //     // Update pH Chart
    //     phChart.data.labels.push(timeLabel);
    //     phChart.data.labels.shift();
    //     phChart.data.datasets[0].data.push((Math.random() * (8 - 6) + 6).toFixed(1));
    //     phChart.data.datasets[0].data.shift();
    //     phChart.update();
    // }, 60000); // Update setiap 1 menit
});
