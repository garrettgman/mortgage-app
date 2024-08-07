# helpers.py
import pandas as pd
import plotnine as p9


def make_dates(start_date, term):

    # start_date = datetime.strptime(start, "%Y-%m-%d")

    # Determine the first day of the following month
    first_day_of_month = start_date.replace(day=1, month=start_date.month + 1)

    # Create list of payment dates
    n_months = term * 12
    dates_list = []

    for i in range(n_months):
        new_month = (first_day_of_month.month + i) % 12
        if new_month == 0:
            new_month = 12
        dates_list.append(first_day_of_month.replace(month = new_month))

    # Convert dates to strings in the format "YYYY-MM-DD"
    dates_list_str = [date.strftime("%Y-%m-%d") for date in dates_list]

    return dates_list_str

def make_amortization_table(amount, rate, term, start_date, payments = None, notes = None):

    # Calculate total number of payments
    n_payments = term * 12

    # Calculate monthly interest rate
    monthly_rate = rate / 12 / 100

    # Assemble payments schedule
    if payments is None:
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
        payments = [monthly_payment] * n_payments

    # Assemble notes field
    if notes is None:
        notes = [''] * n_payments
    
    # Initialize amortization table
    amortization_table = []
    
    # Initialize remaining balance
    remaining_balance = amount
    
    # Calculate each month's principal and interest
    for payment_number in range(1, n_payments + 1):
        if remaining_balance == 0:
            amortization_table.append([payment_number, 0, 0, 0, 0, notes[payment_number - 1]])
        elif payment_number == (n_payments):
            interest_payment = remaining_balance * monthly_rate
            payment = remaining_balance + interest_payment
            principal_payment = payment - interest_payment
            remaining_balance = max(0, remaining_balance - principal_payment)
            amortization_table.append([payment_number, payment, principal_payment, interest_payment, remaining_balance, notes[payment_number - 1]])
        elif payments[payment_number - 1] == 0:
            interest_payment = remaining_balance * monthly_rate
            remaining_balance += interest_payment
            amortization_table.append([payment_number, 0, 0, 0, remaining_balance, notes[payment_number - 1]])
        else:
            interest_payment = remaining_balance * monthly_rate
            payment = payments[payment_number - 1]
            principal_payment = payment - interest_payment
            remaining_balance = max(0, remaining_balance - principal_payment)
            amortization_table.append([payment_number, payment, principal_payment, interest_payment, remaining_balance, notes[payment_number - 1]])

    # Add dates column, and remove payment column

    # Create DataFrame for better visualization
    amortization_df = pd.DataFrame(
        amortization_table, 
        columns=['Payment', 'Amount', 'Principal Payment', 'Interest Payment', 'Remaining Balance', 'Notes']
    ).round(2)
    
    amortization_df["Date"] = make_dates(start_date, term)

    return amortization_df

def make_payment_schedule(amortization_table):
    return amortization_table[['Date', 'Amount', 'Notes']]

def calculate_total_paid(amortization_table):
    return amortization_table['Amount'].sum().round(2)

def calculate_interest_amount(amount_financed, total_paid):
    return (total_paid - amount_financed).round(2)

def calculate_percent_interest(amount_financed, total_paid):
    percent = (total_paid - amount_financed) / total_paid * 100
    return int(percent.round(0))

def plot_amount_paid_over_time(amortization_table, green, gold):
    amortization_table['Cumulative Principal'] = amortization_table['Principal Payment'].cumsum()
    amortization_table['Cumulative Interest'] = amortization_table['Interest Payment'].cumsum()

    cumulative_df = amortization_table[['Payment', 'Cumulative Principal', 'Cumulative Interest']]
    long_df = cumulative_df.melt(id_vars=['Payment'], value_vars=['Cumulative Principal', 'Cumulative Interest'], var_name='Payment Type', value_name='Amount')
    
    return (
        p9.ggplot(long_df, p9.aes(x="Payment", y="Amount", fill="Payment Type"))
        + p9.geom_area()
        + p9.scale_fill_manual(values=(green, gold))
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def plot_payment_composition_over_time(amortization_table, green, gold):
    payments_df = amortization_table[['Payment', 'Principal Payment', 'Interest Payment']]
    long_df = payments_df.melt(id_vars=['Payment'], value_vars=['Principal Payment', 'Interest Payment'], var_name='Payment Type', value_name='Amount')
    long_df = long_df[long_df['Amount'] != 0]

    return (
        p9.ggplot(long_df, p9.aes(x="Payment", y="Amount", fill="Payment Type"))
        + p9.geom_col(position="fill")
        + p9.scale_fill_manual(values=(green, gold))
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def cell_to_float(s):
    try:
        result = float(s)
    except ValueError:
        raise SafeException(
                "Amount values should be numbers."
            )
    else:
        return result