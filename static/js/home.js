var roomData = [
    {image: "/static/images/room1.jpg"},
    {image: "/static/images/room2.jpg"},
    {image: "/static/images/room3.jpg"}
];

var roomImage = document.getElementById("roomImage");
var roomInfo = document.getElementById("roomInfo");
var statusBox = document.querySelector(".status-box");
var statusElement = document.getElementById("status");
var index = 0;

var status = "Available";

function updateRoom() {
    index = (index + 1) % roomData.length;
    roomImage.src = roomData[index].image;
    roomInfo.innerHTML = `<h2>Status Ruangan Embeded</h2>`;
    statusBox.className = status === "Not Available" ? "status-box status-open" : "status-box status-closed";
    statusElement.textContent = status;
}

setInterval(updateRoom, 3000);