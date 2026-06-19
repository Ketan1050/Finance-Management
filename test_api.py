import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

def test_endpoint(method, path, data=None, token=None):
    url = f"{base_url}{path}"
    headers = {}
    if data:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print(f"[{method}] {path} -> {response.status}")
            try:
                return json.loads(res_body)
            except:
                return res_body
    except urllib.error.HTTPError as e:
        print(f"[{method}] {path} -> {e.code} Error: {e.read().decode('utf-8')}")
        return None

def run_tests():
    print("Testing GET / (Frontend)")
    test_endpoint("GET", "/")
    
    print("\nTesting POST /signup")
    import random
    user_email = f"testuser{random.randint(1, 10000)}@example.com"
    res = test_endpoint("POST", "/signup", {"username": "testuser", "email": user_email, "password": "password123"})
    
    print("\nTesting GET /users")
    test_endpoint("GET", "/users")
    
    print("\nTesting POST /login")
    # Note: /login uses OAuth2PasswordRequestForm which requires x-www-form-urlencoded
    url = f"{base_url}/login"
    data = urllib.parse.urlencode({"username": user_email, "password": "password123"}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print(f"[POST] /login -> {response.status}")
            token_data = json.loads(res_body)
            access_token = token_data["access_token"]
    except urllib.error.HTTPError as e:
        print(f"[POST] /login -> {e.code} Error: {e.read().decode('utf-8')}")
        return
        
    print("\nTesting POST /expenses")
    exp_res = test_endpoint("POST", "/expenses", {"title": "Lunch", "amount": 15.5, "category": "Food"}, token=access_token)
    expense_id = exp_res.get("id") if exp_res else None
    
    print("\nTesting GET /expenses")
    test_endpoint("GET", "/expenses", token=access_token)
    
    print("\nTesting GET /expenses/summary")
    test_endpoint("GET", "/expenses/summary", token=access_token)
    
    if expense_id:
        print(f"\nTesting PUT /expenses/{expense_id}")
        test_endpoint("PUT", f"/expenses/{expense_id}", {"amount": 20.0}, token=access_token)
        
        print(f"\nTesting DELETE /expenses/{expense_id}")
        test_endpoint("DELETE", f"/expenses/{expense_id}", token=access_token)
        
if __name__ == '__main__':
    run_tests()
