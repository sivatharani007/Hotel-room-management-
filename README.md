# GrandStay Hotel Room Management System
**Smart Hotel Booking, Dynamic Room Availability, and Automated Billing Management Website**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow.svg)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4%2B-ff6384.svg)

---

## 1. Project Overview

The **GrandStay Hotel Room Management System** is a full-stack web application designed for commercial hotel operations and college mini-project demonstrations.

This project represents the modern web conversion of a classic **Java / JavaFX / JDBC desktop application** into a responsive, browser-accessible architecture using **Python Flask, MySQL, HTML5, CSS3, JavaScript, and Chart.js**.

### Key Automated Capabilities:
- **Real-Time Operational Dashboard:** 8 real-time database counters and 4 interactive Chart.js visualizations (Occupancy Doughnut, Revenue Bars, Booking Trends, Room Type Distribution).
- **Comprehensive Room Management:** Color-coded room cards, grid & table view toggle, filtering by room type and status, price sorting, and safe deletion protection.
- **Guest & Customer Management:** Registration with email/phone format validation, duplicate detection, and instant booking history lookup.
- **11-Step Concurrency-Safe Booking Wizard:** Atomic interval-based room availability checking preventing double bookings with database transactions and row-level locking.
- **Automatic Financial Billing:** Backend night calculation ($Nights \times Price$), tax calculation, payment status tracking (Pending, Paid, Refunded), and printable branded invoices.
- **Cancellation & Check-Out Management:** Dedicated status lifecycle workflows releasing rooms for new reservations while retaining full audit history.
- **Business Analytics & CSV Exports:** Occupancy rates, popular room types, and one-click CSV report exports.
- **College Mini-Project Presentation Section:** Interactive `/about` page featuring side-by-side Java vs. Web comparisons, workflow flowcharts, and architecture diagrams.

---

## 2. Complete Project Folder Structure

```text
hotel-room-management/
│
├── app.py                      # Flask application factory and entry point
├── config.py                   # Environment configuration loader
├── requirements.txt            # Python dependencies (Flask, PyMySQL, cryptography, etc.)
├── .env.example                # Template for environment variables
├── .env                        # Local credentials (create this from .env.example)
├── .gitignore                  # Keeps sensitive credentials and .venv out of git
├── README.md                   # Complete beginner setup and running guide
│
├── database/
│   ├── db.py                   # PyMySQL connection manager, DictCursor & transaction handling
│   └── schema.sql              # MySQL DDL script with tables, indexes, and demonstration seed data
│
├── models/
│   ├── __init__.py
│   ├── customer.py             # Customer database access and queries
│   ├── room.py                 # Room inventory, availability queries, and stats
│   ├── booking.py              # Transactional booking creation, cancellations, and checkouts
│   └── payment.py              # Billing, payment statuses, and invoice generation
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py            # Dashboard view and Chart.js API
│   ├── rooms.py                # Room CRUD and availability search API
│   ├── customers.py            # Customer registration, editing, and history API
│   ├── bookings.py             # Booking wizard, cancellation, and check-out routes
│   ├── billing.py              # Invoices, mark-as-paid, and dynamic calculation API
│   ├── reports.py              # Operational reports, charts API, and CSV exports
│   └── general.py              # About Project presentation and settings routes
│
├── services/
│   ├── __init__.py
│   ├── booking_service.py      # Business logic: date validation, concurrency safety, capacity checks
│   └── billing_service.py      # Financial formulas, tax computation, and invoice compilation
│
├── templates/
│   ├── base.html               # Master layout with navy sidebar, topbar, alerts, and modal system
│   ├── dashboard.html          # Stat cards, 4 Chart.js charts, and recent reservations table
│   ├── rooms.html              # Room grid cards & table view toggle, filters, add/edit modal
│   ├── customers.html          # Customer table, search, add/edit modal, history modal
│   ├── bookings.html           # 11-step interactive booking wizard modal & active reservations
│   ├── booking_history.html    # Full audit log with date filters, search, and invoice links
│   ├── billing.html            # Invoices list, mark paid modal, and print triggers
│   ├── invoice.html            # Printable branded invoice layout with print CSS
│   ├── reports.html            # Comprehensive reports, graphs, and CSV export triggers
│   ├── about.html              # College mini-project presentation view (Java vs Web, architecture)
│   ├── settings.html           # Hotel properties, live DB connection tester, and auto-init button
│   └── 404.html                # Friendly 404/500 error page
│
└── static/
    ├── css/
    │   └── style.css           # Premium hotel dashboard CSS, glassmorphism, responsive styles
    ├── js/
    │   ├── main.js             # Global utilities, toast notifications, mobile sidebar, modal engine
    │   ├── dashboard.js        # Dashboard Chart.js rendering & live updates
    │   ├── rooms.js            # Room view toggle, modals, and edit/delete handlers
    │   ├── customers.js        # Customer search, validation, modals, and history viewer
    │   ├── bookings.js         # 11-step booking wizard, live availability, nights/total calculation
    │   ├── billing.js          # Payment actions & print invoice triggers
    │   └── reports.js          # Reports Chart.js graphs and date range handling
    └── images/
        └── hotel-logo.svg      # GrandStay Hotel luxury SVG vector logo
```

