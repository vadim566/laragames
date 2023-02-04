<?php

$url = 'https://regulus.unige.ch/litedevtools/server/token';

$post = array (
    'grant_type' => 'password',
    'username' => 'lara',
    'password' => 'p0rt@l!'
);
$query = http_build_query($post);

$header = array(
    "Content-Type: application/x-www-form-urlencoded",
    "Content-Length: ".strlen($query),
    "User-Agent:MyAgent/1.0");


$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
curl_setopt($ch, CURLOPT_TIMEOUT, 100);
curl_setopt($ch, CURLOPT_POSTFIELDS, $query);

$result = curl_exec($ch);
print_r($result);
if ($result === FALSE) {
    echo "Error sending". curl_error($ch);
    curl_close ($ch);
}else{
    echo "Success" . curl_error($ch);
    curl_close ($ch);
}
echo "<br/>" . "**************" . "<br/>";


    $url = 'https://regulus.unige.ch/litedevtools/server/token';
    $data = array('grant_type' => 'password', 'username' => 'lara', 'password' => 'p0rt@l!');
    $query = http_build_query($data);   
    $options = array(
        'http' => array(
            'header' => "Content-Type: application/x-www-form-urlencoded\r\n".
                "Content-Length: ".strlen($query)."\r\n".
                "User-Agent:MyAgent/1.0\r\n",
            'method'  => "POST",
            'content' => $query,
        ),
    );
    $context = stream_context_create($options);
    $cURLResult = file_get_contents($url, false, $context);
    print_r($cURLResult);
    if ($cURLResult === FALSE)
    {
        $result = "failed";
        echo $result;
    }
    else
    {
        //$result = CreateResponse($cURLResult);
        echo "success";
    }
?>
