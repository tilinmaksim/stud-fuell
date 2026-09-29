from __future__ import annotations

import html
import itertools
import json
import math
import os
import sqlite3
import threading
import webbrowser
from collections import defaultdict
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_food.db"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MEAL_LABELS = {"breakfast": "Завтрак", "lunch": "Обед", "dinner": "Ужин", "snack": "Перекус"}

CSS = r'''
:root{--bg:#f3f6fb;--surface:#fff;--text:#172033;--muted:#69758c;--primary:#5578c7;--primary2:#6d8ed7;--soft:#e8eefb;--line:#e4e9f2;--success:#2f9d72;--shadow:0 12px 35px rgba(41,58,95,.08);--radius:22px}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}a{color:var(--primary);text-decoration:none}.app-shell{display:flex;min-height:100vh}.sidebar{position:fixed;left:0;top:0;bottom:0;width:250px;background:#17233d;color:#fff;padding:24px 16px;display:flex;flex-direction:column;z-index:10}.brand{display:flex;align-items:center;gap:12px;color:#fff;padding:0 10px 24px}.brand-mark{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#6f92e1,#9bb5ef);font-size:22px;font-weight:800}.brand b{display:block;font-size:19px}.brand small{display:block;color:#93a2bf;margin-top:2px}.sidebar nav{display:grid;gap:4px}.nav-link{color:#b9c6de;display:flex;gap:12px;align-items:center;padding:11px 12px;border-radius:13px;font-weight:600;font-size:14px}.nav-link:hover,.nav-link.active{background:#253555;color:#fff}.sidebar-bottom{margin-top:auto;display:grid;gap:4px}.content{margin-left:250px;padding:28px 34px 18px;width:calc(100% - 250px);max-width:1500px}.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px;gap:20px}.topbar h1{margin:2px 0 0;font-size:30px}.eyebrow{font-size:11px;letter-spacing:.12em;font-weight:800;color:#7890bb}.mobile-menu{display:none;border:0;background:#fff;border-radius:10px;padding:10px}.hero{background:linear-gradient(135deg,#21345d 0%,#5478c7 65%,#7e9bda 100%);border-radius:28px;color:#fff;padding:34px;display:flex;justify-content:space-between;align-items:center;box-shadow:var(--shadow);margin-bottom:20px;overflow:hidden;position:relative}.hero:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;right:-70px;top:-90px;background:rgba(255,255,255,.08)}.hero h2{font-size:31px;line-height:1.15;max-width:720px;margin:12px 0}.hero p{color:#e8eeff;max-width:720px;font-size:16px}.hero-actions{display:flex;gap:10px;margin-top:20px}.hero-score{position:relative;z-index:1;text-align:center}.ring{width:150px;height:150px;border-radius:50%;border:13px solid rgba(255,255,255,.2);border-top-color:#fff;display:grid;place-content:center}.ring b{font-size:28px}.ring span{font-size:12px}.pill,.tag{display:inline-flex;background:#edf2ff;color:#4e70bd;border-radius:999px;padding:7px 11px;font-size:12px;font-weight:800}.hero .pill{background:rgba(255,255,255,.16);color:#fff}.btn{border:0;border-radius:12px;padding:11px 15px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:7px}.btn.primary{background:var(--primary);color:#fff}.hero .btn.primary{background:#fff;color:#345cae}.btn.soft{background:var(--soft);color:#496bb5}.btn.ghost{background:#fff;color:#425e9d;border:1px solid var(--line)}.btn.tiny{padding:8px 10px;font-size:12px}.metrics-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}.metrics-grid.three{grid-template-columns:repeat(3,1fr)}.metric{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 7px 24px rgba(55,72,105,.04)}.metric span,.metric small{display:block;color:var(--muted);font-size:12px}.metric b{font-size:23px;display:block;margin:5px 0}.two-col{display:grid;grid-template-columns:1.35fr 1fr;gap:18px;margin-bottom:18px}.three-col{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:18px}.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow)}.card h2,.card h3{margin-top:7px}.section-head,.intro-row,.day-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:16px}.section-head h3,.intro-row h2,.day-head h3{margin:4px 0}.intro-row>div{max-width:760px}.intro-row p{color:var(--muted)}.meal-list{display:grid;gap:10px}.meal-row{display:flex;align-items:center;gap:13px;padding:12px;border-radius:15px;background:#f8faff;border:1px solid #edf1f8}.meal-icon{min-width:48px;height:42px;border-radius:12px;background:#e8eefb;display:grid;place-items:center;color:#4e70bd;font-size:14px;font-weight:800}.grow{flex:1}.meal-row b,.meal-row small{display:block}.meal-row small{color:var(--muted);margin-top:4px}.macro{text-align:right}.timeline{display:grid;gap:10px}.timeline-row{display:flex;gap:16px;padding:12px 0;border-bottom:1px solid var(--line)}.timeline-row b{color:#526fae}.callout{background:#f1f5ff;border-left:4px solid #6c89ca;padding:14px 16px;border-radius:12px;color:#4b5f85;font-size:14px;margin-top:15px}.shopping-mini,.reminder-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}.cost-note{margin-top:16px;padding:16px;border-radius:15px;background:#f7f9fd}.cost-note span,.cost-note small{display:block;color:var(--muted)}.cost-note b{display:block;font-size:26px;margin:4px 0}.accent-card{background:linear-gradient(145deg,#f6f8ff,#edf2ff)}.accent-card p{color:#5f6f8e;line-height:1.55}.inline-form,.filterbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.inline-form input,.inline-form select,.filterbar input,.filterbar select,input,select{border:1px solid #dbe2ee;background:#fff;border-radius:11px;padding:10px 12px;font:inherit;color:var(--text)}.premium-banner{background:#fff7df;border:1px solid #f1dfa4;border-radius:14px;padding:13px 16px;margin-bottom:16px}.day-card{margin-bottom:18px}.day-stats{display:flex;gap:10px;flex-wrap:wrap}.day-stats span{background:#f3f6fb;padding:8px 11px;border-radius:10px;font-size:13px}.plan-grid,.recipe-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.recipe-plan,.recipe-card{border:1px solid var(--line);background:#fbfcff;border-radius:16px;padding:16px}.recipe-top{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:12px}.recipe-plan h4,.recipe-card h3{margin:12px 0 6px}.recipe-plan p,.recipe-card p{font-size:13px;color:var(--muted);min-height:38px}.nutri{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}.nutri span{font-size:12px;background:#edf2fb;padding:6px 8px;border-radius:8px}.recipe-plan details,.recipe-card details{font-size:13px;color:#526079;margin:10px 0}.details-body{padding:10px 0}.table-card{overflow:auto}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:13px;border-bottom:1px solid var(--line);white-space:nowrap}th{font-size:12px;color:var(--muted);background:#f8faff}.need{color:#b86a35;font-weight:800}.ok{color:var(--success);font-weight:800}.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.quick-card button{width:100%;height:100%;text-align:left;background:#f8faff;border:1px solid var(--line);border-radius:14px;padding:12px;cursor:pointer}.quick-card b,.quick-card span{display:block}.quick-card span{color:var(--muted);font-size:12px;margin-top:4px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.form-grid label{display:grid;gap:6px;color:#56647e;font-size:13px;font-weight:700}.form-grid input,.form-grid select{width:100%}.wide{grid-column:1/-1}.icon-btn{border:0;background:#eef2f8;color:#7c879a;width:29px;height:29px;border-radius:9px;cursor:pointer}.schedule-day{display:grid;grid-template-columns:50px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}.schedule-chip{display:inline-flex;align-items:center;gap:5px;background:#edf2fb;padding:6px 9px;border-radius:9px;margin:2px;font-size:12px}.schedule-chip form{display:inline}.schedule-chip button{border:0;background:transparent}.weekday-checks{display:flex;gap:8px;flex-wrap:wrap}.weekday-checks label{display:flex;align-items:center;gap:5px;background:#f4f7fb;padding:8px 10px;border-radius:9px}.actions{display:flex;align-items:center;gap:6px}.reminder-row small{display:block;color:var(--muted)}.bar-list{display:grid;gap:18px}.bar-label{display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px}.progress{height:8px;background:#edf1f7;border-radius:999px;overflow:hidden;margin:5px 0}.progress i{height:100%;display:block;background:#5d7fc9;border-radius:999px}.progress.protein i{background:#61a980}.feature-list{line-height:1.8;color:#526079}.empty{padding:22px;text-align:center;border:1px dashed #ccd5e4;border-radius:14px;color:var(--muted)}.flash{padding:12px 15px;border-radius:13px;margin-bottom:14px;background:#e7f6ef;color:#31775c;border:1px solid #ccebdc}.simple{min-height:230px}.simple h2{max-width:900px}footer{color:#8b95a7;font-size:11px;text-align:center;padding:22px}.filterbar{background:#fff;border:1px solid var(--line);padding:13px;border-radius:16px;margin-bottom:16px}.filterbar input:first-child{flex:1;min-width:250px}.danger{color:#b15d5d}.center{text-align:center}
@media(max-width:1100px){.plan-grid,.recipe-grid{grid-template-columns:repeat(2,1fr)}.metrics-grid{grid-template-columns:repeat(2,1fr)}.three-col{grid-template-columns:1fr}.two-col{grid-template-columns:1fr}}@media(max-width:760px){.sidebar{transform:translateX(-105%);transition:.2s}.sidebar.open{transform:none}.content{margin-left:0;width:100%;padding:18px}.mobile-menu{display:block}.topbar{align-items:flex-start}.topbar h1{font-size:24px}.topbar .stress{display:none}.hero{padding:24px}.hero-score{display:none}.hero h2{font-size:25px}.metrics-grid,.metrics-grid.three,.plan-grid,.recipe-grid,.quick-grid{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}.wide{grid-column:auto}.day-head,.intro-row,.section-head{align-items:flex-start;flex-direction:column}.table-card{padding:0}.three-col{grid-template-columns:1fr}}
'''


def esc(x):
    return html.escape(str(x), quote=True)

