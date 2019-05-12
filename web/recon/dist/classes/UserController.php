<?php
use Slim\Container;
use Slim\Http\Request;
use Slim\Http\Response;

class UserController
{
    private $app;
    private $recovery_questions;

    public function __construct(Container $app) {
        $this->app = $app;
        $this->recovery_questions = [
            'grapes' => '🍇',
            'melon' => '🍈',
            'watermelon' => '🍉',
            'tangerine' => '🍊',
            'lemon' => '🍋',
            'banana' => '🍌',
            'pineapple' => '🍍',
            'pear' => '🍐',
            'peach' => '🍑',
            'cherries' => '🍒',
            'strawberry' => '🍓',
            'tomato' => '🍅',
            'coconut' => '🥥',
            'mango' => '🥭',
            'avocado' => '🥑',
            'aubergine' => '🍆',
            'potato' => '🥔',
            'carrot' => '🥕',
            'broccoli' => '🥦',
            'mushroom' => '🍄'
        ];
    }

    private function get_csrf_token($request) {    
        $csrf_token_keys = [
            'name' => $this->app->csrf->getTokenNameKey(),        
            'value' => $this->app->csrf->getTokenValueKey(),
        ];
        $csrf_token_values = [
            'name' => $request->getAttribute($csrf_token_keys['name']),
            'value' => $request->getAttribute($csrf_token_keys['value']),
        ];
        return [
            'keys' => $csrf_token_keys,
            'values' => $csrf_token_values,
        ];
    }
    
    public function index(Request $request, Response $response, array $args){
        if (isset($_SESSION['user'])){
            return $response->withRedirect('/profile', 301);            
        } else {
            $values = [
                'token' =>  $this->get_csrf_token($request),
            ];
            if(array_key_exists('notfound', $request->getQueryParams())){
                $values['error_message'] = 'Error: no user matched.';
            }            
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"), 'index.phtml', $values);            
        }
    }

    public function signIn(Request $request, Response $response, array $args){
        $data = $request->getParsedBody();
        
        $mapper = new UserMapper($this->app->db);
        $user_record = $mapper->login($data["username"], $data["password"]);

        if ($user_record) {
            $_SESSION['user'] = $user_record;
            return $response->withRedirect('/profile', 301);
        } else {
            return $response->withRedirect('/?notfound');
        }
    }

    public function signUp(Request $request, Response $response, array $args){
        $data = $request->getParsedBody();        
        $mapper = new UserMapper($this->app->db);
        $user_record = $mapper->getUserInfo($data["username"]);

        if ($user_record) {
            return $response->withRedirect('/sessions?duplicated');
        } else {
            $recovery_answers = array_map(function($i) use ($data) {
                return isset($data["q".$i]);
            }, range(1, 20));
            $user_record = $mapper->createUser($data["username"],
                                               $data["password"],
                                               $data["message"],
                                               $data["profile"],
                                               $recovery_answers);
            $_SESSION['user'] = $user_record;
            return $response->withRedirect('/profile', 301);
        }
    }

    public function signUpView(Request $request, Response $response, array $args){
        if (isset($_SESSION['user'])){
            return $response->withRedirect('/profile', 301);
        } else {
            $values = [
                'token' =>  $this->get_csrf_token($request),
                'recovery_questions' => $this->recovery_questions,
            ];
            if(array_key_exists('duplicated', $request->getQueryParams())){
                $values['error_message'] = 'Error: the username you specified has already been used.';
            }            
            
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"), 'signup.phtml', $values);
        }
    }

    public function signOut(Request $request, Response $response, array $args){
        $_SESSION = array();
        session_destroy();
        return $response->withRedirect('/', 301);
    }

    public function getMyProfile(Request $request, Response $response, array $args){
        $nonce = base64_encode(random_bytes(32));
        if (isset($_SESSION['user'])){
            // CSP is loosened for this page.
            // TODO: remove inline scripts from myprofile.phtml :-(
            $values = [
                'user' => $_SESSION['user'],
                'recovery_questions' => $this->recovery_questions,
                'recovery_answers' => array_map(function($i) {
                        return $_SESSION['user']['q'.$i];
                }, range(1, 20)),
                'token' => $this->get_csrf_token($request),
            ];
            if(array_key_exists('error', $request->getQueryParams())){
                $values['error_message'] = 'Error: the operation you did is prohibited.';
            }
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src-elem 'self'; script-src-attr 'unsafe-inline'; style-src 'self'"),
                                                'myprofile.phtml', $values);
        } else {
            return $response->withRedirect('/', 301);            
        }
    }
    
    public function getProfile(Request $request, Response $response, array $args){
        $mapper = new UserMapper($this->app->db);
        $user_record = $mapper->getUserInfo($args["id"]);
        if ($user_record){
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"),
                                                'profile.phtml',[
                                                    'user' => $user_record,
                                                ]);
        } else {
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"), '404.phtml', []);
        }
    }
    
    public function editProfile(Request $request, Response $response, array $args){
        $data = $request->getParsedBody();
        if (isset($_SESSION['user'])){
            if ($_SESSION['user']['username'] === 'admin'){
                return $response->withRedirect('/profile?error', 301);
            }
            $mapper = new UserMapper($this->app->db);
            $_SESSION['user'] = $mapper->editUser($_SESSION['user']['username'],
                                                  $_SESSION['user']['password'],
                                                  $data['profile']);
            return $response->withRedirect('/profile', 301);
        } else {
            return $response->withRedirect('/', 301);            
        }
    }

    public function startRecovery(Request $request, Response $response, array $args){
        $values = [
            'token' => $this->get_csrf_token($request),
            'recovery_questions' => $this->recovery_questions,
        ];
        if(array_key_exists('invalid', $request->getQueryParams())){
            $values['error_message'] = 'Error: no user matched.';
        }
        return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"), 'recovery.phtml', $values);
    }

    public function startReporting(Request $request, Response $response, array $args){
        $values = [
            'token' =>  $this->get_csrf_token($request),
            'site_key' => getenv('SITE_KEY')
        ];
        if (isset($_SESSION['user'])){
           $values['user'] = $_SESSION['user'];

        }
        if(array_key_exists('recaptcha-error', $request->getQueryParams())){
            $values['error_message'] = 'Error: reCAPTCHA';
        }
        if(array_key_exists('done', $request->getQueryParams())){
            $values['message'] = 'Done. Administrators will check the profile.';
        }
        return $this->app->renderer->render($response, 'report.phtml', $values);
    }

    public function completeRecovery(Request $request, Response $response, array $args){
        $data = $request->getParsedBody();
        $recovery_answers = array_map(function($i) use ($data) {
            return isset($data["q".$i]);
        }, range(1, 20));
        
        $mapper = new UserMapper($this->app->db);
        $recovery_message = $mapper->recoveryUser($data["username"], $recovery_answers);

        if ($recovery_message){        
            return $this->app->renderer->render($response->withHeader("Content-Security-Policy", "script-src 'self'; style-src 'self'"), 'reveal.phtml', [
                'message' => $recovery_message,
            ]);
        } else {
            return $response->withRedirect('/recover?invalid', 301);                        
        }
    }
}
