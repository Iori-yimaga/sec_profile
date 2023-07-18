class GetNewBook(object):
    """
    获得最新的网络安全数据
    """
    def __init__(self, **kwargs):
        """
        初始化
        :param kwargs:
        """
        self.rss_url = 'http://libgen.rs/rss/index.php'
        self.cybersecurity_keywork = [
            'cybersecurity',
            'malware',
            'threat intelligence'
        ]



