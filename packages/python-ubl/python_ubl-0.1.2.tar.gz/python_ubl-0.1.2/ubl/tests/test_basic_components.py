"""
Unit tests for basic components (Amount, Quantity, Identifier, Code).
"""

import unittest
from decimal import Decimal

from ubl.constants import DEFAULT_CURRENCY_CODE, DEFAULT_UNIT_CODE, UNIT_CODE_LIST_ID
from ubl.exceptions import ValidationError
from ubl.models import Amount, Code, Identifier, Quantity


class TestAmount(unittest.TestCase):
    """Test the Amount basic component."""

    def test_create_amount_with_decimal(self):
        """Test creating an Amount with a Decimal value."""
        amount = Amount(value=Decimal("100.50"))
        self.assertEqual(amount.value, Decimal("100.50"))
        self.assertEqual(amount.currencyID, DEFAULT_CURRENCY_CODE)

    def test_create_amount_with_int(self):
        """Test creating an Amount with an int (auto-converted to Decimal)."""
        amount = Amount(value=100)
        self.assertEqual(amount.value, Decimal("100"))

    def test_create_amount_with_float(self):
        """Test creating an Amount with a float (auto-converted to Decimal)."""
        amount = Amount(value=100.50)
        self.assertEqual(amount.value, Decimal("100.50"))

    def test_create_amount_with_custom_currency(self):
        """Test creating an Amount with custom currency."""
        amount = Amount(value=Decimal("50.00"), currencyID="USD")
        self.assertEqual(amount.value, Decimal("50.00"))
        self.assertEqual(amount.currencyID, "USD")

    def test_amount_negative_value_allowed(self):
        """Test that negative amounts are allowed (for credit notes, returns)."""
        amount = Amount(value=Decimal("-10.00"))
        self.assertEqual(amount.value, Decimal("-10.00"))

    def test_amount_is_mutable_but_should_be_treated_as_immutable(self):
        """
        Note: Amount is not frozen due to inheritance constraints.

        While Amount can technically be modified, it should be treated
        as immutable in practice. This test documents that it's not frozen.
        """
        amount = Amount(value=Decimal("100.00"))

        # Not frozen, so this will work (but shouldn't be done in practice)
        amount.value = Decimal("200.00")
        self.assertEqual(amount.value, Decimal("200.00"))

    def test_amount_element_name(self):
        """Test that Amount has correct element name."""
        amount = Amount(value=Decimal("100.00"))
        self.assertEqual(amount.element_name, "Amount")

    def test_amount_custom_element_name(self):
        """Test that Amount element_name can be customized via subclassing."""

        class TaxAmount(Amount):
            pass

        amount = TaxAmount(value=Decimal("100.00"))
        self.assertEqual(amount.element_name, "TaxAmount")


class TestQuantity(unittest.TestCase):
    """Test the Quantity basic component."""

    def test_create_quantity_with_decimal(self):
        """Test creating a Quantity with a Decimal value."""
        quantity = Quantity(value=Decimal("5.0"))
        self.assertEqual(quantity.value, Decimal("5.0"))
        self.assertEqual(quantity.unitCode, DEFAULT_UNIT_CODE)
        self.assertEqual(quantity.unitCodeListID, UNIT_CODE_LIST_ID)

    def test_create_quantity_with_int(self):
        """Test creating a Quantity with an int (auto-converted to Decimal)."""
        quantity = Quantity(value=10)
        self.assertEqual(quantity.value, Decimal("10"))

    def test_create_quantity_with_custom_unit(self):
        """Test creating a Quantity with custom unit code."""
        quantity = Quantity(value=Decimal("2.5"), unitCode="KGM")  # Kilogram
        self.assertEqual(quantity.value, Decimal("2.5"))
        self.assertEqual(quantity.unitCode, "KGM")

    def test_quantity_is_mutable_but_should_be_treated_as_immutable(self):
        """
        Note: Quantity is not frozen due to inheritance constraints.

        While Quantity can technically be modified, it should be treated
        as immutable in practice. This test documents that it's not frozen.
        """
        quantity = Quantity(value=Decimal("10.0"))

        # Not frozen, so this will work (but shouldn't be done in practice)
        quantity.value = Decimal("20.0")
        self.assertEqual(quantity.value, Decimal("20.0"))

    def test_quantity_element_name(self):
        """Test that Quantity has correct element name."""
        quantity = Quantity(value=Decimal("5.0"))
        self.assertEqual(quantity.element_name, "Quantity")

    def test_quantity_custom_element_name(self):
        """Test that Quantity element_name can be customized via subclassing."""

        class InvoicedQuantity(Quantity):
            pass

        quantity = InvoicedQuantity(value=Decimal("5.0"))
        self.assertEqual(quantity.element_name, "InvoicedQuantity")


