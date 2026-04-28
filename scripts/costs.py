#!/usr/bin/env python3
"""
Jarvis cost dashboard — Claude API spend by agent and time period.
Pulls from token_usage table in claudeclaw.db.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = str(Path(__file__).parent.parent / "store" / "claudeclaw.db")

def run():
    db = sqlite3.connect(DB_PATH)

    def q(sql):
        return db.execute(sql).fetchall()

    # Today
    today = q("""
        SELECT agent_id, ROUND(SUM(cost_usd),4), SUM(input_tokens+output_tokens)
        FROM token_usage
        WHERE date(created_at, 'unixepoch', 'localtime') = date('now', 'localtime')
        GROUP BY agent_id ORDER BY SUM(cost_usd) DESC
    """)

    # This week (Mon–today)
    week = q("""
        SELECT agent_id, ROUND(SUM(cost_usd),4), COUNT(*)
        FROM token_usage
        WHERE created_at >= strftime('%s', date('now', 'localtime', 'weekday 1', '-7 days'))
        GROUP BY agent_id ORDER BY SUM(cost_usd) DESC
    """)

    # This month
    month = q("""
        SELECT agent_id, ROUND(SUM(cost_usd),4), COUNT(*)
        FROM token_usage
        WHERE created_at >= strftime('%s', date('now', 'localtime', 'start of month'))
        GROUP BY agent_id ORDER BY SUM(cost_usd) DESC
    """)

    # All time totals
    totals = q("""
        SELECT agent_id, ROUND(SUM(cost_usd),2), COUNT(*) as turns
        FROM token_usage GROUP BY agent_id ORDER BY SUM(cost_usd) DESC
    """)

    def fmt_row(row):
        agent, cost, extra = row
        return f"  {agent}: ${cost:.4f}"

    def total_cost(rows):
        return sum(r[1] for r in rows)

    lines = []
    lines.append(f"Claude API — {datetime.now().strftime('%b %d, %Y')}")
    lines.append("")

    if today:
        lines.append(f"Today: ${total_cost(today):.4f}")
        for r in today:
            lines.append(fmt_row(r))
    else:
        lines.append("Today: $0.00")

    lines.append("")
    if week:
        lines.append(f"This week: ${total_cost(week):.2f}")
        for r in week:
            lines.append(fmt_row(r))

    lines.append("")
    if month:
        lines.append(f"This month: ${total_cost(month):.2f}")
        for r in month:
            lines.append(fmt_row(r))

    lines.append("")
    lines.append("All time:")
    for agent, cost, turns in totals:
        lines.append(f"  {agent}: ${cost:.2f} ({turns} turns)")

    lines.append("")
    lines.append("Gemini: not tracked (personal GCP account)")

    db.close()
    print("\n".join(lines))

if __name__ == "__main__":
    run()
