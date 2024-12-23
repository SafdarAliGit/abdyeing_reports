import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_data(filters=None):
    data = []
    sales_query = """
        SELECT 
            "" AS account,
            sii.item_code AS item_code,
            SUM(sii.qty) AS qty,
            SUM(sii.amount) AS amount,
            0 AS percent
        FROM
            `tabSales Invoice Item` AS sii
        JOIN 
            `tabSales Invoice` AS si 
            ON sii.parent = si.name
        WHERE
            si.docstatus = 1 
            AND si.is_return = 0
            AND si.posting_date >= %(from_date)s AND si.posting_date <= %(to_date)s
        GROUP BY 
            sii.item_code
    """

    sales_result = frappe.db.sql(
        sales_query,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    total_amount_item = sum(item["amount"] for item in sales_result)
    total_item = sum(item["qty"] for item in sales_result)
    # calculations for percent
    for item in sales_result:
        item["percent"] = (item["qty"] * 100) / total_item if total_item > 0 else 0
    # end
    items_heading = [{"account": "<b>ITEMS DETAIL</b>", "item_code": "", "qty": "", "amount": "","percent":""}]
    sales_result = items_heading + sales_result
    sales_result.append({"account": "", "item_code": "<b>Total</b>", "qty": total_item, "amount": total_amount_item, "percent":""})

    gle_query_income = """
            SELECT 
    gle.account AS account,
    "" AS item_code,
    "" AS qty,
    abs(SUM(gle.debit) - SUM(gle.credit)) AS amount,
    0 AS percent
    FROM 
        `tabGL Entry` AS gle
    WHERE 
        gle.account IN (
            SELECT name
            FROM `tabAccount`
            WHERE root_type IN ('Income')
        )
        AND gle.posting_date >= %(from_date)s AND gle.posting_date <= %(to_date)s
    GROUP BY 
        gle.account
        """
    gle_result_income = frappe.db.sql(
        gle_query_income,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    total_amount_income = 0
    total_amount_income = sum(item["amount"] for item in gle_result_income)
    # calculations for percent
    for item in gle_result_income:
        item["percent"] = (abs(item["amount"]) * 100) / abs(total_amount_income) if abs(total_amount_income) > 0 else 0
    # end
    income_heading = [{"account": "<b>INCOME DETAIL</b>", "item_code": "", "qty": "", "amount": "","percent":""}]
    gle_result_income = income_heading + gle_result_income
    gle_result_income.append({"account": "<b>Total</b>", "item_code": "", "qty": "", "amount": abs(total_amount_income), "percent":""})

    gle_query_expense = """
                SELECT 
        gle.account AS account,
        "" AS item_code,
        "" AS qty,
        (SUM(gle.debit) - SUM(gle.credit)) AS amount,
        0 AS percent
        FROM 
            `tabGL Entry` AS gle
        WHERE 
            gle.account IN (
                SELECT name
                FROM `tabAccount`
                WHERE root_type IN ('Expense')
            )
            AND gle.posting_date >= %(from_date)s AND gle.posting_date <= %(to_date)s
        GROUP BY 
            gle.account
            """
    gle_result_expense = frappe.db.sql(
        gle_query_expense,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    total_amount_expense = 0
    total_amount_expense = sum(item["amount"] for item in gle_result_expense)
    # calculations for percent
    for item in gle_result_expense:
        item["percent"] = abs(item["amount"] * 100) / abs(total_amount_expense) if abs(total_amount_expense) > 0 else 0
    # end
    expense_heading = [{"account": "<b>EXPENSE DETAIL</b>", "item_code": "", "qty": "", "amount": "","percent":""}]
    gle_result_expense = expense_heading + gle_result_expense
    gle_result_expense.append({"account": "<b>Total</b>", "item_code": "", "qty": "", "amount": total_amount_expense,"percent":""})


    profit_loss = total_amount_income - total_amount_expense
    profit_loss_heading = [{"account": "<b>PROFIT/LOSS</b>", "item_code": "", "qty": "", "amount": profit_loss,"percent":""}]


    data.extend(sales_result)
    data.extend(gle_result_income)
    data.extend(gle_result_expense)
    data.extend(profit_loss_heading)
    return data

def get_columns(filters):
    columns = [
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 300
        },
        {
            "label": _("Item Code"),
            "fieldtype": "Link",
            "fieldname": "item_code",
            "width": 200,
            "options": "Item"  # Corrected options
        },
        {
            "label": _("Qty"),
            "fieldtype": "Float",
            "fieldname": "qty",
            "width": 200
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Percent"),
            "fieldtype": "Percent",
            "fieldname": "percent",
            "width": 150
        }
    ]
    return columns
