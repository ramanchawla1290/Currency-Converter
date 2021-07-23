"""
CURRENCY CONVERTOR with GUI

GUI Implementation of currency convertor using 'tkinter'


===========================================================
Base Module : currency_converter.py

API Used : https://rapidapi.com/fyhao/api/currency-exchange

Developer : Raman Chawla
"""

import tkinter as tk

from tkinter import ttk

import currency_converter as CC


try:
    cc = CC.CurrencyConverter()
    currencies = cc.get_available_currencies()
    currency_codes = tuple(currencies.keys())
except CC.CurrencyConverterException as cce:
    print(str(cce))
    exit(1)


FONT = ("Calibri", "10")
last_amount = "1.00"


def amount_tracer(*args):
    """Tracer function for amount; Validates amount as numbers only"""
    new_amount = amount.get()
    global last_amount

    if new_amount == "":
        last_amount = "1.00"
        return

    try:
        float(new_amount)
    except ValueError:
        amount.set(last_amount)
    else:
        last_amount = new_amount


def convert():
    """Callback for 'Convert' Button; Performs currency conversion"""
    amt = amount.get().strip()
    source_curr = cb_source.get().strip()
    target_curr = cb_target.get().strip()

    if len(amt) == 0:
        amt = "1.00"
    elif float(amt) == 0:
        amt = "1.00"

    amt = str(float(amt))  # removing leading zeroes
    amount.set(amt)

    if source_curr not in currency_codes or target_curr not in currency_codes:
        result.set("Select Both Currencies!")
        label_result['fg'] = 'red'
        label_result['font'] = FONT
        button_convert.flash()
        return
    elif source_curr == target_curr:
        result.set("Same currencies selected!")
        label_result['fg'] = 'red'
        label_result['font'] = FONT
    else:
        val = cc.convert(source_curr, target_curr, amt)
        result.set(f"{amt} {source_curr} = {val} {target_curr}")
        label_result['fg'] = 'darkblue'
        label_result['font'] = FONT + ("bold",)


def currency_code_tracer(*args):
    """Tracer function for currency codes Comboboxes; Updates currency name labels"""
    for var, label_var in zip((code_source, code_target), (source_currency, target_currency)):
        code = var.get()
        if code in currency_codes:
            label_var.set(currencies[code])
        else:
            label_var.set("")


# GUI Design
window = tk.Tk()
window.title("Currency Converter")
window.resizable(height=False, width=False)

# HEADING LABEL
heading = tk.Label(text="Currency Converter", font=("Calibri", "16", "underline"),
                   justify=tk.CENTER, padx=16, pady=16, bg="white")
heading.pack(fill=tk.X)


# INPUT FIELDS : Amount, From Currency, To Currency
input_frame = tk.Frame(window, padx=16, pady=16)

# LEFT Section : AMOUNT
amount = tk.StringVar()
amount.set("1.00")
amount.trace_add("write", amount_tracer)

label_amount = tk.Label(input_frame, text="Amount", font=FONT)
label_amount.grid(row=1, column=0, padx=2, ipadx=8)

entry_amount = tk.Entry(input_frame, justify=tk.RIGHT, width=8,
                        textvariable=amount)
entry_amount.grid(row=1, column=1)

# CENTER Section : FROM Currency
input_center_frame = tk.Frame(input_frame, padx=8, pady=4)

label_from = tk.Label(input_center_frame, text="From", font=FONT)
label_from.grid(row=0, column=0, pady=4)

code_source = tk.StringVar()

cb_source = ttk.Combobox(input_center_frame, textvariable=code_source)
cb_source["values"] = ("---Select---",) + currency_codes
cb_source.current(0)
cb_source.grid(row=1, column=0)

source_currency = tk.StringVar()

label_from_fullname = tk.Label(input_center_frame, textvariable=source_currency,
                               font=FONT, fg="darkblue")
label_from_fullname.grid(row=2, column=0)

input_center_frame.grid(row=0, column=2, rowspan=3)

# RIGHT Section : TO Currency
label_to = tk.Label(input_frame, text="To", font=FONT)
label_to.grid(row=0, column=3, pady=4)

code_target = tk.StringVar()

cb_target = ttk.Combobox(input_frame, textvariable=code_target)
cb_target["values"] = ("---Select---",) + currency_codes
cb_target.current(0)
cb_target.grid(row=1, column=3)

target_currency = tk.StringVar()

label_to_fullname = tk.Label(input_frame, textvariable=target_currency,
                             font=FONT, fg="darkblue")
label_to_fullname.grid(row=2, column=3)

code_target.trace_add("write", currency_code_tracer)
code_source.trace_add("write", currency_code_tracer)

input_frame.pack()  # Packing INPUT FIELDS input_frame


# RESULT LABEL and CONVERT BUTTON
bottom_frame = tk.Frame(window, padx=8, pady=8)

result = tk.StringVar()

label_result = tk.Label(bottom_frame, textvariable=result,  # width=48,
                        anchor=tk.W, font=FONT)
label_result.pack(fill=tk.X, side=tk.LEFT)

button_convert = tk.Button(bottom_frame, text="Convert", command=convert,
                           anchor=tk.E, bg="blue", fg="white", font=FONT,
                           padx=16, pady=8)
button_convert.pack(side=tk.RIGHT)

bottom_frame.pack(fill=tk.X)

# Launch GUI
window.mainloop()

print(__doc__)
