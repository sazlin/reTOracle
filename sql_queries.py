from filters_json import filter_list


def build_q1_querystring():
    """build a query string for Q1 using filter_list"""
    sql = []
    sql.append("""SELECT hashtag, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery""")
    sql.append("""WHERE""")
    for language in filter_list:
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            sql.append("""hashtag = '""" + hashtag[1:] + """'""")
            sql.append("""OR""")
    sql.pop()  # discard last OR statement
    sql.append("""GROUP BY hashtag""")
    sql.append("""ORDER BY HashTagCount DESC""")
    return " \r\n".join(sql)


def build_q2_querystring():
    """build a query string for Q2 using filter_list"""
    sql = []
    sql.append("""SELECT hashtag, HashTagCount, screen_name""")
    sql.append("""FROM (SELECT hashtag, screen_name, HashTagCount, rank() OVER (PARTITION BY hashtag ORDER BY HashTagCount DESC, screen_name) AS pos""")
    sql.append("""FROM (SELECT hashtag, screen_name, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as unwrap""")
    sql.append("""WHERE""")
    for language in filter_list:
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            sql.append("""hashtag = '""" + hashtag[1:] + """'""")
            sql.append("""OR""")
    sql.pop()  # discard last OR statement
    sql.append("""GROUP BY screen_name, hashtag""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    sql.append(""") as countedhashtags""")
    sql.append(""") as ss""")
    sql.append("""WHERE pos = 1""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    return " \r\n".join(sql)


def build_q3_querystring():
    sql = """
    SELECT screen_name, text FROM massive
    ORDER BY tweet_id DESC
    LIMIT 1;
    """
    return sql
