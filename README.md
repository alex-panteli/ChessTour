ChessTour
=============

ChessTour a sample Django/BackBone.js project for managing chess tournament pairing and scoring. 

Requirements
------------
python 2.7.6+ environment with pip installed


Installation/Deployment
-----------------------
Just run deploy-chesstour script (shell or bat) and it will install all dependencies, sample data (local sqlite3 file) and start the django developemt server listening to default port 8000.

Sample referee profile credentials: jdoe / 1234
Sample admin credentials          : admin / password

(Django) Tests are run as usual with

```
python manage.py test
```

and produce a coverage report automatically

Features
--------
- Automatic pairing for the next round upon completion of a round or creation of a new tournament
- Pairing using swiss-event style rules, using a modified version of PyPair by Jeff Hoogland
- Player color balancing
- Keeps track of live elo rating recalculation per game (not shown/used anywhere though...)
- Support for byes

Goodies
-------
- Single Page Application
- Responsive design using Twitter Bootstrap throughout (including admin page)
- Basic http auth
- REST api developed with django-tastypie
- Object level permissions using django-guardian

Screenshots
-----------
![Main webapp screen](/docs/mainpage.png?raw=true "Main webapp screen")
Main screen: Select currently running tournaments and finished/current rounds.
![Logged in view](/docs/logged.png?raw=true "Logged in view")
After logging in as a referee you can score matches
![Admin main page](/docs/admin.png?raw=true "Admin main page")
Tweaked admin page 

TODOs
-----
- Tie breaking
- Use of authentication sessions (currently auth data is lost upon refreshing the whole page)
- Javascript tests and coverage
