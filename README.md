# Laporan Penugasan Modul 1 Open Recruitment NETICS 2026

| Nama           | NRP        |
| ---            | ---        |
| Hazza Danta Hermandanu               | 5025241117           |

## URL API
`http://52.175.122.105/health`

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

## Langkah - Langkah
1. Buat direktori project dan masuk ke dalamnya
   ```bash
   mkdir -p deployment
   cd deployment
   ```
2. Buat file `modul1.py` sebagai API untuk menamplkan informasi
   ```bash
   nano modul1.py
   ```
   ```python
    from flask import Flask
    import json
    import time
    from datetime import datetime, timezone, timedelta
    
    app = Flask(__name__)
    start_time = time.time()
    wib = timezone(timedelta(hours=7))
    
    @app.route('/health', methods=['GET'])
    def health_page():
        uptime_seconds = int(time.time() - start_time)
        h, remain = divmod(uptime_seconds, 3600)
        m, s = divmod(remain, 60)
    
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
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=6767)
   ```
3. Buat VPS menggunakan Azure
    - Create Virtual Machine
    - Konfigurasi Virtual Machine
        <img width="998" height="648" alt="image" src="https://github.com/user-attachments/assets/b843a00d-eb48-4b0e-9a0f-03de124bc7a9" /><br>
        <img width="1023" height="660" alt="image" src="https://github.com/user-attachments/assets/1f9736d8-6dd2-46d9-bb1e-be550c9d7b6a" /><br>
        <img width="1049" height="580" alt="image" src="https://github.com/user-attachments/assets/4ec63cd3-26f7-4e89-88de-210c502bc615" /><br>
    - Review dan Create Virtual Machine
    - Download key SSH dalam bentuk file `*.pem` yang telah digenerate, simpan file `*.pem` di dalam 1 direktori project
    - Setelah selesai, maka akan mendapatkan ip untuk VPS publik
        <img width="749" height="315" alt="image" src="https://github.com/user-attachments/assets/14cbf62f-7cec-4a47-8be6-ca6091211408" /><br>
