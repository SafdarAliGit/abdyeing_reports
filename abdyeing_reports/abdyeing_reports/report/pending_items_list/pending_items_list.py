from frappe import _
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {
            "label": _("ID"),
            "fieldname": "id",
            "fieldtype": "Link",
            "options": "Gate Outward Pass",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("DC NO"),
            "fieldname": "dc_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Quantity"),
            "fieldname": "quantity",
            "fieldtype": "Float",
            "width": 100
        },
		{
			"label": _("Location"),
			"fieldname": "location",
			"fieldtype": "Data",
			"width": 150
		},
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 150
        }
    ]
    return columns

def get_data(filters):
    query = """
        SELECT 
            gi.name AS id, 
            gi.date AS transaction_date, 
            gi.dn_no AS dc_no, 
            go.item_code AS item_code, 
            go.qty AS quantity,
			go.machine AS location,
            go.remarks
        FROM 
            `tabGate Outward Pass Items` go
        LEFT JOIN 
            `tabGate Outward Pass` gi 
        ON 
            go.parent = gi.name
        WHERE 
            gi.returnable = 1 
            AND gi.docstatus = 1
            AND gi.name NOT IN (
                SELECT 
                    outward_no 
                FROM 
                    `tabGate Inward Pass` 
                WHERE 
                    outward_no IS NOT NULL 
                    AND docstatus = 1
            )
        ORDER BY 
            gi.date DESC
    """

    data = frappe.db.sql(query, as_dict=True)
    return data
