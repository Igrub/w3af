'''
yandex.py

'''


import core.controllers.outputManager as om

# options
from core.data.options.option import option
from core.data.options.optionList import optionList

from core.controllers.basePlugin.baseAuthPlugin import baseAuthPlugin
import core.data.kb.knowledgeBase as kb
from core.controllers.w3afException import w3afException
from core.data.parsers.urlParser import parse_qs

# Advanced shell stuff
from core.data.kb.exec_shell import exec_shell as exec_shell

import plugins.attack.payloads.shell_handler as shell_handler
from plugins.attack.payloads.decorators.exec_decorator import exec_debug

# Url creating
from core.data.parsers.urlParser import url_object
from urllib import urlencode

import re

class yandex(baseAuthPlugin):
    '''
    Exploit eval() vulnerabilities.
    
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''

    def __init__(self):
        baseAuthPlugin.__init__(self)
        self._testOption = False
        self._login = None
        self._password = None
        self._passport_host = 'passport.yandex-team.ru'
        

    def userLogin(self, uriOpener):
        '''
        User login
        
        '''

        u = url_object('http://%s/passport?mode=auth' % self._passport_host)
        res = uriOpener.GET(u)

        logged_username_re = re.compile(r"""
            \'displayName\'\:\'(?P<username>.*?)\'\,
        """, re.IGNORECASE+re.X)

        idkey_search_re = re.compile(r"""
            <input\s+
                type=\"hidden\"\s+
                name=\"idkey\"\s+
                value=\"(?P<idkey>.*?)\"\s*
            /?>
        """, re.IGNORECASE+re.X)

        idkey=None
        r = idkey_search_re.search(res.body)
        if r:
            idkey=r.group('idkey')

        values = {
            'login' : self._login,
            'passwd' : self._password,
            'idkey': idkey,
        }
        res = uriOpener.POST(u, urlencode(values))

        return None
    
    def userLogout(self, *args, **kwargs):
        '''
        User login
        
        '''
        return None
    
    def isUserLogged(self, uriOpener):
        '''
        Check user login
        
        '''
        logged_username_re = re.compile(r"""
            \'displayName\'\:\'(?P<username>.*?)\'\,
        """, re.IGNORECASE+re.X)
        u = url_object('http://%s/passport' % self._passport_host)
        res = uriOpener.GET(u)
        r = logged_username_re.search(res.body)
        logged_username=None
        if r:
            logged_username = r.group('username')

        import sys
        if logged_username==self._login:
            return True
        else:
            print >> sys.stderr, res.body

        return None
    
    def getOptions( self ):
        '''
        @return: A list of option objects for this plugin.
        '''

        d1 = 'Exploit only one vulnerability.'
        o1 = option('testOption', self._testOption, d1, 'boolean')
        
        d2 = 'Login'
        o2 = option('login', self._login, d2, 'string')
        
        d3 = 'Password'
        o3 = option('password', self._password, d3, 'string')
        
        d4 = 'Passport host'
        o4 = option('passport_host', self._passport_host, d4, 'string')

        ol = optionList()
        ol.add(o1)
        ol.add(o2)
        ol.add(o3)
        ol.add(o4)
        return ol

    def setOptions( self, optionsMap ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptions().
        
        @parameter optionsMap: A dict with the options for the plugin.
        @return: No value is returned.
        ''' 
        self._testOption = optionsMap['testOption'].getValue()
        self._login = optionsMap['login'].getValue()
        self._password = optionsMap['password'].getValue()
        self._passport_host = optionsMap['passport_host'].getValue()
            
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be runned before the
        current one.
        '''
        return []
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin exploits eval() vulnerabilities and returns a remote shell. 
        
        Six configurable parameters exist:
            - changeToPost
            - url
            - method
            - injvar
            - data
            - generateOnlyOne
        '''
