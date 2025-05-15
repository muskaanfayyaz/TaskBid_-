
# 🚀 TaskBid — Micro Task Platform

TaskBid is a simple Streamlit-based micro task marketplace where users can **post** or **bid** on small tasks like fixing bugs, designing a logo, or editing content. All gigs are $10, making it fast, easy, and affordable.

## 🌟 Features

- 📝 Post and view tasks
- 📨 Submit and manage bids
- 💳 Stripe payment integration (buyer pays after task completion)
- ✅ Task completion tracking
- 👥 Buyer and seller roles with dashboards
- 💰 Platform fee logic (sellers receive $9 after $1 fee)

---

## ⚙️ Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/your-repo/taskbid.git
cd taskbid
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the app**

```bash
streamlit run main.py
```

---

## 🔐 Test Users

Use the following test accounts to try out the application:

| Username | Password      | Role   | Email                    |
|----------|---------------|--------|--------------------------|
| Muskaan  | `muskaan`     | Buyer  | muskaanfayyaz3@gmail.com |
| test     | `test123`     | Seller | test@gmail.com           |
| alice    | `alicepass`   | Buyer  | alice@example.com        |
| bob      | `bobpass`     | Seller | bob@example.com          |
| charlie  | `charliepass` | Seller | charlie@example.com      |
| diana    | `dianapass`   | Buyer  | diana@example.com        |
| eve      | `evepass`     | Seller | eve@example.com          |

---

## 🧠 OOP Principles Used

### 1. **Encapsulation**  
Encapsulation is implemented through the use of class definitions for `User`, `Task`, and `Bid`. Each class contains only the necessary fields and methods to manipulate its own data.

**Example:**  
```python
class Task:
    def __init__(self, title, description, buyer, price):
        self.title = title
        self.description = description
        self.buyer = buyer
        self.price = price
        self.status = "open"
```

### 2. **Abstraction**  
Database interaction is abstracted into utility functions: `load_db()` and `save_db()`. The main UI doesn't handle file I/O directly.

**Example:**  
```python
def load_db(path):
    ...
def save_db(path, data):
    ...
```

### 3. **Inheritance**  
Though not deeply needed in this app, classes like `User`, `Task`, and `Bid` could easily be extended to inherit common behavior in a larger codebase.

### 4. **Polymorphism**  
Polymorphism is reflected in method overriding and conditional UI rendering based on the user's role (buyer/seller).

---

## 💳 Stripe Payment Flow

- Task is **assigned immediately** upon bid acceptance (no payment yet).
- **Seller marks task completed** → status changes to "pending_payment".
- Buyer sees "Pay with Stripe" and pays.
- Upon payment, task is marked **completed**.

---

## 📂 Project Structure

```
├── main.py
├── models/
│   ├── user.py
│   ├── task.py
│   └── bid.py
├── utils/
│   ├── auth.py
│   └── stripe_utils.py
├── data/
│   ├── users.json
│   ├── tasks.json
│   └── bids.json
├── static/
│   └── logo.png
```

---

## 📬 Contact

For any issues or contributions, please raise an issue or submit a pull request.

