import asyncio
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
import cloudscraper




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

def me_launchpad():

    lock = threading.Lock()

    print('Reading task data...')
    time.sleep(0.75)

    csv_data = []

    try:
        with open('./Tasks/meLaunchpad.csv','r') as task_list:
            csv_reader = reader(task_list)
            header = next(csv_reader)
            if header != None:
                for row in csv_reader:
                    csv_data.append(row)
    except:
        print('Error fetching ME Launchpad tasks...')
        print('Exiting...')
        time.sleep(4)
        exit()

    if len(csv_data) == 0:
        print('Error with ME Launchpad task data. Please check meLaunchpad csv and launch again...')
        print('Exiting...')
        time.sleep(4)
        exit()

    async def initialize(solana_client,wallet_limit_bump, CMID, user_limit):
        client = AsyncClient(solana_client)
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

        get_instructions = Coder(idl)

        test1 = get_instructions.instruction.sighashes['mint_nft']

        test2 = U8.build(wallet_limit_bump)
        test3 = Bool.build(False)
        test6 = U8.build(1)
        if user_limit == {'noLimit' : {}}:
            test4 = test1 + test2 + test3 + test3
        else:
            user_limit_seperate = user_limit['fixedLimit']['limit']
            test5 = U8.build(user_limit_seperate)
            test4 = test1 + test2 + test3 + test6 + test5

        anchorProgram = program

        candyMachine = await anchorProgram.account['CandyMachine'].fetch(candyMachineAddress)

        await program.close()
        return candyMachine, test4

    
    for task in range(0, len(csv_data)):
        collection = csv_data[task][1]

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'if-none-match': 'W/"15b5-B6gYzc0lrpdmjTbmPo8XU5upYaY"',
            'origin': 'https://magiceden.io',
            'referer': 'https://magiceden.io/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        }

        session = tls.create_client()
        get_tls = False
        while get_tls == False:
            try:
                response = session.get('https://api-mainnet.magiceden.io/launchpads/' + str(collection),headers= headers, timeout= 5)
                response_json = response.json()

                csv_data[task].append(response_json['mint']['candyMachineId'])
                stages_length = len(response_json['state']['stages'])
                public_limit = response_json['state']['stages'][-1]['walletLimit']
                price = int(response_json['price'] * 1000000000)
                csv_data[task].append(public_limit)
                csv_data[task].append(price)

                get_tls = True
            except:
                print('TLS Error')


    task_data = {}

    task_data[0] = {
        'task_number' : 0,
        'task_status' : 'blockhash',
        'cmid' : '',
        'payer' : '',
        'mint_account' : '',
        'transaction' : ''
    }

    input_number = 1

    for input in csv_data:

        payer = Keypair.from_secret_key(b58decode(input[0]))

        WALLET_LIMIT_ADDRESS = PublicKey.find_program_address(
            seeds=[
                'wallet_limit'.encode('utf-8'),
                # This is the Candy Machine ID Public Key (Unique to each Mint)
                bytes(PublicKey(input[3])),
                # your public key
                bytes(payer.public_key)
            ],
            # Program ID is ME Public Address
            program_id= PublicKey(MAGIC_EDEN_CANDY_MACHINE)
        )

        candy_machine_data = asyncio.run(initialize(solana_client= SOLANA_CLIENT_URL, wallet_limit_bump= WALLET_LIMIT_ADDRESS[1], CMID= input[3], user_limit= input[4]))


        threads = int(input[2])
        for task_number in range(0,threads):
            task_actual_number = task_number + input_number
            UNIQUE_CANDY_MACHINE_ID = input[3]
            price = input[5]
            payer = Keypair.from_secret_key(b58decode(input[0]))
            mint_account = Keypair.generate()
            allocate_account = Keypair.generate()
            associated_token_account = get_associated_token_address(payer.public_key,mint_account.public_key)
            balance_needed = 1461600
            data = candy_machine_data[1]
            transaction = Transaction(fee_payer=payer.public_key)

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
                    bytes(PublicKey(UNIQUE_CANDY_MACHINE_ID)),
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
                    bytes(PublicKey(UNIQUE_CANDY_MACHINE_ID)),
                ],
                # Program ID is ME Public Address
                program_id= PublicKey(MAGIC_EDEN_CANDY_MACHINE)
            )

            program_id = PublicKey(MAGIC_EDEN_CANDY_MACHINE)

            config_account = candy_machine_data[0].config
            wallet_auth_account = candy_machine_data[0].wallet_authority
            order_info_account = candy_machine_data[0].order_info

            token_ata = get_associated_token_address(mint= mint_account.public_key, owner= payer.public_key)

            pay_to_account = get_associated_token_address(mint= PublicKey(WRAPPED_SOL_ID), owner= wallet_auth_account)


            keys = [
                AccountMeta(pubkey= config_account, is_signer= False, is_writable= False),
                AccountMeta(pubkey= PublicKey(input[3]), is_signer= False, is_writable= True),
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
                AccountMeta(pubkey=PublicKey(SYSTEM_SLOTHASHES), is_signer = False, is_writable = False),
                AccountMeta(pubkey=PublicKey(TOKEN_METADATA_ID), is_signer= False, is_writable= False),
                AccountMeta(pubkey=PublicKey(TOKEN_PROGRAM_ID), is_signer= False, is_writable= False),
                AccountMeta(pubkey=PublicKey(SYSTEM_PROGRAM_ID), is_signer= False, is_writable= False),
                AccountMeta(pubkey=PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'), is_signer= False, is_writable= False),
                AccountMeta(pubkey=PublicKey(SYSTEM_RENT_PROGRAM), is_signer= False, is_writable= False),
                AccountMeta(pubkey= PublicKey('71R43w8efa2H6T3pQR7Hif8nj5A3ow2bnx6dAzYJBffP'), is_signer= True, is_writable= False),
            ]

            transaction.add(
                TransactionInstruction(
                    keys= keys,
                    program_id= program_id,
                    data=data
                )
            )

            task_data[task_actual_number] = {
                'task_number' : task_actual_number,
                'task_session' : tls.create_client(),
                'task_status' : 'mint',
                'cmid' : input[1],
                'payer' : payer,
                'mint_account' : mint_account,
                'transaction' : transaction,
                'signers' : [
                    payer,
                    allocate_account,
                    mint_account,
                    PublicKey(ME_NOTARY)
                ],
                
            }

        input_number = input_number + threads
    
    response = SOLANA_CLIENT.get_recent_blockhash(commitment.Commitment('finalized'))
    CURRENT_BLOCKHASH =  Blockhash(response['result']['value']['blockhash'])

    
 

    def loop(task_data,blockhash):

        CURRENT_BLOCKHASH = blockhash

        lock.acquire()
        print('Starting Task : ' + str(task_data['task_number']))
        time.sleep(0.01)
        lock.release()

        while True:

            if task_data['task_status'] == 'blockhash':
                response = SOLANA_CLIENT.get_recent_blockhash(commitment.Commitment('finalized'))
                CURRENT_BLOCKHASH = Blockhash(response['result']['value']['blockhash'])
            
            if task_data['task_status'] == 'mint':
                session = task_data['task_session']
                signers = task_data['signers']
                txn = task_data['transaction']
                txn.recent_blockhash = CURRENT_BLOCKHASH
                txn.sign_partial(PublicKey(signers[3]))
                txn.sign(*signers)
                message = txn.serialize_message()
                import base64
                message_test = base64.b64encode(message)
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

                # cookies = {
                #     '__cf_bm' : 'r2JlTJt40FUU.zaLfBVEJfD0nq2WTSd0LmC6RLABAmw-1652739831-0-AUwoDqWsth418v1JvxPh6485Yzz6IPwShpFpheHiDvdzeSW87OZcq1uO6oMltDifs2MR7oC3sza7rwmSWuWgPZfnRYmTMK8llRz0vRwZSpprMmd4J0tn0sVP/kdJf/yUSY4oBpHjf5pnXfAGJoO7U6Lflgfrr1AwDw11+krvv3HK'
                # }

                try:
                    # scraper = cloudscraper.create_scraper(
                    #     interpreter='nodejs',
                    #     captcha={
                    #         'provider' : '2captcha',
                    #         'api_key' : '3ef2228fae269ab3692175a370d4aaf0'
                    #     }
                    # )

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
                    
                    try:
                        txn_response = TRANSACTION_CLIENT.send_raw_transaction(prep_txn,OPTS)
                        
                        lock.acquire()
                        print('Task ' + str(task_data['task_number']) + ' - Transaction hash : ' + str(txn_response['result']))
                        lock.release()
                    except Exception as e:
                        lock.acquire()
                        print('Task ' + str(task_data['task_number']) + ' - Error : ' + str(e.args[0]['data']['logs'][-3]))
                        lock.release()
    
    executors_list = []


    while True:
        with ThreadPoolExecutor(max_workers=len(task_data)) as executor:
            for task in task_data:
                executors_list.append(executor.submit(loop,task_data[task],CURRENT_BLOCKHASH))