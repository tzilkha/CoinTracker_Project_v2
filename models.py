from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    username = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String)

class Wallet(Base):
	__tablename__ = "wallet"

	address = Column(String, primary_key=True, unique=True, index=True)
	last_sync = Column(Integer)
	balance = Column(Integer)
	n_txs = Column(Integer)

class UserAddress(Base):
	__tablename__ = "user_address"

	association_id = Column(Integer, primary_key=True, unique=True, index=True)
	username = Column(String)
	address = Column(String)

class Transaction(Base):
	__tablename__ = "transaction"

	tx_hash = Column(String, primary_key=True, unique=True, index=True)
	block_height = Column(Integer)
	time = Column(Integer)

class ValueTransfer(Base):
	__tablename__ = "value_transfer"

	transfer_id = Column(Integer, primary_key=True, unique=True, index=True)
	tx_hash = Column(String)
	address = Column(String)
	value = Column(Integer)