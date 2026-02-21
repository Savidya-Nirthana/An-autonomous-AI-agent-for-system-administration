from langchain.tools import tool
import subprocess
# from cli.request_admin_access import run_as_admin
from typing import Dict, List
from cli.checkOS import checkOS


@tool
def createNewUser(names:List = 'user', password :str = "") -> Dict :
    '''
        create an new user account with or without password 
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'user'].extend(names).extend([ password, '/add'])
        elif os == 'linux' | os == 'darvin' :
            cmd = ['useradd','-m'].extend(names)

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'sucess':False,
            'result':response,
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

#neet to check this with correct commands
@tool
def changeUserPassword(name:str = 'user', password :str = "") -> Dict :
    '''
        change password for user account 
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'user', name, password]
        elif os == 'linux' | os == 'darvin' :
            cmd = ['passwd'] + ['-m', name]

        response = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            'sucess':False,
            'result':response,
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

#neet to check wheter the given group was exist or not
@tool
def addUsersToGroup(user:str = 'user', group :str = "") -> Dict :
    '''
        change or add users to groups
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'localgroup', group ,user,'/add']
        elif os == 'linux' | os == 'darvin' :
            cmd = ['usermod'] + ['-aG' ,group, user] #sudo might be needed

        response = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            'sucess':False,
            'result':response,
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

@tool
def disableAccount(users:List) -> Dict:
    '''disable user accounts before this need to check that the account is available or not'''
    try:
        os =  checkOS()

        if os == 'windows':
            cmd = ['net', 'user'].extend(users).extend(['/deactivate:yes']) #need to check this command
        elif os == 'linux' | os == 'darvin':
            cmd = ['usermod', '-L' ]  #neet to specify user

        response = subprocess.run(cmd, capture_output=True , text=True)
        return {
            'result' : response
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

@tool
def enableAccount(users:List) -> Dict:
    '''enable user accounts before this need to check that the account is available or not'''
    
    try:
        os =  checkOS()

        if os == 'windows':
            cmd = ['net', 'user'].extend(users).extend(['/active:yes'])
        elif os == 'linux' | os == 'darvin':
            cmd = ['usermod' '-U'] #neet to add use

        response = subprocess.run(cmd, capture_output=True , text=True)
        return {
            'result' : response
        }
    except Exception as e:
        return {
            'sucess':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }


#[createNewUser,changeUserPassword,addUsersToGroup,disableAccount,enableAccount]