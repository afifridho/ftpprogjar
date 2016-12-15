# ftpprogjar
fp gan!

[Membuat FTP Server dan Klien]
Ketentuannya adalah mengimplementasikan RFC 959 (dituliskan dengan subbab) sebagai berikut
- Membuat aplikasi FTP klien dan server

bebet
- Autentikasi (USER dan PASS: 4.1.1)
- Mengubah direktori aktif (CWD: 4.1.1)
- Keluar aplikasi (QUIT: 4.1.1)

vivi
- Unduh (RETR: 4.1.3)
- Unggah (STOR: 4.1.3)
- Mengganti nama file (RNTO: 4.1.3)

afif
- Menghapus file (DELE: 4.1.3) 
- Menghapus direktori (RMD: 4.1.3)
- Membuat direktori (MKD: 4.1.3)

oing
- Mencetak direktori aktif (PWD: 4.1.3)
- Mendaftar file dan direktori (LIST: 4.1.3)
- HELP: 4.1.3

- Reply codes (200, 500, 202, 230, 530: 4.2.1)
- Menerapkan teknik multiclient dengan modul select DAN thread
