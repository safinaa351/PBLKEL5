<?php
$pengguna = "root";
$password = "";
$host = "localhost";
$database = "db_rfid";
$id_mysql = mysqli_connect ($host,$pengguna,$password,$database);
if(!$id_mysql){
    die("Database Tidak Bisa Dibuka");
}else{
    echo("");
}
?>