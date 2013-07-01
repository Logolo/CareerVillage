project=$1
user=$2
# If you have easy_install, install pip using that
use=easy_install
hash easy_install 2>&- || {$use = pip} 
if [ $use = easy_install ]; then
	sudo easy_install pip
else
	wget http://python-distribute.org/distribute_setup.py
	sudo python distribute_setup.py
	rm distribute_setup.py
fi
# Now that we have pip, create the virtual environment
sudo pip install virtualenv
virtualenv $project
# activate the new virtualenv, and clone the git
cd $project
source bin/activate
git clone git://github.com/$user/$project.git
# enter project, install dependencies
cd $project
pip install -r requirements.txt
# manage git repos so we can push
git remote rm origin
git remote add origin git@github.com:$user/$project.git

