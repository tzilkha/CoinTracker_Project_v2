# CoinTracker_Project

08/22/22
Tal Zilkha

## Architecture and Assumptions

We will be creating a database to hold all infromation on users, addresses, user-address relations and transactions that we are storing.

A server-side API will serve a potential front end with the ability to create a user, add wallets to that user, and get transasctions for that particular wallet.

We choose to sync transactional data not automatically as transactions are not a very frequent behaviour. But of course, as a platform like this scales, it could be that fetching transaction data frequently will result in new data frequently as the number of users grows. Additionally, in production, it may be the case that we do not want to update as the user fetches information as this would cause user experience to be potentially slow if they haven't used the service in a while. For that we would also change the architecture to work automatically. For this implementation, we will leave API calls to be as generic as possible so that automation could be easily implemented in the future.

We will use an SQL database as the data is relational heavy. For the server-side API implementation, we will use the Fast-API workframe.

We are using the SQLAlchemist library and FastAPI library for database maintaining and API calls.
We are using the Requests library for scraping data specifically from the blockchain.com API.


## Database


The data is relationally heavy, we opt to use an SQL DB.

We define 4 tables.

[User Table] [User-Wallet Table] [Wallets Table] [Transactions Table]

### User table

The User table is a straightforward table to keep track of user information. A new user in the system can create a new user with his information. We will not add log in funtionality for the purposes of this demo, nor ask for email etc. Knowing your username will be enough to use this prototype.

<username> <name>

### Wallets table

The wallets table will help us keep track of how much data we must scrape when transaction data is being requested, we do this by looking at the number of transaction (recorded), this will help us use an offset when scraping, this is to keep us form doing double work. Additionally when calculating the balance for a wallet, We do not need to recalculate transactions we have already checked, so we could take the value at that point and calculate from there.

<address> <last_sync> <balance> <n_txs>

- For the future, it would be smart to keep track of transaction hashes for the addresses we are looking it, if a user is deleted with an address that is singularly connected to a transaction hash (that is, no other address we keep track of is also associated with that transaction) we could delete that transaction from the transactions table, to save space, we leave this functionality for future work.

### User-Wallet table

Each user may be associated to multiple wallet addresses and multiple wallet addresses may be associated with multiple users. This table maintains the relationship between a username and its tracked wallets. The reason for this association is that we wish to display the information from all associated wallets to the requesting user. For this cause, we use a many-to-many table.

<username> <address>


### Transaction table

The Transaction table will keep track of transaction hashes and some useful information on the transaction. Since transactions on bitcoin can be from multiple people to multiple people, we opt to use another table to show value transfers of individual wallet addresses separated. Here the primary key is the transaction hash.

<tx_hash> <total_val> <time> <block>


### Value Transfer table

The Value Transfer table keeps track of the participation of the addresses within a transaction, that is their address and value gained or loss.

<tx_hash> <address> <val>



## Server-side API

### USER

POST create_user [Complete]

This API call will take in a username and a name. If that username is not taken, it will create a new user entry with the given information.

DELETE delete_user [Complete]

This API call will take in a username and delete the corresponding entry for it. Additionally,
it will delete all association information to tracked wallets.

GET user [Incomplete]

This API call will return user information based on username. Not critical for the purposes of this demo.

GET all_users [Complete]

This API call returns the information on all the users. More advanced querys and API calls can be generated but this API call is more of a debugging tool than anything.

### WALLET

POST add_wallet [Complete]

This API call adds a wallet, it takes in an address and a username. If a wallet entry is not created for this address (the wallet is not yet tracked), it instantiates one, and sets the transaction number and last updated  time to 0. The call then associates the wallet to the username if it isn't already.

DELETE remove_wallet [Complete]

This API call removes an association between a wallet and a user. It takes a wallet and a user as parameters.

GET query_wallets [Complete]

This API call returns all the wallets given a username. All the wallets that are associated to that user, that is.

GET get_users_by_wallet [Complete]

This API call returns all usernames associated to a given wallet address. This is more of an admin API call.


### UPDATE
These are scraping API calls.

POST update [Complete]

This API call will update transactional informaiton of a given address to the database. Since we keep note of the amount of transactions stored for a given wallet, we only search for results post those transactions and update.

POST update_user_wallets [Complete]

This API call will go through all the wallet addresses associated with the given username and update transactional information for them.

### TRANSACTION

GET transaction [Complete]

This API call returns all transactional information of a given transaction hash. That is, the general information of the transaction and also the value transfer information.

DELETE transaction [Incomplete]

This API call deletes a transaction and its corresponding value transfer information.

GET get_wallet_transactions [Complete]

This API call returns all transactional information given a username. This includes the transaction information as well as value transfer information of those transactions. The call find the associated wallets of that user and then one by one checks which transactions contain these addresses and then find the complete transaction information for those transactions.

This is a lot of data so offseting and limiting results is a must.



## Usage

The project was done in a virtual environment that is made easy to replicate.

(This assumes git clone was done first, in that directory...)

1. Create a virtual environment

	\# If machine doesn't have virtualenv
	pip3 install virtualenv

	\# Create environment
  	virtualenv tz_project source tz_project/venv/bin/activate

2. Install dependencies

	pip3 -r requirements.txt

3. Run main to initialize DB and run API server

	python3 main.py

4. Look at the API documentation

	at - http://localhost:9000/docs#/

	\# This is also a playground to play with the API. Of course curl calls can be made for more automatic testing, curl calls can be copied straight from documentation.

5. Close the DB and API server

	\# Simply stop the execution

6. Deactivate virtual environment

	deactivate


## Afterthoughts





























