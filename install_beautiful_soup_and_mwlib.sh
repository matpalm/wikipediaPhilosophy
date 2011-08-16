sudo apt-get install libxml2-dev libxslt-dev

wget http://pypi.python.org/packages/source/m/mwlib/mwlib-0.12.15.zip
unzip mwlib-0.12.15.zip
cd mwlib-0.12.15
sudo python setup.py install

cd
wget http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.2.0.tar.gz
tar zxf BeautifulSoup-3.2.0.tar.gz
cd BeautifulSoup-3.2.0
sudo python setup.py install