---

## 3. Prerequisites

Before running the application on your Windows laptop, make sure you have installed:

1. **Python 3.9 or higher**: [Download from python.org](https://www.python.org/downloads/) (Make sure to check the box **"Add Python to PATH"** during installation).
2. **Visual Studio Code (VS Code)**: [Download from code.visualstudio.com](https://code.visualstudio.com/).
3. **MySQL Server**: You can use any of the following:
   - **XAMPP** (Recommended for beginners): [Download XAMPP](https://www.apachefriends.org/) (Includes MySQL and phpMyAdmin).
   - **WampServer** or **MySQL Community Server & Workbench**.

---

## 4. Step-by-Step Installation & Setup in VS Code

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File** &rarr; **Open Folder...**
3. Select the folder:
   ```text
   C:\Users\msiva\.gemini\antigravity-ide\scratch\hotel-room-management
   ```
4. Open the integrated terminal in VS Code:
   - Press <kbd>Ctrl</kbd> + <kbd>`</kbd> (Backtick) or click **Terminal** &rarr; **New Terminal**.
   - Ensure the terminal is running **PowerShell**.

---

### Step 2: Create a Python Virtual Environment
Run the following command in the VS Code PowerShell terminal:

```powershell
python -m venv .venv
```

---

### Step 3: Activate the Virtual Environment

#### Standard Activation:
```powershell
.\.venv\Scripts\Activate.ps1
```
*When activated, your terminal prompt will show `(.venv)` in front.*

#### Safe Alternative (If PowerShell blocks script execution):
If Windows shows a red error stating *"running scripts is disabled on this system"*, do **not** worry. You do not need to change any global Windows security policies. Simply use the virtual environment's Python executable directly:

```powershell
# Directly install dependencies using the venv python:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Directly run the app using the venv python:
.\.venv\Scripts\python.exe app.py
```

---

### Step 4: Install Required Python Packages
With your virtual environment active (or using the alternative command above), install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs:
- `Flask`: The core web framework.
- `PyMySQL`: High-performance, pure-Python MySQL connector.
- `cryptography`: Handles modern MySQL 8 authentication securely.
- `python-dotenv`: Loads `.env` configuration automatically.
- `Werkzeug`: Secure WSGI utility library.

---

### Step 5: Start MySQL & Create the Database

#### Option A: Using XAMPP (Easiest)
1. Open the **XAMPP Control Panel**.
2. Click the **Start** button next to **MySQL** (and Apache if you want to use phpMyAdmin).
3. Open your browser and go to: `http://localhost/phpmyadmin`
4. Click the **Import** tab at the top.
5. Click **Choose File**, browse to:
   ```text
   hotel-room-management/database/schema.sql
   ```
6. Scroll down and click **Import** (or **Go**).
7. The database `hotel_management` and all tables with demonstration data will be created!

#### Option B: Using MySQL Command Line
Open a PowerShell terminal and run:

```powershell
# If MySQL is in your PATH:
mysql -u root -p < database/schema.sql

# If you have no password (default in XAMPP), simply press Enter when prompted.
```

#### Option C: Built-in Auto-Init from the Website
If you start the Flask server first, you can navigate to `http://127.0.0.1:5000/settings` in your browser and click the gold button:
**"Auto-Initialize Database from schema.sql"**! The application will create the database and seed records for you automatically.

---

### Step 6: Configure Environment Credentials (`.env`)

1. In the project root, make a copy of `.env.example` and name it `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in VS Code.
3. Review and adjust your MySQL connection settings:
   ```ini
   # For standard XAMPP (User is 'root' and password is empty):
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=
   MYSQL_DB=hotel_management

   # If using MySQL Installer with a root password, enter it here:
   # MYSQL_PASSWORD=your_mysql_password
   ```

*(The `.env` file is protected by `.gitignore` so your personal database password will never be accidentally committed to GitHub).*

---

### Step 7: Run the Flask Web Application

In the VS Code terminal, start the server:

```powershell
python app.py
```
*(Or `.\.venv\Scripts\python.exe app.py` if not using activation).*

You will see the startup banner:
```text
=================================================================
🏨 GrandStay Hotel & Suites
   Smart Hotel Booking, Room Availability and Billing Management
=================================================================
✅ [Database] MySQL connection established successfully.
🚀 Server running on: http://127.0.0.1:5000
👉 Press Ctrl+C in terminal to stop.
=================================================================
```

---

### Step 8: View the Website in Your Browser

Open any web browser (Google Chrome, Microsoft Edge, Mozilla Firefox) and navigate to:

👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (or **[http://localhost:5000](http://localhost:5000)**)

---

## 5. Website Features Walkthrough

1. **Dashboard (`/`)**:
   - Live KPI statistic cards (Total Rooms, Available, Occupied, Total Bookings, Today's Check-ins & Check-outs, Customers, Total Revenue).
   - 4 Chart.js analytics graphs.
   - Recent Bookings table with status badges and quick invoice print actions.

2. **Rooms (`/rooms`)**:
   - Colorful cards displaying room capacity, nightly rates, and status (Green = Available, Red = Occupied, Orange = Maintenance).
   - Toggle between visual **Cards View** and **Table View**.
   - Filters for room type, availability status, and price sorting.
   - Add Room, Edit Room, and safe Delete Room modals.

3. **Customers (`/customers`)**:
   - Complete guest directory with contact info and identity document numbers.
   - Instant guest booking history modal displaying all past reservations.
   - Form validations for email and phone numbers to prevent duplicates.

4. **Bookings (`/bookings`)**:
   - **11-Step Interactive Booking Wizard**:
     - Step 1: Select/register guest, choose check-in & check-out dates, pick guest count.
     - Automatically checks room availability for the exact date range using server-side interval intersection logic.
     - Select available room card with live calculation of nights and total bill ($Nights \times Rate$).
     - Step 2: Review formatted booking receipt, select payment method, and confirm booking.
     - Generates unique reference code (e.g., `GS-20261020-A1B2`) and saves atomically in MySQL.
   - **Guest Check-Out Workflow**: Updates status to `CHECKED_OUT`, records completion timestamp, and releases room availability.
   - **Reservation Cancellation Workflow**: Updates status to `CANCELLED`, records cancellation timestamp, and updates room availability while retaining history.

5. **Booking History (`/booking-history`)**:
   - Complete archive of all past, checked-out, and cancelled reservations.
   - Date range filters ("From Date" to "To Date") and status filters.

6. **Billing & Invoices (`/billing`)**:
   - Financial ledger displaying all invoices, nights, daily rates, totals, and payment statuses (Pending, Paid, Refunded).
   - "Collect Payment" action to record payment receipts.
   - **Printable Branded Invoice (`/invoice/<id>`)**: Clean official invoice layout ready for 1-click printing or saving as PDF.

7. **Reports & Analytics (`/reports`)**:
   - Detailed occupancy percentage, revenue trends, and demand rankings.
   - **CSV Data Exports**: Download `grandstay_bookings_report.csv` and `grandstay_rooms_inventory.csv` with one click.

8. **About Project (`/about`)**:
   - Dedicated college mini-project presentation view detailing problem statements, system workflows, and the architectural conversion from Java/JavaFX to Flask/MySQL.

9. **Settings (`/settings`)**:
   - Hotel contact information, live database connection diagnostic tester, and schema auto-init trigger.

---

## 6. Troubleshooting Common Issues

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| **"Cannot connect to MySQL server at localhost:3306"** | MySQL service is not running. | Open XAMPP and click **Start** next to MySQL. Or start the MySQL Windows service in `services.msc`. |
| **"Access denied for user 'root'@'localhost'"** | Incorrect password in `.env`. | Open `.env` and set `MYSQL_PASSWORD` to your actual root password (or leave it blank `MYSQL_PASSWORD=` if using XAMPP). |
| **"Database 'hotel_management' does not exist"** | Database not created yet. | Import `database/schema.sql` via phpMyAdmin, or visit `http://127.0.0.1:5000/settings` and click "Auto-Initialize Database". |
| **"File Activate.ps1 cannot be loaded because running scripts is disabled"** | Windows PowerShell Execution Policy. | Run `.\.venv\Scripts\python.exe app.py` directly without activating the virtual environment. |
| **"Address already in use (Port 5000)"** | Another process is using port 5000. | In `app.py`, change `port=5000` to `port=5050`, or terminate the conflicting app in Task Manager. |

---

## 7. License & Credits

Developed as a professional Full-Stack Hotel Room Management System.  
Suitable for academic reviews, portfolio demonstrations, and commercial hotel management prototyping.
