import os
import tempfile
import multiprocessing as mp

from .adjacency_g6 import _structure_to_g6_optimized_worker
from .structures import generate_connected_cotree_structures, generate_all_cotree_structures
from .visualization import render_cotree_jpg


def generate_cographs_final_g6(
        node_count: int,
        output_filename: str = "cographs",
        connected_only: bool = True,
) -> str:
    """
    Generate cographs with ``node_count`` vertices and save them in graph6 format.

    The output file will always have the `.g6` extension, regardless of whether
    the user includes it or not.

    Parameters
    ----------
    node_count : int
        Number of vertices in the cographs to generate.
    output_filename : str, optional
        Base name or filename for the final graph6 output (extension optional).
    connected_only : bool, optional
        If True, generate only connected cographs (root operator 'J').
        If False, generate all cographs (connected + disconnected).

    Returns
    -------
    str
        Path of the output file containing graph6 strings.
    """

    total_structures = 0
    total_graph6 = 0

    if not output_filename.lower().endswith(".g6"):
        output_filename += ".g6"

    num_processes = max(1, mp.cpu_count() // 3)

    if connected_only:
        generator = generate_connected_cotree_structures
    else:
        generator = generate_all_cotree_structures

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_filename = temp.name

        for structure in generator(node_count, 0):
            temp.write(structure + "\n")
            total_structures += 1

    with open(temp_filename, "r") as f_in, open(output_filename, "w") as f_out:
        with mp.Pool(num_processes) as pool:
            for g6 in pool.imap(
                    _structure_to_g6_optimized_worker,
                    f_in,
                    chunksize=100
            ):
                f_out.write(g6.strip() + "\n")
                total_graph6 += 1

    os.remove(temp_filename)

    return output_filename


def generate_cographs_g6(
        node_count: int,
        connected_only: bool = True,
) -> list[str]:
    """
    Generate cographs in graph6 format using parallel processing,
    returning all results in memory (no batching, no temporary files).

    Parameters
    ----------
    node_count : int
        Number of vertices.
    connected_only : bool, optional
        If True, generate only connected cographs.

    Returns
    -------
    list[str]
        All graph6 strings generated.
    """

    # Use 1/3 of available CPU cores (minimum 1)
    num_processes = max(1, mp.cpu_count() // 3)

    if connected_only:
        generator = generate_connected_cotree_structures
    else:
        generator = generate_all_cotree_structures

    results: list[str] = []

    with mp.Pool(num_processes) as pool:
        for g6 in pool.imap_unordered(
                _structure_to_g6_optimized_worker,
                generator(node_count, 0),
                chunksize=100
        ):
            results.append(g6)

    return results


def generate_cotree_images(
        node_count: int,
        output_dir: str = "cotree_images"
) -> int:
    """
    Generate JPG files for all canonical cotrees with the specified number of leaves.
    Structures are produced by ``generate_all_cotree_structures`` and rendered by
    ``render_cotree_jpg``.

    Parameters
    ----------
    node_count : int
        Number of leaves in the cotrees.
    output_dir : str, optional
        Directory where the JPG files will be saved.

    Returns
    -------
    int
        Total number of images generated.
    """
    total = 0
    for structure in generate_all_cotree_structures(node_count, 0):
        render_cotree_jpg(structure, node_count, output_dir)
        total += 1
    return total
