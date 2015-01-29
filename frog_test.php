<!DOCTYPE html>
<html lang="en">
<head>
  <title>Online Test: Frog</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Bootstrap -->
  <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
  <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>

  <!-- Code Mirror Script-->
    <link rel="stylesheet" href="codemirror/lib/codemirror.css">
    <link rel="stylesheet" href="codemirror/theme/frog.css">
    <script src="codemirror/lib/codemirror.js"></script>
    <script src="codemirror/mode/clike/clike.js"></script>

  <!-- Self-Built Script -->
  	<script src="js/main.js"></script>
    <script src="js/utils.js"></script>

  <!-- jQuery File Upload -->
    <link href="plugins/jquery-upload-file-master/css/uploadfile.min.css" rel="stylesheet">
    <!-- <link href="http://hayageek.github.io/jQuery-Upload-File/uploadfile.min.css" rel="stylesheet"> -->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="plugins/jquery-upload-file-master/js/jquery.uploadfile.min.js"></script>
    <!-- <script src="http://hayageek.github.io/jQuery-Upload-File/jquery.uploadfile.min.js"></script> -->
</head>
<body>

<!-- Navigation Bar -->
<nav class="navbar navbar-default">
  <div class="container-fluid">
    <div class="navbar-header">
      <a class="navbar-brand" href="/index.html">Frog</a>
    </div>
    <div>
      <ul class="nav navbar-nav">
        <li ><a href="/frog_test.php"> Source Code</a></li>
        <li><a href="#">Test Suites Generator</a></li>
        <li><a href="#">Fault Localization</a></li>
      </ul>
    </div>
  </div>
</nav>
<!-- End of Navigation Bar -->

<div class="page-header">
  <h2 class="text-center">Frog Bug Finder <small>Testing Panel</small></h2>
</div>

<div class="container" >

<div class="row">
  <div class="col-md-12">
  <div class="bg-warning">
			<p class="text-warning"><strong>Instructions</strong>: Upload source code; Select target function for testing; Judge test case replayed result based on program functionality.</p>
	    <div id="result-window"></div>
  </div>
  </div>
</div>
  <div id="file-uploader">Upload Source Code</div>
<hr>

<div class="container-fluid">
  <div class="row">

    <!-- Code Editor -->
    <div class="col-md-8">
      <div class="panel panel-info">
        <div class="panel-heading">Source Code Editor</div>
        <div class="panel-body">
        <form >
          <textarea id="code" name="code"></textarea>
        </form>
        </div>
      </div>
    </div> 
    <!-- End of Code Editor -->

    <!-- Function List--> 
    <div class="col-md-4">
      <div class="panel panel-info">
          <div class="panel-heading">Function List</div>
          <div class="panel-body">
          Please select desired function to test then press Generate Test.
          <table class="table", id="function_list">
            <thead>
            <tr>
              <th>Function Name</th>
              <th>Selection</th>
            </tr>
            </thead>
          </table>
          </div>
          </div>
    </div>
    <!-- End of Function List -->
  </div>
</div>

<!-- Generate Test Suite -->
<div class="container">
<button type="button" id="generateTestButton" data-loading-text="Generating..." class="btn btn-success" autocomplete="off">
  Generate Test Suite
</button>
</div>
</div>

<!-- Footer -->
<div class="container">
      <hr>
</div> <!-- /container --> 
<footer>
<p class="text-center">Copyright © 2015 UCLA Design Automation Lab</p> 
</footer>
<!-- End of Footer -->

<script>
  $('#generateTestButton').on('click', function () {
    var $btn = $(this).button('loading')
    // business logic...
    //$btn.button('reset')
  })
</script>
</div>
<!-- End of Code Editor -->

</body>
</html>
