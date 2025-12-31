# 🏪 Inventory Management System (Tkinter + SQLite)

यह प्रोजेक्ट **Python Tkinter** और **SQLite** पर आधारित एक पूरा **Inventory & Billing Management System** है, जिसमें **Admin (Manager)** और **Customer** दोनों के लिए अलग-अलग डैशबोर्ड उपलब्ध हैं।

---

## 📌 Features / विशेषताएँ

### 🔐 Login System

* **Admin Login**

  * User ID: `admin`
  * Password: `admin`
* **Customer Login**

  * User ID: `user`
  * Password: `user`

---

### 👨‍💼 Manager (Admin) Dashboard

* 📊 **Dashboard**

  * Total Products
  * Total Stock
  * Out of Stock Products
  * Total Investment & Profit
  * Stock Graphs & Charts

* ➕ **Add Products**

  * Product name, category, cost, price (auto GST), stock
  * Supplier & reorder level
  * Auto-generated **Barcode**

* 👀 **View / Search Products**

  * Search by Name, Category, Supplier
  * Sort & Filter (Low stock highlight)
  * Delete & Bulk Delete

* ✏️ **Update Products**

  * Update cost, stock & reorder level using Product ID

* 📥 **Import Data**

  * Import products from CSV file

* 📤 **Export Data**

  * Export Products to:

    * CSV
    * Excel (.xlsx)
    * PDF (Inventory Report)

* 🧑‍🤝‍🧑 **Manage Suppliers**

  * Add / Delete suppliers

* 📈 **Advanced Analytics**

  * Cheapest products
  * Most stocked products
  * Category-wise stock distribution (Pie & Bar charts)

---

### 🧑‍💻 Customer Dashboard

* 🔍 View Products

  * Search, filter & sort
  * Low stock indication

* 🛒 **Sales & Billing System**

  * Add products to cart
  * Auto stock deduction
  * Total bill calculation
  * Invoice generation (PDF)

* 📄 **Invoice with QR Code**

  * Invoice saved as PDF
  * QR Code to open invoice via local server

---

## 🧰 Technologies Used

* **Python 3**
* **Tkinter** – GUI
* **SQLite3** – Database
* **Matplotlib** – Charts & Graphs
* **Pillow (PIL)** – Image & Blur effects
* **ReportLab** – PDF generation
* **qrcode** – QR code for invoices
* **openpyxl** – Excel export

---

## 📂 Database Tables

* `Products`
* `supplier`
* `Sales`

(All tables are auto-created on first run)

---

## ▶️ How to Run the Project

1. Install required libraries:

```bash
pip install matplotlib pillow reportlab qrcode openpyxl
```

2. Run the Python file:

```bash
python main.py
```

3. Login using:

* Admin → `admin / admin`
* Customer → `user / user`

---

## 📁 Folder Structure

```
project/
│-- main.py
│-- mydatabase.db
│-- invoices/
│-- README.md
```

---

## ⚠️ Notes

* Ensure Python 3 is installed
* Internet is **not required** (local server used for QR invoice)
* Works best on **Windows** (for `os.startfile`)

---

## 👤 Author / Student Details

* **Name:** Ashu
* **Class:** XII A
* **Subject:** Computer Science

---

## ✅ Conclusion

यह प्रोजेक्ट **School / Practical Submission** के लिए एक complete और professional-level Inventory Management System है, जिसमें GUI, Database, Analytics, PDF, QR Code और Billing सभी शामिल हैं।

✨ *Perfect for Computer Science Project Submission* ✨
