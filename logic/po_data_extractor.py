import re
from PyPDF2 import PdfReader

def extract_surface_test_data(pdf_path):

    # Read the PDF content
    reader = PdfReader(pdf_path)
    content = "\n".join(page.extract_text() for page in reader.pages)
    content_split = content.split("\n") # split PdfReader into lines

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
    results_block_pattern = r"Test Result\s*(.*?)\s*Interpretation of sample"  # used to extract results block
    results_pattern = r"^(.+?)\s+((?:[<>]=?\s*)?\d+(?:\.\d+)?)$" # used to extract results

    test_data_pattern = r"\w+\s*\w*\s*\w{3}-\w{6}-\w{2}\s+[\w/\s-]*?(?=/[A-Z]|$)" # used to extract sample data
    # product_name_pattern = r"\w+\s*\w*(?=\w{3}-\w{6}-\w{2})"
    product_name_pattern = r"[a-zA-z ]*\s+(?=\w{3}-\w{6}-\w{2})"
    cat_block_pattern = r"\w{3}-\w{6}-\w{2}.*?(?=\w{3}-\w{6}-\w{2}|$)"
    cat_number_pattern =r"\w{3}-\w{6}-\w{2}"
    lot_numbers_pattern = r"(?<=\w{3}-\w{6}-\w{2})\s*(.*)"
    # lot_numbers_pattern = r"(?<=\w{3}-\w{6}-\w{2})\s*(\d+|AMP-\d+-\d+|M\d+|\d+A|\d+N)"
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

    # Extract Test number
    test_number = re.findall(test_number_pattern, content_split[4])[0]

    # Extract Report Date
    report_date = re.findall(report_date_pattern, content_split[5])[0]

    # Extract Number of Samples
    number_of_samples = re.findall(number_of_samples_pattern, content_split[6])[0]

    # Extract Test Name
    test_name = re.findall(test_name_pattern, content_split[7])[0]

    # Extract Purchase Order
    purchase_order = re.findall(purchase_order_pattern, content_split[8])[0]

    # Extract Date Received
    date_received = re.findall(date_received_pattern, content_split[9])[0]

    # Extract date of sample
    date_of_sample = re.findall(date_of_sample_pattern, content_split[10])[0]

    # Extract State of Sample
    state_of_sample = re.findall(state_of_sample_pattern, content_split[11])[0]

    # Extract Substance Sampled
    substance_sampled = re.findall(substance_sampled_pattern, content_split[12])[0]

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
        
    products = re.findall(test_data_pattern, cat_lot_block) # extracting sample data
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

def extract_air_test_data(pdf_path):

    # Read the PDF content
    reader = PdfReader(pdf_path)
    content = "\n".join(page.extract_text() for page in reader.pages)
    content_split = content.split("\n") # split PdfReader into lines

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
    results_pattern = r"^(.+?)\s+((?:[<>]=?\s*)?\d+(?:\.\d+)?)$" # used to extract results

    test_data_pattern = r"\w+\s*\w*\s*\w{3}-\w{6}-\w{2}\s+[\w/-]*(?=/[A-Z]|$)" # used to extract sample data
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

    # Extract Test number
    test_number = re.findall(test_number_pattern, content_split[4])[0]

    # Extract Report Date
    report_date = re.findall(report_date_pattern, content_split[5])[0]

    # Extract Number of Samples
    number_of_samples = re.findall(number_of_samples_pattern, content_split[6])[0]

    # Extract Test Name
    test_name = re.findall(test_name_pattern, content_split[7])[0]

    # Extract Purchase Order
    purchase_order = re.findall(purchase_order_pattern, content_split[8])[0]

    # Extract Date Received
    date_received = re.findall(date_received_pattern, content_split[9])[0]

    # Extract date of sample
    date_of_sample = re.findall(date_of_sample_pattern, content_split[10])[0]

    # Extract State of Sample
    state_of_sample = re.findall(state_of_sample_pattern, content_split[11])[0]

    # Extract Substance Sampled
    substance_sampled = re.findall(substance_sampled_pattern, content_split[12])[0]

    # Extract samples LOT# and CAT#
    parsed_cat_lot = {
        "Products": [],
        "CAT#": [],
        "LOT#": []
    }

    # Extracting data block
    cat_lot_block = content_split[24]
    items = re.findall(test_data_pattern, cat_lot_block) # extracting sample data
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

