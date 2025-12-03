from sqlalchemy import Column, String, Integer, TIMESTAMP, text, Numeric, ForeignKey
from src.app.db.session import Base


class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    date = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )