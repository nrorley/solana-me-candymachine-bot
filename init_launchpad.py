from solana.rpc.api import Client
from solana.keypair import Keypair  
from csv import reader
from base58 import b58decode
import json
import time
import tls


class me_launchpad():

    def __init__(self):
        
        self.csv_data = []
        
        try:
            with open('Tasks/meLaunchpad.csv','r') as task_list:
                csv_reader = reader(task_list)
                header = next(csv_reader)
                if header != None:
                    for row in csv_reader:
                        self.csv_data.append(row)
        
        except Exception as e:
            print('Error fetching ME Launchpad tasks...{e}')
            print('Exiting...')
            time.sleep(4)
            exit()
        
        if len(self.csv_data) == 0:
            print('Error with ME Launchpad task data. Pleaase check meLaunchpad csv and launch again...')
            print('Exiting...')
            time.sleep(4)
            exit()
        
        else:
            self.test_rpc()
    
    def test_rpc(self):
        
        print('Parsing CSV Task Data...')

        self.master_task_data = {}
        input = 1

        for line in self.csv_data:

            if line[4]:
                print('Testing RPC on line ' + str(input) + ' : {}'.format(line[4]))
            
                test_client = Client(line[4], timeout= 5).is_connected()

                if test_client == True:
                    print('Initial connection pass : Commencing test 2')

                    try:
                        test_blockhash = Client(line[4], timeout= 5).get_recent_blockhash()
                        print('Test 2 pass : Building Tasks')
                    except:
                        print('Failed second test : Defaulting to http://solana-mainnet.phantom.tech')
                        line[4] = 'https://solana-mainnet.phantom.tech'
                else:
                    print('No RPC Input found on line ' + str(input) + ' : Defaulting to https://solana-mainnet.phantom.tech')
                    print('RPC changed : Building tasks')
                    line[4] = 'https://solana-mainnet.phantom.tech'
            
            else:
                print('No RPC Input found on line ' + str(input) + ' : Defaulting to https://solana-mainnet.phantom.tech')
                print('RPC changed : Building tasks')
                line[4] = 'https://solana-mainnet.phantom.tech'

            self.master_task_data[input] = {
                'rpc' : line[4]
            }

            input += 1
        
        self.task_quantity()
    
    def task_quantity(self):
        
        input = 1

        for line in self.csv_data:

            try:
                self.master_task_data[input]['task_quantity'] = int(line[1])
                print('Thread limit on line ' + str(input) + ' set to : ' + str(line[1]))
            except: 
                print('Thread limit on line ' + str(input) + ' is not valid - Defaulting too 100')
                self.master_task_data[input]['task_quantity'] = 100
            input += 1
        
        self.get_wallet()

    
    def get_wallet(self):
        pass
        
        input = 1

        for line in self.csv_data:

            try:
                self.master_task_data[input]['payer_wallet'] = Keypair.from_secret_key(b58decode(line[0]))
                print('Successfully generated wallet from secret key for tasks on line ' + str(input) + ' with the public key of : ' + str(self.master_task_data[input]['payer_wallet'].public_key))
            except:
                print('Unable to generate wallet from given secret key. Will run without tasks on line ' + str(input))
                self.master_task_data[input]['payer_wallet'] = 'invalid'
            
            input += 1
        
        self.get_collection()
    
    def get_collection(self):
        
        input = 1

        for line in self.csv_data:
            print('Checking for collection on line ' + str(input) + ' : ' + str(line[2]) )
            
            try:
                with open('Tasks/me_collection_info/{}.json'.format(line[2]), 'r', encoding = 'utf-8') as f:
                    self.master_task_data[input]['me_info'] = json.load(f)
                    f.close()
                    print('Found \'{}\' collection data locally. Will monitor ME for changes...'.format(line[2]))
            except:
                print('Unable to find \'{}\' collection data locally. Will attempt to fetch from ME...'.format(line[2]))

                session = tls.create_client()

                headers = {
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'origin': 'https://magiceden.io',
                    'referer': 'https://magiceden.io/',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                }

                get_collection = False
                fail_count = 0

                while get_collection == False and fail_count < 5:
                    try:
                        response = session.get('https://api-mainnet.magiceden.io/launchpads/' + str(line[2]), headers= headers, timeout= 5)
                        if response.status_code == 200:
                            response_json = response.json()
                            with open('Tasks/me_collection_info/{}.json'.format(line[2]), 'w', encoding= 'utf-8') as f:
                                json.dump(response_json, f, ensure_ascii=False, indent= 4)
                                self.master_task_data[input]['me_info'] = response_json
                                get_collection = True
                        
                        else:
                            print('Unable to find collection \'{}\' on ME'.format(line[2]))
                            fail_count += 1
                    except:
                        print('TLS Error on ME fetch')
                        fail_count += 1
                
                try:
                    self.master_task_data[input]['me_info']
                except:
                    self.master_task_data[input]['me_info'] = 'invalid'       

            input +=1
        self.launch_stage()  
        
    def launch_stage(self):

        input = 1

        for line in self.csv_data:

            try:
                self.master_task_data[input]['me_info']

                try:
                    desired_stage = int(line[3])
                    stages_length = len(self.master_task_data[input]['me_info']['state']['stages'])

                    if desired_stage > stages_length or desired_stage ==0:
                        print('Invalid launch stage selected on line ' + str(input) + ' : Defaulting to last stage')
                        self.master_task_data[input]['stage_number'] = 'last'
                        self.master_task_data[input]['desired_stage'] = self.master_task_data[input]['me_info']['state']['stages'][-1]
                    else:
                        print('Valid launch stage selected on line ' + str(input) + ' : Setting launch stage ' + str(desired_stage))
                        self.master_task_data[input]['stage_number'] = desired_stage - 1
                        self.master_task_data[input]['desired_stage'] = self.master_task_data[input]['me_info']['state']['stages'][desired_stage - 1]
                except:
                    print('Invalid launch stage selected on line ' + str(input) + ' : Defaulting to last stage')
                    self.master_task_data[input]['stage_number'] = 'last'
                    self.master_task_data[input]['desired_stage'] = self.master_task_data[input]['me_info']['state']['stages'][-1]
                    
            except:
                self.master_task_data[input]['launch_stage'] = 'invalid'
                self.master_task_data[input]['stage_number'] = 'invalid'
        

            input += 1
        
        self.trim_tasks()
    
    def trim_tasks(self):

        for input in range(1, len(self.master_task_data) + 1): 
            for entry in self.master_task_data[input]:
                if self.master_task_data[input][entry] == 'invalid':
                    print('Trimming Tasks on line ' + str(input) + ' : Invalid task data')
                    del self.master_task_data[input]
                    break
        
        return self.master_task_data
        