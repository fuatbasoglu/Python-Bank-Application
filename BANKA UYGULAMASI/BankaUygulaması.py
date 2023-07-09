import csv
import sqlite3
import datetime
import random
import os
os.system("cls") # Konsol Temizlemek için kod eğer Mac veya Linux işletim sistemi kullanılıyorsa ### os.system(“clear”) ### komutu kullanılmalı
# Aşağıdaki kod ile beraber klasörün içine oluşturulacak olan veri tabanı bağlantısını yapıyoruz
conn = sqlite3.connect("banka.db")
cursor = conn.cursor()
# Oluşturduğumuz veritabanının tabloların aşağıdaki kod parçaları oluşturuyor
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    usertype TEXT,
    balance REAL
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    date TEXT,
    amount REAL,
    type TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)""")
# Kullanıcı sınıflarının tanımlanması
class User:
    # Tüm kullanıcıların ortak özellikleri
    def __init__(self, id, username, password, usertype, balance):
        self.id = id
        self.username = username
        self.password = password
        self.usertype = usertype
        self.balance = balance

    def deposit(self, amount):
        # Para yatırma işlemi bu kodlar sayesinde gerçekleşiyor
        self.balance += amount
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (self.balance, self.id))
        conn.commit()
        cursor.execute("INSERT INTO transactions (user_id, date, amount, type) VALUES (?, ?, ?, ?)", (self.id, datetime.datetime.now(), amount, "deposit"))
        conn.commit()
        print(f"{amount} TL yatırıldı. Yeni bakiye: {self.balance} TL")

    def withdraw(self, amount):
        # Para çekme işlemi bu kodlar sayesinde gerçekleşiyor
        if self.balance >= amount:
            self.balance -= amount
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (self.balance, self.id))
            conn.commit()
            cursor.execute("INSERT INTO transactions (user_id, date, amount, type) VALUES (?, ?, ?, ?)", (self.id, datetime.datetime.now(), amount, "withdraw"))
            conn.commit()
            print(f"{amount} TL çekildi. Yeni bakiye: {self.balance} TL")
        else:
            print("Yetersiz bakiye!")

    def transfer(self, other_user, amount):
        # Para transferi işlemi bu kodlar sayesinde gerçekleşiyor
        if self.balance >= amount:
            self.balance -= amount
            other_user.balance += amount
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (self.balance, self.id))
            conn.commit()
            cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (other_user.balance, other_user.id))
            conn.commit()
            cursor.execute("INSERT INTO transactions (user_id, date, amount, type) VALUES (?, ?, ?, ?)", (self.id, datetime.datetime.now(), -amount, "transfer"))
            conn.commit()
            cursor.execute("INSERT INTO transactions (user_id, date, amount, type) VALUES (?, ?, ?, ?)", (other_user.id, datetime.datetime.now(), amount, "transfer"))
            conn.commit()
            print(f"{other_user.username} adlı kullanıcıya {amount} TL transfer edildi. Yeni bakiye: {self.balance} TL")
        else:
            print("Yetersiz bakiye!")

    def report(self):   #Kullanıcı bu kodlarla beraber işlem raporunu csv olarak alabilir
        filename = f"{self.username}_report.csv"
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Amount", "Type"])
            cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (self.id,))
            records = cursor.fetchall()
            for record in records:
                writer.writerow(record[1:])
        print(f"{filename} dosyası oluşturuldu.")

class Admin(User):  # Admin grubundaki kullanıcıların özellikleri 
    def __init__(self, id, username, password):
        super().__init__(id, username, password, "admin", 0)

    def show_users(self):
        # Sistemde kayıtlı olan tüm kullanıcıları gösterme işlemi
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            print(user)

    def show_transactions(self):
        # Sistemdeki tüm işlemleri gösterme işlemi
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        for transaction in transactions:
            print(transaction)

    def report_by_user(self, user_id):
        # Belirli bir kullanıcının işlem raporunu csv dosyası olarak alma kodları
        filename = f"user_{user_id}_report.csv"
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Amount", "Type"])
            cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
            records = cursor.fetchall()
            for record in records:
                writer.writerow(record[1:])
        print(f"{filename} dosyası oluşturuldu.")

class Standard(User):   # Standard kullanıcı grubundaki kullanıcıların özellikleri
    def __init__(self, id, username, password, balance):
        super().__init__(id, username, password, "standard", balance)
# Kullanıcıların oturuma giriş yapma işlemi
def login(username, password):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    if user:
        if user[3] == "admin":
            return Admin(user[0], user[1], user[2])
        elif user[3] == "standard":
            return Standard(user[0], user[1], user[2], user[4])
    else:
        return None
# Yeni bir kullanıcı oluşturmak için fonksiyon kodları
def create_user():
    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")
    balance = float(input("Bakiye: "))
    cursor.execute("INSERT INTO users (username, password, usertype, balance) VALUES (?, ?, ?, ?)", (username, password, "standard", balance))
    conn.commit()
    user_id = cursor.lastrowid
    return Standard(user_id, username, password, balance)
# Programın  çalışması için gereklen ana fonksiyon
def main():
    # Programın giriş tanıtım yazısı
    print("Python Banka Uygulamasına Hoşgeldiniz!")
    print("-" * 30)

    # Kullanıcı girişi veya yeni kullanıcı oluşturma seçenekleri
    print("Lütfen yapmak istediğiniz işlemi seçiniz:")
    print("1) Giriş yap")
    print("2) Yeni kullanıcı oluştur")
    choice = input("Seçiminiz: ")

    # Yukarıda yaptığımız seçime göre o seçimin fonksiyonu aşağıdaki kodlar ile çağırılıyor
    if choice == "1":
        username = input("Kullanıcı adı: ")
        password = input("Şifre: ")
        user = login(username, password)
        if user:
            print(f"Merhaba {user.username}, başarıyla giriş yaptınız.")
        else:
            print("Hatalı kullanıcı adı veya şifre!")
            return
    elif choice == "2":
        user = create_user()
        print(f"Merhaba {user.username}, başarıyla yeni kullanıcı oluşturdunuz.")
    else:
        print("Geçersiz seçim!")
        return
    os.system("cls")

    # Kullanıcının gruplarına (standard ya da admin) göre yapabileceği işlemlerin listelenmesi
    while True:
        print("-" * 30)
        print("Lütfen yapmak istediğiniz işlemi seçiniz:")
        if user.usertype == "admin":
            print("1) Tüm kullanıcıları göster")
            print("2) Tüm işlemleri göster")
            print("3) Belirli bir kullanıcının işlem raporunu al")
            print("4) Çıkış yap")
            choice = input("Seçiminiz: ")
            if choice == "1":
                user.show_users()
            elif choice == "2":
                user.show_transactions()
            elif choice == "3":
                user_id = int(input("Kullanıcı ID: "))
                user.report_by_user(user_id)
            elif choice == "4":
                print(f"Çıkış yaptınız. Görüşmek üzere {user.username}!")
                break
            else:
                print("Geçersiz seçim!")
        elif user.usertype == "standard": # Standard kullanıcı tipinin yapabileceği işlemler aşağıda listelenmiştir 
            print("1) Bakiye sorgula")
            print("2) Para yatır")
            print("3) Para çek")
            print("4) Para transfer et")
            print("5) İşlem raporu al")
            print("6) Çıkış yap")
            choice = input("Seçiminiz: ")
            if choice == "1":
                print(f"Bakiyeniz: {user.balance} TL")
            elif choice == "2":
                amount = float(input("Yatırılacak miktar: "))
                user.deposit(amount)
            elif choice == "3":
                amount = float(input("Çekilecek miktar: "))
                user.withdraw(amount)
            elif choice == "4":
                other_username = input("Transfer edilecek kullanıcı adı: ")
                cursor.execute("SELECT * FROM users WHERE username = ?", (other_username,))
                other_user = cursor.fetchone()
                if other_user:
                    other_user = Standard(other_user[0], other_user[1], other_user[2], other_user[4])
                    amount = float(input("Transfer edilecek miktar: "))
                    user.transfer(other_user, amount)
                else:
                    print("Böyle bir kullanıcı bulunamadı!")
            elif choice == "5":
                user.report()
            elif choice == "6":
                print(f"Çıkış yaptınız. Görüşmek üzere {user.username}!")
                break
            else:
                print("Geçersiz seçim!")
os.system("cls")
if __name__ == "__main__": 
    main()
# En son main fonksiyonunu çağırarak uygulamamızın çalışmasını sağlıyoruz