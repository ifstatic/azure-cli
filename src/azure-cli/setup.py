#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from codecs import open
from setuptools import setup, find_packages
import sys

try:
    from azure_cli_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger

    logger.warn("Wheel is not available, disabling bdist_wheel hook")
    cmdclass = {}

VERSION = "2.26.1"
# If we have source, validate that our version numbers match
# This should prevent uploading releases with mismatched versions.
try:
    with open('azure/cli/__main__.py', 'r', encoding='utf-8') as f:
        content = f.read()
except OSError:
    pass
else:
    import re

    m = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
    if not m:
        print('Could not find __version__ in azure/cli/__main__.py')
        sys.exit(1)
    if m.group(1) != VERSION:
        print('Expected __version__ = "{}"; found "{}"'.format(VERSION, m.group(1)))
        sys.exit(1)

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = [
    'antlr4-python3-runtime~=4.7.2',
    'azure-appconfiguration~=1.1.1',
    'azure-batch~=10.0.0',
    'azure-cli-core=={}'.format(VERSION),
    'azure-cosmos~=3.0,>=3.0.2',
    'azure-datalake-store~=0.0.49',
    'azure-functions-devops-build~=0.0.22',
    'azure-graphrbac~=0.60.0',
    'azure-identity',
    'azure-keyvault-administration==4.0.0b3',
    'azure-keyvault~=1.1.0',
    'azure-loganalytics~=0.1.0',
    'azure-mgmt-advisor==9.0.0',
    'azure-mgmt-apimanagement~=0.2.0',
    'azure-mgmt-appconfiguration~=2.0.0',
    'azure-mgmt-applicationinsights~=1.0.0',
    'azure-mgmt-authorization~=0.61.0',
    'azure-mgmt-batchai~=7.0.0b1',
    'azure-mgmt-batch~=15.0.0',
    'azure-mgmt-billing==6.0.0',
    'azure-mgmt-botservice~=0.3.0',
    'azure-mgmt-cdn==11.0.0',
    'azure-mgmt-cognitiveservices~=12.0.0',
    'azure-mgmt-compute~=22.0.0',
    'azure-mgmt-consumption~=2.0',
    'azure-mgmt-containerinstance~=1.4',
    'azure-mgmt-containerregistry==8.0.0',
    'azure-mgmt-containerservice~=16.0.0',
    'azure-mgmt-cosmosdb~=6.4.0',
    'azure-mgmt-databoxedge~=0.2.0',
    'azure-mgmt-datalake-analytics~=0.2.1',
    'azure-mgmt-datalake-store~=0.5.0',
    'azure-mgmt-datamigration~=9.0.0',
    'azure-mgmt-deploymentmanager~=0.2.0',
    'azure-mgmt-devtestlabs~=4.0',
    'azure-mgmt-dns~=8.0.0',
    'azure-mgmt-eventgrid==9.0.0',
    'azure-mgmt-eventhub~=4.1.0',
    'azure-mgmt-extendedlocation~=1.0.0b2',
    'azure-mgmt-hdinsight~=8.0.0',
    'azure-mgmt-imagebuilder~=0.4.0',
    'azure-mgmt-iotcentral~=9.0.0b1',
    'azure-mgmt-iothub==2.0.0',
    'azure-mgmt-iothubprovisioningservices~=0.2.0',
    'azure-mgmt-keyvault==9.0.0',
    'azure-mgmt-kusto~=0.3.0',
    'azure-mgmt-loganalytics~=11.0.0',
    'azure-mgmt-managedservices~=1.0',
    'azure-mgmt-managementgroups~=0.1',
    'azure-mgmt-maps~=2.0.0',
    'azure-mgmt-marketplaceordering==1.1.0',
    'azure-mgmt-media~=3.0',
    'azure-mgmt-monitor~=2.0.0',
    'azure-mgmt-msi~=0.2',
    'azure-mgmt-netapp~=4.0.0',
    'azure-mgmt-network~=19.0.0',
    'azure-mgmt-policyinsights~=1.0.0',
    'azure-mgmt-privatedns~=1.0.0',
    'azure-mgmt-rdbms~=8.1.0b4',
    'azure-mgmt-recoveryservicesbackup~=0.14.0',
    'azure-mgmt-recoveryservices~=2.0.0',
    'azure-mgmt-redhatopenshift==0.1.0',
    'azure-mgmt-redis~=13.0.0',
    'azure-mgmt-relay~=0.1.0',
    'azure-mgmt-reservations==0.6.0',  # TODO: Use requirements.txt instead of '==' #9781
    'azure-mgmt-resource==18.0.0',
    # 'azure-mgmt-reservations~=0.6.0',
    'azure-mgmt-search~=8.0',
    'azure-mgmt-security~=0.6.0',
    'azure-mgmt-servicebus~=6.0.0',
    'azure-mgmt-servicefabric~=0.5.0',
    'azure-mgmt-servicefabricmanagedclusters~=1.0.0',
    'azure-mgmt-signalr~=1.0.0b2',
    'azure-mgmt-sqlvirtualmachine~=0.5.0',
    'azure-mgmt-sql~=3.0.1',
    'azure-mgmt-storage~=18.0.0',
    'azure-mgmt-synapse~=2.0.0',
    'azure-mgmt-trafficmanager~=0.51.0',
    'azure-mgmt-web~=2.0.0',
    'azure-multiapi-storage~=0.6.2',
    'azure-storage-common~=1.4',
    'azure-synapse-accesscontrol~=0.5.0',
    'azure-synapse-artifacts~=0.6.0',
    'azure-synapse-spark~=0.2.0',
    'fabric~=2.4',
    'javaproperties==0.5.1',
    'jsmin~=2.2.2',
    'jsondiff==1.2.0',
    'packaging~=20.9',
    'PyGithub~=1.38',
    'PyNaCl~=1.4.0',
    'pytz==2019.1',
    'scp~=0.13.2',
    'semver==2.13.0',
    'sshtunnel~=0.1.4',
    'websocket-client~=0.56.0',
    'xmltodict~=0.12'
]

TESTS_REQUIRE = [
    'mock~=4.0'
]

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()

setup(
    name='azure-cli',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools',
    long_description=README,
    license='MIT',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli',
    zip_safe=False,
    classifiers=CLASSIFIERS,
    scripts=[
        'az',
        'az.completion.sh',
        'az.bat',
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "azure", "azure.cli"]),
    install_requires=DEPENDENCIES,
    python_requires='>=3.6.0',
    package_data={
        'azure.cli.command_modules.acr': ['*.json'],
        'azure.cli.command_modules.botservice': ['*.json', '*.config'],
        'azure.cli.command_modules.monitor.operations': ['autoscale-parameters-template.json'],
        'azure.cli.command_modules.servicefabric': [
            'template/windows/template.json',
            'template/windows/parameter.json',
            'template/linux/template.json',
            'template/linux/parameter.json',
            'template/service/template.json',
            'template/service/parameter.json'
        ],
        'azure.cli.command_modules.appservice': [
            'resources/WindowsFunctionsStacks.json',
            'resources/LinuxFunctionsStacks.json',
            'resources/WebappRuntimeStacks.json',
            'resources/GenerateRandomAppNames.json'
        ],
        'azure.cli.command_modules.rdbms': [
            'randomname/adjectives.txt',
            'randomname/nouns.txt',
            'templates/mysql_githubaction_template.yaml',
            'templates/postgresql_githubaction_template.yaml'
        ]
    },
    cmdclass=cmdclass
)
