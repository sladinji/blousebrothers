from django.utils.translation import ugettext_lazy as _

# Users
NATURAL_USER = "N"
BUSINESS = "B"
ORGANIZATION = "O"

USER_TYPE_CHOICES = (
    (NATURAL_USER, _("Natural User")),
    (BUSINESS, "BUSINESS"),
    (ORGANIZATION, "ORGANIZATION"),
)

USER_TYPE_CHOICES_DICT = dict(USER_TYPE_CHOICES)

# Income range choices are given per month in euro
INCOME_RANGE_CHOICES = (
    (1, "0 - 1,500"),
    (2, "1,500 - 2,499"),
    (3, "2,500 - 3,999"),
    (4, "4,000 - 7,499"),
    (5, "7,500 - 9,999"),
    (6, "10,000 +"),
)

# Document types
IDENTITY_PROOF = "IP"
REGISTRATION_PROOF = "RP"
ARTICLES_OF_ASSOCIATION = "AA"
SHAREHOLDER_DECLARATION = "SD"
ADDRESS_PROOF = "AP"

DOCUMENT_TYPE_CHOICES = (
    (IDENTITY_PROOF, "IDENTITY_PROOF"),
    (REGISTRATION_PROOF, "REGISTRATION_PROOF"),
    (ARTICLES_OF_ASSOCIATION, "ARTICLES_OF_ASSOCIATION"),
    (SHAREHOLDER_DECLARATION, "SHAREHOLDER_DECLARATION"),
    (ADDRESS_PROOF, "ADDRESS_PROOF"),
)

DOCUMENT_TYPE_CHOICES_DICT = dict(DOCUMENT_TYPE_CHOICES)

# Document statuses
CREATED = "C"
VALIDATION_ASKED = "A"
VALIDATED = "V"
REFUSED = "R"

STATUS_CHOICES = (
    (CREATED, "CREATED"),
    (VALIDATION_ASKED, "VALIDATION_ASKED"),
    (VALIDATED, "VALIDATED"),
    (REFUSED, "REFUSED"),
)

# Bank account types
BA_BIC_IBAN = "BI"
BA_US = "US"
BA_UK = "UK"  # Not Implemented
BA_CA = "CA"  # Not Implemented
BA_OTHER = "O"
BA_NOT_IMPLEMENTED = (
    BA_UK,
    BA_CA
)

MANGOPAY_BANKACCOUNT_TYPE = (
    (BA_BIC_IBAN, _('BIC & IBAN')),
    (BA_US, _('Local US Format')),
    (BA_OTHER, _('Other')),
)

DEPOSIT_CHECKING = "CHECKING"
DEPOSIT_SAVINGS = "SAVINGS"

BA_US_DEPOSIT_ACCOUNT_TYPES = (
    # Options provided by MangoPay
    (DEPOSIT_CHECKING, _('Checking')),
    (DEPOSIT_SAVINGS, _('Savings'))
)


STATUS_CHOICES_DICT = {v: k for k, v in dict(STATUS_CHOICES).items()}

# Transaction statuses
PENDING = "CREATED"
SUCCEEDED = "SUCCEEDED"
FAILED = "FAILED"

TRANSACTION_STATUS_CHOICES = (
    (PENDING, _("The request is created but not processed.")),
    (SUCCEEDED, _("The request has been successfully processed.")),
    (FAILED, _("The request has failed.")),
)

# Pay in types
CARD_WEB = "card-web"
BANK_WIRE = "bank-wire"

MANGOPAY_PAYIN_CHOICES = (
    (BANK_WIRE, _("Pay in by BankWire")),
    (CARD_WEB, _("Pay in by card via web"))
)

