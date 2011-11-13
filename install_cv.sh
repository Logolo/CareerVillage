$project = CareerVillage
sudo pip install virtualenv
virtualenv $project --no-site-packages
cd $project
source bin/activate
git clone git@github.com:jchubber/$project.git
cd $project
pip install -r requirements.txt
python manage.py syncdb
