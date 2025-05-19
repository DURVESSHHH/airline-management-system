# ✈️ Airline Management System

A full-fledged Airline Management System built with **Django**, **MySQL**, **HTML**, and **CSS**, designed to streamline flight bookings, staff and customer management, and reporting operations for airline companies.

---

## 🔧 Features

### 🎫 Booking Module
- Flight search and reservation
- Real-time booking status
- Ticket cancellation and refund system
- PDF ticket download

### 👤 Customer Module
- Profile management
- Travel history
- Loyalty program tracking

### 👨‍✈️ Staff Module
- Staff account management
- Flight assignments
- Status updates and logs

### ✈️ Flight Module
- Add/update/delete flights
- Schedule and aircraft management
- Real-time flight status

### 💳 Payment Module
- Razorpay/UPI/PayPal payment integration
- Refund processing
- 2FA for secure transactions

### 📊 Reports & Admin Dashboard
- Sales & revenue analytics
- Customer feedback dashboard
- Role-based access control (Admin, Staff, Customer)
- Activity audit log viewer

---

## 🛠️ Technologies Used

- **Backend**: Python (Django)
- **Frontend**: HTML5, CSS3
- **Database**: MySQL
- **Payment Gateway**: Razorpay API
- **Authentication**: Role-based login, 2FA for payments

---

## 🚀 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/DURVESSHH/airline-management-system.git

# Navigate to project
cd airline-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup DB
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