VERTICAL_CSS = r'''
:root{--bg:#f5f6fb;--surface:#ffffff;--text:#1b2236;--muted:#6f7990;--primary:#6c79ff;--primary2:#ff79b9;--soft:#eef1ff;--line:#e7e9f3;--success:#35a06d;--shadow:0 18px 42px rgba(55,66,110,.12);--radius:26px}
body{background:linear-gradient(180deg,#f9fbff 0%,#f4f5fa 55%,#f7f8fd 100%);font-size:17px;color:var(--text)}
.app-shell{display:block;max-width:560px;margin:0 auto;background:transparent}
.sidebar{display:none}
.app-header{position:sticky;top:0;z-index:50;min-height:80px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;background:rgba(250,251,255,.94);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-bottom:1px solid rgba(226,230,243,.92)}
.brand{display:flex;align-items:center;gap:12px;color:var(--text);padding:0}.brand-mark{width:46px;height:46px;border-radius:17px;display:grid;place-items:center;color:#fff;background:linear-gradient(145deg,#7183ff,#89a3ff);box-shadow:0 12px 28px rgba(102,118,255,.30);font-weight:900;font-size:20px}.brand b{display:block;font-size:20px;line-height:1.05}.brand small{display:block;color:var(--muted);font-size:11px;margin-top:4px}
.nav-menu{position:relative}.nav-menu>summary{list-style:none;width:46px;height:46px;border-radius:17px;display:grid;place-items:center;cursor:pointer;font-size:22px;color:#435b8c;background:#fff;border:1px solid var(--line);box-shadow:0 10px 24px rgba(52,70,110,.08)}.nav-menu>summary::-webkit-details-marker{display:none}.nav-menu[open]>summary{background:#eef2ff;color:var(--primary)}
.nav-sheet{position:absolute;top:55px;right:0;width:300px;max-height:72vh;overflow:auto;background:rgba(255,255,255,.99);border:1px solid var(--line);border-radius:24px;padding:12px;box-shadow:0 28px 65px rgba(31,46,81,.22)}.nav-sheet-title{padding:8px 10px 8px;color:var(--muted);font-size:11px;font-weight:900;letter-spacing:.12em}.nav-list{display:grid;gap:6px}.nav-link{color:#4e5f7d;display:flex;gap:12px;align-items:center;padding:12px 13px;border-radius:16px;font-weight:800;font-size:14px}.nav-link .nav-ico{width:30px;height:30px;border-radius:10px;background:#f4f6fb;display:grid;place-items:center}.nav-link:hover,.nav-link.active{background:#eef2ff;color:#4e68dd}.nav-link.active .nav-ico{background:#dfe6ff}
.content{margin-left:0;width:100%;max-width:none;padding:18px 16px 112px}.topbar{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin:4px 2px 18px}.topbar h1{margin:4px 0 0;font-size:36px;line-height:1.02;letter-spacing:-.03em}.topbar .stress .btn{padding:11px 12px;font-size:13px;white-space:nowrap;font-weight:900}.eyebrow{font-size:10px;letter-spacing:.16em;color:#8b93a8}
.hero{display:flex;flex-direction:column;align-items:center;text-align:center;padding:28px 22px 24px;border-radius:32px;margin-bottom:16px;background:linear-gradient(180deg,#ffffff 0%,#fbfcff 100%);border:1px solid #eceef6;box-shadow:0 18px 40px rgba(63,79,125,.10)}.hero:before,.hero:after{display:none}.hero h2{font-size:37px;line-height:1.02;max-width:none;margin:10px 0 12px;letter-spacing:-.04em;color:#171b2e}.hero p{font-size:16px;line-height:1.55;margin:0;color:#616c84;max-width:420px}.hero-actions{display:grid;grid-template-columns:1fr;gap:10px;margin-top:18px;width:100%}.hero .btn{width:100%;min-height:52px;font-size:16px}.hero .btn.primary{background:#171b2e;color:#fff;box-shadow:0 10px 24px rgba(23,27,46,.18)}.hero .btn.soft{background:#f0f3ff;color:#586cdf}.hero-score{display:flex;justify-content:center;align-items:center;margin-top:22px}
.ring{position:relative;width:230px;height:230px;border-radius:50%;display:grid;place-content:center;background:conic-gradient(#8b82ff 0 45%, #ff83bf 45% 75%, #ffc29a 75% 100%);box-shadow:0 18px 35px rgba(137,131,255,.25)}.ring::before{content:"";position:absolute;inset:22px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 1px #eceef6}.ring b,.ring span{position:relative;z-index:1;text-align:center}.ring b{font-size:54px;line-height:1;font-weight:900;letter-spacing:-.04em}.ring span{font-size:14px;color:#828aa0;margin-top:4px}
.pill,.tag{padding:7px 12px;font-size:12px;border-radius:999px}.hero .pill{background:#f2f4ff;color:#6779e8;font-weight:900}.btn{border-radius:18px;padding:12px 16px;transition:.18s transform,.18s box-shadow;font-size:15px}.btn:active{transform:scale(.98)}.btn.primary{background:linear-gradient(135deg,#6474ff,#8e8cff);box-shadow:0 10px 26px rgba(92,104,255,.22)}.btn.soft{background:#eef1ff;color:#5b70dc}.btn.ghost{background:#fff;color:#546084;border:1px solid #e5e8f2}.btn.tiny{padding:10px 12px;font-size:13px;border-radius:14px}
.metrics-grid,.metrics-grid.three{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}.metric{border:1px solid rgba(227,231,243,.95);border-radius:22px;padding:18px 16px;box-shadow:0 10px 28px rgba(60,76,113,.055);background:linear-gradient(180deg,#fff 0%,#fbfcff 100%)}.metric span,.metric small{font-size:12px;color:#7c869d;line-height:1.35}.metric b{font-size:28px;margin:7px 0 3px;line-height:1.05;letter-spacing:-.03em}
.two-col,.three-col,.plan-grid,.recipe-grid,.quick-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-bottom:14px}.card{border-radius:28px;padding:20px;background:#fff;box-shadow:0 12px 30px rgba(58,74,111,.06);border:1px solid #eceef6;margin-bottom:14px}.card h2{font-size:29px;line-height:1.08;margin:6px 0 0;letter-spacing:-.03em}.card h3{font-size:23px;line-height:1.12;margin:6px 0 0;letter-spacing:-.025em}.section-head,.intro-row,.day-head{align-items:flex-start;flex-direction:column;gap:10px;margin-bottom:16px}
.intro-row{padding:20px;border-radius:26px;background:linear-gradient(180deg,#fff 0%,#fbfcff 100%);border:1px solid var(--line);margin-bottom:14px}.intro-row h2{font-size:28px;line-height:1.08;margin:0;letter-spacing:-.03em}.intro-row p{font-size:15px;line-height:1.6;margin:9px 0 0;color:#636d84}.intro-row .inline-form,.intro-row>a.btn{width:100%}.inline-form{display:grid;grid-template-columns:1fr 1fr;width:100%;gap:10px}.inline-form .btn{grid-column:1/-1}
.meal-row{gap:12px;padding:14px;border-radius:20px;background:linear-gradient(180deg,#fbfcff 0%,#f8f9fd 100%);border:1px solid #edf0f8}.meal-icon{min-width:48px;width:48px;height:48px;border-radius:16px;background:#eef2ff;color:#5e73dd;font-size:16px;font-weight:900}.meal-row b{font-size:15px;line-height:1.35}.meal-row small{font-size:12px;line-height:1.4;color:#717b92}.macro b{font-size:18px}.macro small{font-size:11px;color:#8b93a8}
.timeline-row{padding:14px 0}.timeline-row b{font-size:14px}.timeline-row span{font-size:14px;color:#5d6984}.recipe-plan,.recipe-card{border-radius:22px;padding:18px;background:linear-gradient(180deg,#fff 0%,#fafbff 100%);box-shadow:0 8px 22px rgba(50,68,106,.045);border:1px solid #edf0f7}.recipe-top{font-size:13px}.recipe-plan h4,.recipe-card h3{font-size:22px;line-height:1.14;margin:12px 0 8px;letter-spacing:-.025em}.recipe-plan p,.recipe-card p{font-size:14px;color:#68738b;line-height:1.5;min-height:0}.nutri{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.nutri span{font-size:13px;background:#f0f3ff;color:#4f5d83;padding:7px 10px;border-radius:10px}.recipe-plan details,.recipe-card details{font-size:14px;color:#50607b;line-height:1.55}.details-body{padding:10px 0}
.filterbar{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:14px;border-radius:22px;background:#fff;border:1px solid #eceef6;box-shadow:0 8px 20px rgba(50,68,106,.04)}.filterbar input:first-child{grid-column:1/-1;min-width:0;width:100%}.filterbar .btn{grid-column:1/-1}
.quick-card button{background:linear-gradient(180deg,#fff 0%,#fbfcff 100%);border:1px solid #eceef6;border-radius:18px;padding:15px}.quick-card b{font-size:16px;line-height:1.25}.quick-card span{font-size:12px;margin-top:6px;color:#778098}
.form-grid{grid-template-columns:1fr;gap:12px}.wide{grid-column:auto}.form-grid label{font-size:14px;color:#53607b}.form-grid input,.form-grid select,input,select{min-height:48px;border-radius:15px;border:1px solid #e0e4f0;background:#fff;padding:12px 13px;font-size:15px}.icon-btn{width:34px;height:34px;border-radius:11px}
.table-card{padding:0;overflow:hidden}table{display:block;width:100%}thead{display:none}tbody{display:grid;gap:0}tr{display:grid;grid-template-columns:1fr 1fr;gap:7px 12px;padding:16px 18px;border-bottom:1px solid var(--line)}td{padding:0;border:0;white-space:normal;font-size:13px;line-height:1.4}td:first-child{grid-column:1/-1;font-size:16px;margin-bottom:4px;color:#1f2740}td:nth-child(n+2){color:#6c7690}td:nth-child(4),td:nth-child(6){text-align:right;color:#1f2740}
.schedule-day{grid-template-columns:42px 1fr;gap:10px;padding:12px 0}.weekday-checks{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.weekday-checks label{justify-content:center;padding:9px 6px;font-size:12px;border-radius:12px}.schedule-chip{padding:7px 10px;border-radius:11px;font-size:12px;background:#f0f3ff}.shopping-mini,.reminder-row{padding:14px 0}.shopping-mini span,.reminder-row span{font-size:14px}.shopping-mini small,.reminder-row small{display:block;color:#858ea4;font-size:12px;margin-top:4px}.callout{border-left:0;border-top:4px solid #8896ff;border-radius:18px;background:#f2f5ff;font-size:14px;line-height:1.55;color:#50607b}.cost-note{border-radius:22px;background:linear-gradient(180deg,#fafbff 0%,#f4f7ff 100%)}.cost-note b{font-size:34px}.premium-banner{border-radius:20px;font-size:13px;line-height:1.6}
.bar-label{font-size:14px}.progress{height:11px;border-radius:999px;background:#edf1fb}.progress i{background:linear-gradient(90deg,#8d84ff,#6f90ff)}.progress.protein i{background:linear-gradient(90deg,#ff89c3,#ffb3cf)}
.bottom-nav{position:fixed;left:50%;bottom:12px;transform:translateX(-50%);z-index:45;width:min(calc(100% - 18px),540px);display:grid;grid-template-columns:repeat(5,1fr);gap:6px;padding:9px;border:1px solid rgba(220,226,240,.88);border-radius:26px;background:rgba(255,255,255,.94);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:0 18px 45px rgba(27,44,78,.18)}.bottom-link{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:8px 3px 7px;border-radius:17px;color:#9099ad;font-size:10px;font-weight:800}.bottom-link span:first-child{font-size:19px;line-height:1}.bottom-link.active{background:#eef2ff;color:#5b70dc}
footer{padding:20px 12px 10px;font-size:10px;line-height:1.5;color:#9aa3b8}.flash{border-radius:18px;font-size:14px;padding:14px 16px}
.empty{padding:26px 18px;font-size:14px;border-radius:18px}.feature-list{font-size:15px;line-height:1.75;color:#5d6881}
@media(min-width:700px){body{padding:18px 0}.app-shell{min-height:calc(100vh - 36px);border-radius:34px}.app-header{border-radius:34px 34px 0 0}.bottom-nav{bottom:22px}}
@media(max-width:420px){.content{padding-left:12px;padding-right:12px}.topbar h1{font-size:31px}.topbar .stress .btn{font-size:0;width:44px;height:44px;padding:0}.topbar .stress .btn:before{content:"⚡";font-size:18px}.metrics-grid,.metrics-grid.three{grid-template-columns:1fr 1fr}.metric{padding:15px 14px}.metric b{font-size:24px}.hero{padding:24px 18px}.hero h2{font-size:33px}.ring{width:210px;height:210px}.ring b{font-size:48px}}
'''


