from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base

# Define DB

class User(Base):
	__tablename__ = "user"

	username = Column(String, primary_key=True, unique=True, index=True)
	name = Column(String)

	wallets = relationship('UserAddress', cascade='all, delete-orphan')


class Wallet(Base):
	__tablename__ = "wallet"

	address = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
	last_sync = Column(Integer)
	balance = Column(Integer)
	n_txs = Column(Integer)
	# users = relationship('UserAddress', cascade='all, delete-orphan')


class UserAddress(Base):
	__tablename__ = "user_address"

	association_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
	username = Column(String, ForeignKey('user.username'))
	address = Column(String, ForeignKey('wallet.address'))

class Transaction(Base):
	__tablename__ = "transaction"

	tx_hash = Column(String, primary_key=True, unique=True, index=True)
	block_height = Column(Integer)
	time = Column(Integer)

	value_transfers = relationship('ValueTransfer', cascade='all, delete-orphan')

class ValueTransfer(Base):
	__tablename__ = "value_transfer"

	transfer_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
	tx_hash = Column(String, ForeignKey('transaction.tx_hash'))
	address = Column(String)
	value = Column(Integer)
