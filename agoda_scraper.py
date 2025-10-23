from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def init_driver():
    # Gunakan ChromeDriverManager untuk mengelola driver
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def scrape_reviews(driver, url):
    driver.get(url)

    # Tunggu halaman ulasan termuat
    time.sleep(10)

    # List untuk menyimpan data ulasan
    data = []

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        review_section = soup.find("ol", class_="Review-comments")
        reviews = review_section.find_all("div", attrs={"aria-label": "Komentar ulasan"})

        for review in reviews:
            #ngambil nama user
            try:
                user_raw = review.find("div", class_="Review-comment-reviewer")
                user = user_raw.find("strong").text.strip()
            except:
                user = "gak ada user"
            #ngambil ulasan utama
            try:
                comment = review.find("p", class_="Review-comment-bodyText").text.strip()
            except Exception as e:
                comment = "Error not found"
            #ngambil rating
            try:
                rating = review.find("div", class_="Review-comment-leftScore").text.strip()
            except:
                rating = "Gak ada rating"
            # print(rating)

            #ngambil tanggal ulasan
            try:
                date_raw = review.find("span", class_="sc-dlfnbm Typographystyled__TypographyStyled-sc-1uoovui-0 fYfVZM ijeBDa").text.strip()
                date = date_raw.replace("Diulas pada ","")
            except Exception as e:
                print(e)
                date = "gak ada tgl"

            data.append([user, comment, date, rating])

        try:
            next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label= 'Halaman ulasan selanjutnya']"))
                )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
        except:
            print("Tidak ada halaman selanjutnya")
            break
    
    return data

def save_to_excel(data, nama_file):
    # Simpan ke dalam DataFrame
    df = pd.DataFrame(data, columns=["username", "user_review", "review_date", "rating"])

    # Simpan ke file Excel
    df.to_excel(nama_file+".xlsx", index=False)

def main():
    # URL produk Tokopedia (ganti dengan produk yang ingin di-scrape)
    url = input("Masukkan link review: ")

    # Simpan ke file Excel
    nama_file = input("Masukkan Nama File Hasil Scraping: ")

    # Inisiasi driver
    driver = init_driver()

    try:
        data = scrape_reviews(driver, url)
        save_to_excel(data, nama_file)
    finally:
        # Tutup browser
        driver.quit()

        print("Scraping selesai! Semua ulasan telah disimpan")

if __name__ == "__main__":
    main()