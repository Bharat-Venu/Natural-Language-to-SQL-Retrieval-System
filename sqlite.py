import sqlite3

connection=sqlite3.connect("student.db")

cursor=connection.cursor()

table_info='''
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT)
'''

cursor.execute(table_info)

cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES ('John Doe', 'data science', 'A', 85)")
cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES ('Jane Smith', 'data science', 'B', 90)")
cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES ('Alice Johnson', 'DEVOPS', 'A', 95)")
cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES ('Bob Brown', 'DEVOPS', 'B', 80)")
cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES ('Charlie Davis', 'AI', 'A', 50)")


data=cursor.execute(''' select * from STUDENT''')

for row in data:
  print(row)


connection.commit()
connection.close()
