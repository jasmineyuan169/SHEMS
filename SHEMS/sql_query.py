import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '010401Jasmine',
    'database': 'SHEMS',
}

def execute_sql_query(sql_query, params=None):
    conn = None
    cursor = None

    try:
        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute MySQL Query
        if params:
            cursor.execute(sql_query, params)
        else:
            cursor.execute(sql_query)

        # Check if there is any result set
        if cursor.description:
            # Obtain query results
            results = cursor.fetchall()
        else:
            results = None

        # Commit Changes
        conn.commit()

        return results
    except Exception as e:
        print(f"Error executing SQL query: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

