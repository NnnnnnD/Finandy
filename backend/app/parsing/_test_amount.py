from app.parsing.amount_parser import parse_amount

tests = [
    "beli kopi 25rb",
    "makan 40 rb",
    "gaji 1jt",
    "bonus 2.5jt",
    "transfer 1.200.000",
    "bensin 70000",
]

for t in tests:
    print(t, "=>", parse_amount(t))
