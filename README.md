# Photo Friends

A project to share photos between friends or family easily 

## Development installation

```bash
pyenv install 3.9.9 # if not done
pyenv local 3.9.9
poetry install
poetry run python manage.py migrate
```

## Development launch

```bash
python manage.py runserver
```

## Production installation

This project relies on Docker-compose and is designed to have a Nginx / Apache reverse proxy on the host

2 solutions to deploy, Ansible or manual. In both create first create a `.env` (in ansible directory if you choose Ansible) 


```env
STATIC_ROOT=/var/www/photofriends/static
MEDIA_ROOT=/var/www/photofriends/media
DB_ROOT=/var/www/photofriends/db
DEBUG=False
ADMINS=name,you@something.com
EMAIL_HOST_USER=YOURLOGIN
EMAIL_HOST_PASSWORD=YOUPASSWORD
STATIC_URL=https://DOMAIN_NAME/static/
DJANGO_SUPERUSER_USERNAME=ADMIN_LOGIN
DJANGO_SUPERUSER_PASSWORD=ADMIN_PASSWORD
DJANGO_SUPERUSER_EMAIL=admin@DOMAIN_NAME
```

### Simple ansible deployment
- Go in `ansible` directory
- Edit inventory.ini file to set the ight hostname
- ansible-playbook install_photo-friends.yaml -i inventory.ini

### Manual deployment

Go in your VM

#### Prerequisite

Docker and docker-compose
```bash
sudo apt install docker-compose
sudo adduser ubuntu docker
# logout and log again
```

#### Production installation

Install and configure nginx
```bash
sudo apt install nginx python3-certbot-nginx
sudo certbot --nginx
```

Add reverse proxy and statics configurations into `/etc/nginx/sites-available/default`

```nginx
        location / {
                include proxy_params;
                proxy_pass         http://127.0.0.1:9000;
                client_max_body_size 0;

                access_log      /var/log/nginx/photofriends.access.log;
                error_log       /var/log/nginx/photofriends.error.log;
        }
        location /static/ {
                alias /var/www/photofriends/static/;
        }
         location /media/ {
                alias /var/www/photofriends/media/;
        }
```

Restart nginx and prepare static directory mount point for Docker
```bash
sudo service docker restart
sudo mkdir -p /var/www/photofriends/static /var/www/photofriends/media
sudo chown -R www-data:www-data /var/www/photofriends
```
By build it on local + save + load or via your favorite registry
 or build it on local after a clone
```bash
git clone https://github.com/Benji81/photo-friends.git
cd photo-friends
./build-docker.sh
```



Start docker-compose and add a user
```bash
docker-compose up -d
docker exec -it photofriends_django_1 poetry run python manage.py createsuperuser
```

## Update production

```bash
git pull
./build-docker.sh
docker-compose down
docker-compose up -d
```
