import re
from PyPDF2 import PdfReader
import pdfplumber

def extract_surface_test_data(pdf_path):

    # Read the PDF content
    with pdfplumber.open(pdf_path) as pdf:
        content = "\n".join(page.extract_text() for page in pdf.pages)
    content_split = content.split("\n")


    # Regular expressions for extracting samples and results
    test_number_pattern = r"Test\sCertificate\s+([A-Za-z0-9]+)"
    report_date_pattern = r"(\d+/\d+/\d+)"
    number_of_samples_pattern = r"(\d+)"
    test_name_pattern = r":\s+(\w+\s+\w+)"
    purchase_order_pattern = r"(\d+)"
    date_received_pattern = r"(\d+/\d+/\d+)"
    date_of_sample_pattern = r"(\d+/\d+/\d+)"
    state_of_sample_pattern = r":\s+(\w+)"
    substance_sampled_pattern = r":\s+(\w+\s+\w+)"
    sample_number_pattern = r"Sample no\.\s*:\s*(\S+)" # used to extract sample numbers
    results_block_pattern = r"Test\s*(?:Unit)?\s*Result\s*(.*?)\s*Interpretation of sample"  # used to extract results block
    results_pattern = r"^(.+?)\s+((?:[<>]?=?\s*)?\d+(?:\.\d+)?)$" # used to extract results

    test_data_pattern = r"\w+\s*\w*\s*\w{3}-\w{6}-\w{2}\s+.*?(?=neuroprobe|cannula|leadconfirm\s*cable|leadconfirm\s*adaptor|alphaprobe\s*cable|electrode\s*cable|$)" # used to extract sample data
    product_name_pattern = r"[a-zA-z ]*\s+(?=\w{3}-\w{6}-\w{2})"
    cat_block_pattern = r"\w{3}-\w{6}-\w{2}.*?(?=\w{3}-\w{6}-\w{2}|$)"
    cat_number_pattern =r"\w{3}-\w{6}-\w{2}"
    lot_numbers_pattern = r"(?<=\w{3}-\w{6}-\w{2})\s*(.*)"
    lot_numbers_spliter_pattern = r"[/, ]"

    # Dict to hold all data
    data = {
        "Test Number": None,
        "Report Date": None,
        "Number of Samples": None,
        "Test Name": None,
        "Purchase Order": None,
        "Date Received": None,
        "Date Sampled": None,
        "State of Sample": None,
        "Substance Sampled": None,
        "Samples Data": None,
        "Results": None
    }

    # Finding test number and using it as a guide to extract all other data
    for i, line in enumerate(content_split):
        if "Certificate" in line:
            test_number_index = i
            break

    # Extract Test number
    test_number = re.findall(test_number_pattern, content_split[test_number_index])[0]

    # Extract Report Date
    report_date = re.findall(report_date_pattern, content_split[test_number_index + 1])[0]

    # Extract Number of Samples
    number_of_samples = re.findall(number_of_samples_pattern, content_split[test_number_index + 2])[0]

    # Extract Test Name
    test_name = re.findall(test_name_pattern, content_split[test_number_index + 3])[0]

    # Extract Purchase Order
    purchase_order = re.findall(purchase_order_pattern, content_split[test_number_index + 4])[0]

    # Extract Date Received
    date_received = re.findall(date_received_pattern, content_split[test_number_index + 5])[0]

    # Extract date of sample
    date_of_sample = re.findall(date_of_sample_pattern, content_split[test_number_index + 6])[0]

    # Extract State of Sample
    state_of_sample = re.findall(state_of_sample_pattern, content_split[test_number_index + 7])[0]

    # Extract Substance Sampled
    substance_sampled = re.findall(substance_sampled_pattern, content_split[test_number_index + 8])[0]

    # Extract samples LOT# and CAT#
    parsed_cat_lot = {
        "Products": [],
        "CAT#": [],
        "LOT#": []
    }

    # Extracting data block
    for i, line in enumerate(content_split):
        if "Interpretation" in line:
            cat_lot_block = content_split[i + 2]
            break
        
    products = re.findall(test_data_pattern, cat_lot_block, re.IGNORECASE) # extracting sample data
    # Parse LOT# and CAT#
    for i, product in enumerate(products):
        parsed_cat_lot["CAT#"].append([])
        parsed_cat_lot["LOT#"].append([])
        parsed_cat_lot["Products"].append(re.findall(product_name_pattern,product)[0])
        # Dividing items by CAT# if there are multiple CAT# for one product
        items = re.findall(cat_block_pattern, product)
        for item in items:
            parsed_cat_lot["CAT#"][i].append(re.findall(cat_number_pattern,item)[0])
            lot_numbers = re.search(lot_numbers_pattern, item).groups()[0] # get all LOT numbers in one string
            lot_numbers = re.sub(r"\s*", "", lot_numbers) # remove any whitespaces from the LOT string
            parsed_cat_lot["LOT#"][i].append(re.split(lot_numbers_spliter_pattern, lot_numbers))

    # Cleaning the the products strings from non-alphabetical characters
    for i, product in enumerate(parsed_cat_lot["Products"]):
        parsed_cat_lot["Products"][i] = product.strip()

    # Extract test results
    # Extract results block
    results_block_match = re.findall(results_block_pattern, content, flags= re.DOTALL)
    if not results_block_match:
        print("Results not found")
    else:
        results_block_list = results_block_match[0].split("\n")
        results = []
        for i in range(0 ,len(results_block_list), 5): # iterate over results 
            result ={} # initialize results dict
            sample_number = re.findall(sample_number_pattern, results_block_list[i])[0] # finding the sample number
            result[f"Sample {(i+5)//5}"] = sample_number
            result["Tests"] = [] # initialize tests array
            for j in range(3): # extracting test names and results
                result_match = re.findall(results_pattern, results_block_list[i + j + 2]) # finding the test and their results
                if result_match:
                    result["Tests"].append({"Test": result_match[0][0], "Result": result_match[0][1]}) # adding the tests and their results to an array
                    if j == 2: # checking if we're at the last test in the sample
                        results.append(result) # adding the sample tests and data to the results array

    data["Test Number"] = test_number
    data["Report Date"] = report_date
    data["Number of Samples"] = number_of_samples
    data["Test Name"] = test_name
    data["Purchase Order"] = purchase_order
    data["Date Received"] = date_received
    data["Date Sampled"] = date_of_sample
    data["State of Sample"] = state_of_sample
    data["Substance Sampled"] = substance_sampled
    data["Samples Data"] = parsed_cat_lot
    data["Results"] = results
    
    return data