ERROR_MESSAGES = (
    ("001999", _("Generic Operation error")),
    ("001001", _("Insufficient wallet balance")),
    ("001002", _("Author is not the wallet owner")),
    ("001011", _("Transaction amount is higher than maximum permitted amount")),
    ("001012", _("Transaction amount is lower than minimum permitted amount")),
    ("001013", _("Invalid transaction amount")),
    ("001014", _("Credited Funds must be more than 0")),

    ("001030", _("User has not been redirected")),
    ("001031", _("User canceled the payment")),

    ("001401", _("Transaction has already been successfully refunded")),
    ("005403", _("The refund cannot exceed initial transaction amount")),
    ("005404", _("The refunded fees cannot exceed initial fee amount")),
    ("005405", _("Balance of client fee wallet insufficient")),
    ("005407", _("Duplicate operation: you cannot refund the same amount more"
                 " than once for a transaction during the same day.")),
    ("105101", _("Invalid card number")),
    ("105102", _("Invalid cardholder name")),
    ("105103", _("Invalid PIN code")),
    ("105104", _("Invalid PIN format")),
    ("105299", _("Token input Error")),
    ("105202", _("Card number: invalid format")),
    ("105203", _("Expiry date: missing or invalid format")),
    ("105204", _("CSC: missing or invalid format")),
    ("105205", _("Callback URL: Invalid format")),
    ("105206", _("Registration data : Invalid format")),
    ("101001", _("The user did not complete the transaction")),
    ("101002", _("The transaction has been cancelled by the user")),
    ("001032", _("User is filling in the payment card details")),
    ("001033", _("User has not been redirected then the payment session has expired")),
    ("001034", _("User has let the payment session expire without paying")),

    ("101101", _("Transaction refused by the bank. "
                 "No more funds or limit has been reached")),
    ("101102", _("Transaction refused by the bank. "
                 "Amount limit has been reached")),
    ("101103", _("Transaction refused by the terminal")),
    ("101104", _("Transaction refused by the bank. "
                 "The card spent amount limit has been reached")),
    ("101105", _("The card has expired")),
    ("101106", _("The card is inactive.")),
    ("101410", _("The card is not active")),
    ("101111", _("Maximum number of attempts reached. "
                 "Too much attempts for the same transaction")),
    ("101112", _("Maximum amount exceeded. This is a card limitation on spent "
                 "amount")),
    ("101113", _("Maximum Uses Exceeded. Maximum attempts with this cards "
                 "reached. You must try again after 24 hours.")),
    ("101115", _("Debit limit exceeded. This is a card limitation on spent "
                 "amount")),
    ("101116", _("Amount limit. TThe contribution transaction has failed")),
    ("101119", _("Debit limit exceeded")),
    ("101199", _("Transaction refused. The transaction has been refused by the "
                 "bank. Contact your bank in order to have more information "
                 "about it.")),
    ("101399", _("Secure mode: 3DSecure authentication is not available")),
    ("101301", _("Secure mode: 3DSecure authentication has failed")),

    ("001599", _("Token processing error. The token has not been created")),
    ("101699", _("CardRegistration should return a valid JSON response")),
    ("002999", _("The user is blocked due to KYC limitation.")),
    ("008999", _("Fraud policy error")),
    ("008001", _("Counterfeit Card")),
    ("008002", _("Lost Card. A 'lost card' error is a rule carried by the bank"
                 " which deactivates a card due to too many payments or "
                 "attempts.")),
    ("008003", _("Stolen Card. A 'lost card' error is a rule carried by the bank"
                 " which deactivates a card due to too many payments or "
                 "attempts.")),
    ("008004", _("Card bin not authorized")),
    ("008005", _("Security violation")),
    ("008006", _("Fraud suspected by the bank")),
    ("008007", _("Opposition on bank account")),
    ("008500", _("Transaction blocked by Fraud Policy")),
    ("008600", _("Wallet blocked by Fraud policy")),
    ("008700", _("User blocked by Fraud policy")),
    ("009103", _("PSP configuration error")),

    ("009199", _("PSP technical error. You could get this error if your card "
                 " is not supported by the payment service provider, or if the "
                 "amount is higher than the maximum amount per transaction")),
    ("009499", _("Bank technical error")),
    ("009999", _("Technical error")),

    ("02101", _("Internal Error. There is an issue on the tokenization server (PSP side)")),
    ("02632", _("Method GET is not allowed")),


    ("09101", _("Username/Password is incorrect")),
    ("09102", _("Account is locked or inactive")),
    ("01902", _("This card is not active")),
    ("02624", _("Card expired")),

    ("09104", _("Client certificate is disabled")),
    ("09201", _("You do not have permissions to make this API call")),

    ("02631", _("Too much time taken from the creation of the CardRegistration object to the submission of the Card Details on the Tokenizer Server")),

    ("02625", _("Invalid card number")),
    ("02626", _("Invalid date format")),
    ("02627", _("Invalid CSC number")),
    ("02628", _("Transaction refused"))
)

ERROR_MESSAGES_DICT = dict(ERROR_MESSAGES)

