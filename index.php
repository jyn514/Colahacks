<!DOCTYPE html>
<!--
Author:    Brennan Cain
Email:     brennan@brennancain.com
-->
<html>
    <head>
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
			<form action="contact.php" method="post">
				<table>
					<tr>
						<td><textarea name="comment" required><?php if(isset($_SESSION["project"]) echo($_SESSION["project"]);?></textarea></td>
						<td><input value="open" type='submit'></td>
					</tr>
				</table>
		    </form>
<?
if(isset($_SESSION["project"]) {
  dir = "snaps/" . $_SESSION["project"];
	if (is_dir($dir)){
    if ($dh = opendir($dir)){
      $files = array();
	    while (($file = readdir($dh)) !== false){
	      array_push(files,$file)
	    }
	    closedir($dh);

      // CREATE HTML HERE
      echo("<ul>\n");
      foreach($files as $file) {
        if($file==$_SESSION["slide"]) {
          echo("<li>$file</li>\n");
        }
        else {
          echo("<li><strong>$file</strong></li>\n");
        }
      }
      echo("<ul>\n");
	  }
    else("Could not open directory");
	}
  else {
    echo("directory not found<br>");
  }
}
?>

		</div>
        </div>

    </body>
</html>

+
