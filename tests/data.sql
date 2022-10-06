INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:260000$xuN2qRLspcmX3DfW$bcc449e4db5b6280f292d03474552510f12929362f0dd378845e36362efa0a8d'),
    ('other', 'pbkdf2:sha256:260000$mOcgX1uWrl0fJLpU$20d56df60c714482e750ed06fcd07e89c06351d10e77ed368088ca85e3a12390');

INSERT INTO post (title, body, author_id, created)
VALUES
    ('test title', 'test' || x'0a' || 'body', 1, '2022-01-01 00:00:00'); -- tests behavior with line feed
