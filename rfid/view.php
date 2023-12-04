<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tabel Database</title>
  <style>
    table {
      border-collapse: collapse;
      width: 50%;
      margin: 20px auto;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    th, td {
      border: 1px solid #dddddd;
      text-align: left;
      padding: 8px;
    }
    th:nth-child(1), td:nth-child(1) { 
      text-align: center;
    }
    th:nth-child(2), td:nth-child(2){ 
      text-align: center;
    }
    th {
      background-color: #f2f2f2;
    }
    .table-title {
      text-align: center;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <h2 class="table-title">Data RFID</h2>
  <table>
    <thead>
      <tr>
        <th>UID</th>
        <th>Waktu</th> <!-- Kolom waktu -->
      </tr>
    </thead>
    <tbody>
      <?php
      include "koneksi.php";
      include "process.php";
      if ($result_select && mysqli_num_rows($result_select) > 0) {
          while ($row = mysqli_fetch_assoc($result_select)) {
              echo "<tr>";
              echo "<td>" . $row['no_rfid'] . "</td>";
              echo "<td>" . $row['waktu_formatted'] . "</td>"; // Tampilkan waktu
              echo "</tr>";
          }
          mysqli_free_result($result_select);
      } else {
          echo "<tr><td colspan='3'>Tidak ada data ditemukan.</td></tr>";
      }
      ?>
    </tbody>
  </table>
</body>
</html>
