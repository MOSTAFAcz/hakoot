# QuizBattle

Online kvízová hra ve stylu Kahootu — vytvoř kvíz, spusť místnost a soutěž s přáteli v reálném čase.

## Stack

- **Flask** + **Flask-SQLAlchemy** (SQLAlchemy, SQLite) — backend a databáze
- **Flask-Login** — registrace a přihlášení uživatelů
- **Flask-SocketIO** (python-socketio / engineio) — real-time komunikace mezi hráči v místnosti
- **Jinja2** — šablony

## Funkce

- Registrace a přihlášení uživatelů
- Tvorba a úprava kvízů (otázky + odpovědi, bodové ohodnocení)
- Vytvoření herní místnosti s kódem pro připojení
- Společné odpovědání v reálném čase přes WebSockety
- Průběžné skóre a vyhodnocení hráčů

## Spuštění lokálně

```bash
# vytvoření virtualenvu a instalace závislostí
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# spuštění (http://localhost:5000)
python run.py
```

Databáze (`quizbattle.db`) se vytvoří automaticky při prvním spuštění.
