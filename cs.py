import sqlite3 as sql
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import messagebox, ttk, filedialog
import csv
from datetime import datetime
import qrcode
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from PIL import Image, ImageTk, ImageFilter
root = Tk()
root.title("Glass Login")
root.geometry("1200x750")
BG_APP = "#0F172A"
BG_PANEL = "#1E293B"
BG_PANEL_2 = "#24324A"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#CBD5E1"
INPUT_BG = "#F8FAFC"
INPUT_FG = "#0F172A"
BORDER = "#334155"
C_PRIMARY = "#3B82F6"
C_SUCCESS = "#14B8A6"
C_WARN = "#F59E0B"
C_DANGER = "#EF4444"
C_PURPLE = "#A855F7"
C_SNOW = "#F0F8FF"
CHART_COLORS = [C_PRIMARY, C_SUCCESS, C_WARN, C_DANGER, C_PURPLE]
try:
    conn = sql.connect("mydatabase.db")
    curser = conn.cursor()
except Exception as e:
    messagebox.showerror("DB Error", "Ensure MySQL is running and password is correct.")
    conn = None
    curser = None
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass
style.configure("TNotebook", background=BG_APP, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    background=BG_PANEL,
    foreground=TEXT_SECONDARY,
    padding=(14, 8),
    font=("Helvetica", 11, "bold"),
)
style.map(
    "TNotebook.Tab",
    background=[("selected", BG_PANEL_2)],
    foreground=[("selected", TEXT_PRIMARY)],
)
style.configure(
    "Treeview",
    background=C_SNOW,
    fieldbackground=C_SNOW,
    foreground="#000000",
    bordercolor=BORDER,
    lightcolor=BORDER,
    darkcolor=BORDER,
)
style.configure(
    "Treeview.Heading",
    background="aliceblue",
    foreground="#000000",
    font=("Helvetica", 12, "bold")
)
style.map(
    "Treeview",
    background=[("selected", C_PRIMARY)],
    foreground=[("selected", TEXT_PRIMARY)],
)
style.configure(
    "TCombobox",
    fieldbackground=INPUT_BG,
    background=INPUT_BG,
    foreground=INPUT_FG,)

m = Menu(root)
root.config(menu=m)
h = Menu(m, tearoff=0)
m.add_cascade(label="Help", menu=h)
def logout(current_frame):
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        current_frame.destroy()
        glass.place(relx=0.5, rely=0.5, anchor=CENTER) 
        user.delete(0, END) 
        pwd.delete(0, END)


