# PROJECT 3: Simple Banking System - SCROLLABLE GUI
# Jaani, ab scroll karke saare options dekh sakta hai

import json
import os
import datetime
import customtkinter as ctk
from tkinter import messagebox

BANK_FILE = "bank_data.txt"

# ============================================================================
# BANKING CLASSES
# ============================================================================

class Transaction:
    def __init__(self, type, amount, balance_after):
        self.type = type
        self.amount = amount
        self.balance_after = balance_after
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "type": self.type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "date": self.date
        }
    
    @staticmethod
    def from_dict(data):
        trans = Transaction(data["type"], data["amount"], data["balance_after"])
        trans.date = data["date"]
        return trans


class BankAccount:
    def __init__(self, account_number, name, initial_deposit=0):
        self.account_number = account_number
        self.name = name
        self.balance = initial_deposit
        self.transactions = []
        
        if initial_deposit > 0:
            self.add_transaction("Account Created", initial_deposit, initial_deposit)
    
    def add_transaction(self, trans_type, amount, balance_after):
        transaction = Transaction(trans_type, amount, balance_after)
        self.transactions.append(transaction)
    
    def deposit(self, amount):
        if amount <= 0:
            return False, "Amount must be greater than 0"
        self.balance += amount
        self.add_transaction("Deposit", amount, self.balance)
        return True, f"Deposited {amount}. New balance: {self.balance}"
    
    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be greater than 0"
        if amount > self.balance:
            return False, f"Insufficient balance! Available: {self.balance}"
        self.balance -= amount
        self.add_transaction("Withdraw", amount, self.balance)
        return True, f"Withdrew {amount}. New balance: {self.balance}"
    
    def check_balance(self):
        return self.balance
    
    def get_mini_statement(self, limit=5):
        return self.transactions[-limit:] if self.transactions else []
    
    def to_dict(self):
        return {
            "account_number": self.account_number,
            "name": self.name,
            "balance": self.balance,
            "transactions": [t.to_dict() for t in self.transactions]
        }
    
    @staticmethod
    def from_dict(data):
        account = BankAccount(data["account_number"], data["name"], 0)
        account.balance = data["balance"]
        account.transactions = [Transaction.from_dict(t) for t in data["transactions"]]
        return account


class Bank:
    def __init__(self):
        self.accounts = {}
        self.load_data()
    
    def create_account(self, name, initial_deposit=0):
        if not self.accounts:
            account_number = "ACC1001"
        else:
            last_acc = max(self.accounts.keys())
            num = int(last_acc[3:]) + 1
            account_number = f"ACC{num}"
        
        account = BankAccount(account_number, name, initial_deposit)
        self.accounts[account_number] = account
        self.save_data()
        return account_number
    
    def find_account(self, account_number):
        return self.accounts.get(account_number)
    
    def deposit(self, account_number, amount):
        account = self.find_account(account_number)
        if not account:
            return False, "Account not found!"
        result, message = account.deposit(amount)
        if result:
            self.save_data()
        return result, message
    
    def withdraw(self, account_number, amount):
        account = self.find_account(account_number)
        if not account:
            return False, "Account not found!"
        result, message = account.withdraw(amount)
        if result:
            self.save_data()
        return result, message
    
    def check_balance(self, account_number):
        account = self.find_account(account_number)
        if not account:
            return None, "Account not found!"
        return account.check_balance(), ""
    
    def get_mini_statement(self, account_number):
        account = self.find_account(account_number)
        if not account:
            return None, "Account not found!"
        return account.get_mini_statement(), ""
    
    def transfer(self, from_account, to_account, amount):
        from_acc = self.find_account(from_account)
        to_acc = self.find_account(to_account)
        
        if not from_acc:
            return False, "Source account not found!"
        if not to_acc:
            return False, "Destination account not found!"
        if amount <= 0:
            return False, "Amount must be greater than 0"
        if from_acc.balance < amount:
            return False, f"Insufficient balance! Available: {from_acc.balance}"
        
        from_acc.balance -= amount
        to_acc.balance += amount
        
        from_acc.add_transaction(f"Transfer Sent to {to_account}", amount, from_acc.balance)
        to_acc.add_transaction(f"Transfer Received from {from_account}", amount, to_acc.balance)
        
        self.save_data()
        return True, f"Transferred {amount} from {from_account} to {to_account}"
    
    def get_all_accounts(self):
        return self.accounts
    
    def save_data(self):
        data = {}
        for acc_num, account in self.accounts.items():
            data[acc_num] = account.to_dict()
        with open(BANK_FILE, "w") as file:
            json.dump(data, file, indent=4)
    
    def load_data(self):
        if os.path.exists(BANK_FILE):
            try:
                with open(BANK_FILE, "r") as file:
                    data = json.load(file)
                    for acc_num, acc_data in data.items():
                        self.accounts[acc_num] = BankAccount.from_dict(acc_data)
            except:
                pass


