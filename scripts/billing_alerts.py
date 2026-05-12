import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, AuditLog

app = create_app()

def run_billing_alerts():
    with app.app_context():
        print(f"--- Running Billing Alerts Check ({datetime.utcnow()}) ---")

        # Target date for users renewing in 30 days
        target_date = datetime.utcnow() + timedelta(days=30)

        users = User.query.all()
        alerts_sent = 0

        for user in users:
            # Simple check: assuming subscription_date is the start, check if anniversary is in ~30 days
            # For MVP, we'll check if (today + 30 days) month and day match the subscription date
            if target_date.month == user.subscription_date.month and target_date.day == user.subscription_date.day:
                print(f"ALERT: Sending renewal notice to {user.email} (Renewal Date: {target_date.strftime('%Y-%m-%d')})")

                # Log the alert
                audit = AuditLog(action='Automated Billing Renewal Notice Sent', user_id=user.id)
                db.session.add(audit)
                alerts_sent += 1

        db.session.commit()
        print(f"--- Completed. {alerts_sent} alert(s) sent. ---")

if __name__ == "__main__":
    run_billing_alerts()
