import os 
import base64
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import mnemonic
from algosdk import account

# user declared account mnemonics
creator_mnemonic = "speed learn provide enact month rival squeeze dentist ice excuse enhance level maid subway camera canal bean favorite pair monster frozen air urban ability color"
# ensuer this account is funded using TestNet dispenser: https://dispenser.testnet.aws.algodev.network/

# user declared algod connection parameters. 
# Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn) :
    private_key = mnemonic.to_private_key(mn)
    return private_key

# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait    
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return 
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:  
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)                   
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item['key']
        value = item['value']
        formatted_key = base64.b64decode(key).decode('utf-8')
        if value['type'] == 1:
            # byte string
            if formatted_key == 'voted':
                formatted_value = base64.b64decode(value['bytes']).decode('utf-8')
            else:
                formatted_value = value['bytes']
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value['uint']
    return formatted

# helper function to read app global state
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created:
        if app['id'] == app_id:
            return format_state(app['params']['global-state'])
    return {}
    
# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, \
                                            approval_program, clear_program, \
                                            global_schema, local_schema)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id, 500)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id:", app_id)

    return app_id

def main() :
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)

    # declare application state storage (immutable)
    global_ints = 5    # store "Holder"
    global_bytes = 5
    local_ints = 1      # for future use
    local_bytes = 0
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    # compile approval program to binary
    approval_program_compiled = compile_program(algod_client, open("./11_approval.teal").read())

    # compile clear program to binary
    clear_state_program_compiled = compile_program(algod_client, open("./11_clear.teal").read())

    print("--------------------------------------------")
    print("Deploying Holder application......")

    # create new application
    app_id = create_app(algod_client, creator_private_key, approval_program_compiled, clear_state_program_compiled, global_schema, local_schema)
    
    # store app_id in file
    path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path, "app.id"), "w") as f:
        f.write(str(app_id))
    
    # read global state of application
    print("Global state:", read_global_state(algod_client, account.address_from_private_key(creator_private_key), app_id))

main()