# ============================================================================
# SCROLLABLE GUI CLASS
# ============================================================================

class ScrollableBankingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Banking System - Complete Edition")
        self.root.geometry("1300x700")
        
        # Initialize bank
        self.bank = Bank()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fonts
        self.title_font = ctk.CTkFont(size=26, weight="bold")
        self.header_font = ctk.CTkFont(size=15, weight="bold")
        self.normal_font = ctk.CTkFont(size=12)
        
        self.setup_ui()
        self.refresh_accounts_list()
    
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#1a1a2e")
        self.main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, height=70, fg_color="#0f3460", corner_radius=0)
        header_frame.pack(fill="x")
        
        title = ctk.CTkLabel(header_frame, text="SIMPLE BANKING SYSTEM", 
                              font=self.title_font, text_color="#4ECDC4")
        title.pack(pady=15)
        
        # Content Frame (Left and Right)
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a2e")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ==================== LEFT PANEL (SCROLLABLE) ====================
        left_container = ctk.CTkFrame(content_frame, fg_color="#0f3460", corner_radius=15)
        left_container.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        
        # Scrollable frame for left panel
        self.left_canvas = ctk.CTkScrollableFrame(left_container, fg_color="#0f3460")
        self.left_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Feature 1: Create Account
        ctk.CTkLabel(self.left_canvas, text="1. CREATE ACCOUNT", font=self.header_font, text_color="#4ECDC4").pack(pady=(10,5))
        
        create_frame = ctk.CTkFrame(self.left_canvas, fg_color="#16213e", corner_radius=10)
        create_frame.pack(pady=5, padx=15, fill="x")
        
        self.name_entry = ctk.CTkEntry(create_frame, placeholder_text="Full Name", font=self.normal_font, height=38)
        self.name_entry.pack(pady=(10,5), padx=15, fill="x")
        
        self.init_deposit_entry = ctk.CTkEntry(create_frame, placeholder_text="Initial Deposit (0 if none)", font=self.normal_font, height=38)
        self.init_deposit_entry.pack(pady=5, padx=15, fill="x")
        
        self.create_btn = ctk.CTkButton(create_frame, text="Create Account", command=self.create_account,
                                         fg_color="#f39c12", hover_color="#e67e22", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.create_btn.pack(pady=(5,10), padx=15, fill="x")
        
        # Feature 2,3,4: Deposit, Withdraw, Balance
        ctk.CTkLabel(self.left_canvas, text="2. DEPOSIT / 3. WITHDRAW / 4. BALANCE", font=self.header_font, text_color="#4ECDC4").pack(pady=(15,5))
        
        trans_frame = ctk.CTkFrame(self.left_canvas, fg_color="#16213e", corner_radius=10)
        trans_frame.pack(pady=5, padx=15, fill="x")
        
        self.acc_entry = ctk.CTkEntry(trans_frame, placeholder_text="Account Number", font=self.normal_font, height=38)
        self.acc_entry.pack(pady=(10,5), padx=15, fill="x")
        
        self.amount_entry = ctk.CTkEntry(trans_frame, placeholder_text="Amount", font=self.normal_font, height=38)
        self.amount_entry.pack(pady=5, padx=15, fill="x")
        
        btn_row = ctk.CTkFrame(trans_frame, fg_color="#16213e")
        btn_row.pack(pady=(5,10), padx=15, fill="x")
        
        self.deposit_btn = ctk.CTkButton(btn_row, text="Deposit", command=self.deposit_money,
                                          fg_color="#00b894", hover_color="#009432", height=38)
        self.deposit_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.withdraw_btn = ctk.CTkButton(btn_row, text="Withdraw", command=self.withdraw_money,
                                           fg_color="#e74c3c", hover_color="#c0392b", height=38)
        self.withdraw_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.balance_btn = ctk.CTkButton(btn_row, text="Balance", command=self.check_balance,
                                          fg_color="#3498db", hover_color="#2980b9", height=38)
        self.balance_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Feature 5: Mini Statement
        ctk.CTkLabel(self.left_canvas, text="5. MINI STATEMENT", font=self.header_font, text_color="#4ECDC4").pack(pady=(15,5))
        
        self.statement_btn = ctk.CTkButton(self.left_canvas, text="Show Mini Statement", command=self.show_statement,
                                            fg_color="#9b59b6", hover_color="#8e44ad", height=40)
        self.statement_btn.pack(pady=5, padx=30, fill="x")
        
        # Feature 6: Transfer Money
        ctk.CTkLabel(self.left_canvas, text="6. TRANSFER MONEY", font=self.header_font, text_color="#4ECDC4").pack(pady=(15,5))
        
        transfer_frame = ctk.CTkFrame(self.left_canvas, fg_color="#16213e", corner_radius=10)
        transfer_frame.pack(pady=5, padx=15, fill="x")
        
        self.to_acc_entry = ctk.CTkEntry(transfer_frame, placeholder_text="Destination Account Number", font=self.normal_font, height=38)
        self.to_acc_entry.pack(pady=(10,5), padx=15, fill="x")
        
        self.transfer_amount_entry = ctk.CTkEntry(transfer_frame, placeholder_text="Amount to Transfer", font=self.normal_font, height=38)
        self.transfer_amount_entry.pack(pady=5, padx=15, fill="x")
        
        self.transfer_btn = ctk.CTkButton(transfer_frame, text="Transfer Money", command=self.transfer_money,
                                           fg_color="#e67e22", hover_color="#d35400", height=40)
        self.transfer_btn.pack(pady=(5,10), padx=15, fill="x")
        
        # Feature 7: Show All Accounts
        ctk.CTkLabel(self.left_canvas, text="7. SHOW ALL ACCOUNTS", font=self.header_font, text_color="#4ECDC4").pack(pady=(15,5))
        
        self.refresh_btn = ctk.CTkButton(self.left_canvas, text="Show All Accounts", command=self.refresh_accounts_list,
                                          fg_color="#4ECDC4", hover_color="#3ba89c", height=40)
        self.refresh_btn.pack(pady=5, padx=30, fill="x")
        
        # Feature 8: Exit
        ctk.CTkLabel(self.left_canvas, text="8. EXIT", font=self.header_font, text_color="#e74c3c").pack(pady=(15,5))
        
        self.exit_btn = ctk.CTkButton(self.left_canvas, text="Exit Application", command=self.exit_app,
                                       fg_color="#c0392b", hover_color="#e74c3c", height=40)
        self.exit_btn.pack(pady=(5,15), padx=30, fill="x")
        
        # ==================== RIGHT PANEL ====================
        right_panel = ctk.CTkFrame(content_frame, fg_color="#0f3460", corner_radius=15)
        right_panel.pack(side="right", fill="both", padx=10, pady=10, expand=True)
        
        # All Accounts List
        accounts_frame = ctk.CTkFrame(right_panel, fg_color="#16213e", corner_radius=10)
        accounts_frame.pack(pady=15, padx=15, fill="both", expand=True)
        
        ctk.CTkLabel(accounts_frame, text="ALL BANK ACCOUNTS", font=self.header_font, text_color="#4ECDC4").pack(pady=10)
        
        self.accounts_listbox = ctk.CTkTextbox(accounts_frame, font=self.normal_font, height=180)
        self.accounts_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Transaction Result Display
        result_frame = ctk.CTkFrame(right_panel, fg_color="#16213e", corner_radius=10)
        result_frame.pack(pady=15, padx=15, fill="both", expand=True)
        
        ctk.CTkLabel(result_frame, text="TRANSACTION RESULT", font=self.header_font, text_color="#4ECDC4").pack(pady=10)
        
        self.result_display = ctk.CTkTextbox(result_frame, font=self.normal_font, height=120)
        self.result_display.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Statistics Bar
        self.stats_frame = ctk.CTkFrame(right_panel, height=50, fg_color="#4ECDC4", corner_radius=10)
        self.stats_frame.pack(pady=10, padx=15, fill="x")
        
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Total Accounts: 0 | Total Balance: 0", 
                                         font=ctk.CTkFont(size=13, weight="bold"), 
                                         text_color="#1a1a2e")
        self.stats_label.pack(pady=12)
    
    def create_account(self):
        name = self.name_entry.get().strip()
        try:
            deposit = float(self.init_deposit_entry.get().strip()) if self.init_deposit_entry.get() else 0
        except:
            messagebox.showerror("Error", "Invalid deposit amount!")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter your name!")
            return
        
        acc_num = self.bank.create_account(name, deposit)
        self.refresh_accounts_list()
        self.show_result(f"ACCOUNT CREATED SUCCESSFULLY\n\nAccount Number: {acc_num}\nAccount Holder: {name}\nInitial Balance: {deposit}")
        self.name_entry.delete(0, 'end')
        self.init_deposit_entry.delete(0, 'end')
    
    def deposit_money(self):
        acc_num = self.acc_entry.get().strip().upper()
        try:
            amount = float(self.amount_entry.get().strip())
        except:
            messagebox.showerror("Error", "Please enter valid amount!")
            return
        
        if not acc_num:
            messagebox.showerror("Error", "Please enter account number!")
            return
        
        success, message = self.bank.deposit(acc_num, amount)
        if success:
            self.refresh_accounts_list()
            self.show_result(f"DEPOSIT SUCCESSFUL\n\n{message}")
            self.acc_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", message)
    
    def withdraw_money(self):
        acc_num = self.acc_entry.get().strip().upper()
        try:
            amount = float(self.amount_entry.get().strip())
        except:
            messagebox.showerror("Error", "Please enter valid amount!")
            return
        
        if not acc_num:
            messagebox.showerror("Error", "Please enter account number!")
            return
        
        success, message = self.bank.withdraw(acc_num, amount)
        if success:
            self.refresh_accounts_list()
            self.show_result(f"WITHDRAWAL SUCCESSFUL\n\n{message}")
            self.acc_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", message)
    
    def check_balance(self):
        acc_num = self.acc_entry.get().strip().upper()
        
        if not acc_num:
            messagebox.showerror("Error", "Please enter account number!")
            return
        
        balance, message = self.bank.check_balance(acc_num)
        if balance is not None:
            self.show_result(f"BALANCE INQUIRY\n\nAccount Number: {acc_num}\nCurrent Balance: {balance}")
        else:
            messagebox.showerror("Error", message)
    
    def show_statement(self):
        acc_num = self.acc_entry.get().strip().upper()
        
        if not acc_num:
            messagebox.showerror("Error", "Please enter account number!")
            return
        
        transactions, message = self.bank.get_mini_statement(acc_num)
        if transactions is not None:
            if not transactions:
                self.show_result(f"MINI STATEMENT\n\nAccount: {acc_num}\nNo transactions yet!")
            else:
                result = f"MINI STATEMENT for {acc_num}\n\n"
                result += "-" * 50 + "\n"
                result += "Type          | Amount    | Balance\n"
                result += "-" * 50 + "\n"
                for t in transactions:
                    result += f"{t.type:13} | {t.amount:9} | {t.balance_after}\n"
                self.show_result(result)
        else:
            messagebox.showerror("Error", message)
    
    def transfer_money(self):
        from_acc = self.acc_entry.get().strip().upper()
        to_acc = self.to_acc_entry.get().strip().upper()
        try:
            amount = float(self.transfer_amount_entry.get().strip())
        except:
            messagebox.showerror("Error", "Please enter valid amount!")
            return
        
        if not from_acc or not to_acc:
            messagebox.showerror("Error", "Please enter both account numbers!")
            return
        
        success, message = self.bank.transfer(from_acc, to_acc, amount)
        if success:
            self.refresh_accounts_list()
            self.show_result(f"TRANSFER SUCCESSFUL\n\n{message}")
            self.acc_entry.delete(0, 'end')
            self.to_acc_entry.delete(0, 'end')
            self.transfer_amount_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", message)
    
    def refresh_accounts_list(self):
        self.accounts_listbox.delete("1.0", "end")
        
        accounts = self.bank.get_all_accounts()
        
        if not accounts:
            self.accounts_listbox.insert("1.0", "No accounts found!")
            self.stats_label.configure(text="Total Accounts: 0 | Total Balance: 0")
            return
        
        total_balance = 0
        self.accounts_listbox.insert("1.0", "ACCOUNT LIST\n")
        self.accounts_listbox.insert("2.0", "=" * 50 + "\n\n")
        
        for acc_num, account in accounts.items():
            self.accounts_listbox.insert("end", f"{acc_num} | {account.name} | Balance: {account.balance}\n")
            total_balance += account.balance
        
        self.stats_label.configure(text=f"Total Accounts: {len(accounts)} | Total Balance: {total_balance}")
    
    def show_result(self, message):
        self.result_display.delete("1.0", "end")
        self.result_display.insert("1.0", message)
    
    def exit_app(self):
        self.bank.save_data()
        self.root.quit()


# ============================================================================
# RUN GUI
# ============================================================================

if __name__ == "__main__":
    root = ctk.CTk()
    app = ScrollableBankingGUI(root)
    root.mainloop()