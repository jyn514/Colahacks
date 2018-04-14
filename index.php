<!DOCTYPE html>
<!--
Author:    Brennan Cain
Email:     brennan@brennancain.com
-->
<html>
<head>
  <?php
  if(isset($_POST["project"]))
  {
    $_SESSION["project"] = $_POST["project"];
  }
  if(isset($_POST["slide"]))
  {
    $_SESSION["slide"] = $_POST["slide"];
  }
  ?>
  <meta charset="UTF-8">
  <!-- Description -->

  <!-- Latest compiled and minified CSS -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

  <!-- Optional theme -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

  <link rel="stylesheet" href="main.css">
  <!-- Latest compiled and minified JavaScript -->
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

</head>
<body onLoad="loaded()">
    <div class="col-md-2 listpanel" style="top: 0; bottom:0; overflow-y: scroll;">
      <h1>Snapper</h1>

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
              array_push($files,$file);
            }
            closedir($dh);


            $currentIndex=array_search($_SESSION["slide"]);//gets index of slide
            echo("<div class='col-md-6'>");
            if($currentIndex>0 and $currentIndex){
              echo("<a href='" . $files[$currentIndex-1] ."'><span class='glyphicon glyphicon-align-left' aria-hidden='true'></span>");
            }
            echo("</div>");
            echo("<div class='col-md-6'>");
            if($currentIndex<count($files))
            {
              echo("<a href='" . files[$currentIndex+1] ."'<span class='glyphicon glyphicon-align-right' aria-hidden='true'></span>");
            }
            echo("</div>");


            echo("<ul>\n");
            for($i=0; $i<count($files);$i++) {// CREATE LIST OF SLIDES HERE
              $file=$files[$i];
              if($file==$_SESSION["slide"]) {
                echo("<li><strong>$file</strong></li>\n");
              }
              else {
                echo("<li>$file</li>\n");
              }
            }
            echo("<ul>\n");
          }
          else("Could not open directory");
        }
        else {
          echo("Directory not found<br>");
        }
      }
      ?>
      <hr>

      <!-- ZIP UPLOAD SECTION -->
      <form action="upload.php" method="post">
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
      for($i =0; $i<100;$i++)
      {
        echo("<li>".$i."</li>");
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
