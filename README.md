**Appoint Me — Doctor Appointment Booking Portal**

Appoint Me is a modern and responsive doctor appointment system built using Django. It provides a seamless experience for patients to book appointments with doctors, and allows doctors and admins to manage appointments, specializations, and availability efficiently.

---

**Features**

* Patients can book appointments without logging in
* Separate Doctor and Admin portals
* Manage doctor schedules and specializations
* Secure login/logout system for Doctors and Admins
* Clean, responsive UI using Bootstrap and TailwindCSS
* Media support for doctor profiles and images
* Environment-based configurations via `.env`

---

**Tech Stack**

| Layer       | Technology                                                      |
| ----------- | --------------------------------------------------------------- |
| Backend     | Python, Django                                                  |
| Frontend    | HTML, CSS, Bootstrap, TailwindCSS, jQuery                       |
| Database    | MySQL                                                           |
| Templates   | Django Templates with `{% block %}` / `{% include %}` structure |
| Environment | python-dotenv for config                                        |
| Deployment  | WSGI compatible (Gunicorn/Nginx ready)                          |

---

**Project Structure**

```
doctor_appointment/
├── appointmentapp/        # Main Django app (views, models, urls)
├── doctor_appointment/    # Project settings and URLs
├── templates/             # Global templates directory
├── static/                # Static files (CSS, JS, images)
├── media/                 # Uploaded files (e.g. doctor profile photos)
├── .env                   # Environment variables (not pushed to Git)
└── manage.py
```

---

**.env Example**

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=appointmedb
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
```

---

**Setup Instructions**

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/appoint-me.git
cd appoint-me
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup .env file

```bash
cp .env  # Then edit .env with your DB credentials
```

### 4. Create the database

```sql
CREATE DATABASE appointmedb;
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed the admin user

```bash
python manage.py seed_admin
```

Use these credentials to login as Admin:

* **Email:** [admin@gmail.com]
* **Password:** admin123

### 7. Run the development server

```bash
python manage.py runserver
```

### Access the app

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser

---
