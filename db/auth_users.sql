CREATE TABLE users(
  id serial primary key,
  name text not null,
  surname text not null,
  username varchar(32) unique not null,
  password text not null,
  profile varchar(32),
  email varchar(64) unique not null
);

CREATE TABLE users_tokens(
  user_id integer not null REFERENCES users(id),
  token text not null,
  expiration timestamp not null,
  PRIMARY KEY (user_id,token)
);
