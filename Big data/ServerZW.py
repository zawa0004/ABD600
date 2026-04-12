from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)  #创建一个叫 app 的网站对象

DB_PATH = "bigdata.db"  # 告诉程序，我们的数据库文件叫这个名字


# ─────────────────────────────────────────────
# Database connection helper
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)  # 打开那个叫 bigdata.db 的账本
    conn.row_factory = sqlite3.Row    # 赋予变量
    return conn                        #传递变量


# ─────────────────────────────────────────────
# R2: Receive AGV data from TwinCAT (POST)
# Saves timestamp, battery, and location
# TwinCAT sends: { "Position": "A", "Battery": 85, "TimeStamp": "2026-03-11 10:00:00" }
# ─────────────────────────────────────────────
@app.route("/post_data", methods=["POST"])   #localhost>5000/post_data
def post_data():                            

    data = request.get_json()                  #json格式打开agv的包裹

    print("Data received from TwinCAT:", data)  #打印

    position  = data.get("Position")     
    battery   = data.get("Battery")
    timestamp = data.get("TimeStamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()                 

    # Save to battery_status table (R2 requirement: timestamp, battery, location)
    conn.execute(
        """
        INSERT INTO battery_status (Measurement_Time, Location, Battery)
        VALUES (?, ?, ?)
        """,  #写输入 包括三个信息 时间，位置，电量
        (timestamp, position, battery)
    )

    conn.commit()  #确认
    conn.close()   #关闭

    print(f"  >> Saved to DB: Location={position}, Battery={battery}%, Time={timestamp}")

    return jsonify({
        "message": "AGV data saved",
        "location": position,
        "battery": battery,
        "timestamp": timestamp
    }), 200      #返回 存好的信息


# ─────────────────────────────────────────────
# R4: Check safety for ONE location
# Example: GET /get_safety/A
# ─────────────────────────────────────────────
@app.route("/get_safety/<location>", methods=["GET"])   #在get safety目录下用get 方法
def get_safety(location):

    conn = get_db()    #连上数据库

    rows = conn.execute(
        """
        SELECT Damaged
        FROM environmental_conditions  
        WHERE LOWER(Location) = ?
        ORDER BY Record_ID DESC
        LIMIT 10
        """,
        (location.lower(),) #从数据库里查找最近10次记录，
    ).fetchall()    #location 转换为小写，按从小到大排列，只有一个元素的元组， fech， all 

    conn.close()  #关上变量  

    if not rows:
        # 无数据按不安全处理
        return jsonify({
            "location": location.upper(),
            "safe": False,
            "reason": "No data available"
        })

    damage_count = sum(1 for row in rows if row["Damaged"] == 1)  #把damage 数量汇总
    is_safe = damage_count == 0 # 为零就是安全

    print(f"Safety check [{location.upper()}]: {'SAFE' if is_safe else 'UNSAFE'} "
          f"({damage_count} damage(s) in last {len(rows)} records)")
    
    return jsonify({
        
         "safe": "true" if is_safe else "false",
        
    })


# ─────────────────────────────────────────────
# R4: Safety status for ALL locations
# Example: GET /safety
# ─────────────────────────────────────────────
@app.route("/safety", methods=["GET"])
def safety():

    conn = get_db()
    cursor = conn.cursor()

    locations = ["A", "B", "C", "D"]
    result = {}

    for loc in locations:

        cursor.execute(
            """
            SELECT Damaged
            FROM environmental_conditions
            WHERE LOWER(Location) = ?
            ORDER BY Record_ID DESC
            LIMIT 10
            """,
            (loc.lower(),)
        )

        records = cursor.fetchall()
        damage_count = sum(1 for r in records if r[0] == 1)
        is_safe = (damage_count == 0) and (len(records) > 0)

        result[loc] = {
            "status": "SAFE" if is_safe else "UNSAFE",
            "damage_count": damage_count,
            "records_checked": len(records)
        }

    conn.close()

    print("Safety status for all locations:", result)
    return jsonify(result)


# ─────────────────────────────────────────────
# View last 10 AGV stops (battery_status table)
# Example: GET /agv_log
# ─────────────────────────────────────────────
@app.route("/agv_log", methods=["GET"])
def agv_log():

    conn = get_db()
    rows = conn.execute(
        """
        SELECT Record_ID, Measurement_Time, Location, Battery
        FROM battery_status
        ORDER BY Record_ID DESC
        LIMIT 10
        """
    ).fetchall()
    conn.close()

    log = [dict(row) for row in rows]
    return jsonify(log)   #  check db。py 时候用的查找最后10个记录


# ─────────────────────────────────────────────
# Example GET variable endpoint (lab requirement)
# ─────────────────────────────────────────────
variables = {
    "example_var1": "Hello, World!",
    "example_var2": "1234",
    "example_var3": [1, 2, 3, 4, 5]
}   #定义字典

@app.route("/get_variable/<var_name>", methods=["GET"])   #占位符
def get_variable(var_name):

    if var_name in variables:
        return jsonify({var_name: variables[var_name]})  #有这个占位符，打包成json发回去 
    else:
        return jsonify({"message": "Variable not found"}), 404  #没有，返回404


# ─────────────────────────────────────────────
# Start Flask server
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)   #0.0.0.0 任何涉笔都可以访问。 
    
    
