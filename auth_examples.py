from schemas.auth import LoginRequest

alice_login_example = {
    "summary": "Alice (ABC Corporation)",
    "description": "Login as Alice from ABC Corporation",
    "value": {
        "username": "alice",
        "password": "alicepass"
    }
}

dave_login_example = {
    "summary": "Dave (DEF Corporation)",
    "description": "Login as Dave from DEF Corporation",
    "value": {
        "username": "dave",
        "password": "davepass"
    }
}

login_examples = {
    "alice": alice_login_example,
    "dave": dave_login_example
}