import json

from utils.code import StudentsDatabase

interface = StudentsDatabase('postgresql.yaml')
interface.load_rooms('data/rooms.json')
interface.load_students('data/students.json')

sql_1 = 'select room, count(*) as students_count from students group by room order by students_count desc'
sql_2 = 'select room, cast(avg(extract (year from age(now(), birthday))) as int) as avg_age from students group by room order by avg_age limit 5;'
sql_3 = """select room, cast(max(extract (year from age(now(), birthday))) - 
					min(extract (year from age(now(), birthday))) as int) as difference 
					from students group by room order by difference desc limit 5;"""
sql_4 = 'select room from students group by room having count(distinct sex) > 1;'
result_1 = interface.select_query(sql_1, 'result1.json')
result_2 = interface.select_query(sql_2, 'result2.json')
result_3 = interface.select_query(sql_3, 'result3.json')
result_4 = interface.select_query(sql_4, 'result4.json')