def extract_air_test_data(pdf_path):
    
    # Read the PDF content
    with pdfplumber.open(pdf_path) as pdf:
        content = "\n".join(page.extract_text() for page in pdf.pages)
    content_split = content.split("\n")


    # Regular expressions for extracting samples and results
    test_number_pattern = r"Test Certificate\s+([A-Za-z0-9]+)" # used to extract the test number
    report_date_pattern = r"(\d+/\d+/\d+)"
    number_of_samples_pattern = r"(\d+)"
    test_name_pattern = r":\s+(\w+\s+\w+)"
    purchase_order_pattern = r"(\d+)"
    date_received_pattern = r"(\d+/\d+/\d+)"
    date_of_sample_pattern = r"(\d+/\d+/\d+)"
    state_of_sample_pattern = r":\s+(\w+)"
    substance_sampled_pattern = r":\s+(\w+\s+\w+)"
    sample_number_pattern = r":\s*(.*)" # used to extract sample numbers
    results_block_pattern = r"Sample no\.\s*(.*?)(?=\nInterpretation of sample)"  # used to extract results block
    results_pattern = r"^(.+?)\s+((?:[<>]?=?\s*)?\d+(?:\.\d+)?)$" # used to extract results

    test_data_pattern = r"\w+\s*\w*\s*\w{3}-\w{6}-\w{2}\s+.*?(?=neuroprobe|cannula|leadconfirm\s*cable|leadconfirm\s*adaptor|alphaprobe\s*cable|electrode\s*cable|$)" # used to extract sample data
    product_name_pattern = r"\w+\s*\w*(?=\w{3}-\w{6}-\w{2})"
    cat_number_pattern =r"\w{3}-\w{6}-\w{2}"
    lot_numbers_pattern = r"(?<=\w{3}-\w{6}-\w{2})\s*(.*)"
    lot_numbers_spliter_pattern = r"[/, ]"

    # Dict to hold all data
    data = {
        "Test Name": None,
        "Test Number": None,
        "Report Date": None,
        "Number of Samples": None,
        "Purchase Order": None,
        "Date Received": None,
        "Date Sampled": None,
        "State of Sample": None,
        "Substance Sampled": None,
        "Samples Data": None,
        "Results": None
    }

    # Finding test number and using it as a guide to extract all other data
    for i, line in enumerate(content_split):
        if "Certificate" in line:
            test_number_index = i
            break
        
    # Extract Test number
    test_number = re.findall(test_number_pattern, content_split[test_number_index])[0]

    # Extract Report Date
    report_date = re.findall(report_date_pattern, content_split[test_number_index + 1])[0]

    # Extract Number of Samples
    number_of_samples = re.findall(number_of_samples_pattern, content_split[test_number_index + 2])[0]

    # Extract Test Name
    test_name = re.findall(test_name_pattern, content_split[test_number_index + 3])[0]

    # Extract Purchase Order
    purchase_order = re.findall(purchase_order_pattern, content_split[test_number_index + 4])[0]

    # Extract Date Received
    date_received = re.findall(date_received_pattern, content_split[test_number_index + 5])[0]

    # Extract date of sample
    date_of_sample = re.findall(date_of_sample_pattern, content_split[test_number_index + 6])[0]

    # Extract State of Sample
    state_of_sample = re.findall(state_of_sample_pattern, content_split[test_number_index + 7])[0]

    # Extract Substance Sampled
    substance_sampled = re.findall(substance_sampled_pattern, content_split[test_number_index + 8])[0]

    # Extract samples LOT# and CAT#
    parsed_cat_lot = {
        "Products": [],
        "CAT#": [],
        "LOT#": []
    }

    # Extracting data block
    cat_lot_block = content_split[24]
    items = re.findall(test_data_pattern, cat_lot_block, re.IGNORECASE) # extracting sample data
    # Parse LOT# and CAT#
    for item in items:
        parsed_cat_lot["Products"].append(re.findall(product_name_pattern,item)[0])
        parsed_cat_lot["CAT#"].append(re.findall(cat_number_pattern,item))
        lot_numbers = re.search(lot_numbers_pattern, item).groups()[0]
        parsed_cat_lot["LOT#"].append(re.split(lot_numbers_spliter_pattern, lot_numbers))

    # Cleaning the the products strings from non-alphabetical characters
    for i, product in enumerate(parsed_cat_lot["Products"]):
        parsed_cat_lot["Products"][i] = product.strip()

    # Extract test results
    # Extract results block
    results_block_match = re.findall(results_block_pattern, content, flags= re.DOTALL)
    if not results_block_match:
        print("Results not found")
    else:
        results_block_list = results_block_match[0].split("\n")
        results = []
        for i in range(0 ,len(results_block_list), 5): # iterate over results 
            result ={} # initialize results
            sample_number = re.findall(sample_number_pattern, results_block_list[i])[0] # finding the sample number
            result[f"Sample {(i+5)//5}"] = sample_number
            result["Tests"] = [] # initialize tests array
            for j in range(3): # extracting test names and results
                result_match = re.findall(results_pattern, results_block_list[i + j + 2]) # finding the test and their results
                if result_match:
                    result["Tests"].append({"Test": result_match[0][0], "Result": result_match[0][1]}) # adding the tests and their results to an array
                    if j == 2: # checking if we're at the last test in the sample
                        results.append(result) # adding the sample tests and data to the results array
                    

    data["Test Number"] = test_number
    data["Report Date"] = report_date
    data["Number of Samples"] = number_of_samples
    data["Test Name"] = test_name
    data["Purchase Order"] = purchase_order
    data["Date Received"] = date_received
    data["Date Sampled"] = date_of_sample
    data["State of Sample"] = state_of_sample
    data["Substance Sampled"] = substance_sampled
    data["Samples Data"] = parsed_cat_lot
    data["Results"] = results
    
    return data

