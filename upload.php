<?php
$filename = $_POST["filename"];
$zipname = $_FILES["zip"]["name"];
move_uploaded_files($_FILES["zip"]["tmp_name"],"zipfiles/$zipname");

system("python snapper.py $zipname $filename");

header("Location: index.php?project=$zipname");
?>
