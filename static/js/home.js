var roomData = [
    { image: "/static/images/room1.jpg" },
    { image: "/static/images/room2.jpg" },
    { image: "/static/images/room3.jpg" }
];

var roomImage = document.getElementById("roomImage");
var roomInfo = document.getElementById("roomInfo");
var statusBox = document.querySelector(".status-box");
var statusElement = document.getElementById("status");
var index = 0;

function updateRoom() {
    // Mendapatkan status ruangan dari server
    fetch('/admin/access_log')
        .then(response => response.json())
        .then(data => {
            // Memperbarui indeks dan tampilan ruangan
            index = (index + 1) % roomData.length;
            roomImage.src = roomData[index].image;
            roomInfo.innerHTML = `<h2>Embedded Room Availability</h2>`;

            // Memperbarui status ruangan berdasarkan data dari server
            var status = data[data.length - 1].status; // Mengambil status terbaru
            statusElement.textContent = status;

            // Memperbarui kelas status-indicator berdasarkan status
            statusElement.classList.remove("status-open", "status-closed");
            statusElement.classList.add(status === "Not Available" ? "status-closed" : "status-open");
        })
        .catch(error => {
            console.error('Error fetching room status:', error);
        });
}

setInterval(updateRoom, 3000);
