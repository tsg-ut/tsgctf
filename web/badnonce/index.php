<?php
session_start();
$nonce = md5(session_id());
$_SESSION['count'] = isset($_SESSION['count']) ? $_SESSION['count'] + 1 : 0;
if ($_SESSION['count'] > 3){
    setcookie('flag2', null, -1, '/');
}
if (!isset($_GET['q'])){
    header('Location: /?q=[XSS]');
}
?>
<html>
    <head>
        <meta http-equiv="Content-Security-Policy" content="script-src 'nonce-<?= $nonce ?>';">
        <title>BADNONCE</title>
        <style>.container{width: 80%;font-size: 17px;} .bold{font-weight: bold;} .note{font-size: 10px;}</style>
    </head>
    <body>
        <h1>BADNONCE</h1>
        <div id="container" class="container">
            <div id="crawler">
                <p>You can send me an URL from <a href="/submit/">here</a>.</p>
                <p>Administrators will check your link. <a href="/part_of_crawler.js">Here is the part of the crawler administrators use.</a></p>
                <p>This session id was used <?= $_SESSION['count'] ?> times :-)</p>
            </div>
            <div id="q" class="note">
                <p class="bold">This page uses Content-Security-Policy (CSP). Therefore it's safe from XSS! :-)</p>
                <script nonce=<?= $nonce ?>>
                               console.log('Welcome to the dungeon :-)');
                </script>
            </div>
        </div>
        <!-- Here is an injection point :-) -->
        <?= $_GET['q'] ?>
        <hr>
        <div>
            <h2>src of this page</h2>
            <?php highlight_file(__FILE__); ?>
        </div>
    </body>
</html>

