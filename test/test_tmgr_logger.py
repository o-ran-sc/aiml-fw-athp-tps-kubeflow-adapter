import sys
sys.path.append("../kfadapter")
from tmgr_logger import TMLogger

class Test_tmgr_logger:
    def setup_method(self):
        self.TMGR_LOGGER_OBJ = TMLogger("../config/log_config.yaml")
        
    def test_get_loglevel(self):
        ret = self.TMGR_LOGGER_OBJ.get_logLevel
        assert ret == 'DEBUG'
    
    def test_get_logger(self):
        ret = self.TMGR_LOGGER_OBJ.get_logger
        assert ret != None