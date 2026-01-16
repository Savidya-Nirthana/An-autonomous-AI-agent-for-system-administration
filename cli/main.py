import cli_functions as cli

cli.check_packages()
cli.login_form()
cli.welcome_banner()
cli.welcome_msg()

if __name__ == "__main__" :
    while True:
        if not cli.get_requests():
            break
            
        
    