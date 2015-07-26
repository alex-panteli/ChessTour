pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py shell < manual_test_init.py
python manage.py runserver