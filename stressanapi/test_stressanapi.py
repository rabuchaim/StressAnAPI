#!/usr/bin/env python3
import unittest, json, os
from stressanapi import runCommand, stripColor, G, validateConfigFile
from stressanapi import threadMakeRequestsURLLib, getErrorResponseCode, getFormattedStatusCode

class TestStressAnAPI(unittest.TestCase):
    def test_extract_template_var(self):
        variables = {'url://path/%%randomipv4%%/test':'%%randomipv4%%',
                     'url://path/%%randomipv6%%/test':'%%randomipv6%%',
                     'url://path/test/%%randomprivateipv4%%':'%%randomprivateipv4%%',
                     'url://path/customer/%%randomint:1:1000%%':'%%randomint:1:1000%%'
                    }
        for key,val in variables.items():
            result = threadMakeRequestsURLLib.extract_template_var(self,key)
            self.assertEqual(result, val)  # Assert that the result is equal to the expected value

    def test_getErrorResponseCode(self):
        result = getErrorResponseCode('<urlopen error connection refused>')
        self.assertEqual(result, 900)
        result = getErrorResponseCode('<urlopen error timed out urlopen error>')
        self.assertEqual(result, 901)
        result = getErrorResponseCode('<reset by peer urlopen error>')
        self.assertEqual(result, 902)
        result = getErrorResponseCode('<urlopen error closed connection>')
        self.assertEqual(result, 903)
        result = getErrorResponseCode('<another 111 unknown 222 message 333>')
        self.assertEqual(result, 111)
        result = getErrorResponseCode('<another unknown message without error code>')
        self.assertEqual(result, 999)
        
    def test_getFormattedStatusCode(self):
        result = stripColor(getFormattedStatusCode(200))
        self.assertEqual(result,'200 OK')
        result = stripColor(getFormattedStatusCode(903))
        self.assertEqual(result,'### Remote end closed connection without response')
        result = stripColor(getFormattedStatusCode(999))
        self.assertEqual(result,'### Unknown Error')
        
if __name__ == '__main__':
    test_file = '/tmp/stressanapi_unit_test.json'
    template = G.default_template
    template['method'] = "GET"
    del template['syslog_server_url']
    
    with open(test_file,'w') as f:
        json.dump(G.default_template,f,indent=3)
    validateConfigFile(test_file)
    unittest.main()
    os.remove(test_file)
