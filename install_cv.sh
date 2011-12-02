# If you have easy_install, install pip using that
$use = easy_install
hash easy_install 2>&- || { $use = pip } 
if [$use = easy_install]
	sudo easy_install pip
else
	curl -O http://python-distribute.org/distribute_setup.py
	python distribute_setup.py
fi
# Now that we have pip, create the virtual environment
$project = CareerVillage
sudo pip install virtualenv
virtualenv $project --no-site-packages
# activate the new virtualenv, and clone the git
cd $project
source bin/activate
git clone git@github.com:jchubber/$project.git
# enter project, install dependencies
cd $project
pip install -r requirements.txt
# create local version of standard settings
cp settings_local.py.dist settings_local.py
# syncdb and migration. This should create a superuser as well.
python manage.py syncdb --all 
python manage.py migrate forum --fake
# TODO CSS customization
