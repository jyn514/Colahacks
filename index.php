<!DOCTYPE html>
<!--
Author:    Brennan Cain
Email:     brennan@brennancain.com
-->
<html>
<head>
  <?php
  if (session_status() == PHP_SESSION_NONE) {
    session_start();
  }

  if(isset($_POST["project"]))
  {
    $_SESSION["project"] = $_POST["project"];
  }
  if(isset($_POST["slide"]))
  {
    $_SESSION["slide"] = $_POST["slide"];
  }
  if(isset($_GET["project"]))
  {
    $_SESSION["project"] = $_GET["project"];
  }
  if(isset($_GET["slide"]))
  {
    $_SESSION["slide"] = $_GET["slide"];
  }
  ?>
  <meta charset="UTF-8">
  <!-- Description -->

  <!-- Latest compiled and minified CSS -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

  <!-- Optional theme -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

  <link rel="stylesheet" href="main.css">
  <link rel="stylesheet" href="highlights.css">

  <!-- Latest compiled and minified JavaScript -->
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

</head>
<body onLoad="loaded()">
    <div class="col-md-2 listpanel" style="top: 0; bottom:0; overflow-y: scroll;">
      <a href="/"><h1>Snapper</h1></a>

      <!-- OPEN PROJECT SECTION -->
      <form action="index.php" method="post">
        <table>
          <tr>
            <td><textarea name="project" required><?php if(isset($_SESSION["project"])) {echo($_SESSION["project"]);}?></textarea></td>
            <td><input value="open" type='submit'></td>
          </tr>
        </table>
      </form>
      <hr>

      <!-- LIST SLIDES AND CREATE FORWARD/BACKWARD Buttons-->
      <?php
      if(isset($_SESSION["project"])) {
        $dir = "snaps/" . $_SESSION["project"];
        if (is_dir($dir)){
          if ($dh = opendir($dir)){
            $files = array();
            while (($file = readdir($dh)) !== false){
              if($file[0]!==".")
              {
                array_push($files,$file);
              }
            }
            sort($files);
            closedir($dh);
            $currentIndex=0;
            if(isset($_SESSION["slide"])) {
              $currentIndex=array_search($_SESSION["slide"],$files);//gets index of slide
            }
            echo("<div class='col-md-6'>");
            if($currentIndex>0){
              $prev = $files[$currentIndex-1];
              echo("<a href='index.php?slide=$prev'><span class='glyphicon glyphicon-align-left' aria-hidden='true'></span>");
            }
            echo("</div>");
            echo("<div class='col-md-6'>");
            if($currentIndex<count($files)-1)
            {
              $next = $files[$currentIndex+1];
              echo("<a href='index.php?slide=$next'><span class='glyphicon glyphicon-align-right' aria-hidden='true'></span></a>");
            }
            echo("</div><br>");

            echo("<ul>\n");
            for($i=0; $i<count($files);$i++) {// CREATE LIST OF SLIDES HERE
              $file=$files[$i];
              if($file==$_SESSION["slide"]) {
                echo("<li><a href='index.php?slide=$file'><strong>$file</strong></a></li>\n");
              }
              else {
                echo("<li><a href='index.php?slide=$file'>$file</a></li>\n");
              }
            }
            echo("</ul><br>");
          }
          else("Could not open directory");
        }
        else {
          echo("Directory not found<br>");
        }
      }
      ?>
      <hr>
      <br>
      <!-- ZIP UPLOAD SECTION -->
      <form action="upload.php" method="post" enctype="multipart/form-data">
        <table>
          <tr>
            <td>Zip file:</td>
            <td><input type="file" name="zip"/></td>
          </tr>
          <tr>
            <td>Trackable file:</td>
            <td><input type="text" name="filename"/></td>
          </tr>
          <tr>
            <td>&nbsp;</td>
            <td><input value="open" type='submit'></td>
          </tr>
        </table>
      </form>

    </div>
    <div class="col-md-5 codepanel" style="top: 0; bottom:0; overflow-y: scroll;">
      <h2>Code</h2>
      <hr>
      <div id="codepanel">
        <ol>
      <?php
      if(isset($_SESSION["project"]) and isset($_SESSION["slide"])) {
        include("snaps/" . $_SESSION["project"] . "/" . $_SESSION["slide"]."/code.html");
      }
      ?>
    </ol>
  </div>
    </div>
    <div class="col-md-5 outputpanel" style="top: 0; bottom:0; overflow-y: scroll;">
      <h2>Output</h2>
      <hr>
      <?php
      if(isset($_SESSION["project"]) and isset($_SESSION["slide"])) {
        include("snaps/" . $_SESSION["project"] . "/" . $_SESSION["slide"]."/output.html");
      }
      ?>
    </div>

</body>
</html>
