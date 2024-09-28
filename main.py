import logging
from core import Blockchain, Wallet, db_lock
import os
import sqlite3
import threading
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Usar threading.local para garantir que cada thread tenha sua própria conexão com o banco de dados
thread_local = threading.local()

def get_db_connection():
    if not hasattr(thread_local, 'conn'):
        thread_local.conn = sqlite3.connect('blockchain.db', check_same_thread=False)
    return thread_local.conn

class Cryptocurrency:
    def __init__(self, name):
        self.name = name
        self.blockchain = Blockchain()
        if not self.blockchain.chain:
            self.blockchain.create_genesis_block()
        self.wallets = Wallet.load_wallets()  # Load existing wallets
        self.transaction_attempts = {}
        self.pending_transactions = []

        # Load and store the creator's wallet address
        self.creator_wallet_address = None
        self.load_creator_wallet()

    def display_balance(self, identifier):
        # Procurar pelo dono ou endereço da carteira
        for wallet in self.wallets.values():
            if wallet.owner == identifier or wallet.address == identifier:
                return wallet.balance
        return "Wallet not found."

    def load_creator_wallet(self):
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM wallets WHERE owner = ?', ("Cryptocurrency Creator",))
            wallet_data = cursor.fetchone()
            if wallet_data:
                self.creator_wallet_address = wallet_data[0]
                logging.info(f"Creator's wallet loaded: {self.creator_wallet_address}")

    def create_wallet(self, owner):
        if owner in self.wallets:
            logging.warning(f'Wallet already exists for the owner {owner}.')
            return self.wallets[owner]
        new_wallet = Wallet(owner)
        self.wallets[new_wallet.address] = new_wallet
        return new_wallet

    def transfer_funds(self, from_address, to_address, amount):
        with db_lock:
            if from_address not in self.wallets or to_address not in self.wallets:
                raise ValueError("Invalid wallet address.")

            sender_wallet = self.wallets[from_address]
            recipient_wallet = self.wallets[to_address]

            if sender_wallet.balance < amount:
                raise ValueError("Insufficient balance for transfer.")
            sender_wallet.subtract_funds(amount)
            recipient_wallet.add_funds(amount)

            logging.info(f'Transferred {amount} from {from_address} to {to_address}.')

    def add_transaction(self, from_address, to_address, amount):
        transaction = {
            'from': from_address,
            'to': to_address,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
        logging.info(f'Transaction added: {transaction}')

    def mine_block(self, miner_address):
        if miner_address not in self.wallets:
            raise ValueError("Invalid miner wallet address.")

        total_amount = sum(tx['amount'] for tx in self.pending_transactions)
        if total_amount <= 0:
            raise ValueError("No valid transactions to mine.")

        self.blockchain.add_block(data=f"Transactions: {self.pending_transactions}")
        self.pending_transactions.clear()  # Clear pending transactions after mining

        # Add reward to miner's wallet
        miner_wallet = self.wallets[miner_address]
        miner_wallet.add_funds(1.0)  # Fixed reward of 1.0 unit
        logging.info(f'Reward of 1.0 unit added to miner\'s wallet {miner_address}.')

    def close(self):
        self.blockchain.close()
        logging.info('Cryptocurrency closed.')

def display_menu():
    print("\nCLI Panel:")
    print("1. Create Wallet")
    print("2. Add Transaction")
    print("3. Mine Cryptocurrency")
    print("4. Check Balance")
    print("5. Details")
    print("6. Exit")

def cli_interface(cryptocoin):
    while True:
        display_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            owner = input("Enter wallet owner's name: ")
            try:
                address = cryptocoin.create_wallet(owner)
                print(f"Wallet successfully created! Address: {address.address}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            sender = input("Enter sender's address: ")
            recipient = input("Enter recipient's address: ")
            amount = float(input("Enter amount to transfer: "))
            try:
                cryptocoin.add_transaction(sender, recipient, amount)
                print("Transaction successfully added!")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "3":
            miner_address = input("Enter miner's address: ")
            try:
                cryptocoin.mine_block(miner_address)
                print("Mining successfully completed!")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "4":
            identifier = input("Enter wallet address or owner's name: ")
            try:
                balance = cryptocoin.display_balance(identifier)
                print(f"Wallet balance: {balance}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "5":
            identifier = input("Enter wallet address or owner's name: ")
            if re.match(r"^[A-Za-z0-9]{34}$", identifier) or re.match(r"^[A-Za-z0-9 ]{3,50}$", identifier):
                try:
                    balance = cryptocoin.display_balance(identifier)
                    print(f"Wallet balance: {balance}")
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("Invalid identifier. It must be a 34-character address or a name with 3 to 50 characters.")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

    # Display creator's wallet balance at the end of the program
    creator_balance = cryptocoin.display_balance(cryptocoin.creator_wallet_address)
    print(f'Creator\'s wallet balance: {creator_balance}')

def main():
    try:
        # Check if database exists
        db_exists = os.path.exists('blockchain.db')
        if db_exists:
            logging.info('Connected to existing database.')
        else:
            logging.info('Database created and connected.')

        aisten_coin = Cryptocurrency("AistenCoin")

        cli = threading.Thread(target=cli_interface, args=(aisten_coin,))
        cli.start()
        cli.join()
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
    finally:
        # Garantir que a conexão com o banco seja fechada corretamente
        conn = get_db_connection()
        if conn:
            conn.close()
            logging.info('Database connection closed.')

if __name__ == "__main__":
    main()
