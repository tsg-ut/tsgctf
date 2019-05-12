<?php
return [
    'settings' => [
        'cookies.httponly' => true,
        'displayErrorDetails' => false, // set to false in production
        'addContentLengthHeader' => false, // Allow the web server to send the content-length header
        
        // Database settings
        'db' => [
            'host' => $_ENV['DB_HOST'],
            'port' => $_ENV['DB_PORT'],
            'user' => $_ENV['DB_USERNAME'],
            'pass' => $_ENV['DB_PASSWORD'],
            'dbname' => $_ENV['DB_DATABASE'],            
        ],

        // Renderer settings
        'renderer' => [
            'template_path' => __DIR__ . '/../templates/',
            'cache_path' => __DIR__ . '/../caches/',
        ],

        // Monolog settings
        'logger' => [
            'name' => $_ENV['APP_HOST'],
            'path' => isset($_ENV['docker']) ? 'php://stdout' : __DIR__ . '/../storage/logs/slim/app.log',
            'level' => \Monolog\Logger::DEBUG,
        ],
    ],
];
