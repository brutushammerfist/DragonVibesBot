<!DOCTYPE html>
<html>
<body>

<?php
    //chdir("/home/brutus/Desktop/DragonVibesBot/DragonVibesBot");

    if(isset($_GET['hub_challenge']) && !empty($_GET['hub_challenge'])){
        $res = $_GET['hub_challenge'];
        http_response_code(200);
        echo $res;
    } else {
        http_response_code(200);
    }
    
    $webhookResponse = json_decode(file_get_contents('php://input'), true);
    
    if(!empty($webhookResponse)){
        $webRes = fopen('/tmp/webRes.json', 'w');
        $test = fwrite($webRes, json_encode($webhookResponse));
        fclose($webRes);
        
        echo $test;
        
        $discordNotif = 'python3 ./discordNotif.py > /tmp/dumb.log 2> /tmp/dumb.log';
        exec($discordNotif);
    } else {
        exec('echo emtpy webhook > /tmp/dumb.log 2> /tmp/dumb.log');
    }
    
    echo "done!";
?>

</body>
</html>