from langchain.tools import tool
import subprocess
from typing import Dict, List
from cli.checkOS import checkOS
from cli.take_admin_access import req_Admin_Access


# ☠️ these tools required admin access


# testing process for linux...


#working with windows
@tool
def createNewUser(names:List = 'user', password :str = "") -> Dict :
    '''
        create an new user account with or without password
    '''
    try:

        os = checkOS()
        if os == 'windows':

            cmd = ['net', 'user']+names +[ password, '/add']
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'useradd','-m']+ names +['-p', password ]
        response = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'success':True,
            'result': str(response),
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

#working with windows ----
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
            'success':True,
            'result': str(response),
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }


#working with windows
@tool
def createGroup(group:str) -> Dict :
    '''
    Create a new local user group on the system.
    Args:
        group (str): The name of the group to create. Any alphanumeric name is valid, e.g. "newUserGroup", "admins", "developers".
    Returns a dict with success status and command output.
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'localgroup', group, '/add']
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'groupadd', group]

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'success': True,
            'result': response.stdout or response.stderr,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }

#working with windows
@tool
def deleteGroup(group:str) -> Dict :
    '''
    Delete an existing local user group from the system.
    Args:
        group (str): The name of the group to delete, e.g. "newUserGroup", "admins".
    Returns a dict with success status and command output.
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'localgroup', group, '/delete']
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'groupdel', group]

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'success': True,
            'result': response.stdout or response.stderr,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }


#working with windows
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
            'success':True,
            'result': str(response),
            'ui_type':'Normal_window'
        }
    except Exception as e:
        return {
            'success':False,
            'error':str(e),
            'ui_type':'Normal_window'
        }

#working with windows
@tool
def disableAccount(users:List) -> Dict:
    '''disable user accounts — disables each user in the list'''
    try:
        os = checkOS()
        results = []
        for user in users:
            if os == 'windows':
                cmd = ['net', 'user', user, '/active:no']
            elif os == 'linux' or os == 'darwin':
                cmd = ['sudo', 'usermod', '-L', user]

            response = subprocess.run(cmd, capture_output=True, text=True)
            results.append({'user': user, 'stdout': response.stdout, 'stderr': response.stderr})

        return {
            'success': True,
            'result': results,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }

#working with windows
@tool
def enableAccount(users:List) -> Dict:
    '''enable user accounts — enables each user in the list'''

    try:
        os = checkOS()
        results = []
        for user in users:
            if os == 'windows':
                cmd = ['net', 'user', user, '/active:yes']
            elif os == 'linux' or os == 'darwin':
                cmd = ['sudo', 'usermod', '-U', user]

            response = subprocess.run(cmd, capture_output=True, text=True)
            results.append({'user': user, 'stdout': response.stdout, 'stderr': response.stderr})

        return {
            'success': True,
            'result': results,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }


#working with windows
@tool
def deleteUser(user:str) -> Dict :
    '''
        delete a user account
    '''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'user', user, '/delete']
        elif os == 'linux' or os == 'darwin' :
            cmd = ['sudo', 'userdel', '-r', user]

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'success': True,
            'result': response.stdout or response.stderr,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }

#working with windows
@tool
def listUsers() -> Dict:
    '''list all users on the system'''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'user']
        elif os == 'linux' or os == 'darwin':
            cmd = ['cut', '-d:', '-f1', '/etc/passwd']

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'success': True,
            'result': response.stdout or response.stderr,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }

#working with windows
@tool
def listGroups() -> Dict:
    '''list all groups on the system'''
    try:
        os = checkOS()
        if os == 'windows':
            cmd = ['net', 'localgroup']
        elif os == 'linux' or os == 'darwin':
            cmd = ['cut', '-d:', '-f1', '/etc/group']

        response = subprocess.run(cmd, capture_output=True, text=True)

        return {
            'success': True,
            'result': response.stdout or response.stderr,
            'ui_type': 'Normal_window'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }



@tool
def listUsersByGroup() -> Dict:
    '''view users grouped by local group membership'''
    try:
        os = checkOS()

        if os == 'windows':
            groups_result = subprocess.run(['net', 'localgroup'], capture_output=True, text=True)
            if groups_result.returncode != 0:
                return {
                    'success': False,
                    'error': groups_result.stderr or groups_result.stdout,
                    'ui_type': 'Normal_window'
                }

            groups: List[str] = []
            for line in (groups_result.stdout or '').splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                low = stripped.lower()
                if low.startswith('aliases for') or low.startswith('the command completed') or stripped.startswith('---'):
                    continue
                if stripped.startswith('*'):
                    groups.append(stripped.lstrip('*').strip())

            grouped_users: Dict[str, List[str]] = {}
            errors: Dict[str, str] = {}

            for group in groups:
                members_result = subprocess.run(['net', 'localgroup', group], capture_output=True, text=True)
                if members_result.returncode != 0:
                    errors[group] = members_result.stderr or members_result.stdout
                    continue

                members: List[str] = []
                capture_members = False
                for line in (members_result.stdout or '').splitlines():
                    stripped = line.strip()
                    low = stripped.lower()

                    if not stripped:
                        continue
                    if low.startswith('the command completed'):
                        break
                    if low == 'members':
                        capture_members = True
                        continue
                    if capture_members and stripped.startswith('---'):
                        continue
                    if capture_members and 'no members' in low:
                        members = []
                        break
                    if capture_members:
                        members.append(stripped)

                grouped_users[group] = members

            return {
                'success': True,
                'result': {
                    'groups': grouped_users,
                    'errors': errors
                },
                'ui_type': 'Normal_window'
            }

        elif os == 'linux' or os == 'darwin':
            result = subprocess.run(['getent', 'group'], capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr or result.stdout,
                    'ui_type': 'Normal_window'
                }

            grouped_users: Dict[str, List[str]] = {}
            for line in (result.stdout or '').splitlines():
                parts = line.split(':')
                if len(parts) < 4:
                    continue
                group_name = parts[0].strip()
                members = [u.strip() for u in parts[3].split(',') if u.strip()]
                grouped_users[group_name] = members

            return {
                'success': True,
                'result': {
                    'groups': grouped_users,
                    'errors': {}
                },
                'ui_type': 'Normal_window'
            }

        return {
            'success': False,
            'error': 'Unsupported operating system',
            'ui_type': 'Normal_window'
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'ui_type': 'Normal_window'
        }