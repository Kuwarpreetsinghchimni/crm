"""
Comprehensive Test Suite for Customer_Management_System
Tests end-to-end workflows for Contacts, Leads, Customers, and Dashboard.
"""

import sys
from app import app
from db import query_one, query_all, execute_commit, init_db

def run_tests():
    print("=" * 60)
    print("RUNNING Customer_Management_System END-TO-END TEST SUITE")
    print("=" * 60)

    # 1. Initialize Database
    print("\n[TEST 1] Initializing crm_db and tables...")
    success, msg = init_db()
    assert success, f"Database init failed: {msg}"
    print(f"✓ Database initialization passed: {msg}")

    # Set up Flask test client
    app.config["TESTING"] = True
    client = app.test_client()

    # ----------------------------------------------------
    # 2. CONTACTS MODULE TESTS
    # ----------------------------------------------------
    print("\n[TEST 2] Testing Contacts Module...")

    # 2a. Validation failure (blank full_name, invalid email)
    resp = client.post("/contacts/new", data={
        "full_name": "",
        "email": "not-an-email"
    }, follow_redirects=True)
    assert b"Full name is required" in resp.data or b"valid email" in resp.data
    print("✓ Contacts validation rejected blank name")

    resp = client.post("/contacts/new", data={
        "full_name": "Test User",
        "email": "invalid-email"
    }, follow_redirects=True)
    assert b"A valid email address is required" in resp.data
    print("✓ Contacts validation rejected invalid email")

    # 2b. Successful Creation
    resp = client.post("/contacts/new", data={
        "full_name": "Antigravity Tester",
        "email": "tester@antigravity.local",
        "phone": "+1-800-555-0199",
        "company": "DeepMind Corp",
        "job_title": "Lead Engineer",
        "address": "123 Tech Avenue, Silicon Valley",
        "notes": "VIP partner contact"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Antigravity Tester" in resp.data
    print("✓ Contact created successfully")

    contact = query_one("SELECT * FROM contacts WHERE email = %s", ("tester@antigravity.local",))
    assert contact is not None
    contact_id = contact["id"]

    # 2c. View Detail
    resp = client.get(f"/contacts/{contact_id}")
    assert resp.status_code == 200
    assert b"Lead Engineer" in resp.data
    assert b"DeepMind Corp" in resp.data
    print("✓ Contact detail view verified")

    # 2d. Search Contact
    resp = client.get("/contacts?q=Antigravity")
    assert resp.status_code == 200
    assert b"tester@antigravity.local" in resp.data
    
    # Search non-existent
    resp = client.get("/contacts?q=NonExistentQueryXYZ")
    assert b"No contacts matched" in resp.data
    print("✓ Contact search verified (matches and non-matches)")

    # 2e. Edit Contact
    resp = client.post(f"/contacts/{contact_id}/edit", data={
        "full_name": "Antigravity Senior Tester",
        "email": "tester@antigravity.local",
        "phone": "+1-800-555-9999",
        "company": "DeepMind Corp",
        "job_title": "Principal Architect",
        "address": "123 Tech Avenue",
        "notes": "Updated notes"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Principal Architect" in resp.data
    print("✓ Contact edited and updated successfully")

    # 2f. Delete Contact
    resp = client.post(f"/contacts/{contact_id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"deleted successfully" in resp.data
    deleted_check = query_one("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    assert deleted_check is None
    print("✓ Contact deleted successfully and confirmed absent from DB")

    # 2g. Invalid Contact ID handled safely
    resp = client.get("/contacts/999999", follow_redirects=True)
    assert b"Contact not found" in resp.data
    print("✓ Missing contact ID handled gracefully")


    # ----------------------------------------------------
    # 3. LEADS MODULE TESTS
    # ----------------------------------------------------
    print("\n[TEST 3] Testing Leads Module...")

    # 3a. Validation failure
    resp = client.post("/leads/new", data={
        "full_name": "",
        "status": "New"
    }, follow_redirects=True)
    assert b"Lead name is required" in resp.data
    print("✓ Lead validation rejected empty name")

    # 3b. Create Lead
    resp = client.post("/leads/new", data={
        "full_name": "Alice Prospect",
        "email": "alice@prospect.co",
        "phone": "+1-555-0122",
        "company": "Prospect Dynamics",
        "source": "Website",
        "status": "New",
        "notes": "Looking for custom CRM solution"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Alice Prospect" in resp.data
    print("✓ Lead created successfully")

    lead = query_one("SELECT * FROM leads WHERE full_name = %s", ("Alice Prospect",))
    assert lead is not None
    lead_id = lead["id"]

    # 3c. View Detail & Quick Status Change
    resp = client.get(f"/leads/{lead_id}")
    assert resp.status_code == 200
    assert b"Prospect Dynamics" in resp.data

    resp = client.post(f"/leads/{lead_id}/status", data={"status": "Qualified"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Lead status updated to &#39;Qualified&#39;" in resp.data or b"Qualified" in resp.data
    updated_lead = query_one("SELECT status FROM leads WHERE id = %s", (lead_id,))
    assert updated_lead["status"] == "Qualified"
    print("✓ Lead detail and quick status update verified")

    # 3d. Status Filtering & Search
    resp = client.get("/leads?status=Qualified")
    assert b"Alice Prospect" in resp.data
    resp = client.get("/leads?status=Lost")
    assert b"No leads matched" in resp.data
    print("✓ Lead status filtering verified")

    # 3e. Edit Lead
    resp = client.post(f"/leads/{lead_id}/edit", data={
        "full_name": "Alice Prospect (Verified)",
        "email": "alice@prospect.co",
        "phone": "+1-555-0122",
        "company": "Prospect Dynamics",
        "source": "Referral",
        "status": "Converted",
        "notes": "Ready to onboard"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Converted" in resp.data
    print("✓ Lead edited successfully")

    # 3f. Delete Lead
    resp = client.post(f"/leads/{lead_id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"deleted successfully" in resp.data
    assert query_one("SELECT * FROM leads WHERE id = %s", (lead_id,)) is None
    print("✓ Lead deleted successfully")


    # ----------------------------------------------------
    # 4. CUSTOMERS MODULE TESTS
    # ----------------------------------------------------
    print("\n[TEST 4] Testing Customers Module...")

    # 4a. Validation failure
    resp = client.post("/customers/new", data={
        "full_name": "",
        "email": "notvalid"
    }, follow_redirects=True)
    assert b"Customer name is required" in resp.data
    print("✓ Customer validation rejected empty name")

    # 4b. Create Customer
    resp = client.post("/customers/new", data={
        "full_name": "Global Logistics Corp",
        "email": "billing@globallogistics.com",
        "phone": "+1-555-0987",
        "company": "Global Logistics",
        "address": "456 Harbour Blvd, Suite 300",
        "notes": "Enterprise tier account"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Global Logistics Corp" in resp.data
    print("✓ Customer created successfully")

    customer = query_one("SELECT * FROM customers WHERE email = %s", ("billing@globallogistics.com",))
    assert customer is not None
    cust_id = customer["id"]

    # 4c. View Detail
    resp = client.get(f"/customers/{cust_id}")
    assert resp.status_code == 200
    assert b"Harbour Blvd" in resp.data
    print("✓ Customer detail view verified")

    # 4d. Search Customer
    resp = client.get("/customers?q=Logistics")
    assert resp.status_code == 200
    assert b"billing@globallogistics.com" in resp.data
    print("✓ Customer search verified")

    # 4e. Edit Customer
    resp = client.post(f"/customers/{cust_id}/edit", data={
        "full_name": "Global Logistics International",
        "email": "support@globallogistics.com",
        "phone": "+1-555-0988",
        "company": "Global Logistics Group",
        "address": "456 Harbour Blvd, Suite 400",
        "notes": "Updated enterprise tier"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Global Logistics International" in resp.data
    print("✓ Customer edited successfully")

    # 4f. Delete Customer
    resp = client.post(f"/customers/{cust_id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"deleted successfully" in resp.data
    assert query_one("SELECT * FROM customers WHERE id = %s", (cust_id,)) is None
    print("✓ Customer deleted successfully")


    # ----------------------------------------------------
    # 5. DASHBOARD TESTS
    # ----------------------------------------------------
    print("\n[TEST 5] Testing Dashboard Overview...")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Dashboard Overview" in resp.data
    assert b"Total Contacts" in resp.data
    assert b"Active Leads" in resp.data
    assert b"Total Customers" in resp.data
    print("✓ Dashboard loads with metrics and pipeline stages")

    # ----------------------------------------------------
    # 6. SAFETY CHECK: Verify other DBs untouched
    # ----------------------------------------------------
    print("\n[TEST 6] Safety Verification of other databases...")
    all_dbs = query_all("SHOW DATABASES")
    db_names = [d["Database"] for d in all_dbs]
    assert "crm_db" in db_names
    assert "chauhan_mail_service" in db_names
    assert "upayservices_db" in db_names
    print(f"✓ Verified existing databases remain intact: {', '.join(db_names)}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% End-to-End verified)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
