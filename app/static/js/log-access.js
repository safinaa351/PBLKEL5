$(document).ready(function () {
    // Define variables for pagination
    var currentPage = 1;
    var itemsPerPage = 10;
    var data; // Assuming data is available globally

    // Function to update the log access table
    function updateLogAccessTable() {
        // Calculate the timestamp for 24 hours ago
        var twentyFourHoursAgo = new Date();
        twentyFourHoursAgo.setHours(twentyFourHoursAgo.getHours() - 24);

        // Send AJAX request to the server with the time filter
        $.ajax({
            url: "/admin/access_log",
            method: "GET",
            data: { startTime: twentyFourHoursAgo.toISOString() }, // Send the start time as a parameter
            success: function (responseData) {
                // Sort data by log time in descending order
                data = responseData.sort(function (a, b) {
                    return new Date(b.waktu) - new Date(a.waktu);
                });

                // Filter data for the last 24 hours
                data = data.filter(function (log) {
                    return new Date(log.waktu) >= twentyFourHoursAgo;
                });

                // Clear the existing table content
                $(".log-table-body").empty();

                // Calculate start and end indices for the current page
                var startIndex = (currentPage - 1) * itemsPerPage;
                var endIndex = startIndex + itemsPerPage;
                var maxPage = Math.ceil(data.length / itemsPerPage);

                // Loop through the data and add rows within the specified range
                for (var i = startIndex; i < endIndex && i < data.length; i++) {
                    var logTime = new Date(data[i].waktu);
                    var row = "<tr>";
                    row += "<td>" + data[i].no_rfid + "</td>";
                    row += "<td>" + data[i].waktu + "</td>";
                    row += "<td>" + data[i].access + "</td>";
                    row += "</tr>";
                    $(".log-table-body").append(row);
                }

                updatePaginationInfo(maxPage);
            }
        });
    }

    // Event listener for previous page button
    $("#prev-page").click(function () {
        if (currentPage > 1) {
            currentPage--;
            updateLogAccessTable();
        }
    });

    // Event listener for next page button
    $("#next-page").click(function () {
        var maxPage = Math.ceil(data.length / itemsPerPage);
        if (currentPage < maxPage) {
            currentPage++;
            updateLogAccessTable();
        }
    });

    // Function to update pagination information
    function updatePaginationInfo(maxPage) {
        $("#current-page").text("Page " + currentPage + " of " + maxPage);
    }

    // ... Existing code ...

    setInterval(updateLogAccessTable, 1000);
});

function openModal(imageData, fileName) {
    // Mendapatkan ID modal berdasarkan nama file
    var modalId = "myModal_" + fileName;
  
    // Menampilkan modal
    var modalElement = document.getElementById(modalId);
    if (modalElement) {
      modalElement.style.display = 'block';
  
      // Menentukan gambar yang akan ditampilkan dalam modal
      var modalImgElement = modalElement.querySelector('img');
      if (modalImgElement) {
        modalImgElement.src = "data:image/jpeg;base64," + imageData;
      }
    }
  }
  
  function closeModal(fileName) {
    // Mendapatkan ID modal berdasarkan nama file
    var modalId = "myModal_" + fileName;
  
    // Menutup modal
    var modalElement = document.getElementById(modalId);
    if (modalElement) {
      modalElement.style.display = 'none';
    }
  }