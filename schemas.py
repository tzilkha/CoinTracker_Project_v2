from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):

    class Config:
        orm_mode = True



class WalletBase(BaseModel):
    address: str
    last_sync: int
    n_txs: int

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

class ValueTransfer(BaseModel):
    transfer_id: int
    tx_hash: str
    address: str
    value: int

    class Config:
        orm_mode = True

class Transaction(TransactionBase):
    value_transfers: List[ValueTransfer] = []

    class Config:
        orm_mode = True





# class ValueTransfer(BaseModel):
#     inp: Address
#     outp: Address
#     value: int

# class Transaction(BaseModel):
#     tx_hash: str

# class TransactionCreate(Transaction):
#     time: int
#     block_height: int
#     transfers: List[ValueTransfer] = []
    
