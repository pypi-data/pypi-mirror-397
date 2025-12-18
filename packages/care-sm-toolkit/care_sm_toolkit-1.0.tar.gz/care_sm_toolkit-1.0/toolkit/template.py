from copy import deepcopy

class Template_OBO:

    base_template = dict(
        pid=None,
        role_type=None,
        process_type=None,
        attribute_type=None,
        organisation=None,
        input_type=None,
        input_id=None,
        target_type=None,
        target_id=None,
        output_type=None,
        output_id=None,
        output_id_type=None,
        unit_type=None,
        specific_method_type=None,
        protocol_type=None,
        protocol_id=None,
        cause_type=None,
        cause_id=None,
        frequency_type=None,
        frequency_value=None,
        value_date=None,
        value_integer=None,
        value_string=None,
        value_id_string=None,
        value_float=None,
        value_datatype=None,
        comments=None,
        startdate=None,
        enddate=None,
        age=None,
        uniqid=None,
        event_id=None,
        value=None,
        valueIRI=None,
        activity=None,
        target=None,
        agent=None,
        input=None,
        unit=None,
    )

    @classmethod
    def build_entry(cls, **overrides):
        entry = deepcopy(cls.base_template)
        entry.update(overrides)
        return entry

TEMPLATE_MAP_OBO = {

        "Birthdate": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C68615",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:date"
        ),
        "Birthyear": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C83164",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:integer"
        ),
        "Birthplace": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C176764",
            output_type="http://purl.obolibrary.org/obo/NCIT_C25464",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C20108",
            value_datatype="xsd:string"
        ),
        "Deathdate": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C70810",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            cause_type="http://purl.obolibrary.org/obo/NCIT_C81239",
            value_datatype="xsd:date"
        ),
        "First_visit": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C159705",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:date"
        ),
        "Symptoms_onset": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C124353",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            target_type="http://purl.obolibrary.org/obo/NCIT_C4876",
            value_datatype="xsd:date"
        ),
        "Sex": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            output_type="http://purl.obolibrary.org/obo/NCIT_C160908",
            value_datatype="xsd:string"
        ),
        "Status": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C142470",
            output_type="http://purl.obolibrary.org/obo/OPMI_0000326",
            value_datatype="xsd:string"
        ),
        "Diagnosis": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C18020",
            attibute_type="http://purl.obolibrary.org/obo/NCIT_C7057",
            output_type="http://purl.obolibrary.org/obo/OGMS_0000073",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C154625",
            value_datatype="xsd:string"
        ),
        "Phenotype": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C18020",
            output_type="http://purl.obolibrary.org/obo/NCIT_C16977",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C164535",
            value_datatype="xsd:string"
        ),
        "Genetic": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C15709",
            output_type="http://purl.obolibrary.org/obo/NCIT_C171178",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C164607",
            value_datatype="xsd:string"
        ),
        "Examination": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/MAXO_0000487",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:float"
        ),
        "Laboratory": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C25294",
            output_type="http://purl.obolibrary.org/obo/NCIT_C70856",
            value_datatype="xsd:float"
        ),
        "Surgery": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type = "http://purl.obolibrary.org/obo/NCIT_C15329",
            value_datatype = "xsd:string"
        ),
        "Hospitalization": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type = "http://purl.obolibrary.org/obo/NCIT_C25179",
            value_datatype = "xsd:string"
        ),
        "Medication": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/IAO_0000104",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type = "http://purl.obolibrary.org/obo/NCIT_C70962",
            input_type = "http://purl.obolibrary.org/obo/NCIT_C177929",
            value_datatype = "xsd:float"
        ),
        "Clinical_trial": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000097",
            process_type = "http://purl.obolibrary.org/obo/NCIT_C71104",
            output_type = "http://purl.obolibrary.org/obo/NCIT_C142439",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C83082",
            target_type = "http://purl.obolibrary.org/obo/NCIT_C7057",
            value_datatype = "xsd:string"
        ),
        "Cohort": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000097",
            process_type = "http://purl.obolibrary.org/obo/NCIT_C15208",
            output_type = "http://purl.obolibrary.org/obo/NCIT_C142439",
            output_id_type="http://purl.obolibrary.org/obo/NCIT_C83082",
            target_type = "http://purl.obolibrary.org/obo/NCIT_C7057",
            value_datatype = "xsd:string"
        ),
        "Biobank": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type = "http://purl.obolibrary.org/obo/OBIB_0000668",
            output_type = "http://purl.obolibrary.org/obo/NCIT_C19697", 
            output_id_type = "http://purl.obolibrary.org/obo/NCIT_C25402", 
            value_datatype = "xsd:string"
        ),
        "Consent": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type = "http://purl.obolibrary.org/obo/OBI_0000810",
            attribute_type = "http://purl.obolibrary.org/obo/NCIT_C25460", 
            value_datatype = "xsd:string"
        ),
        "Questionnaire": Template_OBO.build_entry(
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/NCIT_C20993",
            output_type="http://purl.obolibrary.org/obo/NCIT_C49149",
            input_type="http://purl.obolibrary.org/obo/NCIT_C91102",
            protocol_type="http://purl.obolibrary.org/obo/NCIT_C177377",
            value_datatype="xsd:float"
        ),
        "Disability": Template_OBO.build_entry(
            protocol_type="http://purl.obolibrary.org/obo/OBI_0000272",
            role_type="http://purl.obolibrary.org/obo/OBI_0000093",
            process_type="http://purl.obolibrary.org/obo/OMIT_0005448",
            attribute_type="http://purl.obolibrary.org/obo/NCIT_C21007",
            output_type="http://purl.obolibrary.org/obo/NCIT_C49149",
            value_datatype="xsd:float"
        ),
    }

