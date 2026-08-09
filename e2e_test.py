import httpx
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    password = "password123"
    
    print(f"--- STARTING E2E TEST ---")
    
    # 1. Register
    print("1. Registering user...")
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "E2E Tester",
        "github_username": "siddharth1728"
    })
    if res.status_code != 201:
        print(f"FAIL: Registration failed - {res.status_code} {res.text}")
        sys.exit(1)
        
    # 2. Login
    print("2. Logging in...")
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    if res.status_code != 200:
        print(f"FAIL: Login failed - {res.status_code} {res.text}")
        sys.exit(1)
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Add Project
    print("3. Adding project...")
    res = client.post("/projects/", headers=headers, json={
        "title": "E2E Project",
        "tech_stack": "Python, React, PostgreSQL",
        "description": "A fullstack application for E2E testing",
        "status": "completed"
    })
    if res.status_code != 201:
        print(f"FAIL: Add project failed - {res.status_code} {res.text}")
        sys.exit(1)
        
    # 4. GitHub Stats
    print("4. Fetching GitHub stats...")
    res = client.get("/github/user-stats", headers=headers)
    if res.status_code != 200:
        print(f"FAIL: GitHub fetch failed - {res.status_code} {res.text}")
        sys.exit(1)
    gh_data = res.json()
    print(f"   GitHub repos: {gh_data.get('total_repos')}, stars: {gh_data.get('total_stars')}")
    
    # 5. AI Insights
    print("5. Generating AI Insights...")
    res = client.get("/ai/resume-insights", headers=headers)
    if res.status_code != 200:
        print(f"FAIL: AI Insights failed - {res.status_code} {res.text}")
        sys.exit(1)
    ai_data = res.json()
    print(f"   AI Score: {ai_data.get('portfolio_score')}")
    print(f"   Strengths: {len(ai_data.get('strengths', []))}")
    print(f"   Missing Skills: {len(ai_data.get('missing_skills', []))}")
    
    # 6. Dashboard Stats
    print("6. Fetching Dashboard Stats...")
    res = client.get("/dashboard/stats", headers=headers)
    if res.status_code != 200:
        print(f"FAIL: Dashboard fetch failed - {res.status_code} {res.text}")
        sys.exit(1)
    dash_data = res.json()
    print(f"   Total Projects: {dash_data.get('total_projects')}")
    print(f"   Top Languages: {dash_data.get('top_languages')}")
    
    # 7. Check Profile (ME)
    print("7. Fetching Profile...")
    res = client.get("/auth/me", headers=headers)
    if res.status_code != 200:
        print(f"FAIL: Profile fetch failed - {res.status_code} {res.text}")
        sys.exit(1)
    
    # 8. Check Logout (Client side only deletes token, but let's verify we can't fetch without token)
    print("8. Verifying Auth protection...")
    res = client.get("/auth/me")
    if res.status_code != 401:
        print(f"FAIL: Auth protection failed (expected 401, got {res.status_code})")
        sys.exit(1)
        
    print("\n--- E2E TEST PASSED ---")

if __name__ == "__main__":
    run_test()