COUNTRY_CHOICES = (
    ('AF', _('Afghanistan')),
    ('AX', _('\xc5land Islands')),
    ('AL', _('Albania')),
    ('DZ', _('Algeria')),
    ('AS', _('American Samoa')),
    ('AD', _('Andorra')),
    ('AO', _('Angola')),
    ('AI', _('Anguilla')),
    ('AQ', _('Antarctica')),
    ('AG', _('Antigua and Barbuda')),
    ('AR', _('Argentina')),
    ('AM', _('Armenia')),
    ('AW', _('Aruba')),
    ('AU', _('Australia')),
    ('AT', _('Austria')),
    ('AZ', _('Azerbaijan')),
    ('BS', _('Bahamas')),
    ('BH', _('Bahrain')),
    ('BD', _('Bangladesh')),
    ('BB', _('Barbados')),
    ('BY', _('Belarus')),
    ('BE', _('Belgium')),
    ('BZ', _('Belize')),
    ('BJ', _('Benin')),
    ('BM', _('Bermuda')),
    ('BT', _('Bhutan')),
    ('BO', _('Bolivia, Plurinational State of')),
    ('BQ', _('Bonaire, Sint Eustatius and Saba')),
    ('BA', _('Bosnia and Herzegovina')),
    ('BW', _('Botswana')),
    ('BV', _('Bouvet Island')),
    ('BR', _('Brazil')),
    ('IO', _('British Indian Ocean Territory')),
    ('BN', _('Brunei Darussalam')),
    ('BG', _('Bulgaria')),
    ('BF', _('Burkina Faso')),
    ('BI', _('Burundi')),
    ('KH', _('Cambodia')),
    ('CM', _('Cameroon')),
    ('CA', _('Canada')),
    ('CV', _('Cape Verde')),
    ('KY', _('Cayman Islands')),
    ('CF', _('Central African Republic')),
    ('TD', _('Chad')),
    ('CL', _('Chile')),
    ('CN', _('China')),
    ('CX', _('Christmas Island')),
    ('CC', _('Cocos (Keeling) Islands')),
    ('CO', _('Colombia')),
    ('KM', _('Comoros')),
    ('CG', _('Congo')),
    ('CD', _('Congo, The Democratic Republic of the')),
    ('CK', _('Cook Islands')),
    ('CR', _('Costa Rica')),
    ('CI', _("C\xf4te D'ivoire")),
    ('HR', _('Croatia')),
    ('CU', _('Cuba')),
    ('CW', _('Cura\xe7ao')),
    ('CY', _('Cyprus')),
    ('CZ', _('Czech Republic')),
    ('DK', _('Denmark')),
    ('DJ', _('Djibouti')),
    ('DM', _('Dominica')),
    ('DO', _('Dominican Republic')),
    ('EC', _('Ecuador')),
    ('EG', _('Egypt')),
    ('SV', _('El Salvador')),
    ('GQ', _('Equatorial Guinea')),
    ('ER', _('Eritrea')),
    ('EE', _('Estonia')),
    ('ET', _('Ethiopia')),
    ('FK', _('Falkland Islands (Malvinas)')),
    ('FO', _('Faroe Islands')),
    ('FJ', _('Fiji')),
    ('FI', _('Finland')),
    ('FR', _('France')),
    ('GF', _('French Guiana')),
    ('PF', _('French Polynesia')),
    ('TF', _('French Southern Territories')),
    ('GA', _('Gabon')),
    ('GM', _('Gambia')),
    ('GE', _('Georgia')),
    ('DE', _('Germany')),
    ('GH', _('Ghana')),
    ('GI', _('Gibraltar')),
    ('GR', _('Greece')),
    ('GL', _('Greenland')),
    ('GD', _('Grenada')),
    ('GP', _('Guadeloupe')),
    ('GU', _('Guam')),
    ('GT', _('Guatemala')),
    ('GG', _('Guernsey')),
    ('GN', _('Guinea')),
    ('GW', _('Guinea-bissau')),
    ('GY', _('Guyana')),
    ('HT', _('Haiti')),
    ('HM', _('Heard Island and McDonald Islands')),
    ('VA', _('Holy See (Vatican City State)')),
    ('HN', _('Honduras')),
    ('HK', _('Hong Kong')),
    ('HU', _('Hungary')),
    ('IS', _('Iceland')),
    ('IN', _('India')),
    ('ID', _('Indonesia')),
    ('IR', _('Iran, Islamic Republic of')),
    ('IQ', _('Iraq')),
    ('IE', _('Ireland')),
    ('IM', _('Isle of Man')),
    ('IL', _('Israel')),
    ('IT', _('Italy')),
    ('JM', _('Jamaica')),
    ('JP', _('Japan')),
    ('JE', _('Jersey')),
    ('JO', _('Jordan')),
    ('KZ', _('Kazakhstan')),
    ('KE', _('Kenya')),
    ('KI', _('Kiribati')),
    ('KP', _("Korea, Democratic People's Republic of")),
    ('KR', _('Korea, Republic of')),
    ('KW', _('Kuwait')),
    ('KG', _('Kyrgyzstan')),
    ('LA', _("Lao People's Democratic Republic")),
    ('LV', _('Latvia')),
    ('LB', _('Lebanon')),
    ('LS', _('Lesotho')),
    ('LR', _('Liberia')),
    ('LY', _('Libya')),
    ('LI', _('Liechtenstein')),
    ('LT', _('Lithuania')),
    ('LU', _('Luxembourg')),
    ('MO', _('Macao')),
    ('MK', _('Macedonia, The Former Yugoslav Republic of')),
    ('MG', _('Madagascar')),
    ('MW', _('Malawi')),
    ('MY', _('Malaysia')),
    ('MV', _('Maldives')),
    ('ML', _('Mali')),
    ('MT', _('Malta')),
    ('MH', _('Marshall Islands')),
    ('MQ', _('Martinique')),
    ('MR', _('Mauritania')),
    ('MU', _('Mauritius')),
    ('YT', _('Mayotte')),
    ('MX', _('Mexico')),
    ('FM', _('Micronesia, Federated States of')),
    ('MD', _('Moldova, Republic of')),
    ('MC', _('Monaco')),
    ('MN', _('Mongolia')),
    ('ME', _('Montenegro')),
    ('MS', _('Montserrat')),
    ('MA', _('Morocco')),
    ('MZ', _('Mozambique')),
    ('MM', _('Myanmar')),
    ('NA', _('Namibia')),
    ('NR', _('Nauru')),
    ('NP', _('Nepal')),
    ('NL', _('Netherlands')),
    ('NC', _('New Caledonia')),
    ('NZ', _('New Zealand')),
    ('NI', _('Nicaragua')),
    ('NE', _('Niger')),
    ('NG', _('Nigeria')),
    ('NU', _('Niue')),
    ('NF', _('Norfolk Island')),
    ('MP', _('Northern Mariana Islands')),
    ('NO', _('Norway')),
    ('OM', _('Oman')),
    ('PK', _('Pakistan')),
    ('PW', _('Palau')),
    ('PS', _('Palestinian Territory, Occupied')),
    ('PA', _('Panama')),
    ('PG', _('Papua New Guinea')),
    ('PY', _('Paraguay')),
    ('PE', _('Peru')),
    ('PH', _('Philippines')),
    ('PN', _('Pitcairn')),
    ('PL', _('Poland')),
    ('PT', _('Portugal')),
    ('PR', _('Puerto Rico')),
    ('QA', _('Qatar')),
    ('RE', _('R\xe9union')),
    ('RO', _('Romania')),
    ('RU', _('Russian Federation')),
    ('RW', _('Rwanda')),
    ('BL', _('Saint Barth\xe9lemy')),
    ('SH', _('Saint Helena, Ascension and Tristan Da Cunha')),
    ('KN', _('Saint Kitts and Nevis')),
    ('LC', _('Saint Lucia')),
    ('MF', _('Saint Martin (French Part)')),
    ('PM', _('Saint Pierre and Miquelon')),
    ('VC', _('Saint Vincent and the Grenadines')),
    ('WS', _('Samoa')),
    ('SM', _('San Marino')),
    ('ST', _('Sao Tome and Principe')),
    ('SA', _('Saudi Arabia')),
    ('SN', _('Senegal')),
    ('RS', _('Serbia')),
    ('SC', _('Seychelles')),
    ('SL', _('Sierra Leone')),
    ('SG', _('Singapore')),
    ('SX', _('Sint Maarten (Dutch Part)')),
    ('SK', _('Slovakia')),
    ('SI', _('Slovenia')),
    ('SB', _('Solomon Islands')),
    ('SO', _('Somalia')),
    ('ZA', _('South Africa')),
    ('GS', _('South Georgia and the South Sandwich Islands')),
    ('SS', _('South Sudan')),
    ('ES', _('Spain')),
    ('LK', _('Sri Lanka')),
    ('SD', _('Sudan')),
    ('SR', _('Suriname')),
    ('SJ', _('Svalbard and Jan Mayen')),
    ('SZ', _('Swaziland')),
    ('SE', _('Sweden')),
    ('CH', _('Switzerland')),
    ('SY', _('Syrian Arab Republic')),
    ('TW', _('Taiwan, Province of China')),
    ('TJ', _('Tajikistan')),
    ('TZ', _('Tanzania, United Republic of')),
    ('TH', _('Thailand')),
    ('TL', _('Timor-leste')),
    ('TG', _('Togo')),
    ('TK', _('Tokelau')),
    ('TO', _('Tonga')),
    ('TT', _('Trinidad and Tobago')),
    ('TN', _('Tunisia')),
    ('TR', _('Turkey')),
    ('TM', _('Turkmenistan')),
    ('TC', _('Turks and Caicos Islands')),
    ('TV', _('Tuvalu')),
    ('UG', _('Uganda')),
    ('UA', _('Ukraine')),
    ('AE', _('United Arab Emirates')),
    ('GB', _('United Kingdom')),
    ('US', _('United States')),
    ('UM', _('United States Minor Outlying Islands')),
    ('UY', _('Uruguay')),
    ('UZ', _('Uzbekistan')),
    ('VU', _('Vanuatu')),
    ('VE', _('Venezuela, Bolivarian Republic of')),
    ('VN', _('Viet Nam')),
    ('VG', _('Virgin Islands, British')),
    ('VI', _('Virgin Islands, U.S.')),
    ('WF', _('Wallis and Futuna')),
    ('EH', _('Western Sahara')),
    ('YE', _('Yemen')),
    ('ZM', _('Zambia')),
    ('ZW', _('Zimbabwe')),
)