class Template_SNOMED:

    base_template = dict(
        pid=None,
        role_type="http://snomed.info/id/116154003",
        process_type=None,
        attribute_type=None,
        organisation=None,
        input_type=None,
        input_id=None,
        target_type=None,
        target_id=None,
        output_type=None,
        output_id=None,
        output_id_type=None,
        unit_type=None,
        specific_method_type=None,
        protocol_type=None,
        protocol_id=None,
        cause_type=None,
        cause_id=None,
        frequency_type=None,
        frequency_value=None,
        value_date=None,
        value_integer=None,
        value_string=None,
        value_id_string=None,
        value_float=None,
        value_datatype=None,
        comments=None,
        startdate=None,
        enddate=None,
        age=None,
        uniqid=None,
        event_id=None,
        value=None,
        valueIRI=None,
        activity=None,
        target=None,
        agent=None,
        input=None,
        unit=None,
    )

    @classmethod
    def build_entry(cls, **overrides):
        entry = deepcopy(cls.base_template)
        entry.update(overrides)
        return entry

TEMPLATE_MAP_SNOMED = {
        "Birthdate":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/312486000",
            attribute_type="http://snomed.info/id/3950001",
            output_type="http://snomed.info/id/184099003",
            value_datatype="xsd:date"
        ),
        "Birthyear":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/312486000",
            attribute_type="http://snomed.info/id/3950001",
            output_type="http://snomed.info/id/258707000",
            value_datatype="xsd:integer"
        ),
        "Birthplace":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/312486000",
            output_type="http://snomed.info/id/315354004",
            output_id_type="http://snomed.info/id/118522005",
            value_datatype="xsd:integer"
        ),
        "Deathdate":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/363049002",
            attribute_type="http://snomed.info/id/419620001",
            output_type="http://snomed.info/id/399753006",
            cause_type="http://snomed.info/id/184305005",
            value_datatype="xsd:date"
        ),
        "First_visit":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/308335008",
            attribute_type="http://snomed.info/id/769681006",
            output_type="http://snomed.info/id/406543005",
            value_datatype="xsd:date"
        ),
        "Symptoms_onset":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/308335008",
            attribute_type="http://snomed.info/id/308918001",
            output_type="http://snomed.info/id/263501003",
            target_type="http://snomed.info/id/162408000",
            value_datatype="xsd:date"
        ),
        "Sex":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/312486000",
            output_type="http://snomed.info/id/734000001",
            value_datatype="xsd:string"
        ),
        "Status":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/386053000",
            output_type="http://snomed.info/id/420107008",
            value_datatype="xsd:string"
        ),
        "Diagnosis":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/103693007",
            output_type="http://snomed.info/id/439401001",
            output_id_type="http://snomed.info/id/118522005",
            attribute_type="http://snomed.info/id/64572001",
            value_datatype="xsd:string"
        ),
        "Phenotype":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/363778006",
            output_type="http://snomed.info/id/8116006",
            output_id_type="http://snomed.info/id/118522005",
            value_datatype="xsd:string"
        ),
        "Genetic":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/405824009",
            output_type="http://snomed.info/id/41482005",
            output_id_type="http://snomed.info/id/118522005",
            value_datatype="xsd:string"
        ),
        "Questionnaire":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type ="http://snomed.info/id/1402981000000101",
            process_type="http://snomed.info/id/840297006",
            input_type = "https://loinc.org/LP175698-2",
            output_type = "https://loinc.org/82783-2",
            value_datatype="xsd:float"
        ),
        "Disability":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/81078003",
            attribute_type="http://snomed.info/id/21134002",
            output_type="http://snomed.info/id/273421001",
            value_datatype="xsd:float"
        ),
        "Examination":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/315306007",
            output_type="http://snomed.info/id/363789004",
            value_datatype="xsd:float"
        ),
        "Laboratory":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type="http://snomed.info/id/108252007",
            output_type="http://snomed.info/id/4241000179101",
            value_datatype="xsd:float"
        ),
        "Surgery":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type = "http://snomed.info/id/387713003",
            value_datatype = "xsd:string"
        ),
        "Hospitalization":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type = "https://loinc.org/LA15417-1",
            value_datatype = "xsd:string"
        ),
        "Medication":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type = "http://snomed.info/id/18629005",
            input_type = "http://snomed.info/id/2533004",      
            output_type = "https://loinc.org/18615-5",
            value_datatype = "xsd:float"
        ),
        "Clinical_trial":Template_SNOMED.build_entry(
            protocol_type="http://snomed.info/id/258049002",
            role_type="http://snomed.info/id/428024001",
            process_type = "http://snomed.info/id/110465008",
            output_id_type = "http://snomed.info/id/118522005",
            output_type = "http://snomed.info/id/229059009", 
            target_type ="http://snomed.info/id/64572001", 
            value_datatype = "xsd:string"
        ),
        "Cohort":Template_SNOMED.build_entry(
            protocol_type="http://snomed.info/id/258049002",
            role_type="http://snomed.info/id/428024001",
            process_type = "http://snomed.info/id/719581000000108",
            output_id_type = "http://snomed.info/id/118522005",
            output_type = "http://snomed.info/id/229059009", 
            target_type ="http://snomed.info/id/64572001", 
            value_datatype = "xsd:string"
        ),
        "Biobank":Template_SNOMED.build_entry(
            role_type="http://snomed.info/id/116154003",
            protocol_type="http://snomed.info/id/258049002",
            process_type = "http://snomed.info/id/433465004",
            output_type = "http://snomed.info/id/364611000000101", 
            output_id_type = "http://snomed.info/id/118522005",     
            value_datatype = "xsd:string"
        )
    }