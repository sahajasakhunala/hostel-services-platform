from app.db.connection import get_db_cursor


class ReportRepository:
    """Data Access Object (DAO) executing Phase 5 analytical business intelligence queries."""

    @staticmethod
    def get_hostel_occupancy():
        """Report 01: Hostel Occupancy Analysis (CTEs & Conditional Aggregations)."""
        query = """
            WITH hostel_bed_stats AS (
                SELECT 
                    h.hostel_id,
                    h.name AS hostel_name,
                    h.gender_type,
                    COUNT(bd.bed_id) AS total_beds,
                    SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds,
                    SUM(CASE WHEN bd.status = 'available' THEN 1 ELSE 0 END) AS vacant_beds,
                    SUM(CASE WHEN bd.status = 'under_maintenance' THEN 1 ELSE 0 END) AS maintenance_beds
                FROM hostels h
                LEFT JOIN blocks b ON h.hostel_id = b.hostel_id
                LEFT JOIN floors fl ON b.block_id = fl.block_id
                LEFT JOIN rooms r ON fl.floor_id = r.floor_id
                LEFT JOIN beds bd ON r.room_id = bd.room_id
                GROUP BY h.hostel_id, h.name, h.gender_type
            )
            SELECT 
                hostel_id,
                hostel_name,
                gender_type,
                total_beds,
                occupied_beds,
                vacant_beds,
                maintenance_beds,
                CASE 
                    WHEN total_beds = 0 THEN 0.00
                    ELSE ROUND((occupied_beds / total_beds) * 100.0, 2)
                END AS occupancy_percentage
            FROM hostel_bed_stats
            ORDER BY occupancy_percentage DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_block_occupancy_ranking():
        """Report 02: Block Occupancy Ranking (ROW_NUMBER Window Function)."""
        query = """
            WITH block_bed_stats AS (
                SELECT 
                    h.hostel_id,
                    h.name AS hostel_name,
                    b.block_id,
                    b.name AS block_name,
                    COUNT(bd.bed_id) AS total_beds,
                    SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds,
                    CASE 
                        WHEN COUNT(bd.bed_id) = 0 THEN 0.00
                        ELSE ROUND((SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) / COUNT(bd.bed_id)) * 100.0, 2)
                    END AS occupancy_percentage
                FROM blocks b
                JOIN hostels h ON b.hostel_id = h.hostel_id
                LEFT JOIN floors fl ON b.block_id = fl.block_id
                LEFT JOIN rooms r ON fl.floor_id = r.floor_id
                LEFT JOIN beds bd ON r.room_id = bd.room_id
                GROUP BY h.hostel_id, h.name, b.block_id, b.name
            )
            SELECT 
                hostel_name,
                block_name,
                total_beds,
                occupied_beds,
                occupancy_percentage,
                ROW_NUMBER() OVER (
                    PARTITION BY hostel_id 
                    ORDER BY occupancy_percentage DESC, total_beds DESC
                ) AS block_rank_within_hostel
            FROM block_bed_stats
            ORDER BY hostel_name ASC, block_rank_within_hostel ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_outstanding_dues_ranking():
        """Report 03: Outstanding Fee Ranking (DENSE_RANK Window Function)."""
        query = """
            SELECT 
                invoice_id,
                student_id,
                registration_number,
                student_name,
                academic_year,
                room_type,
                total_amount,
                paid_amount,
                outstanding_balance,
                due_date,
                days_overdue,
                DENSE_RANK() OVER (ORDER BY outstanding_balance DESC) AS fee_due_rank
            FROM v_fee_dues
            ORDER BY fee_due_rank ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_allocation_stay_analysis():
        """Report 04: Allocation Stay Analysis (Date Math & Aggregations)."""
        query = """
            SELECT 
                hostel_name,
                COUNT(allocation_id) AS total_historical_allocations,
                SUM(CASE WHEN allocation_status = 'active' THEN 1 ELSE 0 END) AS active_allocations,
                SUM(CASE WHEN allocation_status = 'transferred' THEN 1 ELSE 0 END) AS transferred_allocations,
                SUM(CASE WHEN allocation_status = 'vacated' THEN 1 ELSE 0 END) AS vacated_allocations,
                MIN(stay_duration_days) AS min_stay_days,
                MAX(stay_duration_days) AS max_stay_days,
                ROUND(AVG(stay_duration_days), 1) AS avg_stay_days
            FROM v_allocation_history
            GROUP BY hostel_name
            ORDER BY total_historical_allocations DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_complaint_resolution_analysis():
        """Report 05: Complaint Resolution Analysis (Time Metrics & Resolution Rates)."""
        query = """
            SELECT 
                cc.category_id,
                cc.name AS category_name,
                COUNT(c.complaint_id) AS total_complaints,
                SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved_complaints,
                SUM(CASE WHEN c.status IN ('open', 'in_progress') THEN 1 ELSE 0 END) AS unresolved_complaints,
                CASE 
                    WHEN COUNT(c.complaint_id) = 0 THEN 0.00
                    ELSE ROUND((SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) / COUNT(c.complaint_id)) * 100.0, 2)
                END AS resolution_rate_pct,
                ROUND(AVG(TIMESTAMPDIFF(HOUR, c.filed_at, c.resolved_at)), 1) AS avg_resolution_time_hours
            FROM complaint_categories cc
            LEFT JOIN complaints c ON cc.category_id = c.category_id
            GROUP BY cc.category_id, cc.name
            ORDER BY total_complaints DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_maintenance_analysis():
        """Report 06: Maintenance Cost & Status Analysis (Financial Aggregations)."""
        query = """
            SELECT 
                hostel_name,
                category AS maintenance_category,
                COUNT(request_id) AS total_requests,
                SUM(CASE WHEN maintenance_status = 'completed' THEN 1 ELSE 0 END) AS completed_requests,
                SUM(CASE WHEN maintenance_status IN ('pending', 'assigned', 'in_progress') THEN 1 ELSE 0 END) AS pending_requests,
                COALESCE(SUM(cost), 0.00) AS total_maintenance_cost,
                COALESCE(ROUND(AVG(cost), 2), 0.00) AS avg_cost_per_request
            FROM v_maintenance_status
            GROUP BY hostel_name, category
            ORDER BY total_maintenance_cost DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_visitor_trends():
        """Report 07: Visitor Traffic & Gate Activity Trends."""
        query = """
            SELECT 
                COALESCE(hostel_name, 'Unallocated Resident') AS hostel_name,
                COUNT(visitor_id) AS total_visitors,
                SUM(CASE WHEN visitor_status = 'currently_checked_in' THEN 1 ELSE 0 END) AS currently_checked_in_visitors,
                SUM(CASE WHEN visitor_status = 'checked_out' THEN 1 ELSE 0 END) AS checked_out_visitors,
                ROUND(AVG(TIMESTAMPDIFF(MINUTE, check_in_time, check_out_time)), 1) AS avg_visit_duration_minutes
            FROM v_visitor_report
            GROUP BY hostel_name
            ORDER BY total_visitors DESC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_hostel_operational_summary():
        """Report 08: Cross-Domain Hostel Dashboard Summary (Multi-Domain Analytical Integration)."""
        query = """
            SELECT 
                h.name AS hostel_name,
                h.gender_type,
                COUNT(DISTINCT bd.bed_id) AS total_beds,
                SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) AS occupied_beds,
                CASE 
                    WHEN COUNT(DISTINCT bd.bed_id) = 0 THEN 0.00
                    ELSE ROUND((SUM(CASE WHEN bd.status = 'occupied' THEN 1 ELSE 0 END) / COUNT(DISTINCT bd.bed_id)) * 100.0, 2)
                END AS occupancy_pct,
                COALESCE(SUM(DISTINCT i.outstanding_balance), 0.00) AS total_outstanding_dues,
                (
                    SELECT COUNT(*) 
                    FROM v_unresolved_complaints uc 
                    JOIN students s ON uc.student_id = s.student_id
                    JOIN allocations a ON s.student_id = a.student_id AND a.status = 'active'
                    JOIN beds b2 ON a.bed_id = b2.bed_id
                    JOIN rooms r2 ON b2.room_id = r2.room_id
                    JOIN floors fl2 ON r2.floor_id = fl2.floor_id
                    JOIN blocks bl2 ON fl2.block_id = bl2.block_id
                    WHERE bl2.hostel_id = h.hostel_id
                ) AS unresolved_complaints_count,
                (
                    SELECT COUNT(*) 
                    FROM v_maintenance_status ms 
                    JOIN rooms r3 ON ms.room_id = r3.room_id
                    JOIN floors fl3 ON r3.floor_id = fl3.floor_id
                    JOIN blocks bl3 ON fl3.block_id = bl3.block_id
                    WHERE bl3.hostel_id = h.hostel_id AND ms.maintenance_status != 'completed'
                ) AS pending_maintenance_count
            FROM hostels h
            LEFT JOIN blocks b ON h.hostel_id = b.hostel_id
            LEFT JOIN floors fl ON b.block_id = fl.block_id
            LEFT JOIN rooms r ON fl.floor_id = r.floor_id
            LEFT JOIN beds bd ON r.room_id = bd.room_id
            LEFT JOIN allocations a ON bd.bed_id = a.bed_id AND a.status = 'active'
            LEFT JOIN invoices i ON a.student_id = i.student_id AND i.outstanding_balance > 0.00
            GROUP BY h.hostel_id, h.name, h.gender_type
            ORDER BY h.name ASC;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
