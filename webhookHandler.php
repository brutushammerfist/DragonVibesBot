<!DOCTYPE html>
<html>
<body>

<?php
    if(isset($_GET['hub_challenge']) && !empty($_GET['hub_challenge'])){
        $res = $_GET['hub_challenge'];
        http_response_code(200);
        echo $res;
    } else {
        http_response_code(200);
    }
    
    $webhookResponse = json_decode(file_get_contents('php://input'), true);
    
    if(!empty($webhookResponse)){
        $webRes = fopen('webRes.json', 'w');
        fwrite($webRes, json_encode($webhookResponse));
        fclose($webRes);
        
        $discordNotif = escapeshellcmd('python3 ./discordNotif.py > /tmp/dumb.log 2> /tmp/dumb.log');
        exec($discordNotif);
    }
?>

</body>
</html>