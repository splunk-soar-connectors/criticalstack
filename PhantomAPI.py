import json
import requests


class PhantomList(object):

    def __init__(
        self,
        base_url='https://127.0.0.1',
        verify_cert=False
    ):
        self.base_url = base_url
        # self.auth_token = auth_token
        # self.header = {
        #     "ph-auth-token": self.auth_token
        # }
        self.header = {}
        self.verify_cert = False

    def _list_exists(self, list_name):
        found = True
        response = self.get_list(list_name)

        if 'failed' in response:
            if 'item not found' in response['message']:
                found = False
            else:
                # something terribly wrong happned
                raise Exception(
                    'Error reading from list - ' + list_name
                    + '. Error: ' + response['message']
                )

        return found

    def _send_request(self, url, method, payload=None, content_type=None):
        url = self.base_url + url

        try:
            if(method == "GET"):
                r = requests.get(
                    url,
                    headers=self.header,
                    data=payload,
                    verify=self.verify_cert
                )
            elif(method == "POST"):
                r = requests.post(
                    url,
                    headers=self.header,
                    data=payload,
                    verify=self.verify_cert
                )
            elif(method == "DELETE"):
                r = requests.post(
                    url,
                    headers=self.header,
                    data=payload,
                    verify=self.verify_cert
                )
            elif(method == "PUT"):
                r = requests.put(
                    url,
                    headers=self.headers,
                    data=payload,
                    verify=False
                )
            r.raise_for_status
        except requests.exceptions.SSLError as err:
            raise Exception(
                'Error connecting to API - '
                'Likely due to the "validate server certificate" option. '
                'Details: ' + str(err)
            )
        except requests.exceptions.HTTPError as err:
            raise Exception(
                'Error calling - ' + url + ' - \n'
                'HTTP Status: ' + r.status
                + 'Reason: ' + r.reason
                + 'Details: ' + str(err)
            )
        except requests.exceptions.RequestException as err:
            raise Exception(
                'Error calling - ' + url + ' - Details: ' + str(err)
            )

        try:
            results = r.json()
        except ValueError:
            results = r.text

        return results

    def create_list(self, list_data, list_name, overwrite=True):
        list_json = {
            "content": list_data,
            "name": list_name
        }

        list_exists = self._list_exists(list_name)

        if not overwrite and list_exists:
            raise Exception(
                'Cannot create list - ' + list_name + ' - because '
                'it already exists.'
            )
        elif list_exists:
            response = self._send_request(
                '/rest/decided_list/' + list_name,
                'POST',
                payload=json.dumps(list_json),
                content_type='application/json'
            )
        elif not list_exists:
            response = self._send_request(
                '/rest/decided_list',
                'POST',
                payload=json.dumps(list_json),
                content_type='application/json'
            )

        return response

    def get_list(self, list_name):
        response = self._send_request(
            '/rest/decided_list/' + list_name + '?_output_format=JSON',
            'GET',
        )

        return response

    def search_list(self, list_data, column_num, search_val, find_all=True):

        if len(list_data['content'][0]) < column_num:
            raise Exception(
                'Searching in column number - ' + column_num + ' but '
                'the list - ' + list_data['name'] + ' has only '
                + len(list_data['content'][0]) + ' columns.'
            )

        found_rows = []

        for row_num, record in enumerate(list_data['content']):
            if search_val == record[column_num]:
                found_rows.append(row_num)
                if not find_all:
                    break

        return found_rows