# ==================================================================================
#
#       Copyright (c) 2022 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================

from kfadapter import kfadapter_util

class Test_kfadapter_util:
    def setup_method(self):
        print('')
    
    def test_keys_match_diff_array(self):
        d1={'key1':{'a', 'b'}}
        d2={'key1':{'a', 'b'}}
        ret = kfadapter_util.keys_match(d1, d2)
        assert ret == True
        
    def test_keys_match_same_array(self):
        d1={'key1':{'a', 'b'}}
        d2={'key1':{'c', 'd'}}
        ret = kfadapter_util.keys_match(d1, d2)
        assert ret == True
        
    def test_random_suffix(self):
        ret = kfadapter_util.random_suffix()
        assert len(ret) == 10
        assert str(ret).islower() == True
        
    def test_run_finished_succeeded(self):
        ret = kfadapter_util.run_finished('SUCCEEDED')
        assert ret == True
    
    def test_run_finished_failed(self):
        ret = kfadapter_util.run_finished('FAILED')
        assert ret == True
        
    def test_run_finished_error(self):
        ret = kfadapter_util.run_finished('ERROR')
        assert ret == True
        
    def test_run_finished_skipped(self):
        ret = kfadapter_util.run_finished('SKIPPED')
        assert ret == True
        
    def test_run_finished_terminated(self):
        ret = kfadapter_util.run_finished('TERMINATED')
        assert ret == True

    def test_check_list(self):
        data = data = [[{'key1':'a'},3,4,5,6],[4,5,6,{'key2':'value2'}],3,4,5]
        ret = kfadapter_util.check_list(data, 'key1')  
        assert ret == 'a'
        
        ret = kfadapter_util.check_list(data, 'key2')  
        assert ret == 'value2'
        
    def test_check_map(self):
        data =  data = {'key3':[[{'keya':"a", 'keyb':"b"}, {'keyc':"c", 'keyd':"d"}, {'keye':"e", 'keyf':"f"}, {'keyg':"g", 'keyh':"h"}, {'keyi':"i", 'keyj':"j"}], [1,2,3,4]], 
    'key4':[[[[{'keya':"a", 'keyb':"b"}, {'keya':"a", 'keyb':"b"}, {'keya':"a", 'keyb':"b"}],[1, 2, 3],[5, 6, 4]],[4,5,6],[7,8,9]], ['e','f','g']]}
        ret = kfadapter_util.check_map(data, 'keya')
        assert ret == 'a'
        
        data = {'key3':[{'key1':"value1", 'key2':"value2"}, {'key3':"value1", 'key4':"value2"}], 'key4':[{'key1':"value1", 'key2':"value2"}, {'key3':"value1", 'key4':"value2"}]}
        ret = kfadapter_util.check_map(data, 'key1')
        assert ret == 'value1'
        
        data = {'key3':[1, 2, 3, 4, 5], 'key4':['a','b','e']}
        ret = kfadapter_util.check_map(data, 'key3')
        assert ret == [1, 2, 3, 4, 5]
