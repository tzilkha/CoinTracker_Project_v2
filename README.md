# CoinTracker_Project

08/22/22
Tal Zilkha

## Setup


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


### Value Transfer table (relationship table)

The Value Transfer table keeps track of the participation of the addresses within a transaction, that is their address and value gained or loss.

<tx_hash> <address> <val>



## Server-side API

USER

POST create_user
DELETE delete_user
GET get_user
GET get_all_users


WALLET

POST add_wallet
DELETE remove_wallet
GET get_wallets_by_user
GET get_users_by_wallet

GET wallet_transactions



UPDATE

POST update_wallet
POST update_user_wallets




























