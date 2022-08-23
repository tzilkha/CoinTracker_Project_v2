"""

Server-side API
This file describes the methods to call to get the data needed from backend APIs.

"""

from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
import asyncio

import models
import schemas
from database import get_db, engine
from repositories import *

from scrape import get_txs_all, get_txs, clean_tx

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CoinTracker Demo App",
              description="Backend Project for user wallet and transaction tracking.",
              version="1.0.0", )

# For API Exceptions

@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})

# Create a new user

@app.post('/users/create_user', tags=["User"], response_model=schemas.User, status_code=201)
async def create_user(user_request: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a user and store it in the database
    """
    
    db_user = UserRepo.fetch_by_username(db, username=user_request.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already in use!")

    return await UserRepo.create_user(db=db, user=user_request)

# Get all users

@app.get('/users/all_users', tags=["User"], response_model=List[schemas.User], status_code=200)
def get_all_users(db: Session = Depends(get_db)):
    """
    Get all the users stored
    """
    return UserRepo.fetch_all(db)

# Delete a user

@app.delete('/users/remove_user', tags=["User"], status_code=200)
async def delete_user(username: str, db: Session = Depends(get_db)):
    """
    Delete a user by username
    """
    db_user = UserRepo.fetch_by_username(db, username=username)
    if db_user == None:
        raise HTTPException(status_code=400, detail="No user with such Username!")

    await UserRepo.delete(db=db, username=username)


    # We need to delete wallet associations
    db_associations = AssociationRepo.fetch_by_username(db, username=username)
    if db_user:
        await AssociationRepo.delete_by_user(db=db, username=username)


    return "User deleted successfully! (" + username + ")."

# Associate a wallet

@app.post('/wallets/add_wallet', tags=["Wallet"], status_code=201)
async def add_address(user_request: schemas.AssociationCreate, db: Session = Depends(get_db)):
    """
    Create a user and store it in the database

    Input - username and wallet address
    """

    # Check user exists first
    db_user = UserRepo.fetch_by_username(db, username=user_request.username)
    if db_user == None:
        raise HTTPException(status_code=400, detail="Can't associate, user doesn't exist!")


    response = ""

    db_wallet = WalletRepo.fetch_by_address(db=db, address=user_request.address)

    # Wallet doesn't exist
    if db_wallet == None:
        await WalletRepo.create_wallet(db=db, address=user_request.address)
        response += "Added wallet {} to the system.".format(user_request.address)

    else:
        response += "Wallet {} is already in the system.".format(user_request.address)

    db_association = AssociationRepo.fetch_association(db=db, address=user_request.address, username=user_request.username)

    # Association doesn't exist
    if db_association == None:
        await AssociationRepo.create_association(db=db, address=user_request.address, username=user_request.username)

        return response + " Associated {} to {}".format(user_request.address, user_request.username)

    else:
        raise HTTPException(status_code=400, detail = response + " Wallet {} already associated with {}!".format(user_request.address, 
            user_request.username))

# Get all wallets of a user

@app.get('/wallets/query_wallets', tags=["Wallet"], response_model=List[schemas.Wallet], status_code=200)
def get_all_wallets(username: str, db: Session = Depends(get_db)):
    """
    Get all wallets associated with a username
    """
    # Check user exists first
    db_user = UserRepo.fetch_by_username(db, username=username)
    if db_user == None:
        raise HTTPException(status_code=400, detail="Username doesn't exist!")

    # Convert associations to wallets
    addresses = [entry.address for entry in AssociationRepo.fetch_all_addresses(db=db, username=username)]
    return WalletRepo.fetch_by_addresses(db, addresses = addresses)

# Get all users associated with a wallet

@app.get('/wallets/query_users', tags=["Wallet"], response_model=List[schemas.User], status_code=200)
def get_all_users(address: str, db: Session = Depends(get_db)):
    """
    Get all users associated with a wallet
    """
    # Check wallet first
    db_user = WalletRepo.fetch_by_address(db, address=address)
    if db_user == None:
        raise HTTPException(status_code=400, detail="Address not tracked!")

    # Convert associations to users
    users = [entry.address for entry in AssociationRepo.fetch_all_addresses(db=db, username=username)]
    return UserRepo.fetch_by_usernames(db, usernames = users)

# Delete an association

@app.delete('/wallets/remove', tags=["Wallet"], status_code=200)
async def remove_wallet(username: str, address: str, db: Session = Depends(get_db)):
    """
    Delete an association
    """
    # Check wallet first
    db_wallet = WalletRepo.fetch_by_address(db, address=address)
    if db_wallet == None:
        raise HTTPException(status_code=400, detail="Address not tracked!")

    # Check user exists first
    db_user = UserRepo.fetch_by_username(db, username=username)
    if db_user == None:
        raise HTTPException(status_code=400, detail="Username doesn't exist!")


    # Remove association if exists
    db_association = AssociationRepo.fetch_association(db=db, address=address, username=username)
    if db_association == None:
        raise HTTPException(status_code=400, detail="{} not associated with {}.".format(address, username))

    else:
        await AssociationRepo.delete_association(db=db, username=username, address=address)

    return "{} removed successfully from {}!".format(address, username)

# Update wallet

@app.post('/wallets/update', tags=["Update"], status_code=201)
async def update_wallet(address: str, db: Session = Depends(get_db)):
    import time
    LIMIT = 100
    DELAY = 11

    # Check wallet has been created in the first place for tracking
    db_wallet = WalletRepo.fetch_by_address(db, address=address)
    if db_wallet == None:
        raise HTTPException(status_code=400, detail="Address not tracked!")

    last_sync = db_wallet.last_sync
    last_n_txs = db_wallet.n_txs

    print("Last Synced {} at {} with {} txs".format(address, last_sync, last_n_txs))

    # Instead of doing the get all function, lets

    new_n_txs = last_n_txs
    new_balance = db_wallet.balance

    got_all = False

    while not got_all:

        # Scrape a page
        txs = get_txs(address, offset = new_n_txs, limit = LIMIT)

        # We already know the current final balance of the account
        new_balance = txs['final_balance']

        for tx in txs['txs']:
            # Clean tx and extract useful information
            tx = clean_tx(tx)
            tx_hash = tx['hash']
            tx_time = tx['time']
            block_height = tx['block_height']

            # Check if transaction exists:
            db_tx = TransactionRepo.get_transaction(db, tx_hash)
            # if not we update this transaction
            if db_tx == None:

                # Insert transaction information
                tx_info = schemas.TransactionBase(**{'tx_hash':tx_hash, 'time':tx_time, 'block_height':block_height})
                await TransactionRepo.create_transaction(db, tx_info)

                # Get value transfers (inputs is negative, outputs is positive)
                v_t = [{'tx_hash':tx_hash, 'address':vt['addr'], 'value':vt['value']*-1} for vt in tx['inputs']]
                v_t += [{'tx_hash':tx_hash, 'address':vt['addr'], 'value':vt['value']} for vt in tx['outputs']]

                print("Inserting {} value transfers.".format(len(v_t)))
                # Insert value transfer information
                for vt in v_t:
                    await TransactionRepo.create_value_transfer(db, schemas.ValueTransfer(**vt))

                # Moving count of n_txs
                new_n_txs += 1

                # Update the wallet information
                print("Updating wallet information.")
                new_sync = int(time.time())
                await WalletRepo.update_n_txs(db, address=address, n_txs=new_n_txs)
                await WalletRepo.update_balance(db, address=address, balance=new_balance)
                await WalletRepo.update_sync_time(db, address=address, time=new_sync)

        # End condition otherwise sleep (cos blockchain.com API)
        if len(txs['txs']) < LIMIT: got_all = True
        else: 
            print('Time delay...')
            time.sleep(DELAY)
            print('Time delay done.')

    # As a safe in case nothing new came in, we still update the sync time
    new_sync = int(time.time())
    await WalletRepo.update_sync_time(db, address=address, time=new_sync)

    return "Successfully upated {}. Number of transactions: {}. Current Balance: {}.".format(address, 
        new_n_txs, new_balance)

# Update all user's wallets

@app.post('/wallets/update_user_wallets', tags=["Update"], status_code=201)
async def update_user_wallets(username: str, db: Session = Depends(get_db)):

    # Get users wallets
    wallets = get_all_wallets(username, db)
    
    # update them
    for w in wallets:
        await update_wallet(w.address, db)

    return "Successfully updated {} wallets for user {}. {}".format(len(wallets), username, [w.address for w in wallets])

# Get transaction information

@app.get('/transactions/get_transaction', response_model=schemas.Transaction, tags=["Transaction"], status_code=200)
async def get_transaction(tx_hash: str, db: Session = Depends(get_db)):

    # First check we recorded this transaction
    db_transaction = TransactionRepo.get_transaction(db, tx_hash=tx_hash)
    if db_transaction == None:
        raise HTTPException(status_code=400, detail="This transaction is not recorded!")

    db_transaction = db_transaction.__dict__

    # Lets get the value transfers for this transaction
    db_value_transfers = TransactionRepo.get_value_transfers(db, tx_hash=tx_hash)

    return schemas.Transaction(**{**db_transaction, 'value_transfers':db_value_transfers})

# Get transaction information for wallet

@app.get('/transactions/get_user_transactions', response_model=List[schemas.Transaction], tags=["Transaction"], status_code=200)
async def get_user_transactions(username: str, offset: int = 0, db: Session = Depends(get_db)):

    # Last transactions (since this is a lot of information)
    LIMIT = 50

    # Check user exists first
    db_user = UserRepo.fetch_by_username(db, username=username)
    if db_user == None:
        raise HTTPException(status_code=400, detail="Username doesn't exist!")

    # Convert associations to wallets
    addresses = [entry.address for entry in AssociationRepo.fetch_all_addresses(db=db, username=username)]

    tx_hashes = []

    # Get the corresponding transactions which involve an address
    for addr in addresses:
        db_value_transfers = TransactionRepo.get_transactions_by_address(db=db, address=addr)

    # Get unique hashes
    tx_hashes = list(set([vt.tx_hash for vt in db_value_transfers]))
    # Get most recent
    tx_hashes = tx_hashes[max(0, len(tx_hashes) - offset - LIMIT) : max(len(tx_hashes), len(tx_hashes) - offset)]

    # Get transaction information including value transfers for each hash
    return [await get_transaction(h, db) for h in tx_hashes]



if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)