PREMIUM_CSS = r'''
/* Premium wellness UI */
body{background:radial-gradient(circle at 10% 8%,rgba(126,111,255,.13),transparent 23%),radial-gradient(circle at 94% 22%,rgba(255,115,180,.12),transparent 24%),linear-gradient(180deg,#fafbff 0%,#f6f6fb 100%)}
.app-shell{position:relative;overflow:visible}.app-shell:before{content:"";position:fixed;pointer-events:none;z-index:-1;width:180px;height:180px;border-radius:50%;top:130px;left:calc(50% - 330px);background:rgba(125,109,255,.08);filter:blur(2px)}
.app-header{background:rgba(250,251,255,.86);border-bottom:1px solid rgba(225,228,241,.78)}.brand-mark{background:linear-gradient(145deg,#7a71ff 0%,#668bff 100%);box-shadow:0 12px 28px rgba(97,104,255,.30)}.brand b{font-size:21px;letter-spacing:-.02em}.brand small{font-size:12px}
.content{padding-top:20px}.topbar{margin-bottom:20px}.topbar h1{font-size:38px;font-weight:900}.eyebrow{font-size:10px;font-weight:900;color:#8991a8}.topbar .stress .btn{background:#fff;border-color:#ececf5;color:#664fa9;box-shadow:0 8px 22px rgba(62,70,108,.07)}
.hero{position:relative;padding:24px 22px 22px;border-radius:34px;background:#fff;border:1px solid rgba(232,232,242,.95);box-shadow:0 24px 55px rgba(54,61,98,.11);overflow:hidden}.hero:before{display:block;content:"";position:absolute;width:180px;height:180px;right:-74px;top:-74px;border-radius:50%;background:linear-gradient(145deg,rgba(255,119,183,.18),rgba(255,199,157,.12))}.hero:after{display:block;content:"";position:absolute;width:130px;height:130px;left:-66px;bottom:-60px;border-radius:50%;background:rgba(118,107,255,.10)}.hero>div:first-child{position:relative;z-index:2;order:2;width:100%}.hero-score{position:relative;z-index:2;order:1;margin:2px 0 22px;display:flex;flex-direction:column;align-items:center;width:100%}.hero .pill{background:linear-gradient(90deg,#f0efff,#fff0f7);color:#705dd8;border:1px solid #ece8ff;font-size:12px;padding:8px 13px}.hero h2{font-size:39px;line-height:1.02;color:#171922;margin:10px 0 12px;text-align:center}.hero p{font-size:16px;line-height:1.55;color:#687086;text-align:center;margin:0 auto;max-width:420px}.ring{width:238px;height:238px;border:none;overflow:hidden;isolation:isolate;display:grid;place-content:center;background:conic-gradient(from -90deg,#776cff 0 45%,#ff73b7 45% 75%,#ffb78f 75% 100%);box-shadow:0 20px 40px rgba(119,108,255,.25);animation:rise .45s ease both}.ring:before{inset:24px;background:linear-gradient(180deg,#fff,#fbfbff);box-shadow:inset 0 0 0 1px #ececf5,0 6px 20px rgba(73,79,111,.06)}.ring b{font-size:56px;color:#171922}.ring span{font-size:13px;color:#838a9d}.hero-score>small{font-size:13px;color:#81889a;margin-top:11px;font-weight:800}.macro-legend{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:13px}.macro-chip{display:flex;align-items:center;gap:7px;padding:8px 10px;border-radius:999px;background:#fafafe;border:1px solid #eeeef5;font-size:12px;color:#596176;font-weight:800}.macro-chip i{width:8px;height:8px;border-radius:50%;display:block}.macro-chip.protein i{background:#ff73b7}.macro-chip.carb i{background:#776cff}.macro-chip.fat i{background:#ffb78f}.hero-actions{margin-top:20px;gap:10px}.hero .btn.primary{background:#1d1d22;color:#fff;border-radius:19px;min-height:56px;font-size:16px;box-shadow:0 12px 26px rgba(28,28,34,.18)}.hero .btn.soft{min-height:50px;background:#f1f2ff;color:#5f66c9;border-radius:18px;font-size:15px}
.metrics-grid{gap:12px}.metric{position:relative;overflow:hidden;padding:18px 16px;border-radius:24px;background:#fff;border:1px solid #ececf4;box-shadow:0 11px 28px rgba(50,57,89,.055)}.metric:after{content:"";position:absolute;width:72px;height:72px;right:-22px;top:-28px;border-radius:50%;opacity:.65}.metric:nth-child(1):after{background:#eadfff}.metric:nth-child(2):after{background:#ffe4ef}.metric:nth-child(3):after{background:#e2edff}.metric:nth-child(4):after{background:#ffe9d6}.metric span{font-size:12px;font-weight:800;color:#7d8497}.metric b{font-size:29px;color:#202334}.metric small{font-size:12px;color:#9298a8}
.card{border-radius:30px;border:1px solid rgba(233,233,242,.96);box-shadow:0 15px 34px rgba(53,62,99,.065)}.card h3{font-size:25px}.section-head a{font-size:13px;font-weight:900;color:#6d69d8;background:#f1f0ff;padding:8px 10px;border-radius:12px}.meal-row{position:relative;background:#fbfbfe;border:1px solid #eeeef5;padding:15px;border-radius:21px}.meal-row:nth-child(1) .meal-icon{background:#fff2d8;color:#b97811}.meal-row:nth-child(2) .meal-icon{background:#edeaff;color:#6658d4}.meal-row:nth-child(3) .meal-icon{background:#ffe8f2;color:#d45389}.meal-row:nth-child(4) .meal-icon{background:#e7f6ef;color:#27815d}.meal-icon{font-size:17px}.meal-row b{font-size:16px}.meal-row small{font-size:12px}.macro b{font-size:19px}.callout{background:linear-gradient(145deg,#f6f4ff,#eff5ff);border-top:0;border-left:4px solid #7b72ef;color:#56617c;border-radius:18px;padding:15px 16px;font-size:14px}.cost-note{background:linear-gradient(145deg,#f7f4ff,#fff6fa);border:1px solid #eee8fa}.cost-note b{font-size:36px}.accent-card{background:linear-gradient(145deg,#29283a,#3a3650);color:#fff;border:0;box-shadow:0 20px 45px rgba(41,40,58,.18)}.accent-card .eyebrow{color:#bcb6ff}.accent-card h3{color:#fff}.accent-card p{color:#dbd9e7}.accent-card .btn.primary{background:#fff;color:#252432;box-shadow:none}
.intro-row{border-radius:30px;background:linear-gradient(145deg,#fff,#faf9ff);box-shadow:0 12px 28px rgba(52,60,96,.05)}.intro-row h2{font-size:30px}.premium-banner{background:linear-gradient(90deg,#fff7e9,#fff0f7);border:1px solid #f3e2cf;color:#6d5962}.day-card{background:#fff}.day-stats span{background:#f7f6ff;border:1px solid #eeebff;border-radius:12px}.recipe-plan,.recipe-card{border-radius:24px;background:#fff;border:1px solid #ededf5;box-shadow:0 10px 25px rgba(58,66,100,.05)}.recipe-plan:hover,.recipe-card:hover{transform:translateY(-1px)}.tag{background:#f0eeff;color:#655fca}.nutri span{background:#f5f5fb;color:#596176}.actions .btn.primary{background:#22222a}.actions .btn.soft{background:#f0f0ff;color:#605ec2}
.filterbar{border-radius:24px}.form-grid input,.form-grid select,input,select{font-size:16px}.quick-card button{border-radius:21px}.quick-card button:hover{border-color:#dcd8ff;background:#faf9ff}.progress{height:12px;background:#efeff6}.progress i{background:linear-gradient(90deg,#776cff,#8ca1ff)}.progress.protein i{background:linear-gradient(90deg,#ff73b7,#ff9dcc)}.bottom-nav{border-radius:29px;background:rgba(255,255,255,.91);border:1px solid rgba(227,228,239,.95);box-shadow:0 20px 48px rgba(37,43,72,.17)}.bottom-link{font-size:10px}.bottom-link span:first-child{font-size:20px}.bottom-link.active{background:linear-gradient(145deg,#eeeaff,#f4f2ff);color:#645dd2}
@keyframes rise{from{transform:translateY(10px) scale(.98);opacity:.6}to{transform:none;opacity:1}}
@media(max-width:420px){.hero h2{font-size:35px}.ring{width:220px;height:220px}.ring b{font-size:50px}.topbar h1{font-size:33px}.metric b{font-size:25px}}

'''

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_connect()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1),name TEXT NOT NULL DEFAULT 'Студент',monthly_budget REAL NOT NULL DEFAULT 20000,calorie_target INTEGER NOT NULL DEFAULT 2200,protein_target INTEGER NOT NULL DEFAULT 100,max_prep INTEGER NOT NULL DEFAULT 30,activity TEXT NOT NULL DEFAULT 'Умеренная',goal TEXT NOT NULL DEFAULT 'Сбалансированное питание',dislikes TEXT NOT NULL DEFAULT '',mode TEXT NOT NULL DEFAULT 'standard');
    CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY AUTOINCREMENT,weekday INTEGER NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,title TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,category TEXT NOT NULL,package_size REAL NOT NULL,unit TEXT NOT NULL,package_price REAL NOT NULL,kcal100 REAL NOT NULL DEFAULT 0,protein100 REAL NOT NULL DEFAULT 0,fat100 REAL NOT NULL DEFAULT 0,carbs100 REAL NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS recipes(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,meal_type TEXT NOT NULL,calories INTEGER NOT NULL,protein REAL NOT NULL,fat REAL NOT NULL,carbs REAL NOT NULL,cost REAL NOT NULL,prep_minutes INTEGER NOT NULL,portable INTEGER NOT NULL DEFAULT 0,difficulty TEXT NOT NULL DEFAULT 'Легко',tags TEXT NOT NULL DEFAULT '',ingredients TEXT NOT NULL,steps TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS pantry(id INTEGER PRIMARY KEY AUTOINCREMENT,product_name TEXT UNIQUE NOT NULL,amount REAL NOT NULL,unit TEXT NOT NULL,expires TEXT NOT NULL DEFAULT '');
    CREATE TABLE IF NOT EXISTS meal_plan(id INTEGER PRIMARY KEY AUTOINCREMENT,plan_date TEXT NOT NULL,meal_type TEXT NOT NULL,recipe_id INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS meal_log(id INTEGER PRIMARY KEY AUTOINCREMENT,log_date TEXT NOT NULL,meal_time TEXT NOT NULL,title TEXT NOT NULL,calories REAL NOT NULL,protein REAL NOT NULL,fat REAL NOT NULL,carbs REAL NOT NULL,cost REAL NOT NULL DEFAULT 0,source TEXT NOT NULL DEFAULT 'manual');
    CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,reminder_time TEXT NOT NULL,weekdays TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6',enabled INTEGER NOT NULL DEFAULT 1);
    ''')

    def ensure_columns(table, columns):
        existing = {r[1] for r in conn.execute(f'PRAGMA table_info({table})')}
        for name, ddl in columns.items():
            if name not in existing:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {ddl}')

    ensure_columns('profile', {
        'name': "TEXT NOT NULL DEFAULT 'Студент'",
        'monthly_budget': 'REAL NOT NULL DEFAULT 20000',
        'calorie_target': 'INTEGER NOT NULL DEFAULT 2200',
        'protein_target': 'INTEGER NOT NULL DEFAULT 100',
        'max_prep': 'INTEGER NOT NULL DEFAULT 30',
        'activity': "TEXT NOT NULL DEFAULT 'Умеренная'",
        'goal': "TEXT NOT NULL DEFAULT 'Сбалансированное питание'",
        'dislikes': "TEXT NOT NULL DEFAULT ''",
        'mode': "TEXT NOT NULL DEFAULT 'standard'",
    })
    ensure_columns('pantry', {
        'expires': "TEXT NOT NULL DEFAULT ''",
    })
    ensure_columns('meal_log', {
        'cost': 'REAL NOT NULL DEFAULT 0',
        'source': "TEXT NOT NULL DEFAULT 'manual'",
    })
    ensure_columns('reminders', {
        'weekdays': "TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6'",
        'enabled': 'INTEGER NOT NULL DEFAULT 1',
    })
    ensure_columns('recipes', {
        'difficulty': "TEXT NOT NULL DEFAULT 'Легко'",
        'tags': "TEXT NOT NULL DEFAULT ''",
        'portable': 'INTEGER NOT NULL DEFAULT 0',
    })

    conn.execute("INSERT OR IGNORE INTO profile(id) VALUES(1)")
    seed_data(conn)
    conn.commit(); conn.close()


def seed_data(conn):
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        rows=[
        ("Овсянка","Крупы",500,"г",95,370,13,7,62),("Рис","Крупы",900,"г",130,350,7,1,77),("Гречка","Крупы",900,"г",145,340,13,3,68),("Макароны","Крупы",450,"г",90,350,12,2,70),("Куриное филе","Белок",800,"г",390,165,31,4,0),("Яйца","Белок",10,"шт",120,155,13,11,1),("Творог 5%","Молочное",300,"г",150,145,17,5,3),("Молоко","Молочное",1000,"мл",90,52,3,3,5),("Йогурт натуральный","Молочное",300,"г",120,70,5,3,7),("Хлеб цельнозерновой","Хлеб",350,"г",95,240,9,3,43),("Бананы","Фрукты",1000,"г",150,89,1,.3,23),("Яблоки","Фрукты",1000,"г",170,52,.3,.2,14),("Овощная смесь","Овощи",400,"г",130,65,3,1,10),("Помидоры","Овощи",500,"г",170,18,.9,.2,4),("Огурцы","Овощи",500,"г",140,15,.8,.1,3),("Сыр","Молочное",200,"г",220,350,25,28,2),("Тунец консервированный","Белок",185,"г",180,120,26,1,0),("Фасоль консервированная","Белок",400,"г",120,95,6,.5,15),("Картофель","Овощи",2000,"г",180,77,2,.1,17),("Лаваш","Хлеб",300,"г",100,275,8,1,56),("Арахисовая паста","Дополнительно",300,"г",250,590,25,50,20)]
        conn.executemany("INSERT INTO products(name,category,package_size,unit,package_price,kcal100,protein100,fat100,carbs100) VALUES(?,?,?,?,?,?,?,?,?)",rows)
    if conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] == 0:
        rows=[
        ("Овсянка с бананом и яйцами","breakfast",520,24,16,70,82,12,0,"Очень легко","быстро,сытно,бюджетно",{"Овсянка":[70,"г"],"Молоко":[200,"мл"],"Бананы":[120,"г"],"Яйца":[2,"шт"]},"Сварить овсянку на молоке. Нарезать банан. Яйца сварить или пожарить."),
        ("Творог с бананом и пастой","breakfast",460,31,16,48,105,3,1,"Очень легко","без готовки,белок,быстро",{"Творог 5%":[200,"г"],"Бананы":[120,"г"],"Арахисовая паста":[15,"г"]},"Смешать творог с бананом и ложкой арахисовой пасты."),
        ("Яичный лаваш с овощами","breakfast",510,28,20,51,118,10,1,"Легко","с собой,быстро",{"Яйца":[3,"шт"],"Лаваш":[80,"г"],"Помидоры":[100,"г"],"Сыр":[25,"г"]},"Сделать омлет, выложить в лаваш вместе с помидорами и сыром, свернуть."),
        ("Курица, рис и овощи","lunch",680,51,15,82,145,25,1,"Легко","контейнер,белок,meal-prep",{"Куриное филе":[170,"г"],"Рис":[90,"г"],"Овощная смесь":[180,"г"]},"Сварить рис. Курицу приготовить, овощи прогреть. Разложить в контейнер."),
        ("Гречка с курицей","lunch",640,50,14,75,138,22,1,"Легко","контейнер,бюджетно",{"Куриное филе":[170,"г"],"Гречка":[90,"г"],"Овощная смесь":[150,"г"]},"Сварить гречку, приготовить курицу и овощи. Можно сделать 2–3 порции."),
        ("Лаваш с тунцом","lunch",570,44,13,62,170,8,1,"Очень легко","с собой,без готовки,быстро",{"Лаваш":[90,"г"],"Тунец консервированный":[130,"г"],"Йогурт натуральный":[40,"г"],"Огурцы":[120,"г"]},"Смешать тунец с йогуртом, добавить огурец и завернуть в лаваш."),
        ("Паста с курицей","dinner",720,50,18,89,152,25,0,"Легко","сытно,meal-prep",{"Макароны":[100,"г"],"Куриное филе":[170,"г"],"Помидоры":[120,"г"],"Сыр":[20,"г"]},"Сварить макароны. Приготовить курицу с помидорами, смешать, посыпать сыром."),
        ("Картофель с яйцами и салатом","dinner",590,27,20,77,105,20,0,"Легко","бюджетно,просто",{"Картофель":[350,"г"],"Яйца":[3,"шт"],"Огурцы":[120,"г"],"Помидоры":[120,"г"]},"Картофель отварить или запечь. Добавить яйца и свежий салат."),
        ("Рис с фасолью и яйцом","dinner",610,28,13,92,92,18,1,"Легко","бюджетно,без мяса",{"Рис":[90,"г"],"Фасоль консервированная":[160,"г"],"Яйца":[2,"шт"],"Овощная смесь":[120,"г"]},"Сварить рис, добавить фасоль и овощи, сверху яйцо."),
        ("Быстрый лаваш с фасолью и яйцом","dinner",625,31,20,73,116,10,1,"Очень легко","сессия,быстро,бюджетно",{"Лаваш":[90,"г"],"Фасоль консервированная":[120,"г"],"Яйца":[2,"шт"],"Сыр":[20,"г"],"Помидоры":[100,"г"]},"Разогреть фасоль, добавить готовые яйца, сыр и помидор, завернуть в лаваш."),
        ("Йогурт, яблоко и хлеб с сыром","snack",330,16,11,44,97,3,1,"Очень легко","перекус,с собой",{"Йогурт натуральный":[180,"г"],"Яблоки":[160,"г"],"Хлеб цельнозерновой":[45,"г"],"Сыр":[25,"г"]},"Собрать перекус с собой."),
        ("Творог и яблоко","snack",300,27,10,29,91,1,1,"Очень легко","перекус,белок",{"Творог 5%":[180,"г"],"Яблоки":[160,"г"]},"Нарезать яблоко и съесть с творогом.")]
        for r in rows:
            conn.execute("INSERT INTO recipes(name,meal_type,calories,protein,fat,carbs,cost,prep_minutes,portable,difficulty,tags,ingredients,steps) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(*r[:11],json.dumps(r[11],ensure_ascii=False),r[12]))
    if conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0] == 0:
        conn.executemany("INSERT INTO schedule(weekday,start_time,end_time,title) VALUES(?,?,?,?)",[(0,"09:00","12:10","Пары"),(0,"13:00","16:10","Пары"),(1,"10:40","15:20","Пары"),(2,"09:00","13:30","Пары"),(3,"12:20","17:00","Пары"),(4,"09:00","12:10","Пары")])
    if conn.execute("SELECT COUNT(*) FROM reminders").fetchone()[0] == 0:
        conn.executemany("INSERT INTO reminders(title,reminder_time,weekdays,enabled) VALUES(?,?,?,1)",[("Не забудь позавтракать","08:00","0,1,2,3,4"),("Время нормального обеда","13:20","0,1,2,3,4")])


def profile(conn): return conn.execute("SELECT * FROM profile WHERE id=1").fetchone()
def to_minutes(t):
    h,m=map(int,t.split(':')); return h*60+m

def busy_midday(conn,d):
    for r in conn.execute("SELECT * FROM schedule WHERE weekday=?",(d.weekday(),)):
        if max(to_minutes(r['start_time']),690)<min(to_minutes(r['end_time']),900): return True
    return False

def get_recipes(conn,mt=None):
    return conn.execute("SELECT * FROM recipes"+(" WHERE meal_type=?" if mt else "")+" ORDER BY cost",((mt,) if mt else ())).fetchall()
def pantry_map(conn): return {r['product_name']:(r['amount'],r['unit']) for r in conn.execute("SELECT * FROM pantry")}

def generate_best_day(conn,d,used=None):
    p=profile(conn); used=set(used or []); dislikes=[x.strip().lower() for x in p['dislikes'].split(',') if x.strip()]; daily_budget=max(p['monthly_budget']/30,250); busy=busy_midday(conn,d)
    pools={}
    for mt in ('breakfast','lunch','dinner'):
        cand=[]
        for r in get_recipes(conn,mt):
            text=(r['name']+' '+r['tags']+' '+r['ingredients']).lower()
            if r['prep_minutes']<=p['max_prep'] and not any(x in text for x in dislikes) and not(mt=='lunch' and busy and not r['portable']): cand.append(r)
        pools[mt]=cand or list(get_recipes(conn,mt))
    best=None; pantry=pantry_map(conn)
    for combo4 in itertools.product(pools['breakfast'],pools['lunch'],pools['dinner'],[None]+list(get_recipes(conn,'snack'))):
        combo=[x for x in combo4 if x]; cal=sum(x['calories'] for x in combo); prot=sum(x['protein'] for x in combo); cost=sum(x['cost'] for x in combo); prep=sum(x['prep_minutes'] for x in combo)
        pantry_hits=sum(1 for r in combo for n in json.loads(r['ingredients']) if n in pantry)
        protein_w = 115 if p['goal']=='Больше белка' else 80
        cost_w = 155 if p['goal']=='Экономия' else 100
        score=abs(cal-p['calorie_target'])/p['calorie_target']*65+max(0,p['protein_target']-prot)/p['protein_target']*protein_w+max(0,cost-daily_budget)/daily_budget*cost_w+prep/18+sum(1 for x in combo if x['id'] in used)*18-pantry_hits*2
        if best is None or score<best[0]: best=(score,combo)
    return best

def save_plan(conn,start,days):
    conn.execute("DELETE FROM meal_plan WHERE plan_date BETWEEN ? AND ?",(start.isoformat(),(start+timedelta(days=days-1)).isoformat())); used=[]
    for i in range(days):
        d=start+timedelta(days=i); best=generate_best_day(conn,d,used)
        for r in best[1]:
            conn.execute("INSERT INTO meal_plan(plan_date,meal_type,recipe_id) VALUES(?,?,?)",(d.isoformat(),r['meal_type'],r['id'])); used.append(r['id'])
    conn.commit()

def get_plan(conn,start,days=1):
    end=start+timedelta(days=days-1); rows=conn.execute("SELECT mp.*,r.name,r.calories,r.protein,r.fat,r.carbs,r.cost,r.prep_minutes,r.portable,r.tags,r.ingredients,r.steps FROM meal_plan mp JOIN recipes r ON r.id=mp.recipe_id WHERE mp.plan_date BETWEEN ? AND ? ORDER BY mp.plan_date,CASE mp.meal_type WHEN 'breakfast' THEN 1 WHEN 'lunch' THEN 2 WHEN 'dinner' THEN 3 ELSE 4 END",(start.isoformat(),end.isoformat())).fetchall(); g=defaultdict(list)
    for r in rows:g[r['plan_date']].append(r)
    return g

def shopping_list(conn,start,days):
    need=defaultdict(float); units={}
    for rows in get_plan(conn,start,days).values():
        for r in rows:
            for n,(a,u) in json.loads(r['ingredients']).items():need[n]+=float(a); units[n]=u
    pan=pantry_map(conn); prods={r['name']:r for r in conn.execute("SELECT * FROM products")}; out=[]; checkout=used=0
    for n,a in sorted(need.items()):
        u=units[n]; stock=pan.get(n,(0,u))[0] if pan.get(n,(0,u))[1]==u else 0; buy=max(0,a-stock); p=prods.get(n); packs=math.ceil(buy/p['package_size']) if p and buy else 0; co=packs*p['package_price'] if p else 0; uv=buy/p['package_size']*p['package_price'] if p and buy else 0; checkout+=co; used+=uv
        out.append(dict(name=n,needed=round(a,1),unit=u,stock=round(stock,1),buy=round(buy,1),packages=packs,checkout=round(co),used_value=round(uv)))
    return out,round(checkout),round(used)

def log_stats(conn,d):
    r=conn.execute("SELECT COALESCE(SUM(calories),0) calories,COALESCE(SUM(protein),0) protein,COALESCE(SUM(fat),0) fat,COALESCE(SUM(carbs),0) carbs,COALESCE(SUM(cost),0) cost FROM meal_log WHERE log_date=?",(d.isoformat(),)).fetchone(); return dict(r)

def next_reminder(conn):
    now=datetime.now(); wd=str(now.weekday()); cur=now.strftime('%H:%M')
    for r in conn.execute("SELECT * FROM reminders WHERE enabled=1 ORDER BY reminder_time"):
        if wd in r['weekdays'].split(',') and r['reminder_time']>=cur:return r
    return None

def money(x): return str(round(float(x)))
def selected(cond): return ' selected' if cond else ''
def checked(cond): return ' checked' if cond else ''

def nav(active):
    items=[('/', '⌂','Сегодня','dashboard'),('/plan','✦','Умный рацион','plan'),('/shopping','🛒','Корзина','shopping'),('/diary','＋','Дневник','diary'),('/recipes','◫','База блюд','recipes'),('/pantry','▦','Что есть дома','pantry'),('/schedule','◷','Расписание','schedule'),('/reminders','♢','Напоминания','reminders'),('/analytics','▥','Аналитика','analytics'),('/profile','⚙','Профиль и режим','profile'),('/about','?','О проекте','about')]
    links=''.join(f'<a class="nav-link {"active" if active==key else ""}" href="{href}"><span class="nav-ico">{ico}</span><span>{label}</span></a>' for href,ico,label,key in items)
    return f'<header class="app-header"><a class="brand" href="/"><span class="brand-mark">С</span><span><b>СтудЕда</b><small>умное питание студента</small></span></a><details class="nav-menu"><summary aria-label="Открыть меню">☰</summary><div class="nav-sheet"><div class="nav-sheet-title">ВСЕ РАЗДЕЛЫ</div><nav class="nav-list">{links}</nav></div></details></header>'

def bottom_nav(active):
    items=[('/', '⌂','Сегодня','dashboard'),('/plan','✦','Рацион','plan'),('/shopping','🛒','Корзина','shopping'),('/diary','＋','Дневник','diary'),('/recipes','◫','Блюда','recipes')]
    return '<nav class="bottom-nav">'+''.join(f'<a class="bottom-link {"active" if active==key else ""}" href="{href}"><span>{ico}</span><span>{label}</span></a>' for href,ico,label,key in items)+'</nav>'

def page(title,active,body,msg=''):
    flash=f'<div class="flash">{esc(msg)}</div>' if msg else ''
    js = """<script>
async function checkReminders(){try{if(!('Notification' in window)||Notification.permission!=='granted')return;const r=await fetch('/api/reminders');const data=await r.json();const now=new Date();const hh=String(now.getHours()).padStart(2,'0')+':'+String(now.getMinutes()).padStart(2,'0');for(const x of data){if(x.time===hh){const key='stueda-'+now.toDateString()+'-'+x.id+'-'+hh;if(!localStorage.getItem(key)){new Notification('СтудЕда',{body:x.title});localStorage.setItem(key,'1');}}}}catch(e){}}
setInterval(checkReminders,30000);checkReminders();
</script>"""
    head = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#f8faff"><title>{esc(title)} — СтудЕда</title><style>{CSS}
{VERTICAL_CSS}
{PREMIUM_CSS}</style></head><body><div class="app-shell">{nav(active)}<main class="content"><header class="topbar"><div><div class="eyebrow">СТУДЕНЧЕСКИЙ ПОМОЩНИК ПО ПИТАНИЮ</div><h1>{esc(title)}</h1></div><form class="stress" method="post" action="/stress-mode"><button class="btn ghost">⚡ Режим сессии</button></form></header>{flash}{body}<footer>Локальный учебный прототип · Калорийность и цены ориентировочные</footer></main>{bottom_nav(active)}</div>'''
    return head + js + '</body></html>'

def metric(label,value,small): return f'<div class="metric"><span>{label}</span><b>{value}</b><small>{small}</small></div>'
def meal_row(r):
    ico={'breakfast':'☀','lunch':'☕','dinner':'☾','snack':'•'}.get(r['meal_type'],'•'); portable=' · можно взять с собой' if r['portable'] else ''
    return f'<div class="meal-row"><div class="meal-icon">{ico}</div><div class="grow"><b>{MEAL_LABELS[r["meal_type"]]} · {esc(r["name"])}</b><small>{r["prep_minutes"]} мин · {money(r["cost"])} ₽{portable}</small></div><div class="macro"><b>{r["calories"]}</b><small>ккал</small></div></div>'

def render_dashboard(q):
    conn=db_connect(); p=profile(conn); today=date.today()
    if conn.execute("SELECT COUNT(*) FROM meal_plan WHERE plan_date=?",(today.isoformat(),)).fetchone()[0]==0:save_plan(conn,today,1)
    plan=get_plan(conn,today,1)[today.isoformat()]; planned={'calories':sum(r['calories'] for r in plan),'protein':sum(r['protein'] for r in plan),'fat':sum(r['fat'] for r in plan),'carbs':sum(r['carbs'] for r in plan),'cost':sum(r['cost'] for r in plan)}; actual=log_stats(conn,today); sched=conn.execute("SELECT * FROM schedule WHERE weekday=? ORDER BY start_time",(today.weekday(),)).fetchall(); rem=next_reminder(conn); shopping,checkout,used=shopping_list(conn,today,1); conn.close()
    body=f'''<div class="hero"><div><span class="pill">✦ {'Премиум-план' if p['mode']=='premium' else 'Персональный план'}</span><h2>Твой рацион на сегодня готов</h2><p>{esc(p['name'])}, мы уже учли бюджет, пары и время на готовку. Не нужно считать всё вручную.</p><div class="hero-actions"><a class="btn primary" href="/plan">Давайте начнём!</a><a class="btn soft" href="/diary">+ Записать, что съел</a></div></div><div class="hero-score"><div class="ring"><b>{planned['calories']}</b><span>ккал / день</span></div><div class="macro-legend"><span class="macro-chip carb"><i></i>Углеводы {round(planned['carbs'])} г</span><span class="macro-chip protein"><i></i>Белки {round(planned['protein'])} г</span><span class="macro-chip fat"><i></i>Жиры {round(planned['fat'])} г</span></div><small>Цель: {p['calorie_target']} ккал</small></div></div>'''
    body+='<div class="metrics-grid">'+metric('Белок в плане',f"{round(planned['protein'])} г",f"цель {p['protein_target']} г")+metric('Стоимость дня',f"≈ {money(planned['cost'])} ₽",f"дневной ориентир ≈ {money(p['monthly_budget']/30)} ₽")+metric('Факт сегодня',f"{round(actual['calories'])} ккал",f"{round(actual['protein'])} г белка")+metric('Следующее напоминание',rem['reminder_time'] if rem else '—',esc(rem['title']) if rem else 'на сегодня всё')+'</div>'
    body+='<div class="two-col"><section class="card"><div class="section-head"><div><span class="eyebrow">ПЛАН БЕЗ РУТИНЫ</span><h3>Что поесть сегодня</h3></div><a href="/plan">изменить →</a></div><div class="meal-list">'+''.join(meal_row(r) for r in plan)+'</div></section>'
    schedule_html=''.join(f'<div class="timeline-row"><b>{esc(s["start_time"])}–{esc(s["end_time"])}</b><span>{esc(s["title"])}</span></div>' for s in sched) or '<div class="empty">Сегодня блоков нет.</div>'
    body+=f'<section class="card"><div class="section-head"><div><span class="eyebrow">РЕАЛЬНЫЙ ДЕНЬ</span><h3>Расписание</h3></div><a href="/schedule">редактировать →</a></div><div class="timeline">{schedule_html}</div><div class="callout">Если пары пересекаются с обедом, генератор отдаёт приоритет блюдам, которые можно взять в контейнере.</div></section></div>'
    mini_parts=[]
    for x in shopping[:4]:
        status = f"{x['buy']} {x['unit']}" if x['buy']>0 else "есть дома ✓"
        mini_parts.append(f'<div class="shopping-mini"><span>{esc(x["name"])}</span><b>{esc(status)}</b></div>')
    mini=''.join(mini_parts)
    body+=f'<div class="two-col"><section class="card"><div class="section-head"><div><span class="eyebrow">НЕ ТОЛЬКО КАЛОРИИ</span><h3>Мини-корзина на день</h3></div><a href="/shopping">вся корзина →</a></div>{mini}<div class="cost-note"><span>На кассе примерно</span><b>{checkout} ₽</b><small>Из купленного в рацион уйдёт примерно на {used} ₽ — остатки останутся на следующие дни.</small></div></section><section class="card accent-card"><span class="eyebrow">ИНСАЙТ ИЗ ИССЛЕДОВАНИЯ</span><h3>«Хочу питаться правильно, но вспоминаю об этом, когда уже голоден»</h3><p>Поэтому приложение помогает принять решение заранее: что приготовить, что взять с собой и что купить — вместо того чтобы просто считать последствия.</p><a class="btn primary" href="/plan">Спланировать заранее</a></section></div>'
    return page(f"Сегодня, {today.strftime('%d.%m')}",'dashboard',body,q.get('msg',[''])[0])

def render_plan(q):
    conn=db_connect(); p=profile(conn); start=date.fromisoformat(q.get('start',[date.today().isoformat()])[0]); allowed=3 if p['mode']=='premium' else 1; days=min(max(int(q.get('days',[str(allowed)])[0]),1),allowed)
    grouped=get_plan(conn,start,days); body=f'<div class="intro-row"><div><h2>Рацион, который помещается в реальную студенческую жизнь</h2><p>Генератор учитывает калории, белок, бюджет, максимум {p["max_prep"]} минут готовки и расписание.</p></div><form method="post" action="/plan" class="inline-form"><input type="date" name="start" value="{start.isoformat()}"><select name="days"><option value="1">1 день</option>{"<option value=\"3\">3 дня</option>" if allowed>=3 else ""}</select><button class="btn primary">✦ Пересобрать план</button></form></div>'
    if p['mode']!='premium':body+='<div class="premium-banner"><b>Стандарт:</b> генерация на 1 день. В Премиум-режиме можно собирать 3 дня сразу и объединять покупки. <a href="/profile">Переключить режим →</a></div>'
    for i in range(days):
        d=start+timedelta(days=i); rows=grouped.get(d.isoformat(),[]); cal=sum(r['calories'] for r in rows); prot=round(sum(r['protein'] for r in rows)); cost=round(sum(r['cost'] for r in rows)); busy=busy_midday(conn,d)
        cards=''
        for r in rows:
            ing=json.loads(r['ingredients']); lis=''.join(f'<li>{esc(n)} — {a} {esc(u)}</li>' for n,(a,u) in ing.items())
            cards+=f'<article class="recipe-plan"><div class="recipe-top"><span class="tag">{MEAL_LABELS[r["meal_type"]]}</span><span>{r["prep_minutes"]} мин</span></div><h4>{esc(r["name"])}</h4><p>{esc(r["tags"].replace(","," · "))}</p><div class="nutri"><span>{r["calories"]} ккал</span><span>Б {round(r["protein"])} г</span><span>{money(r["cost"])} ₽</span></div><details><summary>Ингредиенты и способ</summary><div class="details-body"><ul>{lis}</ul><p>{esc(r["steps"])}</p></div></details><div class="actions"><form method="post" action="/swap"><input type="hidden" name="plan_id" value="{r["id"]}"><input type="hidden" name="return" value="/plan?{urlencode({"start":start.isoformat(),"days":days})}"><button class="btn tiny soft">↻ Заменить</button></form><form method="post" action="/diary-quick"><input type="hidden" name="recipe_id" value="{r["recipe_id"]}"><input type="hidden" name="date" value="{d.isoformat()}"><input type="hidden" name="return" value="/plan?{urlencode({"start":start.isoformat(),"days":days})}"><button class="btn tiny primary">✓ Съел</button></form></div></article>'
        if not cards: cards='<div class="empty">План ещё не создан. Нажми «Пересобрать план».</div>'
        body+=f'<section class="card day-card"><div class="day-head"><div><span class="pill">{WEEKDAYS_RU[d.weekday()]} · {d.strftime("%d.%m")}</span><h3>{"Плотный день — обед с собой" if busy else "Обычный день"}</h3></div><div class="day-stats"><span><b>{cal}</b> ккал</span><span><b>{prot}</b> г белка</span><span><b>{cost}</b> ₽</span></div></div><div class="plan-grid">{cards}</div></section>'
    conn.close(); return page('Умный рацион','plan',body,q.get('msg',[''])[0])

def render_shopping(q):
    conn=db_connect(); p=profile(conn); start=date.fromisoformat(q.get('start',[date.today().isoformat()])[0]); maxd=3 if p['mode']=='premium' else 1; days=min(int(q.get('days',[str(maxd)])[0]),maxd)
    if conn.execute("SELECT COUNT(*) FROM meal_plan WHERE plan_date BETWEEN ? AND ?",(start.isoformat(),(start+timedelta(days=days-1)).isoformat())).fetchone()[0]==0:save_plan(conn,start,days)
    items,checkout,used=shopping_list(conn,start,days)
    row_parts=[]
    for x in items:
        buy_html = f'<span class="need">{x["buy"]} {esc(x["unit"])}</span>' if x['buy']>0 else '<span class="ok">не нужно ✓</span>'
        checkout_html = f'{x["checkout"]} ₽' if x['checkout'] else '—'
        row_parts.append(f'<tr><td><b>{esc(x["name"])}</b></td><td>{x["needed"]} {esc(x["unit"])}</td><td>{x["stock"]} {esc(x["unit"])}</td><td>{buy_html}</td><td>{x["packages"] or "—"}</td><td>{checkout_html}</td></tr>')
    rows=''.join(row_parts)
    body=f'<div class="intro-row"><div><h2>Покупай ровно то, что нужно плану</h2><p>Корзина объединяет ингредиенты, вычитает запасы дома и показывает разницу между суммой на кассе и стоимостью реально использованных продуктов.</p></div><a class="btn soft" href="/pantry">Обновить запасы дома</a></div><div class="metrics-grid three">{metric("План",f"{days} дн.",f"с {start.strftime("%d.%m")}")}{metric("Примерно на кассе",f"{checkout} ₽","с учётом целых упаковок")}{metric("Будет использовано",f"≈ {used} ₽","остальное — запас")}</div><section class="card table-card"><table><thead><tr><th>Продукт</th><th>Нужно</th><th>Есть дома</th><th>Докупить</th><th>Упаковки</th><th>Цена на кассе</th></tr></thead><tbody>{rows}</tbody></table></section><div class="callout"><b>Почему это важно:</b> рацион считает граммы, а магазин продаёт упаковки. Здесь обе величины показаны вместе.</div>'
    conn.close(); return page('Продуктовая корзина','shopping',body,q.get('msg',[''])[0])

def render_diary(q):
    conn=db_connect(); p=profile(conn); d=date.fromisoformat(q.get('date',[date.today().isoformat()])[0]); stats=log_stats(conn,d); logs=conn.execute("SELECT * FROM meal_log WHERE log_date=? ORDER BY meal_time DESC,id DESC",(d.isoformat(),)).fetchall(); quick=conn.execute("SELECT * FROM recipes ORDER BY meal_type,cost LIMIT 12").fetchall()
    quickh=''.join(f'<form method="post" action="/diary-quick" class="quick-card"><input type="hidden" name="recipe_id" value="{r["id"]}"><input type="hidden" name="date" value="{d.isoformat()}"><button><b>{esc(r["name"])}</b><span>{r["calories"]} ккал · Б {round(r["protein"])} · {money(r["cost"])} ₽</span></button></form>' for r in quick)
    logh=''.join(f'<div class="meal-row"><div class="meal-icon">{esc(x["meal_time"])}</div><div class="grow"><b>{esc(x["title"])}</b><small>{round(x["protein"])} г белка · {money(x["cost"])} ₽</small></div><div class="macro"><b>{round(x["calories"])}</b><small>ккал</small></div><form method="post" action="/diary-delete"><input type="hidden" name="id" value="{x["id"]}"><button class="icon-btn">×</button></form></div>' for x in logs) or '<div class="empty">Пока пусто. Быстрые карточки помогают начать без долгого ввода.</div>'
    body=f'''<div class="intro-row"><div><h2>Контроль без ежедневной бухгалтерии</h2><p>Добавляй знакомые блюда одним нажатием или внеси только главное вручную.</p></div><form method="get"><input type="date" name="date" value="{d.isoformat()}" onchange="this.form.submit()"></form></div><div class="metrics-grid">{metric("Калории",round(stats['calories']),f"из {p['calorie_target']}")}{metric("Белок",f"{round(stats['protein'])} г",f"из {p['protein_target']} г")}{metric("Жиры / углеводы",f"{round(stats['fat'])} / {round(stats['carbs'])}","граммов")}{metric("Расходы",f"{round(stats['cost'])} ₽","за отмеченную еду")}</div><section class="card"><div class="section-head"><div><span class="eyebrow">ОДНО НАЖАТИЕ</span><h3>Быстро добавить знакомое блюдо</h3></div></div><div class="quick-grid">{quickh}</div></section><div class="two-col"><section class="card"><span class="eyebrow">РУЧНОЙ ВВОД</span><h3>Если блюда нет в базе</h3><form method="post" action="/diary" class="form-grid"><input type="hidden" name="date" value="{d.isoformat()}"><label class="wide">Что съел<input name="title" placeholder="Например, суп и хлеб" required></label><label>Время<input type="time" name="meal_time" value="12:30"></label><label>Ккал<input type="number" name="calories" min="0" value="400"></label><label>Белок, г<input type="number" step="0.1" name="protein" min="0" value="20"></label><label>Жиры, г<input type="number" step="0.1" name="fat" min="0" value="15"></label><label>Углеводы, г<input type="number" step="0.1" name="carbs" min="0" value="50"></label><label>Цена, ₽<input type="number" name="cost" min="0" value="0"></label><button class="btn primary wide">Добавить</button></form></section><section class="card"><span class="eyebrow">ИСТОРИЯ ДНЯ</span><h3>Что уже записано</h3><div class="meal-list">{logh}</div></section></div>'''
    conn.close(); return page('Дневник питания','diary',body,q.get('msg',[''])[0])

def render_recipes(q):
    conn=db_connect(); search=q.get('q',[''])[0].strip(); mt=q.get('meal_type',[''])[0]; max_cost=q.get('max_cost',[''])[0]; sql='SELECT * FROM recipes WHERE 1=1'; args=[]
    if search: sql+=' AND (name LIKE ? OR tags LIKE ?)'; args += [f'%{search}%',f'%{search}%']
    if mt: sql+=' AND meal_type=?'; args.append(mt)
    if max_cost:
        try: sql+=' AND cost<=?'; args.append(float(max_cost))
        except: pass
    rows=conn.execute(sql+' ORDER BY cost,prep_minutes',args).fetchall(); cards=''
    for r in rows:
        cards+=f'<article class="recipe-card"><div class="recipe-top"><span class="tag">{MEAL_LABELS[r["meal_type"]]}</span><span>{r["prep_minutes"]} мин</span></div><h3>{esc(r["name"])}</h3><p>{esc(r["tags"].replace(","," · "))}</p><div class="nutri"><span>{r["calories"]} ккал</span><span>Б {round(r["protein"])} г</span><span>{money(r["cost"])} ₽</span></div><details><summary>Как приготовить</summary><p>{esc(r["steps"])}</p></details><form method="post" action="/diary-quick"><input type="hidden" name="recipe_id" value="{r["id"]}"><input type="hidden" name="date" value="{date.today().isoformat()}"><button class="btn tiny soft">+ Я это съел сегодня</button></form></article>'
    options='<option value="">Любой приём</option>'+''.join(f'<option value="{k}"{selected(mt==k)}>{v}</option>' for k,v in MEAL_LABELS.items())
    body=f'<div class="intro-row"><div><h2>Простые блюда вместо «что бы приготовить?»</h2><p>База собрана вокруг студенческих ограничений: цена, скорость, сытость и возможность взять еду с собой.</p></div></div><form class="filterbar" method="get"><input name="q" value="{esc(search)}" placeholder="Поиск: быстро, белок, контейнер..."><select name="meal_type">{options}</select><input type="number" name="max_cost" value="{esc(max_cost)}" placeholder="до ₽"><button class="btn primary">Найти</button></form><div class="recipe-grid">{cards or "<div class=empty>Ничего не найдено.</div>"}</div>'
    conn.close(); return page('База недорогих блюд','recipes',body,q.get('msg',[''])[0])

def render_pantry(q):
    conn=db_connect(); pan=conn.execute("SELECT * FROM pantry ORDER BY product_name").fetchall(); products=conn.execute("SELECT name FROM products ORDER BY name").fetchall(); options=''.join(f'<option>{esc(p["name"])}</option>' for p in products); row_parts=[]
    for x in pan:
        expiry = f' · до {esc(x["expires"])}' if x['expires'] else ''
        row_parts.append(f'<div class="shopping-mini"><span>{esc(x["product_name"])}<small>{expiry}</small></span><b>{x["amount"]} {esc(x["unit"])}</b><form method="post" action="/pantry-delete"><input type="hidden" name="id" value="{x["id"]}"><button class="icon-btn">×</button></form></div>')
    rows=''.join(row_parts) or '<div class="empty">Запасы пока не указаны.</div>'
    body=f'<div class="two-col"><section class="card"><span class="eyebrow">ЗАПАСЫ</span><h2>Не покупай то, что уже есть</h2><p>Корзина вычтет остатки из покупок, а генератор будет поощрять блюда с ними.</p><form method="post" action="/pantry" class="form-grid"><label class="wide">Продукт<select name="product_name">{options}</select></label><label>Количество<input type="number" step="0.1" name="amount" value="200"></label><label>Единица<select name="unit"><option>г</option><option>мл</option><option>шт</option></select></label><label class="wide">Годен до (необязательно)<input type="date" name="expires"></label><button class="btn primary wide">Сохранить запас</button></form></section><section class="card"><span class="eyebrow">СЕЙЧАС ДОМА</span><h3>Текущие остатки</h3>{rows}</section></div>'
    conn.close(); return page('Что есть дома','pantry',body,q.get('msg',[''])[0])

def render_schedule(q):
    conn=db_connect(); g=defaultdict(list)
    for r in conn.execute("SELECT * FROM schedule ORDER BY weekday,start_time"):g[r['weekday']].append(r)
    days=''
    for i in range(7):
        chips=''.join(f'<span class="schedule-chip">{esc(x["start_time"])}–{esc(x["end_time"])} {esc(x["title"])} <form method="post" action="/schedule-delete"><input type="hidden" name="id" value="{x["id"]}"><button>×</button></form></span>' for x in g[i]) or '<small>свободно</small>'; days+=f'<div class="schedule-day"><b>{WEEKDAYS_RU[i]}</b><div>{chips}</div></div>'
    opts=''.join(f'<option value="{i}">{WEEKDAYS_RU[i]}</option>' for i in range(7)); body=f'<div class="intro-row"><div><h2>Рацион должен учитывать пары, а не существовать отдельно от них</h2><p>Если обеденное окно занято, приложение выбирает переносимые блюда.</p></div></div><div class="two-col"><section class="card"><span class="eyebrow">ДОБАВИТЬ БЛОК</span><form method="post" action="/schedule" class="form-grid"><label>День<select name="weekday">{opts}</select></label><label>Название<input name="title" value="Пары"></label><label>Начало<input type="time" name="start_time" value="09:00"></label><label>Конец<input type="time" name="end_time" value="12:10"></label><button class="btn primary wide">Добавить</button></form></section><section class="card"><span class="eyebrow">НЕДЕЛЯ</span>{days}</section></div>'
    conn.close(); return page('Учебное расписание','schedule',body,q.get('msg',[''])[0])

def render_reminders(q):
    conn=db_connect(); rows=conn.execute("SELECT * FROM reminders ORDER BY reminder_time").fetchall(); rh=''.join(f'<div class="reminder-row"><div><b>{esc(r["reminder_time"])} · {esc(r["title"])}</b><small>{"включено" if r["enabled"] else "выключено"}</small></div><div class="actions"><form method="post" action="/reminder-toggle"><input type="hidden" name="id" value="{r["id"]}"><button class="btn tiny soft">{"Пауза" if r["enabled"] else "Включить"}</button></form><form method="post" action="/reminder-delete"><input type="hidden" name="id" value="{r["id"]}"><button class="icon-btn">×</button></form></div></div>' for r in rows) or '<div class="empty">Пока нет напоминаний.</div>'
    checks=''.join(f'<label><input type="checkbox" name="weekdays" value="{i}"{checked(i<5)}>{WEEKDAYS_RU[i]}</label>' for i in range(7)); body=f'<div class="two-col"><section class="card"><span class="eyebrow">НОВОЕ НАПОМИНАНИЕ</span><h2>Не жди сильного голода</h2><p>Напоминания помогают перейти от решения «по ситуации» к более стабильному режиму.</p><button type="button" class="btn soft" onclick="Notification.requestPermission()">🔔 Разрешить уведомления в браузере</button><form method="post" action="/reminders" class="form-grid"><label class="wide">Текст<input name="title" value="Время нормально поесть"></label><label>Время<input type="time" name="reminder_time" value="13:00"></label><div class="wide weekday-checks">{checks}</div><button class="btn primary wide">Сохранить</button></form></section><section class="card"><span class="eyebrow">СОХРАНЁННЫЕ</span><h3>Твои напоминания</h3>{rh}</section></div>'
    conn.close(); return page('Напоминания','reminders',body,q.get('msg',[''])[0])

def render_analytics(q):
    conn=db_connect(); p=profile(conn); start=date.today()-timedelta(days=6); rows=[]
    for i in range(7):
        d=start+timedelta(days=i); s=log_stats(conn,d); s['date']=d; s['cal_pct']=min(100,round(s['calories']/max(p['calorie_target'],1)*100)); s['protein_pct']=min(100,round(s['protein']/max(p['protein_target'],1)*100)); rows.append(s)
    avgcal=round(sum(x['calories'] for x in rows)/7); avgp=round(sum(x['protein'] for x in rows)/7); cost=round(sum(x['cost'] for x in rows)); bars=''.join(f'<div class="bar-day"><div class="bar-label"><b>{WEEKDAYS_RU[x["date"].weekday()]} {x["date"].strftime("%d.%m")}</b><span>{round(x["calories"])} ккал · Б {round(x["protein"])} г</span></div><div class="progress"><i style="width:{x["cal_pct"]}%"></i></div><div class="progress protein"><i style="width:{x["protein_pct"]}%"></i></div></div>' for x in rows)
    body=f'<div class="intro-row"><div><h2>Показываем картину, а не наказываем цифрами</h2><p>Быстро видно, где рацион проседает: регулярность, белок, калории или расходы.</p></div></div><div class="metrics-grid three">{metric("Средние калории",avgcal,f"цель {p['calorie_target']}")}{metric("Средний белок",f"{avgp} г",f"цель {p['protein_target']} г")}{metric("Отмеченные расходы",f"{cost} ₽","за 7 дней")}</div><section class="card"><div class="bar-list">{bars}</div></section><div class="callout">Если день пустой, это не «провал»: возможно, учёт оказался лишним действием. Используй быстрые карточки в дневнике.</div>'
    conn.close(); return page('Аналитика недели','analytics',body,q.get('msg',[''])[0])

def render_profile(q):
    conn=db_connect(); p=profile(conn); body=f'''<div class="two-col"><section class="card"><span class="eyebrow">НАСТРОЙКИ</span><h2>Что должен учитывать генератор</h2><form method="post" action="/profile" class="form-grid"><label class="wide">Имя<input name="name" value="{esc(p['name'])}"></label><label>Бюджет на питание / мес., ₽<input type="number" name="monthly_budget" value="{round(p['monthly_budget'])}"></label><label>Цель калорий<input type="number" name="calorie_target" value="{p['calorie_target']}"></label><label>Белок, г<input type="number" name="protein_target" value="{p['protein_target']}"></label><label>Максимум готовки, мин<input type="number" name="max_prep" value="{p['max_prep']}"></label><label>Активность<select name="activity"><option{selected(p['activity']=='Низкая')}>Низкая</option><option{selected(p['activity']=='Умеренная')}>Умеренная</option><option{selected(p['activity']=='Высокая')}>Высокая</option></select></label><label>Цель<select name="goal"><option{selected(p['goal']=='Сбалансированное питание')}>Сбалансированное питание</option><option{selected(p['goal']=='Больше белка')}>Больше белка</option><option{selected(p['goal']=='Экономия')}>Экономия</option></select></label><label class="wide">Не люблю / исключить<input name="dislikes" value="{esc(p['dislikes'])}" placeholder="тунец, творог"></label><label class="wide">Режим<select name="mode"><option value="standard"{selected(p['mode']=='standard')}>Стандарт</option><option value="premium"{selected(p['mode']=='premium')}>Премиум</option></select></label><button class="btn primary wide">Сохранить</button></form></section><section class="card"><span class="eyebrow">ДВА РЕЖИМА</span><h3>Стандарт — уже полноценный</h3><ul class="feature-list"><li>план на сегодня;</li><li>КБЖУ и стоимость;</li><li>дневник, напоминания и база блюд;</li><li>расписание и продукты дома.</li></ul><h3>Премиум — больше автоматизации</h3><ul class="feature-list"><li>план сразу на 3 дня;</li><li>общая корзина с упаковками;</li><li>быстрые замены блюд без сильного изменения баланса.</li></ul><div class="callout">Премиум не блокирует базовые функции: он экономит больше времени.</div></section></div>'''; conn.close(); return page('Профиль и режим','profile',body,q.get('msg',[''])[0])

def render_about(q):
    body='<div class="hero simple"><div><span class="pill">Исследование → продукт</span><h2>СтудЕда решает не проблему «где узнать калории», а проблему «как питаться нормально в реальной студенческой жизни».</h2><p>Студент хочет питаться правильно, но часто решает, что есть, уже в момент сильного голода. При этом точный ручной учёт быстро становится ещё одной обязанностью.</p></div></div><div class="three-col"><div class="card"><span class="eyebrow">ПРОБЛЕМА 1</span><h3>План отдельно от расписания</h3><p>Пары влияют на выбор переносимых блюд.</p></div><div class="card"><span class="eyebrow">ПРОБЛЕМА 2</span><h3>Граммы ≠ упаковки</h3><p>Корзина показывает нужное количество и сумму на кассе.</p></div><div class="card"><span class="eyebrow">ПРОБЛЕМА 3</span><h3>Учёт слишком трудный</h3><p>Знакомое блюдо добавляется одним нажатием.</p></div></div><div class="three-col"><div class="card"><span class="eyebrow">ПРОБЛЕМА 4</span><h3>Сессия ломает рацион</h3><p>Режим сессии ограничивает готовку 12 минутами.</p></div><div class="card"><span class="eyebrow">ПРОБЛЕМА 5</span><h3>Покупки без плана</h3><p>Список строится из рациона и вычитает продукты дома.</p></div><div class="card"><span class="eyebrow">ГЛАВНЫЙ ИНСАЙТ</span><h3>Помочь до момента голода</h3><p>Приложение заранее отвечает: что съесть, приготовить и купить.</p></div></div>'
    return page('О проекте','about',body,q.get('msg',[''])[0])

RENDERERS={'/':render_dashboard,'/plan':render_plan,'/shopping':render_shopping,'/diary':render_diary,'/recipes':render_recipes,'/pantry':render_pantry,'/schedule':render_schedule,'/reminders':render_reminders,'/analytics':render_analytics,'/profile':render_profile,'/about':render_about}

def form_data(handler):
    length=int(handler.headers.get('Content-Length','0') or 0); raw=handler.rfile.read(length).decode('utf-8'); return parse_qs(raw,keep_blank_values=True)
def val(d,k,default=''): return d.get(k,[default])[0]
def redirect(handler,path,msg=''):
    sep='&' if '?' in path else '?'; target=path+(sep+urlencode({'msg':msg}) if msg else ''); handler.send_response(303); handler.send_header('Location',target); handler.end_headers()

def handle_post(handler,path,data):
    conn=db_connect()
    try:
        if path=='/plan':
            start=date.fromisoformat(val(data,'start',date.today().isoformat())); p=profile(conn); days=min(int(val(data,'days','1')),3 if p['mode']=='premium' else 1); save_plan(conn,start,days); redirect(handler,f'/plan?{urlencode({"start":start.isoformat(),"days":days})}','План собран с учётом бюджета, времени и расписания.'); return
        if path=='/swap':
            pid=int(val(data,'plan_id','0')); row=conn.execute("SELECT mp.*,r.calories old_cal,r.protein old_protein,r.cost old_cost FROM meal_plan mp JOIN recipes r ON r.id=mp.recipe_id WHERE mp.id=?",(pid,)).fetchone()
            if row:
                c=conn.execute("SELECT * FROM recipes WHERE meal_type=? AND id<>?",(row['meal_type'],row['recipe_id'])).fetchall(); d=date.fromisoformat(row['plan_date']); p=profile(conn)
                if row['meal_type']=='lunch' and busy_midday(conn,d): c=[r for r in c if r['portable']] or c
                c=[r for r in c if r['prep_minutes']<=p['max_prep']] or c; best=min(c,key=lambda r:abs(r['calories']-row['old_cal'])+abs(r['protein']-row['old_protein'])*8+abs(r['cost']-row['old_cost'])*.7); conn.execute("UPDATE meal_plan SET recipe_id=? WHERE id=?",(best['id'],pid)); conn.commit()
            redirect(handler,val(data,'return','/plan'),'Блюдо заменено на близкое по калориям, белку и цене.'); return
        if path=='/diary':
            d=val(data,'date',date.today().isoformat()); nums=[]
            for k in ('calories','protein','fat','carbs','cost'):
                try: nums.append(float(val(data,k,'0') or 0))
                except: nums.append(0)
            conn.execute("INSERT INTO meal_log(log_date,meal_time,title,calories,protein,fat,carbs,cost) VALUES(?,?,?,?,?,?,?,?)",(d,val(data,'meal_time',datetime.now().strftime('%H:%M')),val(data,'title','Приём пищи'),*nums)); conn.commit(); redirect(handler,f'/diary?date={d}','Приём пищи добавлен без лишних экранов.'); return
        if path=='/diary-quick':
            rid=int(val(data,'recipe_id','0')); d=val(data,'date',date.today().isoformat()); r=conn.execute("SELECT * FROM recipes WHERE id=?",(rid,)).fetchone()
            if r:conn.execute("INSERT INTO meal_log(log_date,meal_time,title,calories,protein,fat,carbs,cost,source) VALUES(?,?,?,?,?,?,?,?,?)",(d,datetime.now().strftime('%H:%M'),r['name'],r['calories'],r['protein'],r['fat'],r['carbs'],r['cost'],'recipe'));conn.commit()
            redirect(handler,val(data,'return',f'/diary?date={d}'),'Добавлено в дневник одним нажатием.'); return
        if path=='/diary-delete':
            rid=int(val(data,'id','0')); r=conn.execute("SELECT log_date FROM meal_log WHERE id=?",(rid,)).fetchone(); conn.execute("DELETE FROM meal_log WHERE id=?",(rid,));conn.commit();redirect(handler,f'/diary?date={r["log_date"] if r else date.today().isoformat()}');return
        if path=='/pantry':
            name=val(data,'product_name'); amount=float(val(data,'amount','0') or 0); unit=val(data,'unit','г'); expires=val(data,'expires',''); conn.execute("INSERT INTO pantry(product_name,amount,unit,expires) VALUES(?,?,?,?) ON CONFLICT(product_name) DO UPDATE SET amount=excluded.amount,unit=excluded.unit,expires=excluded.expires",(name,amount,unit,expires));conn.commit();redirect(handler,'/pantry','Запас обновлён — корзина и план теперь его учитывают.');return
        if path=='/pantry-delete':conn.execute("DELETE FROM pantry WHERE id=?",(int(val(data,'id','0')),));conn.commit();redirect(handler,'/pantry');return
        if path=='/schedule':conn.execute("INSERT INTO schedule(weekday,start_time,end_time,title) VALUES(?,?,?,?)",(int(val(data,'weekday','0')),val(data,'start_time'),val(data,'end_time'),val(data,'title','Пары')));conn.commit();redirect(handler,'/schedule','Расписание обновлено.');return
        if path=='/schedule-delete':conn.execute("DELETE FROM schedule WHERE id=?",(int(val(data,'id','0')),));conn.commit();redirect(handler,'/schedule');return
        if path=='/reminders':
            w=data.get('weekdays',[str(i) for i in range(7)]); conn.execute("INSERT INTO reminders(title,reminder_time,weekdays,enabled) VALUES(?,?,?,1)",(val(data,'title','Время поесть'),val(data,'reminder_time','13:00'),','.join(w)));conn.commit();redirect(handler,'/reminders','Напоминание сохранено.');return
        if path=='/reminder-toggle':conn.execute("UPDATE reminders SET enabled=1-enabled WHERE id=?",(int(val(data,'id','0')),));conn.commit();redirect(handler,'/reminders');return
        if path=='/reminder-delete':conn.execute("DELETE FROM reminders WHERE id=?",(int(val(data,'id','0')),));conn.commit();redirect(handler,'/reminders');return
        if path=='/profile':
            conn.execute("UPDATE profile SET name=?,monthly_budget=?,calorie_target=?,protein_target=?,max_prep=?,activity=?,goal=?,dislikes=?,mode=? WHERE id=1",(val(data,'name','Студент'),float(val(data,'monthly_budget','20000')),int(val(data,'calorie_target','2200')),int(val(data,'protein_target','100')),int(val(data,'max_prep','30')),val(data,'activity','Умеренная'),val(data,'goal','Сбалансированное питание'),val(data,'dislikes',''),val(data,'mode','standard')));conn.commit();redirect(handler,'/profile','Профиль сохранён. Новые планы будут учитывать настройки.');return
        if path=='/stress-mode':
            p=profile(conn); new=12 if p['max_prep']>12 else 30; conn.execute("UPDATE profile SET max_prep=? WHERE id=1",(new,));conn.commit();redirect(handler,'/', 'Режим сессии включён: блюда до 12 минут.' if new==12 else 'Режим сессии выключен.');return
        redirect(handler,'/')
    finally: conn.close()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlparse(self.path); q=parse_qs(u.query)
        if u.path=='/favicon.ico': self.send_response(204); self.end_headers(); return
        if u.path=='/api/reminders':
            conn=db_connect(); now=datetime.now(); wd=str(now.weekday()); data=[{'id':r['id'],'time':r['reminder_time'],'title':r['title']} for r in conn.execute("SELECT * FROM reminders WHERE enabled=1 ORDER BY reminder_time") if wd in r['weekdays'].split(',')]; conn.close(); out=json.dumps(data,ensure_ascii=False).encode('utf-8'); self.send_response(200); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(out))); self.end_headers(); self.wfile.write(out); return
        renderer=RENDERERS.get(u.path)
        if not renderer: self.send_error(404); return
        try: out=renderer(q).encode('utf-8')
        except Exception as e:
            out=page('Ошибка','dashboard',f'<section class="card"><h2>Что-то пошло не так</h2><p>{esc(e)}</p><p>Закрой окно сервера и запусти приложение снова. Данные сохранятся.</p></section>').encode('utf-8')
        self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(out))); self.end_headers(); self.wfile.write(out)
    def do_POST(self):
        u=urlparse(self.path); data=form_data(self)
        try: handle_post(self,u.path,data)
        except Exception as e: redirect(self,'/',f'Ошибка: {e}')
    def log_message(self,fmt,*args):
        print(f"[СтудЕда] {self.address_string()} - {fmt%args}")

if __name__=='__main__':
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    actual_port = server.server_address[1]

    print('\n' + '='*58)
    print('  СТУДЕДА ЗАПУЩЕНА')
    print(f'  Сервер: {HOST}:{actual_port}')
    if os.environ.get('RENDER'):
        print('  Облачный режим Render')
    else:
        local_url = f'http://127.0.0.1:{actual_port}'
        print('  Откройте в браузере: ' + local_url)
        if os.environ.get('STUDEDA_NO_BROWSER') != '1':
            threading.Timer(0.8, lambda: webbrowser.open(local_url)).start()
    print('  Для остановки нажмите Ctrl+C')
    print('='*58 + '\n')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСтудЕда остановлена.')
    finally:
        server.server_close()
