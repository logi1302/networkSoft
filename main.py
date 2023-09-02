
╭╮
┃┃
┃┃╱╱╭━━┳━━┳╮
┃┃╱╭┫╭╮┃╭╮┣┫
┃╰━╯┃╰╯┃╰╯┃┃
╰━━━┻━━┻━╮┣╯
╱╱╱╱╱╱╱╭━╯┃
╱╱╱╱╱╱╱╰━━╯

#В 56 рядку необхідно вказати мак ядра для перевірки, чи не є порт аплінковим

import paramiko
import time

class SSHAndTelnetClient:   #Клас для роботи з Edge core
    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password, telnet_host, telnet_username, telnet_password):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.telnet_host = telnet_host
        self.telnet_username = telnet_username
        self.telnet_password = telnet_password

    def connect_ssh(self):  #встановлення з'єднання з сервером
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.ssh_host, port=self.ssh_port, username=self.ssh_username, password=self.ssh_password)
            print(f'SSH connection established to {self.ssh_host}:{self.ssh_port}')
        except Exception as e:
            print(f'Error connecting via SSH: {e}')
            exit(1)

    def connect_telnet(self):  #встановлення з'єднання по telnet з комутатором
        try:
            self.telnet_channel = self.ssh_client.invoke_shell()
            self.telnet_channel.send("telnet " + self.telnet_host + "\n")
            time.sleep(1) 
            self.telnet_channel.send(self.telnet_username + "\n")
            self.telnet_channel.send(self.telnet_password + "\n")
            response = self.telnet_channel.recv(4096).decode('utf-8')
            print(response)
            print(f'Telnet connection established to {self.telnet_host}')
        except Exception as e:
            print(f'Error connecting via Telnet: {e}')
            self.ssh_client.close()
            exit(1)


    def send_telnet_command(self, command):  #виконання команди по telnet
        try:
            self.telnet_channel.send(command + "\n")
            time.sleep(1)  
            response = self.telnet_channel.recv(4096).decode('utf-8')
            print(response)
        except Exception as e:
            print(f'Error sending Telnet command: {e}')
        return response
    
    def check_mac_core(self, switch):   #перевірка чи не є порт аплінковим
        try:
            self.telnet_channel.send("show MAC-ADDress-table" + "\n")
            time.sleep(1)  
            response = self.telnet_channel.recv(4096).decode('utf-8')
            
            if "@@@@@@@@@@@@@@@" in response:
                search_word = "Eth"
                words = response.split()
                index = words.index(search_word)
                if index + 1 < len(words):
                    next_word = words[index + 1]
            return next_word
            
        except Exception as e:
            print(f'Error sending Telnet command: {e}')
        return False

    def close_connections(self):
        self.telnet_channel.close()
        self.ssh_client.close()
        print('Connections closed.')

if __name__ == "__main__":
    ssh_host = "XX.XX.XX.XX"     # хост сервера
    ssh_port = XXX              # порт сервера
    ssh_username = "XXXXX"     # логін користувача серверу
    ssh_password = "XXXXX"    # пароль користувача серверу
    telnet_host = "XXXXXXXXXXXXXXX"        # Хост комутатора
    telnet_username = "XXXXXXXXXXXXXXXX"  # Логін telnet
    telnet_password = "XXXXXXXXXXXXX"    # Пароль telnet

    count_up = 0

    def connect_and_count_up(host, username, password):   #рекурсія
        global count_up                                   #якщо на порт не приходить мак ядра, тобто він не аплінк
        try:                                              #продовжуємо на ньому рахувати абонів
            client = SSHAndTelnetClient(ssh_host, ssh_port, ssh_username, ssh_password, host, telnet_username, telnet_password)

            client.connect_ssh()
            client.connect_telnet()

            lines = client.send_telnet_command("show interface brief")
            lines += client.send_telnet_command(" ")

            count_up += sum(1 for line in lines.split('\n') if "Up" in line and "client" in line)
            print(count_up)

            words = lines.split()

            modified_words = []

            for word in words:
                if word.startswith("sw") and "." in word:
                    parts = word.split(".")
                    sw_word = parts[0] + ".te.clb"
                    modified_words.append(sw_word)

            for sub_switch in modified_words:
                
                if client.check_mac_core("sub_switch") == False:
                    connect_and_count_up(sub_switch, username, password)
            print(f'Telnet connection to {host} closed.')
        except Exception as e:
            print(f'Error connecting via Telnet to {host}: {e}')
    
        return count_up

    print(connect_and_count_up(telnet_host, telnet_username, telnet_password))

    



