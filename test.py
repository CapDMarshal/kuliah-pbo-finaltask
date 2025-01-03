import streamlit as st
from datetime import datetime
import pandas as pd
import json

# Kelas Mahasiswa merepresentasikan data mahasiswa
class Mahasiswa:
    def __init__(self, nama, nim, ipk):
        self.nama = nama
        self.nim = nim
        self.ipk = ipk
        self.status = None
        self.tanggal_daftar = datetime.now()

# Kelas ProgramStudi merepresentasikan program studi
class ProgramStudi:
    def __init__(self, nama_prodi, akreditasi):
        self.nama_prodi = nama_prodi
        self.akreditasi = akreditasi
        self.daftar_mahasiswa = []

    # Metode untuk menambahkan mahasiswa ke dalam program studi
    def tambah_mahasiswa(self, mahasiswa):
        self.daftar_mahasiswa.append(mahasiswa)

# Kelas Fakultas merepresentasikan fakultas
class Fakultas:
    def __init__(self, nama_fakultas):
        self.nama_fakultas = nama_fakultas
        self.daftar_prodi = []

    # Metode untuk menambahkan program studi ke dalam fakultas
    def tambah_prodi(self, prodi):
        self.daftar_prodi.append(prodi)

# Kelas Universitas merepresentasikan universitas
class Universitas:
    def __init__(self, nama_universitas):
        self.nama_universitas = nama_universitas
        self.daftar_fakultas = []

    # Metode untuk menambahkan fakultas ke dalam universitas
    def tambah_fakultas(self, fakultas):
        self.daftar_fakultas.append(fakultas)

