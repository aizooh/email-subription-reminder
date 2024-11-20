from datetime import datetime, timedelta
from send_email import send_email

def test_reminder_email(days_before):
    """
    Test email simulating different days before expiry
    """
    # Set a fixed expiry date
    expiry_date = datetime(2024, 3, 15).date()
    
    # Fixed test data
    test_data = {
        'to': 'isaackaris.52@gmail.com',  # Your email
        'name': 'Test Customer',
        'due_date': expiry_date.strftime('%Y-%m-%d'),
        'invoice_no': 'TEST-001',
        'amount': 'KES 5,000',
        'package_name': 'Premium Package'
    }
    
    print(f"\nTesting email simulation:")
    print(f"Expiry date: {expiry_date.strftime('%Y-%m-%d')} (fixed)")
    print(f"Current simulation: {days_before} days before expiry")
    
    # Send test email
    success, message = send_email(**test_data)
    
    if success:
        print("✓ Email sent successfully!")
    else:
        print(f"✗ Failed to send email: {message}")

def run_all_tests():
    # Test all reminder periods
    test_days = [5, 3, 1, 0]
    
    print("""
    Email Reminder Test Script
    -------------------------
    Testing different reminder periods...
    """)
    
    for days in test_days:
        test_reminder_email(days)  # Now only passing days
def run_all_tests():
    # Test all reminder periods
    test_days = [5, 3, 1, 0]
    
    print("""
    Email Reminder Test Script
    -------------------------
    Testing different reminder periods...
    """)
    
    for days in test_days:
        test_reminder_email(days)  # Now only passing days
        # Removed the input prompt
if __name__ == "__main__":
    print("""
    Email Reminder Test Script
    -------------------------
    This will simulate emails at different points before a fixed expiry date.
    """)
    run_all_tests()