"""myDATA / ΑΑΔΕ invoicing provider interface.

This is a stub: the interface is defined so that later a real implementation
can be swapped in without changing any other code.
"""


class InvoicingProvider:
    """Abstract base for invoicing providers (ΑΑΔΕ myDATA, etc.)."""

    def submit_invoice(self, invoice_payload: dict) -> dict:
        raise NotImplementedError

    def get_status(self, submission_id: str) -> dict:
        raise NotImplementedError

    def cancel_invoice(self, mark: str) -> dict:
        raise NotImplementedError


class MyDataProviderStub(InvoicingProvider):
    """Stub implementation — replace with real AADE API calls later."""

    def submit_invoice(self, invoice_payload: dict) -> dict:
        # TODO: Real AADE myDATA API call + return MARK / status
        return {"status": "stub", "mark": None, "raw": None}

    def get_status(self, submission_id: str) -> dict:
        return {"status": "stub", "submission_id": submission_id}

    def cancel_invoice(self, mark: str) -> dict:
        return {"status": "stub", "mark": mark}


# singleton — swap class when you integrate the real provider
mydata_provider: InvoicingProvider = MyDataProviderStub()
