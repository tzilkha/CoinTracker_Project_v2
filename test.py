import requests as req
import json

def res_print(response):
	print('Response:', response.status_code)
	response = json.loads(response.content)
	print('Content:', response)

def res_content(response):
	return json.loads(response.content)

base_url = 'http://localhost:9000'

headers = {
	'accept': 'application/json',
    'Content-Type': 'application/json'
}

ADD1 = '3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd'
ADD2 = 'bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5'
ADD3 = '12xQ9k5ousS8MqNsMBqHKtjAtCuKezm2Ju'


# Create users
# We will create 5 users

for i in range(1, 6):

	data = {
		'username': 'user_' + str(i),
		'name': 'user_' + str(i) + '_name'
	}
	 
	print('-- Created User', i)
	response = req.post(base_url + '/users/create_user', headers=headers, json=data)

	# res_print(response)
	assert(res_content(response) == {'username': 'user_' + str(i), 'name': 'user_' + str(i) + '_name'})



# Lets see the users

print('-- Getting all users')
response = req.get(base_url + '/users/all_users', headers=headers)
# res_print(response)

assert(res_content(response) == [{'username': 'user_' + str(i), 'name': 'user_' + str(i) + '_name'} for i in range(1, 6)])



# Lets delete user 5 twice and make sure we get an error the second time

data = {
	'username': 'user_5'
}

print('-- Deleted User 5')
response = req.delete(base_url + '/users/remove_user', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == 'User deleted successfully! (user_5).')




# Lets see the users after delete

print('-- Getting all users')
response = req.get(base_url + '/users/all_users', headers=headers)
# res_print(response)

assert(res_content(response) == [{'username': 'user_' + str(i), 'name': 'user_' + str(i) + '_name'} for i in range(1, 5)])




# Lets delete a user that has been deleted

data = {
	'username': 'user_5'
}

print('-- Deleted User 5')
response = req.delete(base_url + '/users/remove_user', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'detail': 'No user with such Username!'})




# Lets try to add a user with a username that exists

data = {
	'username': 'user_1',
	'name': 'user_1_name'
}
 
print('-- Creating User 1')
response = req.post(base_url + '/users/create_user', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'detail': 'Username already in use!'})




# Lets add wallet 1 to users 1 and 2

data = {
	'username': 'user_1',
	'address': ADD1
}

print('-- Adding {} to {}.'.format(ADD1, 'user_1'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'address': ADD1, 'last_sync': 0, 
	'n_txs': 0, 'username': 'user_1'})

data = {
	'username': 'user_2',
	'address': ADD1
}

print('-- Adding {} to {}.'.format(ADD1, 'user_2'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'address': ADD1, 'last_sync': 0, 
	'n_txs': 0, 'username': 'user_2'})




# Lets add wallet 2 to users 1 and 3

data = {
	'username': 'user_1',
	'address': ADD2
}

print('-- Adding {} to {}.'.format(ADD2, 'user_1'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'address': ADD2, 'last_sync': 0, 
	'n_txs': 0, 'username': 'user_1'})

data = {
	'username': 'user_3',
	'address': ADD2
}

print('-- Adding {} to {}.'.format(ADD2, 'user_3'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'address': ADD2, 'last_sync': 0, 
	'n_txs': 0, 'username': 'user_3'})



# Lets add wallet 3 to user 3

data = {
	'username': 'user_3',
	'address': ADD3
}

