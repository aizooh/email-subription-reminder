from datetime import datetime, timedelta
from send_email import send_email

def test_reminder_email(expiry_date, days_before):
    """
    Test email with a fixed expiry date, simulating different days before expiry
    """
    # Fixed test data
    test_data = {
        'to': 'your.email@gmail.com',  # Put your email here
        'name': 'Test Customer',
        'due_date': expiry_date.strftime('%Y-%m-%d'),  # Fixed expiry date
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
    
    print("Starting email tests...")
    print("----------------------")
    
    for days in test_days:
        test_reminder_email(days)
        input(f"\nPress Enter to test next email ({days} days to expiry)...")

if __name__ == "__main__":
    print("""
    Email Reminder Test Script
    -------------------------
    This will send test emails simulating different expiry dates.
    Make sure to check your email after each test.
    """)
    
    # Ask for confirmation
    confirm = input("Ready to start testing? (yes/no): ")
    if confirm.lower() == 'yes':
        run_all_tests()
    else:
        print("Test cancelled")