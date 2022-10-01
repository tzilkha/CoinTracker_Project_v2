# WalletTracker

08/22/22
Tal Zilkha

## Architecture and Assumptions

We will be creating a database to hold all information on users, addresses, user-address relations and transactions that we are storing.

A server-side API will serve a potential front end and also devs with the ability to create a user, add wallets to that user, and get transactional information for that particular wallet.

We choose to sync transactional data not automatically as transactions are not a very frequent behavior. But of course, as a platform like this scales, it could be that fetching transaction data frequently will result in new data being frequently added as the number of users grows. Additionally, in production, it may be the case that we do not want to update as the user fetches information as this would cause user experience to be potentially slow if they haven't used the service in a while. For that we would also change the architecture to work automatically. For this implementation, we will leave API calls to be as generic as possible so that automation could be easily implemented in the future.

We will use an SQL database as the data is relational heavy. For the server-side API implementation, we will use the Fast-API and SQLAlchemy frame-work for database maintaining and API calls.

We are using the Requests library for scraping data specifically from the blockchain.com API.


## Database


The data is relationally heavy, we opt to use an SQL DB.

We define 4 tables.

[User Table] [User-Wallet Table] [Wallets Table] [Transactions Table] [Value Transfer]

### User table

The User table is a straightforward table to keep track of user information. A new user in the system can create a new user with his information. We will not add log-in functionality for the purposes of this demo, nor ask for email etc. Knowing your username will be enough to use this prototype.

<username> <name>

Username will act as a unique primary key.

### Wallets table

The wallets table will help us keep track of how much data we must scrape when transaction data is being requested, we do this by looking at the number of transactions (recorded), this will help us use an offset when scraping, this is to keep us form doing double work. Additionally when calculating the balance for a wallet, We do not need to recalculate transactions we have already checked, so we could take the value at that point and calculate from there.

<address> <last_sync> <balance> <n_txs>

Address will act as a unique primary key.

- For the future, it would be smart to keep track of transaction hashes for the addresses we are looking at, if a user is deleted with an address that is singularly connected to a transaction hash (that is, no other address we keep track of is also associated with that transaction) we could delete that transaction from the transactions table, to save time, we leave this functionality for future work.

### User-address table

Each user may be associated to multiple wallet addresses and multiple wallet addresses may be associated with multiple users. This table maintains the relationship between a username and its tracked wallets. The reason for this association is that we wish to display the information from all associated wallets to the requesting user. For this cause, we use a many-to-many table.

<association_id> <username> <address>

The association_id will be a generated index and primary key. We do not need it but could help in the future and is also necessary within the SQLAlchemy framework.

### Transaction table

The Transaction table will keep track of transaction hashes and some useful information on the transaction. Since transactions on bitcoin can be from multiple people to multiple people, we opt to use another table to show value transfers of individual wallet addresses separate. Here the primary key is the transaction hash.

<tx_hash> <total_val> <time> <block>


### Value Transfer table

The Value Transfer table keeps track of the participation of the addresses within a transaction, that is their address and value gained or loss.

<tx_hash> <address> <val>

There is no indicator of whether the address was form or two, we simply look at the value, if it is negative, that address was an input in the transaction, if positive, an output.

## Server-side API

### USER

POST create_user [Complete]

This API call will take in a username and a name. If that username is not taken, it will create a new user entry with the given information.

DELETE delete_user [Complete]

This API call will take in a username and delete the corresponding entry for it. Additionally, it will delete all association information to tracked wallets.

GET user [Incomplete]

This API call will return user information based on username. Not critical for the purposes of this demo.

GET all_users [Complete]

This API call returns the information on all the users. More advanced queries and API calls can be generated but this API call is more of a dev debugging tool than anything.

### WALLET

POST add_wallet [Complete]

This API call adds a wallet, it takes in an address and a username. If a wallet entry is not created for this address (the wallet is not yet tracked), it instantiates one, and sets the transaction number and last updated time to 0. The call then associates the wallet to the username if it isn't already.

DELETE remove_wallet [Complete]

This API call removes an association between a wallet and a user. It takes a wallet and a user as parameters.

GET query_wallets [Complete]

This API call returns all the wallets given a username. All the wallets that are associated to that user, that is.

GET get_users_by_wallet [Complete]

This API call returns all usernames associated to a given wallet address. This is more of an admin API call.


### UPDATE
These are scraping API calls.

POST update [Complete]

This API call will update transactional information of a given address to the database. Since we keep note of the amount of transactions stored for a given wallet, we only search for results post those transactions and update.

POST update_user_wallets [Complete]

