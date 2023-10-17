import enum
from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Float
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.decl_api import DeclarativeBase

from data_validation import email_validation, username_validation


class MergingMixin(object):
    def merge_fromdict(self, dict: dict):
        for key, value in dict.items():
            if value is not None:
                setattr(self, key, value)


class Base(DeclarativeBase):
    pass


class RoleEmployees(enum.Enum):
    commercial = 1
    support = 2
    gestion = 3


@dataclass
class Employee(Base, MergingMixin):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    username = Column(String(70), unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEmployees))

    @validates("username")
    def validate_username(self, key, value):
        is_valid, result = username_validation(value)
        if is_valid:
            return result
        else:
            raise ValueError(result)


@dataclass
class Client(Base, MergingMixin):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(70))
    lastname = Column(String(70), nullable=False)

    @hybrid_property
    def fullname(self):
        return self.firstname + " " + self.lastname

    email = Column(String)

    @validates("email")
    def validate_email(self, key, value):
        if value is None:
            return None
        if isinstance(value, str):
            is_valid, result = email_validation(value)
            if is_valid:
                return result
            else:
                raise ValueError(result)
        else:
            raise ValueError("Invalid type.")

    tel = Column(Integer)
    society_name = Column(String)
    created_date = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=False)
    commercial_employee_id = Column(
        Integer, ForeignKey("employee.id", ondelete="restrict")
    )
    commercial_employee = relationship(
        "Employee"
    )  # TODO Validate that employee is a commercial
    contracts = relationship("Contract", back_populates="client")


class ContractStatus(enum.Enum):
    pending = 1
    signed = 2
    archived = 3


@dataclass
class Contract(Base, MergingMixin):
    __tablename__ = "contract"
    id = Column(Integer, primary_key=True)
    client_id = Column(
        Integer, ForeignKey("client.id", ondelete="restrict"), nullable=False
    )
    client = relationship("Client", back_populates="contracts", uselist=False)
    total_amount = Column(Float)
    amount_to_pay = Column(Float)
    created_date = Column(DateTime, nullable=False)
    status = Column(Enum(ContractStatus))
    # indirect commercial_employee (= client.commercial_employee)
    associated_event = relationship("Event", back_populates="contract", uselist=False)

    # TODO : add a validator that verify total_amount > amount_to_pay


@dataclass
class Event(Base, MergingMixin):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    contrat_id = Column(
        Integer, ForeignKey("contract.id", ondelete="restrict"), nullable=False
    )
    contract = relationship(
        "Contract", back_populates="associated_event", uselist=False
    )
    datetime_start = Column(DateTime)
    datetime_end = Column(DateTime)
    location = Column(String)
    support_employee_id = Column(
        Integer, ForeignKey("employee.id", ondelete="restrict")
    )
    support_employee = relationship(
        "Employee"
    )  # TODO Validate that employee is a support
    attendees = Column(Integer)
    notes = Column(String)
    # indirect client (=contract.client)
