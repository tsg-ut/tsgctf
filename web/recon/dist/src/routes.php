<?php

use Slim\Http\Request;
use Slim\Http\Response;

$app->get('/', UserController::class . ':index');

// sessions (sign in/out)
$app->post('/signin', UserController::class . ':signIn');
$app->get('/signup', UserController::class . ':signUpView');
$app->post('/signup', UserController::class . ':signUp');
$app->delete('/signout', UserController::class . ':signOut');

// user profiles
$app->get('/profile', UserController::class . ':getMyProfile');
$app->get('/profile/{id}', UserController::class . ':getProfile');
$app->post('/profile', UserController::class . ':editProfile');
                   
// recovery password
$app->get('/recover', UserController::class . ':startRecovery');
$app->post('/recover', UserController::class . ':completeRecovery');

$app->get('/report', UserController::class . ':startReporting');
