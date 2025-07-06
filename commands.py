# seeder.py

import os
from app import db, app
from models import Nationality

# قائمة بالجنسيات (يمكنك وضعها هنا أو استيرادها من ملف آخر)

NATIONALITIES_LIST = [
    {"name_ar": "آيسلندي", "name_en": "Icelandic", "country_code": "ISL"},
    {"name_ar": "أذربيجاني", "name_en": "Azerbaijani", "country_code": "AZE"},
    {"name_ar": "أردني", "name_en": "Jordanian", "country_code": "JOR"},
    {"name_ar": "أرجنتيني", "name_en": "Argentine", "country_code": "ARG"},
    {"name_ar": "أرميني", "name_en": "Armenian", "country_code": "ARM"},
    {"name_ar": "إريتري", "name_en": "Eritrean", "country_code": "ERI"},
    {"name_ar": "إسباني", "name_en": "Spanish", "country_code": "ESP"},
    {"name_ar": "أسترالي", "name_en": "Australian", "country_code": "AUS"},
    {"name_ar": "إستوني", "name_en": "Estonian", "country_code": "EST"},
    {"name_ar": "إسرائيلي", "name_en": "Israeli", "country_code": "ISR"},
    {"name_ar": "أفغاني", "name_en": "Afghan", "country_code": "AFG"},
    {"name_ar": "إكوادوري", "name_en": "Ecuadorian", "country_code": "ECU"},
    {"name_ar": "ألباني", "name_en": "Albanian", "country_code": "ALB"},
    {"name_ar": "ألماني", "name_en": "German", "country_code": "DEU"},
    {"name_ar": "إماراتي", "name_en": "Emirati", "country_code": "ARE"},
    {"name_ar": "أمريكي", "name_en": "American", "country_code": "USA"},
    {"name_ar": "أندوري", "name_en": "Andorran", "country_code": "AND"},
    {"name_ar": "إندونيسي", "name_en": "Indonesian", "country_code": "IDN"},
    {"name_ar": "أنغولي", "name_en": "Angolan", "country_code": "AGO"},
    {"name_ar": "أوروغواياني", "name_en": "Uruguayan", "country_code": "URY"},
    {"name_ar": "أوزبكي", "name_en": "Uzbek", "country_code": "UZB"},
    {"name_ar": "أوغندي", "name_en": "Ugandan", "country_code": "UGA"},
    {"name_ar": "أوكراني", "name_en": "Ukrainian", "country_code": "UKR"},
    {"name_ar": "إيراني", "name_en": "Iranian", "country_code": "IRN"},
    {"name_ar": "أيرلندي", "name_en": "Irish", "country_code": "IRL"},
    {"name_ar": "إيطالي", "name_en": "Italian", "country_code": "ITA"},
    {"name_ar": "إثيوبي", "name_en": "Ethiopian", "country_code": "ETH"},
    {"name_ar": "بابوا غينيا الجديدة", "name_en": "Papua New Guinean", "country_code": "PNG"},
    {"name_ar": "باراغواياني", "name_en": "Paraguayan", "country_code": "PRY"},
    {"name_ar": "باكستاني", "name_en": "Pakistani", "country_code": "PAK"},
    {"name_ar": "بالاوي", "name_en": "Palauan", "country_code": "PLW"},
    {"name_ar": "بحريني", "name_en": "Bahraini", "country_code": "BHR"},
    {"name_ar": "برازيلي", "name_en": "Brazilian", "country_code": "BRA"},
    {"name_ar": "بربادوسي", "name_en": "Barbadian", "country_code": "BRB"},
    {"name_ar": "برتغالي", "name_en": "Portuguese", "country_code": "PRT"},
    {"name_ar": "بريطاني", "name_en": "British", "country_code": "GBR"},
    {"name_ar": "بروني", "name_en": "Bruneian", "country_code": "BRN"},
    {"name_ar": "بلجيكي", "name_en": "Belgian", "country_code": "BEL"},
    {"name_ar": "بلغاري", "name_en": "Bulgarian", "country_code": "BGR"},
    {"name_ar": "بليزي", "name_en": "Belizean", "country_code": "BLZ"},
    {"name_ar": "بنغلاديشي", "name_en": "Bangladeshi", "country_code": "BGD"},
    {"name_ar": "بنمي", "name_en": "Panamanian", "country_code": "PAN"},
    {"name_ar": "بنيني", "name_en": "Beninese", "country_code": "BEN"},
    {"name_ar": "بوتاني", "name_en": "Bhutanese", "country_code": "BTN"},
    {"name_ar": "بوتسواني", "name_en": "Motswana", "country_code": "BWA"},
    {"name_ar": "بوركينابي", "name_en": "Burkinabe", "country_code": "BFA"},
    {"name_ar": "بوروندي", "name_en": "Burundian", "country_code": "BDI"},
    {"name_ar": "بوسني", "name_en": "Bosnian", "country_code": "BIH"},
    {"name_ar": "بولندي", "name_en": "Polish", "country_code": "POL"},
    {"name_ar": "بوليفي", "name_en": "Bolivian", "country_code": "BOL"},
    {"name_ar": "بيروفي", "name_en": "Peruvian", "country_code": "PER"},
    {"name_ar": "بيلاروسي", "name_en": "Belarusian", "country_code": "BLR"},
    {"name_ar": "تايلاندي", "name_en": "Thai", "country_code": "THA"},
    {"name_ar": "تايواني", "name_en": "Taiwanese", "country_code": "TWN"},
    {"name_ar": "تركمانستاني", "name_en": "Turkmen", "country_code": "TKM"},
    {"name_ar": "تركي", "name_en": "Turkish", "country_code": "TUR"},
    {"name_ar": "ترينيدادي", "name_en": "Trinidadian/Tobagonian", "country_code": "TTO"},
    {"name_ar": "تشادي", "name_en": "Chadian", "country_code": "TCD"},
    {"name_ar": "تشيكي", "name_en": "Czech", "country_code": "CZE"},
    {"name_ar": "تشيلي", "name_en": "Chilean", "country_code": "CHL"},
    {"name_ar": "تنزاني", "name_en": "Tanzanian", "country_code": "TZA"},
    {"name_ar": "توغولي", "name_en": "Togolese", "country_code": "TGO"},
    {"name_ar": "توفالي", "name_en": "Tuvaluan", "country_code": "TUV"},
    {"name_ar": "تونسي", "name_en": "Tunisian", "country_code": "TUN"},
    {"name_ar": "تونغي", "name_en": "Tongan", "country_code": "TON"},
    {"name_ar": "تيموري شرقي", "name_en": "East Timorese", "country_code": "TLS"},
    {"name_ar": "جامايكي", "name_en": "Jamaican", "country_code": "JAM"},
    {"name_ar": "جبل طارق", "name_en": "Gibraltar", "country_code": "GIB"},
    {"name_ar": "جزائري", "name_en": "Algerian", "country_code": "DZA"},
    {"name_ar": "جزر البهاما", "name_en": "Bahamian", "country_code": "BHS"},
    {"name_ar": "جزر القمر", "name_en": "Comoran", "country_code": "COM"},
    {"name_ar": "جزر سليمان", "name_en": "Solomon Islander", "country_code": "SLB"},
    {"name_ar": "جزر مارشال", "name_en": "Marshallese", "country_code": "MHL"},
    {"name_ar": "جمهورية أفريقيا الوسطى", "name_en": "Central African", "country_code": "CAF"},
    {"name_ar": "جنوب أفريقي", "name_en": "South African", "country_code": "ZAF"},
    {"name_ar": "جنوب سوداني", "name_en": "South Sudanese", "country_code": "SSD"},
    {"name_ar": "جورجي", "name_en": "Georgian", "country_code": "GEO"},
    {"name_ar": "جياني", "name_en": "Guyanese", "country_code": "GUY"},
    {"name_ar": "جيبوتي", "name_en": "Djiboutian", "country_code": "DJI"},
    {"name_ar": "داني", "name_en": "Danish", "country_code": "DNK"},
    {"name_ar": "دومينيكي", "name_en": "Dominican", "country_code": "DMA"},
    {"name_ar": "رواندي", "name_en": "Rwandan", "country_code": "RWA"},
    {"name_ar": "روسي", "name_en": "Russian", "country_code": "RUS"},
    {"name_ar": "روماني", "name_en": "Romanian", "country_code": "ROU"},
    {"name_ar": "زامبي", "name_en": "Zambian", "country_code": "ZMB"},
    {"name_ar": "زيمبابوي", "name_en": "Zimbabwean", "country_code": "ZWE"},
    {"name_ar": "ساح العاج", "name_en": "Ivorian", "country_code": "CIV"},
    {"name_ar": "سالفادوري", "name_en": "Salvadoran", "country_code": "SLV"},
    {"name_ar": "ساموي", "name_en": "Samoan", "country_code": "WSM"},
    {"name_ar": "سان مارينو", "name_en": "Sammarinese", "country_code": "SMR"},
    {"name_ar": "ساوتومي", "name_en": "Sao Tomean", "country_code": "STP"},
    {"name_ar": "سعودي", "name_en": "Saudi Arabian", "country_code": "SAU"},
    {"name_ar": "سريلانكي", "name_en": "Sri Lankan", "country_code": "LKA"},
    {"name_ar": "سلوفاكي", "name_en": "Slovak", "country_code": "SVK"},
    {"name_ar": "سلوفيني", "name_en": "Slovenian", "country_code": "SVN"},
    {"name_ar": "سنغافوري", "name_en": "Singaporean", "country_code": "SGP"},
    {"name_ar": "سنغالي", "name_en": "Senegalese", "country_code": "SEN"},
    {"name_ar": "سوازيلاندي", "name_en": "Swazi", "country_code": "SWZ"},
    {"name_ar": "سوداني", "name_en": "Sudanese", "country_code": "SDN"},
    {"name_ar": "سوري", "name_en": "Syrian", "country_code": "SYR"},
    {"name_ar": "سورينامي", "name_en": "Surinamer", "country_code": "SUR"},
    {"name_ar": "سويسري", "name_en": "Swiss", "country_code": "CHE"},
    {"name_ar": "سويدي", "name_en": "Swedish", "country_code": "SWE"},
    {"name_ar": "سيراليوني", "name_en": "Sierra Leonean", "country_code": "SLE"},
    {"name_ar": "سيشلي", "name_en": "Seychellois", "country_code": "SYC"},
    {"name_ar": "صربي", "name_en": "Serbian", "country_code": "SRB"},
    {"name_ar": "صيني", "name_en": "Chinese", "country_code": "CHN"},
    {"name_ar": "صومالي", "name_en": "Somali", "country_code": "SOM"},
    {"name_ar": "طاجيكي", "name_en": "Tajik", "country_code": "TJK"},
    {"name_ar": "عراقي", "name_en": "Iraqi", "country_code": "IRQ"},
    {"name_ar": "عماني", "name_en": "Omani", "country_code": "OMN"},
    {"name_ar": "غابوني", "name_en": "Gabonese", "country_code": "GAB"},
    {"name_ar": "غامبي", "name_en": "Gambian", "country_code": "GMB"},
    {"name_ar": "غاني", "name_en": "Ghanaian", "country_code": "GHA"},
    {"name_ar": "غرينادي", "name_en": "Grenadian", "country_code": "GRD"},
    {"name_ar": "غواتيمالي", "name_en": "Guatemalan", "country_code": "GTM"},
    {"name_ar": "غيني", "name_en": "Guinean", "country_code": "GIN"},
    {"name_ar": "غيني استوائي", "name_en": "Equatorial Guinean", "country_code": "GNQ"},
    {"name_ar": "غيني بيساوي", "name_en": "Guinea-Bissauan", "country_code": "GNB"},
    {"name_ar": "فانواتي", "name_en": "Vanuatuan", "country_code": "VUT"},
    {"name_ar": "فرنسي", "name_en": "French", "country_code": "FRA"},
    {"name_ar": "فلسطيني", "name_en": "Palestinian", "country_code": "PSE"},
    {"name_ar": "فلبيني", "name_en": "Philippine", "country_code": "PHL"},
    {"name_ar": "فنزويلي", "name_en": "Venezuelan", "country_code": "VEN"},
    {"name_ar": "فنلندي", "name_en": "Finnish", "country_code": "FIN"},
    {"name_ar": "فيتنامي", "name_en": "Vietnamese", "country_code": "VNM"},
    {"name_ar": "فيجي", "name_en": "Fijian", "country_code": "FJI"},
    {"name_ar": "قبرصي", "name_en": "Cypriot", "country_code": "CYP"},
    {"name_ar": "قرغيزي", "name_en": "Kyrgyz", "country_code": "KGZ"},
    {"name_ar": "قطري", "name_en": "Qatari", "country_code": "QAT"},
    {"name_ar": "كازاخستاني", "name_en": "Kazakhstani", "country_code": "KAZ"},
    {"name_ar": "كاميروني", "name_en": "Cameroonian", "country_code": "CMR"},
    {"name_ar": "كرواتي", "name_en": "Croatian", "country_code": "HRV"},
    {"name_ar": "كمبودي", "name_en": "Cambodian", "country_code": "KHM"},
    {"name_ar": "كندي", "name_en": "Canadian", "country_code": "CAN"},
    {"name_ar": "كوبي", "name_en": "Cuban", "country_code": "CUB"},
    {"name_ar": "كوري جنوبي", "name_en": "South Korean", "country_code": "KOR"},
    {"name_ar": "كوري شمالي", "name_en": "North Korean", "country_code": "PRK"},
    {"name_ar": "كوستاريكي", "name_en": "Costa Rican", "country_code": "CRI"},
    {"name_ar": "كوسوفي", "name_en": "Kosovan", "country_code": "XKX"}, # Code is provisional
    {"name_ar": "كولومبي", "name_en": "Colombian", "country_code": "COL"},
    {"name_ar": "كونغولي", "name_en": "Congolese", "country_code": "COG"},
    {"name_ar": "كويتي", "name_en": "Kuwaiti", "country_code": "KWT"},
    {"name_ar": "كيريباتي", "name_en": "I-Kiribati", "country_code": "KIR"},
    {"name_ar": "كيني", "name_en": "Kenyan", "country_code": "KEN"},
    {"name_ar": "لاتفي", "name_en": "Latvian", "country_code": "LVA"},
    {"name_ar": "لاوسي", "name_en": "Laotian", "country_code": "LAO"},
    {"name_ar": "لبناني", "name_en": "Lebanese", "country_code": "LBN"},
    {"name_ar": "لوكسمبورغي", "name_en": "Luxembourger", "country_code": "LUX"},
    {"name_ar": "ليبيري", "name_en": "Liberian", "country_code": "LBR"},
    {"name_ar": "ليبي", "name_en": "Libyan", "country_code": "LBY"},
    {"name_ar": "ليتواني", "name_en": "Lithuanian", "country_code": "LTU"},
    {"name_ar": "ليختنشتايني", "name_en": "Liechtensteiner", "country_code": "LIE"},
    {"name_ar": "ليسوتي", "name_en": "Mosotho", "country_code": "LSO"},
    {"name_ar": "مالي", "name_en": "Malian", "country_code": "MLI"},
    {"name_ar": "مالطي", "name_en": "Maltese", "country_code": "MLT"},
    {"name_ar": "مالديفي", "name_en": "Maldivan", "country_code": "MDV"},
    {"name_ar": "ماليزي", "name_en": "Malaysian", "country_code": "MYS"},
    {"name_ar": "مدغشقري", "name_en": "Malagasy", "country_code": "MDG"},
    {"name_ar": "مصري", "name_en": "Egyptian", "country_code": "EGY"},
    {"name_ar": "مقدوني", "name_en": "Macedonian", "country_code": "MKD"},
    {"name_ar": "مغربي", "name_en": "Moroccan", "country_code": "MAR"},
    {"name_ar": "مكسيكي", "name_en": "Mexican", "country_code": "MEX"},
    {"name_ar": "منغولي", "name_en": "Mongolian", "country_code": "MNG"},
    {"name_ar": "موريتاني", "name_en": "Mauritanian", "country_code": "MRT"},
    {"name_ar": "موريشيوسي", "name_en": "Mauritian", "country_code": "MUS"},
    {"name_ar": "موزمبيقي", "name_en": "Mozambican", "country_code": "MOZ"},
    {"name_ar": "مولدوفي", "name_en": "Moldovan", "country_code": "MDA"},
    {"name_ar": "موناكو", "name_en": "Monegasque", "country_code": "MCO"},
    {"name_ar": "مونتينيغري", "name_en": "Montenegrin", "country_code": "MNE"},
    {"name_ar": "ميانماري", "name_en": "Myanma", "country_code": "MMR"},
    {"name_ar": "ميكرونيزي", "name_en": "Micronesian", "country_code": "FSM"},
    {"name_ar": "ناميبي", "name_en": "Namibian", "country_code": "NAM"},
    {"name_ar": "ناورو", "name_en": "Nauruan", "country_code": "NRU"},
    {"name_ar": "نرويجي", "name_en": "Norwegian", "country_code": "NOR"},
    {"name_ar": "نمساوي", "name_en": "Austrian", "country_code": "AUT"},
    {"name_ar": "نيبالي", "name_en": "Nepalese", "country_code": "NPL"},
    {"name_ar": "نيجيري", "name_en": "Nigerian", "country_code": "NGA"},
    {"name_ar": "نيجيري (النيجر)", "name_en": "Nigerien", "country_code": "NER"},
    {"name_ar": "نيكاراغوي", "name_en": "Nicaraguan", "country_code": "NIC"},
    {"name_ar": "نيوزيلندي", "name_en": "New Zealander", "country_code": "NZL"},
    {"name_ar": "هايتي", "name_en": "Haitian", "country_code": "HTI"},
    {"name_ar": "هندي", "name_en": "Indian", "country_code": "IND"},
    {"name_ar": "هندوراسي", "name_en": "Honduran", "country_code": "HND"},
    {"name_ar": "هنغاري", "name_en": "Hungarian", "country_code": "HUN"},
    {"name_ar": "هولندي", "name_en": "Dutch", "country_code": "NLD"},
    {"name_ar": "ياباني", "name_en": "Japanese", "country_code": "JPN"},
    {"name_ar": "يمني", "name_en": "Yemeni", "country_code": "YEM"},
    {"name_ar": "يوناني", "name_en": "Greek", "country_code": "GRC"}
]








def seed_nationalities():
    """
    دالة تقوم بإضافة الجنسيات إلى قاعدة البيانات.
    """
    print("Starting to seed nationalities...")

    # التحقق مما إذا كان الجدول يحتوي على بيانات بالفعل
    if Nationality.query.first():
        print("Nationalities table is not empty. Aborting.")
        return

    # إضافة الجنسيات من القائمة
    for nat_data in NATIONALITIES_LIST:
        nationality = Nationality(
            name_ar=nat_data['name_ar'],
            name_en=nat_data.get('name_en'),
            country_code=nat_data.get('country_code')
        )
        db.session.add(nationality)
        print(f"Adding: {nat_data['name_ar']}")
    
    # حفظ التغييرات في قاعدة البيانات
    try:
        db.session.commit()
        print("Successfully seeded all nationalities to the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()

if __name__ == '__main__':
    # إنشاء التطبيق باستخدام إعدادات الإنتاج أو التطوير
    # اختر `DevelopmentConfig` أو `ProductionConfig` حسب الحاجة


    # استخدام سياق التطبيق للوصول إلى قاعدة البيانات
    with app.app_context():
        # استدعاء دالة التعبئة
        seed_nationalities()