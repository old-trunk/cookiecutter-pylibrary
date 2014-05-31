#!.tox/configure/bin/python
import re
from itertools import product, chain
from jinja2 import FileSystemLoader, Environment
jinja = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
mangle_name = re.compile(r'[A-Za-z/:.>]+[/=]+(.*?)(,.*|/.*)?$')
mangle_python = re.compile(r'[\\/:>]+')

########################################################
################# EDIT AFTER THIS LINE #################
pythons = [
{%- for ver in cookiecutter.test_pythons.split('|') %}
    {{ ver.__repr__() }},
{%- endfor %}
]
deps = [  # set to [''] if you have no deps
{%- for ver in cookiecutter.test_dependencies.split('|') %}
    {{ ver.__repr__() }},
{%- endfor %}
]
covers = [True, False]
envs = ['']  # could be some env vars that activate certain features

skips = list(chain(  # set to [] if you don't want to skip anything
    # skip 1.4 on py3
    product(
        ['3.3', '3.4'],
        [dep for dep in deps if 'Django==1.4' in dep],
        covers,
        envs
    ),
    # skip 1.7 on py2.6
    product(
        ['2.6'],
        [dep for dep in deps if 'djangoproject.com/download/1.7' in dep],
        covers,
        envs
    ),
))
########### SHOULD NOT EDIT BELOW THIS LINE ############
########################################################

# the list of environments is the product of python versions,
# dependencies, coverage switches (on/off) and
# environment variables

matrix = {}
for python, dep, cover, env in product(pythons, deps, covers, envs):
    if (python, dep, cover, env) not in skips:
        name = '-'.join(filter(None, (  # mangle the python version, deps,
                                        # cover flags and env vars into
                                        # something pretty
            mangle_python.sub(r'_', python),
            '-'.join(mangle_name.sub(r'\1', dep).split(' ')), # strip useless characters
            '' if cover else 'nocover',
            env and env.lower().replace('_', ''),
        )))

        matrix[name] = {
            'python': 'python' + python if 'py' not in python else python,
            'deps': dep.split(),
            'cover': cover,
            'env': env,
        }

with open('tox.ini', 'w') as fh:
    fh.write(jinja.get_template('tox.tmpl.ini').render(matrix=matrix))

with open('.travis.yml', 'w') as fh:
    fh.write(jinja.get_template('.travis.tmpl.yml').render(matrix=matrix))

print("DONE.")