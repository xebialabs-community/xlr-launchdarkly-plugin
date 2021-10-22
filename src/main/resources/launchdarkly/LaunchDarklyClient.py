#
# Copyright 2021 DIGITAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import traceback
import sets
import sys
import urllib
import json
from xlrelease.HttpRequest import HttpRequest
import org.slf4j.Logger as Logger
import org.slf4j.LoggerFactory as LoggerFactory

HTTP_SUCCESS = sets.Set([200, 201, 202, 203, 204, 205, 206, 207, 208])
HTTP_ERROR = sets.Set([400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410,412, 413, 414, 415])

class LaunchDarkly_Client(object):
    def __init__(self, httpConnection, token=None):
        self.httpConnection = httpConnection
        self.logger = LoggerFactory.getLogger("LaunchDarkly")
        if token == None:
            self.token = httpConnection['token']
        self.httpRequest = HttpRequest(httpConnection, token)

    @staticmethod
    def create_client(httpConnection, token=None):
        return LaunchDarkly_Client(httpConnection, token)

    def testServer(self):
        launchDarklyUrl = 'api/v2/tokens'
        self.logger.error("Open URL %s" % launchDarklyUrl)
        header = {"Authorization": self.token}
        response = self.httpRequest.get(launchDarklyUrl, headers=header, contentType='application/json')
        if response.getStatus() in HTTP_SUCCESS:
            data = json.loads(response.getResponse())
            self.logger.error("\n=====================\n%s\n=====================\n" % data )
            return
        self.logger.error("HTTP ERROR Code = %s" % response.getStatus() )
        self.throw_error(response)

    def launchdarkly_listallfeatures(self, variables):
        query=""
        if variables['tag'] is not None :
            query="/?tag=%s" % variables['tag']
        launchDarklyUrl = "/api/v2/flags/%s%s" % ( variables['projectKey'], query)
        header = {"Authorization": self.token}
        self.logger.error("List All Features Request %s" % launchDarklyUrl)
        response = self.httpRequest.get(launchDarklyUrl, headers=header, contentType='application/json')
        data = json.loads(response.getResponse())
        self.logger.debug("List All Configurations Response\n=============\n%s\n==================" % json.dumps(response.getResponse(), indent=4, sort_keys=True))
        if response.getStatus() not in HTTP_SUCCESS:
            self.logger.error("List All Features Request Error (%s)" % response.getStatus())
            self.throw_error(response)
        items = data['items']
        results = {}
        for item in items:
            self.logger.error("%s = %s" % (item['key'], item['name']))
            results[item['key']] = item['name']
        return {'output': {'items': results, 'featureKeys': results.keys() } }

    def launchdarkly_getfeatureflagstatus(self, variables):
        launchDarklyUrl = "api/v2/flags/%s/%s" % ( variables['projectKey'], variables['featureKey'])
        header = {"Authorization": self.token}
        self.logger.error("List A Feature Request %s" % launchDarklyUrl)
        response = self.httpRequest.get(launchDarklyUrl, headers=header, contentType='application/json')
        data = json.loads(response.getResponse())
        self.logger.debug("List All Configurations Response\n=============\n%s\n==================" % json.dumps(response.getResponse(), indent=4, sort_keys=True))
        if response.getStatus() not in HTTP_SUCCESS:
            self.logger.error("List A Feature Request Error (%s)" % response.getStatus())
            self.throw_error(response)
        data['status'] = data['environments'][variables['environmentKey']]['on']
        return {'output': data}

    def launchdarkly_getlistoffeatureflagstatuses(self, variables):
        callData = {}
        callData['projectKey'] = variables['projectKey']
        callData['environmentKey'] = variables['environmentKey']
        statusList = {}
        for key in variables['featureList'] :
            callData['featureKey'] = key
            data = self.launchdarkly_getfeatureflagstatus(callData)['output']
            statusList[key] = data['status']
            self.logger.error("%s = %s" % (key, statusList[key]) )
        self.logger.error("============================")
        return { 'output': { 'statusList': statusList } }

    def launchdarkly_setfeatureflagstatus(self, variables):
        launchDarklyUrl = "api/v2/flags/%s/%s" % ( variables['projectKey'], variables['featureKey'] )

        header = {
            "Content-Type": "application/json; domain-model=launchdarkly.semanticpatch",
            "Authorization": self.token
            }

        if variables['status']:
            instruction = "turnFlagOn"
        else:
            instruction = "turnFlagOff"

        self.logger.error("Set Feature flag Status %s" % launchDarklyUrl)
        envKey = variables['environmentKey']
        payload =   {
                        'environmentKey': envKey,
                        'instructions': [
                            {
                                'kind': instruction
                            }
                        ]
                    }

        response = self.httpRequest.patch(launchDarklyUrl, json.dumps(payload), headers=header )
        self.logger.debug("Get Feature Flag Status Response\n=============\n%s\n==================" % json.dumps(response.getResponse(), indent=4, sort_keys=True))
        if response.getStatus() not in HTTP_SUCCESS:
            self.logger.error("Get Feature Flag Status Request Error (%s)" % response.getStatus())
            self.throw_error(response)
        data = json.loads(response.getResponse())
        data['outStatus'] = data['environments'][variables['environmentKey']]['on']
        return { 'output': { 'outStatus': data['outStatus'] } }

    def launchdarkly_setlistoffeatureflagstatuses(self, variables):
        callData = {}
        callData['projectKey'] = variables['projectKey']
        callData['environmentKey'] = variables['environmentKey']
        callData['status'] = variables['status']
        statusList = {}
        for key in variables['featureList'] :
            callData['featureKey'] = key
            data = self.launchdarkly_setfeatureflagstatus(callData)['output']
            statusList[key] = data['outStatus']
            self.logger.error("%s = %s" % (key, statusList[key]) )
        self.logger.error("============================")
        return { 'output': { 'statusList': statusList } }


    def throw_error(self, response):
        self.logger.error("Error from LaunchDarklyService, HTTP Return: %s\n" % ( response.getStatus() ) )
        raise Exception(response.getStatus())