# Kelas SeleksiMahasiswa mengelola proses seleksi mahasiswa untuk beasiswa
class SeleksiMahasiswa:
    def __init__(self, data):
        self.data = data
        self.universitas = Universitas(data["nama_universitas"])
        self.kuota = data.get("kuota", 10)
        self.batas_ipk = data.get("batas_ipk", 3.5)
        for fakultas_data in data["fakultas"]:
            fakultas = Fakultas(fakultas_data["nama_fakultas"])
            self.universitas.tambah_fakultas(fakultas)
            for prodi_data in fakultas_data["prodi"]:
                prodi = ProgramStudi(
                    prodi_data["nama_prodi"],
                    prodi_data["akreditasi"]
                )
                fakultas.tambah_prodi(prodi)
                for mahasiswa_data in prodi_data["mahasiswa"]:
                    mahasiswa = Mahasiswa(
                        mahasiswa_data["nama"],
                        mahasiswa_data["nim"],
                        mahasiswa_data["ipk"]
                    )
                    prodi.tambah_mahasiswa(mahasiswa)

    # Metode untuk menambahkan mahasiswa baru ke dalam program studi tertentu
    def tambah_mahasiswa(self, nama_fakultas, nama_prodi, nama, nim, ipk):
        fakultas = next((f for f in self.universitas.daftar_fakultas if f.nama_fakultas == nama_fakultas), None)
        if not fakultas:
            fakultas = Fakultas(nama_fakultas)
            self.universitas.tambah_fakultas(fakultas)

        prodi = next((p for p in fakultas.daftar_prodi if p.nama_prodi == nama_prodi), None)
        if not prodi:
            prodi = ProgramStudi(nama_prodi, "A")
            fakultas.tambah_prodi(prodi)

        mahasiswa = Mahasiswa(nama, nim, ipk)
        prodi.tambah_mahasiswa(mahasiswa)

        # Memperbarui data JSON
        self.update_json()

    # Metode untuk memperbarui file JSON dengan data terbaru dari objek Universitas
    def update_json(self):
        data = {
            "nama_universitas": self.universitas.nama_universitas,
            "fakultas": [],
            "beasiswa": self.data.get("beasiswa", []),
            "kuota": self.kuota,
            "batas_ipk": self.batas_ipk
        }
        for fakultas in self.universitas.daftar_fakultas:
            fakultas_data = {
                "nama_fakultas": fakultas.nama_fakultas,
                "prodi": []
            }
            for prodi in fakultas.daftar_prodi:
                prodi_data = {
                    "nama_prodi": prodi.nama_prodi,
                    "akreditasi": prodi.akreditasi,
                    "mahasiswa": []
                }
                for mahasiswa in prodi.daftar_mahasiswa:
                    mahasiswa_data = {
                        "nama": mahasiswa.nama,
                        "nim": mahasiswa.nim,
                        "ipk": mahasiswa.ipk,
                        "tanggal_daftar": mahasiswa.tanggal_daftar.strftime("%Y-%m-%d")
                    }
                    prodi_data["mahasiswa"].append(mahasiswa_data)
                fakultas_data["prodi"].append(prodi_data)
            data["fakultas"].append(fakultas_data)

        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

    # Metode untuk menampilkan data mahasiswa dalam bentuk tabel
    def tampilkan_mahasiswa(self):
        if not self.universitas.daftar_fakultas:
            st.write("Tidak ada data mahasiswa.")
            return

        for fakultas in self.universitas.daftar_fakultas:
            st.write(f"### Fakultas: {fakultas.nama_fakultas}")
            for prodi in fakultas.daftar_prodi:
                st.write(f"#### Program Studi: {prodi.nama_prodi}")
                data = []
                for mahasiswa in prodi.daftar_mahasiswa:
                    data.append({
                        "Nama": mahasiswa.nama,
                        "NIM": mahasiswa.nim,
                        "IPK": mahasiswa.ipk,
                        "Status": mahasiswa.status,
                        "Tanggal Daftar": mahasiswa.tanggal_daftar.strftime("%Y-%m-%d")
                    })
                df = pd.DataFrame(data)
                st.table(df)

    # Metode untuk melakukan seleksi beasiswa berdasarkan nama beasiswa yang dipilih
    def seleksi_beasiswa(self, nama_beasiswa):
        st.write(f"\nSeleksi Beasiswa {nama_beasiswa}:")
        lulus = []
        tidak_lulus = []

        beasiswa = next((b for b in self.data["beasiswa"] if b["nama_beasiswa"] == nama_beasiswa), None)
        if not beasiswa:
            st.write(f"Beasiswa {nama_beasiswa} tidak ditemukan.")
            return

        tanggal_mulai = datetime.strptime(beasiswa["tanggal_mulai"], "%Y-%m-%d")
        tanggal_akhir = datetime.strptime(beasiswa["tanggal_akhir"], "%Y-%m-%d")
        kuota = beasiswa["kuota"]

        valid_tanggal = False

        for fakultas in self.universitas.daftar_fakultas:
            if fakultas.nama_fakultas == beasiswa["fakultas"]:
                for prodi in fakultas.daftar_prodi:
                    if prodi.nama_prodi == beasiswa["prodi"]:
                        for mahasiswa in prodi.daftar_mahasiswa:
                            if tanggal_mulai <= mahasiswa.tanggal_daftar <= tanggal_akhir:
                                valid_tanggal = True
                                if len(lulus) < kuota and mahasiswa.ipk >= beasiswa["batas_ipk"]:
                                    lulus.append((fakultas.nama_fakultas, prodi.nama_prodi, mahasiswa))
                                else:
                                    tidak_lulus.append((fakultas.nama_fakultas, prodi.nama_prodi, mahasiswa))

        if not valid_tanggal:
            st.write(f"Tidak ada pendaftaran beasiswa pada periode {tanggal_mulai.strftime('%Y-%m-%d')} hingga {tanggal_akhir.strftime('%Y-%m-%d')}.")
            return

        st.write("\nMahasiswa yang Lolos Seleksi Beasiswa:")
        if not lulus:
            st.write("Tidak ada mahasiswa yang lolos seleksi beasiswa.")
        else:
            for nama_fakultas, nama_prodi, mahasiswa in lulus:
                st.write(f"Fakultas: {nama_fakultas}, Program Studi: {nama_prodi}, Nama: {mahasiswa.nama}, NIM: {mahasiswa.nim}, IPK: {mahasiswa.ipk:.2f}")

        st.write("\nMahasiswa yang Tidak Lolos Seleksi Beasiswa:")
        if not tidak_lulus:
            st.write("Semua mahasiswa lolos seleksi beasiswa.")
        else:
            for nama_fakultas, nama_prodi, mahasiswa in tidak_lulus:
                st.write(f"Fakultas: {nama_fakultas}, Program Studi: {nama_prodi}, Nama: {mahasiswa.nama}, NIM: {mahasiswa.nim}, IPK: {mahasiswa.ipk:.2f}")

        for beasiswa in self.data["beasiswa"]:
            if beasiswa["nama_beasiswa"] == nama_beasiswa:
                for _, _, mahasiswa in lulus:
                    beasiswa["mahasiswa"].append({
                        "nama": mahasiswa.nama,
                        "nim": mahasiswa.nim,
                        "ipk": mahasiswa.ipk
                    })
                break

        self.update_json()

    # Metode untuk membuat beasiswa baru dengan mengisi form yang disediakan
    def buat_beasiswa(self):
        st.write("\nPembuatan Beasiswa per Program Studi:")

        nama_beasiswa = st.text_input("Masukkan Nama Beasiswa:")
        fakultas_nama = st.selectbox("Pilih Nama Fakultas:", [f.nama_fakultas for f in self.universitas.daftar_fakultas])
        fakultas = next((f for f in self.universitas.daftar_fakultas if f.nama_fakultas == fakultas_nama), None)

        prodi_nama = st.selectbox("Pilih Nama Program Studi:", [p.nama_prodi for p in fakultas.daftar_prodi])
        prodi = next((p for p in fakultas.daftar_prodi if p.nama_prodi == prodi_nama), None)

        tanggal_mulai = st.text_input("Masukkan Tanggal Mulai Pendaftaran Beasiswa (YYYY-MM-DD):")
        tanggal_akhir = st.text_input("Masukkan Tanggal Akhir Pendaftaran Beasiswa (YYYY-MM-DD):")
        kuota = st.number_input("Masukkan Kuota Beasiswa:", min_value=1)
        batas_ipk = st.number_input("Masukkan Batas IPK untuk Beasiswa:", min_value=0.0, max_value=4.0, step=0.01)

        if st.button("Buat Beasiswa"):
            st.write(f"Beasiswa {nama_beasiswa} untuk Program Studi {prodi.nama_prodi} berhasil dibuat")
            st.write(f"Periode Pendaftaran: {tanggal_mulai} hingga {tanggal_akhir}")
            st.write(f"Kuota Beasiswa: {kuota}, Batas IPK: {batas_ipk:.2f}")

            beasiswa_data = {
                "nama_beasiswa": nama_beasiswa,
                "fakultas": fakultas_nama,
                "prodi": prodi_nama,
                "tanggal_mulai": tanggal_mulai,
                "tanggal_akhir": tanggal_akhir,
                "kuota": kuota,
                "batas_ipk": batas_ipk,
                "mahasiswa": []
            }
            self.data["beasiswa"].append(beasiswa_data)
            self.update_json()

