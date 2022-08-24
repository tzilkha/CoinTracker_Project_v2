from typing import List, Optional
from pydantic import BaseModel

# pydantic schemas

class UserBase(BaseModel):
    username: str
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):

    class Config:
        orm_mode = True

class UserDelete(BaseModel):
    username: str

class UserUpdate(UserDelete):
    pass

class WalletBase(BaseModel):
    address: str
    last_sync: int
    n_txs: int

class WalletAdd(WalletBase):
    username: str

    class Config:
        orm_mode = True

class WalletRemove(BaseModel):
    address: str
    username: str

class WalletUpdate(BaseModel):
    address: str

class Wallet(WalletBase):

    class Config:
        orm_mode = True

class AssociationBase(BaseModel):
    address: str
    username: str

class AssociationCreate(AssociationBase):
    pass

class Association(AssociationBase):

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    tx_hash: str
    time: int
    block_height: int

class ValueTransferUndigested(BaseModel):
    tx_hash: str
    address: str
    value: int

class ValueTransfer(ValueTransferUndigested):
    transfer_id: int

    class Config:
        orm_mode = True

class Transaction(TransactionBase):
    value_transfers: List[ValueTransfer] = []

    class Config:
        orm_mode = True


    
