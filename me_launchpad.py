from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from anchorpy import Program, Wallet, Provider, Coder
import asyncio
import init_launchpad
import time
import subprocess
import asyncio
import cf_cloudscraper
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from solana.rpc import commitment, types
from solana.blockhash import Blockhash
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from spl.token.instructions import get_associated_token_address, initialize_account, InitializeAccountParams
from solana.system_program import allocate, AllocateParams, assign, AssignParams, transfer, TransferParams
from borsh_construct import U8, Bool
from anchorpy import Program, Wallet, Provider, Coder
from base58 import b58decode, b58encode
from concurrent.futures.thread import ThreadPoolExecutor
import threading
import time
import tls
from csv import reader

launchpad_tasks = init_launchpad.me_launchpad().master_task_data

def clear():
        subprocess.run('cls', shell=True)

if len(launchpad_tasks) == 0:
    print('No Valid tasks could be created...Please check your meLaunchpad csv file and amend errors...')
    print('Exiting...')
    time.sleep(4)
    exit()

clear()

class build_tx():

    def __init__(self,task_data):
        pass

        self.anchor_tasks = {}
        
        for task in task_data:
            pass
            cmid = task_data[task]['me_info']['mint']['candyMachineId']

            if cmid in self.anchor_tasks:
                current_tasks = self.anchor_tasks[cmid]
                current_tasks.append(task)
                self.anchor_tasks[cmid] = current_tasks
            else:
                self.anchor_tasks[cmid] = [task]
        

        for cmid in self.anchor_tasks:
            pass
            
            async def initialize(CMID):
                client = AsyncClient('https://solana-mainnet.phantom.tech', timeout= 10)
                provider = Provider(client, Wallet(Keypair.generate()))
                candyMachineAddress = str(CMID)

                program_id = PublicKey("CMZYPASGWeTz7RNGHaRJfCq2XQ5pYK6nDvVQxzkH51zb")

                idl = await Program.fetch_idl(
                    program_id,
                    provider
                )

                program = Program(
                    idl,
                    program_id, 
                    provider
                )

                anchorProgram = program

                candyMachine = await anchorProgram.account['CandyMachine'].fetch(candyMachineAddress)

                await program.close()
                return candyMachine
            
            anchor_data = False
            retry = 0
            while anchor_data == False and retry < 4:
                try:
                    candy_data = asyncio.run(initialize(CMID = cmid))
                    anchor_data = True
                except:
                    retry += 1
            

            for task_number in self.anchor_tasks[cmid]:
                task_data[task_number]['anchor_data'] = candy_data
            
        self.master_task_data = task_data

        self.build_transaction()

    def build_transaction(self):
        pass

        CURRENT_BLOCKHASH = ''
        TRANSACTION_CLIENT = Client('https://solana-mainnet.phantom.tech', commitment= 'finalized', blockhash_cache= True)
        SOLANA_CLIENT = Client('https://solana-mainnet.phantom.tech', commitment= 'finalized', blockhash_cache= True)
        SOLANA_CLIENT_URL = 'https://solana-mainnet.phantom.tech'
        TOKEN_PROGRAM_ID = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
        MAGIC_EDEN_CANDY_MACHINE = 'CMZYPASGWeTz7RNGHaRJfCq2XQ5pYK6nDvVQxzkH51zb'
        MEMO_PROGRAM_ID = 'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'
        ME_NOTARY = '71R43w8efa2H6T3pQR7Hif8nj5A3ow2bnx6dAzYJBffP'
        TOKEN_METADATA_ID = 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s'
        SYSTEM_PROGRAM_ID = '11111111111111111111111111111111'
        SYSTEM_RENT_PROGRAM = 'SysvarRent111111111111111111111111111111111'
        SYSTEM_SLOTHASHES = 'SysvarS1otHashes111111111111111111111111111'
        SYSTEM_CLOCK_PROGRAM = 'SysvarC1ock11111111111111111111111111111111'
        WRAPPED_SOL_ID = 'So11111111111111111111111111111111111111112'
        OPTS = types.TxOpts(skip_preflight = False)
        MINT_LEN = 82

        self.transaction_tasks = {}
        child_task_count = 1

        for master_task in self.master_task_data:
            
            input = 1
            task_count = self.master_task_data[master_task]['task_quantity']

            for task in range(1,task_count + 1):
                
                payer = self.master_task_data[master_task]['payer_wallet']
                price = self.master_task_data[master_task]['desired_stage']['price']
                mint_account = Keypair.generate()
                allocate_account = Keypair.generate()
                token_ata = get_associated_token_address(payer.public_key, mint_account.public_key)
                data = self.master_task_data[master_task]['anchor_data']
                transaction = Transaction(fee_payer= payer.public_key)
                me_cmid = self.master_task_data[master_task]['me_info']['mint']['candyMachineId']

                transaction.add(
                    TransactionInstruction(
                        keys= [],
                        program_id= PublicKey('ComputeBudget111111111111111111111111111111'),
                        data = b58decode('16jwcDm')
                    )
                )

                transaction.add(
                    transfer(
                        TransferParams(
                            from_pubkey= payer.public_key,
                            to_pubkey= allocate_account.public_key,
                            lamports= price
                        )
                    )
                )

                transaction.add(
                    allocate(
                        AllocateParams(
                            account_pubkey= allocate_account.public_key,
                            space = 165
                        )
                    )
                )

                transaction.add(
                    assign(
                        AssignParams(
                            account_pubkey= allocate_account.public_key,
                            program_id= PublicKey(TOKEN_PROGRAM_ID)
                        )
                    )
                )

                transaction.add(
                    initialize_account(
                        InitializeAccountParams(
                            program_id= PublicKey(TOKEN_PROGRAM_ID),
                            account= allocate_account.public_key,
                            mint = PublicKey(WRAPPED_SOL_ID),
                            owner= payer.public_key
                        )
                    )
                )

                METADATA_PROGRAM_ADDRESS = PublicKey.find_program_address(
                    seeds=[
                        'metadata'.encode('utf-8'),
                        # Metadata Program ID
                        bytes(PublicKey(TOKEN_METADATA_ID)),
                        # New/Mint Account Public ID
                        bytes(mint_account.public_key)
                    ],
                    # Metadata Program ID
                    program_id= PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
                )

                EDITION_PROGRAM_ADDRESS = PublicKey.find_program_address(
                    seeds=[
                        'metadata'.encode('utf-8'),
                        # Metadata Program ID
                        bytes(PublicKey(TOKEN_METADATA_ID)),
                        # New/Mint Account Public ID
                        bytes(mint_account.public_key),
                        'edition'.encode('utf-8')
                    ],
                    # Program ID = Metadata Program ID
                    program_id= PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
                )

                WALLET_LIMIT_ADDRESS = PublicKey.find_program_address(
                    seeds=[
                        'wallet_limit'.encode('utf-8'),
                        # This is the Candy Machine ID Public Key (Unique to each Mint)
                        bytes(PublicKey(me_cmid)),
                        # your public key
                        bytes(payer.public_key)
                    ],
                    # Program ID is ME Public Address
                    program_id= PublicKey(MAGIC_EDEN_CANDY_MACHINE)
                )

                LAUNCH_STAGES_ADDRESS = PublicKey.find_program_address(
                    seeds=[
                        'candy_machine'.encode('utf-8'),
                        # This is the Candy Machine ID Public Key (Unique to each Mint)
                        'launch_stages'.encode('utf-8'),
                        bytes(PublicKey(me_cmid)),
                    ],
                    # Program ID is ME Public Address
                    program_id= PublicKey(MAGIC_EDEN_CANDY_MACHINE)
                )

                program_id = PublicKey(MAGIC_EDEN_CANDY_MACHINE)

                config_account = data.config
                wallet_auth_account = data.wallet_authority
                order_info_account = data.order_info

                pay_to_account = get_associated_token_address(mint= PublicKey(WRAPPED_SOL_ID), owner= wallet_auth_account)

                user_limit = self.master_task_data[master_task]['desired_stage']['walletLimit']

                tx_base = b'\xd39\x06\xa7\x0f\xdb#\xfb'
                tx_variable_1 = U8.build(WALLET_LIMIT_ADDRESS[1])
                tx_variable_2 = Bool.build(False)
                tx_variable_3 = U8.build(1)

                if user_limit == {'variableLimit' : {}}:
                    me_data = tx_base + tx_variable_1 + tx_variable_2 + tx_variable_2
                elif user_limit == {'noLimit' : {}}:
                    user_limit_seperate = 1
                    tx_variable_4 = U8.build(user_limit_seperate)
                    me_data = tx_base + tx_variable_1 + tx_variable_2 + tx_variable_3 + tx_variable_4
                else:
                    user_limit_seperate = user_limit['fixedLimit']['limit']
                    tx_variable_4 = U8.build(user_limit_seperate)
                    me_data = tx_base + tx_variable_1 + tx_variable_2 + tx_variable_3 + tx_variable_4


                keys = [
                    AccountMeta(pubkey= config_account, is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey(me_cmid), is_signer= False, is_writable= True),
                    AccountMeta(pubkey= payer.public_key, is_signer= True, is_writable= True),
                    AccountMeta(pubkey= payer.public_key, is_signer= True, is_writable= True),
                    AccountMeta(pubkey= LAUNCH_STAGES_ADDRESS[0], is_signer= False, is_writable= True),
                    AccountMeta(pubkey= allocate_account.public_key, is_signer= True, is_writable= False),
                    AccountMeta(pubkey= pay_to_account, is_signer= False, is_writable= True),
                    AccountMeta(pubkey= PublicKey('71R43w8efa2H6T3pQR7Hif8nj5A3ow2bnx6dAzYJBffP'), is_signer= True, is_writable= False),
                    AccountMeta(pubkey= METADATA_PROGRAM_ADDRESS[0], is_signer= False, is_writable= True),
                    AccountMeta(pubkey= mint_account.public_key, is_signer= True, is_writable= False),
                    AccountMeta(pubkey= token_ata, is_signer= False, is_writable= True),
                    AccountMeta(pubkey= EDITION_PROGRAM_ADDRESS[0], is_signer= False, is_writable= True),
                    AccountMeta(pubkey= WALLET_LIMIT_ADDRESS[0], is_signer= False, is_writable= True),
                    AccountMeta(pubkey= order_info_account, is_signer= False, is_writable= True),
                    AccountMeta(pubkey= PublicKey(SYSTEM_SLOTHASHES), is_signer = False, is_writable = False),
                    AccountMeta(pubkey= PublicKey(TOKEN_METADATA_ID), is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey(TOKEN_PROGRAM_ID), is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey(SYSTEM_PROGRAM_ID), is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'), is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey(SYSTEM_RENT_PROGRAM), is_signer= False, is_writable= False),
                    AccountMeta(pubkey= PublicKey('71R43w8efa2H6T3pQR7Hif8nj5A3ow2bnx6dAzYJBffP'), is_signer= True, is_writable= False),
                ]

                transaction.add(
                    TransactionInstruction(
                        keys= keys,
                        program_id= program_id,
                        data=me_data
                    )
                )
                
                self.transaction_tasks[child_task_count] = {
                    'task_id' : str(master_task) + ':' + str(input),
                    'rpc' : Client(self.master_task_data[master_task]['rpc'], commitment= 'finalized', blockhash_cache= True, timeout= 3),
                    'transaction' : transaction,
                    'signers' : [
                        payer,
                        allocate_account,
                        mint_account,
                        PublicKey(ME_NOTARY)
                    ],
                    'session' : tls.create_client(),
                    # 'blockhash' : CURRENT_BLOCKHASH
                }

                input += 1
                child_task_count += 1


get_blockhash = False
while get_blockhash == False:
    try:
        response = Client('https://solana-mainnet.phantom.tech', commitment= 'finalized').get_recent_blockhash(commitment.Commitment('finalized'))
        CURRENT_BLOCKHASH = Blockhash(response['result']['value']['blockhash'])
        get_blockhash = True
    except:
        pass

transactions = build_tx(task_data= launchpad_tasks)

task_num = 0


class send_tx():

    def __init__(self, task_data):

        time.sleep(5)

        lock = threading.Lock()
        client = task_data['rpc']
        session = task_data['session']
        signers = task_data['signers']
        txn = task_data['transaction']
        global CURRENT_BLOCKHASH
        txn.recent_blockhash = CURRENT_BLOCKHASH

        
        txn.sign_partial(PublicKey(signers[3]))
        txn.sign(*signers)

        message = txn.serialize_message()
        message_encoded = b58encode(message)
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'ar_session_token': 'stub-until-arkose-is-fixed',
            'origin': 'https://magiceden.io',
            'referer': 'https://magiceden.io/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        }

        json_data = {
            'response': '',
            'message': message_encoded.decode('utf-8'),
        }

        response = session.post('https://wk-notary-prod.magiceden.io/sign', headers=headers, json=json_data)

        try:

            # response = scraper.post('https://wk-notary-prod.magiceden.io/sign', headers=headers, json=json_data, cookies = cookies)
            response = session.post('https://wk-notary-prod.magiceden.io/sign', headers=headers, json=json_data)
            tls_error = False
        except:
            tls_error = True
        
        if tls_error == True:
            dang = 'dang'
        
        elif response.status_code == 401:
            lock.acquire()
            print(response.text)
            time.sleep(0.01)
            lock.release()

        elif response.status_code == 403:
            lock.acquire()
            print('Cloudflare enabled - Unable to get signature')
            time.sleep(0.01)
            lock.release()
        
        elif response.status_code == 500:
            lock.acquire()
            print(response.text)
            time.sleep(0.01)
            lock.release()

        else:
            response_json = response.json()


            signature = response_json['signature']
            signature_hash = b58decode(signature)

            txn.add_signature(PublicKey(signers[3]),signature=signature_hash)

            prep_txn = txn.serialize()
            
            OPTS = types.TxOpts(skip_preflight = False,preflight_commitment= 'finalized')
            
            while True:
                try:
                    txn_response = client.send_raw_transaction(prep_txn,OPTS)
                    
                    lock.acquire()
                    print('Task ' + str(task_data['task_id']) + ' - Transaction hash : ' + str(txn_response['result']))
                    lock.release()
                except Exception as e:
                    lock.acquire()
                    global task_num
                    task_num = task_num + 1
                    print(task_num)
                    # print('Task ' + str(task_data['task_id']) + ' - Error : ' + str(e.args[0]['data']['logs'][-3]))
                    time.sleep(0.2)
                    lock.release()

# send_tx(task_data= transactions.transaction_tasks[1])

executors_list = []


while True:
    with ThreadPoolExecutor(max_workers= len(transactions.transaction_tasks)) as executor:
        for task in transactions.transaction_tasks:
            executors_list.append(executor.submit(send_tx,transactions.transaction_tasks[task]))