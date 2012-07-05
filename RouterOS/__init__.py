# coding: utf-8
import core
import socket
socket.setdefaulttimeout(10.0)

class ConnectionError(Exception):
    pass

class API:

    def __init__(self, ip, username, password):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, 8728))
        except socket.error:
            raise ConnectionError("Can't connect to the API port")
        
        self.api = core.Core(s)
        self.api.login(username, password)

    def do(self, full_action, **kwargs):
        action = full_action.split('/')[-1]
        path = '/'.join(full_action.split('/')[:-1])

        # Faz o parse dos parametros
        parsed_params = []
        query_words = []
        for key, value in kwargs.iteritems():
            if key.startswith('_'):
                query_words.append("?%s=%s" % (key[1:].replace('_','-'), value))
            else:
                parsed_params.append('=%s=%s' % (key.replace('_','-'), value))

        if action=='remove':
            for ID in self.getItemID(path, query_words):     # É necessário fazer a iteração sobre todos os items, pois pode
                params = [full_action, '=.id=%s'%ID]         # ocorrer de existir mais de um item com o mesmo paramemtro de ID 
                self.api.talk(params)                        # (Ex: mais de uma entrada de ip em IP -> ARP com macs diferentes)
                #print 'removing >>>', params
        elif action=='set':
            for ID in self.getItemID(path, query_words):
                params = [full_action, '=.id=%s'%ID]
                params.extend(parsed_params)
                self.api.talk(params)
                #print 'updating >>>', params
        elif action=='add':
            params = [full_action]
            params.extend(parsed_params)
            self.api.talk(params)
            #print 'adding >>>', params

    def getItemID(self, path, query_words):
        """Receives a path (eg: /ip/arp) and a set of query words
           Returns a list of .ids based on the query words
        """
        params = query_words
        params.insert(0, '%s/print'%path)
        result = self.api.talk(params)
        return [r[1]['.id'] for r in result if r[0]=='!re']
       
    #def arp_active(self):
    #    """Retorna a lista de usuarios atualmente ativos (online) no mikrotik via ARP.
    #    
    #    Requisitos:
    #    - Ativar a API do mikrotik
    #    - Configurar no mikrotik, em mangle, as regras para criar umam address-list dos
    #      usuarios ativos.
    #    """
    #    response = self.api.talk(['/ip/firewall/address-list/print'])
    #    for reg in response:
    #        if reg[0] == '!done':
    #            return
    #            
    #        yield reg[1]['address']
       
        
    def close(self):
        try:
            self.api.talk(['/quit'])
        except core.Error:
            print 'Disconnecting'

