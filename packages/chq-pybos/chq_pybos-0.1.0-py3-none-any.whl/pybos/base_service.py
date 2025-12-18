import requests
from xmltodict import parse, unparse
from time import sleep
import html


class BaseService:
    """A base class that all service classes share.
    It is responsible for providing acess to the main
    BOS api class"""

    bos_api: "BOS"
    wsdl_service: str

    BASE_REQUEST_ENVELOPE = """<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:WsAPIUserIntf-IWsAPIUser">
        <soapenv:Header/>
        <soapenv:Body>
            {}
        </soapenv:Body>
        </soapenv:Envelope>"""

    def __init__(self, bos: "BOS", wsdl_service: str) -> None:
        self.bos_api = bos
        self.wsdl_service = wsdl_service

    def _build_soap_url(self) -> str:
        """Builds and returns the WSDL endpoint for this service"""
        return self.bos_api._build_soap_url(self.wsdl_service)

    @staticmethod
    def _escape_xml_string(value: str) -> str:
        """Escape XML special characters in a string.

        Escapes the following characters as required for well-formed XML:
        - & -> &amp;
        - < -> &lt;
        - > -> &gt;
        - ' -> &apos;
        - " -> &quot;

        Args:
            value: The string to escape

        Returns:
            The escaped string safe for XML

        Example:
            >>> BaseService._escape_xml_string("Company & Co. <special>")
            'Company &amp; Co. &lt;special&gt;'
        """
        if not isinstance(value, str):
            return value

        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;")
        )

    def _escape_xml_data(self, data):
        """Recursively escape XML special characters in data structures.

        Args:
            data: The data structure to escape (dict, list, str, or other)

        Returns:
            The data structure with all string values escaped

        Example:
            >>> service._escape_xml_data({"name": "John & Jane", "desc": "A <special> company"})
            {"name": "John &amp; Jane", "desc": "A &lt;special&gt; company"}
        """
        if isinstance(data, str):
            return self._escape_xml_string(data)
        elif isinstance(data, dict):
            return {key: self._escape_xml_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._escape_xml_data(item) for item in data]
        else:
            return data

    def send_request(self, payload: dict, header={}) -> requests.Response:
        """Sends a request to the BOS API and returns the response"""
        header["OvwSessionId"] = self.bos_api.api_key
        header["Content-Type"] = "application/xml"

        # Escape XML special characters in the payload
        escaped_payload = self._escape_xml_data(payload)

        response = requests.post(
            self._build_soap_url(),
            data=self.BASE_REQUEST_ENVELOPE.format(
                unparse(escaped_payload, full_document=False)
            ).encode("utf-8"),
            headers=header,
        )
        return parse(response.content)["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]
