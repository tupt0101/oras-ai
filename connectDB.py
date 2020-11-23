import psycopg2

connection = None
cursor = None
try:
    connection = psycopg2.connect(user = "ornphnuodjuqxc",
                                  password = "027924e9378c409d321d057aaeab4b257031508694d3fc0ce6cad8fddc3d57b0",
                                  host = "ec2-54-84-98-18.compute-1.amazonaws.com",
                                  port = "5432",
                                  database = "db67ot35cl90oe")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
