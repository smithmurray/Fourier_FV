import pymssql

host = "41.203.23.36"
username = "FE-User"
password = "Fourier.01"
database = "PGAluminium"

conn = pymssql.connect(host, username, password, database)
cursor = conn.cursor()

cursor.execute(
    """
    insert into UserRoles (UserId, RoleId)
    values
    (1,1),
    (2,1),
    (3,1),
    (4,1),
    (5,1),
    (6,1),
    (7,1),
    (8,1),
    (9,1),
    (10,1),
    (11,1),
    (12,1),
    (13,1),
    (14,1),
    (15,1),
    (16,1),
    (17,1),
    (18,1),
    (19,1),
    (20,1),
    (21,1),
    (22,1),
    (23,1),
    (24,1),
    (25,1),
    (26,1),
    (27,1),
    (28,1),
    (29,1),
    (30,2),
    (31,2),
    (32,2),
    (33,2),
    (34,2),
    (35,2),
    (36,2),
    (37,3),
    (38,4),
    (39,4),
    (40,4)
    """)

conn.commit()

conn.close()

