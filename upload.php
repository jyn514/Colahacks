<?php
$filename = $_POST["filename"];
$zipname = basename($_FILES["zip"]["name"]);
echo $filename . " F";
echo $zipname . " Z";
move_uploaded_file($_FILES["zip"]["tmp_name"],"zipfiles/$zipname.zip");

system("python snapper.py $zipname $filename");

//header("Location: index.php?project=$zipname");
die();
