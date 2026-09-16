import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for
from jinja2 import ChoiceLoader, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "crm.db"

app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = "techbridge-class-project"
app.jinja_loader = ChoiceLoader(
    [FileSystemLoader(BASE_DIR / "templates"), FileSystemLoader(BASE_DIR)]
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def setup_database():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        );
        """
    )
    db.close()


@app.route("/")
def dashboard():
    db = get_db()
    customer_total = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    ticket_total = db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    open_total = db.execute("SELECT COUNT(*) FROM tickets WHERE status != 'Closed'").fetchone()[0]
    recent_tickets = db.execute(
        """
        SELECT tickets.*, customers.company_name
        FROM tickets
        JOIN customers ON customers.id = tickets.customer_id
        ORDER BY tickets.id DESC
        LIMIT 5
        """
    ).fetchall()
    return render_template(
        "dashboard.html",
        customer_total=customer_total,
        ticket_total=ticket_total,
        open_total=open_total,
        recent_tickets=recent_tickets,
    )


@app.route("/customers", methods=["GET", "POST"])
def customers():
    db = get_db()
    if request.method == "POST":
        company_name = request.form["company_name"].strip()
        contact_name = request.form["contact_name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        if not company_name or not contact_name or not email:
            flash("Please fill in the company, contact person and email.")
        else:
            db.execute(
                "INSERT INTO customers (company_name, contact_name, email, phone) VALUES (?, ?, ?, ?)",
                (company_name, contact_name, email, phone),
            )
            db.commit()
            flash("Customer added.")
            return redirect(url_for("customers"))

    customer_list = db.execute("SELECT * FROM customers ORDER BY company_name").fetchall()
    return render_template("customers.html", customers=customer_list)


@app.route("/tickets", methods=["GET", "POST"])
def tickets():
    db = get_db()
    customer_list = db.execute("SELECT * FROM customers ORDER BY company_name").fetchall()

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "")
        subject = request.form["subject"].strip()
        description = request.form["description"].strip()
        priority = request.form["priority"]

        if not customer_id or not subject or not description:
            flash("Please choose a customer and complete the ticket details.")
        else:
            db.execute(
                """
                INSERT INTO tickets (customer_id, subject, description, priority)
                VALUES (?, ?, ?, ?)
                """,
                (customer_id, subject, description, priority),
            )
            db.commit()
            flash("Ticket logged.")
            return redirect(url_for("tickets"))

    ticket_list = db.execute(
        """
        SELECT tickets.*, customers.company_name
        FROM tickets JOIN customers ON customers.id = tickets.customer_id
        ORDER BY tickets.id DESC
        """
    ).fetchall()
    return render_template("tickets.html", tickets=ticket_list, customers=customer_list)


@app.post("/tickets/<int:ticket_id>/status")
def change_ticket_status(ticket_id):
    status = request.form["status"]
    if status not in ("Open", "In Progress", "Closed"):
        flash("That status is not allowed.")
    else:
        db = get_db()
        db.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        db.commit()
        flash("Ticket status updated.")
    return redirect(url_for("tickets"))


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
