import configparser, os


class ConfigParse():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.getcwd() + "/PhishingCampaignConfig.ini")
    
    def get_config(self):
        return self.config
    

