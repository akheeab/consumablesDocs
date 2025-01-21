# import pandas as pd

def log_data_to_excel(results_structure, output_path="test_results.xlsx"):
    # """
    # Writes the structured results data into an Excel file with separate sheets for each test.
    # """
    # with pd.ExcelWriter(output_path) as writer:
    #     for test_name, test_data in results_structure.items():
    #         if "Samples" in test_data:
    #             df = pd.DataFrame(test_data["Samples"])
    #         elif "Results" in test_data:
    #             df = pd.DataFrame(test_data["Results"])
    #         else:
    #             df = pd.DataFrame()
    #         df.to_excel(writer, sheet_name=test_name[:31], index=False)
    # print(f"Results written to {output_path}")
    pass
