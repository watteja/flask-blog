# Flask blog

This is a blog I'm creating both to learn Flask, Python, web development in
general, and also have some place where to write down stuff regardless which
device I'm using, with the specific functionalities I need.

## Phase 1 - Official Flask tutorial

The initial version of this blog was pretty much identical to the original
Flask [tutorial].

[tutorial]: <https://flask.palletsprojects.com/en/2.2.x/tutorial/>

## Phase 2 - Imitating Learning Log

This is the main development phase. Instead of just following the tutorial,
I expanded the initial blog to be the functional equivalent of the app
Learning Log, developed for _Python Crash Course, 2nd Edition_ by Eric
Matthes. Since Learning Log relies on Django, this means implementing several
additional features, major ones through extensions:

- [x] More modern look and responsive design with transition to __Bootstrap 5__
- [x] Object-relational mapping with __Flask-SQLAlchemy__, for easier and more
sustainable handling of underlying database models
- [ ] ~~Server-side session management with __Flask-Session__~~  
(after some research I decided to not switch, since I couldn't find a [good
reason](https://stackoverflow.com/questions/3948975/why-store-sessions-on-the-server-instead-of-inside-a-cookie)
to do so, considering both current state and plans for this blog.)
- [x] Administrator dashboard for easier tracking and managing of users,
topics, and posts with __Flask-Admin__

## Phase 3 - My own blog

The phase during which the actual depoloyment will take place.
Here I should add any missing essential features for the
microblogging I want to do, and then possibly expand further
for learning or fun, if I have time.

---

## Running

To run the app locally, in debug mode:

```bash
flask --app flaskr --debug run
```
