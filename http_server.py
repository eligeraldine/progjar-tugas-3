import sys
import os
import os.path
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        
        self.upload_dir = 'uploads'
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")

        response_headers=''
        for i in resp:
            response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
		#response adalah bytes
        return response

    def proses(self, data):
        parts = data.split("\r\n\r\n", 1)
        headers_section = parts[0]
        body = parts[1] if len(parts) > 1 else ""

        requests = headers_section.split("\r\n")
        baris = requests[0]

        all_headers = {h.split(': ')[0]: h.split(': ')[1] for h in requests[1:] if ': ' in h}

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address, all_headers)
            if method == 'POST':
                return self.http_post(object_address, all_headers, body)
            if method == 'DELETE':
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', 'Metode tidak didukung', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        if object_address == '/':
            return self.response(200, 'OK', 'Ini adalah web server percobaan', {})
            
        if object_address == '/list':
            try:
                main_files = os.listdir('./')
                upload_files = os.listdir(self.upload_dir)
                
                file_list_html = "<h1>Daftar File</h1>"
                file_list_html += "<h3>Direktori Utama (Server)</h3><ul>"
                for f in main_files:
                    file_list_html += f"<li>{f}</li>"
                file_list_html += "</ul>"
                
                file_list_html += f"<h3>Folder Uploads (/{self.upload_dir})</h3><ul>"
                for f in upload_files:
                    file_list_html += f"<li>{f}</li>"
                file_list_html += "</ul>"
                
                return self.response(200, 'OK', file_list_html, {'Content-Type': 'text/html'})
            except OSError:
                return self.response(500, 'Internal Server Error', 'Tidak bisa membaca direktori', {})

        file_path = object_address.lstrip('/')
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return self.response(404, 'Not Found', f'File {file_path} tidak ditemukan', {})
        
        with open(file_path, 'rb') as fp:
            isi = fp.read()
        
        fext = os.path.splitext(file_path)[1]
        content_type = self.types.get(fext, 'application/octet-stream')
        
        headers = {'Content-type': content_type}
        return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers, body):
        if object_address != '/upload':
            return self.response(405, 'Method Not Allowed', 'POST hanya dapat dilakukan untuk folder /upload', {})
        
        filename = headers.get('file_name')
        if not filename:
            return self.response(400, 'Bad Request', 'Header file_name tidak ditemukan', {})

        if not body:
            return self.response(400, 'Bad Request', 'Request body kosong', {})
            
        try:
            file_path = os.path.join(self.upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))
            return self.response(201, 'Created', f'File {filename} berhasil diupload ke /{self.upload_dir}/', {})
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Gagal menyimpan file: {e}', {})
            
    def http_delete(self, object_address, headers):
        filename = object_address.lstrip('/')
        file_path = os.path.join(self.upload_dir, filename)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return self.response(404, 'Not Found', f'File {filename} tidak dapat ditemukan di folder {self.upload_dir}', {})

        try:
            os.remove(file_path)
            return self.response(200, 'OK', f'File {filename} berhasil dihapus dari folder {self.upload_dir}.', {})
        except OSError as e:
            return self.response(500, 'Internal Server Error', f'Gagal menghapus file: {e}', {})