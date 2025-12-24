# SPDX-FileCopyrightText: Copyright (c) 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import List, Union, Optional, Literal
import numpy as np
import numpy.typing as npt
import pandas as pd


def assign_boxes(
    box: Union[List[float], npt.NDArray[np.float64]],
    candidate_boxes: npt.NDArray[np.float64],
    delta: float = 2.0,
    min_overlap: float = 0.25,
    mode: Literal["cell", "row", "column"] = "cell",
) -> npt.NDArray[np.int_]:
    """
    Assigns the best candidate boxes to a reference `box` based on overlap.

    If mode is "cell", the overlap is calculated using surface area overlap.
    If mode is "row", the overlap is calculated using row height overlap.
    If mode is "column", the overlap is calculated using column width overlap.

    If delta > 1, it will look for multiple matches,
    using candidates with score >= max_overlap / delta.

    Args:
        box (list or numpy.ndarray): Reference bounding box [x_min, y_min, x_max, y_max].
        candidate_boxes (numpy.ndarray [N, 4]): Array of candidate bounding boxes.
        delta (float, optional): Factor for matches relative to the best overlap. Defaults to 2.0.
        min_overlap (float, optional): Minimum required overlap for a match. Defaults to 0.25.
        mode (str, optional): Mode to assign boxes ("cell", "row", or "column"). Defaults to "cell".

    Returns:
        numpy.ndarray [M]: Indices of the matched boxes sorted by decreasing overlap.
                          Returns an empty array if no matches are found.
    """
    if not len(candidate_boxes):
        return np.array([], dtype=np.int_)

    x0_1, y0_1, x1_1, y1_1 = box
    x0_2, y0_2, x1_2, y1_2 = (
        candidate_boxes[:, 0],
        candidate_boxes[:, 1],
        candidate_boxes[:, 2],
        candidate_boxes[:, 3],
    )

    # Intersection
    inter_y0 = np.maximum(y0_1, y0_2)
    inter_y1 = np.minimum(y1_1, y1_2)
    inter_x0 = np.maximum(x0_1, x0_2)
    inter_x1 = np.minimum(x1_1, x1_2)

    if mode == "cell":
        inter_area = np.maximum(0, inter_y1 - inter_y0) * np.maximum(0, inter_x1 - inter_x0)
        box_area = (y1_1 - y0_1) * (x1_1 - x0_1)
        overlap = inter_area / (box_area + 1e-6)
    elif mode == "row":
        inter_area = np.maximum(0, inter_y1 - inter_y0)
        box_area = y1_1 - y0_1
        overlap = inter_area / (box_area + 1e-6)
    elif mode == "column":
        inter_area = np.maximum(0, inter_x1 - inter_x0)
        box_area = x1_1 - x0_1
        overlap = inter_area / (box_area + 1e-6)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    max_overlap = np.max(overlap)
    if max_overlap <= min_overlap:  # No match
        return np.array([], dtype=np.int_)

    n = len(np.where(overlap >= (max_overlap / delta))[0]) if delta > 1 else 1
    matches = np.argsort(-overlap)[:n]
    return matches


def merge_text_in_cell(df_cell: pd.DataFrame) -> pd.DataFrame:
    """
    Merges text from multiple rows into a single cell and recalculates its bounding box.
    Values are sorted by rounded (y, x) coordinates.

    Args:
        df_cell (pandas.DataFrame): DataFrame containing cells to merge.

    Returns:
        pandas.DataFrame: Updated DataFrame with merged text and a single bounding box.
    """
    boxes = np.stack(df_cell["box"].values)

    df_cell["x"] = (boxes[:, 0] - boxes[:, 0].min()) // 10
    df_cell["y"] = (boxes[:, 1] - boxes[:, 1].min()) // 10
    df_cell = df_cell.sort_values(["y", "x"])

    text = " ".join(df_cell["text"].values.tolist())
    df_cell["text"] = text
    df_cell = df_cell.head(1)
    df_cell["box"] = df_cell["cell"]
    df_cell.drop(["x", "y"], axis=1, inplace=True)

    return df_cell


