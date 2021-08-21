# crypto wallet

### note

Nothing about authorization/authentication in tasks description, so everybody can send money from any wallet.

### docker-compose

docker-compose up -d --build<br>
docker-compose exec web pytest<br>

### alternatively
python manage.py migrate<br>
pytest # run test<br>
python manage.py runserver<br>
cd crypto_wallet<br>
pip install virtualenv<br>
virtualenv venv<br>
source venv/bin/activate<br>
pip install -r requirements.txt<br>

### schema

localhost:8000/swagger/
