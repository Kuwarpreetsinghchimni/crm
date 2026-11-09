"""
Customer_Management_System - Beginner-Friendly Local CRM
Tech Stack: Python, Flask, MySQL, HTML5, CSS, Vanilla JavaScript
"""

import re
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from config import Config
from db import query_one, query_all, execute_commit, init_db

app = Flask(__name__)
app.config.from_object(Config)

# Allowed lead statuses for validation and dropdowns
LEAD_STATUSES = ["New", "Contacted", "Qualified", "Converted", "Lost"]

# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

def is_valid_email(email_str):
    """Simple, practical email validation."""
    if not email_str:
        return False
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(email_regex, email_str.strip()))

def sanitize_text(val):
    """Strip surrounding whitespace from user inputs."""
    return val.strip() if val else ""


def sync_converted_lead_to_customer(lead_id):
    """Create a customer record when a lead is converted, once per email."""
    lead = query_one("SELECT * FROM leads WHERE id = %s", (lead_id,))
    if not lead or lead.get("status") != "Converted":
        return False

    email = sanitize_text(lead.get("email"))
    if not email:
        return False

    if query_one("SELECT id FROM customers WHERE email = %s LIMIT 1", (email,)):
        return True

    success, _ = execute_commit(
        """INSERT INTO customers (full_name, email, phone, company, address, notes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (lead["full_name"], email, lead.get("phone"), lead.get("company"), "", lead.get("notes") or "")
    )
    return success


# ---------------------------------------------------------------------------
# Context Processors & Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    """Custom friendly 404 page."""
    return render_template("base.html", error_title="Record or Page Not Found",
                           error_message="The requested record or URL does not exist."), 404

@app.errorhandler(500)
def server_error(e):
    """Custom friendly 500 page."""
    return render_template("base.html", error_title="Server Error",
                           error_message="An unexpected error occurred. Please verify your database connection."), 500


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """
    Main dashboard displaying summary metric cards,
    lead status breakdown, and recent records.
    """
    # Summary counts
    contact_count_row = query_one("SELECT COUNT(*) AS total FROM contacts")
    lead_count_row = query_one("SELECT COUNT(*) AS total FROM leads")
    customer_count_row = query_one("SELECT COUNT(*) AS total FROM customers")

    total_contacts = contact_count_row["total"] if contact_count_row else 0
    total_leads = lead_count_row["total"] if lead_count_row else 0
    total_customers = customer_count_row["total"] if customer_count_row else 0

    # Leads grouped by status
    lead_status_rows = query_all(
        "SELECT status, COUNT(*) AS count FROM leads GROUP BY status"
    )
    status_counts = {status: 0 for status in LEAD_STATUSES}
    for row in lead_status_rows:
        if row["status"] in status_counts:
            status_counts[row["status"]] = row["count"]

    # Recent entries (last 5 of each)
    recent_contacts = query_all(
        "SELECT id, full_name, email, company, created_at FROM contacts ORDER BY created_at DESC LIMIT 5"
    )
    recent_leads = query_all(
        "SELECT id, full_name, company, status, created_at FROM leads ORDER BY created_at DESC LIMIT 5"
    )
    recent_customers = query_all(
        "SELECT id, full_name, email, company, created_at FROM customers ORDER BY created_at DESC LIMIT 5"
    )

    return render_template(
        "dashboard.html",
        total_contacts=total_contacts,
        total_leads=total_leads,
        total_customers=total_customers,
        status_counts=status_counts,
        recent_contacts=recent_contacts,
        recent_leads=recent_leads,
        recent_customers=recent_customers,
        lead_statuses=LEAD_STATUSES
    )


# ---------------------------------------------------------------------------
# MODULE A: Contacts Management
# ---------------------------------------------------------------------------

@app.route("/contacts")
def contacts_list():
    """Display contacts with optional search by name, email, or phone."""
    search_query = sanitize_text(request.args.get("q", ""))
    
    if search_query:
        like_pattern = f"%{search_query}%"
        sql = """
            SELECT * FROM contacts 
            WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY created_at DESC
        """
        contacts = query_all(sql, (like_pattern, like_pattern, like_pattern))
    else:
        sql = "SELECT * FROM contacts ORDER BY created_at DESC"
        contacts = query_all(sql)

    return render_template("contacts.html", contacts=contacts, search_query=search_query)

@app.route("/contacts/new", methods=["GET", "POST"])
def contact_create():
    """Create a new contact."""
    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        job_title = sanitize_text(request.form.get("job_title"))
        address = sanitize_text(request.form.get("address"))
        notes = sanitize_text(request.form.get("notes"))

        # Validation
        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("contact_form.html", form_data=request.form, action="Add")
        
        if not email or not is_valid_email(email):
            flash("A valid email address is required.", "danger")
            return render_template("contact_form.html", form_data=request.form, action="Add")

        sql = """
            INSERT INTO contacts (full_name, email, phone, company, job_title, address, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        success, result = execute_commit(sql, (full_name, email, phone, company, job_title, address, notes))
        if success:
            flash(f"Contact '{full_name}' created successfully!", "success")
            return redirect(url_for("contacts_list"))
        else:
            flash("Failed to create contact due to a database error.", "danger")
            return render_template("contact_form.html", form_data=request.form, action="Add")

    return render_template("contact_form.html", form_data={}, action="Add")

@app.route("/contacts/<int:contact_id>")
def contact_detail(contact_id):
    """View details of a specific contact."""
    contact = query_one("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    if not contact:
        flash("Contact not found.", "warning")
        return redirect(url_for("contacts_list"))
    return render_template("contact_detail.html", contact=contact)

@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    """Edit an existing contact."""
    contact = query_one("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    if not contact:
        flash("Contact not found.", "warning")
        return redirect(url_for("contacts_list"))

    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        job_title = sanitize_text(request.form.get("job_title"))
        address = sanitize_text(request.form.get("address"))
        notes = sanitize_text(request.form.get("notes"))

        # Validation
        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("contact_form.html", form_data=request.form, action="Edit", contact_id=contact_id)

        if not email or not is_valid_email(email):
            flash("A valid email address is required.", "danger")
            return render_template("contact_form.html", form_data=request.form, action="Edit", contact_id=contact_id)

        sql = """
            UPDATE contacts 
            SET full_name = %s, email = %s, phone = %s, company = %s, job_title = %s, address = %s, notes = %s
            WHERE id = %s
        """
        success, result = execute_commit(sql, (full_name, email, phone, company, job_title, address, notes, contact_id))
        if success:
            flash(f"Contact '{full_name}' updated successfully!", "success")
            return redirect(url_for("contact_detail", contact_id=contact_id))
        else:
            flash("Failed to update contact due to a database error.", "danger")

    return render_template("contact_form.html", form_data=contact, action="Edit", contact_id=contact_id)

@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    """Delete a contact (strictly POST)."""
    contact = query_one("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    if not contact:
        flash("Contact not found.", "warning")
        return redirect(url_for("contacts_list"))

    success, _ = execute_commit("DELETE FROM contacts WHERE id = %s", (contact_id,))
    if success:
        flash(f"Contact '{contact['full_name']}' deleted successfully.", "success")
    else:
        flash("Could not delete contact.", "danger")

    return redirect(url_for("contacts_list"))


# ---------------------------------------------------------------------------
# MODULE B: Leads Management
# ---------------------------------------------------------------------------

@app.route("/leads")
def leads_list():
    """Display leads with search and optional status filtering."""
    search_query = sanitize_text(request.args.get("q", ""))
    status_filter = sanitize_text(request.args.get("status", ""))

    where_clauses = []
    params = []

    if search_query:
        where_clauses.append("(full_name LIKE %s OR email LIKE %s OR phone LIKE %s OR company LIKE %s)")
        like_p = f"%{search_query}%"
        params.extend([like_p, like_p, like_p, like_p])

    if status_filter and status_filter in LEAD_STATUSES:
        where_clauses.append("status = %s")
        params.append(status_filter)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    sql = f"SELECT * FROM leads {where_sql} ORDER BY created_at DESC"
    
    leads = query_all(sql, params)
    return render_template(
        "leads.html",
        leads=leads,
        search_query=search_query,
        status_filter=status_filter,
        lead_statuses=LEAD_STATUSES
    )

@app.route("/leads/new", methods=["GET", "POST"])
def lead_create():
    """Create a new lead."""
    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        source = sanitize_text(request.form.get("source"))
        status = sanitize_text(request.form.get("status", "New"))
        notes = sanitize_text(request.form.get("notes"))

        # Validation
        if not full_name:
            flash("Lead name is required.", "danger")
            return render_template("lead_form.html", form_data=request.form, action="Add", lead_statuses=LEAD_STATUSES)

        if email and not is_valid_email(email):
            flash("If provided, email must be valid.", "danger")
            return render_template("lead_form.html", form_data=request.form, action="Add", lead_statuses=LEAD_STATUSES)

        if status not in LEAD_STATUSES:
            status = "New"

        sql = """
            INSERT INTO leads (full_name, email, phone, company, source, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        success, result = execute_commit(sql, (full_name, email, phone, company, source, status, notes))
        if success:
            flash(f"Lead '{full_name}' created successfully!", "success")
            return redirect(url_for("leads_list"))
        else:
            flash("Failed to create lead due to a database error.", "danger")
            return render_template("lead_form.html", form_data=request.form, action="Add", lead_statuses=LEAD_STATUSES)

    return render_template("lead_form.html", form_data={"status": "New"}, action="Add", lead_statuses=LEAD_STATUSES)

@app.route("/leads/<int:lead_id>")
def lead_detail(lead_id):
    """View details of an individual lead."""
    lead = query_one("SELECT * FROM leads WHERE id = %s", (lead_id,))
    if not lead:
        flash("Lead not found.", "warning")
        return redirect(url_for("leads_list"))
    return render_template("lead_detail.html", lead=lead, lead_statuses=LEAD_STATUSES)

@app.route("/leads/<int:lead_id>/edit", methods=["GET", "POST"])
def lead_edit(lead_id):
    """Edit an existing lead."""
    lead = query_one("SELECT * FROM leads WHERE id = %s", (lead_id,))
    if not lead:
        flash("Lead not found.", "warning")
        return redirect(url_for("leads_list"))

    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        source = sanitize_text(request.form.get("source"))
        status = sanitize_text(request.form.get("status", "New"))
        notes = sanitize_text(request.form.get("notes"))

        if not full_name:
            flash("Lead name is required.", "danger")
            return render_template("lead_form.html", form_data=request.form, action="Edit", lead_id=lead_id, lead_statuses=LEAD_STATUSES)

        if email and not is_valid_email(email):
            flash("If provided, email must be valid.", "danger")
            return render_template("lead_form.html", form_data=request.form, action="Edit", lead_id=lead_id, lead_statuses=LEAD_STATUSES)

        if status not in LEAD_STATUSES:
            status = lead["status"]

        sql = """
            UPDATE leads
            SET full_name = %s, email = %s, phone = %s, company = %s, source = %s, status = %s, notes = %s
            WHERE id = %s
        """
        success, _ = execute_commit(sql, (full_name, email, phone, company, source, status, notes, lead_id))
        if success:
            if status == "Converted" and not sync_converted_lead_to_customer(lead_id):
                flash("Lead updated, but it could not be added as a customer. Ensure it has a valid email address.", "warning")
            else:
                flash(f"Lead '{full_name}' updated successfully!", "success")
            return redirect(url_for("lead_detail", lead_id=lead_id))
        else:
            flash("Failed to update lead.", "danger")

    return render_template("lead_form.html", form_data=lead, action="Edit", lead_id=lead_id, lead_statuses=LEAD_STATUSES)

@app.route("/leads/<int:lead_id>/status", methods=["POST"])
def lead_quick_status(lead_id):
    """Quickly update a lead's status directly from detail view."""
    new_status = sanitize_text(request.form.get("status"))
    if new_status in LEAD_STATUSES:
        success, _ = execute_commit("UPDATE leads SET status = %s WHERE id = %s", (new_status, lead_id))
        if success:
            if new_status == "Converted" and not sync_converted_lead_to_customer(lead_id):
                flash("Lead status updated, but it could not be added as a customer. Ensure it has a valid email address.", "warning")
            else:
                flash(f"Lead status updated to '{new_status}'.", "success")
        else:
            flash("Could not update status.", "danger")
    else:
        flash("Invalid status selected.", "warning")
    return redirect(url_for("lead_detail", lead_id=lead_id))

@app.route("/leads/<int:lead_id>/delete", methods=["POST"])
def lead_delete(lead_id):
    """Delete a lead (strictly POST)."""
    lead = query_one("SELECT * FROM leads WHERE id = %s", (lead_id,))
    if not lead:
        flash("Lead not found.", "warning")
        return redirect(url_for("leads_list"))

    # Remove the matching customer record when deleting a converted lead.
    if lead.get("status") == "Converted" and lead.get("email"):
        execute_commit("DELETE FROM customers WHERE email = %s", (lead["email"],))

    success, _ = execute_commit("DELETE FROM leads WHERE id = %s", (lead_id,))
    if success:
        flash(f"Lead '{lead['full_name']}' deleted successfully.", "success")
    else:
        flash("Could not delete lead.", "danger")

    return redirect(url_for("leads_list"))


# ---------------------------------------------------------------------------
# MODULE C: Customers Management
# ---------------------------------------------------------------------------

@app.route("/customers")
def customers_list():
    """Display customers with search by name, email, phone, or company."""
    search_query = sanitize_text(request.args.get("q", ""))
    
    if search_query:
        like_p = f"%{search_query}%"
        sql = """
            SELECT * FROM customers 
            WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s OR company LIKE %s
            ORDER BY created_at DESC
        """
        customers = query_all(sql, (like_p, like_p, like_p, like_p))
    else:
        sql = "SELECT * FROM customers ORDER BY created_at DESC"
        customers = query_all(sql)

    return render_template("customers.html", customers=customers, search_query=search_query)

@app.route("/customers/new", methods=["GET", "POST"])
def customer_create():
    """Create a new customer."""
    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        address = sanitize_text(request.form.get("address"))
        notes = sanitize_text(request.form.get("notes"))

        if not full_name:
            flash("Customer name is required.", "danger")
            return render_template("customer_form.html", form_data=request.form, action="Add")

        if not email or not is_valid_email(email):
            flash("A valid email address is required.", "danger")
            return render_template("customer_form.html", form_data=request.form, action="Add")

        sql = """
            INSERT INTO customers (full_name, email, phone, company, address, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        success, _ = execute_commit(sql, (full_name, email, phone, company, address, notes))
        if success:
            flash(f"Customer '{full_name}' created successfully!", "success")
            return redirect(url_for("customers_list"))
        else:
            flash("Failed to create customer due to a database error.", "danger")

    return render_template("customer_form.html", form_data={}, action="Add")

@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):
    """View details of a customer."""
    customer = query_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers_list"))
    return render_template("customer_detail.html", customer=customer)

@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
def customer_edit(customer_id):
    """Edit an existing customer."""
    customer = query_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers_list"))

    if request.method == "POST":
        full_name = sanitize_text(request.form.get("full_name"))
        email = sanitize_text(request.form.get("email"))
        phone = sanitize_text(request.form.get("phone"))
        company = sanitize_text(request.form.get("company"))
        address = sanitize_text(request.form.get("address"))
        notes = sanitize_text(request.form.get("notes"))

        if not full_name:
            flash("Customer name is required.", "danger")
            return render_template("customer_form.html", form_data=request.form, action="Edit", customer_id=customer_id)

        if not email or not is_valid_email(email):
            flash("A valid email address is required.", "danger")
            return render_template("customer_form.html", form_data=request.form, action="Edit", customer_id=customer_id)

        sql = """
            UPDATE customers
            SET full_name = %s, email = %s, phone = %s, company = %s, address = %s, notes = %s
            WHERE id = %s
        """
        success, _ = execute_commit(sql, (full_name, email, phone, company, address, notes, customer_id))
        if success:
            flash(f"Customer '{full_name}' updated successfully!", "success")
            return redirect(url_for("customer_detail", customer_id=customer_id))
        else:
            flash("Failed to update customer.", "danger")

    return render_template("customer_form.html", form_data=customer, action="Edit", customer_id=customer_id)

@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def customer_delete(customer_id):
    """Delete a customer (strictly POST)."""
    customer = query_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
    if not customer:
        flash("Customer not found.", "warning")
        return redirect(url_for("customers_list"))

    success, _ = execute_commit("DELETE FROM customers WHERE id = %s", (customer_id,))
    if success:
        flash(f"Customer '{customer['full_name']}' deleted successfully.", "success")
    else:
        flash("Could not delete customer.", "danger")

    return redirect(url_for("customers_list"))


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Ensure database tables exist upon start
    init_db()
    print("Starting Customer_Management_System locally on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
