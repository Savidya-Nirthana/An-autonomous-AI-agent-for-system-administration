from langchain.tools import tool
import subprocess
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
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'useradd','-m'].extend(names).extend(['-p', password ])

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
        elif os == 'linux' or os == 'darwin' :
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

#neet to check this with correct commands
@tool
def createGroup(group:str) -> Dict :
    '''
        create user groups
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = [] #no direct command , commands need to be added
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'groupadd ', group]

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
        elif os == 'linux' or os == 'darwin' :
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
        elif os == 'linux' or os == 'darwin':
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
        elif os == 'linux' or os == 'darwin':
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

@tool
def deleteUser(user:str) -> Dict :
    '''
        create user groups
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['Remove-LocalUser', '-Name', user] #powershell
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'userdel', '-r', group]

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

#[createNewUser,changeUserPassword,addUsersToGroup,disableAccount,enableAccount ,deleteUser,createGroup]