def manager():
    manager_frame = Frame(root, bg=BG_APP)
    manager_frame.pack(fill="both", expand=True)
    header_frame = Frame(manager_frame, bg=BG_PANEL, height=50)
    header_frame.pack(fill="x", side="top")
    Label(header_frame, text="Manager Dashboard", font=("Helvetica", 14, "bold"), bg=BG_PANEL, fg=TEXT_PRIMARY).pack(side="left", padx=20, pady=10)
    Button(header_frame, text="Logout", command=lambda: logout(manager_frame), bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 10, "bold")).pack(side="right", padx=20, pady=10)
    tabs = ttk.Notebook(manager_frame)
    tabs.pack(expand=1, fill="both", padx=10, pady=10)
    def database_setup():
        global conn,curser
        curser.execute('''
            create table if not exists Products(
                    id integer primary key autoincrement,
                    name text,
                    category text,
                    cost float,
                    price float,
                    stock integer,
                    supplier text,
                    reorder integer,
                    barcode text unique
            )''')
        curser.execute('''
            create table if not exists supplier(
                    id integer primary key autoincrement,
                    name text,
                    contact text,
                    email unique,
                    address text
            )''')
        curser.execute('''
            create table if not exists Sales(
                    id integer primary key autoincrement,
                    Customer_Name text,
                    Date text,
                    totalamount real,
                    items text
            )''')
        conn.commit()
    database_setup()
    def generate_barcode():
        import random,string
        return ''.join(random.choices(string.ascii_uppercase + string.digits,k =8))
    def show_dashboard():
        global curser,conn
        for i in range(len(tabs.tabs())):
            if tabs.tab(i, "text") == "Dashboard":
                tabs.forget(i)
                break
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Dashboard")
        main_frame = Frame(tab, bg=BG_PANEL)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        try:  
            curser.execute("SELECT COUNT(*) FROM Products")
            total_products = curser.fetchone()[0]
            curser.execute("SELECT SUM(Stock) FROM Products")
            total_stock = curser.fetchone()[0] or 0
            curser.execute("SELECT SUM(price) FROM Products")
            total_price = curser.fetchone()[0] or 0
            curser.execute("SELECT COUNT(*) FROM Products WHERE Stock = 0")
            out_of_stock = curser.fetchone()[0]
            curser.execute("SELECT sum(cost) FROM Products")
            cost_price = curser.fetchone()[0] or 0
            stats_frame = Frame(main_frame, bg=BG_PANEL)
            stats_frame.pack(fill="x", pady=(0, 20))
            stats = [
                ("Total Products", total_products, C_PRIMARY),
                ("Total Stock", total_stock, C_SUCCESS),
                ("Out of Stock", out_of_stock, C_DANGER),
                ("Total Investment", f"₹{cost_price:.2f}", C_PURPLE),
                ("Total Profit", f"₹{(total_price-cost_price):.2f}", C_WARN)
            ]
            for stat_name, stat_value, color in stats:
                card = Frame(stats_frame, bg=color, height=80)
                card.pack(side="left", fill="both", expand=True, padx=5)
                Label(card, text=stat_name, font=("Helvetica", 11, "bold"), bg=color, fg=TEXT_PRIMARY).pack(pady=(10, 2))
                Label(card, text=str(stat_value), font=("Helvetica", 18, "bold"), bg=color, fg=TEXT_PRIMARY).pack(pady=(2, 10))
            graph_frame = Frame(main_frame, bg=BG_PANEL)
            graph_frame.pack(fill="both", expand=True, pady=10)
            def show_graphs():
                global curser,conn
                for widget in graph_frame.winfo_children():
                    widget.destroy()
                curser.execute("SELECT Category, SUM(Stock) FROM Products GROUP BY Category")
                cat_data = curser.fetchall()
                curser.execute("SELECT Name, Stock FROM Products ORDER BY Stock DESC LIMIT 10")
                top_stock = curser.fetchall()
                if cat_data:
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=BG_PANEL)
                    categories = [x[0] or "Uncategorized" for x in cat_data]
                    stocks = [x[1] for x in cat_data]
                    ax1.bar(categories, stocks, color=C_PRIMARY)
                    ax1.set_title("Stock by Category", fontsize=12, color=TEXT_PRIMARY, fontweight='bold')
                    ax1.set_ylabel("Stock", color=TEXT_PRIMARY)
                    ax1.tick_params(colors=TEXT_PRIMARY)
                    ax1.set_facecolor(BG_PANEL)
                    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    if top_stock:
                        names = [x[0][:15] for x in top_stock]
                        stocks_list = [x[1] for x in top_stock]
                        ax2.barh(names, stocks_list, color=C_SUCCESS)
                        ax2.set_title("Top 10 Most Stocked", fontsize=12, color=TEXT_PRIMARY, fontweight='bold')
                        ax2.set_xlabel("Stock", color=TEXT_PRIMARY)
                        ax2.tick_params(colors=TEXT_PRIMARY)
                        ax2.set_facecolor(BG_PANEL)
                    plt.tight_layout()
                    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
            refresh_button = Button(main_frame, text='Refresh Dashboard', command=show_graphs, bg=C_PRIMARY, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold"))
            refresh_button.pack(pady=10)
            show_graphs()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def add_tab():
        tab = ttk.Frame(tabs)
        tabs.add(tab,text='Add Products')
        content = Frame(tab,bg =BG_PANEL)
        content.pack(fill="both",expand=True,padx=10,pady=10)
        content.grid_columnconfigure(0,weight =1)
        labels = ["Products Name:","Category:","Cost (₹):","Stock:","Supplier:","Reorder Level:"]
        entries =[]
        catagories =["Electronic","Beauty Product","Sports & Fitness","Books & Stationery","Cloths","Groceries","Other"]
        for i,text in enumerate(labels):
            lbl = Label(content,text =text,font=("Helvetica",14,'bold'),bg =BG_PANEL,fg =TEXT_PRIMARY)
            lbl.grid(row=i*2,column=0,sticky='w',pady =(10,2))
            if text == "Category:":
                category_var = StringVar(value=catagories[0])
                category_combo= ttk.Combobox(content,values=catagories,textvariable=category_var,state="readonly",font=("Helvetica",13))
                category_combo.grid(row=i*2+1,column=0,sticky='ew',ipadx=8,ipady=8,pady=(0,10))
                entries.append(category_var)
            else:
                ent = Entry(content,font=("Helvetica",13),relief="flat",bg=INPUT_BG)
                ent.grid(row=i*2+1,column=0,sticky='ew',ipadx=8,ipady=8,pady=(0,10))
                entries.append(ent)
        def add_data():
            global conn,curser
            try:
                name = entries[0].get().strip()
                category = entries[1].get()
                cost = float(entries[2].get()or 0)
                stock = int(entries[3].get()or 0)
                supplier = entries[4].get().strip()
                reorder = int(entries[5].get()or 0)
                price = cost + cost * 0.18
                if not name:
                    messagebox.showwarning("Input Error","Products Name is required!")
                    return
                barcode = generate_barcode()
                curser.execute('''
                    insert into Products(name,category,Cost,Price,stock,supplier,reorder,barcode)
                    values(?,?,?,?,?,?,?,?)''',(name,category,cost,price,stock,supplier,reorder,barcode))
                conn.commit()
                messagebox.showinfo("Success",f"Products '{name}' added! Barcode: {barcode}")
                entries[0].delete(0,END)
                entries[1].set(catagories[0])
                entries[2].delete(0,END)
                entries[3].delete(0,END)
                entries[4].delete(0,END)
                entries[5].delete(0,END)
            except ValueError:
                messagebox.showerror("Invalid Input","Cost and Stock must be numbers!")
            except sql.Error as e:
                messagebox.showerror("Database Error",str(e))
        btn = Button(content,text="Add Products",command=add_data,
                    bg=C_SUCCESS,fg=TEXT_PRIMARY,font=("Helvetica",14,"bold"),pady=10)
        btn.grid(row =12,column=0,pady=20,sticky='ew')
    def show_table():
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="View Products")
        frame = Frame(tab, bg=BG_PANEL)
        frame.pack(fill="both", expand=True, padx=10, pady=15)
        search_frame = Frame(frame, bg=BG_PANEL)
        search_frame.pack(fill="x", pady=(0, 10))
        Label(search_frame,text='Search:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        search_var = StringVar()
        search_entry = Entry(search_frame,textvariable=search_var,font=("Helvetica",11))
        search_entry.pack(side='left',padx=5,fill='x',expand=True)
        Label(search_frame,text='Filter By:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        filter_var = StringVar(value='Name')
        filter_combo = ttk.Combobox(search_frame,textvariable=filter_var,values=['Name','Category','Supplier','Cost','Stock'],state='readonly',width=15)
        filter_combo.pack(side='left',padx=5)
        Label(search_frame,text='Sort By:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        sort_var = StringVar(value='Id')
        sort_combo = ttk.Combobox(search_frame,textvariable=sort_var,values=['Name','Cost','Stock'],state='readonly',width=15)
        sort_combo.pack(side='left',padx=5)
        low_stock_var = BooleanVar()
        low_stock_check = Checkbutton(search_frame,text='Low Stock',variable=low_stock_var,bg=BG_PANEL,fg=TEXT_PRIMARY)
        low_stock_check.pack(side='left',padx=5)
        style=ttk.Style()
        style.configure("Treeview",font = ("Helvetica",11,"bold"),rowheight=25,background=C_SNOW,fieldbackground=C_SNOW,foreground="#000000")
        style.configure("Treeview.Heading",font = ("Helvetica",12,'bold'),background="aliceblue",foreground="#000000") 
        tree = ttk.Treeview(frame,columns=('ID','Name','Category','Cost','Price','Stock','Supplier','Reorder','Barcode'),show='headings',style="Treeview")
        cols =['ID','Name','Category','Cost','Price','Stock','Supplier','Reorder','Barcode']
        widths =[50,100,150,80,80,70,100,80,120]
        anchors =['center','w','w','e','e','center','w','center','center' ]
        for col,width,anchor in zip(cols,widths,anchors):
            tree.heading(col,text=col)
            tree.column(col,width=width,anchor=anchor)
        tree.pack(fill='both',expand=True,pady=(10,10))                                                                        
        def load_data():
            global conn,curser
            for item in tree.get_children():
                tree.delete(item)
            try:
                search_term = search_var.get().strip()
                filter_type = filter_var.get()
                sort_type = sort_var.get()
                low_stock_only = low_stock_var.get()
                query = "SELECT * FROM Products where 1=1"
                params = []
                conditions = []
                if search_term:
                    filter_map = {"Name": "Name", "Category": "Category", "Supplier": "Supplier", "Cost": "Cost", "Stock": "Stock"}
                    conditions.append(f"{filter_map[filter_type]} LIKE %s")
                    params.append(f"%{search_term}%")
                if low_stock_only:
                    conditions.append("Stock <= Reorder")
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                sort_map = {"Name": "Name", "Cost": "Cost", "Stock": "Stock"}
                # Primary sort by selected field, secondary stable sort by id ASC
                if sort_type in sort_map:
                    query += f" ORDER BY {sort_map[sort_type]} ASC, id ASC"
                else:
                    query += " ORDER BY id ASC"
                curser.execute(query, params)
                rows = curser.fetchall()
                for row in rows:
                    try:
                        stock_val = int(row[5]) if row[5] is not None else 0
                        reorder_val = int(row[7]) if row[7] is not None else 0
                        tag = "low_stock" if stock_val <= reorder_val else ""
                    except (ValueError, TypeError):
                        tag = ""
                    tree.insert("", END, values=row, tags=(tag,))
                tree.tag_configure("low_stock", background=C_DANGER, foreground=TEXT_PRIMARY)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        load_data()
        button_frame = Frame(frame, bg=BG_PANEL)
        button_frame.pack(fill="x", pady=10)
        Button(button_frame, text="Search/Filter", command=load_data, bg=C_PRIMARY, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        def delete_product():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select a product to delete!")
                return
            item = tree.item(selected[0])
            product_id = item['values'][0]
            if messagebox.askyesno("Confirm", "Delete this product?"):
                try:
                    curser.execute("DELETE FROM Products WHERE id = ?", (product_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Products deleted!")
                    load_data()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        Button(button_frame, text="Delete Selected", command=delete_product, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        def bulk_delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select products to delete!")
                return
            if messagebox.askyesno("Confirm", f"Delete {len(selected)} products?"):
                try:
                    for item in selected:
                        product_id = tree.item(item)['values'][0]
                        curser.execute("DELETE FROM Products WHERE id = ?", (product_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Deleted {len(selected)} products!")
                    load_data()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        Button(button_frame, text="Bulk Delete", command=bulk_delete, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        Button(button_frame, text="Refresh", command=load_data, bg=C_SUCCESS, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
    def import_data():
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Import Data")
        content = Frame(tab, bg=BG_PANEL)
        content.pack(fill="both", expand=True, padx=10, pady=10)
        content.grid_columnconfigure(0, weight=1)
        Label(content,text="Import Products table From Csv",font=("Helventica",18,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(pady=20)
        def import_csv():
            global conn,curser
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files","*csv")])
            if not file_path:
                return
            try:
                with open(file_path,"r") as f:
                    reader = csv.reader(f)
                    count =0
                    for row in reader:
                        if len(row)>=8:
                            try:
                                barcode =row[8] if len(row)>8 else generate_barcode()
                                curser.execute('''
                                    insert into Products values(?, ?, ?, ?, ?, ?, ?)''',(row[1], row[2], float(row[3]), int(row[4]), row[5], int(row[6]), barcode))
                                count+=1
                            except Exception:
                                continue
                conn.commit()
                messagebox.showinfo("Success",f"Imported {count} Products")
            except Exception as e:
                messagebox.showerror("Error",str(e))
        Button(content,text="Select CSV File",command=import_csv,bg=C_PRIMARY,fg=TEXT_PRIMARY,font=("bold"),pady=12).pack(fill="x",pady=10)
    def update_table():
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Update Table")
        content = Frame(tab,bg=BG_PANEL)
        content.pack(fill="both",expand=True,padx=10,pady=10)
        content.grid_columnconfigure(0,weight=1)
        Label(content,text ="Id",font=("Helvetica",14,'bold'),bg =BG_PANEL,fg =TEXT_PRIMARY).pack(pady=(10,2))
        id_entry =Entry(content,font=("Helvetica",13),bg=INPUT_BG,relief="flat")
        id_entry.pack(fill="x",ipadx=8,ipady=8,pady=(0,10))
        Label(content,text="Cost",font=("Helventica",14,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(pady=(10,2))
        price_entry =Entry(content,font=("Helvetica",13),bg=INPUT_BG,relief="flat")
        price_entry.pack(fill="x",ipadx=8,ipady=8,pady=(0,10))
        Label(content,text="Stock",font=("Helventica",14,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(pady=(10,2))
        stock_entry =Entry(content,font=("Helvetica",13),bg=INPUT_BG,relief="flat")
        stock_entry.pack(fill="x",ipadx=8,ipady=8,pady=(0,10))
        Label(content,text="Reorder",font=("Helventica",14,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(pady=(10,2))
        reorder_entry =Entry(content,font=("Helvetica",13),bg=INPUT_BG,relief="flat")
        reorder_entry.pack(fill="x",ipadx=8,ipady=8,pady=(0,10))
        def update_data():
            global conn,curser
            try:
                _id = id_entry.get()
                price = price_entry.get()
                stock = stock_entry.get()
                reorder = reorder_entry.get()
                if not _id:
                    messagebox.showwarning("Input Error","ID is required!")
                    return
                curser.execute("UPDATE Products SET cost=?,stock=?,reorder=? WHERE id=?",(price,stock,reorder,_id))
                conn.commit()
                messagebox.showinfo("Success","Data Updated!")
            except Exception as e:
                messagebox.showerror("Error",str(e))
        Button(content,text="Update Table",command=update_data,bg=C_PRIMARY,fg=TEXT_PRIMARY,font=("bold"),pady=12).pack(fill="x",pady=10)
    def Export_data():
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Export Data")
        content = Frame(tab,bg=BG_PANEL)
        content.pack(fill="both",expand=True,padx=10,pady=10)
        content.grid_columnconfigure(0,weight=1)
        def export_csv():
            global conn,curser
            curser.execute("SELECT * FROM Products")
            rows = curser.fetchall()
            if not rows:
                messagebox.showwarning("Empty", "No data to export!")
                return
            filepath = filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[("CSV Files","*.csv")])
            if filepath:
                try:
                    with open(filepath,'w',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["ID","Name","Category","Cost","Price","Stock","Supplier","Reorder","Barcode"])
                        writer.writerows(rows)
                        messagebox.showinfo("Success","Exported to CSV")
                except Exception as e:
                    messagebox.showerror("Error",str(e))
        def export_excel():
            from openpyxl import Workbook
            global conn,curser
            curser.execute("SELECT * FROM Products")
            rows = curser.fetchall()
            if not rows:
                messagebox.showwarning("Empty", "No data to export!")
                return
            filepath = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[("Excel Files","*.xlsx")])
            if filepath:
                try:
                    wb = Workbook()
                    ws = wb.active
                    ws.title="Products"
                    ws.append(["ID","Name","Category","Cost","Price","Stock","Supplier","Reorder","Barcode"])
                    for rows in rows:
                        ws.append(rows)
                    wb.save(filepath)
                    messagebox.showinfo("Success","Exported to Excel")
                except ImportError:
                    messagebox.showerror("Error", "Install openpyxl: pip install openpyxl")
                except Exception as e:
                    messagebox.showerror("Error",str(e))
        def export_pdf():
            try:
                from reportlab.lib.pagesizes import letter, landscape
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                global conn,curser
                curser.execute("select * from Products")
                rows = curser.fetchall()
                if not rows:
                    messagebox.showwarning("Empty","No data to export!")
                    return
                filepath = filedialog.asksaveasfilename(defaultextension='.pdf',filetypes=[("PDF Files","*.pdf")])
                if filepath:
                    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
                    elements = []
                    title = Paragraph("Store Inventory Report", getSampleStyleSheet()['Title'])
                    elements.append(title)
                    data = [["ID", "Name", "Category", "Cost", "Price", "Stock", "Supplier", "Reorder", "Barcode"]]
                    data.extend(rows)
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ]))
                    elements.append(table)
                    doc.build(elements)
                    messagebox.showinfo("Success", f"Exported to {filepath}")
            except ImportError:
                messagebox.showerror("Error", "Install reportlab: pip install reportlab")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        Label(content,text="Export Products table to CSV",font=("Helventica",18,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(pady=20)
        Button(content,text="Export to CSV",command=export_csv,bg=C_PRIMARY,fg=TEXT_PRIMARY,font=("bold"),pady=12).pack(fill="x",pady=10)
        Button(content,text="Export to Excel",command=export_excel,bg=C_SUCCESS,fg=TEXT_PRIMARY,font=("bold"),pady=12).pack(fill="x",pady=10)
        Button(content,text="Export to PDF",command=export_pdf,bg=C_WARN,fg=TEXT_PRIMARY,font=("bold"),pady=12).pack(fill="x",pady=10)
    def mange_Supplier():
        tab = ttk.Frame(tabs)
        tabs.add(tab,text='Manage Supplier')
        frame = Frame(tab,bg=BG_PANEL)
        frame.pack(fill="both",expand=True,padx=10,pady=10)
        from_frame = Frame(frame,bg=BG_APP)
        from_frame.pack(fill="x",pady=(0,15))
        Label(from_frame,text="Name:",bg=BG_APP,fg=TEXT_PRIMARY,font=("Helvetica",12,"bold")).grid(row=0,column=0,sticky="w",padx=5,pady=5)
        name_entry=Entry(from_frame,font=("Helvetica",12),relief="flat",bg=INPUT_BG)
        name_entry.grid(row=0,column=1,sticky="ew",padx=5,pady=5)
        Label(from_frame,text="Contact No:",bg=BG_APP,fg=TEXT_PRIMARY,font=("Helvetica",12,"bold")).grid(row=0,column=2,sticky="w",padx=5,pady=5)
        contact_entry=Entry(from_frame,font=("Helvetica",12),relief="flat",bg=INPUT_BG)
        contact_entry.grid(row=0,column=3,sticky="ew",padx=5,pady=5)
        Label(from_frame,text="Email",bg=BG_APP,fg=TEXT_PRIMARY,font=("Helvetica",12,"bold")).grid(row=1,column=0,sticky="w",padx=5,pady=5)
        email_entry=Entry(from_frame,font=("Helvetica",12),relief="flat",bg=INPUT_BG)
        email_entry.grid(row=1,column=1,sticky="ew",padx=5,pady=5)
        Label(from_frame,text="Address",bg=BG_APP,fg=TEXT_PRIMARY,font=("Helvetica",12,"bold")).grid(row=1,column=2,sticky="w",padx=5,pady=5)
        address_entry=Entry(from_frame,font=("Helvetica",12),relief="flat",bg=INPUT_BG)
        address_entry.grid(row=1,column=3,sticky="ew",padx=5,pady=5)
        from_frame.grid_columnconfigure(1,weight=1)
        from_frame.grid_columnconfigure(3,weight=1)
        style =ttk.Style()
        style.configure("Treeview",background = C_SNOW,fieldbackground=C_SNOW,foreground="#000000",bordercolor=BORDER,lightcolor=BORDER,darkcolor=BORDER)
        tree = ttk.Treeview(frame,columns=("ID","Name","Contact","Email","Address"),show='headings',style="Treeview")
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor='center')
        tree.heading("Name", text="Supplier Name")
        tree.column("Name", width=200, anchor='w')
        tree.heading("Contact", text="Contact")
        tree.column("Contact", width=150, anchor='w')
        tree.heading("Email", text="Email")
        tree.column("Email", width=200, anchor='w')
        tree.heading("Address", text="Address")
        tree.column("Address", width=300, anchor='w')
        tree.pack(fill="both", expand=True, pady=10)
        def load_supplier():
            global conn,curser
            for item in tree.get_children():
                tree.delete(item)
            try:
                curser.execute("SELECT * FROM supplier")
                rows = curser.fetchall()
                for row in rows:
                    tree.insert("",END,values=row)
            except Exception as e:
                messagebox.showerror("Error",str(e))
        load_supplier()
        def add_supplier():
            global conn,curser
            name = name_entry.get().strip()
            contact = contact_entry.get()
            email = email_entry.get().strip()
            address = address_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error","Supplier Name is required!")
                return
            try:
                curser.execute('''
                    insert into supplier(name,contact,email,address)
                    values(?,?,?,?)''',(name,contact,email,address))
                conn.commit()
                messagebox.showinfo("Success",f"Supplier '{name}' added!")
                name_entry.delete(0,END)
                contact_entry.delete(0,END)
                email_entry.delete(0,END)
                address_entry.delete(0,END)
                load_supplier()
            except sql.IntegrityError:
                messagebox.showerror("Error","Supplier already exists!")
            except Exception as e:
                messagebox.showerror("Error",str(e))
        def delete_supplier():
            global conn,curser
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select","Select a supplier to delete!")
                return
            supplier_id = tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Confirm","Delete this supplier?"):
                curser.execute("DELETE FROM supplier WHERE id = ?",(supplier_id,))
                conn.commit()
                messagebox.showinfo("Success","Supplier deleted!")
                load_supplier()
        btn_frame = Frame(frame, bg=BG_PANEL)
        btn_frame.pack(fill="x", pady=10)
        Button(btn_frame, text="Add Supplier", command=add_supplier, bg=C_SUCCESS, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        Button(btn_frame, text="Delete Selected", command=delete_supplier, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
    def analyze_table():
        for i in range(len(tabs.tabs())):
            if tabs.tab(i, "text") == "Advanced Analytics":
                tabs.forget(i)
                break
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Advanced Analytics")
        ctrl_frame = Frame(tab, bg=BG_PANEL)
        ctrl_frame.pack(fill="both", side="bottom", padx=10, pady=10)
        graph_frame = Frame(tab, bg=BG_PANEL)
        graph_frame.pack(fill="both", expand=True, padx=10)
        def show_graphs():
            global conn,curser
            for widget in graph_frame.winfo_children():
                widget.destroy()
            try:
                curser.execute("SELECT Name, Price FROM Products ORDER BY Price ASC LIMIT 10")
                cheapest = curser.fetchall()
                curser.execute("SELECT Name, Stock FROM Products ORDER BY Stock DESC LIMIT 10")
                top_stock = curser.fetchall()
                curser.execute("SELECT Category, SUM(Stock) FROM Products GROUP BY Category")
                category_stock = curser.fetchall()
                curser.execute("SELECT Category, COUNT(*) FROM Products GROUP BY Category")
                category_count = curser.fetchall()
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10), facecolor=BG_PANEL)
                if cheapest:
                    names = [x[0][:12] for x in cheapest]
                    prices = [x[1] for x in cheapest]
                    ax1.barh(names, prices, color=C_WARN)
                    ax1.set_title("Top 10 Cheapest Products", fontsize=11, color=TEXT_PRIMARY, fontweight='bold')
                    ax1.set_xlabel("Price (₹)", color=TEXT_PRIMARY)
                    ax1.tick_params(colors=TEXT_PRIMARY)
                    ax1.set_facecolor(BG_PANEL)
                if top_stock:
                    names = [x[0][:12] for x in top_stock]
                    stocks = [x[1] for x in top_stock]
                    ax2.bar(names, stocks, color=C_SUCCESS)
                    ax2.set_title("Top 10 Most Stocked Items", fontsize=11, color=TEXT_PRIMARY, fontweight='bold')
                    ax2.set_ylabel("Stock", color=TEXT_PRIMARY)
                    ax2.tick_params(colors=TEXT_PRIMARY)
                    ax2.set_facecolor(BG_PANEL)
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                if category_stock:
                    categories = [x[0] or "Uncategorized" for x in category_stock]
                    stocks = [x[1] for x in category_stock]
                    ax3.pie(stocks, labels=categories, autopct='%1.1f%%', colors=CHART_COLORS[:len(stocks)], textprops={'color': TEXT_PRIMARY})
                    ax3.set_title("Stock Distribution by Category", fontsize=11, color=TEXT_PRIMARY, fontweight='bold')
                    ax3.set_facecolor(BG_PANEL)
                if category_count:
                    categories = [x[0] or "Uncategorized" for x in category_count]
                    counts = [x[1] for x in category_count]
                    ax4.bar(categories, counts, color=C_PRIMARY)
                    ax4.set_title("Products per Category", fontsize=11, color=TEXT_PRIMARY, fontweight='bold')
                    ax4.set_ylabel("Count", color=TEXT_PRIMARY)
                    ax4.tick_params(colors=TEXT_PRIMARY)
                    ax4.set_facecolor(BG_PANEL)
                    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Chart error:\n{e}")
        Button(ctrl_frame, text='Refresh Analytics', command=show_graphs, bg=C_PRIMARY, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(pady=10)
        show_graphs()
    show_dashboard()
    add_tab()  
    show_table()
    update_table()
    import_data()
    Export_data()
    mange_Supplier()
    analyze_table()
def customer():
    customer_frame = Frame(root, bg=BG_APP)
    customer_frame.pack(fill="both", expand=True)
    header_frame = Frame(customer_frame, bg=BG_PANEL, height=50)
    header_frame.pack(fill="x", side="top")
    Label(header_frame, text="Customer Dashboard", font=("Helvetica", 14, "bold"), bg=BG_PANEL, fg=TEXT_PRIMARY).pack(side="left", padx=20, pady=10)
    Button(header_frame, text="Logout", command=lambda: logout(customer_frame), bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 10, "bold")).pack(side="right", padx=20, pady=10)
    tabs = ttk.Notebook(customer_frame)
    tabs.pack(expand=1, fill="both", padx=10, pady=10)
    def show_table():
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="View Products")
        frame = Frame(tab, bg=BG_PANEL)
        frame.pack(fill="both", expand=True, padx=10, pady=15)
        search_frame = Frame(frame, bg=BG_PANEL)
        search_frame.pack(fill="x", pady=(0, 10))
        Label(search_frame,text='Search:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        search_var = StringVar()
        search_entry = Entry(search_frame,textvariable=search_var,font=("Helvetica",11))
        search_entry.pack(side='left',padx=5,fill='x',expand=True)
        Label(search_frame,text='Filter By:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        filter_var = StringVar(value='Name')
        filter_combo = ttk.Combobox(search_frame,textvariable=filter_var,values=['Name','Category','Supplier','Cost','Stock'],state='readonly',width=15)
        filter_combo.pack(side='left',padx=5)
        Label(search_frame,text='Sort By:',font=("Helvetica",11,"bold"),bg=BG_PANEL,fg=TEXT_PRIMARY).pack(side='left',padx=5)
        sort_var = StringVar(value='Name')
        sort_combo = ttk.Combobox(search_frame,textvariable=sort_var,values=['Name','Cost','Stock'],state='readonly',width=15)
        sort_combo.pack(side='left',padx=5)
        low_stock_var = BooleanVar()
        low_stock_check = Checkbutton(search_frame,text='Low Stock',variable=low_stock_var,bg=BG_PANEL,fg=TEXT_PRIMARY)
        low_stock_check.pack(side='left',padx=5)
        tree = ttk.Treeview(frame,columns=('ID','Name','Category','Price','Stock','Supplier','Reorder','Barcode'),show='headings',style="Treeview")
        cols =['ID','Name','Category','Price','Stock','Supplier','Reorder','Barcode']
        widths =[50,100,150,80,70,100,80,120]
        anchors =['center','w','w','e','center','w','center','center' ]
        for col,width,anchor in zip(cols,widths,anchors):
            tree.heading(col,text=col)
            tree.column(col,width=width,anchor=anchor)
        tree.pack(fill='both',expand=True,pady=(10,10))                                                                        
        def load_data():
            global conn,curser
            for item in tree.get_children():
                tree.delete(item)
            try:
                search_term = search_var.get().strip()
                filter_type = filter_var.get()
                sort_type = sort_var.get()
                low_stock_only = low_stock_var.get()
                query = "SELECT id, Name, Category, Price, Stock, Supplier, Reorder, Barcode FROM Products WHERE 1=1"
                params = []

                if search_term:
                    filter_map = {
                        "Name": "Name",
                        "Category": "Category",
                        "Supplier": "Supplier",
                        "Price": "Price",
                        "Stock": "Stock"
                    }
                    query += f" AND {filter_map[filter_type]} LIKE ?"
                    params.append(f"%{search_term}%")

                if low_stock_only:
                    query += " AND Stock <= Reorder"

                sort_map = {"Name": "Name", "Price": "Price", "Stock": "Stock"}
                query += f" ORDER BY id ASC"
                curser.execute(query,params)
                rows = curser.fetchall()
                for row in rows:
                    try:
                        stock_val = int(row[4]) if row[4] is not None else 0
                        reorder_val = int(row[6]) if row[6] is not None else 0
                        tag = "low_stock" if stock_val <= reorder_val else ""
                    except (ValueError, TypeError):
                        tag = ""
                    tree.insert("", END, values=row, tags=(tag,))
                tree.tag_configure("low_stock", background=C_DANGER, foreground=TEXT_PRIMARY)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        load_data()
        button_frame = Frame(frame, bg=BG_PANEL)
        button_frame.pack(fill="x", pady=10)
        Button(button_frame, text="Search/Filter", command=load_data, bg=C_PRIMARY, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        def delete_product():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select a product to delete!")
                return
            item = tree.item(selected[0])
            product_id = item['values'][0]
            if messagebox.askyesno("Confirm", "Delete this product?"):
                try:
                    curser.execute("DELETE FROM Products WHERE id = ?", (product_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Products deleted!")
                    load_data()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        Button(button_frame, text="Delete Selected", command=delete_product, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        def bulk_delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Select products to delete!")
                return
            if messagebox.askyesno("Confirm", f"Delete {len(selected)} products?"):
                try:
                    for item in selected:
                        product_id = tree.item(item)['values'][0]
                        curser.execute("DELETE FROM Products WHERE id = ?", (product_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Deleted {len(selected)} products!")
                    load_data()
                except Exception as e:
                    messagebox.showerror("Error", str(e)) 
        Button(button_frame, text="Bulk Delete", command=bulk_delete, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        Button(button_frame, text="Refresh", command=load_data, bg=C_SUCCESS, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
    def sales():
        tab = ttk.Frame(tabs)
        tabs.add(tab,text='Sales')
        frame= Frame(tab,bg=BG_APP)
        frame.pack(fill="both",expand=True,padx=15,pady=15)
        top_frame = Frame(frame,bg=BG_APP)
        top_frame.pack(fill="x",pady=(0,10))
        Label(top_frame, text="Customer name:", font=("Helvetica", 14, 'bold'), bg=BG_APP, fg=TEXT_PRIMARY).pack(side="left", padx=5)
        name_entry = Entry(top_frame, font=("Helvetica", 11), bg=INPUT_BG, width=20)
        name_entry.pack(side="left", padx=5)
        Label(top_frame, text="Product ID / Name:", font=("Helvetica", 11, 'bold'), bg=BG_APP, fg=TEXT_PRIMARY).pack(side="left", padx=5)
        product_entry = Entry(top_frame, font=("Helvetica", 11), bg=INPUT_BG, width=20)
        product_entry.pack(side="left", padx=5)
        Label(top_frame, text="Quantity:", font=("Helvetica", 11, 'bold'), bg=BG_APP, fg=TEXT_PRIMARY).pack(side="left", padx=5)
        qty_entry = Entry(top_frame, font=("Helvetica", 11), bg=INPUT_BG, width=10)
        qty_entry.pack(side="left", padx=5)      
        tree = ttk.Treeview(frame, columns=("Custome name","Product", "Qty", "Price", "Total"), show='headings', style="Treeview")
        tree.heading("Custome name", text="Customer Name")
        tree.column("Custome name", width=150, anchor='w')
        tree.heading("Product", text="Product")
        tree.column("Product", width=150, anchor='w')
        tree.heading("Qty", text="Quantity")
        tree.column("Qty", width=80, anchor='center')
        tree.heading("Price", text="Price")
        tree.column("Price", width=80, anchor='center')
        tree.heading("Total", text="Total")
        tree.column("Total", width=80, anchor='center')
        tree.pack(fill="both", expand=True, pady=10)
        bill_frame = Frame(frame, bg=BG_PANEL)
        bill_frame.pack(fill="x", pady=10)
        summary_label = Label(bill_frame, text="Total: Rs.", font=("Helvetica", 14, 'bold'), bg=BG_APP, fg=C_SUCCESS)
        summary_label.pack(side="left", padx=20)
        cart_items = []
        def add_to_cart():
            customer = name_entry.get().strip()
            product_search = product_entry.get().strip()
            try:
                qty = int(qty_entry.get().strip())
                if qty <= 0:
                    messagebox.showwarning("Invalid", "Quantity must be positive!")
                    return
            except ValueError:
                messagebox.showwarning("Invalid", "Enter valid quantity!")
                return
            try:
                curser.execute("SELECT id, Name, Price, Stock FROM Products WHERE id = ? OR Name LIKE ?", (product_search if product_search.isdigit() else -1, f"%{product_search}%"))
                product = curser.fetchone()
                if not product:
                    messagebox.showwarning("Not Found", "Product not found!")
                    return
                if product[3] < qty:
                    messagebox.showwarning("Stock", f"Insufficient stock! Available: {product[3]}")
                    return
                cart_items.append((customer,product[0], product[1], product[2], qty))
                refresh_cart()
                product_entry.delete(0, END)
                qty_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        def refresh_cart():
            for item in tree.get_children():
                tree.delete(item)            
            total = 0
            for customer,pid, name, price, qty in cart_items:
                item_total = price * qty
                total += item_total
                tree.insert("", END, values=(customer, name, qty, f"Rs.{price:.2f}", f"Rs.{item_total:.2f}"))
            summary_label.config(text=f"Total: Rs.{total:.2f}")
        def remove_item():
            selected = tree.selection()
            if selected:
                index = tree.index(selected[0])
                cart_items.pop(index)
                refresh_cart()
        def checkout():
            if not os.path.exists("invoices"):
                os.makedirs("invoices")

            def start_local_server():
                try:
                    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
                    server.serve_forever()
                except:
                    pass
            threading.Thread(target=start_local_server, daemon=True).start()
            def get_local_ip():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    ip = s.getsockname()[0]
                except:
                    ip = '127.0.0.1'
                finally:
                    s.close()
                return ip
            def generate_invoice_pdf(customer, cart_items, total_amount):
                file_name = f"Invoice_{customer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                invoice_dir = os.path.join(os.getcwd(), "invoices")
                os.makedirs(invoice_dir, exist_ok=True)
                file_path = os.path.join(invoice_dir, file_name)
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                y = height - 50
                c.setFont("Helvetica-Bold", 20)
                c.drawString(200, y, "INVOICE")
                y -= 40
                c.setFont("Helvetica", 11)
                c.drawString(50, y, f"Customer Name: {customer}")
                y -= 20
                c.drawString(50, y, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
                y -= 40
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Items")
                y -= 20
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "Product")
                c.drawString(250, y, "Qty")
                c.drawString(300, y, "Price")
                c.drawString(380, y, "Total")           
                y -= 15
                c.line(50, y, 500, y)            
                c.setFont("Helvetica", 10)
                for _, _, name, price, qty in cart_items:
                    y -= 20
                    c.drawString(50, y, name)
                    c.drawString(250, y, str(qty))
                    c.drawString(300, y, f"Rs.{price}")
                    c.drawString(380, y, f"Rs.{price * qty}")         
                    if y < 100:
                        c.showPage()
                        y = height - 50
                y -= 30
                c.setFont("Helvetica-Bold", 12)
                c.drawString(300, y, f"Total Amount: Rs.{total_amount}")            
                c.save()            
                return file_path, file_name
            def show_invoice_qrcode(pdf_filename):
                ip = get_local_ip()
                url = f"http://{ip}:8000/invoices/{pdf_filename}"
                qr = qrcode.make(url)
                qr = qr.resize((280, 280))
                win = Toplevel(root)
                win.title("Invoice QR Code")
                win.config(bg=BG_APP)
                img = ImageTk.PhotoImage(qr)
                Label(win, image=img, bg="#f0f0f0").pack(pady=20)
                win.image = img
            if not cart_items:
                messagebox.showwarning("Empty", "Cart is empty!")
                return
            try:
                customer = cart_items[0][0]
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
                total_amount = sum(price * qty for _, _, _, price, qty in cart_items)
                items_text = "\n".join(
                    [f"{name} x {qty} = Rs{price * qty}"
                        for _, _, name, price, qty in cart_items])
                invoice_text = (
                    f"INVOICE\n"
                    f"Customer: {customer}\n"
                    f"Date: {date_time}\n\n"
                    f"Items:\n{items_text}\n\n"
                    f"Total Amount: Rs.{total_amount}")
                curser.execute(
                    "INSERT INTO Sales (Customer_Name, Date, TotalAmount, Items) VALUES (?, ?, ?, ?)",
                    (customer, date_time, total_amount, items_text))
                for _, pid, _, _, qty in cart_items:
                    curser.execute(
                        "UPDATE Products SET Stock = Stock - ? WHERE id = ?",
                        (qty, pid))
                conn.commit()
                messagebox.showinfo("Success", "Invoice Generated Successfully!")
                pdf_path, pdf_name = generate_invoice_pdf(customer, cart_items, total_amount)
        
                os.startfile(pdf_path)
                show_invoice_qrcode(pdf_name)
        
                cart_items.clear()
                refresh_cart()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        btn_frame = Frame(frame, bg=BG_PANEL)
        btn_frame.pack(fill="x", pady=10)

        Button(btn_frame, text="Add to Cart", command=add_to_cart, bg=C_PRIMARY, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        Button(btn_frame, text="Remove Item", command=remove_item, bg=C_DANGER, fg=TEXT_PRIMARY, font=("Helvetica", 11, "bold")).pack(side="left", padx=5)
        Button(btn_frame, text="Checkout", command=checkout, bg=C_SUCCESS, fg=TEXT_PRIMARY, font=("Helvetica", 12, "bold")).pack(side="left", padx=5)

    show_table()
    sales()

def about():
    messagebox.showinfo(
        "Information",
        "For user login\nuserid = user\npassword = user\n\n"
        "For admin login\nuserid = admin\npassword = admin"
    )
h.add_command(label='About', command=about)
try:
    img = Image.open(r"hello1.jpg")
    img = img.resize((1200, 750))
    blur_img = img.filter(ImageFilter.GaussianBlur(2))
    bg_photo = ImageTk.PhotoImage(blur_img)
    Label(root, image=bg_photo).place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    Label(root, bg=BG_APP).place(x=0, y=0, relwidth=1, relheight=1)
glass = Frame(root, bg="#f5f5f5", padx=25, pady=25)
glass.place(relx=0.5, rely=0.5, anchor=CENTER)
Label(glass, text="LOGIN",
      font=("Helvetica", 18, "bold"),
      bg="#f5f5f5").pack(pady=10)
Label(glass, text="User ID",
      font=("Helvetica", 13, "bold"),
      bg="#f5f5f5").pack(anchor="w")
user = Entry(glass, width=25, font=("Helvetica", 12, "bold"))
user.pack(pady=10)
Label(glass, text="Password",
      font=("Helvetica", 13, "bold"),
      bg="#f5f5f5").pack(anchor="w")
pwd = Entry(glass, show="*", width=25, font=("Helvetica", 12, "bold"))
pwd.pack(pady=10)
def login():
    if user.get() == "admin" and pwd.get() == "admin":
        messagebox.showinfo("Login", "Login Successful")
        glass.place_forget()
        manager()
    elif user.get() == "user" and pwd.get() == "user":
        messagebox.showinfo("Login", "Login Successful")
        glass.place_forget()
        customer()
    else:
        messagebox.showerror("Login", "Login Failed")
Button(glass, text="Login",
       font=("Helvetica", 13, "bold"),
       bg="#2563eb", fg="white",
       width=18,
       command=login).pack(pady=15)
root.mainloop()
