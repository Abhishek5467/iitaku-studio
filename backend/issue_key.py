"""Issue a one-use plan/product key after manually verifying payment.
python -m backend.issue_key --plan sr_4k --days 7
Run on the worker with its DATA_DIR. Never publish issued keys or expose this CLI as HTTP."""
import argparse
import secrets
import time
from backend.server import PLANS, PREMIUM, db, digest
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--plan",required=True,choices=[k for k,v in PLANS.items() if v["price"]]+[f"product:{k}" for k in sorted(PREMIUM)]);p.add_argument("--days",type=int,default=7);a=p.parse_args()
    if not 1<=a.days<=30:p.error("Expiry must be 1–30 days")
    token=secrets.token_urlsafe(32)
    with db() as c:c.execute("INSERT INTO keys VALUES(?,?,?,NULL)",(digest(token),a.plan,time.time()+a.days*86400))
    print(token)
