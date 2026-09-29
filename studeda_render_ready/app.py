
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sqlite3, json, os

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DB = ROOT / "studeda.db"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "10000"))

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS meals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        meal_date TEXT NOT NULL,
        meal_time TEXT NOT NULL,
        product_name TEXT NOT NULL,
        calories REAL DEFAULT 0,
        protein REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        carbs REAL DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS reminders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        title TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS catalog(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        kind TEXT NOT NULL,
        price TEXT,
        calories REAL DEFAULT 0,
        protein REAL DEFAULT 0,
        fat REAL DEFAULT 0,
        carbs REAL DEFAULT 0,
        prep_time TEXT,
        description TEXT,
        icon TEXT,
        tag TEXT
    )""")
    rows = [
      ("Овсянка","Продукт","≈ 55 ₽ / 500 г",366,12.3,6.1,59.5,"5–10 мин","Сложные углеводы, клетчатка и удобный завтрак на каждый день.","🥣","Бюджет"),
      ("Яйца","Продукт","≈ 120 ₽ / 10 шт",157,12.7,11.5,0.7,"7–10 мин","Недорогой источник белка и жиров. Можно варить, жарить или добавлять в блюда.","🥚","Белок"),
      ("Гречка","Продукт","≈ 90 ₽ / 800 г",313,12.6,3.3,62.1,"15–20 мин","Сытная крупа, которая долго хранится и хорошо подходит для студенческого рациона.","🌾","База"),
      ("Куриная грудка","Продукт","≈ 390 ₽ / кг",165,31,3.6,0,"20–30 мин","Постный источник белка для обеда и ужина.","🍗","Белок"),
      ("Творог 5%","Продукт","≈ 110 ₽ / 200 г",121,17.2,5,1.8,"0 мин","Белковый продукт для быстрого завтрака или вечернего перекуса.","🥛","Быстро"),
      ("Банан","Продукт","≈ 150 ₽ / кг",89,1.1,0.3,22.8,"0 мин","Быстрый источник углеводов, удобно брать с собой на учёбу.","🍌","Перекус"),
      ("Чечевица","Продукт","≈ 150 ₽ / 450 г",352,24.6,1.1,63.4,"20–25 мин","Доступный растительный белок и клетчатка.","🫘","Выгодно"),
      ("Замороженные овощи","Продукт","≈ 140 ₽ / 400 г",55,3,0.5,9,"10–12 мин","Помогают быстро добавить овощи к крупе или мясу.","🥦","Быстро"),
      ("Овсянка с бананом","Рецепт","≈ 45 ₽ / порция",420,14,12,62,"10 мин","1. Сварить овсянку на воде или молоке.\n2. Нарезать банан.\n3. Добавить банан и корицу.\n4. По желанию добавить немного орехов.","🍌","Завтрак"),
      ("Гречка с курицей","Рецепт","≈ 165 ₽ / порция",530,48,14,52,"25 мин","1. Отварить гречку.\n2. Приготовить курицу небольшими кусочками.\n3. Добавить овощи.\n4. Смешать и приправить.","🍗","Сытно"),
      ("Омлет с овощами","Рецепт","≈ 95 ₽ / порция",310,24,20,10,"12 мин","1. Взбить 3 яйца.\n2. Добавить овощи.\n3. Готовить под крышкой 7–9 минут.\n4. Добавить зелень.","🍳","Быстро"),
      ("Паста с тунцом","Рецепт","≈ 180 ₽ / порция",560,36,10,76,"15 мин","1. Отварить пасту.\n2. Добавить тунца.\n3. Смешать с томатами или овощами.\n4. Добавить специи.","🍝","Обед"),
      ("Творог с бананом","Рецепт","≈ 130 ₽ / порция",360,30,11,38,"3 мин","1. Выложить творог.\n2. Нарезать банан.\n3. Смешать.\n4. Добавить корицу или ложку йогурта.","🥣","3 минуты"),
      ("Чечевица с яйцом","Рецепт","≈ 110 ₽ / порция",510,31,16,58,"25 мин","1. Отварить чечевицу.\n2. Сварить два яйца.\n3. Добавить овощи и специи.\n4. Смешать.","🫘","Выгодно")
    ]
    cur.executemany("""INSERT OR IGNORE INTO catalog
      (name,kind,price,calories,protein,fat,carbs,prep_time,description,icon,tag)
      VALUES(?,?,?,?,?,?,?,?,?,?,?)""", rows)
    con.commit()
    con.close()

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except Exception:
            return {}

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path or "/"
        qs = parse_qs(p.query)

        if path.startswith("/api/"):
            return self.api_get(path, qs)

        if path != "/" and path.endswith("/"):
            path = path[:-1]

        routes = {
            "/": "index.html",
            "/index.html": "index.html",
            "/today": "index.html",
            "/plan": "plan.html",
            "/catalog": "catalog.html",
            "/reminders": "reminders.html",
        }
        fp = STATIC / (routes.get(path) or path.lstrip("/"))
        if not fp.exists() or fp.is_dir():
            if "." not in Path(path).name:
                fp = STATIC / "index.html"
            else:
                return self.send_error(404)

        ctype = {
            ".html":"text/html; charset=utf-8",
            ".css":"text/css; charset=utf-8",
            ".js":"application/javascript; charset=utf-8",
            ".svg":"image/svg+xml",
            ".png":"image/png",
            ".ico":"image/x-icon"
        }.get(fp.suffix.lower(), "application/octet-stream")
        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def api_get(self, path, qs):
        con = db()
        try:
            cid = qs.get("client_id", [""])[0]
            if path == "/api/meals":
                day = qs.get("date", [""])[0]
                rows = con.execute(
                    "SELECT * FROM meals WHERE client_id=? AND meal_date=? ORDER BY meal_time,id",
                    (cid, day)
                ).fetchall()
                return self.send_json([dict(x) for x in rows])

            if path == "/api/reminders":
                rows = con.execute(
                    "SELECT * FROM reminders WHERE client_id=? ORDER BY reminder_time,id", (cid,)
                ).fetchall()
                return self.send_json([dict(x) for x in rows])

            if path == "/api/catalog":
                kind = qs.get("kind", ["Все"])[0]
                q = qs.get("q", [""])[0].strip().lower()
                sql = "SELECT * FROM catalog WHERE 1=1"
                pars = []
                if kind in ("Продукт", "Рецепт"):
                    sql += " AND kind=?"
                    pars.append(kind)
                if q:
                    like = f"%{q}%"
                    sql += " AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)"
                    pars += [like, like]
                sql += " ORDER BY CASE kind WHEN 'Продукт' THEN 0 ELSE 1 END,name"
                rows = con.execute(sql, pars).fetchall()
                return self.send_json([dict(x) for x in rows])

            return self.send_json({"error":"not found"}, 404)
        finally:
            con.close()

    def do_POST(self):
        path = urlparse(self.path).path
        d = self.read_json()
        con = db()
        try:
            if path == "/api/meals":
                cid = str(d.get("client_id","")).strip()
                name = str(d.get("product_name","")).strip()
                if not cid or not d.get("meal_date") or not d.get("meal_time") or not name:
                    return self.send_json({"error":"Заполните название, дату и время"}, 400)
                cur = con.execute("""INSERT INTO meals
                    (client_id,meal_date,meal_time,product_name,calories,protein,fat,carbs)
                    VALUES(?,?,?,?,?,?,?,?)""", (
                    cid,d["meal_date"],d["meal_time"],name,
                    float(d.get("calories") or 0),float(d.get("protein") or 0),
                    float(d.get("fat") or 0),float(d.get("carbs") or 0)
                ))
                con.commit()
                return self.send_json({"ok":True,"id":cur.lastrowid},201)

            if path == "/api/reminders":
                cid = str(d.get("client_id","")).strip()
                title = str(d.get("title","")).strip()
                t = str(d.get("reminder_time","")).strip()
                if not cid or not title or not t:
                    return self.send_json({"error":"Заполните название и время"},400)
                cur = con.execute(
                    "INSERT INTO reminders(client_id,title,reminder_time,enabled) VALUES(?,?,?,1)",
                    (cid,title,t)
                )
                con.commit()
                return self.send_json({"ok":True,"id":cur.lastrowid},201)

            return self.send_json({"error":"not found"},404)
        finally:
            con.close()

    def do_PATCH(self):
        path = urlparse(self.path).path
        d = self.read_json()
        if not path.startswith("/api/reminders/"):
            return self.send_json({"error":"not found"},404)
        try:
            rid = int(path.rsplit("/",1)[1])
        except Exception:
            return self.send_json({"error":"bad id"},400)
        cid = str(d.get("client_id","")).strip()
        con = db()
        try:
            con.execute(
                "UPDATE reminders SET enabled=? WHERE id=? AND client_id=?",
                (1 if d.get("enabled") else 0,rid,cid)
            )
            con.commit()
            return self.send_json({"ok":True})
        finally:
            con.close()

    def do_DELETE(self):
        p = urlparse(self.path)
        path = p.path
        qs = parse_qs(p.query)
        cid = qs.get("client_id", [""])[0]
        con = db()
        try:
            if path.startswith("/api/meals/"):
                mid = int(path.rsplit("/",1)[1])
                con.execute("DELETE FROM meals WHERE id=? AND client_id=?", (mid,cid))
                con.commit()
                return self.send_json({"ok":True})
            if path.startswith("/api/reminders/"):
                rid = int(path.rsplit("/",1)[1])
                con.execute("DELETE FROM reminders WHERE id=? AND client_id=?", (rid,cid))
                con.commit()
                return self.send_json({"ok":True})
            return self.send_json({"error":"not found"},404)
        finally:
            con.close()

if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"СтудЕда запущена на {HOST}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
