from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
import qrcode
import io


app = Flask(__name__)
app.secret_key = "nftix_secret_key"


# In-memory storage for tickets
minted_tickets = {}


# ===== Home Page =====
@app.route("/")
def index():
    return render_template("index.html")


# ===== Mint NFT Ticket =====
@app.route("/mint", methods=["GET", "POST"])
def mint():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        event = request.form.get("event")

        if not name or not email or not event:
            flash("All fields are required!", "error")
            return redirect(url_for("mint"))

        ticket_id = f"{event[:3].upper()}-{len(minted_tickets) + 1:04d}"

        minted_tickets[ticket_id] = {
            "name": name,
            "email": email,
            "event": event,
        }

        flash(
            (
                f"Ticket Minted! Your Ticket ID: {ticket_id}"
            ),
            "success",
        )

        return redirect(
            url_for(
                "ticket_qr",
                ticket_id=ticket_id,
            )
        )

    return render_template("mint.html")


# ===== Generate QR Code =====
@app.route("/ticket/<ticket_id>")
def ticket_qr(ticket_id):
    ticket = minted_tickets.get(ticket_id)
    if not ticket:
        flash("Invalid Ticket ID!", "error")
        return redirect(url_for("mint"))

    qr_data = (
        f"Ticket ID: {ticket_id}\n"
        f"Name: {ticket['name']}\n"
        f"Event: {ticket['event']}"
    )
    qr_img = qrcode.make(qr_data)

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(
        buf,
        mimetype="image/png",
    )


# ===== Verify NFT Ticket =====
@app.route("/verify", methods=["GET", "POST"])
def verify():
    ticket_info = None
    ticket_id = None

    if request.method == "POST":
        ticket_id = request.form.get("ticketId", "").strip().upper()
        ticket_info = minted_tickets.get(ticket_id)

        if ticket_info:
            flash(
                (
                    f"Ticket Verified! Event: {ticket_info['event']}, "
                    f"Name: {ticket_info['name']}"
                ),
                "success",
            )
        else:
            flash("Invalid Ticket ID!", "error")

    return render_template(
        "verify.html",
        ticket_info=ticket_info,
        ticket_id=ticket_id,
    )


# ===== Run Flask App =====
if __name__ == "__main__":
    app.run(debug=True)













