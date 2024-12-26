import streamlit as st
from datetime import datetime
import pandas as pd
import json

class Mahasiswa:
    def __init__(self, nama, nim, ipk):
        self.nama = nama
        self.nim = nim
        self.ipk = ipk
        self.status = None
        self.tanggal_daftar = datetime.now()

class ProgramStudi:
    def __init__(self, nama_prodi, akreditasi, kuota, batas_ipk):
        self.nama_prodi = nama_prodi
        self.akreditasi = akreditasi
        self.kuota = kuota
        self.batas_ipk = batas_ipk
        self.daftar_mahasiswa = []
        self.mahasiswa_lulus = []

    def tambah_mahasiswa(self, mahasiswa):
        self.daftar_mahasiswa.append(mahasiswa)

    def seleksi_beasiswa(self, mahasiswa):
        if len(self.mahasiswa_lulus) < self.kuota:
            if mahasiswa.ipk >= self.batas_ipk:
                mahasiswa.status = "Lolos Beasiswa"
                self.mahasiswa_lulus.append(mahasiswa)
                return True
        mahasiswa.status = "Tidak Lolos"
        return False

class Fakultas:
    def __init__(self, nama_fakultas):
        self.nama_fakultas = nama_fakultas
        self.daftar_prodi = []

    def tambah_prodi(self, prodi):
        self.daftar_prodi.append(prodi)

class Universitas:
    def __init__(self, nama_universitas):
        self.nama_universitas = nama_universitas
        self.daftar_fakultas = []

    def tambah_fakultas(self, fakultas):
        self.daftar_fakultas.append(fakultas)

class SeleksiMahasiswa:
    def __init__(self, data):
        self.data = data
        self.universitas = Universitas(data["nama_universitas"])
        for fakultas_data in data["fakultas"]:
            fakultas = Fakultas(fakultas_data["nama_fakultas"])
            self.universitas.tambah_fakultas(fakultas)
            for prodi_data in fakultas_data["prodi"]:
                prodi = ProgramStudi(
                    prodi_data["nama_prodi"],
                    prodi_data["akreditasi"],
                    prodi_data["kuota"],
                    prodi_data["batas_ipk"]
                )
                fakultas.tambah_prodi(prodi)
                for mahasiswa_data in prodi_data["mahasiswa"]:
                    mahasiswa = Mahasiswa(
                        mahasiswa_data["nama"],
                        mahasiswa_data["nim"],
                        mahasiswa_data["ipk"]
                    )
                    prodi.tambah_mahasiswa(mahasiswa)

    def tambah_mahasiswa(self, nama_fakultas, nama_prodi, nama, nim, ipk):
        fakultas = next((f for f in self.universitas.daftar_fakultas if f.nama_fakultas == nama_fakultas), None)
        if not fakultas:
            fakultas = Fakultas(nama_fakultas)
            self.universitas.tambah_fakultas(fakultas)

        prodi = next((p for p in fakultas.daftar_prodi if p.nama_prodi == nama_prodi), None)
        if not prodi:
            prodi = ProgramStudi(nama_prodi, "A", 10, 3.5)
            fakultas.tambah_prodi(prodi)

        mahasiswa = Mahasiswa(nama, nim, ipk)
        prodi.tambah_mahasiswa(mahasiswa)

        # Update the JSON data
        self.update_json()

    def update_json(self):
        data = {
            "nama_universitas": self.universitas.nama_universitas,
            "fakultas": [],
            "beasiswa": self.data.get("beasiswa", [])
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
                    "kuota": prodi.kuota,
                    "batas_ipk": prodi.batas_ipk,
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
                                if len(lulus) < kuota and prodi.seleksi_beasiswa(mahasiswa):
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

        # Append selected students to the corresponding beasiswa in the JSON data
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

            # Update the JSON data
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

def main():
    with open('data.json', 'r') as f:
        data = json.load(f)

    seleksi = SeleksiMahasiswa(data)

    st.title("Seleksi Mahasiswa Beasiswa")

    menu = st.selectbox("Menu", ["Tambah Mahasiswa", "Tampilkan Mahasiswa", "Atur Seleksi Beasiswa", "Seleksi Beasiswa"])

    if menu == "Tambah Mahasiswa":
        nama_fakultas = st.selectbox("Pilih Nama Fakultas:", [f.nama_fakultas for f in seleksi.universitas.daftar_fakultas])
        fakultas = next((f for f in seleksi.universitas.daftar_fakultas if f.nama_fakultas == nama_fakultas), None)

        nama_prodi = st.selectbox("Pilih Nama Program Studi:", [p.nama_prodi for p in fakultas.daftar_prodi])
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