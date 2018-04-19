<?php
$filename = $_POST["filename"];
$zipname = basename($_FILES["zip"]["name"]);
$project = pathinfo($zipname, PATHINFO_FILENAME);
// echo("File: $filename<br>");
// echo("Zip: $zipname<br>");
// echo("Project: $project<br>");
// echo("<br>Please wait while your files are processed...");
move_uploaded_file($_FILES["zip"]["tmp_name"],"zipfiles/$zipname");
//system("chmod 777 zipfiles/$zipname");
//echo "done 777";
system("./snappy.sh $zipname $filename");
// echo "done snapper";
$_SESSION["slide"]=0;
$_SESSION["project"]=$project;
header("Location: /");
die("We done");
?>
