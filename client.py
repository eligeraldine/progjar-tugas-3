import requests
import os

# Port server disesuaikan (8885 untuk Thread Pool, 8889 untuk Process Pool)
SERVER_PORT = 8889
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def list_files():
    print("\n--- Meminta daftar (list) file ---")
    try:
        response = requests.get(f"{BASE_URL}/list")
        response.raise_for_status()
        print("Status:", response.status_code)

        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print("\nResponse Body (HTML):")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def upload_file(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} tidak dapat ditemukan untuk diupload.")
        return
        
    filename = os.path.basename(filepath)
    print(f"\n--- Mengupload file: {filename} ---")
    
    headers = {'file_name': filename}
    
    with open(filepath, 'rb') as f:
        file_content = f.read()

    try:
        response = requests.post(f"{BASE_URL}/upload", headers=headers, data=file_content)
        response.raise_for_status()
        print("Status:", response.status_code)

        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print("\nResponse Body:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def delete_file(filename):
    print(f"\n--- Menghapus file: {filename} ---")
    try:
        response = requests.delete(f"{BASE_URL}/{filename}")
        response.raise_for_status()
        print("Status:", response.status_code)

        print("\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print("\nResponse Body:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_files()

    # test case (file tidak ada di server)
    # upload_file('test_failed.jpg')

    upload_file('donalbebek.jpg')

    list_files()

    # test case (file tidak ada di folder uploads)
    # delete_file('progjar_test.jpg')

    delete_file('donalbebek.jpg')
    
    list_files()
