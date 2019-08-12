
########## clone repo if not done

git clone https://github.com/theis188/jobs-numbers-website.git
cd jobs-numbers-website

########## install pip

sudo apt install python-pip

##########

pip install -r requirements.txt

##########

sudo apt update
sudo apt install nginx

# sudo systemctl stop nginx
# sudo systemctl start nginx
# sudo systemctl restart nginx

########## 

sudo apt install ufw
# sudo ufw default deny incoming
# sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 5000
##########

# sudo apt update
sudo apt install redis-server
redis-cli KEYS *
sudo systemctl restart redis.service

#########

sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv

python3.6 -m venv jobs_numbers
source jobs_numbers/bin/activate
pip install wheel
pip install -r requirements.txt
pip install uwsgi

cp jobs_numbers.service /etc/systemd/system/jobs_numbers.service

sudo systemctl start jobs_numbers
sudo systemctl enable jobs_numbers
sudo systemctl status jobs_numbers

systemctl daemon-reload

cp nginx_conf.txt /etc/nginx/sites-available/jobs_numbers
sudo ln -s /etc/nginx/sites-available/jobs_numbers /etc/nginx/sites-enabled
sudo nginx -t

#########

cp -r static /var/www/html

#########

scp /mnt/c/dev/jobs_numbers_website/database/OE.db root@159.65.247.56:/root/jobs-numbers-website/database

#########

sudo add-apt-repository ppa:certbot/certbot
sudo apt install python-certbot-nginx
sudo systemctl reload nginx
sudo ufw allow 'Nginx Full'
sudo certbot --nginx -d jobs-numbers.com -d www.jobs-numbers.com #(2)
sudo certbot renew --dry-run

