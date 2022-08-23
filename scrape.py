import requests as req
import json
import time

# Helper function to scrape transaction data that contains an address 
def get_txs(add, offset=0, limit=100):
    query = 'https://blockchain.info/rawaddr/{}?limit={}&offset={}'.format(add, limit, offset)
    print(query)
    
    res = req.get(query) 
    print(res)

    if res.status_code != 200:
        print('Error scraping - code:', res.status_code, '- reason:', res.reason)
        return None

    res_json = json.loads(res.content)
    
    return res_json

# Extract only the information we care about
# we use the .get function to safely extract data, it could be that there are addresses missing
# or other relevant fields missing.
def clean_tx(tx):
	return {'hash': tx.get('hash', ''),
		     'time': tx.get('time', 0),
		     'fee': tx.get('fee', 0),
		     'block_height': tx.get('block_height', 0),
		     'inputs': [{'addr': inp.get('prev_out', {'addr':''}).get('addr', ''), 
		                 'value':inp.get('prev_out', {'value':0}).get('value', 0)} \
		                for inp in tx.get('inputs', [])],
		     'outputs': [{'addr': outp.get('addr', ''), 'value':outp.get('value', 0)} \
		                for outp in tx.get('out', [])]
		    }

# Function to scrape all transasctions that involve an address
# optional parameter offset to only check beyond n transactions
def get_txs_all(add, offset=0, limit=100, delay=11):
    
    # condition to stop querying
    got_all = False
    
    txs = []
    n_txs, final_balance = None, None
    
    while not got_all:
        res = get_txs(add, offset, limit)
        
        # Error occured
        if res == None:
            return None
        
        # Get only the information we need to store from each transaction

        for tx in res.get('txs', []):
            txs += [clean_tx(tx)]

        # Some more useful information to scrape
        if n_txs == None: 
            n_txs = res.get('n_tx', None)
            final_balance = res.get('final_balance', None)
            
        # Last result didn't max at the limit, there must be no more results.
        if len(res.get('txs', [])) < limit:
            got_all = True

        # API requests not to query more than once every 10 seconds
        else: 
            offset += limit
            time.sleep(delay)
           
    return {'n_txs': n_txs, 'final_balance': final_balance, 'txs': txs}

    