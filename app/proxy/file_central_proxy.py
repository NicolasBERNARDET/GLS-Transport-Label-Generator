class FileCentralProxy:
    @staticmethod
    def get_file_central(server: str):
        if 's-05' in server.lower():
            return 'filecentral.s-05.saas-fr'
        elif 'p-05' in server.lower():
            return 'filecentral.p-05.saas-fr'
        return 'FILECENTRAL'
