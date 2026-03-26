# Laporan Penugasan Modul 1 Open Recruitment NETICS 2026

| Nama           | NRP        |
| ---            | ---        |
| Hazza Danta Hermandanu               | 5025241117           |

## Deskripsi Tugas
1. Membuat API publik dengan endpoint `/health` yang menampilkan informasi:
    ```python
    {
      "nama": "(nama lengkap)",
      "nrp": "(nrp)",
      "status": "UP",
      "timestamp": time	//Current time
      "uptime": time	//Server uptime
    }
    ```
2. Lakukan deployment API dalam container VPS publik.
3. Gunakan ansible untuk menginstall dan meletakkan konfigurasi nginx pada VPS, nginx berperan sebagai reverse proxy dan diakses dengan menjalankan ansible (bukan konfigurasi manual).
4. Lakukan proses CI/CD menggunakan github actions untuk melakukan otomasi proses deployment.
5. Dokumentasikan pekerjaan dalam laporan berbentuk markdown.

## Environtment yang digunakan
- VPS: Micrososft Azure
- Bahasa: Python
- Otomasi: Ansible
- Container: Docker
- CI/CD: Github Action
- Nginx (Reverse Proxy), di konfigurasi di `playbook.yaml`

## Penjelasan
1. modul1.py
    - Import Library
    ```python
    from flask import Flask
    import json
    import time
    from datetime import datetime, timezone, timedelta
    ```
    <br>

    - Membuat instance
    ```python
    app = Flask(__name__)
    ```
    <br>

    - Simpan `start_time` dalam format Unix
    ```python
    start_time = time.time()
    ```
    <br>

    - Buat objek timezone UTC+7 (WIB)
    ```python
    wib = timezone(timedelta(hours=7))
    ```
    <br>
    
    - Buta rute `/health` dengan metode `GET`
    ```python
    @app.route('/health', methods=['GET'])
    ```
    <br>

    - Handler page `/health`
    ```python
    def health_page():
        uptime_seconds = int(time.time() - start_time) #selisih current time dan start time
        h, remain = divmod(uptime_seconds, 3600) //jam dan sisanya dalam detik
        m, s = divmod(remain, 60) //menit dan sisanya dalam detik
    
        data_set = {
            'nama': 'Hazza Danta Hermandanu',
            'nrp': '5025241117',
            'status': 'UP',
            'timestamp': datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': f"{h:02d}:{m:02d}:{s:02d}"
        }
        return app.response_class(
            response=json.dumps(data_set),
        )
    ```
    <br>

    - Jalankan
    ```python
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=6767)
    ```
    <br>

2. inventory.ini
   File `inventory.ini` berisi target server (vps) yang akan dikelola oleh ansible.  
    ```ini
    [vps_azure]
    52.175.122.105 ansible_user=azureuser ansible_ssh_private_key_file=~/vps-api-danu_key.pem ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ```
    <br>

3. Dockerfile
   Berisi perintah untuk membuat docker image.
   - Gunakan image python 3.9
    ```dockerfile
    FROM python:3.9-slim
    ```
    - Tetapkan work direktori
    ```dockerfile
    WORKDIR /modul1
    ```
    - Salin semua folder ke work direktori
    ```dockerfile
    COPY . /modul1
    ```
    - Install `flask`
    ```dockerfile
    RUN pip install flask
    ```
    - Beritahu docker bahwa container menggunakan port 6767
    ```dockerfile
    EXPOSE 6767
    ```
    - Jalankan saat container dinyalakan
    ```dockerfile
    CMD ["python", "modul1.py"]
    ```

