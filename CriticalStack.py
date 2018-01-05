from contextlib import closing
import os
os.sys.path.insert(
    0,
    '{}/paramiko'.format(os.path.dirname(os.path.abspath(__file__)))
)
import paramiko
import time


class Intel(object):

    def __init__(
            self,
            client_loc,
            user,
            password,
            apiKey=None,
            file_loc=(
                '/opt/critical-stack/frameworks/intel/master-public.bro.dat'
            )
    ):

        self.client_loc = client_loc
        self.user = user
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.file_loc = file_loc
        self.apiKey = apiKey

    def _is_connected(self):
        connected = False
        if(
            self.ssh
            and self.ssh.get_transport() is not None
            and self.ssh.get_transport().is_active()
        ):
            connected = True

        return connected

    def connect_to_cs(self, verify_connect=False):
        message = ''

        try:
            self.ssh.connect(
                self.client_loc,
                22,
                self.user,
                self.password
            )
        except Exception as e:
            raise Exception(
                'Failed connecting to CriticalStack client location - '
                + self.client_loc + ': ' + e.message
            )

        if verify_connect:
            message = self.run_cs_command('list')
            if(
                len(message) < 1
                or not any(
                    'Pulling feed list from' in line for line in message
                )
            ):
                raise Exception(
                    'Unable to verify CriticalStack connectivity using '
                    'command - sudo critical-stack-intel list. Please '
                    'verify the command works on the server and the user - '
                    + self.user + ' - is a sudoer. Details: ' + str(message)
                )

            if self._is_connected():
                self.ssh.close()

        return True

    def run_cs_command(self, cs_command):
        output = ''

        if not self._is_connected():
            self.connect_to_cs()

        try:
            stdin, stdout, stderr = self.ssh.exec_command(
                "sudo critical-stack-intel "
                + "--api-key=" + self.apiKey + " "
                + cs_command,
                get_pty=True
            )
        except Exception as e:
            raise Exception(
                'Failed running CriticalStack command - ' + cs_command
                + ' - at client location - ' + self.client_loc
                + ': ' + e.message
            )

        if stdout.channel.eof_received:
            sshError = stderr.readlines()
            if len(sshError) > 0:
                raise Exception(
                    'Failed running CriticalStack command - ' + cs_command
                    + ' - at client location - ' + self.client_loc
                    + '. Details: ' + str(sshError)
                )
        else:
            # Send Sudo Password
            stdin.write(''.join([self.password, '\n']))
            stdin.flush()

        try:

            # Put this in here just in case there's stdout hanging
            # timeout = 120
            # endtime = time.time() + timeout
            #
            # while not stdout.channel.eof_received:
            #     time.sleep(1)
            #     if time.time() > endtime:
            #         stdout.channel.close()
            #         break

            output = stdout.readlines()
        except Exception as e:
            raise Exception(
                'CriticalStack output verification failed running '
                'command - sudo critical-stack-intel ' + cs_command
                + '. Message: ' + e.message
            )

        if self._is_connected():
            self.ssh.close()

        return output

    def get_cs_list_data(self):
        cs_list = []

        if not self._is_connected():
            self.connect_to_cs()

        try:
            with closing(self.ssh.open_sftp()) as sftp:
                with closing(sftp.open(self.file_loc)) as cs_file:
                    cs_list = cs_file.readlines()
        except Exception as e:
            raise Exception(
                'Unable to read file - "' + self.file_loc + '" at '
                'location - "' + self.client_loc + '". Error: '
                + e.message
            )

        if self._is_connected():
            self.ssh.close()

        return cs_list
