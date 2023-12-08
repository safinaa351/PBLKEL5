<?php
include "koneksi.php";
ini_set('date.timezone', 'Asia/Jakarta');

$now = new DateTime();
$datenow = $now->format("Y-m-d H:i:s");

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['uid'])) {
    $uid = $_POST['uid'];
    $access = '';

    // Cek UID untuk menentukan nilai kolom access
    if ($uid === '046b43b2e04b80') {
        $access = 'GRANTED';
    } else {
        $access = 'DENIED';
    }

    // Query untuk menyimpan UID, waktu, dan access ke dalam tabel log_rfid
    $query = "INSERT INTO log_rfid (no_rfid, waktu, access) VALUES ('$uid', '$datenow', '$access')";
    $result = mysqli_query($id_mysql, $query);

    if ($result) {
        echo "Data UID berhasil disimpan ke database.\n";
        echo "==================================================";
    } else {
        echo "Gagal menyimpan data UID ke database: " . mysqli_error($id_mysql);
    }
}

// Query untuk mengambil data dari tabel log_rfid
$query_select = "SELECT no_rfid, DATE_FORMAT(waktu, '%Y-%m-%d %H:%i:%s') as waktu_formatted, access FROM log_rfid";

// Eksekusi query untuk menampilkan data tabel log_rfid
$result_select = mysqli_query($id_mysql, $query_select);
?>
