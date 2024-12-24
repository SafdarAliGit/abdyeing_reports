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
            sii.item_code AS account,
            SUM(sii.qty) AS amount,
            0 AS percent
        FROM
            `tabSales Invoice Item` AS sii
        JOIN 
            `tabSales Invoice` AS si 
            ON sii.parent = si.name
        WHERE
            si.docstatus = 1 
            AND si.is_return = 0
            AND sii.item_group = 'Finish'
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

    # total_amount_item = sum(item["amount"] for item in sales_result)
    total_item = sum(item["amount"] for item in sales_result)
    # calculations for percent
    total_item_percent = 0
    for item in sales_result:
        item["percent"] = round((item["amount"] * 100) / total_item,2) if total_item > 0 else 0
        total_item_percent += item["percent"]
    # end
    # items_heading = [{"account": "<b>ITEMS DETAIL</b>", "amount": "","percent":""}]
    # sales_result = items_heading + sales_result
    sales_result.append({"account": "<b>ITEMS TOTAL</b>", "amount": total_item, "percent": total_item_percent})

    finish_sales_query = """
            SELECT 
                "" AS account,
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
                AND sii.item_group = 'Finish'
                AND si.posting_date >= %(from_date)s AND si.posting_date <= %(to_date)s
        """

    finish_sales_result = frappe.db.sql(
        finish_sales_query,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )
    finish_total_item = 0
    # total_amount_item = sum(item["amount"] for item in sales_result)
    finish_total_item = sum(item["amount"] for item in finish_sales_result if item["amount"])

    # calculations for percent
    total_finish_item_percent = 0
    # for item in sales_result:
    #     item["percent"] = round((item["amount"] * 100) / total_item, 2) if total_item > 0 else 0
    #     total_item_percent += item["percent"]
    # end
    # items_heading = [{"account": "<b>ITEMS DETAIL</b>", "amount": "","percent":""}]
    # sales_result = items_heading + sales_result
    finish_sales_row = {"account": "<b>Billing</b>", "amount": finish_total_item, "percent": ""}

    products_sales_query = """
                SELECT 
                    "" AS account,
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
                    AND sii.item_group = 'Products'
                    AND si.posting_date >= %(from_date)s AND si.posting_date <= %(to_date)s
            """

    products_sales_result = frappe.db.sql(
        products_sales_query,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    # total_amount_item = sum(item["amount"] for item in sales_result)
    products_total_item = 0
    products_total_item = sum(item["amount"] for item in products_sales_result if item["amount"])

    # calculations for percent
    total_finish_item_percent = 0
    # for item in sales_result:
    #     item["percent"] = round((item["amount"] * 100) / total_item, 2) if total_item > 0 else 0
    #     total_item_percent += item["percent"]
    # end
    # items_heading = [{"account": "<b>ITEMS DETAIL</b>", "amount": "","percent":""}]
    # sales_result = items_heading + sales_result
    products_sales_row = {"account": "<b>Rejected Fabric Sale</b>", "amount": products_total_item, "percent": ""}



    gle_query_indirect_income = """
                SELECT 
        gle.account AS account,
        abs(SUM(gle.debit) - SUM(gle.credit)) AS amount,
        0 AS percent
        FROM 
            `tabGL Entry` AS gle
        WHERE 
            gle.account IN (
                SELECT name
                FROM `tabAccount`
                WHERE parent_account = 'Indirect Income - ABD'
                AND root_type = 'Income'
            )
            AND gle.posting_date >= %(from_date)s AND gle.posting_date <= %(to_date)s
        GROUP BY 
            gle.account
            """
    gle_result_indirect_income = frappe.db.sql(
        gle_query_indirect_income,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    total_amount_indirect_income = 0
    total_amount_indirect_income = sum(item["amount"] for item in gle_result_indirect_income)
    total_income = finish_total_item + products_total_item + total_amount_indirect_income
    # calculations for percent
    total_direct_income_percent = 0
    total_indirect_income_percent = 0
    total_income_percent = 0
    # for item in gle_result_direct_income:
    #     item["percent"] = round((abs(item["amount"]) * 100) / abs(total_income),2) if abs(total_income) > 0 else 0
    #     total_direct_income_percent += item["percent"]
    for item in gle_result_indirect_income:
        item["percent"] = round((abs(item["amount"]) * 100) / abs(total_income),2) if abs(total_income) > 0 else 0
        total_indirect_income_percent += item["percent"]
    total_income_percent = total_direct_income_percent + total_indirect_income_percent
    # end
    # finish_percent = round((finish_total_item * 100) / abs(total_income),2) if abs(total_income) > 0 else 0
    # finish_sales_row['percent'] = finish_percent

    gle_result_indirect_income.append(
        {"account": "<b>TOTAL REVENUE</b>", "amount": abs(total_income),
         "percent": ""})

    gle_query_direct_expense = """
        SELECT 
        gle.account AS account,
        ABS(SUM(gle.debit) - SUM(gle.credit)) AS amount
        FROM 
            `tabGL Entry` AS gle
        WHERE 
            gle.account IN (
                SELECT name
                FROM `tabAccount`
                WHERE parent_account = 'Manufacturing Expense - ABD' 
                AND root_type = 'Expense'
            )
            AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s -- Add your desired date filters
        GROUP BY 
        gle.account
    """
    gle_result_direct_expense = frappe.db.sql(
        gle_query_direct_expense,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    # Initialize total amount
    total_amount_direct_expense = sum(item.get("amount", 0) for item in gle_result_direct_expense)

    # Calculate percentages
    total_direct_expense_percent = 0
    if total_amount_direct_expense > 0:
        for item in gle_result_direct_expense:
            item["percent"] = round((item["amount"] * 100) / total_amount_direct_expense,2) if total_amount_direct_expense > 0 else 0
            total_direct_expense_percent += item["percent"]
    else:
        for item in gle_result_direct_expense:
            item["percent"] = 0

    # Append the total heading
    direct_expense_heading = {
        "account": "<b>TOTAL DIRECT EXPENSES</b>",
        "amount": total_amount_direct_expense,
        "percent": total_direct_expense_percent
    }
    gle_result_direct_expense.append(direct_expense_heading)

    gle_query_indirect_expense = """
        SELECT 
            gle.account AS account,
            ABS(SUM(gle.debit) - SUM(gle.credit)) AS amount,
            0 AS percent
        FROM 
            `tabGL Entry` AS gle
        WHERE 
            gle.account IN (
                SELECT name
                FROM `tabAccount`
                WHERE parent_account = 'Indirect Expenses - ABD'
                AND root_type = 'Expense'
            )
            AND gle.posting_date >= %(from_date)s 
            AND gle.posting_date <= %(to_date)s
        GROUP BY 
            gle.account
    """
    gle_result_indirect_expense = frappe.db.sql(
        gle_query_indirect_expense,
        {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        },
        as_dict=True
    )

    # Calculate totals
    total_amount_indirect_expense = sum(item.get("amount", 0) for item in gle_result_indirect_expense)
    total_expense = total_amount_direct_expense + total_amount_indirect_expense

    # Initialize expense percentages
    total_direct_expense_percent = 0
    total_indirect_expense_percent = 0

    # Calculate percentage for direct expenses
    if total_expense > 0:
        for item in gle_result_direct_expense[:-1]:  # Exclude the last item
            item["percent"] = round((item["amount"] * 100) / total_expense, 2) if total_expense > 0 else 0
            total_direct_expense_percent += item["percent"]
        # Still calculate "percent" for the last item if needed
        gle_result_direct_expense[-1]["percent"] = round(
            (gle_result_direct_expense[-1]["amount"] * 100) / total_expense, 2)

    # Calculate percentage for indirect expenses
    if total_expense > 0:
        for item in gle_result_indirect_expense[:-1]:  # Exclude the last item
            item["percent"] = round((item["amount"] * 100) / total_expense, 2) if total_expense > 0 else 0
            total_indirect_expense_percent += item["percent"]
        # Still calculate "percent" for the last item if needed
        gle_result_indirect_expense[-1]["percent"] = round(
            (gle_result_indirect_expense[-1]["amount"] * 100) / total_expense, 2)

    # Append total indirect expenses
    gle_result_indirect_expense.append({
        "account": "<b>TOTAL INDIRECT EXPENSES</b>",
        "amount": total_amount_indirect_expense,
        "percent": total_indirect_expense_percent
    })

    # Combine total expense percentages
    total_expense_percent = total_direct_expense_percent + total_indirect_expense_percent
    profit_and_loss = total_income - total_expense
    total_expense_row =  {"account": "<b>TOTAL DIRECT & INDIRECT EXPENSES</b>","amount":total_expense ,"percent": total_expense_percent}
    profit_loss_heading =  {"account": "<b>PROFIT/LOSS</b>","amount":round(profit_and_loss,2) ,"percent": ""}

    data.extend(sales_result)
    data.append(finish_sales_row)
    data.append(products_sales_row)
    data.extend(gle_result_indirect_income)
    data.extend(gle_result_direct_expense)
    data.extend(gle_result_indirect_expense)
    data.append(total_expense_row)
    data.append(profit_loss_heading)
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
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Float",
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
