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

  <!-- Latest compiled and minified JavaScript -->
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
</head>
<body>
  <div class="row" style="height:100%; width: 100%">
    <div class="col-md-2" style="top: 0; bottom:0; overflow-y: scroll;">
      <h1>Snapper</h1>
      <form action="index.php" method="post">
        <table>
          <tr>
            <td><textarea name="project" required><?php if(isset($_SESSION["project"])) {echo($_SESSION["project"]);}?></textarea></td>
            <td><input value="open" type='submit'></td>
          </tr>
        </table>
      </form>
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

            /*
            $currentIndex=array_search($_SESSION["slide"]);//gets index of slide
            echo("<div class='col-md-6'>");
            if($currentIndex>0 and !$currentIndex){
              echo "<span class="glyphicon glyphicon-align-left" aria-hidden="true"></span>"
            }
            */

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

    </div>
    <div class="col-md-5" style="top: 0; bottom:0; overflow-y: scroll;">
      <h2>Code</h2>
      <hr>
      <?php
      if(isset($_SESSION["project"]) and isset($_SESSION["slide"])) {
        include("snaps/" . $_SESSION["project"] . "/" . $_SESSION["slide"]."/code.html");
      }
      ?>
    </div>
    <div class="col-md-5" style="top: 0; bottom:0; overflow-y: scroll;">
      <h2>Output</h2>
      <hr>
      <?php
      if(isset($_SESSION["project"]) and isset($_SESSION["slide"])) {
        include("snaps/" . $_SESSION["project"] . "/" . $_SESSION["slide"]."/output.html");
      }
      ?>
    </div>
  </div>

</body>
</html>
