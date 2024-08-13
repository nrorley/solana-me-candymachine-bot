from art import tprint
import time
import json
import tls
from os import system, name
import socket
import requests
import launchpad
import subprocess

print('Contacting Api...')
time.sleep(1.5)

version = '0.0.3'
release = 'Beta'

auth_cleared = False
hostname = socket.gethostname()
# get auth key
try:
    f = open('settings.json')
    settings = json.load(f)
    f.close()
except:
    print('Unable to load auth_key from settings.json')
    print('Exiting...')
    time.sleep(2)
    exit()

if settings:

    url_version = 'https://www.mintmatenft.com/api/v1/auth/user/search/id/version_check'
    url = 'https://www.mintmatenft.com/api/v1/auth/user/search/key/' + settings['auth_key']

    headers = {
    'accept': 'application/json',
    }

    json_data = {
        'auth_token' : 'XmDYTTJZGXW_T_myVES0Tg4rnEVjX9vUBsLUMj1NNOgwSEoF6NUqj11u9Rzkw6X6pDJv_YurO-5D0cQQQu5zPA'
    }

    version_response = requests.post(url=url_version, headers=headers, json=json_data)

    if version_response.status_code == 200:
        version_response_json = version_response.json()

        if version == version_response_json['key']:
            print('Version is valid...\nChecking Key...')
        else:
            print('Version is invalid...\nPlease download the latest version from discord')
            print('Exiting...')
            time.sleep(5)
            exit()
    
    else:
        print('Version is invalid...\nPlease download the latest version from discord')
        print('Exiting...')
        time.sleep(5)
        exit()

    response = requests.post(url=url, headers=headers, json=json_data)

    if response.status_code == 200:
        print('Key is valid...\nChecking Session...')
        response_json = response.json()
        if response_json['session'] == 'None':
            url = 'https://www.mintmatenft.com/api/v1/auth/users/' + str(response_json['id'])
            json_data['session'] = str(hostname)
            update_response = requests.patch(url=url, headers= headers, json=json_data)

            if update_response.status_code == 200:
                print('Session is valid...')
                auth_cleared = True
            
            else:
                print('Error Updating Session')
                print('Exiting...')
                time.sleep(2)
        
        elif response_json['session'] == hostname:
            print('Session Okay - Welcome to Mint Mate')
            auth_cleared = True
        
        else:
            print('Session Invalid. Please reset your session with the \'!reset\' command in discord')
            print('Exiting...')
            time.sleep(2)

    elif response.status_code == 404:
        print('Key does not exist in database. Please authorize yourself on discord to gain a valid key')
        print('Exiting...')
        time.sleep(2)
    else:
        print('An unexpected error occured')
        print('Exiting...')
        time.sleep(2)
    

if auth_cleared == True:

    def clear():
        subprocess.run('cls', shell=True)

    time.sleep(1.5)
    clear()
    tprint('\nMint Mate', font= 'sub-zero')
    print(str(release) + ' - ' + str(version))

    module_status = {
        'CMV2' : False,
        'Launchpad' : True,
        'ME Sniper' : False,
    }



    def main_menu():
        print()
        print('Main Menu:\n')
        print('1) Tasks')
        print('2) Exit')
        main_menu_options()

    def main_menu_revert():
        tprint('\nMint Mate', font= 'sub-zero')
        print()
        print('Main Menu:\n')
        print('1) Tasks')
        print('2) Exit')
        main_menu_options()

    def main_menu_options():
        option = input('\nEnter your option: ')

        while option != 'command:exitmenu':
            if option == '1':
                # Do option 1 stuff
                print('\nOpening Task Menu')
                time.sleep(0.5)
                task_menu()
                option = 'command:exitmenu'
            elif option == '2':
                # Do option 2 stuff
                print('Exiting...')
                time.sleep(1.5)
                exit()
            elif option == '':
                option = input('Enter valid option: ')      
            else:
                option = input('Enter valid option: ')


    def task_menu():
        clear()

        tprint('\nMint Mate', font= 'sub-zero')


        print('\nTask Menu:\n')
        if module_status['CMV2'] == False:
            print('1) CMV2 - Locked')
        else:
            print('1) CMV2')
        if module_status['Launchpad'] == False:
            print('2) Launchpad - Locked')
        else:
            print('2) Launchpad')
        if module_status['ME Sniper'] == False:
            print('3) ME Sniper - Locked')
        else:
            print('3) ME Sniper')

        print('\n4) Main Menu')
        print('5) Exit')
        task_menu_options()
        

    def task_menu_options():
        option = input('\nEnter your option: ')

        while option != 'command:exitmenu':
            if option == '1':
                if module_status['CMV2'] == False:
                    task_menu_options()
                else:
                    #put call here for run task
                    task_menu_options()

            if option == '2':
                if module_status['Launchpad'] == False:
                    task_menu_options()
                else:
                    clear()
                    launchpad.me_launchpad()

            if option == '3':
                if module_status['ME Sniper'] == False:
                    task_menu_options()
                else:
                    #put call here for run task
                    task_menu_options()

            if option == '4':
                clear()
                main_menu_revert()
            
            if option == '5':
                print('Exiting...')
                time.sleep(1.5)
                exit()
            
            if option != 1 or 2 or 3 or 4 or 5:
                task_menu_options()

    main_menu()
