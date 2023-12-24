import hashlib
import time
import json
from collections import OrderedDict

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, merkle_root, nonce, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.merkle_root = merkle_root
        self.nonce = nonce
        self.hash = hash

def calculate_hash(index, previous_hash, timestamp, transactions, merkle_root, nonce):
    value = f"{index}{previous_hash}{timestamp}{transactions}{merkle_root}{nonce}"
    return hashlib.sha256(value.encode()).hexdigest()

def create_genesis_block():
    return Block(0, "0", time.time(), [], "", 0, calculate_hash(0, "0", time.time(), "", "", 0))

def create_new_block(previous_block, transactions, nonce):
    index = previous_block.index + 1
    timestamp = time.time()
    merkle_root = build_merkle_tree(transactions)
    hash = calculate_hash(index, previous_block.hash, timestamp, transactions, merkle_root, nonce)
    return Block(index, previous_block.hash, timestamp, transactions, merkle_root, nonce, hash)

def build_merkle_tree(transactions):
    if not transactions:
        return ""

    transaction_hashes = [hashlib.sha256(json.dumps(transaction.__dict__, sort_keys=True).encode()).hexdigest() for transaction in transactions]
    
    while len(transaction_hashes) > 1:
        new_hashes = []
        for i in range(0, len(transaction_hashes), 2):
            concat_hashes = transaction_hashes[i]
            if i + 1 < len(transaction_hashes):
                concat_hashes += transaction_hashes[i + 1]
            new_hashes.append(hashlib.sha256(concat_hashes.encode()).hexdigest())
        transaction_hashes = new_hashes

    return transaction_hashes[0]

class Blockchain:
    def __init__(self):
        self.chain = [create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2
        self.mining_reward = 1
        self.accounts = {}  # {account_address: balance}

    def add_transaction(self, sender, recipient, amount):
        if sender not in self.accounts or recipient not in self.accounts:
            print("Invalid sender or recipient. Make sure accounts exist.")
            return False

        if self.accounts[sender] < amount:
            print("Insufficient funds.")
            return False

        transaction = Transaction(sender, recipient, amount)
        self.pending_transactions.append(transaction)
        print("Transaction added successfully!")
        return True

    def mine_block(self, miner_address):
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        previous_block = self.chain[-1]
        nonce = self.proof_of_work(previous_block.hash)
        new_block = create_new_block(previous_block, self.pending_transactions, nonce)
        self.chain.append(new_block)

        # Reward the miner
        self.accounts[miner_address] = self.accounts.get(miner_address, 0) + self.mining_reward

        # Process transactions
        for transaction in new_block.transactions:
            self.accounts[transaction.sender] -= transaction.amount
            self.accounts[transaction.recipient] = self.accounts.get(transaction.recipient, 0) + transaction.amount

        self.pending_transactions = []
        print("Block mined successfully!")

    def proof_of_work(self, previous_hash):
        nonce = 0
        while True:
            hash_attempt = calculate_hash(self.chain[-1].index + 1, previous_hash, time.time(), self.pending_transactions, "", nonce)
            if hash_attempt.startswith('0' * self.difficulty):
                print(f"Proof of Work found: {hash_attempt}")
                return nonce
            nonce += 1

    def display_chain(self):
        for block in self.chain:
            print("Index:", block.index)
            print("Previous Hash:", block.previous_hash)
            print("Timestamp:", block.timestamp)
            print("Transactions:", block.transactions)
            print("Merkle Root:", block.merkle_root)
            print("Nonce:", block.nonce)
            print("Hash:", block.hash)
            print("-" * 30)

    def display_accounts(self):
        print("\nAccount Balances:")
        for account, balance in self.accounts.items():
            print(f"{account}: {balance} units")

# Example usage:
if __name__ == "__main__":
    blockchain = Blockchain()

    while True:
        print("\nBlockchain Menu:")
        print("1. Create Account")
        print("2. Add Transaction")
        print("3. Mine Block")
        print("4. Display Blockchain")
        print("5. Display Account Balances")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            account_address = input("Enter account address: ")
            initial_balance = float(input("Enter initial balance: "))
            blockchain.accounts[account_address] = initial_balance
            print("Account created successfully!")

        elif choice == "2":
            sender = input("Enter sender: ")
            recipient = input("Enter recipient: ")
            amount = float(input("Enter amount: "))
            blockchain.add_transaction(sender, recipient, amount)

        elif choice == "3":
            miner_address = input("Enter miner's address: ")
            blockchain.mine_block(miner_address)

        elif choice == "4":
            print("\nBlockchain:")
            blockchain.display_chain()

        elif choice == "5":
            blockchain.display_accounts()

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")
