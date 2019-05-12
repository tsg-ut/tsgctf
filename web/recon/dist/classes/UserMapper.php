<?php

class UserMapper
{
    protected $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    public function login($username, $password) {
        $sql = "SELECT * FROM users WHERE username=:username and password=:password";        
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam("username", $username);
        $stmt->bindParam("password", $password);
        $stmt->execute();
        return $stmt->fetch();
    }
    
    public function getUserInfo($id) {
        $sql = "SELECT * FROM users WHERE id=:id";
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam("id", $id);
        $stmt->execute();
        return $stmt->fetch();
    }

    public function createUser($username, $password, $message, $profile, $recovery_answers){
        $sql = sprintf("INSERT INTO users (id, username, password, profile, recovery_message, %s) VALUES (:id, :username, :password, :profile, :message, %s)",
                       join(',', array_map(function($i) { return "q". $i;}, range(1, 20))),
                       join(',', array_map(function($i) { return ":q". $i;}, range(1, 20))));        
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam("id", md5(getenv('APP_SALT') . $username));
        $stmt->bindParam("username", $username);
        $stmt->bindParam("password", $password);
        $stmt->bindParam("profile", $profile);
        $stmt->bindParam("message", $message);
        foreach(range(1, 20) as $i){
            $stmt->bindParam("q" . $i, $recovery_answers[$i-1]);
        }
        $stmt->execute();
        
        return $this->login($username, $password);
    }

    public function editUser($username, $password, $profile){
        $sql = "UPDATE users SET profile=:profile WHERE username=:username and password=:password";        
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam("username", $username);
        $stmt->bindParam("password", $password);
        $stmt->bindParam("profile", $profile);
        $stmt->execute();        
        return $this->login($username, $password);
    }

    public function recoveryUser($username, $recovery_answers){
        $sql = sprintf("SELECT recovery_message FROM users WHERE username=:username and %s",
                       join(' and ', array_map(function($i) {
                           return "q". $i . "= :q" . $i;
                       }, range(1, 20))));
        
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam("username", $username);
        foreach(range(1, 20) as $i){
            $stmt->bindParam("q" . $i, $recovery_answers[$i-1]);
        }
        $stmt->execute();
        return $stmt->fetch()['recovery_message'];        
    }
}