This API call will go through all the wallet addresses associated with the given username and update transactional information for them.

### TRANSACTION

GET transaction [Complete]

This API call returns all transactional information off a given transaction hash. That is, the general information of the transaction and also the value transfer information.

DELETE transaction [Incomplete]

This API call deletes a transaction and its corresponding value transfer information.

GET get_wallet_transactions [Complete]

This API call returns all transactional information given a username. This includes the transaction information as well as value transfer information of those transactions. The call finds the associated wallets of that user and then one by one checks which transactions contain these addresses and then finds the complete transaction information for those transactions.

This is a lot of data so offsetting and limiting results is a must.



## Usage

The project was done in a virtual environment that is made easy to replicate.

(This assumes git clone was done first, in that directory...)

1. Create a virtual environment

	\# If machine doesn't have virtualenv
	pip3 install virtualenv

	\# Create environment
  	python3 -m venv tz_demo/venv

2. Activate environment

	source tz_demo/venv/bin/activate

2. Install dependencies

	pip3 -r requirements.txt

3. Run main to initialize DB and run API server

	python3 main.py

4. Look at the API documentation

	at - http://localhost:9000/docs#/

	\# This is also a playground to play with the API. Of course CURL calls can be made for more automatic testing, CURL calls can be copied straight from documentation.

5. Close the DB and API server

	\# Simply stop the execution

6. Deactivate virtual environment

	deactivate


## Afterthoughts

This working prototype has many areas for optimization and problems which could be easily fixed given time.

- Database relations for robustness and optimization

Perhaps the biggest addition for future work is implementing logic for data relations within the SQL table. This will optimize the robustness, security, and performance of the DB. By linking account IDs to the account-address table, for instance, we can use this dependency to simply remove wallet data which is no longer linked to any account (removed from deletion or address removal). Relations such as these also prevent redundant data and further optimizes resources and performance.

- Optimization through keeping track of address-transaction hash relations

At its current state, we find all transactions linked to an address by going through all value transfers and finding specific addresses, instead we could link addresses to transaction hashes to easily get transactional data for addresses instead of going through once to find transaction hashes and then querying again to re-complete the transaction data.

- Threading for better performance

The scraping calls are currently done on the main thread of the API server. When a user calls to update his wallet information, he must wait for a response, this can take an immense amount of time, especially if his wallet address' transaction count is in the thousands. A smarter way to approach this is to thread this operation and not have the user wait for any response that it's complete.

- Boolean update status fields

Following the threading logic, there could be discrepancies in results shown to a user if the backend is still processing data into its database. We could have a boolean indicator for whether a particular address is being processed, and if that is the case, we can prevent showing results to the user. Once, backend processing is complete, the indicator can be switched and the user can access information safely.

- API security and authority control

A lot of the API calls implemented in this demo are not to be used by any user. Specific API calls should be gated for dev-only and some based on credentials given by a user. Only a user who owns an account should be able to add a wallet to it and only devs should be able to see all user information, for example. A simple login mechanism with credentials information on the account table could be a fix. Additionally, creating admin accounts and gating particular API calls would increase safety.

- More data maintenance

There is currently an issue with gettin transaction data on a wallet address. Information returned is not sorted at the moment so the user is displayed with a maximum of 50 random transactions, there are a number of possible fixes to this, for example - merge in the query with transaction data to get the time as well and order it by that when getting the most recent results.

- Automatic data update

I have realized that it would increase the user experience immensely if scraping was done automatically so that the user doesn't have to wait a long time for his data to show up. A short script that updates every few minutes and goes through all wallet addresses and updates them would do the trick - unless a user attempts to see his data, we could have an additional update call on these events.

- Test script

I am currently missing a test script to automate testing conditions for the DB. This is high priority for future work.

## Conclusion

I was extremely happy to work on this project, even though it is far from my realm of expertise. As a statistician and ML engineer by education, my knowledge revolves heavily around AI and statistical models rather than database and API specification and creation. But unfortunately, I felt as though there was not much room for pure statistics in this project.

The part I felt most comfortable working on was the web scraping portion, which didn't take longer than 30 minutes to set up and test.

The extent of my knowledge on databases goes as far as a University course I took over three years ago and for APIs a course I took on AWS (lambda functions, gateways, and DynamoDB). I have never used pydantic, Fast-API nor SQLAlchemy, but as I was starting off from almost a clean slate in terms of my confidence to use those tools again, I thought these would be easiest as I am the most proficient in Python. I am extremely happy that I did, these are extremely powerful libraries which I would like to keep learning about and add to my toolkit.