def extract_peel_test_data(pdf_path):

    # Read the PDF content
    with pdfplumber.open(pdf_path) as pdf:
        content = "\n".join(page.extract_text() for page in pdf.pages)
    content_split = content.split("\n")

    # Regular expressions for extracting samples and results
    test_name_pattern = r".*"
    report_date_pattern = r"(\d+.\d+.\d+)"
    test_number_pattern = r"(SO[0-9]*)"
    purchase_order_pattern = r""
    production_date_pattern = r""
    date_received_pattern = r""
    date_start_of_test_pattern = r""
    date_end_of_test_pattern = r""
    result_pattern = r"\d+.\d+"
    # TODO: add patterns to parse sample description data
    # TODO: Add the rest of the patterns

    # Dict to hold all data
    data = {
        "Test Name": None,
        "Report Date": None,
        "Test Number": None,
        "Purchase Order": None,
        "Production Date": None,
        "Samples": {
            "Products": [],
            "CAT#": [],
            "LOT#": []
        },
        "Date Received": None,
        "Date of Test Start": None,
        "Date of Test End": None,
        "Results": []
    }

    # Indecies placeholders
    test_name_index = None
    report_date_index = None
    test_number_index = None
    purchase_order_index = None
    production_date_index = None
    date_received_index = None
    date_start_of_test_index = None
    date_end_of_test_index = None
    results_block_start_index = None

    # Iterating over the output to find required indecies 
    for i, line in enumerate(content_split):
        if not test_name_index:
            if "Package" in line and "Integrity" in line:
                test_name_index = i
        
        if not report_date_index:
            if "Date" in line and "report" in line:
                report_date_index = i

        if not test_number_index:
            if "Laboratory" in line and "Number" in line:
                test_number_index = i

        if not purchase_order_index:
            if "Order" in line and "Number" in line:
                purchase_order_index = i
                production_date_index = i

        if not date_received_index:
            if "Date" in line and "received" in line:
                date_received_index = i

        if not date_start_of_test_index:
            if "Beginning" in line and "Test" in line:
                date_start_of_test_index = i
        
        if not date_end_of_test_index:
            if "End" in line and "Test" in line:
                date_end_of_test_index = i

        if not results_block_start_index:
            if "Annex" in line:
                results_block_start_index = i
        
    # Extraction
    test_name = re.findall(test_name_pattern, content_split[test_name_index])[0]
    test_number = re.findall(test_number_pattern, content_split[test_number_index])[0]
    # Extract results
    first_result = re.findall(result_pattern, content_split[results_block_start_index + 1])[0]
    second_result = re.findall(result_pattern, content_split[results_block_start_index + 2])[0]
    # TODO: Extract the rest of the data
    
    data["Test Name"] = ' '.join(test_name.split())
    data["Test Number"] = test_number
    data["Results"].append(first_result)
    data["Results"].append(second_result)

    return data

