$(document).ready(function () {
    // Define variables for pagination
    var currentPage = 1;
    var itemsPerPage = 10;
    var data; // Assuming data is available globally

    // Function to update the log access table
    function updateLogAccessTable() {
        // Send AJAX request to the server
        $.ajax({
            url: "/admin/access_log", // Replace with your actual API endpoint
            method: "GET",
            success: function (responseData) {
                data = responseData; // Update global data variable

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