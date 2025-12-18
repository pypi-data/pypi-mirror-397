from pybos.services.account import AccountService
from pybos.services.admissions import AdmissionService
from pybos.services.masks import MaskService
from pybos.services.users import UserService
from pybos.services.orders import OrderService
from pybos.services.events import EventService
from pybos.services.performances import PerformanceService
from pybos.services.products import ProductService
from pybos.services.accountfinancial import AccountFinancialService
from pybos.services.adapter import AdapterService
from pybos.services.capacity import CapacityService
from pybos.services.delivery import DeliveryService
from pybos.services.donation import DonationService
from pybos.services.externalreservation import ExternalReservationService
from pybos.services.fair import FairService
from pybos.services.frictionless import FrictionlessService
from pybos.services.installment import InstallmentService
from pybos.services.invoice import InvoiceService
from pybos.services.moneycard import MoneyCardService
from pybos.services.other import OtherService
from pybos.services.pricelist import PriceListService
from pybos.services.promotion import PromotionService
from pybos.services.renewalplan import RenewalPlanService
from pybos.services.report import ReportService
from pybos.services.reservation import ReservationService
from pybos.services.resourcemanagement import ResourceManagementService
from pybos.services.seasonalprice import SeasonalPriceService
from pybos.services.seat import SeatService
from pybos.services.shopcartvalidation import ShopCartValidationService
from pybos.services.siaethirdpartyintegration import SiaeThirdPartyIntegrationService
from pybos.services.subscription import SubscriptionService
from pybos.services.ticket import TicketService
from pybos.services.thirdparty import ThirdPartyService
from pybos.services.upsell import UpsellService
from pybos.services.waitlistsubscription import WaitListSubscriptionService
from pybos.wsdl_services import SERVICES


class BOS:
    """
    An interface to the BOS API. This class is responsible for managing
    the basic interactions with the API.
    """

    SERVICES = SERVICES

    # Service instances
    accounts: AccountService
    admissions: AdmissionService
    masks: MaskService
    users: UserService
    orders: OrderService
    events: EventService
    performances: PerformanceService
    products: ProductService
    accountfinancial: AccountFinancialService
    adapter: AdapterService
    capacity: CapacityService
    delivery: DeliveryService
    donation: DonationService
    externalreservation: ExternalReservationService
    fair: FairService
    frictionless: FrictionlessService
    installment: InstallmentService
    invoice: InvoiceService
    moneycard: MoneyCardService
    other: OtherService
    pricelist: PriceListService
    promotion: PromotionService
    renewalplan: RenewalPlanService
    report: ReportService
    reservation: ReservationService
    resourcemanagement: ResourceManagementService
    seasonalprice: SeasonalPriceService
    seat: SeatService
    shopcartvalidation: ShopCartValidationService
    siaethirdpartyintegration: SiaeThirdPartyIntegrationService
    subscription: SubscriptionService
    ticket: TicketService
    thirdparty: ThirdPartyService
    upsell: UpsellService
    waitlistsubscription: WaitListSubscriptionService
    accountfinancial: AccountFinancialService
    adapter: AdapterService

    # Configuration
    isapi_url: str
    username: str
    workstation: str
    password: str
    api_key: str

    session_token: str

    def __init__(
        self,
        isapi_url: str,
        api_key: str,
        *args,
        **kwargs,
    ) -> None:
        self.isapi_url = isapi_url
        self.api_key = api_key

        # Initialize all service instances
        self.accounts = AccountService(self, "IWsAPIAccount")
        self.admissions = AdmissionService(self, "IWsAPIAdmission")
        self.masks = MaskService(self, "IWsAPIMask")
        self.users = UserService(self, "IWsAPIUser")
        self.orders = OrderService(self, "IWsAPIOrder")
        self.events = EventService(self, "IWsAPIEvent")
        self.performances = PerformanceService(self, "IWsAPIPerformance")
        self.products = ProductService(self, "IWsAPIProduct")
        self.accountfinancial = AccountFinancialService(self, "IWsAPIAccountFinancial")
        self.adapter = AdapterService(self, "IWsAPIAdapter")
        self.capacity = CapacityService(self, "IWsAPICapacity")
        self.delivery = DeliveryService(self, "IWsAPIDelivery")
        self.donation = DonationService(self, "IWsAPIDonation")
        self.externalreservation = ExternalReservationService(
            self, "IWsAPIExternalReservation"
        )
        self.fair = FairService(self, "IWsAPIFair")
        self.frictionless = FrictionlessService(self, "IWsAPIFrictionless")
        self.installment = InstallmentService(self, "IWsAPIInstallment")
        self.invoice = InvoiceService(self, "IWsAPIInvoice")
        self.moneycard = MoneyCardService(self, "IWsAPIMoneyCard")
        self.other = OtherService(self, "IWsAPIOther")
        self.pricelist = PriceListService(self, "IWsAPIPriceList")
        self.promotion = PromotionService(self, "IWsAPIPromotion")
        self.renewalplan = RenewalPlanService(self, "IWsAPIRenewalPlan")
        self.report = ReportService(self, "IWsAPIReport")
        self.reservation = ReservationService(self, "IWsAPIReservation")
        self.resourcemanagement = ResourceManagementService(
            self, "IWsAPIResourceManagement"
        )
        self.seasonalprice = SeasonalPriceService(self, "IWsAPISeasonalPrice")
        self.seat = SeatService(self, "IWsAPISeat")
        self.shopcartvalidation = ShopCartValidationService(
            self, "IWsAPIShopCartValidation"
        )
        self.siaethirdpartyintegration = SiaeThirdPartyIntegrationService(
            self, "IWsAPISiaeThirdPartyIntegration"
        )
        self.subscription = SubscriptionService(self, "IWsAPISubscription")
        self.ticket = TicketService(self, "IWsAPITicket")
        self.thirdparty = ThirdPartyService(self, "IWsAPIThirdParty")
        self.upsell = UpsellService(self, "IWsAPIUpsell")
        self.waitlistsubscription = WaitListSubscriptionService(
            self, "IWsAPIWaitListSubscription"
        )
        self.accountfinancial = AccountFinancialService(self, "IWsAPIAccountFinancial")
        self.adapter = AdapterService(self, "IWsAPIAdapter")

    def _build_soap_url(self, service: str) -> str:
        """Builds and returns the WSDL enpoint for the specified
        service. A list of services can be found in services.py"""
        return f"{self.isapi_url}{self.SERVICES[service]}"