# List of ISO 13616-Compliant IBAN Countries
# Pulled from:
# http://www.swift.com/dsp/resources/documents/IBAN_Registry.pdf
# on July 23, 2015.
# Document Version 59, for August 2015

IBAN_COMPLIANT_COUNTRIES = (
    ('AX', _('\xc5land Islands')),
    ('AL', _('Albania')),
    ('AD', _('Andorra')),
    ('AT', _('Austria')),
    ('AZ', _('Republic of Azerbaijan')),
    ('BH', _('Bahrain')),
    ('BE', _('Belgium')),
    ('BA', _('Bosnia and Herzegovina')),
    ('BR', _('Brazil')),
    ('BG', _('Bulgaria')),
    ('CR', _('Costa Rica')),
    ('HR', _('Croatia')),
    ('CY', _('Cyprus')),
    ('CZ', _('Czech Republic')),
    ('DK', _('Denmark')),
    ('DO', _('Dominican Republic')),
    ('EE', _('Estonia')),
    ('FI', _('Finland')),
    ('FR', _('France')),
    ('GE', _('Georgia')),
    ('DE', _('Germany')),
    ('GI', _('Gibraltar')),
    ('GR', _('Greece')),
    ('GT', _('Guatemala')),
    ('HU', _('Hungary')),
    ('IS', _('Iceland')),
    ('IE', _('Ireland')),
    ('IL', _('Israel')),
    ('IT', _('Italy')),
    ('JO', _('Jordan')),
    ('KZ', _('Kazakhstan')),
    ('XK', _('Republic of Kosovo')),
    ('KW', _('Kuwait')),
    ('LV', _('Latvia')),
    ('LB', _('Lebanon')),
    ('LI', _('Principality of Liechtenstein')),
    ('LT', _('Lithuania')),
    ('LU', _('Luxembourg')),
    ('MK', _('Macedonia, Former Yugoslav Republic of')),
    ('MT', _('Malta')),
    ('MR', _('Mauritania')),
    ('MU', _('Mauritius')),
    ('MD', _('Moldova')),
    ('MC', _('Monaco')),
    ('ME', _('Montenegro')),
    ('NL', _('The Netherlands')),
    ('NO', _('Norway')),
    ('PK', _('Pakistan')),
    ('PS', _('Palestine, State of')),
    ('PL', _('Poland')),
    ('PT', _('Portugal')),
    ('RO', _('Romania')),
    ('QA', _('Qatar')),
    ('LC', _('Saint Lucia')),
    ('SM', _('San Marino')),
    ('SA', _('Saudi Arabia')),
    ('RS', _('Serbia')),
    ('SK', _('Slovak Republic')),
    ('SI', _('Slovenia')),
    ('ES', _('Spain')),
    ('SE', _('Sweden')),
    ('CH', _('Switzerland')),
    ('TL', _('Timor-Leste')),
    ('TN', _('Tunisia')),
    ('TR', _('Turkey')),
    ('AE', _('United Arab Emirates')),
    ('GB', _('United Kingdom')),
    ('VG', _('Virgin Islands, British'))
)


IBAN_COMPLIANT_COUNTRY_CODES = [code for (code, name) in IBAN_COMPLIANT_COUNTRIES]
