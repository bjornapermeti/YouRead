CREATE TABLE `users` (
	`user_id`	VARCHAR(120) NOT NULL UNIQUE,
	`name`		VARCHAR(120),
	`email`		VARCHAR(120) NOT NULL UNIQUE,
	`pwd`		VARCHAR(120) NOT NULL,
	`is_admin`	BOOLEAN,
	PRIMARY KEY(`user_id`)
);
CREATE TABLE `books` (
	`id`	INTEGER NOT NULL UNIQUE,
	`book_id`	INTEGER NOT NULL UNIQUE,
	`goodreads_book_id`	INTEGER UNIQUE,
	`best_book_id`	INTEGER,
	`work_id`	INTEGER,
	`books_count`	INTEGER,
	`isbn`	INTEGER,
	`isbn13`	REAL,
	`authors`	TEXT,
	`original_publication_year`	REAL,
	`original_title`	TEXT,
	`title`	TEXT,
	`language_code`	TEXT,
	`average_rating`	REAL,
	`ratings_count`	INTEGER,
	`work_ratings_count`	INTEGER,
	`work_text_reviews_count`	INTEGER,
	`ratings_1`	INTEGER,
	`ratings_2`	INTEGER,
	`ratings_3`	INTEGER,
	`ratings_4`	INTEGER,
	`ratings_5`	INTEGER,
	`image_url`	TEXT,
	`small_image_url`	TEXT,
	PRIMARY KEY(`id`)
);
CREATE TABLE `ratings` (
	`id`:       INTEGER NOT NULL UNIQUE,
	`user_id`	INTEGER,
	`book_id`	INTEGER,
	`rating`	INTEGER
);
CREATE TABLE `book_tags` (
	`id`:       INTEGER NOT NULL UNIQUE,
	`goodreads_book_id`	INTEGER,
	`tag_id`	INTEGER,
	`tag_name`  VARCHAR(120)
	`count`	INTEGER
);
CREATE TABLE `user_books` (
	`id` INTEGER NOT NULL UNIQUE,
	`user_id` INTEGER,
	`book_id` INTEGER,
    `time` INTEGER,
	`reading_state` INTEGER
)
CREATE TABLE `similar_books` (
	`id` INTEGER NOT NULL UNIQUE,
	`goodreads_book_id` INTEGER,
	`sim_goodreads_book_id` INTEGER,
)