print('-- Adding {} to {}.'.format(ADD3, 'user_3'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)
# res_print(response)

assert(res_content(response) == {'address': ADD3, 'last_sync': 0, 
	'n_txs': 0, 'username': 'user_3'})



# Lets try adding walet 3 to user 3 again

data = {
	'username': 'user_3',
	'address': ADD3
}

print('-- Adding {} to {}.'.format(ADD3, 'user_3'))
response = req.post(base_url + '/wallets/add_wallet', headers=headers, json=data)

assert(res_content(response) == {'detail': ' Wallet {} already associated with {}!'.format(ADD3, 'user_3')})




# Lets get the wallets of user 1,2,3

data = {
	'username': 'user_3',
}

print('-- Getting wallets of {}.'.format(data['username']))
response = req.get(base_url + '/wallets/query_wallets?username=' + data['username'], headers=headers)

expected = [{'address': ADD2, 'last_sync': 0, 'n_txs': 0}, {'address': ADD3, 'last_sync': 0, 'n_txs': 0}]
assert [i for i in expected if i not in res_content(response)] == []

data = {
	'username': 'user_2',
}

print('-- Getting wallets of {}.'.format(data['username']))
response = req.get(base_url + '/wallets/query_wallets?username=' + data['username'], headers=headers)

expected = [{'address': ADD1, 'last_sync': 0, 'n_txs': 0}]
assert [i for i in expected if i not in res_content(response)] == []

data = {
	'username': 'user_1',
}

print('-- Getting wallets of {}.'.format(data['username']))
response = req.get(base_url + '/wallets/query_wallets?username=' + data['username'], headers=headers)

expected = [{'address': ADD1, 'last_sync': 0, 'n_txs': 0}, {'address': ADD2, 'last_sync': 0, 'n_txs': 0}]
assert [i for i in expected if i not in res_content(response)] == []




# Lets get all accounts associated with addresses 1, 2, 3

data = {
	'address': ADD1
}

print('-- Getting users with address {}.'.format(data['address']))
response = req.get(base_url + '/wallets/query_users?address=' + data['address'], headers=headers)

expected = [{'username': 'user_1', 'name': 'user_1_name'}, {'username': 'user_2', 'name': 'user_2_name'}]
assert [i for i in expected if i not in res_content(response)] == []

data = {
	'address': ADD2
}

print('-- Getting users with address {}.'.format(data['address']))
response = req.get(base_url + '/wallets/query_users?address=' + data['address'], headers=headers)

expected = [{'username': 'user_1', 'name': 'user_1_name'}]
assert [i for i in expected if i not in res_content(response)] == []

data = {
	'address': ADD3
}

print('-- Getting users with address {}.'.format(data['address']))
response = req.get(base_url + '/wallets/query_users?address=' + data['address'], headers=headers)

expected = [{'username': 'user_3', 'name': 'user_3_name'}]
assert [i for i in expected if i not in res_content(response)] == []




# Lets dissociate address 1 with user 1

data = {
	'address': ADD1,
	'username': 'user_1'
}

print('-- Deleting address {} from user {}.'.format(data['address'], data['username']))
response = req.delete(base_url + '/wallets/remove', headers=headers, json=data)

assert (res_content(response) == '{} removed successfully from {}!'.format(data['address'], data['username']))




# Lets see the wallets associated with user 1

data = {
	'username': 'user_1',
}

print('-- Getting wallets of {}.'.format(data['username']))
response = req.get(base_url + '/wallets/query_wallets?username=' + data['username'], headers=headers)

expected = [{'address': ADD2, 'last_sync': 0, 'n_txs': 0}]
assert [i for i in expected if i not in res_content(response)] == []




# Lets see the wallets associated with address 1

data = {
	'address': ADD1
}

print('-- Getting users with address {}.'.format(data['address']))
response = req.get(base_url + '/wallets/query_users?address=' + data['address'], headers=headers)

expected = [{'username': 'user_2', 'name': 'user_2_name'}]
assert [i for i in expected if i not in res_content(response)] == []




# Lets try to delete address 1 again from user 1

data = {
	'address': ADD1,
	'username': 'user_1'
}

print('-- Deleting address {} from user {}.'.format(data['address'], data['username']))
response = req.delete(base_url + '/wallets/remove', headers=headers, json=data)

assert (res_content(response) == {'detail': '{} not associated with {}.'.format(data['address'], data['username'])})




# Lets try to delete a fake address from 1

data = {
	'address': 'fake address',
	'username': 'user_1'
}

print('-- Deleting address {} from user {}.'.format(data['address'], data['username']))
response = req.delete(base_url + '/wallets/remove', headers=headers, json=data)

assert (res_content(response) == {'detail':"Address not tracked!"})




# Lets try to delete address 1 from a user that doesnt exist

data = {
	'address': ADD1,
	'username': 'fake user'
}

print('-- Deleting address {} from user {}.'.format(data['address'], data['username']))
response = req.delete(base_url + '/wallets/remove', headers=headers, json=data)

assert (res_content(response) == {'detail':"Username doesn't exist!"})




# Lets update an address that isnt tracked

data = {
	'address': 'fake address',
}

print('-- Updating address {}.'.format(data['address']))
response = req.post(base_url + '/wallets/update', headers=headers, json=data)

assert (res_content(response) == {'detail':"Address not tracked!"})




# Lets update address 1

# data = {
# 	'address': ADD1,
# }

# print('-- Updating address {}.'.format(data['address']))
# response = req.post(base_url + '/wallets/update', headers=headers, json=data)

# res_print(response)




# Lets update addresses of user 2

data = {
	'username': 'user_2',
}

print('-- Getting wallets of {}.'.format(data['username']))
response = req.get(base_url + '/wallets/query_wallets?username=' + data['username'], headers=headers)

res_print(response)




# Lets update addresses for user 1

data = {
	'username': 'user_1'
}

print('-- Updating wallets of {}.'.format(data['username']))
response = req.post(base_url + '/wallets/update_user_wallets', headers=headers, json=data)

expected = "Successfully updated 1 wallets for user {}. [\'{}\']".format(data['username'], ADD2)

assert (res_content(response) == expected)



# Get all transactions for user 1

data = {
	'username': 'user_1'
}

print('-- Getting transactions of {}.'.format(data['username']))
response = req.get(base_url + '/transactions/get_user_transactions?username=' + data['username'], headers=headers)

res_print(response)






