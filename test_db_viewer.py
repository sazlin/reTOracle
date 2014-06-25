if __name__ == "__main__":
    import psycopg2
    from secrets import SECRETS
    try:
        connection_string = []
        connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
        connection_string.append("dbname=rhetorical-db")
        connection_string.append("user=" + SECRETS['DB_USERNAME'])
        connection_string.append("password=" + SECRETS['DB_PASSWORD'])
        conn = psycopg2.connect(" ".join(connection_string))
    except Exception as x:
        print "Error connecting to DB: ", x.args

    cur = conn.cursor()
    try:
        cur.execute("""SELECT * from massive""")
    except:
        print "Error selecting from massive"

    rows = cur.fetchall()
    for row in rows:
        print "========================="
        print "Tweet ID: {}".format(row[0])
        print "Hashtags: {}".format(row[2])
        print "Mentions: {}".format(row[3])
        print "URL: {}".format(row[4])
        print "Location: {}".format(row[5])
        print "Retweets: {}".format(row[7])
    print "========================="
