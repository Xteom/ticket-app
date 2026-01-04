from dataclasses import dataclass
from datetime import datetime


@dataclass
class TSVRow:
    date: str
    account: str
    category: str
    subcategory: str
    note: str          # item name
    amount: float
    income_expense: str = "Expense"
    description: str = ""


def today_mmddyyyy() -> str:
    return datetime.now().strftime("%m/%d/%Y")


def to_tsv(rows: list[TSVRow]) -> str:
    header = "Date\tAccount\tCategory\tSubcategory\tNote\tAmount\tIncome/Expense\tDescription"
    lines = [header]
    for r in rows:
        lines.append(
            f"{r.date}\t{r.account}\t{r.category}\t{r.subcategory}\t{r.note}\t{r.amount}\t{r.income_expense}\t{r.description}"
        )
    return "\n".join(lines) + "\n"
