# ============== S.E.A.N. — Senate Edits & Amendments Notifier ==============

@app.route("/admin/senate-amendments")
@login_required
@admin_required
def senate_amendments():
    """S.E.A.N. — Track House Bills amended by the Senate."""
    import pymssql
    import re

    bills = []
    error = None

    try:
        conn = pymssql.connect(
            server="66.211.150.69", port=1433,
            user="publicuser", password="PublicAccess",
            database="NHLegislatureDB"
        )
        cursor = conn.cursor(as_dict=True)

        # Step 1: Find all HBs with Senate amendment-related docket actions in 2026
        cursor.execute("""
            SELECT DISTINCT d.CondensedBillNo
            FROM Docket d
            WHERE d.sessionyear = 2026
              AND d.LegislativeBody = 'S'
              AND d.CondensedBillNo LIKE 'HB%%'
              AND (
                  d.Description LIKE '%%amendment%%'
                  OR d.Description LIKE '%%ought to pass with%%'
                  OR d.Description LIKE '%%OTP/A%%'
                  OR d.Description LIKE '%%OTP-A%%'
                  OR d.Description LIKE '%%concur%%'
                  OR d.Description LIKE '%%nonconcur%%'
              )
        """)
        qualifying_bills = [row['CondensedBillNo'].strip() for row in cursor.fetchall()]

        if qualifying_bills:
            # Step 2: Get all docket entries for qualifying bills
            placeholders = ",".join(["%s"] * len(qualifying_bills))
            cursor.execute(f"""
                SELECT d.CondensedBillNo, d.Description, d.StatusDate, d.LegislativeBody
                FROM Docket d
                WHERE d.sessionyear = 2026
                  AND d.CondensedBillNo IN ({placeholders})
                ORDER BY d.CondensedBillNo, d.StatusDate
            """, tuple(qualifying_bills))
            docket_rows = cursor.fetchall()

            # Step 3: Get bill titles from Legislation table
            cursor.execute(f"""
                SELECT CondensedBillNo, LSRTitle
                FROM Legislation
                WHERE sessionyear = 2026
                  AND CondensedBillNo IN ({placeholders})
            """, tuple(qualifying_bills))
            titles = {row['CondensedBillNo'].strip(): row['LSRTitle'] for row in cursor.fetchall()}

            # Step 4: Build bill data
            bill_map = {}
            for row in docket_rows:
                bn = row['CondensedBillNo'].strip()
                desc = (row['Description'] or '').strip()
                body = (row['LegislativeBody'] or '').strip()
                date = row['StatusDate']
                date_str = date.strftime('%-m/%-d/%Y') if date else ''

                if bn not in bill_map:
                    bill_map[bn] = {
                        'bill_number': bn,
                        'title': titles.get(bn, ''),
                        'senate_actions': [],
                        'amendment_numbers': [],
                        'house_committee': None,
                        'senate_committee': None,
                        'latest_senate_date': None,
                    }

                # Extract committee referrals
                if 'efer' in desc and ' to ' in desc:
                    m = re.search(r'referred? to\s+(.+?)(?:\s+[HS]J\s*\d+|\s*$)', desc, re.IGNORECASE)
                    if m:
                        comm = m.group(1).strip().rstrip('.')
                        comm = re.sub(r'^Committee on\s+', '', comm, flags=re.IGNORECASE)
                        if body == 'H' and not bill_map[bn]['house_committee']:
                            bill_map[bn]['house_committee'] = comm
                        elif body == 'S' and not bill_map[bn]['senate_committee']:
                            bill_map[bn]['senate_committee'] = comm

                # Senate amendment actions
                desc_lower = desc.lower()
                is_amend = any(kw in desc_lower for kw in [
                    'amendment', 'ought to pass with', 'otp-a', 'otp/a', 'concur', 'nonconcur'
                ])
                if body == 'S' and is_amend:
                    bill_map[bn]['senate_actions'].append({
                        'date': date_str,
                        'date_obj': date,
                        'description': desc,
                    })
                    # Track latest date for sorting
                    if not bill_map[bn]['latest_senate_date'] or date > bill_map[bn]['latest_senate_date']:
                        bill_map[bn]['latest_senate_date'] = date

                    # Extract amendment numbers like #2026-1234h
                    for m in re.finditer(r'#\s*(\d{4}-\d{4,5}[a-z]?)', desc):
                        num = m.group(1)
                        if num not in bill_map[bn]['amendment_numbers']:
                            bill_map[bn]['amendment_numbers'].append(num)

            # Sort each bill's actions newest first
            for bn in bill_map:
                bill_map[bn]['senate_actions'].sort(
                    key=lambda a: a.get('date_obj') or datetime.min, reverse=True
                )

            # Sort bills by latest Senate action date (newest first)
            bills = sorted(
                bill_map.values(),
                key=lambda b: b.get('latest_senate_date') or datetime.min,
                reverse=True
            )

        conn.close()

    except Exception as e:
        app.logger.error(f"S.E.A.N. GC query failed: {e}")
        error = str(e)

    return render_template("admin/senate_amendments.html", bills=bills, error=error)
