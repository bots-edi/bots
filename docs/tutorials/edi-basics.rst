EDI Basics
==========

A high level introduction to EDI - business process focused

High Level EDI Business Flow
----------------------------

    Various documents need to be exchanged during the lifecycle of a business transaction. A generic flow is shown below, this focuses on the business processes, not a particular EDI implementation (we'll get to that later).

    There may be other communication, for example business process/contracts may dictate that all changes are requested and approved by email prior to the ERP systems being modified.

    **Example Business Flow**

    * Buyer (customer) creates a purchase order (PO)
    * PO is sent to supplier via EDI
    * Supplier loads a Sale Order in response to the PO, with optional changes.
    * Supplier acknowledges PO (with any changes)
    * Buyer changes quantity of a line (part)
    * Buyer-initiated Change Request is sent to supplier via EDI
    * Supplier implements or rejects changes
    * Supplier sends summary of changes/rejects to buyer via EDI
    * Supplier needs to delete a line as they can no longer supply
    * Supplier sends supplier-initiated change request to buyer/customer via EDI
    * Buyer receives change request and implement or rejects changes
    * Supplier ships material
    * Supplier sends an Advance Ship Notice (shipping manifest) via EDI
    * Supplier sends invoice via EDI

Typical EDI Document Types
--------------------------

* **Purchase Order**

    The Purchase Order, or PO, is sent from buyer to supplier. It is similar to a paper purchase order.

    **Typical Contents**

    A PO sent to a supplier typically contains:

    * Customer Purchase Order (PO) Number
    * Line level information: part codes, quantities and prices
    * Delivery Schedule (due date)
    * Incoterms
    * Delivery and invoice addresses

    **Document Numbers**

    * ASC X12: 850
    * UN/EDIFACT: ORDERS
    * TRADACOMS: Order File

* **Purchase Order Acknowledgement**

    The Purchase Order Acknowledge is sent from supplier to buyer. It confirms acceptance of the buyer's Purchase Order along with any changes required by the supplier (for example pricing or scheduled delivery dates).

    **Typical Contents**

    A PO Acknowledgement sent to a buyer typically contains:

    * Customer Purchase Order (PO) Number
    * Line level information: part codes, quantities and prices
    * Delivery Schedule 

    **Document Numbers**

    * ASC X12: 855
    * UN/EDIFACT: ORDRSP
    * TRADACOMS: Acknowledgement of Order File

* **Purchase Order Change Request**

    Purchase Order Change Request documents may be sent from supplier to buyer (supplier initiated) or from buyer to supplier (buyer-initiated).

    **Typical Contents**

    * Original PO Number
    * Currency
    * Delivery and Invoice Addresses
    * Line(s) Add/Delete/Change code
    * Line part code, price, quantity and Unit of Measure codes

    **Document Numbers**

    * ASC X12: 860 (buyer initiated) and 865 (supplier initiated)
    * UN/EDIFACT: ORDCHG
    * TRADACOMS: ?

* **Advance Ship Notice(ASN)**

    The Advance Ship Notice, or ASN, electronically communicates the contents of a shipment to a trading partner. It is sent in advance of the shipment arriving at the partner’s facility, this gives the receiver time to arrange storage space or onward logistics.

    **Typical Contents**

    An ASN sent to a customer typically contains:

    * Customer Purchase Order (PO) Number
    * Carrier information, such as name and tracking/Airway Bill number
    * Estimated Time of Arrival
    * Line level information such as part codes and quantities
    * Item or pack level information such as serial numbers

    **Document Numbers**

    * ASC X12: 856
    * UN/EDIFACT: DESADV
    * TRADACOMS: Delivery Notification File

* **Invoice**

    The electronic Invoice document is similar to a paper invoice.

    **Typical Contents**

    An Invoice sent to a customer typically contains:

    * Customer Purchase Order (PO) Number
    * Estimated Time of Arrival
    * Line level information such as part codes, quantities, prices and taxes.
    * Untaxed, tax and total amounts
    * Invoice currency
    * Payment due date
    * Payment address

    **Document Numbers**

    * ASC X12: 810
    * UN/EDIFACT: INVOIC
    * TRADACOMS: Invoice File
