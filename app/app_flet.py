import flet as ft
import requests

API_BASE = "http://127.0.0.1:8000/auth"

def main(page: ft.Page):
    user_token = None
    refresh_token = None

    user_status = ft.Text("You are not logged in.", color="red", size=16)
    welcome_text = ft.Text("Please log in or register.", size=18)

    def update_status(message, success=False):
        user_status.value = message
        user_status.color = "green" if success else "red"
        page.update()

    def check_token(e):
        nonlocal user_token
        if not user_token:
            update_status("You are not logged in.", success=False)
            welcome_text.value = "Please log in or register."
            return False

        response = requests.get(
            f"{API_BASE}/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            welcome_text.value = f"Welcome, {user_data.get('username', 'User')}!"
            update_status("Token is valid.", success=True)
            return True
        else:
            refresh_user_token()
            return False

    def refresh_user_token():
        nonlocal user_token, refresh_token
        response = requests.post(f"{API_BASE}/token/refresh", json={"refresh_token": refresh_token})
        if response.status_code == 200:
            tokens = response.json()
            user_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            update_status("Token refreshed successfully!", success=True)
        else:
            user_token = None
            refresh_token = None
            update_status("Token refresh failed. Please log in again.", success=False)

    def login(e):
        nonlocal user_token, refresh_token
        response = requests.post(f"{API_BASE}/login", data={
            "username": username.value,
            "password": password.value,
        })

        if response.status_code == 200:
            tokens = response.json()
            user_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            update_status("Login successful! You are now logged in.", success=True)
            check_token()
        else:
            update_status("Login failed. Please try again.", success=False)

    def logout(e):
        nonlocal user_token, refresh_token
        user_token, refresh_token = None, None
        update_status("You are not logged in.", success=False)
        welcome_text.value = "Please log in or register."

    def register(e):
        response = requests.post(f"{API_BASE}/register", json={
            "username": username.value,
            "password": password.value,
        })

        if response.status_code == 200:
            update_status("Registration successful! You can now log in.", success=True)
        else:
            update_status("Registration failed. Username might already be taken.", success=False)

    username = ft.TextField(label="Username", width=300)
    password = ft.TextField(label="Password", password=True, width=300)

    page.add(
        ft.Column(
            [
                ft.Text("Authentication App", size=20, weight="bold"),
                username,
                password,
                ft.Row(
                    [
                        ft.ElevatedButton("Login", on_click=login),
                        ft.ElevatedButton("Register", on_click=register),
                        ft.ElevatedButton("Logout", on_click=logout),
                        ft.ElevatedButton("Check Token", on_click=check_token),
                    ],
                    spacing=10,
                ),
                user_status,
                welcome_text,
            ],
            spacing=20,
        )
    )

ft.app(target=main)
