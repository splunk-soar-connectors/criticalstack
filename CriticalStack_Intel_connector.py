from CriticalStack import Intel
from datetime import datetime
from phantom.action_result import ActionResult
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from PhantomAPI import PhantomList


class CriticalStack_Intel_connector(BaseConnector):

    BANNER = "CriticalStack Connector"
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    CS_DATA_TYPES = {'ip': 'ADDR', 'domain': 'DOMAIN', 'hash': 'FILE_HASH'}
    CS_LAST_UPDATED_LIST = 'CriticalStack-LastUpdated'

    def initialize(self):
        return phantom.APP_SUCCESS

    def finalize(self):
        return

    def handle_exception(self, exception_object):
        """All the code within BaseConnector::_handle_action is within a 'try:
        except:' clause. Thus if an exception occurs during the execution of
        this code it is caught at a single place. The resulting exception
        object is passed to the AppConnector::handle_exception() to do any
        cleanup of it's own if required. This exception is then added to the
        connector run result and passed back to spawn, which gets displayed
        in the Phantom UI.
        """

        return

    def _initialize_critical_stack(self, config):
        cs = Intel(
            config.get('criticalStackServer'),
            config.get('sshUser'),
            config.get('sshPassword'),
            apiKey=config.get('criticalStackApiKey'),
            file_loc=config.get('criticalStackFileLoc')
        )

        return cs

    def _initialize_phantom_list(self, config):
        phant = PhantomList(
            verify_cert=config.get("verifyPhantomServerCert"),
            base_url=self.get_phantom_base_url()
        )

        return phant

    def _pluralize(self, cs_type):
        return {
            'IP': 'IPs',
            'DOMAIN': 'domains',
            'HASH': 'hashes'
        }[cs_type.upper()] or 'unknown'

    def _set_error(self, action_result, message, err):
        action_result.set_status(
            phantom.APP_ERROR,
            message,
            err.message
        )
        return action_result.get_status()

    def _update_needed(self, phant, prefix):

        last_updated_list = phant.get_list(self.CS_LAST_UPDATED_LIST)
        last_updated_record = []
        update_needed = True

        if('content' in last_updated_list and len(last_updated_list['content'][0]) < 2):
            raise IndexError('{0} - list is malformed. Expected Column1-Prefix, Column2-Last Updated Date.'.format(self.CS_LAST_UPDATED_LIST))
        elif 'content' in last_updated_list:
            last_updated_record = [
                record for record in last_updated_list['content']
                if record[0] == prefix
            ]

        if len(last_updated_record) > 0:

            try:
                t1 = datetime.strptime(
                    last_updated_record[0][1],
                    self.TIME_FORMAT
                )
            except ValueError as err:
                raise ValueError('Second column of list - {0} - does not represent a date time in {1} format. Details: {2}'.format(self.CS_LAST_UPDATED_LIST,
                                 self.TIME_FORMAT, err.message))

            now = datetime.now()

            if((now - t1).total_seconds() < 1800):
                update_needed = False

        return update_needed

    def _update_phantom_lists(self, cs, phant, prefix):
        cs.run_cs_command('pull')
        response = cs.get_cs_list_data()

        for cs_type in list(self.CS_DATA_TYPES.values()):
            cs_list = [record for record in response if 'Intel::' + cs_type in record]

            phant.create_list([line.split('\t') for line in cs_list], prefix + '-' + cs_type)

        last_updated_list = phant.get_list(self.CS_LAST_UPDATED_LIST)

        now = datetime.now().strftime(self.TIME_FORMAT)

        if 'content' in last_updated_list:
            rows_to_update = phant.search_list(last_updated_list, 0, prefix)
            if len(rows_to_update) > 0:
                for row_num in rows_to_update:
                    if len(last_updated_list['content'][row_num]) < 2:
                        raise IndexError('{0} - list is malformed. Expected Column1-Prefix, Column2-Last Updated Date.'.format(self.CS_LAST_UPDATED_LIST))
                    else:
                        last_updated_list['content'][row_num][1] = now
            else:
                last_updated_list['content'].append([prefix, now])

            phant.create_list(last_updated_list['content'], self.CS_LAST_UPDATED_LIST)
        else:
            phant.create_list([[prefix, now]], self.CS_LAST_UPDATED_LIST)

        return

    def _perform_action(self, param, cs_type):
        config = self.get_config()
        prefix = config.get('criticalStackPrefix')

        action_result = self.add_action_result(ActionResult(dict(param)))

        cs = self._initialize_critical_stack(config)
        phant = self._initialize_phantom_list(config)

        try:
            update_needed = self._update_needed(
                phant,
                prefix
            )
        except Exception as err:
            return self._set_error(action_result, 'Phantom List Error 1', err)

        if update_needed:
            try:
                self._update_phantom_lists(cs, phant, prefix)
            except Exception as err:
                return self._set_error(action_result, 'Phantom List Error 2', err)

        try:
            phantom_list = phant.get_list(prefix + '-' + self.CS_DATA_TYPES[cs_type])
        except Exception as err:
            return self._set_error(action_result, 'Phantom List Error 3', err)

        found_rows = []

        if('content' in phantom_list):

            try:
                found_rows = phant.search_list(phantom_list, 0, param[cs_type])
            except Exception as err:
                return self._set_error(action_result, 'Phantom List Error 4', err)
            else:
                message = "{0} {1} scanned.".format(str(len(phantom_list['content'])), self._pluralize(cs_type))

        else:
            message = 'No {0} exist in {1}-{2}'.format(self._pluralize(cs_type), prefix, self.CS_DATA_TYPES[cs_type])

        summary = {
            'detected_' + cs_type + '_count': str(len(found_rows)),
            'lists_updated': update_needed,
            'list_prefix': prefix,
            'additional_details': message
        }

        results = {'sources': []}

        if len(found_rows) > 0:
            results = {
                'sources':
                [
                    {
                        cs_type: phantom_list['content'][row][0],
                        'source': phantom_list['content'][row][2]
                    } for row in found_rows
                ]
            }

        action_result.update_summary(summary)
        action_result.add_data(results)
        action_result.set_status(phantom.APP_SUCCESS)

        return action_result.get_status()

    def _test_connectivity(self, param):
        config = self.get_config()

        cs = self._initialize_critical_stack(config)
        phant = self._initialize_phantom_list(config)

        try:
            cs.connect_to_cs(verify_connect=True)
        except Exception as err:
            self.save_progress("Test Connectivity Failed.")
            self.set_status(phantom.APP_ERROR, 'Error connecting to Phantom API. Details: {0}'.format(err.message))
            return self.get_status()

        try:
            phant.get_list('testConnectionList')
        except Exception as err:
            self.save_progress("Test Connectivity Failed.")
            self.set_status(phantom.APP_ERROR, '{0} Error connecting to Phantom API. Details: {1}'.format(config.get('phantomApiKey'), err.message))
            return self.get_status()

        msg = "Successfully logged into - {0} and ran - sudo critical-stack-intel list. Succesfully connected to Phantom API.".format(config.get('criticalStackServer'))
        self.set_status(phantom.APP_SUCCESS, msg)

        self.save_progress("Test Connectivity Passed.")
        return self.get_status()

    def handle_action(self, param):

        action_id = self.get_action_identifier()

        supported_actions = {
            "test connectivity": self._test_connectivity,
            "ip reputation": self.ip_reputation,
            "domain reputation": self.domain_reputation,
            "file reputation": self.file_reputation
        }

        run_action = supported_actions[action_id]

        return run_action(param)

    def ip_reputation(self, param):

        return self._perform_action(param, 'ip')

    def domain_reputation(self, param):

        return self._perform_action(param, 'domain')

    def file_reputation(self, param):

        return self._perform_action(param, 'hash')
