CREATE DATABASE IF NOT EXISTS DB_NAME;
USE DB_NAME;
SET @@global.local_infile = 1;

SET @original_sql_mode = @@SESSION.sql_mode;

SET SESSION sql_mode = '';

CREATE TABLE IF NOT EXISTS video_axis (
    video_id varchar(255) NOT NULL,
    course_id varchar(255),
    name varchar(255),
    video_length INT,
    youtube_id varchar(255),
    index_chapter SMALLINT,
    index_video SMALLINT,
    category varchar(31),
    chapter_name varchar(255),
    PRIMARY KEY (video_id)
);

CREATE TABLE IF NOT EXISTS video_stats (
    video_id varchar(255) NOT NULL,
    name varchar(255),
    videos_viewed INT,
    videos_watched INT,
    index_chapter SMALLINT,
    index_video SMALLINT,
    chapter_name varchar(255),
    PRIMARY KEY (video_id)
);

CREATE TABLE IF NOT EXISTS video_stats_day (
    user_id varchar(255) NOT NULL,
    video_id varchar(255) NOT NULL,
    _date DATE,
    position FLOAT,
    PRIMARY KEY (user_id),
    INDEX (user_id, video_id, _date)
);

CREATE TABLE IF NOT EXISTS pc_day_totals (
    user_id varchar(255) NOT NULL,
    ndays_act INT,
    nevents INT,
    nvideo INT,
    ntranscript INT,
    nseek_video INT,
    npause_video INT,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS person_course_day (
    user_id varchar(255) NOT NULL,
    _date DATE NOT NULL,
    nvideo INT,
    nseek_video INT,
    nvideos_viewed INT,
    nvideos_watched_sec FLOAT,
    PRIMARY KEY (user_id),
    INDEX (user_id, _date)
);

CREATE TABLE IF NOT EXISTS person_course_video_watched (
    original_user_id varchar(255) NOT NULL,
    course_id varchar(255),
    n_unique_videos_watched INT,
    fract_total_videos_watched FLOAT,
    viewed BOOLEAN,
    certified BOOLEAN,
    verified BOOLEAN,
    PRIMARY KEY (original_user_id)
);

CREATE TABLE IF NOT EXISTS stats_activity_by_day (
    _date DATE NOT NULL,
    nevents INT,
    nvideo INT,
    ntranscript INT,
    nseek_video INT,
    npause_video INT,
    PRIMARY KEY (_date)
);

CREATE TABLE IF NOT EXISTS stats_overall (
    course_id varchar(255) NOT NULL,
    registered_sum INT,
    nregistered_active INT,
    n_unregistered INT,
    viewed_sum INT,
    explored_sum INT,
    certified_sum INT,
    n_male INT,
    n_female INT,
    n_verified_id INT,
    verified_viewed INT,
    verified_explored INT,
    verified_certified INT,
    verified_n_male INT,
    verified_n_female INT,
    nplay_video_sum INT,
    nchapters_avg FLOAT,
    ndays_act_sum INT,
    nevents_sum INT,
    nforum_posts_sum INT,
    min_start_time TIMESTAMP,
    max_last_event TIMESTAMP,
    max_nchapters INT,
    nforum_votes_sum INT,
    nforum_endorsed_sum INT,
    nforum_threads_sum INT,
    nforum_commments_sum INT,
    nforum_pinned_sum INT,
    nprogcheck_avg FLOAT,
    verified_nprogcheck FLOAT,
    nshow_answer_sum INT,
    nseq_goto_sum INT,
    npause_video_sum INT,
    avg_of_avg_dt FLOAT,
    avg_of_sum_dt FLOAT,
    n_have_ip INT,
    n_missing_cc INT,
    PRIMARY KEY (course_id)
);

CREATE TABLE IF NOT EXISTS time_on_task (
    user_id varchar(255) NOT NULL,
    _date DATE NOT NULL,
    total_time_5 FLOAT,
    total_time_30 FLOAT,
    total_video_time_5 FLOAT,
    total_video_time_30 FLOAT,
    serial_video_time_30 FLOAT,
    PRIMARY KEY (user_id),
    INDEX (user_id, _date)
);

CREATE TABLE IF NOT EXISTS time_on_task_totals (
    user_id varchar(255) NOT NULL,
    total_time_5 FLOAT,
    total_time_30 FLOAT,
    total_video_time_5 FLOAT,
    total_video_time_30 FLOAT,
    serial_video_time_30 FLOAT,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS user_info_combo (
    user_id varchar(255) NOT NULL,
    orignial_user_id varchar(255) NOT NULL,
    last_login TIMESTAMP,
    date_joined TIMESTAMP,
    enrollment_course_id varchar(255),
    enrollment_created TIMESTAMP,
    enrollment_is_active BOOLEAN,
    enrollment_mode varchar(31),
    PRIMARY KEY (user_id),
    INDEX (user_id, orignial_user_id)
);


LOAD DATA local INFILE 'MOOCDB_DIR/video_axis.csv'
IGNORE INTO TABLE video_axis
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/video_stats.csv'
IGNORE INTO TABLE video_stats
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/video_stats_day.csv'
IGNORE INTO TABLE video_stats_day
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/pc_day_totals.csv'
IGNORE INTO TABLE pc_day_totals
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/person_course_day.csv'
IGNORE INTO TABLE person_course_day
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/person_course_video_watched.csv'
IGNORE INTO TABLE person_course_video_watched
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/stats_activity_by_day.csv'
IGNORE INTO TABLE stats_activity_by_day
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/stats_overall.csv'
IGNORE INTO TABLE stats_overall
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/time_on_task.csv'
IGNORE INTO TABLE time_on_task
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/time_on_task_totals.csv'
IGNORE INTO TABLE time_on_task_totals
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

LOAD DATA local INFILE 'MOOCDB_DIR/user_info_combo.csv'
IGNORE INTO TABLE user_info_combo
FIELDS TERMINATED BY ',' ENCLOSED BY '"';

SET SESSION sql_mode = @original_sql_mode;