#
# Copyright 2021 DIGITAL.AI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import launchdarkly.LaunchDarklyClient
if classReload:
    reload(launchdarkly.LaunchDarklyClient)
from launchdarkly.LaunchDarklyClient import LaunchDarkly_Client
import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("LaunchDarkly")
launchDarkly = LaunchDarkly_Client.create_client(launchdarklyServer, username, password, token)
method = str(task.getTaskType()).lower().replace('.', '_')
logger.error("Call LaunchDarkly Method %s" % method)

call = getattr(launchDarkly, method)
response = call(locals())
logger.error("##### Return Values ####")

for key,value in response['output'].items():
    logger.error("%s = %s" % (key, value))
    locals()[key] = value

if 'reports' in response['output']:
    print("# Reports:\n\n")
    for key,value in response['output']['reports'].items():
        print("- [%s](%s)\n" % (key, value))
