from setuptools import setup

setup(
    name='ansible-manageiq_api',
    description='Ansible ManageIQ API',
    author='Drew Bomhof',
    email='dbomhof@redhat.com',
    url='https://github.com/syncrou/manageiq-ansible_api',
    package_dir={'': 'library'},
    pymodules=['ansible-manageiq_api'],
    install_requires='ansible manageiq-client'.split(),
)