def extract_microbiological_test_data(pdf_path):

    # Read the PDF content
    with pdfplumber.open(pdf_path) as pdf:
        content = "\n".join(page.extract_text() for page in pdf.pages)
        # Extract tables
        tables = [table for page in pdf.pages for table in page.extract_tables()]
    content_split = content.split("\n")

    # Regular expressions for extracting samples and results
    test_name_pattern = r".*"
    test_number_pattern = r"(SO[0-9]*)"
    purchase_order_pattern = r""
    production_date_pattern = r""
    date_received_pattern = r""
    date_start_of_test_pattern = r""
    date_end_of_test_pattern = r""
    samples_name_pattern = r"neuroprobe|cannula|leadconfirm\s*cable|leadconfirm\s*adaptor|alphaprobe\s*cable|electrode\s*cable"
    samples_cat_pattern = r"\w{3}\s*-\s*\w{6}\s*-\s*\w{2}"
    samples_lot_pattern = r"M?\d{5}A?N?|\S{3}-\S{5}-\S{2}"
    result_pattern = r"\d*\s*[-0-9a-zA-Z]*\s*(<?\d+)"
    # TODO: add patterns to parse cleaning batch data
    # TODO: Add the rest of the patterns

    # Dict to hold all data
    data = {
        "Test Name": None,
        "Test Number": None,
        "Samples": {
            "Products": [],
            "CAT#": [],
            "LOT#": []
        },
        "Cleaning Batches": {
            "Products": None,
            "CAT#": None,
            "LOT#": None
        },
        "Results": []
    }

    # Indecies placeholders
    test_name_index = None
    test_number_index = None
    purchase_order_index = None
    production_date_index = None
    date_received_index = None
    date_start_of_test_index = None
    date_end_of_test_index = None
    sample_block_start_index = None
    results_block_start_index = None
    # TODO: placeholders for the rest of the data

    # Iterating over the output to find required indecies 
    for i, line in enumerate(content_split):
        if not test_name_index:
            if "Microbiological" in line and "Test" in line:
                test_name_index = i
        
        if not test_number_index:
            if "Laboratory" in line and "Number" in line:
                test_number_index = i
        
    # Extraction
    test_name = re.findall(test_name_pattern, content_split[test_name_index])[0]
    test_number = re.findall(test_number_pattern, content_split[test_number_index])[0]

    # Extract samples data
    # Placeholders for samples data
    samples_names = []
    samples_cats =[]
    samples_lots = []
    # Temporary placeholders for smaple data exraction
    temp_product = None
    temp_cat = []
    temp_lots = [] # For LOTs of multiple CAT#
    temp_lot = [] # For LOTs of a single CAT#
    # Sample data extraction
    for i, product in enumerate(tables[0][0][:-1]):
        if product:
            temp_product = product
            temp_cat = []
            temp_lots = []
        if tables[0][1][i]:
            temp_cat.append(tables[0][1][i])
            temp_lot = []
        temp_lot.append(tables[0][2][i])        
        if tables[0][1][i + 1]: # Check if another CAR# was found to log previous LOT
            temp_lots.append(temp_lot)
        if tables[0][0][i + 1] and tables[0][1][i + 1]: # Check if another product was found to log previous data by looking ahead for CAT# and product name in the same column
            samples_names.append(temp_product)
            samples_cats.append(temp_cat)
            samples_lots.append(temp_lots)

    # Extract results
    results = [] # Placeholder for results
    for i, result in enumerate(tables[-1][1:]):
        results.append(result[2])

    # TODO: Extract the rest of the data

    data["Test Name"] = ' '.join(test_name.split())
    data["Test Number"] = test_number
    data["Samples"]["Products"] = samples_names
    data["Samples"]["CAT#"] = samples_cats
    data["Samples"]["LOT#"] = samples_lots
    data["Results"] = results

    return data
