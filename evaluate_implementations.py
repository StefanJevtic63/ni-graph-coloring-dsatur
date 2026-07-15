"""Module for evaluating the performance of different DSatur implementations on generated input files.
The evaluation measures the execution time and the ratio of additional colors used compared to the optimal coloring for each input graph.
The results of the evaluation are saved in a Excel file for easier comparison and analysis of the different implementations.

The input files can be found on the following website: https://www.cs.haifa.ac.il/~oren/graph-coloring/benchmarks.html
"""

import networkx as nx
import pandas as pd
from os import path, listdir, remove
from time import time
from openpyxl.utils import get_column_letter

from dsatur.DSaturBase import DSaturBase
from dsatur.DSaturStandard import DSaturStandard
from dsatur.DSaturBinHeap import DSaturBinHeap
from dsatur.DSaturFibHeap import DSaturFibHeap

from constants import EVAL_INPUT_DIR, CSV_FILE_PATH_TEMPLATE, CSV_FILE_HEADER, OPTIMAL_COLORING_DICT
from utility import read_graph_from_file


def create_csv_file(
    file_path: str,
    content: list[str]
) -> None:
    """Creates and populates the CSV file at the specified path with the given content.

    Args:
        file_path (str): The path where the CSV file will be created.
        content (list[str]): The content to write into the CSV file, where each string represents a line.

    Returns:
        None
    """
    with open(file_path, "w", encoding="utf-8") as file:
        data: list[str] = [CSV_FILE_HEADER] + content
        file.write("\n".join(data))

def evaluate(
    concrete_implementation_class: type[DSaturBase],
    input_dir: str = EVAL_INPUT_DIR,
) -> None:
    """Evaluates the given DSatur implementation on the generated input files by measuring the 
    execution time and the ratio of additional colors used compared to the optimal coloring for each input graph.
    
    Args:
        concrete_implementation_class (type[DSaturBase]): The DSatur implementation class to evaluate.
        input_dir (str): The directory where the input files are located. Defaults to EVAL_INPUT_DIR.

    Returns:
        None
    """
    implementation_name: str = concrete_implementation_class.__name__
    csv_file_name: str = CSV_FILE_PATH_TEMPLATE.format(implementation_name)
    content: list[str] = []

    for file_name in listdir(input_dir):
        if not file_name.endswith(".txt"):
            continue

        file_path: str = path.join(input_dir, file_name)
        G: nx.Graph = read_graph_from_file(file_path=file_path)
        instance: DSaturBase = concrete_implementation_class(G=G, input_file_name=file_name)
        
        current_time: float = time()
        instance.solve()
        elapsed_time: float = time() - current_time
        ratio_incorrect: float = instance.evaluate()

        # Ekstrakcija metapodataka o grafu
        nodes_count: int = G.number_of_nodes()
        edges_count: int = G.number_of_edges()
        optimal_num_colors: int | str = OPTIMAL_COLORING_DICT.get(file_name, "N/A")

        content.append(
            f"{implementation_name},{file_name},{nodes_count},{edges_count},"
            f"{optimal_num_colors},{elapsed_time:.4f},{ratio_incorrect:.4f}"
        )

    create_csv_file(
        file_path=csv_file_name,
        content=content
    )

def merge_csv_files() -> None:
    """Merges the evaluation results from all DSatur implementations into a single CSV file.
    
    Returns:
        None
    """
    merged_file_path: str = CSV_FILE_PATH_TEMPLATE.format("final")
    if path.exists(merged_file_path):
        remove(merged_file_path)

    merged_content: list[str] = []
    for file_name in listdir("."): 
        if file_name.endswith(".csv"):
            with open(file_name, "r", encoding="utf-8") as file:
                lines: list[str] = [line.strip() for line in file.readlines()[1:]]  # Skip header
                merged_content.extend(lines)

            remove(file_name)

    create_csv_file(
        file_path=merged_file_path,
        content=merged_content
    )

def convert_csv_to_excel(csv_file_path: str, excel_file_path: str) -> None:
    """Converts a CSV file to an Excel file with pivoted metrics, meta columns, and applies AutoFit.

    Args:
        csv_file_path (str): The path to the input CSV file.
        excel_file_path (str): The path where the output Excel file will be saved.

    Returns:
        None
    """
    if path.exists(excel_file_path):
        remove(excel_file_path)

    df: pd.DataFrame = pd.read_csv(csv_file_path)

    meta_df: pd.DataFrame = df.drop_duplicates(subset=["File Name"])[
        ["File Name", "Nodes", "Edges", "Optimal Num Colors"]
    ].set_index("File Name")

    time_df: pd.DataFrame = df.pivot(
        index="File Name",
        columns="Implementation",
        values="Elapsed Time (s)"
    )
    ratio_df: pd.DataFrame = df.pivot(
        index="File Name",
        columns="Implementation",
        values="Ratio of Additional Colors"
    )

    result: pd.DataFrame = pd.DataFrame(index=time_df.index)

    result["nodes"] = meta_df["Nodes"]
    result["edges"] = meta_df["Edges"]
    result["optimal_num_colors"] = meta_df["Optimal Num Colors"]

    result["standard_time"] = time_df["DSaturStandard"]
    result["binary_heap_time"] = time_df["DSaturBinHeap"]
    result["fibonacci_heap_time"] = time_df["DSaturFibHeap"]

    result["standard_ratio"] = ratio_df["DSaturStandard"]
    result["binary_heap_ratio"] = ratio_df["DSaturBinHeap"]
    result["fibonacci_heap_ratio"] = ratio_df["DSaturFibHeap"]

    result.reset_index(inplace=True)
    result.rename(columns={"File Name": "input_file"}, inplace=True)

    with pd.ExcelWriter(excel_file_path, engine="openpyxl") as writer:
        result.to_excel(writer, sheet_name="Results", index=False)
        worksheet = writer.sheets["Results"]

        for col in worksheet.columns:
            max_len: int = max(len(str(cell.value or "")) for cell in col)
            col_letter: str = get_column_letter(col[0].column)
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 10)

    remove(csv_file_path)

def main() -> None:
    """Main function to generate input files and perform the evaluation for all of the DSatur implementations.
    The evaluation consists of running each implementation on the generated input files and measuring the execution time,
    as well as the ratio of the incorrectly colored nodes to the total number of nodes in the graph.
    
    The results of the evaluation are saved in a CSV file for further analysis.

    Returns:
        None
    """
    evaluate(concrete_implementation_class=DSaturStandard, input_dir=EVAL_INPUT_DIR)
    evaluate(concrete_implementation_class=DSaturBinHeap, input_dir=EVAL_INPUT_DIR)
    evaluate(concrete_implementation_class=DSaturFibHeap, input_dir=EVAL_INPUT_DIR)

    merge_csv_files()

    convert_csv_to_excel(
        csv_file_path=CSV_FILE_PATH_TEMPLATE.format("final"),
        excel_file_path=CSV_FILE_PATH_TEMPLATE.format("final").replace(".csv", ".xlsx")
    )

if __name__ == "__main__":
    main()