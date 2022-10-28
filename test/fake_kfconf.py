from kfadapter.tmgr_logger import TMLogger

class FakeKfConf:
    __instance = None

    def get_instance():
        if FakeKfConf.__instance is None:
            FakeKfConf()

        return FakeKfConf.__instance

    def __init__(self):
        FakeKfConf.__instance = self

        self.kf_dict = {}
        self.ucmgr_dict = {}
        self.tmgr_logger = TMLogger("config/log_config.yaml")
        self.logger = self.tmgr_logger.logger

        self.run_status_polling_interval_sec = 20
        self.kf_dict['kfhostname'] = 'kfhostname'
        self.kf_dict['kfport'] = 9999
        self.kf_dict['kfdefaultns'] = 'ai-server'
        self.appport = 7777
        self.ucmgr_dict['ucmgr_host'] = '127.0.0.1'
        self.ucmgr_dict['ucmgr_port'] = 30025
