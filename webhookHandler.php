<!DOCTYPE html>
<html>
<body>

<?php
    if(isset($_GET['hub_challenge']) && !empty($_GET['hub_challenge'])){
        $res = $_GET['hub_challenge'];
        echo $res;
    } else {
        http_response_code(200);
    }
    
    $webhookResponse = json_decode(file_get_contents('php://input'), true);
    
    if(!empty($webhookResponse)){
        $webRes = fopen('webRes.json', 'w');
        fwrite($webRes, json_encode($webhookResponse));
        fclose($webRes);
        
        $discordNotif = escapeshellcmd('python3 ./discordNotif.py');
        exec($discordNotif);
    }
?>

</body>
</html>