import requests

API_URL = "http://localhost:8000"

# -------------------------- Manual library --------------------------

def upload_manual(file):
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    response = requests.post(f"{API_URL}/upload", files=files, timeout=300)
    response.raise_for_status()
    return response.json()


def get_manuals():
    response = requests.get(f"{API_URL}/manuals", timeout=30)
    response.raise_for_status()
    return response.json().get("manuals", [])


def get_view_url(manual_name: str):
    return f"{API_URL}/manuals/{manual_name}/view"


def get_download_url(manual_name: str):
    return f"{API_URL}/manuals/{manual_name}/download"


def delete_manual(manual_name: str):
    response = requests.delete(f"{API_URL}/manuals/{manual_name}", timeout=30)
    response.raise_for_status()
    return response.json()

def bulk_delete_manuals(manual_names: list):
    response = requests.post(
        f"{API_URL}/manuals/bulk-delete",
        json=manual_names,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

    # -------------------------- Alert History --------------------------

def get_alert_history():
    response = requests.get(f"{API_URL}/alerts", timeout=30)
    response.raise_for_status()
    return response.json()["alerts"]