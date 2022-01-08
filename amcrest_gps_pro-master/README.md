
'''
# Installation Process
- sudo add-apt-repository ppa:jonathonf/python-3.6
- sudo apt-get update
- sudo apt-get install python3.6
- sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1
- sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2
- sudo update-alternatives --config python3

- sudo apt-get install python3-pip
- sudo pip3 install virtualenv
'''

'''
# Create and Activate Virtualenv
- virtualenv <env>
- source env/bin/activate
'''

'''
# Install Dependencies
(Go to project folder)
- sudo apt-get install libmysqlclient-dev
- pip install setuptools==3.3
- sudo apt install python3.6-dev
- pip install -r requirements.txt

'''


'''
# Environment Variables
export AMCREST_RELATIONAL_USER=amcrest_1234
export AMCREST_RELATIONAL_DB=amcrest
export AMCREST_RELATIONAL_DB2=amcrest_listener
export AMCREST_RELATIONAL_PASSWORD=amcrest_1234
export AMCREST_RELATIONAL_HOST=18.209.141.132
export AMCREST_RELATIONAL_PORT=3306
export AMCREST_NON_RELATIONAL_PORT=27017
export AMCREST_NON_RELATIONAL_HOST=127.0.0.1
export AMCREST_NON_RELATIONAL_DB=amcrest
export AMCREST_EMAIL_HOST=smtp.mailgun.org
export AMCREST_EMAIL_HOST_USER=postmaster@mg.amcrest.in
export AMCREST_EMAIL_HOST_PASSWORD=1db52be4513bd7476298b425346bd685-b0aac6d0-733b8f3e
export AMCREST_EMAIL_PORT=587
export AMCREST_EMAIL_USE_TLS=True
export AMCREST_MONGO_USER=santosh
export AMCREST_MONGO_PASSWORD=Info@1234
export AMCREST_BRAINTREE_MERCHANT=bv5xh43c47krpfkr
export AMCREST_BRAINTREE_PUBLIC_KEY=t428h5pdcxwvcphk
export AMCREST_BRAINTREE_PRIVATE_KEY=bdfe5cbc1cd6c07c7d4e7c3633134e1e


---------------Digital Ocean-------------
export AMCREST_RELATIONAL_USER=root
export AMCREST_RELATIONAL_DB=amcrest
export AMCREST_RELATIONAL_DB2=amcrest_listener
export AMCREST_RELATIONAL_PASSWORD=Info@1234
export AMCREST_RELATIONAL_HOST=127.0.0.1
export AMCREST_RELATIONAL_PORT=3306
export AMCREST_NON_RELATIONAL_PORT=27017
export AMCREST_NON_RELATIONAL_HOST=127.0.0.1
export AMCREST_NON_RELATIONAL_DB=amcrest
export AMCREST_EMAIL_HOST=smtp.mailgun.org
export AMCREST_EMAIL_HOST_USER=postmaster@mg.amcrest.in
export AMCREST_EMAIL_HOST_PASSWORD=1db52be4513bd7476298b425346bd685-b0aac6d0-733b8f3e
export AMCREST_EMAIL_PORT=587
export AMCREST_EMAIL_USE_TLS=True
export AMCREST_MONGO_USER=santosh
export AMCREST_MONGO_PASSWORD=Info@1234
export AMCREST_BRAINTREE_MERCHANT=bv5xh43c47krpfkr
export AMCREST_BRAINTREE_PUBLIC_KEY=t428h5pdcxwvcphk
export AMCREST_BRAINTREE_PRIVATE_KEY=bdfe5cbc1cd6c07c7d4e7c3633134e1e


---------------Local-------------
export AMCREST_RELATIONAL_USER=root
export AMCREST_RELATIONAL_DB=amcrest
export AMCREST_RELATIONAL_DB2=amcrest_listener
export AMCREST_RELATIONAL_PASSWORD=r00t
export AMCREST_RELATIONAL_HOST=127.0.0.1
export AMCREST_RELATIONAL_PORT=3306
export AMCREST_NON_RELATIONAL_PORT=27017
export AMCREST_NON_RELATIONAL_HOST=127.0.0.1
export AMCREST_NON_RELATIONAL_DB=amcrest
export AMCREST_EMAIL_HOST=smtp.mailgun.org
export AMCREST_EMAIL_HOST_USER=postmaster@mg.amcrest.in
export AMCREST_EMAIL_HOST_PASSWORD=1db52be4513bd7476298b425346bd685-b0aac6d0-733b8f3e
export AMCREST_EMAIL_PORT=587
export AMCREST_EMAIL_USE_TLS=True
export AMCREST_MONGO_USER=santosh
export AMCREST_MONGO_PASSWORD=Info@1234
export AMCREST_BRAINTREE_MERCHANT=bv5xh43c47krpfkr
export AMCREST_BRAINTREE_PUBLIC_KEY=t428h5pdcxwvcphk
export AMCREST_BRAINTREE_PRIVATE_KEY=bdfe5cbc1cd6c07c7d4e7c3633134e1e


'''


scp /home/mayur/Documents/amcrest/phase2/registration/public.zip root@159.65.152.235:/root/