def extract_peel_test_data(ocr_output):
    """
    Extract numerical results for "Result X" patterns from the OCR output.
    """

    # split ocr_output into lines
    ocr_output_split = ocr_output.split("\n")

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
    
    # regex patterns to extract data
    report_date_pattern = r"Date\s+of\s+report\s*:\s*(\d{2}.\d{2}.\d{2})"
    test_number_pattern = r"Laboratory\s+Number:\s+(.*)"
    purchase_order_pattern = r"Order\s+Number\s*:\s*(\d*)"
    production_date_pattern = r"Production:\s*(.*)"
    product_data_pattern = r"(\w+\s*\w*)\s+(\w{3}-\w{6}-\w{2})\s+Lot:\s*(.*)" ## 3 groups for name, CAT and LOT
    date_received_pattern = r"Date\s+sample\s+received:\s+(.*)"
    date_test_start_pattern = r"Beginning\s+of\s+Test:\s+(.*)"
    date_test_end_pattern = r"End\s+of\s+Test:\s+(.*)"
    result_pattern = r"Result\s*\d.*?(\d+.\d+)"

    # Extraction
    # Loop over the lines in the OCR output to extract data
    # First, find the index of the test name line and use it as a guide for the rest of the data (except for results)
    for i, line in enumerate(ocr_output_split):
        if "test" in line.lower():
            test_name_index = i
            break
    
    test_name = ocr_output_split[test_name_index]
    report_date = re.search(report_date_pattern, ocr_output_split[test_name_index + 3]).groups()[0]
    test_number = re.search(test_number_pattern, ocr_output_split[test_name_index + 4]).groups()[0]
    purchase_order = re.search(purchase_order_pattern, ocr_output_split[test_name_index + 5]).groups()[0]
    production_date = re.search(production_date_pattern, ocr_output_split[test_name_index + 5]).groups()[0]

    # Extract sample description
    # iterate over the products of the samples
    samples_index = test_name_index + 6
    while True:
        samples_temp_data = re.findall(product_data_pattern, ocr_output_split[samples_index])
        if samples_temp_data:
            data["Samples"]["Products"].append(samples_temp_data[0][0])
            data["Samples"]["CAT#"].append(samples_temp_data[0][1])
            data["Samples"]["LOT#"].append(samples_temp_data[0][2])
            samples_index += 1
        else:
            break
        
    # Extract results
    # Finding the index for the results
    for i, line in enumerate(ocr_output_split):
        if "conclusions" in line.lower():
            results_index = i - 2 # results are the two lines before conclusions
            break
    
    # First result
    first_result = re.findall(result_pattern, ocr_output_split[results_index])[0]
    data["Results"].append(["Result 1", first_result])
    # Second result
    second_result = re.findall(result_pattern, ocr_output_split[results_index + 1])[0]
    data["Results"].append(["Result 2", second_result])
        
    # Modifying test number to the correct format, OCR does not recognize the first 2 characters correctly
    if test_number[1] == "0":
        test_number = "SO" + test_number[1:]

    data["Test Name"] = ' '.join(test_name.split())
    data["Report Date"] = report_date
    data["Test Number"] = test_number
    data["Purchase Order"] = purchase_order
    data["Production Date"] = production_date

    return data

def extract_microbiological_test_data(ocr_output):

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

    # Regex patterns for data extraction
    lot_number_pattern = r"(?:AMP-)?M?\d{5,6}A?N?(?:-\d{2})?"

    # Indecies placeholders
    test_name_index = None
    test_number_index = None
    samples_block_index = None
    sample_products_index = None
    sample_CAT_index = None
    sample_LOT_index = None
    cleaning_batches_block_index = None
    results_start_index = None
    results_end_index = None

    # Iterating over the output to find required indecies
    for i, line in enumerate(ocr_output):
        if not test_name_index:
            if "Test" in line:
                test_name_index = i

        elif not test_number_index:
            if "Laboratory" in line:
                test_number_index = i + 1

        elif not samples_block_index:
            if "Samples" in line:
                samples_block_index = i

        elif not sample_products_index:
            if "Product" in line:
                sample_products_index = i
        
        elif not sample_CAT_index:
            if "CAT#" in line:
                sample_CAT_index = i
        
        elif not sample_LOT_index:
            if "LOT#" in line:
                sample_LOT_index = i
        
        elif not cleaning_batches_block_index:
            if "Cleaning" in line:
                cleaning_batches_block_index = i

        elif not results_start_index:
            if "Corrected" in line:
                results_start_index = i + 1

        elif not results_end_index:
            if "*" in line:
                results_end_index = i
        else:
            break
    
    # test name and number placeholders
    data["Test Name"] = ocr_output[test_name_index]
    data["Test Number"] = "SO" + ocr_output[test_number_index][2:] # the OCR recognizes "O" as 0, so we adjust that here
    
    # Extracting Samples Data
    # Extracting products
    for i, product in enumerate(ocr_output[samples_block_index + 1:sample_products_index]):
        data["Samples"]["Products"].append(product)

    # Extracting CAT#
    for i, cat in enumerate(ocr_output[sample_products_index + 1:sample_CAT_index]):
        data["Samples"]["CAT#"].append(cat)

    # Extracting LOT#
    for i, lot in enumerate(ocr_output[sample_CAT_index + 1:sample_LOT_index]):
        if re.search(lot_number_pattern, lot):
            data["Samples"]["LOT#"].append(lot)

    # Extracting results
    lot_number_exists = False # bool to check if there's a lot number in the results
    if re.fullmatch(lot_number_pattern, ocr_output[results_start_index + 1]):
        lot_number_exists = True

    for i, result in enumerate(ocr_output[results_start_index + 2 if lot_number_exists else results_start_index + 1 : results_end_index : 3 if lot_number_exists else 2]):
        result = result.replace("l", "1")
        data["Results"].append([f"Sample {i + 1}", result])

    return data