4. Buat `Dockerfile` yang berisi perintah untuk membuat docker image yang akan digunakan
   ```bash
   nano Dockerfile
   ```
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /modul1
   COPY . /modul1
   RUN pip install flask
   EXPOSE 6767
   CMD ["python", "modul1.py"]
   ```
5. Buat `inventory.ini` berisi target vps yang akan dikelola ansible
   ```ini
   [vps_azure]
   52.175.122.105 ansible_user=azureuser ansible_ssh_private_key_file=~/vps-api-danu_key.pem ansible_ssh_common_args='-o StrictHostKeyChecking=no'
   ```
6. Buat `playbook.yml` yang berisi serangkaian instruksi untuk menyelesaikan task yang diberikan
   ```yaml
    ---
    - name: Deployment API ke Docker
      hosts: vps_azure
      become: yes
      tasks:
        - name: Install Nginx, Docker, pip
          apt:
            name:
              - nginx
              - docker.io
              - python3-pip
            state: present
            update_cache: yes
    
        - name: Install Docker SDK
          pip:
            name: docker
            state: present
            extra_args: "--break-system-packages"
        - name: Cek Docker
          systemd:
            name: docker
            state: started
            enabled: yes
    
        - name: Buat direktori di VPS
          file:
            path: /home/azureuser/modul_deployment
            state: directory
    
        - name: Copy file modul1.py dan Dockerfile ke VPS
          copy:
            src: "{{ item }}"
            dest: /home/azureuser/modul_deployment/
          with_items:
            - modul1.py
            - Dockerfile
    
        - name: Build Docker Image di VPS
          community.docker.docker_image:
            name: api-danu
            build:
              path: /home/azureuser/modul_deployment
            source: build
            force_source: yes
    
        - name: Jalankan Container API di port 6767
          community.docker.docker_container:
            name: api_container
            image: api-danu:latest
            state: started
            restart_policy: always
            published_ports:
              - "127.0.0.1:6767:6767"
    
        - name: Konfigurasi Nginx sebagai Reverse Proxy
          copy:
            dest: /etc/nginx/sites-available/default
            content: |
              server {
                  listen 80;
                  server_name _;
                  location / {
                      proxy_pass http://127.0.0.1:6767;
                      proxy_set_header Host $host;
                      proxy_set_header X-Real-IP $remote_addr;
                      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                  }
              }
          notify: Restart Nginx
    
      handlers:
        - name: Restart Nginx
          systemd:
            name: nginx
            state: restarted
   ```
7. Push ke GitHub
   ```bash
    git init
    git add .
    git commit -m "initial commit"
    git branch -M main
    git remote add origin https://github.com/ItsDannz/deployment.git
    git push -u origin main     
   ```
8. Buat GitHub Action (deploy.yaml)
   ```bash
   nano .github/workflows/deploy.yml
   ```
   ```yaml
    name: CI/CD Deploy
    
    on:
      push:
        branches:
          - main
    jobs:
      deploy:
        runs-on: ubuntu-latest
    
        steps:
          - name: Checkout repository
            uses: actions/checkout@v3
    
          - name: Setup Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.x'
    
          - name: Install Ansible
            run: |
              pip install ansible
              ansible-galaxy collection install community.docker
    
          - name: Setup SSH Key
            run: |
              mkdir -p ~/.ssh
              echo "${{ secrets.KEY }}" > ~/.ssh/vps-key.pem
              chmod 400 ~/.ssh/vps-key.pem
    
          - name: Update inventory
            run: |
              sed -i 's|ansible_ssh_private_key_file=.*pem|ansible_ssh_private_key_file=~/.ssh/vps-key.pem|' inventory.ini
    
          - name: Run Ansible Playbook
            run: |
              ansible-playbook -i inventory.ini playbook.yaml
    
          - name: Test endpoint
            run: |
              sleep 5
              curl -f http://52.175.122.105/health
    ```
10. Buat `Repository Secret` baru dan tambahkan SSH key yang sudah didapatkan dari file `*.pem` ke GitHub Secret
    <img width="751" height="122" alt="image" src="https://github.com/user-attachments/assets/73406ed8-03d7-47d7-a380-a0fb612107b0" /><br>
11. Push `deploy.yaml` ke GitHub
    ```bash
    git add .
    git commit -m "github actions"
    git push
    ```
    <br>

## Penjelasan Code
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
        h, remain = divmod(uptime_seconds, 3600) #jam dan sisanya dalam detik
        m, s = divmod(remain, 60) #menit dan sisanya dalam detik
    
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
        <br>

4. playbook.yaml
    ```yaml
    #Header
    ---
    - name: Deployment API ke Docker
      hosts: vps_azure
      become: yes
    ```
    - Task
      ```yaml
      tasks:
      ```
        - Install Nginx, Docker, dan pip: Menginstall 3 package menggunakan `apt`, `update_cache: yes` akan menjalankan `apt update` terlebih dahulu
            ```yaml
            - name: Install Nginx, Docker, pip
                  apt:
                    name:
                      - nginx
                      - docker.io
                      - python3-pip
                    state: present
                    update_cache: yes
            ```
        - Install Docker SDK: Menginstall library python untuk ansible agar bisa mengontrol docker. Karena saya menggunakan VPS dengan versi Ubuntu 24.04, maka diperlukan extra argument berupa `--break-system-packages` untuk memaksa pip menginstall package
            ```yaml
            - name: Install Docker SDK
              pip:
                name: docker
                state: present
                extra_args: "--break-system-packages"
           ```
        - Cek Docker: Memastikan service Docker sudah berjalan dan akan otomatis start saat reboot
            ```yaml
            - name: Cek Docker
              systemd:
                name: docker
                state: started
                enabled: yes
            ```
        - Buat direktori di VPS: Membuat folder di VPS sebagai tempat menyimpan file project
            ```yaml
            - name: Buat direktori di VPS
              file:
                path: /home/azureuser/modul_deployment
                state: directory
            ```
        - Copy modul.py & Dockerfile ke VPS: Menyalin `modul1.py` dan `Dockerfile` ke VPS
            ```yaml
            - name: Copy file modul1.py dan Dockerfile ke VPS
              copy:
                src: "{{ item }}"
                dest: /home/azureuser/modul_deployment/
              with_items:
                - modul1.py
                - Dockerfile
            ```
        - Build Docker Image di VPS: Membuild Docker image bernama `api-danu` dari folder `modul_deployment`, `force_source: yes` akan memaksa rebuild meskipun image sudah ada
            ```yaml
            - name: Build Docker Image di VPS
              community.docker.docker_image:
                name: api-danu
                build:
                  path: /home/azureuser/modul_deployment
                source: build
                force_source: yes
            ```
        - Jalankan API di port 6767: Menjalankan container dari image `api-danu`. `127.0.0.1:6767:6767` berarti port 6767 hanya bisa diakses dari dalam VPS dan tidak bisa langsung dari internet
            ```yaml
            - name: Jalankan Container API di port 6767
              community.docker.docker_container:
                name: api_container
                image: api-danu:latest
                state: started
                restart_policy: always
                published_ports:
                  - "127.0.0.1:6767:6767"
            ```
        - Konfigurasi Nginx sebagai Reverse Proxy: Menulis konfigurasi Nginx langsung ke file default dan `notify: Restart Nginx` akan memanggil handler untuk restart Nginx setelah konfigurasi berubah
            ```yaml
            - name: Konfigurasi Nginx sebagai Reverse Proxy
              copy:
                dest: /etc/nginx/sites-available/default
                content: |
                  server {
                      listen 80;
                      server_name _;
                      location / {
                          proxy_pass http://127.0.0.1:6767;
                          proxy_set_header Host $host;
                          proxy_set_header X-Real-IP $remote_addr;
                          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                      }
                  }
              notify: Restart Nginx
            ```
    - Handler: Handler akan dijalankan jika dipanggil oleh `notify`
        ```yaml
        handlers:
        ```
        - Restart Nginx
            ```yaml
            - name: Restart Nginx
              systemd:
                name: nginx
                state: restarted
            ```
            <br>
5. .github/workflows/deploy.yaml
    - Header
        ```yaml
        name: CI/CD Deploy
        ```
    <br>
    
    - Event: Workflow otomatis berjalan setiap kali ada `git push` ke branch `main`
        ```yaml
        on:
          push:
            branches:
              - main
        ```
    <br>
    
    - Job: Mendefinisikan job bernama `deploy` yang berjalan di vm Ubuntu milik GitHub
        ```yaml 
        jobs:
          deploy:
            runs-on: ubuntu-latest
        ```
        <br>

        - Step
            ```yaml
            steps:
            ```
            <br>
            
            - Checkout Repository: Mengunduh isi repository ke vm GitHub Actions agar file bisa diakses
                ```yaml
                  - name: Checkout repository
                    uses: actions/checkout@v3
                ```
                <br>

            - Setup Python: Menginstall Python di vm GitHub Actions
                ```yaml
                  - name: Setup Python
                    uses: actions/setup-python@v4
                    with:
                      python-version: '3.x'
                ```
                <br>

            - Install Ansible: Menginstall Ansible dan collection `community.docker` agar `docker_image` dan `docker_container` bisa digunakan di playbook
                ```yaml
                  - name: Install Ansible
                    run: |
                      pip install ansible
                      ansible-galaxy collection install community.docker
                ```
                <br>

            - Setup SSH Key: Membuat folder SSH lalu mengambil SSH key dari GitHub Secrets dan menyimpannya ke file `vps-key.pem`
                ```yaml
                  - name: Setup SSH Key
                    run: |
                      mkdir -p ~/.ssh
                      echo "${{ secrets.KEY }}" > ~/.ssh/vps-key.pem
                      chmod 400 ~/.ssh/vps-key.pem
                ```
                <br>

            - Update Inventory: Mengganti path SSH key di `inventory.ini` dengan path yang ada di vm GitHub Actions
                ```yaml
                  - name: Update inventory
                    run: |
                      sed -i 's|ansible_ssh_private_key_file=.*pem|ansible_ssh_private_key_file=~/.ssh/vps-key.pem|' inventory.ini
                ```
                <br>

            - Run Ansible Playbook: Menjalankan Ansible Playbook untuk melakukan deployment ke VPS
                ```yaml
                  - name: Run Ansible Playbook
                    run: |
                      ansible-playbook -i inventory.ini playbook.yaml
                ```
                <br>

            - Test Endpoint: Tunggu 5 detik, lalu akses endpoint. Jika gagal maka workflow akan dianggap error
                ```yaml
                  - name: Test endpoint
                    run: |
                      sleep 5
                      curl -f http://52.175.122.105/health
                ```

