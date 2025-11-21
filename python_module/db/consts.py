

SQL_TABLE_CREATE = {'rooms':"""
                create table rooms (
                        id serial primary key, 
                        name varchar
                        );""",
                    'students': """create table students (
                        birthday timestamp,
                        id serial primary key,
                        name varchar,
                        room serial references rooms(id) ON DELETE CASCADE ON UPDATE CASCADE,
                        sex char(1),
                        check (sex in ('F', 'M'))
                        );
                        create index r_number ON students (room);
                        create index birthday ON students (birthday);"""
                    }

"""
sql_1 = 'select room, count(*) as students_count from students group by room order by students_count desc'
sql_2 = 'select room, cast(avg(extract (year from age(now(), birthday))) as int) as avg_age from students group by room order by avg_age limit 5;'
sql_3 = "select room, cast(max(extract (year from age(now(), birthday))) - 
					min(extract (year from age(now(), birthday))) as int) as difference 
					from students group by room order by difference desc limit 5;"
sql_4 = 'select room from students group by room having count(distinct sex) > 1;'
"""

PREDEFINED_SELECT_SQL_QUERIES = {"task_1": """select room, count(*) as students_count 
                                 from students group by room order by students_count desc""",
                                 "task_2": """select room, cast(avg(extract (year from age(now(), birthday))) as int) as avg_age 
                                 from students group by room order by avg_age limit 5;""",
                                 "task_3": """select room, cast(max(extract (year from age(now(), birthday))) - 
					             min(extract (year from age(now(), birthday))) as int) as difference 
					             from students group by room order by difference desc limit 5""",
                                 "task_4": """select room from students group by room having count(distinct sex) > 1;"""}