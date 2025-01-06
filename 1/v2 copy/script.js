// script.js

document.addEventListener('DOMContentLoaded', () => {
    const notificationButton = document.getElementById('notificationButton');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    // Dropdown Notifikasi
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

    // Navigasi antar section
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = e.currentTarget.getAttribute('data-section');

            // Sembunyikan semua section
            sections.forEach(section => {
                if (section.id === targetSection) {
                    section.classList.remove('hidden');
                } else {
                    section.classList.add('hidden');
                }
            });

            // Update judul header
            const headerTitle = document.querySelector('header h2');
            headerTitle.textContent = capitalizeFirstLetter(targetSection.replace('-', ' '));
        });
    });

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

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

    // -------- Manajemen Mesin Vending --------

    const addMachineButton = document.getElementById('addMachineButton');
    const machineModal = document.getElementById('machineModal');
    const cancelButton = document.getElementById('cancelButton');
    const machineForm = document.getElementById('machineForm');
    const modalTitle = document.getElementById('modalTitle');
    const machineTableBody = document.getElementById('machineTableBody');

    let editMode = false;
    let editRow = null;

    // Event Listener untuk Tombol Tambah Mesin
    addMachineButton.addEventListener('click', () => {
        openModal('Tambah Mesin Vending');
    });

    // Event Listener untuk Tombol Batal di Modal
    cancelButton.addEventListener('click', () => {
        closeModal();
    });

    // Event Listener untuk Formulir Modal
    machineForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('machineName').value.trim();
        const location = document.getElementById('machineLocation').value.trim();
        const status = document.getElementById('machineStatus').value;

        if (editMode && editRow) {
            // Edit mesin vending
            editRow.querySelector('.machineName').textContent = name;
            editRow.querySelector('.machineLocation').textContent = location;
            editRow.querySelector('.machineStatus').innerHTML = getStatusBadge(status);
            closeModal();
            editMode = false;
            editRow = null;
        } else {
            // Tambah mesin vending baru
            const newRow = document.createElement('tr');

            const idCell = document.createElement('td');
            idCell.classList.add('py-2', 'px-4', 'border-b', 'text-center');
            idCell.textContent = getNextMachineID();

            const nameCell = document.createElement('td');
            nameCell.classList.add('py-2', 'px-4', 'border-b', 'machineName');
            nameCell.textContent = name;

            const locationCell = document.createElement('td');
            locationCell.classList.add('py-2', 'px-4', 'border-b', 'machineLocation');
            locationCell.textContent = location;

            const statusCell = document.createElement('td');
            statusCell.classList.add('py-2', 'px-4', 'border-b', 'text-center', 'machineStatus');
            statusCell.innerHTML = getStatusBadge(status);

            const actionsCell = document.createElement('td');
            actionsCell.classList.add('py-2', 'px-4', 'border-b', 'text-center');

            const editButton = document.createElement('button');
            editButton.classList.add('editButton', 'bg-yellow-500', 'text-white', 'px-2', 'py-1', 'rounded', 'hover:bg-yellow-600', 'mr-2');
            editButton.textContent = 'Edit';
            editButton.addEventListener('click', () => {
                openModal('Edit Mesin Vending');
                populateModal(name, location, status);
                editMode = true;
                editRow = newRow;
            });

            const deleteButton = document.createElement('button');
            deleteButton.classList.add('deleteButton', 'bg-red-500', 'text-white', 'px-2', 'py-1', 'rounded', 'hover:bg-red-600');
            deleteButton.textContent = 'Hapus';
            deleteButton.addEventListener('click', () => {
                if (confirm('Apakah Anda yakin ingin menghapus mesin vending ini?')) {
                    machineTableBody.removeChild(newRow);
                }
            });

            actionsCell.appendChild(editButton);
            actionsCell.appendChild(deleteButton);

            newRow.appendChild(idCell);
            newRow.appendChild(nameCell);
            newRow.appendChild(locationCell);
            newRow.appendChild(statusCell);
            newRow.appendChild(actionsCell);

            machineTableBody.appendChild(newRow);

            closeModal();
        }

        machineForm.reset();
    });

    // Fungsi untuk Membuka Modal
    function openModal(title) {
        modalTitle.textContent = title;
        machineModal.classList.remove('hidden');
    }

    // Fungsi untuk Menutup Modal
    function closeModal() {
        machineModal.classList.add('hidden');
        machineForm.reset();
        editMode = false;
        editRow = null;
    }

    // Fungsi untuk Mendapatkan Badge Status
    function getStatusBadge(status) {
        let colorClass = '';
        if (status === 'Aktif') {
            colorClass = 'bg-green-200 text-green-800';
        } else if (status === 'Non-Aktif') {
            colorClass = 'bg-gray-200 text-gray-800';
        } else if (status === 'Maintenance') {
            colorClass = 'bg-yellow-200 text-yellow-800';
        }
        return `<span class="${colorClass} px-2 py-1 rounded">${status}</span>`;
    }

    // Fungsi untuk Mengisi Formulir Modal saat Edit
    function populateModal(name, location, status) {
        document.getElementById('machineName').value = name;
        document.getElementById('machineLocation').value = location;
        document.getElementById('machineStatus').value = status;
    }

    // Fungsi untuk Mendapatkan ID Mesin Vending Berikutnya
    function getNextMachineID() {
        const rows = machineTableBody.querySelectorAll('tr');
        return rows.length + 1;
    }
});
