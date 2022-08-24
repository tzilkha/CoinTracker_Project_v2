
from sqlalchemy.orm import Session

import models, schemas

# Database Calls

class UserRepo:
    
    async def create_user(db: Session, user: schemas.UserCreate):
        db_users = models.User(name=user.name, username=user.username)
        db.add(db_users)
        db.commit()
        db.refresh(db_users)
        return db_users

    def fetch_by_username(db: Session, username):
        return db.query(models.User).filter(models.User.username == username).first()

    def fetch_by_usernames(db: Session, usernames):
        return db.query(models.User).filter(models.User.username.in_(usernames)).all()    

    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()

    async def delete(db: Session, username):
        db_user= db.query(models.User).filter_by(username=username).first()
        db.delete(db_user)
        db.commit()
     
    
class WalletRepo:

    async def create_wallet(db: Session, address):
        db_wallet = models.Wallet(address=address, last_sync=0, balance=0, n_txs=0)
        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)
        return db_wallet

    def fetch_by_address(db: Session, address):
        return db.query(models.Wallet).filter(models.Wallet.address == address).first()

    def fetch_by_addresses(db: Session, addresses):
        return db.query(models.Wallet).filter(models.Wallet.address.in_(addresses)).all()
     
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Wallet).offset(skip).limit(limit).all()
     
    async def delete(db: Session, address):
        db_wallet = db.query(models.Wallet).filter_by(address=address).first()
        db.delete(db_wallet)
        db.commit()

    async def update_n_txs(db: Session, address, n_txs):
        db_wallet = db.query(models.Wallet).filter_by(address=address).first()
        db_wallet.n_txs = n_txs
        db.commit()

    async def update_balance(db: Session, address, balance):
        db_wallet = db.query(models.Wallet).filter_by(address=address).first()
        db_wallet.balance = balance
        db.commit()

    async def update_sync_time(db: Session, address, time):
        db_wallet = db.query(models.Wallet).filter_by(address=address).first()
        db_wallet.last_sync = time
        db.commit()


class AssociationRepo:

    async def create_association(db: Session, address, username):
        db_association = models.UserAddress(address=address, username=username)
        db.add(db_association)
        db.commit()
        db.refresh(db_association)
        return db_association

    def fetch_association(db: Session, address, username):
        return db.query(models.UserAddress).filter(models.UserAddress.address == address, models.UserAddress.username == username).first()

    def fetch_all_addresses(db: Session, username):
        return db.query(models.UserAddress).filter(models.UserAddress.username == username).all()

    def fetch_all_usernames(db: Session, address):
        return db.query(models.UserAddress).filter(models.UserAddress.address == address).all()

    async def delete_association(db: Session, username, address):
        db_association = db.query(models.UserAddress).filter(models.UserAddress.address == address, models.UserAddress.username == username).first()
        db.delete(db_association)
        db.commit()

    async def delete_by_user(db: Session, username):
        db_association = db.query(models.UserAddress).filter(models.UserAddress.username == username).all()
        map(db.delete, db_association)
        db.commit()


class TransactionRepo:
    async def create_transaction(db: Session, transaction: schemas.TransactionBase):   
        db_transaction = models.Transaction(tx_hash=transaction.tx_hash, block_height=transaction.block_height, time=transaction.time)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    async def create_value_transfer(db: Session, value_transfer: schemas.ValueTransferUndigested):
        next_id = db.query(models.ValueTransfer).count()
        db_value_transfer = models.ValueTransfer(transfer_id = next_id, tx_hash=value_transfer.tx_hash, 
            address=value_transfer.address, value=value_transfer.value)
        db.add(db_value_transfer)
        db.commit()
        db.refresh(db_value_transfer)
        return db_value_transfer

    def get_value_transfers(db: Session, tx_hash: str):
        return db.query(models.ValueTransfer).filter(models.ValueTransfer.tx_hash == tx_hash).all()

    def get_transaction(db: Session, tx_hash: str):
        return db.query(models.Transaction).filter(models.Transaction.tx_hash == tx_hash).first()

    def get_transactions_by_address(db: Session, address: str):
        return db.query(models.ValueTransfer).filter(models.ValueTransfer.address == address).all()

    async def delete_transaction(db: Session, tx_hash: str):
        db_transaction = db.query(models.Transaction).filter(models.Transaction.tx_hash == tx_hash).first()
        db.delete(db_transaction)
        # db.commit()

        db_value_transfer = db.query(models.ValueTransfer).filter(models.ValueTransfer.tx_hash == tx_hash).all()
        db.delete(db_value_transfer)

        db.commit()