# Fungsi utama yang dijalankan saat program dimulai
def main():
    with open('data.json', 'r') as f:
        data = json.load(f)

    seleksi = SeleksiMahasiswa(data)

    st.title("Seleksi Mahasiswa Beasiswa")

    menu = st.selectbox("Menu", ["Tambah Mahasiswa", "Tampilkan Mahasiswa", "Atur Seleksi Beasiswa", "Seleksi Beasiswa"])

    if menu == "Tambah Mahasiswa":
        nama_fakultas = st.text_input("Nama Fakultas:").title()
        fakultas = next((f for f in seleksi.universitas.daftar_fakultas if f.nama_fakultas == nama_fakultas), None)
        if not fakultas:
            fakultas = Fakultas(nama_fakultas)
            seleksi.universitas.tambah_fakultas(fakultas)

        nama_prodi = st.text_input("Nama Program Studi:").title()
        prodi = next((p for p in fakultas.daftar_prodi if p.nama_prodi == nama_prodi), None)
        if not prodi:
            akreditasi = st.text_input("Akreditasi Program Studi:").upper()
            prodi = ProgramStudi(nama_prodi, akreditasi)
            fakultas.tambah_prodi(prodi)

        nama = st.text_input("Nama Mahasiswa:").title()
        nim = st.text_input("NIM:")
        ipk = st.number_input("IPK:", min_value=0.0, max_value=4.0, step=0.01)
        if st.button("Tambah Mahasiswa"):
            seleksi.tambah_mahasiswa(nama_fakultas, nama_prodi, nama, nim, ipk)
            st.write("Mahasiswa berhasil ditambahkan.")

    elif menu == "Tampilkan Mahasiswa":
        seleksi.tampilkan_mahasiswa()

    elif menu == "Atur Seleksi Beasiswa":
        seleksi.buat_beasiswa()

    elif menu == "Seleksi Beasiswa":
        nama_beasiswa = st.selectbox("Pilih Nama Beasiswa:", [b["nama_beasiswa"] for b in data["beasiswa"]])
        if st.button("Seleksi Beasiswa"):
            seleksi.seleksi_beasiswa(nama_beasiswa)

if __name__ == "__main__":
    main()