def remove_empty_row(mat: List[List[str]]) -> List[List[str]]:
    """
    Remove empty rows from a matrix.

    Args:
        mat (list[list]): The matrix to remove empty rows from.

    Returns:
        list[list]: The matrix with empty rows removed.
    """
    mat_filter = []
    for row in mat:
        if max([len(c) for c in row]):
            mat_filter.append(row)
    return mat_filter


def build_markdown(
    df: pd.DataFrame,
    remove_empty: bool = True,
    n_rows: Optional[int] = None,
    repeat_single: bool = False,
) -> Union[List[List[str]], npt.NDArray[np.str_]]:
    """
    Convert a dataframe into a markdown table.

    Args:
        df (pandas.DataFrame): The dataframe to convert with columns 'col_ids',
            'row_ids', and 'text'.
        remove_empty (bool, optional): Whether to remove empty rows & cols. Defaults to True.
        n_rows (int, optional): Number of rows. Inferred from df if None. Defaults to None.
        repeat_single (bool, optional): Whether to repeat single element in rows.
            Defaults to False.

    Returns:
        list[list[str]] or numpy.ndarray: A list of lists or array representing the markdown table.
    """
    df = df.reset_index(drop=True)
    n_cols = max([np.max(c) for c in df['col_ids'].values])
    if n_rows is None:
        n_rows = max([np.max(c) for c in df['row_ids'].values])
    else:
        n_rows = max(
            n_rows - 1,
            max([np.max(c) for c in df['row_ids'].values])
        )

    mat = np.empty((n_rows + 1, n_cols + 1), dtype=str).tolist()

    for i in range(len(df)):
        if isinstance(df["row_ids"][i], int) or isinstance(df["col_ids"][i], int):
            continue
        for r in df["row_ids"][i]:
            for c in df["col_ids"][i]:
                mat[r][c] = (mat[r][c] + " " + df["text"][i]).strip()

    # Remove empty rows & columns
    if remove_empty:
        mat = remove_empty_row(mat)
        mat = np.array(remove_empty_row(np.array(mat).T.tolist())).T.tolist()

    if repeat_single:
        new_mat = []
        for row in mat:
            if sum([len(c) > 0 for c in row]) == 1:
                txt = [c for c in row if len(c)][0]
                new_mat.append([txt for _ in range(len(row))])
            else:
                new_mat.append(row)
        mat = np.array(new_mat)

    return mat


def display_markdown(
    data: List[List[str]], show: bool = True, use_header: bool = True
) -> str:
    """
    Convert a list of lists of strings into a markdown table.
    If show is True, use_header will be set to True.

    Args:
        data (list[list[str]]): The table data. The first sublist should contain headers.
        show (bool, optional): Whether to display the table. Defaults to True.
        use_header (bool, optional): Whether to use the first sublist as headers. Defaults to True.

    Returns:
        str: A markdown-formatted table as a string.
    """
    if show:
        use_header = True
        data = [[re.sub(r'\n', ' ', c) for c in row] for row in data]

    if not len(data):
        return "EMPTY TABLE"

    max_cols = max(len(row) for row in data)
    data = [row + [""] * (max_cols - len(row)) for row in data]

    if use_header:
        header = "| " + " | ".join(data[0]) + " |"
        separator = "| " + " | ".join(["---"] * max_cols) + " |"
        body = "\n".join("| " + " | ".join(row) + " |" for row in data[1:])
        markdown_table = (
            f"{header}\n{separator}\n{body}" if body else f"{header}\n{separator}"
        )

        if show:
            from IPython.display import display, Markdown
            markdown_table = re.sub(r'\$', r'\\$', markdown_table)
            markdown_table = re.sub(r'\%', r'\\%', markdown_table)
            display(Markdown(markdown_table))

    else:
        markdown_table = "\n".join("| " + " | ".join(row) + " |" for row in data)

    return markdown_table
