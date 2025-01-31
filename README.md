# Flask blog

This is a microblogging platform I'm creating both to learn Flask, Python,
web development in general, and also have some place where to write down stuff
regardless which device I'm using, with the specific functionalities I need.

## Phase 1 - Official Flask tutorial

The initial version of this blog was pretty much identical to the original
Flask [tutorial].

[tutorial]: https://flask.palletsprojects.com/en/2.2.x/tutorial/

## Phase 2 - Imitating Learning Log

This is the main development phase. Instead of just following the tutorial,
I expanded the initial blog to be the functional equivalent of the app
Learning Log, developed for _Python Crash Course, 2nd Edition_ by Eric
Matthes. Since Learning Log relies on Django, this means implementing several
additional features, major ones through extensions:

- [x] More modern look and responsive design with transition to **Bootstrap 5**
- [x] Object-relational mapping with **Flask-SQLAlchemy**, for easier and more
      sustainable handling of underlying database models
- [ ] ~~Server-side session management with **Flask-Session**~~  
       (after some research I decided to not switch, since I couldn't find a [good
      reason](https://stackoverflow.com/questions/3948975/why-store-sessions-on-the-server-instead-of-inside-a-cookie)
      to do so, considering both current state and plans for this blog.)
- [x] Administrator dashboard for easier tracking and managing of users,
      topics, and posts with **Flask-Admin**
- [x] Faster RDBMS (which also matches the database on the hosting platform), with **PyMySQL**

## Phase 3 - My own blog

The phase after the actual depoloyment.
Here I should add any missing essential features for the microblogging I want to do,
and then possibly expand further for learning or fun, if I have time.
Most significant single source of inspiration (and technical implementation) is
_Flask Web Development, 2nd Edition_ by Miguel Grinberg.

Besides updating site structure and altering the visual appearance, some noteable
changes are:

- [x] Localization of date and time with **Flask-Moment**
- [x] Handling database changes with **Flask-Migrate**
- [x] Transitioning to more secure and convenient forms with **Flask-WTF**
- [x] Rich text editing for posts with **Flask-PageDown**
- [ ] Improved visual appearance with **Bootswatch** theme
- [ ] Toggling between light and dark themes
- [ ] Additional password security with **zxcvbn**
- [ ] Add image support

---

## Running

To run the app locally, in debug mode:

```bash
flask --app dailypush --debug run
```

### Testing

For `pytest` to successfully recognize `dailypush` as a module, install the project:

```bash
pip install -e .
```

Alternatively, invoke pytest through Python interpreter (effectively adding the current directory to `sys.path`):

```bash
python -m pytest
```

## Live version

The app currently lives at [dailypush.pythonanywhere.com](https://dailypush.pythonanywhere.com)
