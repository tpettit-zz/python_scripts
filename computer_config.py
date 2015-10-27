from string import Template


class PercentTemplate(Template):
    delimiter = '%'


config = {
    'git': {
        'user': {
            'email': 'timothp@amazon.com',
            'name': 'timothp',
        },
        'color': {
            'ui': 'true',
        },
        'core': {
            'pager': 'less -FMRiX',
        },
        'push': {
            'default': 'tracking',
        },
        'alias': {
            'br': 'branch',
            'ci': 'commit',
            'co': 'checkout',
            'st': 'status',
        },
        'branch': {
            'autosetuprebase': 'always',
        },
        'amazon': {
            'append-cr-url': 'true',
            'pull-request-by-default': 'true',
        },
    },
    'laptop': {
        'host': 'timothp-laptop.aka.corp.amazon.com',
        'home': '/Users/timothp',
        'bashrc': {
            'name': '.profile',
            'pre_tmpl': PercentTemplate(open('laptop.tmpl', 'r').read())
        },
        'git': 'git'
    },

    'desktop': {
        'host': 'timothp.aka.amazon.com',
        'home': '/home/timothp',
        'bashrc': '.bashrc',
        'git': '/apollo/env/SDETools/bin/git'
    },
    'bashrc': PercentTemplate(open('bashrc.tmpl', 'r').read())
}

config['laptop']['desktop'] = config['desktop']['host']
config['laptop']['laptop'] = config['laptop']['host']

config['desktop']['desktop'] = config['desktop']['host']
config['desktop']['laptop'] = config['laptop']['host']
