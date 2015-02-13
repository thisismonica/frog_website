<?php
//retrieve our data from POST
$username = $_POST['username'];
$password1 = $_POST['password1'];
$password2 = $_POST['password2'];
 
if($password1 != $password2)
    printf("Not the same password");
    //header('Location: ../index.html');
 
if(strlen($username) > 30)
	printf("user name too long");
    //header('Location: ../index.html');

$hash = hash('sha256', $password1);
 
function createSalt()
{
    $text = md5(uniqid(rand(), true));
    return substr($text, 0, 3);
}
 
$salt = createSalt();
$password = hash('sha256', $salt . $hash);

//Check connection
//$conn = mysql_connect('localhost', 'root', '');
$servername='localhost';
$mysql_user='root';
$mysql_password='';
$dbname='login';
$conn = new mysqli($servername, $mysql_user, $mysql_password, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 
//mysql_select_db('login', $conn);
 
//sanitize username
$username = mysql_real_escape_string($username);
 
$query = "INSERT INTO member ( username, password, salt )
        VALUES ( '$username', '$password', '$salt' );";

if ($conn->query($query) === TRUE) {
    echo "New record created successfully";
} else {
    echo "Error: " . $query . "<br>" . $conn->error;
}

$conn->close();
//mysql_query($query);

//mysql_close();
printf("mysql done!");
//header('Location: ../index.html');
?>