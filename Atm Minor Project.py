import json, os
from tkinter import *
from tkinter import messagebox, simpledialog
from datetime import datetime

DATA_FILE = 'bank_data.json'

class BankAccount:
    def __init__(self, name, account_number, pin, balance=0.0):
        self.name, self.account_number, self.pin, self.balance = name, account_number, pin, balance
        self.transactions = []
    
    def deposit(self, amount):
        if amount <= 0: raise ValueError("Amount must be positive")
        self.balance += amount
        self.transactions.append(('Deposit', amount, datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    def withdraw(self, amount):
        if amount <= 0: raise ValueError("Amount must be positive")
        if amount > self.balance: raise ValueError("Insufficient balance")
        self.balance -= amount
        self.transactions.append(('Withdraw', amount, datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    def to_dict(self):
        return {'name': self.name, 'account_number': self.account_number, 
                'pin': self.pin, 'balance': self.balance, 'transactions': self.transactions}

def load_accounts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: 
                data = json.load(f)
                accounts = {}
                for k, v in data.items():
                    acc = BankAccount(v['name'], v['account_number'], v['pin'], v['balance'])
                    acc.transactions = v.get('transactions', [])
                    accounts[k] = acc
                return accounts
            except: pass
    return {}

def save_accounts(accounts):
    with open(DATA_FILE, 'w') as f:
        json.dump({k: v.to_dict() for k, v in accounts.items()}, f)

accounts = load_accounts()
current_user = None

class SimpleBankApp:
    def __init__(self, root):
        self.root = root
        root.title("Smart Bank System")
        root.geometry("420x500")
        root.configure(bg="#f0f4f8")

        Label(root, text="Smart Bank System", font=("Arial", 18, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=15)
        
        self.buttons = [
            ("Create Account", self.create_account, "#4CAF50"),
            ("Login", self.login, "#2196F3"),
            ("Deposit", self.deposit, "#8BC34A"),
            ("Withdraw", self.withdraw, "#FF9800"),
            ("Transaction History", self.show_history, "#9C27B0"),
            ("Logout", self.logout, "#F44336")
        ]

        for text, cmd, color in self.buttons:
            Button(root, text=text, command=cmd, bg=color, fg="white", 
                  font=("Arial", 12), width=20, pady=5).pack(pady=5)

        self.status = Label(root, text="Please login", bg="#f0f4f8", fg="gray")
        self.status.pack(pady=15)

    def update_status(self):
        if current_user:
            self.status.config(text=f"Welcome, {current_user.name}\nBalance: ₹{current_user.balance:.2f}")
        else:
            self.status.config(text="Please login")

    def create_account(self):
        top = Toplevel(self.root)
        top.title("Create Account")
        
        entries = []
        for i, label in enumerate(["Name:", "Account Number:", "PIN (4 digits):"]):
            Label(top, text=label).grid(row=i, column=0, padx=10, pady=5)
            e = Entry(top, show="*" if "PIN" in label else "")
            e.grid(row=i, column=1, padx=10, pady=5)
            entries.append(e)
        
        def save():
            try:
                name, acc_no, pin = (e.get() for e in entries)
                if acc_no in accounts: raise ValueError("Account exists")
                if not (pin.isdigit() and len(pin) == 4): raise ValueError("Invalid PIN")
                accounts[acc_no] = BankAccount(name, acc_no, pin)
                save_accounts(accounts)
                messagebox.showinfo("Success", "Account created!")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        Button(top, text="Create", command=save, bg="#4CAF50", fg="white").grid(row=3, column=1, pady=10)

    def login(self):
        top = Toplevel(self.root)
        top.title("Login")
        
        Label(top, text="Account Number:").grid(row=0, column=0, padx=10, pady=5)
        acc_entry = Entry(top)
        acc_entry.grid(row=0, column=1, padx=10, pady=5)
        
        Label(top, text="PIN:").grid(row=1, column=0, padx=10, pady=5)
        pin_entry = Entry(top, show="*")
        pin_entry.grid(row=1, column=1, padx=10, pady=5)
        
        def auth():
            global current_user
            try:
                acc_no = acc_entry.get()
                if acc_no not in accounts: raise ValueError("Account not found")
                if accounts[acc_no].pin != pin_entry.get(): raise ValueError("Invalid PIN")
                current_user = accounts[acc_no]
                self.update_status()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        Button(top, text="Login", command=auth, bg="#2196F3", fg="white").grid(row=2, column=1, pady=10)

    def deposit(self):
        self._transaction("Deposit", lambda a: current_user.deposit(a))

    def withdraw(self):
        self._transaction("Withdraw", lambda a: current_user.withdraw(a))

    def _transaction(self, action, func):
        if not current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        amount = simpledialog.askfloat(action, "Enter amount:")
        if amount:
            try:
                func(amount)
                save_accounts(accounts)
                self.update_status()
                messagebox.showinfo("Success", f"{action} successful!\nNew balance: ₹{current_user.balance:.2f}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_history(self):
        if not current_user:
            messagebox.showerror("Error", "Please login first")
            return
        
        top = Toplevel(self.root)
        top.title("Transaction History")
        
        text = Text(top, width=50, height=15)
        scroll = Scrollbar(top, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        
        text.pack(side=LEFT, fill=BOTH)
        scroll.pack(side=RIGHT, fill=Y)
        
        text.insert(END, f"Transaction History for {current_user.name}\n\n")
        for txn in current_user.transactions[-20:]:
            color = "green" if txn[0] == "Deposit" else "orange"
            text.insert(END, f"{txn[2]} - {txn[0]}: ₹{txn[1]:.2f}\n", color)
        
        text.tag_config("green", foreground="green")
        text.tag_config("orange", foreground="orange")

    def logout(self):
        global current_user
        current_user = None
        self.update_status()
        messagebox.showinfo("Logged out", "You have been logged out")

if __name__ == "__main__":
    root = Tk()
    SimpleBankApp(root)
    root.mainloop()