class TestIdentifier(unittest.TestCase):
    """Test the Identifier basic component."""

    def test_create_identifier(self):
        """Test creating a simple Identifier."""
        identifier = Identifier(value="BE0597601756")
        self.assertEqual(identifier.value, "BE0597601756")
        self.assertIsNone(identifier.schemeID)

    def test_create_identifier_with_scheme(self):
        """Test creating an Identifier with scheme."""
        identifier = Identifier(value="BE0597601756", schemeID="BE:VAT")
        self.assertEqual(identifier.value, "BE0597601756")
        self.assertEqual(identifier.schemeID, "BE:VAT")

    def test_identifier_is_mutable_but_should_be_treated_as_immutable(self):
        """
        Note: Identifier is not frozen due to inheritance constraints.

        While Identifier can technically be modified, it should be treated
        as immutable in practice. This test documents that it's not frozen.
        """
        identifier = Identifier(value="test")

        # Not frozen, so this will work (but shouldn't be done in practice)
        identifier.value = "new_value"
        self.assertEqual(identifier.value, "new_value")

    def test_identifier_equality_case_insensitive(self):
        """Test that Identifier equality is case-insensitive."""
        id1 = Identifier(value="BE0597601756", schemeID="BE:VAT")
        id2 = Identifier(value="be0597601756", schemeID="BE:VAT")

        self.assertEqual(id1, id2)

    def test_identifier_equality_different_schemes(self):
        """Test that Identifiers with different schemes are not equal."""
        id1 = Identifier(value="0597601756", schemeID="BE:VAT")
        id2 = Identifier(value="0597601756", schemeID="BE:EN")

        self.assertNotEqual(id1, id2)

    def test_identifier_hash_for_sets(self):
        """Test that Identifiers can be used in sets (hashable)."""
        id1 = Identifier(value="BE0597601756", schemeID="BE:VAT")
        id2 = Identifier(value="be0597601756", schemeID="BE:VAT")  # Same, different case

        identifier_set = {id1, id2}
        # Should be deduplicated to one item
        self.assertEqual(len(identifier_set), 1)

    def test_identifier_element_name(self):
        """Test that Identifier has correct element name."""
        identifier = Identifier(value="test")
        self.assertEqual(identifier.element_name, "ID")

    def test_identifier_custom_element_name(self):
        """Test that Identifier element_name can be customized via subclassing."""

        class EndpointID(Identifier):
            # Need to override since Identifier.element_name returns "ID"
            @property
            def element_name(self) -> str:
                return self.__class__.__name__

        identifier = EndpointID(value="test")
        self.assertEqual(identifier.element_name, "EndpointID")


class TestCode(unittest.TestCase):
    """Test the Code basic component."""

    def test_create_code(self):
        """Test creating a simple Code."""
        code = Code(value="S")
        self.assertEqual(code.value, "S")
        self.assertIsNone(code.listID)
        self.assertIsNone(code.listAgencyID)

    def test_create_code_with_list_metadata(self):
        """Test creating a Code with list metadata."""
        code = Code(value="S", listID="UNCL5305", listAgencyID="6")
        self.assertEqual(code.value, "S")
        self.assertEqual(code.listID, "UNCL5305")
        self.assertEqual(code.listAgencyID, "6")

    def test_code_is_mutable_but_should_be_treated_as_immutable(self):
        """
        Note: Code is not frozen due to inheritance constraints.

        While Code can technically be modified, it should be treated
        as immutable in practice. This test documents that it's not frozen.
        """
        code = Code(value="S")

        # Not frozen, so this will work (but shouldn't be done in practice)
        code.value = "Z"
        self.assertEqual(code.value, "Z")

    def test_code_element_name(self):
        """Test that Code has correct element name."""
        code = Code(value="S")
        self.assertEqual(code.element_name, "Code")

    def test_code_custom_element_name(self):
        """Test that Code element_name can be customized via subclassing."""

        class PaymentMeansCode(Code):
            pass

        code = PaymentMeansCode(value="31")
        self.assertEqual(code.element_name, "PaymentMeansCode")


if __name__ == "__main__":
    unittest.main()
