from sqlalchemy import Column, String, Integer, DATE, Numeric, ForeignKey, UniqueConstraint
from src.app.db.session import Base


class Budgets(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(String, nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    month = Column(DATE, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "category", "month", name="user_category_month_unique"),
    )