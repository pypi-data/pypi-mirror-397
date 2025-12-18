import base64
import copy
import glob
import json
import os
import random
import re
import tempfile
import webbrowser
from collections import Counter
from io import BytesIO

import cv2
import harmonypy as harmonize
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.offline as pyo
import seaborn as sns
import skimage
import umap
from csbdeep.utils import normalize
from skimage import measure
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from stardist.models import StarDist2D
from stardist.plot import render_label
from tqdm import tqdm

pio.renderers.default = "browser"

import jimg_ncd.config as cfg

from .utils import *

random.seed(42)


# new features (nuclei adjustment and repair images)


class RepTools:
    """
    A utility class for processing and repairing nuclei data.
    Provides methods for extracting subsets, removing outliers, computing geometrical features,
    and merging/splitting nuclei based on spatial and intensity criteria.
    """

    def extract_dict_by_indices(self, d, indices):
        """
        Extracts elements from all dictionary lists using provided indices.

        Parameters
        ----------
        d : dict
            Dictionary with list values.

        indices : list
            List of indices to extract from each dictionary entry.

        Returns
        -------
        dict
            Dictionary containing only the selected elements.
        """

        return {
            key: [values[i] for i in indices if i < len(values)]
            for key, values in d.items()
        }

    def drop_outlires(self, row, diff_FC_intensity=0.95, circ=0.6):
        """
        Identify indices of nuclei that are considered outliers based on circularity and intensity.

        Parameters
        ----------
        row : dict
            Dictionary containing nuclei properties, including 'circularity' and 'intensity_mean'.

        diff_FC_intensity : float
            Fraction of mean intensity below which a nucleus is considered an outlier.

        circ : float
            Minimum circularity threshold for nuclei to be considered.

        Returns
        -------
        list
            List of indices to drop as outliers.
        """

        cd = []
        for n, _ in enumerate(row["circularity"]):
            if row["circularity"][n] > circ:
                cd.append(n)

        row = self.extract_dict_by_indices(row, cd)

        drop = []
        is_mean = np.mean(row["intensity_mean"])

        for n, _ in enumerate(row["intensity_mean"]):
            FC_mean = row["intensity_mean"][n] / is_mean
            if FC_mean < diff_FC_intensity:
                drop.append(n)

        return drop

    def nn(self, coords):
        """
        Compute close neighbors between nuclei coordinates using a threshold distance.

        Parameters
        ----------
        coords : list
            List of numpy arrays, each containing coordinates for a nucleus.

        Returns
        -------
        dict
            Dictionary mapping pairs of nuclei indices to the number of close neighbors.
        """

        full_list = {}
        for i in range(len(coords)):
            for j in range(len(coords)):
                if i != j:

                    tree1 = cKDTree(coords[i])

                    distances, indices = tree1.query(coords[j])

                    threshold = 2
                    close_neighbors = np.sum(distances < threshold)

                    full_list[f"{i} --> {j}"] = close_neighbors

        return full_list

    def compute_axes_length(self, contour):
        """
        Compute major and minor axis lengths of a nucleus from its contour.

        Parameters
        ----------
        contour : np.ndarray
            Coordinates of nucleus contour points.

        Returns
        -------
        tuple
            Major and minor axis lengths.
        """

        cov = np.cov(contour.T)

        eigvals, _ = np.linalg.eigh(cov)

        axis_major_length = 2 * np.sqrt(eigvals.max())
        axis_minor_length = 2 * np.sqrt(eigvals.min())

        return axis_major_length, axis_minor_length

    def compute_eccentricity(self, contour):
        """
        Compute eccentricity of a nucleus from its contour.

        Parameters
        ----------
        contour : np.ndarray
            Coordinates of nucleus contour points.

        Returns
        -------
        float
            Eccentricity of the nucleus.
        """

        cov = np.cov(contour.T)
        eigvals, _ = np.linalg.eigh(cov)

        eccentricity = np.sqrt(1 - (eigvals.min() / eigvals.max()))
        return eccentricity

    def compute_feret_diameter(self, contour):
        """
        Compute the Feret diameter of a given contour.

        The Feret diameter is defined as the maximum pairwise Euclidean distance between points in the contour.

        Parameters
        ----------
        contour : np.ndarray
            Array of shape (N, 2) representing the contour coordinates.

        Returns
        -------
        float
            The maximum distance between any two points in the contour.
        """

        rect = cv2.minAreaRect(contour)
        (w, h) = rect[1]
        return max(w, h)

    def compute_perimeter(self, contour):
        """
        Compute the perimeter of a contour.

        The perimeter is calculated as the sum of Euclidean distances between consecutive points in the contour.

        Parameters
        ----------
        contour : np.ndarray
            Array of shape (N, 2) representing the contour coordinates.

        Returns
        -------
        float
            Perimeter length of the contour.
        """

        return np.sum(np.linalg.norm(np.diff(contour, axis=0), axis=1))

    def compute_circularity(self, contour):
        """
        Compute the circularity of a contour.

        Circularity is a measure of how close the shape is to a perfect circle.
        It is calculated as 4 * pi * (area / perimeter^2).

        Parameters
        ----------
        contour : np.ndarray
            Array of shape (N, 2) representing the contour coordinates.

        Returns
        -------
        float
            Circularity of the contour. Value ranges from 0 to 1, where 1 indicates a perfect circle.
        """
        perimeter = self.compute_perimeter(contour)
        hull = ConvexHull(contour)
        area = hull.volume

        return (4 * np.pi * area) / (perimeter**2)

    def repairing_nuclei(self, results):
        """
        Repair nuclei segmentation results by merging or removing outlier nuclei.

        This method adjusts nuclei detection results based on global and local thresholds, circularity, nearest neighbor relationships,
        and merges small or fragmented nuclei when appropriate. It also recalculates key morphological properties for merged nuclei.

        Parameters
        ----------
        results : dict
            Dictionary where keys are image identifiers and values are dictionaries containing detected nuclei properties
            (e.g., 'area', 'coords', 'label', 'circularity', etc.).

        Returns
        -------
        dict
            A dictionary in the same structure as `results`, but with repaired nuclei information after merging or removing outliers.
        """

        # repairing nuclei
        mean_sum_area = []
        im = []
        n = []
        for r in tqdm(results.keys()):
            mean_sum_area.append(np.sum(results[r]["area"]))
            n.append(len(results[r]["area"]))
            im.append(r)

        mean_sum_area_sum = np.mean(mean_sum_area)

        results_dict = {}

        print("\nImage repairing:\n\n")

        for i, m in tqdm(zip(im, n), total=len(im)):

            if (
                m > 1
                and np.sum(results[i]["area"]) / mean_sum_area_sum
                < self.hyperparameter_nuclei["FC_diff_global"]
            ):
                # adjustment to global changes

                temporary_dict = results[i]

                check_drop = self.drop_outlires(
                    temporary_dict,
                    diff_FC_intensity=self.hyperparameter_nuclei[
                        "FC_diff_local_intensity"
                    ],
                    circ=self.hyperparameter_nuclei["circularity"],
                )

                to_final = [
                    x
                    for x in list(range(len(temporary_dict["area"])))
                    if int(x) not in check_drop
                ]

                tmp = self.extract_dict_by_indices(temporary_dict, to_final)

                to_concat = []

                if len(tmp["coords"]) > 1:

                    results_nn = self.nn(tmp["coords"])

                    for kn in results_nn.keys():
                        if results_nn[kn] > self.hyperparameter_nuclei["nn_min"]:
                            to_concat.append(int(re.sub(" --> .*", "", kn)))
                            to_concat.append(int(re.sub(".* --> ", "", kn)))

                    to_concat = list(set(to_concat))

                    to_rest = [
                        x for x in list(range(len(tmp["area"]))) if x not in to_concat
                    ]

                #
                if len(to_concat) > 1:
                    to_concat_dict = self.extract_dict_by_indices(tmp, to_concat)
                    to_concat_dict["coords"] = [np.vstack(to_concat_dict["coords"])]
                    to_concat_dict["label"] = [min(to_concat_dict["label"])]
                    to_concat_dict["area"] = [np.sum(to_concat_dict["area"])]
                    to_concat_dict["area_bbox"] = [np.sum(to_concat_dict["area_bbox"])]
                    to_concat_dict["area_convex"] = [
                        np.sum(to_concat_dict["area_convex"])
                    ]
                    to_concat_dict["area_filled"] = [
                        np.sum(to_concat_dict["area_filled"])
                    ]
                    to_concat_dict["intensity_max"] = [
                        np.max(to_concat_dict["intensity_max"])
                    ]
                    to_concat_dict["intensity_mean"] = [
                        np.mean(to_concat_dict["intensity_mean"])
                    ]
                    to_concat_dict["intensity_min"] = [
                        np.min(to_concat_dict["intensity_min"])
                    ]
                    major, minor = self.compute_axes_length(to_concat_dict["coords"][0])
                    to_concat_dict["axis_major_length"] = [major]
                    to_concat_dict["axis_minor_length"] = [minor]
                    to_concat_dict["ratio"] = [minor / major]
                    ecc = self.compute_eccentricity(to_concat_dict["coords"][0])
                    to_concat_dict["eccentricity"] = [ecc]
                    to_concat_dict["equivalent_diameter_area"] = [
                        np.sum(to_concat_dict["equivalent_diameter_area"])
                    ]
                    feret_diameter = self.compute_feret_diameter(
                        to_concat_dict["coords"][0]
                    )
                    to_concat_dict["feret_diameter_max"] = [feret_diameter]
                    to_concat_dict["solidity"] = [np.mean(to_concat_dict["solidity"])]
                    to_concat_dict["perimeter"] = [np.sum(to_concat_dict["perimeter"])]
                    to_concat_dict["perimeter_crofton"] = [
                        np.sum(to_concat_dict["perimeter_crofton"])
                    ]
                    to_concat_dict["circularity"] = [
                        np.mean(to_concat_dict["circularity"])
                    ]

                    to_rest_dict = self.extract_dict_by_indices(tmp, to_rest)

                    for ik in to_rest_dict.keys():
                        to_rest_dict[ik] = to_rest_dict[ik] + to_concat_dict[ik]

                    results_dict[i] = to_rest_dict

                else:
                    results_dict[i] = tmp

            elif (
                m == 1
                and results[i]["circularity"][0]
                > self.hyperparameter_nuclei["circularity"]
            ):

                results_dict[i] = results[i]

        return results_dict


class ImagesManagement:
    """
    A class for managing, preprocessing, merging, stitching, saving, and loading
    microscopy or flow cytometry images used in NucleiFinder-based analyses.

    This class provides a unified interface for:

    - loading image data,
    - selecting images by IDs,
    - preprocessing images (equalization, CLAHE, gamma/contrast/brightness adjustment),
    - merging images with user-defined intensity ratios,
    - stitching images horizontally,
    - retrieving and saving processed image sets.

    The class stores original or loaded data in the ``results_images`` attribute,
    and all processed images in ``prepared_images`` under user-defined acronyms.
    These acronyms allow flexible retrieval with ``get_prepared_images()``
    and exporting via ``save_prepared_images()``.

    Parameters
    ----------
    images_ids : list[int]
        List of selected image identifiers.

    result_dict : dict or None
        Dictionary containing raw or preprocessed images.
        If ``None``, images may later be loaded or processed from file.

    experiment_name : str
        Name of the experiment. Used for saving and structuring output.

    Attributes
    ----------
    images_ids : list[int]
        IDs of images managed by the class.

    results_images : dict or None
        Dictionary containing raw or analysis-derived images.

    experiment_name : str
        Name of the experiment. Used in saved filenames.

    prepared_images : dict
        Container for processed/adjusted/merged/stitched images,
        indexed by user-defined acronyms.

    Notes
    -----
    Processed images are stored only in memory until saved explicitly with
    ``save_prepared_images()``.

    Raw images loaded from NucleiFinder analyses can be saved for later reuse
    in a serialized `.inuc` format using ``save_raw()``.

    Examples
    --------
    Load image results from an analysis:

    >>> manager = ImagesManagement.load_experimental_images(results, "experiment1")

    Adjust selected images:

    >>> manager.adjust_images(
    ...     acronyme="adj",
    ...     path_to_images="path/to/imgs",
    ...     eq=True,
    ...     clahe=True
    ... )

    Merge multiple prepared sets:

    >>> manager.image_merging(["adj", "other"], ratio_list=[0.7, 0.3])

    Retrieve processed images:

    >>> imgs = manager.get_prepared_images("adj")

    Save stitched images to disk:

    >>> manager.save_prepared_images("stitched_adj_other", "./output/")
    """

    def __init__(self, images_ids, result_dict, experiment_name):
        """
        Initialize the ImagesManagement object.

        Parameters
        ----------
        images_ids : list[int]
            List of image identifiers.

        result_dict : dict or None
            Dictionary containing processed images.

        experiment_name : str
            Name of the experiment.
        """

        self.images_ids = images_ids
        """Stores the list of image IDs managed by this instance."""
        self.results_images = result_dict
        """Stores dictionary containing processed images."""
        self.experiment_name = experiment_name
        """Stores the experiment name for file naming and organizational purposes."""
        self.prepared_images = {}
        """Dictionary for storing processed images (adjusted, merged, stitched),
        indexed by user-defined acronyms for flexible retrieval."""

    @classmethod
    def load_from_dict(cls, path: str, experiment_name: str):
        """
        Load an ImagesManagement instance from a `.inuc` serialized dictionary.

        Parameters
        ----------
        path : str
            Path to the `.inuc` file exported with `save_raw()`.

        experiment_name : str
            Name of the experiment.

        Returns
        -------
        ImagesManagement
            A reconstructed ImagesManagement object.
        """

        if ".inuc" in path:

            if os.path.exists(path):

                loaded_data = np.load(path)
                data_dict = {key: loaded_data[key] for key in loaded_data}

                id_list = []

                for k in data_dict.keys():
                    id_list.append(re.sub("_.*", "", k))

                return cls(id_list, data_dict, experiment_name)

            else:
                raise ValueError("\nInvalid path!")

        else:
            raise ValueError(
                "\nInvalid dictionary to load. It must contain a .inuc extension!"
            )

    @classmethod
    def load_experimental_images(cls, results_dict: dict, experiment_name: str):
        """
        Load results exported from NucleiFinder series analysis.

        Initialize the object with results from series_analysis_nuclei()
        or series_analysis_chromatinization() of the NucleiFinder class.


        Parameters
        ----------
        results_dict : dict
            Dictionary returned by `series_analysis_nuclei()` or
            `series_analysis_chromatinization()`.

        experiment_name : str
            Name of the experiment.

        Returns
        -------
        ImagesManagement

        """

        res_dict = {}
        id_list = []

        if set(results_dict[list(results_dict.keys())[0]].keys()) != set(
            ["stats", "img"]
        ):
            raise ValueError(
                "Incorrect data provided. The data must come from series_analysis_nuclei() "
                "or series_analysis_chromatinization() of the NucleiFinder class."
            )

        for k in results_dict.keys():
            res_dict[k] = results_dict[k]["img"]
            id_list.append(re.sub("_.*", "", k))

        return cls(id_list, res_dict, experiment_name)

    @classmethod
    def load_images_ids(cls, images_ids: list, experiment_name: str):
        """
        Initialize the object with list of images IDs for porcesing.

        Parameters
        ----------
        images_ids : list[int]
            List of selected image IDs.

        experiment_name : str
            Name of the experiment.

        Returns
        -------
        ImagesManagement

        """

        if len(images_ids) == 0:
            raise ValueError(
                "Incorrect data provided. There must be a list of image IDs."
            )

        return cls(images_ids, None, experiment_name)

    def get_included_acronyms(self):
        """
        Print the data acronyms for adjusted images, processed using the
        self.adjust_images(), self.image_merging(), and self.image_stitching() methods.

        Acronym information is essential for retrieving and saving data using
        the self.get_prepared_images() and self.save_prepared_images() methods.

        Notes
        -----
        This method prints the list of available acronyms but does not return it.

        """

        if len(self.prepared_images.keys()) > 0:
            print("\nAvaiable stored images:\n")
            for kd in self.prepared_images.keys():
                print(kd)

        else:
            print("Nothing to return!")

    def get_prepared_images(self, acronyme=None):
        """
        Retrieves the prepared images (returned from preapre_selected_img()) stored in the object.


        Parameters
        ----------
        acronyme : str or None
            Acronym identifying a processed image set. If None, prints available keys.


        Returns
        -------
        dict
            Dictionary of prepared images.
        """

        if acronyme is None:

            self.get_included_acronyms()

        else:

            if acronyme in list(self.prepared_images.keys()):
                return self.prepared_images[acronyme]

            raise ValueError("Incorrect acronyme!")

    def save_prepared_images(self, acronyme: str, path_to_save: str = ""):
        """
        Saves prepared images (returned from preapre_selected_img() method) to the specified directory.

        Parameters
        ----------
        path_to_save : str
            Directory path where the images will be saved. Default is the current working directory.

        """
        if acronyme is None:

            self.get_included_acronyms()

        else:

            if acronyme in list(self.prepared_images.keys()):

                path_to_save = os.path.join(
                    path_to_save, f"{self.experiment_name}_{acronyme}"
                )

                if not os.path.exists(path_to_save):
                    os.makedirs(path_to_save, exist_ok=True)

                for i in tqdm(self.prepared_images[acronyme].keys()):
                    cv2.imwrite(
                        os.path.join(path_to_save, i + ".png"),
                        self.prepared_images[acronyme][i],
                    )

            else:
                raise ValueError("Incorrect acronyme!")

    def adjust_images(
        self,
        acronyme: str,
        path_to_images: str,
        file_extension: str = "tif",
        eq: bool = True,
        clahe: bool = True,
        kernal: tuple = (50, 50),
        fille_name_part: str = "",
        color: str = "gray",
        max_intensity: int = 65535,
        min_intenisty: int = 0,
        brightness: int = 1000,
        contrast: float = 1.0,
        gamma: float = 1.0,
        img_n: int = 0,
    ):
        """
        Prepares selected images for processing, applying histogram equalization and CLAHE, if required.

        Parameters
        ----------
        acronyme : str
            Name of images being adjusted in this run.

        path_to_images : str
            Path to the directory containing images.

        file_extension : str
            Image file extension. Default is 'tiff'.

        eq : bool
            Whether to apply histogram equalization. Default is True.

        clahe : bool
            Whether to apply CLAHE. Default is True.

        kernal : tuple
            Kernel size for CLAHE. Default is (50, 50).

        fille_name_part : str
            Part of the file name to filter images. Default is an empty string.

        color : str
            Color space to use. Default is 'gray'.

        max_intensity : int
            Maximum intensity for image adjustment. Default is 65535.

        min_intenisty : int
            Minimum intensity for image adjustment. Default is 0.

        brightness : int
            Brightness adjustment value. Default is 1000.

        contrast : float
            Contrast adjustment factor. Default is 1.0.

        gamma : float
            Gamma correction factor. Default is 1.0.

        img_n : int
            Number of images to process. Default is 0, which means all images.


        Returns
        -------
        dict
            Dictionary containing the processed images.

        Notes
        -----
        To access the processed images, use the ``get_prepared_images()`` method.

        To save the processed images to disk, use the ``save_prepared_images()`` method.
        """

        results_dict = {}

        files = glob.glob(os.path.join(path_to_images, "*." + file_extension))

        if len(fille_name_part) > 0:
            files = [x for x in files if fille_name_part.lower() in x.lower()]

        selected_id = self.images_ids

        if len(selected_id) > 0:
            selected_id = [str(x) for x in selected_id]
            files = [
                x
                for x in files
                if re.sub("_.*", "", os.path.basename(x)) in selected_id
            ]

        if img_n > 0:

            files = random.sample(files, img_n)

        for file in tqdm(files):

            image = load_image(file)

            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            except:
                pass

            if eq is True:
                image = equalizeHist_16bit(image)

            if clahe is True:
                image = clahe_16bit(image, kernal=kernal)

            image = adjust_img_16bit(
                img=image,
                color=color,
                max_intensity=max_intensity,
                min_intenisty=min_intenisty,
                brightness=brightness,
                contrast=contrast,
                gamma=gamma,
            )

            results_dict[os.path.basename(file)] = image

        self.prepared_images[acronyme] = results_dict

    def image_merging(self, acronyms: list, ratio_list: list):
        """
        Merge previously prepared images stored in `self.prepared_images`,
        adjusted based on the image ratios. The used ratios adjust relative image intensity.

        Parameters
        ----------
        acronyme : list
            List of image names to be merged.

        ratio_list : list[float]
            List of ratio intensity values (0.0–1.0) for the merged image.
            The `acronyme` list and `ratio_list` must be of the same length.

        Returns
        -------
        dict
            Dictionary of processed images.

        Notes
        -----
        To access the processed images, use the ``get_prepared_images()`` method.

        To save the processed images to disk, use the ``save_prepared_images()`` method.
        """

        for a in acronyms:
            if a not in list(self.prepared_images.keys()):
                raise ValueError(f"Incorrect {a} acronyme!")

        results_img = {}
        for k in self.images_ids:
            img_list = []
            for a in acronyms:
                nam = [
                    x
                    for x in self.prepared_images[a].keys()
                    if str(k) == re.sub("_.*", "", x)
                ]
                if len(nam) == 0:
                    print(f"There were not images for {k} ids")
                    break

                img_list.append(self.prepared_images[a][nam[0]])

            if len(img_list) == len(acronyms):
                results_img[f'{k}_{"_".join(acronyms)}'] = merge_images(
                    img_list, ratio_list
                )

        self.prepared_images[f'merged_{"_".join(acronyms)}'] = results_img

        print(f'Images stored in self.prepared_images["merged_{"_".join(acronyms)}"]')

    def image_stitching(self, acronyms: list, to_results_image: bool = False):
        """
        Stitch (horizontally) previously prepared images stored in `self.prepared_images`.

        Parameters
        ----------
        acronyme : list
            List of image names to be stitched.

        to_results_image : bool
            Boolean value indicating whether images obtained from the
            `series_analysis_nuclei()` or `series_analysis_chromatinization()`
            methods of the `NucleiFinder` class should be stitched to the right
            side of the images in the `acronyme` list.

        Returns
        -------
        dict
            Dictionary of processed images.

        Notes
        -----
        To access the processed images, use the ``get_prepared_images()`` method.

        To save the processed images to disk, use the ``save_prepared_images()`` method.
        """

        for a in acronyms:
            if a not in list(self.prepared_images.keys()):
                raise ValueError(f"Incorrect {a} acronyme!")

        results_img = {}
        for k in tqdm(self.images_ids):
            img_list = []
            for a in acronyms:
                nam = [
                    x
                    for x in self.prepared_images[a].keys()
                    if str(k) == re.sub("_.*", "", x)
                ]
                if len(nam) == 0:
                    print(f"There were not images for {k} ids")
                    break

                img_list.append(self.prepared_images[a][nam[0]])

            if to_results_image:
                nam = [
                    x
                    for x in self.results_images.keys()
                    if str(k) == re.sub("_.*", "", x)
                ]
                if len(nam) != 0:
                    img_list.append(self.results_images[nam[0]])

                if len(img_list) == len(acronyms) + 1:
                    results_img[f'{k}_{"_".join(acronyms)}_res'] = cv2.hconcat(img_list)

            elif to_results_image is not False:
                if len(img_list) == len(acronyms):
                    results_img[f'{k}_{"_".join(acronyms)}'] = cv2.hconcat(img_list)

        self.prepared_images[f'stitched_{"_".join(acronyms)}'] = results_img

        print(f'Images stored in self.prepared_images["stitched_{"_".join(acronyms)}"]')

    def save_raw(self, path_to_save: str = ""):
        """
        Save `self.results_images` loaded by the `self.load_experimental_images()` method,
        obtained from the `series_analysis_nuclei()` or `series_analysis_chromatinization()`
        methods of the `NucleiFinder` class for later usage with cls.load_from_dict() method.
        The data will be saved with a `.inuc` extension.

        Parameters
        ----------
        path_to_save : str
            The directory path where the images will be saved.
            Default is the current working directory.
        """

        full_path = os.path.join(path_to_save, f"{self.experiment_name}.inuc")

        np.savez(full_path, **self.results_images)


class NucleiFinder(ImageTools, RepTools):
    """
    Implements a comprehensive pipeline for automated segmentation,
    selection, and analysis of cell nuclei and their internal chromatin structure
    in microscopy images.

    It utilizes a pre-trained deep learning model (StarDist2D) for initial
    nuclear identification, followed by the application of advanced morphological
    and intensity filters, and a dedicated algorithm for quantifying chromatinization.
    The class provides detailed control over the hyperparameters for both the
    segmentation process and image preprocessing stages.

    Parameters
    ----------
    image : np.ndarray, optional
        The input image (typically 16-bit) for analysis.

    test_results : list, optional
        Plots resulting from parameter testing (e.g., NMS/Prob combinations).

    hyperparameter_nuclei : dict, optional
        Parameters for nuclei segmentation and filtering (e.g., 'nms', 'prob', 'min_size', 'circularity').

    hyperparameter_chromatinization : dict, optional
        Parameters for segmenting and filtering chromatin spots (e.g., 'cut_point', 'ratio').

    img_adj_par_chrom : dict, optional
        Image adjustment parameters (gamma, contrast) specifically for chromatin analysis.

    img_adj_par : dict, optional
        Image adjustment parameters for nuclei segmentation.

    show_plots : bool, optional
        Flag controlling the automatic display of visual results.

    nuclei_results : dict, optional
        A dictionary storing numerical data (features) extracted from the nuclei.

    images : dict, optional
        A dictionary storing output images and masks.

    Attributes
    ----------
    image : np.ndarray
        The currently loaded image for analysis.

    test_results : list
        The visual outcomes of NMS/Prob parameter tests.

    hyperparameter_nuclei : dict
        A dictionary of active parameters used by the `find_nuclei()` and `select_nuclei()` methods.

    hyperparameter_chromatinization : dict
        A dictionary of active parameters used by the `nuclei_chromatinization()` method.

    img_adj_par : dict
        Image correction parameters for nuclei segmentation.

    img_adj_par_chrom : dict
        Image correction parameters for chromatin analysis.

    show_plots : bool
        The state of the plot display flag.

    nuclei_results : dict
        Stores feature dictionaries for: all detected ('nuclei'), selected ('nuclei_reduced'),
        and chromatinization data ('nuclei_chromatinization').

    images : dict
        Stores masks and images visualizing the results.

    series_im : bool
        Flag indicating if the class is operating in a batch or series processing mode.

    Methods
    -------
    set_nms(nms)
        Sets the Non-Maximum Suppression (NMS) threshold.

    set_prob(prob)
        Sets the segmentation probability threshold.

    set_nuclei_circularity(circ)
        Sets the minimum required circularity for a nucleus.

    set_nuclei_local_intenisty_FC(local_FC)
        Sets the factor used for removing false positives based on local intensity differences.

    set_nuclei_global_area_FC(global_FC)
        Sets the factor used for removing size-based outlier false positives.

    set_nuclei_size(size)
        Sets the minimum and maximum area (in pixels) for nuclei selection.

    set_nuclei_min_mean_intensity(intensity)
        Sets the minimum required mean intensity value for a nucleus.

    set_chromatinization_size(size)
        Sets the minimum and maximum area (in pixels) for chromatin spot selection.

    set_chromatinization_cut_point(cut_point)
        Sets the factor used to adjust the chromatin segmentation threshold (Otsu's method).

    set_adj_image_gamma(gamma)
        Sets the gamma correction for the nuclei image.

    set_adj_chrom_contrast(contrast)
        Sets the contrast adjustment for the chromatinization image.

    current_parameters_nuclei (property)
        Returns the active nuclei segmentation and filtering parameters.

    find_nuclei()
        Performs nuclei segmentation using StarDist and extracts initial features.

    select_nuclei()
        Filters the detected nuclei based on set morphological and intensity criteria.

    nuclei_chromatinization()
        Performs quantitative and morphological analysis of chromatin spots in selected nuclei.

    get_features(model_out, image)
        Calculates geometric and intensity features from a segmented mask (label image).

    Notes
    -----
    The typical analysis workflow follows this order:
    1. `input_image()`
    2. `find_nuclei()`
    3. `select_nuclei()` (Optional)
    4. `nuclei_chromatinization()` (Optional)
    """

    def __init__(
        self,
        image=None,
        test_results=None,
        hyperparameter_nuclei=None,
        hyperparameter_chromatinization=None,
        img_adj_par_chrom=None,
        img_adj_par=None,
        show_plots=None,
        nuclei_results=None,
        images=None,
    ):
        """
        The main class for the detection and analysis of cell nuclei and their chromatinization
        in microscopy or flow cytometry images, utilizing the StarDist segmentation model.

        This class inherits functionality for image processing (ImageTools) and
        results handling (RepTools).

        Parameters
        ----------
        image : np.ndarray, optional
            The input image for analysis.
            Default: None.

        test_results : list, optional
            A list of plots or images resulting from parameter testing.
            Default: None.

        hyperparameter_nuclei : dict, optional
            The segmentation parameters for nuclei detection.
            Default:
            {'nms': 0.8, 'prob': 0.4, 'max_size': 1000, 'min_size': 20,
             'circularity': 0.6, 'intensity_mean': 6553.5, 'nn_min': 10,
             'FC_diff_global': 1.5, 'FC_diff_local_intensity': 0.6}

        hyperparameter_chromatinization : dict, optional
            The analysis parameters for chromatin spots within the nuclei.
            Default:
            {'max_size': 800, 'min_size': 2, 'ratio': 0.1, 'cut_point': 0.95}

        img_adj_par_chrom : dict, optional
            Image adjustment parameters (gamma, contrast, brightness) for chromatin analysis.
            Default: {'gamma': 0.25, 'contrast': 5, 'brightness': 950}

        img_adj_par : dict, optional
            Image adjustment parameters (gamma, contrast, brightness) for nuclei segmentation.
            Default: {'gamma': 0.9, 'contrast': 2, 'brightness': 1000}

        show_plots : bool, optional
            Flag to determine whether results and plots should be displayed automatically.
            Default: True.

        nuclei_results : dict, optional
            A dictionary storing the numerical results of the analysis.
            Default: {'nuclei': None, 'nuclei_reduced': None, 'nuclei_chromatinization': None}

        images : dict, optional
            A dictionary storing the output images (e.g., masks).
            Default: {'nuclei': None, 'nuclei_reduced': None, 'nuclei_chromatinization': None}

        Attributes
        ----------
        image : np.ndarray
            The currently loaded image for analysis.

        hyperparameter_nuclei : dict
            Active nuclei segmentation parameters.

        hyperparameter_chromatinization : dict
            Active chromatinization analysis parameters.

        img_adj_par : dict
            Active image correction parameters for nuclei segmentation.

        img_adj_par_chrom : dict
            Active image correction parameters for chromatin analysis.

        show_plots : bool
            The current state of the plot display flag.

        series_im : bool
            Flag indicating if a series of images is being processed.

        Notes
        -----
        The default value for 'intensity_mean' in hyperparameter_nuclei is calculated
        as $(2^{16} - 1) / 10$, which represents 10% of the maximum 16-bit value (65535 / 10 = 6553.5).

        The image adjustment parameters are crucial for optimizing contrast and brightness
        to improve the performance of both the StarDist model and the subsequent
        chromatin thresholding.
        """

        # Use default values if parameters are None
        self.image = image or None
        """Loaded input image."""
        self.test_results = test_results or None
        """Results of parameter tests.

            This attribute or method stores the outcomes of parameter testing procedures.
            For interactive browsing and inspection of the results, use the 
            `browser_test(self)` method."""

        self.hyperparameter_nuclei = hyperparameter_nuclei or {
            "nms": 0.8,
            "prob": 0.4,
            "max_size": 1000,
            "min_size": 20,
            "circularity": 0.6,
            "intensity_mean": (2**16 - 1) / 10,
            "nn_min": 10,
            "FC_diff_global": 1.5,
            "FC_diff_local_intensity": 0.6,
        }
        """Active nuclei segmentation/filter parameters."""

        self.hyperparameter_chromatinization = hyperparameter_chromatinization or {
            "max_size": 800,
            "min_size": 2,
            "ratio": 0.1,
            "cut_point": 0.95,
        }
        """Active chromatin analysis parameters."""

        self.img_adj_par_chrom = img_adj_par_chrom or {
            "gamma": 0.25,
            "contrast": 5,
            "brightness": 950,
        }
        """Image adjustment for chromatin analysis."""

        self.img_adj_par = img_adj_par or {
            "gamma": 0.9,
            "contrast": 2,
            "brightness": 1000,
        }
        """Image adjustment for nuclei segmentation."""

        self.show_plots = show_plots or True
        """Flag controlling plot display."""

        self.nuclei_results = nuclei_results or {
            "nuclei": None,
            "nuclei_reduced": None,
            "nuclei_chromatinization": None,
        }
        """Stored dictionary of nuclei analysis results."""

        self.images = images or {
            "nuclei": None,
            "nuclei_reduced": None,
            "nuclei_chromatinization": None,
        }
        """Stored dictionary of images from nuclei analysis."""

        # sereies images
        self.series_im = False
        """Flag for batch/series image processing."""

    def set_nms(self, nms: float):
        """
        Set the Non-Maximum Suppression (NMS) threshold.

        The NMS threshold controls how aggressively overlapping detections are suppressed.
        A lower value reduces the probability of overlapping nuclei being kept.

        Parameters
        ----------
        nms : float
            The NMS IoU threshold value.
        """

        self.hyperparameter_nuclei["nms"] = nms

    def set_prob(self, prob: float):
        """
        Set the probability threshold used in segmentation.

        The probability threshold determines the minimum confidence required for an object
        (e.g., a nucleus) to be classified as a segmented entity. Higher values result in
        fewer segmented objects, as only detections with strong confidence scores are kept.
        This may lead to omission of weaker or less distinct structures.

        Because optimal values depend on image characteristics, it is important to visually
        inspect segmentation results produced with different thresholds to determine the
        most suitable setting.

        Parameters
        ----------
        prob : float
            The probability threshold value.
        """

        self.hyperparameter_nuclei["prob"] = prob

    def set_nuclei_circularity(self, circ: float):
        """
        This method sets 'circ' parameter. The circ is a parameter used for adjust minimal nucleus circularity.

        Parameters
        ----------
        circ : float
            Nuclei circularity value.
        """

        self.hyperparameter_nuclei["circularity"] = circ

    def set_nuclei_local_intenisty_FC(self, local_FC: float):
        """
        This method sets the 'FC_diff_local_intensity' parameter. The 'local_FC' is used to remove false positive multiple nuclei that were detected in single image.

        Parameters
        ----------
        local_FC : float
            local_FC value.
        """

        self.hyperparameter_nuclei["FC_diff_local_intensity"] = local_FC

    # change
    def set_nuclei_global_area_FC(self, global_FC: float):
        """
        This method sets the 'FC_diff_global' parameter. The 'global_FC' is used to remove false positive multiple nuclei that were detected in a single image and are outliers from the global mean area size.

        Parameters
        ----------
        FC_diff_global : float
            global_FC value.
        """

        self.hyperparameter_nuclei["FC_diff_global"] = global_FC

    def set_nuclei_size(self, size: tuple):
        """
        This method sets 'size' parameter. The size is a parameter used for adjust minimal and maximal nucleus area (px).

        Parameters
        ----------
        size : tuple
            (min_value, max_value)
        """

        self.hyperparameter_nuclei["min_size"] = size[0]
        self.hyperparameter_nuclei["max_size"] = size[1]

    def set_nuclei_min_mean_intensity(self, intensity: int):
        """
        This method sets 'intensity' parameter. The 'intensity' parameter is used to adjust the minimum mean intensity of all pixel intensities within the nucleus.

        Parameters
        ----------
        intensity : int
            intensity value.
        """

        self.hyperparameter_nuclei["intensity_mean"] = intensity

    def set_chromatinization_size(self, size: tuple):
        """
        This method sets 'size' parameter. The size is a parameter used for adjust minimal and maximal chromanitization spot area (px) within the nucleus.

        Parameters
        ----------
        size : tuple
            (min_value, max_value)
        """

        self.hyperparameter_chromatinization["min_size"] = size[0]
        self.hyperparameter_chromatinization["max_size"] = size[1]

    def set_chromatinization_ratio(self, ratio: int):
        """
        This method sets the 'ratio' parameter. In this case, the 'ratio' parameter is similar to 'circularity' as it describes the ratio between the maximum lengths in the x and y dimensions of the nucleus chromatinization.

        Parameters
        ----------
        ratio : float
            ratio value.
        """

        self.hyperparameter_chromatinization["ratio"] = ratio

    def set_chromatinization_cut_point(self, cut_point: int):
        """
        This method sets the 'cut_point' parameter. The 'cut_point' parameter is a factor used to adjust the threshold for separating the background from chromatin spots.

        Parameters
        ----------
        cut_point : int
            cut_point value.
        """

        self.hyperparameter_chromatinization["cut_point"] = cut_point

    #

    def set_adj_image_gamma(self, gamma: float):
        """
        This method sets 'gamma' parameter. The gamma is a parameter used for adjust gamma of the nucleus image.

        Parameters
        ----------
        gamma : float
            gamma value.
        """

        self.img_adj_par["gamma"] = gamma

    def set_adj_image_contrast(self, contrast: float):
        """
        This method sets 'contrast' parameter. The contrast is a parameter used for adjust contrast of the nucleus image.

        Parameters
        ----------
        contrast : float
            contrast value.
        """

        self.img_adj_par["contrast"] = contrast

    def set_adj_image_brightness(self, brightness: float):
        """
        This method sets 'brightness' parameter. The brightness is a parameter used for adjust brightness of the nucleus image.

        Parameters
        ----------
        brightness : float
            brightness value.
        """

        self.img_adj_par["brightness"] = brightness

    #

    def set_adj_chrom_gamma(self, gamma: float):
        """
        This method sets 'gamma' parameter. The gamma is a parameter used for adjust gamma of the nucleus chromatinization image.

        Parameters
        ----------
        gamma : float
            gamma value.
        """

        self.img_adj_par_chrom["gamma"] = gamma

    def set_adj_chrom_contrast(self, contrast: float):
        """
        This method sets 'contrast' parameter. The contrast is a parameter used for adjust contrast of the nucleus chromatinization image.

        Parameters
        ----------
        contrast : float
            contrast value.
        """

        self.img_adj_par_chrom["contrast"] = contrast

    def set_adj_chrom_brightness(self, brightness: float):
        """
        This method sets 'brightness' parameter. The brightness is a parameter used for adjust brightness of the nucleus chromatinization image.

        Parameters
        ----------
        brightness : float
            brightness value.
        """

        self.img_adj_par_chrom["brightness"] = brightness

    @property
    def current_parameters_nuclei(self):
        """
        This method returns current nuclei analysis parameters.

        Returns
        -------
        dict
            Nuclei analysis parameters.
        """
        print(self.hyperparameter_nuclei)
        return self.hyperparameter_nuclei

    @property
    def current_parameters_chromatinization(self):
        """
        This method returns current nuclei chromatinization analysis parameters.

        Returns
        -------
        dict
            Nuclei chromatinization analysis parameters.
        """

        print(self.hyperparameter_chromatinization)
        return self.hyperparameter_chromatinization

    @property
    def current_parameters_img_adj(self):
        """
        This method returns current nuclei image setup.

        Returns
        -------
        dict
            Nuclei image setup.
        """

        print(self.img_adj_par)
        return self.img_adj_par

    @property
    def current_parameters_img_adj_chro(self):
        """
        This method returns current nuclei chromatinization image setup.

        Returns
        -------
        dict
            Nuclei chromatinization image setup.
        """

        print(self.img_adj_par_chrom)
        return self.img_adj_par_chrom

    def get_results_nuclei(self):
        """
        This function returns nuclei analysis results.

        Returns
        -------
        dict
            Nuclei results in the dictionary format.
        """

        if self.images["nuclei"] is None:
            print("No results to return!")
            return None
        else:
            if cfg._DISPLAY_MODE:
                if self.show_plots:
                    display_preview(self.resize_to_screen_img(self.images["nuclei"]))
            return self.nuclei_results["nuclei"], self.images["nuclei"]

    def get_results_nuclei_selected(self):
        """
        This function returns the results of the nuclei analysis following adjustments to the data selection thresholds.

        Returns
        -------
        dict
            Nuclei results in the dictionary format.
        """

        if self.images["nuclei_reduced"] is None:
            print("No results to return!")
            return None
        else:
            if cfg._DISPLAY_MODE:
                if self.show_plots:
                    display_preview(
                        self.resize_to_screen_img(self.images["nuclei_reduced"])
                    )
            return self.nuclei_results["nuclei_reduced"], self.images["nuclei_reduced"]

    def get_results_nuclei_chromatinization(self):
        """
        This function returns the results of the nuclei chromatinization analysis.

        Returns
        -------
        dict
            Nuclei chromatinization results in the dictionary format.
        """

        if self.images["nuclei_chromatinization"] is None:
            print("No results to return!")
            return None
        else:
            if cfg._DISPLAY_MODE:
                if self.show_plots:
                    display_preview(self.images["nuclei_chromatinization"])
            return (
                self.nuclei_results["nuclei_chromatinization"],
                self.images["nuclei_chromatinization"],
            )

    def add_test(self, plots):
        self.test_results = plots

        """
        Helper method.
        """

    def input_image(self, img):
        """
        This method adds the image to the class for nuclei and/or chromatinization analysis.

        Parameters
        ----------
        img : np.ndarray
            Input image.
        """

        self.image = img
        self.add_test(None)

    def get_features(self, model_out, image):
        """
        Extracts numerical feature descriptors from model output for a given image.

        This method processes the output returned by a feature-extraction model
        (e.g., CNN, encoder network, statistical model) and converts it into a
        structured feature vector associated with the provided image.
        Typically used for downstream analysis, classification, or clustering.

        Parameters
        ----------
        model_out : any
            Output returned by the feature-extraction model.
            The expected format depends on the model (e.g., tensor, dict, list of arrays).

        image : ndarray
            The input image (2D or 3D array) for which features are being extracted.
            Provided for reference or for combining raw image metrics with model features.

        Returns
        -------
        features : dict
            Dictionary containing extracted features.
            Keys correspond to feature names, and values are numerical descriptors.
        """

        features = {
            "label": [],
            "area": [],
            "area_bbox": [],
            "area_convex": [],
            "area_filled": [],
            "axis_major_length": [],
            "axis_minor_length": [],
            "eccentricity": [],
            "equivalent_diameter_area": [],
            "feret_diameter_max": [],
            "solidity": [],
            "perimeter": [],
            "perimeter_crofton": [],
            "circularity": [],
            "intensity_max": [],
            "intensity_mean": [],
            "intensity_min": [],
            "ratio": [],
            "coords": [],
        }

        for region in skimage.measure.regionprops(model_out, intensity_image=image):

            # Compute circularity
            if region.perimeter > 0:
                circularity = 4 * np.pi * region.area / (region.perimeter**2)
            else:
                circularity = 0

            features["area"].append(region.area)
            features["area_bbox"].append(region.area_bbox)
            features["area_convex"].append(region.area_convex)
            features["area_filled"].append(region.area_filled)
            features["axis_major_length"].append(region.axis_major_length)
            features["axis_minor_length"].append(region.axis_minor_length)
            features["eccentricity"].append(region.eccentricity)
            features["equivalent_diameter_area"].append(region.equivalent_diameter_area)
            features["feret_diameter_max"].append(region.feret_diameter_max)
            features["solidity"].append(region.solidity)
            features["perimeter"].append(region.perimeter)
            features["perimeter_crofton"].append(region.perimeter_crofton)
            features["label"].append(region.label)
            features["coords"].append(region.coords)
            features["circularity"].append(circularity)
            features["intensity_max"].append(np.max(region.intensity_max))
            features["intensity_min"].append(np.max(region.intensity_min))
            features["intensity_mean"].append(np.max(region.intensity_mean))

        ratios = []

        # Calculate the ratio for each pair of values
        for min_len, max_len in zip(
            features["axis_minor_length"], features["axis_major_length"]
        ):
            if max_len != 0:
                ratio = min_len / max_len
                ratios.append(ratio)
            else:
                ratios.append(float(0.0))

        features["ratio"] = ratios

        return features

    # repaired stat
    def nuclei_finder_test(self):
        """
        This method performs testing analysis of parameters (specified 'nms' and 'prob' parameters)
        for the image provided by the input_image() method.

        This method evaluates the performance of the internal NucleiFinder
        configuration using the currently loaded images, parameters, or model
        settings. It is typically used to check whether the detection, segmentation
        or preprocessing stages run correctly on sample data.

        Examples
        --------
        >>> nf.nuclei_finder_test()
        >>> nf.browser_test()
        """

        StarDist2D.from_pretrained()
        model = StarDist2D.from_pretrained("2D_versatile_fluo")

        nmst = [0.1, 0.2, 0.6]
        probt = [0.1, 0.5, 0.9]

        try:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        except:
            img = self.image

        plot = []

        # adj img
        img = adjust_img_16bit(
            img,
            brightness=self.img_adj_par["brightness"],
            contrast=self.img_adj_par["contrast"],
            gamma=self.img_adj_par["gamma"],
        )
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        fig = plt.figure(dpi=300)
        plt.imshow(img)
        plt.axis("off")
        plt.title("Original", fontsize=25)

        if cfg._DISPLAY_MODE:
            if self.show_plots:
                plt.show()

        plot.append(fig)

        for n in tqdm(nmst, desc="Loop 1: nmst"):
            print(f"\n➡️ Starting outer loop for n = {n}")

            for t in tqdm(probt, desc=f"   ↳ Loop 2 for n={n}", leave=False):
                print(f"   → Starting inner loop for t = {t}")

                labels, _ = model.predict_instances(
                    normalize(img.copy()), nms_thresh=n, prob_thresh=t
                )

                tmp = self.get_features(model_out=labels, image=img)

                fig = plt.figure(dpi=300)
                plt.imshow(render_label(labels, img=img))
                plt.axis("off")
                plt.title(
                    f"nms {n} & prob {t} \n detected nuc: {len(tmp['area'])}",
                    fontsize=25,
                )

                if cfg._DISPLAY_MODE:
                    if self.show_plots:
                        plt.show()

                plot.append(fig)

        self.add_test(plot)

    def find_nuclei(self):
        """
        Performs analysis on the image provided by the ``input_image()`` method
        using default or user-defined parameters.

        To show current parameters, use:
            - ``current_parameters_nuclei``
            - ``current_parameters_img_adj``

        To set new parameters, use:
            - ``set_nms()``
            - ``set_prob()``
            - ``set_adj_image_gamma()``
            - ``set_adj_image_contrast()``
            - ``set_adj_image_brightness()``

        To get analysis results, use:
            - ``get_results_nuclei()``
        """

        if isinstance(self.image, np.ndarray):

            model = StarDist2D.from_pretrained("2D_versatile_fluo")

            try:
                img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            except:
                img = self.image

            img = adjust_img_16bit(
                img,
                brightness=self.img_adj_par["brightness"],
                contrast=self.img_adj_par["contrast"],
                gamma=self.img_adj_par["gamma"],
            )
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            labels, _ = model.predict_instances(
                normalize(img),
                nms_thresh=self.hyperparameter_nuclei["nms"],
                prob_thresh=self.hyperparameter_nuclei["prob"],
            )

            self.nuclei_results["nuclei"] = self.get_features(
                model_out=labels, image=img
            )

            if len(self.nuclei_results["nuclei"]["coords"]) > 0:

                oryginal = adjust_img_16bit(img, color="gray")

                # series repaired nuclesu
                if self.series_im is True:
                    self.images["nuclei"] = oryginal
                else:
                    nuclei_mask = adjust_img_16bit(
                        cv2.cvtColor(
                            self.create_mask(self.nuclei_results["nuclei"], oryginal),
                            cv2.COLOR_BGR2GRAY,
                        ),
                        color="blue",
                    )
                    concatenated_image = cv2.hconcat([oryginal, nuclei_mask])
                    self.images["nuclei"] = concatenated_image

                if cfg._DISPLAY_MODE:
                    if self.show_plots:
                        display_preview(
                            self.resize_to_screen_img(self.images["nuclei"])
                        )

            else:

                self.nuclei_results["nuclei"] = None
                self.nuclei_results["nuclei_reduced"] = None
                self.nuclei_results["nuclei_chromatinization"] = None

                print("Nuclei not detected!")

        else:
            print("\nAdd image firstly!")

    def select_nuclei(self):
        """
        Selects data obtained from ``find_nuclei()`` based on the set threshold parameters.

        To show current parameters, use:
            - ``current_parameters_nuclei``

        To set new parameters, use:
            - ``set_nuclei_circularity()``
            - ``set_nuclei_size()``
            - ``set_nuclei_min_mean_intensity()``

        To get analysis results, use:
            - ``get_results_nuclei_selected()``
        """

        if self.nuclei_results["nuclei"] is not None:
            input_in = copy.deepcopy(self.nuclei_results["nuclei"])

            nuclei_dictionary = self.drop_dict(
                input_in,
                key="area",
                var=self.hyperparameter_nuclei["min_size"],
                action=">",
            )
            nuclei_dictionary = self.drop_dict(
                nuclei_dictionary,
                key="area",
                var=self.hyperparameter_nuclei["max_size"],
                action="<",
            )
            nuclei_dictionary = self.drop_dict(
                nuclei_dictionary,
                key="intensity_mean",
                var=self.hyperparameter_nuclei["intensity_mean"],
                action=">",
            )

            if len(nuclei_dictionary["coords"]) > 0:

                self.nuclei_results["nuclei_reduced"] = nuclei_dictionary

                try:
                    img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                except:
                    img = self.image

                oryginal = adjust_img_16bit(img, color="gray")

                # series repaired nuclesu
                if self.series_im is True:
                    self.images["nuclei_reduced"] = oryginal
                else:
                    nuclei_mask = adjust_img_16bit(
                        cv2.cvtColor(
                            self.create_mask(
                                self.nuclei_results["nuclei_reduced"], oryginal
                            ),
                            cv2.COLOR_BGR2GRAY,
                        ),
                        color="blue",
                    )
                    concatenated_image = cv2.hconcat([oryginal, nuclei_mask])

                    self.images["nuclei_reduced"] = concatenated_image

                if cfg._DISPLAY_MODE:
                    if self.show_plots:
                        display_preview(
                            self.resize_to_screen_img(self.images["nuclei_reduced"])
                        )

            else:
                self.nuclei_results["nuclei"] = None
                self.nuclei_results["nuclei_reduced"] = None
                self.nuclei_results["nuclei_chromatinization"] = None

                print("Selected zero nuclei! Analysis stop!")

        else:
            print("Lack of nuclei data to select!")

    def nuclei_chromatinization(self):
        """
        Performs chromatinization analysis of nuclei using data obtained from
        ``find_nuclei()`` and/or ``select_nuclei()``.

        To show current parameters, use:
            - ``current_parameters_chromatinization``
            - ``current_parameters_img_adj_chro``

        To set new parameters, use:
            - ``set_chromatinization_size()``
            - ``set_chromatinization_ratio()``
            - ``set_chromatinization_cut_point()``
            - ``set_adj_chrom_gamma()``
            - ``set_adj_chrom_contrast()``
            - ``set_adj_chrom_brightness()``

        To get analysis results, use:
            - ``get_results_nuclei_chromatinization()``
        """

        def add_lists(f, g):

            result = []
            max_length = max(len(f), len(g))

            for i in range(max_length):
                f_elem = f[i] if i < len(f) else ""
                g_elem = g[i] if i < len(g) else ""
                result.append(f_elem + g_elem)

            return result

        def reverse_coords(image, x, y):

            zero = np.zeros(image.shape)

            zero[x, y] = 2**16

            zero_indices = np.where(zero == 0)

            return zero_indices[0], zero_indices[1]

        if isinstance(self.nuclei_results["nuclei_reduced"], dict):
            nuclei_dictionary = self.nuclei_results["nuclei_reduced"]
        else:
            nuclei_dictionary = self.nuclei_results["nuclei"]

        if nuclei_dictionary is not None:
            arrays_list = copy.deepcopy(nuclei_dictionary["coords"])

            chromatione_info = {
                "area": [],
                "area_bbox": [],
                "area_convex": [],
                "area_filled": [],
                "axis_major_length": [],
                "axis_minor_length": [],
                "eccentricity": [],
                "equivalent_diameter_area": [],
                "feret_diameter_max": [],
                "solidity": [],
                "perimeter": [],
                "perimeter_crofton": [],
                "coords": [],
            }

            full_im = np.zeros(self.image.shape[0:2], dtype=np.uint16)
            full_im = adjust_img_16bit(full_im)

            for arr in arrays_list:
                x = list(arr[:, 0])
                y = list(arr[:, 1])

                x1, y1 = reverse_coords(self.image, x, y)

                regions_chro2 = self.image.copy()

                regions_chro2[x1, y1] = 0

                regions_chro2 = regions_chro2.astype("uint16")

                try:
                    regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)
                except:
                    pass

                regions_chro2 = adjust_img_16bit(
                    regions_chro2,
                    brightness=self.img_adj_par_chrom["brightness"],
                    contrast=self.img_adj_par_chrom["contrast"],
                    gamma=self.img_adj_par_chrom["gamma"],
                )

                full_im = merge_images(
                    image_list=[full_im, regions_chro2], intensity_factors=[1, 1]
                )

                ret, thresh = cv2.threshold(
                    regions_chro2[x, y],
                    0,
                    2**16 - 1,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU,
                )

                regions_chro2[
                    regions_chro2
                    <= ret * self.hyperparameter_chromatinization["cut_point"]
                ] = 0

                regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)

                chromatione = regions_chro2 > 0

                labeled_cells = measure.label(chromatione)
                regions = measure.regionprops(labeled_cells)
                regions = measure.regionprops(
                    labeled_cells, intensity_image=regions_chro2
                )

                for region in regions:

                    chromatione_info["area"].append(region.area)
                    chromatione_info["area_bbox"].append(region.area_bbox)
                    chromatione_info["area_convex"].append(region.area_convex)
                    chromatione_info["area_filled"].append(region.area_filled)
                    chromatione_info["axis_major_length"].append(
                        region.axis_major_length
                    )
                    chromatione_info["axis_minor_length"].append(
                        region.axis_minor_length
                    )
                    chromatione_info["eccentricity"].append(region.eccentricity)
                    chromatione_info["equivalent_diameter_area"].append(
                        region.equivalent_diameter_area
                    )
                    chromatione_info["feret_diameter_max"].append(
                        region.feret_diameter_max
                    )
                    chromatione_info["solidity"].append(region.solidity)
                    chromatione_info["perimeter"].append(region.perimeter)
                    chromatione_info["perimeter_crofton"].append(
                        region.perimeter_crofton
                    )
                    chromatione_info["coords"].append(region.coords)

            ratios = []

            for min_len, max_len in zip(
                chromatione_info["axis_minor_length"],
                chromatione_info["axis_major_length"],
            ):
                if max_len != 0:
                    ratio = min_len / max_len
                    ratios.append(ratio)
                else:
                    ratios.append(float(0.0))

            chromatione_info["ratio"] = ratios

            chromation_dic = self.drop_dict(
                chromatione_info,
                key="area",
                var=self.hyperparameter_chromatinization["min_size"],
                action=">",
            )
            chromation_dic = self.drop_dict(
                chromation_dic,
                key="area",
                var=self.hyperparameter_chromatinization["max_size"],
                action="<",
            )
            chromation_dic = self.drop_dict(
                chromation_dic,
                key="ratio",
                var=self.hyperparameter_chromatinization["ratio"],
                action=">",
            )

            arrays_list2 = copy.deepcopy(chromation_dic["coords"])

            nuclei_dictionary["spot_size_area"] = []
            nuclei_dictionary["spot_size_area_bbox"] = []
            nuclei_dictionary["spot_size_area_convex"] = []
            nuclei_dictionary["spot_size_area_filled"] = []
            nuclei_dictionary["spot_axis_major_length"] = []
            nuclei_dictionary["spot_axis_minor_length"] = []
            nuclei_dictionary["spot_eccentricity"] = []
            nuclei_dictionary["spot_size_equivalent_diameter_area"] = []
            nuclei_dictionary["spot_feret_diameter_max"] = []
            nuclei_dictionary["spot_perimeter"] = []
            nuclei_dictionary["spot_perimeter_crofton"] = []

            for i, arr in enumerate(arrays_list):

                spot_size_area = []
                spot_size_area_bbox = []
                spot_size_area_convex = []
                spot_size_area_convex = []
                spot_size_area_filled = []
                spot_axis_major_length = []
                spot_axis_minor_length = []
                spot_eccentricity = []
                spot_size_equivalent_diameter_area = []
                spot_feret_diameter_max = []
                spot_perimeter = []
                spot_perimeter_crofton = []

                # Flatten the array,
                df_tmp = pd.DataFrame(arr)
                df_tmp["duplicates"] = add_lists(
                    [str(x) for x in df_tmp[0]], [str(y) for y in df_tmp[1]]
                )

                counter_tmp = Counter(df_tmp["duplicates"])

                for j, arr2 in enumerate(arrays_list2):
                    df_tmp2 = pd.DataFrame(arr2)
                    df_tmp2["duplicates"] = add_lists(
                        [str(x) for x in df_tmp2[0]], [str(y) for y in df_tmp2[1]]
                    )

                    counter_tmp2 = Counter(df_tmp2["duplicates"])
                    intersection_length = len(counter_tmp.keys() & counter_tmp2.keys())
                    min_length = min(len(counter_tmp), len(counter_tmp2))

                    if intersection_length >= 0.8 * min_length:

                        if (
                            len(list(df_tmp2["duplicates"]))
                            / len(list(df_tmp["duplicates"]))
                        ) >= 0.025 and (
                            len(list(df_tmp2["duplicates"]))
                            / len(list(df_tmp["duplicates"]))
                        ) <= 0.5:
                            spot_size_area.append(chromation_dic["area"][j])
                            spot_size_area_bbox.append(chromation_dic["area_bbox"][j])
                            spot_size_area_convex.append(
                                chromation_dic["area_convex"][j]
                            )
                            spot_size_area_filled.append(
                                chromation_dic["area_filled"][j]
                            )
                            spot_axis_major_length.append(
                                chromation_dic["axis_major_length"][j]
                            )
                            spot_axis_minor_length.append(
                                chromation_dic["axis_minor_length"][j]
                            )
                            spot_eccentricity.append(chromation_dic["eccentricity"][j])
                            spot_size_equivalent_diameter_area.append(
                                chromation_dic["equivalent_diameter_area"][j]
                            )
                            spot_feret_diameter_max.append(
                                chromation_dic["feret_diameter_max"][j]
                            )
                            spot_perimeter.append(chromation_dic["perimeter"][j])
                            spot_perimeter_crofton.append(
                                chromation_dic["perimeter_crofton"][j]
                            )

                nuclei_dictionary["spot_size_area"].append(spot_size_area)
                nuclei_dictionary["spot_size_area_bbox"].append(spot_size_area_bbox)
                nuclei_dictionary["spot_size_area_convex"].append(spot_size_area_convex)
                nuclei_dictionary["spot_size_area_filled"].append(spot_size_area_filled)
                nuclei_dictionary["spot_axis_major_length"].append(
                    spot_axis_major_length
                )
                nuclei_dictionary["spot_axis_minor_length"].append(
                    spot_axis_minor_length
                )
                nuclei_dictionary["spot_eccentricity"].append(spot_eccentricity)
                nuclei_dictionary["spot_size_equivalent_diameter_area"].append(
                    spot_size_equivalent_diameter_area
                )
                nuclei_dictionary["spot_feret_diameter_max"].append(
                    spot_feret_diameter_max
                )
                nuclei_dictionary["spot_perimeter"].append(spot_perimeter)
                nuclei_dictionary["spot_perimeter_crofton"].append(
                    spot_perimeter_crofton
                )

            self.nuclei_results["chromatinization"] = chromation_dic
            self.nuclei_results["nuclei_chromatinization"] = nuclei_dictionary

            self.images["nuclei_chromatinization"] = self.create_mask(
                chromation_dic, self.image
            )

            img_chrom = adjust_img_16bit(
                cv2.cvtColor(
                    self.create_mask(
                        self.nuclei_results["chromatinization"], self.image
                    ),
                    cv2.COLOR_BGR2GRAY,
                ),
                color="yellow",
            )

            if isinstance(self.nuclei_results["nuclei_reduced"], dict):
                nuclei_mask = adjust_img_16bit(
                    cv2.cvtColor(
                        self.create_mask(
                            self.nuclei_results["nuclei_reduced"], self.image
                        ),
                        cv2.COLOR_BGR2GRAY,
                    ),
                    color="blue",
                )
            else:
                nuclei_mask = adjust_img_16bit(
                    cv2.cvtColor(
                        self.create_mask(self.nuclei_results["nuclei"], self.image),
                        cv2.COLOR_BGR2GRAY,
                    ),
                    color="blue",
                )

            nuclei_mask = merge_images([nuclei_mask, img_chrom], [1, 1])

            try:
                img = cv2.cvtColor(full_im, cv2.COLOR_BGR2GRAY)
            except:
                img = full_im

            oryginal = adjust_img_16bit(img, color="gray")

            concatenated_image = cv2.hconcat([oryginal, nuclei_mask])

            self.images["nuclei_chromatinization"] = concatenated_image

            if cfg._DISPLAY_MODE:
                if self.show_plots:
                    display_preview(
                        self.resize_to_screen_img(
                            self.images["nuclei_chromatinization"]
                        )
                    )

        else:
            print("Lack of nuclei data to select!")

    # separate function for chromatinization

    def _nuclei_chromatinization_series(self, image, nuclei_data):
        """
        Helper method for performing chromatinization analysis on nuclei detected in the provided image.
        """

        def add_lists(f, g):
            result = []
            max_length = max(len(f), len(g))

            for i in range(max_length):
                f_elem = f[i] if i < len(f) else ""
                g_elem = g[i] if i < len(g) else ""
                result.append(f_elem + g_elem)

            return result

        def reverse_coords(image, x, y):

            zero = np.zeros(image.shape)

            zero[x, y] = 2**16

            zero_indices = np.where(zero == 0)

            return zero_indices[0], zero_indices[1]

        nuclei_dictionary = nuclei_data.copy()

        if nuclei_dictionary is not None:
            arrays_list = copy.deepcopy(nuclei_dictionary["coords"])

            chromatione_info = {
                "area": [],
                "area_bbox": [],
                "area_convex": [],
                "area_filled": [],
                "axis_major_length": [],
                "axis_minor_length": [],
                "eccentricity": [],
                "equivalent_diameter_area": [],
                "feret_diameter_max": [],
                "solidity": [],
                "perimeter": [],
                "perimeter_crofton": [],
                "coords": [],
            }

            full_im = np.zeros(image.shape[0:2], dtype=np.uint16)
            full_im = adjust_img_16bit(full_im)

            for arr in arrays_list:
                x = list(arr[:, 0])
                y = list(arr[:, 1])

                x1, y1 = reverse_coords(image, x, y)

                regions_chro2 = image.copy()

                regions_chro2[x1, y1] = 0

                regions_chro2 = regions_chro2.astype("uint16")

                try:
                    regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)
                except:
                    pass

                regions_chro2 = adjust_img_16bit(
                    regions_chro2,
                    brightness=self.img_adj_par_chrom["brightness"],
                    contrast=self.img_adj_par_chrom["contrast"],
                    gamma=self.img_adj_par_chrom["gamma"],
                )

                full_im = merge_images(
                    image_list=[full_im, regions_chro2], intensity_factors=[1, 1]
                )

                ret, _ = cv2.threshold(
                    regions_chro2[x, y],
                    0,
                    2**16 - 1,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU,
                )

                regions_chro2[
                    regions_chro2
                    <= ret * self.hyperparameter_chromatinization["cut_point"]
                ] = 0

                regions_chro2 = cv2.cvtColor(regions_chro2, cv2.COLOR_BGR2GRAY)

                chromatione = regions_chro2 > 0

                labeled_cells = measure.label(chromatione)
                regions = measure.regionprops(labeled_cells)
                regions = measure.regionprops(
                    labeled_cells, intensity_image=regions_chro2
                )

                for region in regions:

                    chromatione_info["area"].append(region.area)
                    chromatione_info["area_bbox"].append(region.area_bbox)
                    chromatione_info["area_convex"].append(region.area_convex)
                    chromatione_info["area_filled"].append(region.area_filled)
                    chromatione_info["axis_major_length"].append(
                        region.axis_major_length
                    )
                    chromatione_info["axis_minor_length"].append(
                        region.axis_minor_length
                    )
                    chromatione_info["eccentricity"].append(region.eccentricity)
                    chromatione_info["equivalent_diameter_area"].append(
                        region.equivalent_diameter_area
                    )
                    chromatione_info["feret_diameter_max"].append(
                        region.feret_diameter_max
                    )
                    chromatione_info["solidity"].append(region.solidity)
                    chromatione_info["perimeter"].append(region.perimeter)
                    chromatione_info["perimeter_crofton"].append(
                        region.perimeter_crofton
                    )
                    chromatione_info["coords"].append(region.coords)

            ratios = []

            for min_len, max_len in zip(
                chromatione_info["axis_minor_length"],
                chromatione_info["axis_major_length"],
            ):
                if max_len != 0:
                    ratio = min_len / max_len
                    ratios.append(ratio)
                else:
                    ratios.append(float(0.0))

            chromatione_info["ratio"] = ratios

            chromation_dic = self.drop_dict(
                chromatione_info,
                key="area",
                var=self.hyperparameter_chromatinization["min_size"],
                action=">",
            )
            chromation_dic = self.drop_dict(
                chromation_dic,
                key="area",
                var=self.hyperparameter_chromatinization["max_size"],
                action="<",
            )
            chromation_dic = self.drop_dict(
                chromation_dic,
                key="ratio",
                var=self.hyperparameter_chromatinization["ratio"],
                action=">",
            )

            arrays_list2 = copy.deepcopy(chromation_dic["coords"])

            nuclei_dictionary["spot_size_area"] = []
            nuclei_dictionary["spot_size_area_bbox"] = []
            nuclei_dictionary["spot_size_area_convex"] = []
            nuclei_dictionary["spot_size_area_filled"] = []
            nuclei_dictionary["spot_axis_major_length"] = []
            nuclei_dictionary["spot_axis_minor_length"] = []
            nuclei_dictionary["spot_eccentricity"] = []
            nuclei_dictionary["spot_size_equivalent_diameter_area"] = []
            nuclei_dictionary["spot_feret_diameter_max"] = []
            nuclei_dictionary["spot_perimeter"] = []
            nuclei_dictionary["spot_perimeter_crofton"] = []

            for arr in arrays_list:

                spot_size_area = []
                spot_size_area_bbox = []
                spot_size_area_convex = []
                spot_size_area_convex = []
                spot_size_area_filled = []
                spot_axis_major_length = []
                spot_axis_minor_length = []
                spot_eccentricity = []
                spot_size_equivalent_diameter_area = []
                spot_feret_diameter_max = []
                spot_perimeter = []
                spot_perimeter_crofton = []

                # Flatten the array,
                df_tmp = pd.DataFrame(arr)
                df_tmp["duplicates"] = add_lists(
                    [str(x) for x in df_tmp[0]], [str(y) for y in df_tmp[1]]
                )

                counter_tmp = Counter(df_tmp["duplicates"])

                for j, arr2 in enumerate(arrays_list2):
                    df_tmp2 = pd.DataFrame(arr2)
                    df_tmp2["duplicates"] = add_lists(
                        [str(x) for x in df_tmp2[0]], [str(y) for y in df_tmp2[1]]
                    )

                    counter_tmp2 = Counter(df_tmp2["duplicates"])
                    intersection_length = len(counter_tmp.keys() & counter_tmp2.keys())
                    min_length = min(len(counter_tmp), len(counter_tmp2))

                    if intersection_length >= 0.8 * min_length:

                        if (
                            len(list(df_tmp2["duplicates"]))
                            / len(list(df_tmp["duplicates"]))
                        ) >= 0.025 and (
                            len(list(df_tmp2["duplicates"]))
                            / len(list(df_tmp["duplicates"]))
                        ) <= 0.5:
                            spot_size_area.append(chromation_dic["area"][j])
                            spot_size_area_bbox.append(chromation_dic["area_bbox"][j])
                            spot_size_area_convex.append(
                                chromation_dic["area_convex"][j]
                            )
                            spot_size_area_filled.append(
                                chromation_dic["area_filled"][j]
                            )
                            spot_axis_major_length.append(
                                chromation_dic["axis_major_length"][j]
                            )
                            spot_axis_minor_length.append(
                                chromation_dic["axis_minor_length"][j]
                            )
                            spot_eccentricity.append(chromation_dic["eccentricity"][j])
                            spot_size_equivalent_diameter_area.append(
                                chromation_dic["equivalent_diameter_area"][j]
                            )
                            spot_feret_diameter_max.append(
                                chromation_dic["feret_diameter_max"][j]
                            )
                            spot_perimeter.append(chromation_dic["perimeter"][j])
                            spot_perimeter_crofton.append(
                                chromation_dic["perimeter_crofton"][j]
                            )

                nuclei_dictionary["spot_size_area"].append(spot_size_area)
                nuclei_dictionary["spot_size_area_bbox"].append(spot_size_area_bbox)
                nuclei_dictionary["spot_size_area_convex"].append(spot_size_area_convex)
                nuclei_dictionary["spot_size_area_filled"].append(spot_size_area_filled)
                nuclei_dictionary["spot_axis_major_length"].append(
                    spot_axis_major_length
                )
                nuclei_dictionary["spot_axis_minor_length"].append(
                    spot_axis_minor_length
                )
                nuclei_dictionary["spot_eccentricity"].append(spot_eccentricity)
                nuclei_dictionary["spot_size_equivalent_diameter_area"].append(
                    spot_size_equivalent_diameter_area
                )
                nuclei_dictionary["spot_feret_diameter_max"].append(
                    spot_feret_diameter_max
                )
                nuclei_dictionary["spot_perimeter"].append(spot_perimeter)
                nuclei_dictionary["spot_perimeter_crofton"].append(
                    spot_perimeter_crofton
                )

            self.nuclei_results["chromatinization"] = chromation_dic
            self.nuclei_results["nuclei_chromatinization"] = nuclei_dictionary

            self.images["nuclei_chromatinization"] = self.create_mask(
                chromation_dic, image
            )

            img_chrom = adjust_img_16bit(
                cv2.cvtColor(
                    self.create_mask(self.nuclei_results["chromatinization"], image),
                    cv2.COLOR_BGR2GRAY,
                ),
                color="yellow",
            )

            nuclei_mask = adjust_img_16bit(
                cv2.cvtColor(self.create_mask(nuclei_data, image), cv2.COLOR_BGR2GRAY),
                color="blue",
            )

            nuclei_mask = merge_images([nuclei_mask, img_chrom], [1, 1])

            try:
                img = cv2.cvtColor(full_im, cv2.COLOR_BGR2GRAY)
            except:
                img = full_im

            oryginal = adjust_img_16bit(img, color="gray")

            concatenated_image = cv2.hconcat([oryginal, nuclei_mask])

            self.images["nuclei_chromatinization"] = concatenated_image

            if cfg._DISPLAY_MODE:
                if self.show_plots:
                    display_preview(
                        self.resize_to_screen_img(
                            self.images["nuclei_chromatinization"]
                        )
                    )

        else:
            print("Lack of nuclei data to select!")

    def browser_test(self):
        """
        Displays test results generated by the ``nuclei_finder_test()`` method
        in the default web browser.
        """

        html_content = ""

        for fig in self.test_results:
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            img_base64 = base64.b64encode(buf.read()).decode("utf-8")

            html_content += f'<img src="data:image/png;base64,{img_base64}" style="margin:10px;"/>\n'

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".html"
        ) as tmp_file:
            tmp_file.write(html_content)
            tmp_filename = tmp_file.name

        webbrowser.open_new_tab(tmp_filename)

    def series_analysis_chromatinization(
        self,
        path_to_images: str,
        file_extension: str = "tiff",
        selected_id: list = [],
        fille_name_part: str = "",
        selection_opt: bool = True,
        include_img: bool = True,
        test_series: int = 0,
    ):
        """
        Performs full analysis on images provided via the ``input_image()`` method
        using default or user-defined parameters.

        This method runs nuclei detection, nuclei selection, and chromatinization
        analysis in a single pipeline. Users can adjust parameters for each step
        before running the analysis.

        To show current parameters, use:
            - ``current_parameters_nuclei``
            - ``current_parameters_img_adj``
            - ``current_parameters_chromatinization``
            - ``current_parameters_img_adj_chro``

        To set new parameters, use:
            - ``set_nms()``
            - ``set_prob()``
            - ``set_adj_image_gamma()``
            - ``set_adj_image_contrast()``
            - ``set_adj_image_brightness()``
            - ``set_nuclei_circularity()``
            - ``set_nuclei_size()``
            - ``set_nuclei_min_mean_intensity()``
            - ``set_chromatinization_size()``
            - ``set_chromatinization_ratio()``
            - ``set_chromatinization_cut_point()``
            - ``set_adj_chrom_gamma()``
            - ``set_adj_chrom_contrast()``
            - ``set_adj_chrom_brightness()``

        Parameters
        ----------
        path_to_images : str
            Path to the directory containing images for analysis.

        file_extension : str, optional
            Extension of the image files. Default is 'tiff'.

        selected_id : list, optional
            List of IDs that must be part of the image name to distinguish them
            from others. Default is an empty list, which means all images in
            the directory will be processed.

        fille_name_part : str, optional
            Part of the file name to filter images. Default is an empty string.

        selection_opt : bool, optional
            Whether to run ``select_nuclei()`` with the defined parameters. Default is True.

        include_img : bool, optional
            Whether to include the images in the result dictionary. Default is True.

        test_series : int, optional
            Number of images to test the parameters and return results. Default is 0,
            which means all images in the directory will be processed.

        Returns
        -------
        results_dict : dict
            Dictionary containing results for each image in the directory.
            Keys correspond to image file names.

        Notes
        -----
        This method runs the complete nuclei and chromatinization analysis pipeline.

        Parameters must be set appropriately before calling to ensure correct results.
        """

        results_dict = {}
        results_img = {}
        results_img_raw = {}

        files = glob.glob(os.path.join(path_to_images, "*." + file_extension))

        if len(fille_name_part) > 0:
            files = [x for x in files if fille_name_part.lower() in x.lower()]

        if len(selected_id) > 0:
            selected_id = [str(x) for x in selected_id]
            files = [
                x
                for x in files
                if re.sub("_.*", "", os.path.basename(x)) in selected_id
            ]

        if test_series > 0:

            files = random.sample(files, test_series)

        self.show_plots = False
        self.series_im = True

        print("\nFile analysis:\n\n")

        for file in tqdm(files):

            print(file)

            self.show_plots = False

            image = self.load_image(file)

            self.input_image(image)

            self.find_nuclei()

            tmp = None

            if selection_opt is True:
                self.select_nuclei()
                tmp = self.get_results_nuclei_selected()

            else:
                tmp = self.get_results_nuclei()

            if tmp is not None:

                if tmp[0] is not None:

                    results_dict[str(os.path.basename(file))] = tmp[0]
                    results_img[str(os.path.basename(file))] = tmp[1]
                    results_img_raw[str(os.path.basename(file))] = image
                    del tmp
                    del image

        results_dict_tmp = self.repairing_nuclei(results_dict)

        results_dict = {}

        print("\nChromatization searching:\n\n")

        for ke in tqdm(results_dict_tmp.keys()):

            tmp = None

            try:
                self._nuclei_chromatinization_series(
                    results_img_raw[ke], results_dict_tmp[ke]
                )
                tmp = self.get_results_nuclei_chromatinization()
            except:
                print(f"Sample {ke} could not be processed.")

            if tmp is not None:

                if tmp[0] is not None:

                    tmp[0].pop("coords")

                    if include_img:
                        results_dict[str(os.path.basename(ke))] = {
                            "stats": tmp[0],
                            "img": cv2.hconcat([results_img[ke], tmp[1]]),
                        }
                        del tmp
                    else:
                        results_dict[str(os.path.basename(ke))] = tmp[0]
                        del tmp

            else:
                print(f"Unable to obtain results for {print(ke)}")

        self.show_plots = True
        self.series_im = False

        return results_dict

    def series_analysis_nuclei(
        self,
        path_to_images: str,
        file_extension: str = "tiff",
        selected_id: list = [],
        fille_name_part: str = "",
        selection_opt: bool = True,
        include_img: bool = True,
        test_series: int = 0,
    ):
        """
        Performs analysis on the image provided by the ``input_image()`` method
        using default or user-defined parameters.

        This method runs nuclei detection and selection using the currently set
        parameters. Users can adjust image preprocessing and nuclei detection
        parameters before running the analysis.

        To show current parameters, use:
            - ``current_parameters_nuclei``
            - ``current_parameters_img_adj``

        To set new parameters, use:
            - ``set_nms()``
            - ``set_prob()``
            - ``set_adj_image_gamma()``
            - ``set_adj_image_contrast()``
            - ``set_adj_image_brightness()``
            - ``set_nuclei_circularity()``
            - ``set_nuclei_size()``
            - ``set_nuclei_min_mean_intensity()``

        Parameters
        ----------
        path_to_images : str
            Path to the directory containing images for analysis.

        file_extension : str, optional
            Extension of the image files. Default is 'tiff'.

        selected_id : list, optional
            List of IDs that must be part of the image name to distinguish them
            from others. Default is an empty list, which means all images in
            the directory will be processed.

        fille_name_part : str, optional
            Part of the file name to filter images. Default is an empty string.

        selection_opt : bool, optional
            Whether to run the ``select_nuclei()`` method with the defined parameters.
            Default is True.

        include_img : bool, optional
            Whether to include the images in the result dictionary. Default is True.

        test_series : int, optional
            Number of images to test the parameters and return results. Default is 0,
            which means all images in the directory will be processed.

        Returns
        -------
        results_dict : dict
            Dictionary containing results for each image in the directory.
            Keys correspond to image file names.
        """

        results_dict = {}
        results_img = {}

        files = glob.glob(os.path.join(path_to_images, "*." + file_extension))

        if len(fille_name_part) > 0:
            files = [x for x in files if fille_name_part.lower() in x.lower()]

        if len(selected_id) > 0:
            selected_id = [str(x) for x in selected_id]
            files = [
                x
                for x in files
                if re.sub("_.*", "", os.path.basename(x)) in selected_id
            ]

        if test_series > 0:

            files = random.sample(files, test_series)

        self.show_plots = False
        self.series_im = True

        print("\nFile analysis:\n\n")

        for file in tqdm(files):

            print(file)

            image = self.load_image(file)

            self.input_image(image)

            self.find_nuclei()

            if self.nuclei_results["nuclei"] is not None:

                tmp = [None]

                if selection_opt is True:
                    self.select_nuclei()
                    tmp = self.get_results_nuclei_selected()

                else:
                    tmp = self.get_results_nuclei()

                if tmp is not None:

                    if tmp[0] is not None:

                        if include_img:
                            results_dict[str(os.path.basename(file))] = tmp[0]
                            results_img[str(os.path.basename(file))] = tmp[1]

                            del tmp

                        else:
                            results_dict[str(os.path.basename(file))] = tmp[0]
                            del tmp

                else:
                    print(f"Unable to obtain results for {print(file)}")

            else:

                print(f"Unable to obtain results for {print(file)}")

        self.show_plots = True
        self.series_im = False

        results_dict_tmp = self.repairing_nuclei(results_dict)

        if include_img is False:

            return results_dict_tmp

        else:

            results_dict = {}

            for ke in results_dict_tmp.keys():

                nuclei_mask = adjust_img_16bit(
                    cv2.cvtColor(
                        self.create_mask(results_dict_tmp[ke], results_img[ke]),
                        cv2.COLOR_BGR2GRAY,
                    ),
                    color="blue",
                )
                concatenated_image = cv2.hconcat([results_img[ke], nuclei_mask])

                cred = results_dict_tmp[ke]
                # cred.pop('coords')

                results_dict[ke] = {"stats": cred, "img": concatenated_image}

            return results_dict


class NucleiDataManagement:
    """
    Manages nuclei analysis data obtained from the `NucleiFinder` class,
    including nuclei properties and optionally Image Stream (IS) data.

    This class allows loading nuclei data from JSON files or directly from
    `NucleiFinder` analysis results, converting them to pandas DataFrames,
    adding IS data, concatenating results from multiple experiments, and
    saving results in JSON or CSV format. It also provides helper methods
    for merging, filtering, and retrieving data.

    Attributes
    ----------
    nuceli_data : dict
        Dictionary storing nuclei properties for each image or experiment.

    experiment_name : str
        Name of the experiment.

    nuceli_data_df : pd.DataFrame or None
        DataFrame representation of nuclei properties.

    nuclei_IS_data : pd.DataFrame or None
        DataFrame of nuclei data merged with IS data.

    concat_data : list or None
        List of other `NucleiDataManagement` objects added for combined analysis.

    Methods
    -------
    load_nuc_dict(path)
        Load nuclei data from a JSON dictionary file (*.nuc) and initialize the object.
        _convert_to_df()
        Convert nuclei dictionary data to a pandas DataFrame.

    add_IS_data(IS_data, IS_features)
        Merge Image Stream (IS) data with nuclei data.

    get_data()
        Retrieve the nuclei data as a pandas DataFrame.

    get_data_with_IS()
        Retrieve the nuclei data merged with IS data.

    save_nuc_project(path)
        Save nuclei data as a JSON file with *.nuc extension.

    save_results_df(path)
        Save nuclei data as a CSV file.

    save_results_df_with_IS(path)
        Save nuclei data merged with IS data as a CSV file.

    add_experiment(data_list)
        Add other `NucleiDataManagement` objects for concatenated analysis.

    get_mutual_experiments_data(inc_is)
        Retrieve concatenated nuclei data from multiple experiments.

    save_mutual_experiments(path, inc_is)
        Save concatenated data from multiple experiments as a CSV file.
    """

    def __init__(self, nuclei_data: dict, experiment_name: str):
        """
        Initialize a NucleiDataManagement object with nuclei data and experiment name.

        Parameters
        ----------
        nuclei_data : dict
            Dictionary containing nuclei properties for each image or experiment.
            If the dictionary entries have keys 'stats' and 'img', only 'stats' are stored.

        experiment_name : str
            Name of the experiment.

        Attributes
        ----------
        nuceli_data : dict
            Dictionary storing nuclei properties for each image or experiment.

        experiment_name : str
            Name of the experiment.

        nuceli_data_df : pd.DataFrame or None
            DataFrame representation of nuclei properties (initialized as None).

        nuclei_IS_data : pd.DataFrame or None
            DataFrame of nuclei data merged with Image Stream (IS) data (initialized as None).

        concat_data : list or None
            List of other `NucleiDataManagement` objects added for combined analysis (initialized as None).
        """

        if set(nuclei_data[list(nuclei_data.keys())[0]].keys()) == set(
            ["stats", "img"]
        ):

            self.nuceli_data = {}

            for k in nuclei_data.keys():
                self.nuceli_data[k] = nuclei_data[k]["stats"]

            for k in self.nuceli_data.keys():
                if "coords" in self.nuceli_data[k].keys():
                    self.nuceli_data[k].pop("coords")

        else:
            self.nuceli_data = nuclei_data

            for k in self.nuceli_data.keys():
                if "coords" in self.nuceli_data[k].keys():
                    self.nuceli_data[k].pop("coords")

        self.experiment_name = experiment_name
        """Name of the experiment."""

        self.nuceli_data_df = None
        """Stored DataFrame representation of nuclei features"""

        self.nuclei_IS_data = None
        """Stored DataFrame of data from Image Stream (IS)."""

        self.concat_data = None
        """Sotored list of other `NucleiDataManagement` objects."""

    @classmethod
    def load_nuc_dict(cls, path: str):
        """
        Initialize a NucleiDataManagement object from a JSON dictionary file.

        The loaded data must be previously saved using the ``save_nuc_project()`` method.

        Parameters
        ----------
        path : str
            Path to the *.nuc JSON file containing nuclei data.
        """

        if ".nuc" in path:

            if os.path.exists(path):

                with open(path, "r") as json_file:
                    loaded_data = json.load(json_file)

                return cls(loaded_data, os.path.splitext(os.path.basename(path))[0])

            else:
                raise ValueError("\nInvalid path!")

        else:
            raise ValueError(
                "\nInvalid dictionary to load. It must contain a .nuc extension!"
            )

    def _convert_to_df(self):
        """
        Helper method that converts the internal nuclei dictionary into a pandas DataFrame.

        This method iterates over the nuclei data stored in `self.nuceli_data`,
        flattens the information for each nucleus, computes aggregate statistics
        for associated spots if present, and stores the resulting DataFrame in
        `self.nuceli_data_df`.
        """

        nuclei_data = self.nuceli_data

        data = []

        for i in tqdm(nuclei_data.keys()):
            for n, _ in enumerate(nuclei_data[i]["area"]):
                row = {
                    "id_name": re.sub("_.*", "", i),
                    "nuclei_area": nuclei_data[i]["area"][n],
                    "nuclei_area_bbox": nuclei_data[i]["area_bbox"][n],
                    "nuclei_equivalent_diameter_area": nuclei_data[i][
                        "equivalent_diameter_area"
                    ][n],
                    "nuclei_feret_diameter_max": nuclei_data[i]["feret_diameter_max"][
                        n
                    ],
                    "nuclei_axis_major_length": nuclei_data[i]["axis_major_length"][n],
                    "nuclei_axis_minor_length": nuclei_data[i]["axis_minor_length"][n],
                    "nuclei_circularity": nuclei_data[i]["circularity"][n],
                    "nuclei_eccentricity": nuclei_data[i]["eccentricity"][n],
                    "nuclei_perimeter": nuclei_data[i]["perimeter"][n],
                    "nuclei_ratio": nuclei_data[i]["ratio"][n],
                    "nuclei_solidity": nuclei_data[i]["solidity"][n],
                }

                if "spot_size_area" in nuclei_data[i]:
                    if len(nuclei_data[i]["spot_size_area"][n]) > 0:
                        row.update(
                            {
                                "spot_n": len(nuclei_data[i]["spot_size_area"][n]),
                                "avg_spot_area": np.mean(
                                    nuclei_data[i]["spot_size_area"][n]
                                ),
                                "avg_spot_area_bbox": np.mean(
                                    nuclei_data[i]["spot_size_area_bbox"][n]
                                ),
                                "avg_spot_perimeter": np.mean(
                                    nuclei_data[i]["spot_perimeter"][n]
                                ),
                                "sum_spot_area": np.sum(
                                    nuclei_data[i]["spot_size_area"][n]
                                ),
                                "sum_spot_area_bbox": np.sum(
                                    nuclei_data[i]["spot_size_area_bbox"][n]
                                ),
                                "sum_spot_perimeter": np.sum(
                                    nuclei_data[i]["spot_perimeter"][n]
                                ),
                                "avg_spot_axis_major_length": np.mean(
                                    nuclei_data[i]["spot_axis_major_length"][n]
                                ),
                                "avg_spot_axis_minor_length": np.mean(
                                    nuclei_data[i]["spot_axis_minor_length"][n]
                                ),
                                "avg_spot_eccentricity": np.mean(
                                    nuclei_data[i]["spot_eccentricity"][n]
                                ),
                                "avg_spot_size_equivalent_diameter_area": np.mean(
                                    nuclei_data[i][
                                        "spot_size_equivalent_diameter_area"
                                    ][n]
                                ),
                                "sum_spot_size_equivalent_diameter_area": np.sum(
                                    nuclei_data[i][
                                        "spot_size_equivalent_diameter_area"
                                    ][n]
                                ),
                            }
                        )
                    else:
                        row.update(
                            {
                                k: 0
                                for k in [
                                    "spot_n",
                                    "avg_spot_area",
                                    "avg_spot_area_bbox",
                                    "avg_spot_perimeter",
                                    "sum_spot_area",
                                    "sum_spot_area_bbox",
                                    "sum_spot_perimeter",
                                    "avg_spot_axis_major_length",
                                    "avg_spot_axis_minor_length",
                                    "avg_spot_eccentricity",
                                    "avg_spot_size_equivalent_diameter_area",
                                    "sum_spot_size_equivalent_diameter_area",
                                ]
                            }
                        )

                data.append(row)

        nuclei_df = pd.DataFrame(data)

        nuclei_df["nuclei_per_img"] = nuclei_df.groupby("id_name")["id_name"].transform(
            "count"
        )
        nuclei_df["set"] = self.experiment_name

        self.nuceli_data_df = nuclei_df

    def add_IS_data(self, IS_data: pd.DataFrame, IS_features: list = []):
        """
        Merge Image Stream (IS) data with nuclei analysis data.

        This method concatenates IS (Image Stream, https://cytekbio.com/pages/imagestream)
        results with the nuclei data stored in the object. The merge is performed based
        on object IDs, allowing joint analysis of nuclei features and IS features.

        Parameters
        ----------
        IS_data : pd.DataFrame
            DataFrame containing IS data results.

        IS_features : list, optional
            List of features to extract from the IS data. Default is an empty list.

        Notes
        -----
        The merged data will be stored in the attribute `self.nuclei_IS_data`.
        """

        nuclei_data = self._get_df()

        IS_data["set"] = self.experiment_name

        if len(IS_features) > 0:
            IS_features = list(set(IS_features + ["Object Number", "set"]))
            IS_data = IS_data[IS_features]

        nuclei_data["id"] = (
            nuclei_data["id_name"].astype(str) + "_" + nuclei_data["set"]
        )
        IS_data["id"] = IS_data["Object Number"].astype(str) + "_" + IS_data["set"]

        merged_data = pd.merge(nuclei_data, IS_data, on="id", how="left")
        merged_data.pop("set_x")
        merged_data = merged_data.rename(columns={"set_y": "set"})

        self.nuclei_IS_data = merged_data

    def _get_df(self):
        """
        Helper method to retrieve the nuclei data as a pandas DataFrame.

        If the internal DataFrame `self.nuceli_data_df` has not been created yet,
        this method calls `_convert_to_df()` to generate it from `self.nuceli_data`.
        """

        if self.nuceli_data_df is None:
            self._convert_to_df()

        return self.nuceli_data_df

    def get_data_with_IS(self):
        """
        Retrieve nuclei results for a single project including IS data.

        Returns
        -------
        pd.DataFrame or None
            DataFrame containing nuclei results merged with IS (Image Stream) data
            added via `self.add_IS_data()`. Returns None if no IS data has been added.
        """

        if self.nuclei_IS_data is None:
            print("\nNothing to return!")
        return self.nuclei_IS_data

    def get_data(self):
        """
        Retrieve nuclei results for a single project as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            DataFrame containing nuclei analysis results for the experiment.
        """

        return self._get_df()

    def save_nuc_project(self, path: str = ""):
        """
        Save nuclei results as a JSON file with a *.nuc extension.

        The saved data can later be loaded using the `cls.load_nuc_dict()` method.
        Results must be obtained from the `NucleiFinder` class using
        `series_analysis_nuclei()` or `series_analysis_chromatinization()` methods.

        Parameters
        ----------
        path : str, optional
            Directory where the results will be saved. Default is the current working directory.
        """

        data = self.nuceli_data

        if len(data.keys()) > 0:
            full_path = os.path.join(path, self.experiment_name)

            with open(full_path + ".nuc", "w") as json_file:
                json.dump(data, json_file, indent=4)
        else:
            print("\nData not provided!")

    def save_results_df(self, path: str = ""):
        """
        Save nuclei results for a single project as a CSV file.

        Results must be obtained from the `NucleiFinder` class using
        `series_analysis_nuclei()` or `series_analysis_chromatinization()` methods.

        Parameters
        ----------
        path : str, optional
            Directory where the CSV file will be saved. Default is the current working directory.
        """

        data = self.get_data()

        full_path = os.path.join(path, f"{self.experiment_name}.csv")

        data.to_csv(full_path, index=False)

    def save_results_df_with_IS(self, path: str = ""):
        """
        Save nuclei results with IS data for a single project as a CSV file.

        Results must be obtained from the `NucleiFinder` class using
        `series_analysis_nuclei()` or `series_analysis_chromatinization()` methods.
        IS data should have been added via `self.add_IS_data()`.

        Parameters
        ----------
        path : str, optional
            Directory where the CSV file will be saved. Default is the current working directory.
        """

        data = self.get_data_with_IS()

        if data is None:
            raise ValueError("There was nothing to save.")

        full_path = os.path.join(path, f"{self.experiment_name}_IS.csv")
        data.to_csv(full_path, index=False)

    def add_experiment(self, data_list: list):
        """
        Add additional NucleiDataManagement objects from other experiments for concatenation.

        Parameters
        ----------
        data_list : list
            List of `NucleiDataManagement` objects from separate experiments to be added.
        """

        valid_class = []
        for obj in data_list:
            if isinstance(obj, self.__class__):
                valid_class.append(obj)
            else:
                print(f"Object {obj} is invalid type.")

        self.concat_data = valid_class

    def get_mutual_experiments_data(self, inc_is: bool = False):
        """
        Retrieve concatenated NucleiDataManagement data from other added experiments.

        Parameters
        ----------
        inc_is : bool, optional
            Whether to include IS (Image Stream) data, if it was added to each experiment. Default is False.

        Returns
        -------
        pd.DataFrame
            Concatenated nuclei data (with or without IS data) from all added experiments.
        """

        if self.concat_data is not None:
            if inc_is:

                try:
                    final_df = pd.concat(
                        [x.get_data_with_IS() for x in self.concat_data]
                        + [self.get_data_with_IS()]
                    )
                except:
                    raise ValueError(
                        "Lack of IS data in some object. Check if the IS data was added to each project."
                    )

            else:
                final_df = pd.concat(
                    [x.get_data() for x in self.concat_data] + [self.get_data()]
                )

            return final_df

        raise ValueError("No object to concatenate. Nothing to return!")

    def save_mutual_experiments(self, path: str = "", inc_is: bool = False):
        """
        Save concatenated NucleiDataManagement data from added experiments as a CSV file.

        Parameters
        ----------
        inc_is : bool, optional
            Whether to include IS (Image Stream) data, if it was added to each experiment. Default is False.
        """

        dt = self.get_mutual_experiments_data(inc_is=inc_is)

        experimets = [self.experiment_name] + [
            n.experiment_name for n in self.concat_data
        ]

        experimets_names = "_".join(experimets)

        if inc_is:
            full_path = os.path.join(path, f"{experimets_names}_IS.csv")
        else:
            full_path = os.path.join(path, f"{experimets_names}.csv")

        dt.to_csv(full_path, index=False)


class GroupAnalysis:
    """
    A class for performing multivariate analysis, dimensionality reduction,
    clustering, and differential feature analysis (DFA) on biological or
    experimental datasets.

    This class provides tools for:
    - Scaling and PCA of input data
    - UMAP embedding and DBSCAN clustering
    - Differential Feature Analysis across groups
    - Proportion analysis and plotting
    - Data selection and merging with metadata

    Attributes
    ----------
    input_data : pd.DataFrame
        The primary dataset containing features for analysis.

    input_metadata : pd.DataFrame
        Metadata corresponding to the input data, including identifiers and group labels.

    tmp_data : pd.DataFrame
        Temporary copy of the input data, used for feature selection and filtering.

    tmp_metadata : pd.DataFrame
        Temporary copy of metadata, used for filtered or subsetted operations.

    scaled_data : np.ndarray or None
        Scaled version of the temporary dataset (`tmp_data`), updated after `data_scale()`.

    PCA_results : np.ndarray or None
        Results of PCA transformation applied on scaled data.

    var_data : np.ndarray or None
        Explained variance ratio from PCA.

    knee_plot : matplotlib.figure.Figure or None
        Figure of cumulative explained variance for PCA components.

    UMAP_data : np.ndarray or None
        Embedding results from UMAP dimensionality reduction.

    UMAP_plot : dict
        Dictionary containing UMAP plots. Keys: 'static' (matplotlib) and 'html' (plotly).

    dblabels : list or None
        Cluster labels assigned by DBSCAN after UMAP embedding.

    explained_variance_ratio : np.ndarray or None
        Explained variance ratio of PCA components.

    DFA_results : pd.DataFrame or None
        Results of Differential Feature Analysis (DFA).

    proportion_stats : pd.DataFrame or None
        Statistics from proportion analysis.

    proportion_plot : matplotlib.figure.Figure or None
        Figure of proportion analysis results.

    Methods
    -------
    resest_project():
        Reset all temporary and analysis results to initial state.

    load_data(data, ids_col='id_name', set_col='set'):
        Class method to load data and metadata and initialize the object.

    groups:
        Property returning available groups in the metadata.

    get_DFA(), get_PCA(), get_knee_plot(), get_var_data(), get_scaled_data():
        Methods to retrieve previously computed results.

    UMAP(), db_scan(), UMAP_on_clusters():
        Methods for dimensionality reduction and clustering visualization.

    DFA(meta_group_by='sets', sets={}, n_proc=5):
        Perform Differential Feature Analysis.

    proportion_analysis(grouping_col='sets', val_col='nuclei_per_img', ...):
        Perform and plot proportion analysis across groups.
    """

    def __init__(
        self,
        input_data,
        input_metadata,
    ):
        """
        Initialize a GroupAnalysis instance with data and metadata.

        Parameters
        ----------
        input_data : pd.DataFrame
            Dataset containing features for analysis. Rows represent samples and columns represent features.

        input_metadata : pd.DataFrame
            Metadata corresponding to `input_data`, including sample identifiers and group labels.
        """

        self.input_data = input_data
        """Stored input dataset for analysis."""

        self.input_metadata = input_metadata
        """Stored metadata associated with `input_data`."""

        self.tmp_metadata = input_metadata
        """Temporary copy of `input_data` used for filtering, selection, or scaling."""

        self.tmp_data = input_data
        """Temporary copy of `input_metadata` used for filtered operations."""

        self.scaled_data = None
        """Stored scaled version of `tmp_data` after normalization or standardization."""

        self.PCA_results = None
        """ Stored results of PCA transformation applied on `scaled_data`."""

        self.var_data = None
        """Sotred explained variance ratio for PCA components."""

        self.knee_plot = None
        """Figure showing cumulative explained variance for PCA."""

        self.UMAP_data = None
        """Stored embedding coordinates from UMAP dimensionality reduction."""

        self.UMAP_plot = {"static": {}, "html": {}}
        """Stored dictionary containing UMAP plots: 'static' (matplotlib) and 'html' (plotly)."""

        self.dblabels = None
        """Stored cluster labels assigned by DBSCAN after UMAP embedding."""

        self.explained_variance_ratio = None
        """Stored explained variance ratio of PCA components."""

        self.DFA_results = None
        """Stored Differential Feature Analysis (DFA) results."""

        self.proportion_stats = None
        """Stored statistics from proportion analysis of groups."""

        self.proportion_plot = None
        """Figure visualizing proportion analysis results."""

    def resest_project(self):
        """
        Resets the project state by clearing or reinitializing various attributes.

        This method resets the following attributes to initial values:
        - `tmp_metadata`
        - `tmp_data`
        - `scaled_data`
        - `PCA_results`
        - `var_data`
        - `knee_plot`
        - `UMAP_data`
        - `UMAP_plot`
        - `dblabels`
        - `explained_variance_ratio`
        - `DFA_results`

        This method is typically called to reinitialize the project data and results, preparing the system for new computations or project resets.
        """

        self.tmp_metadata = self.input_metadata
        self.tmp_data = self.input_data
        self.scaled_data = None
        self.PCA_results = None
        self.var_data = None
        self.knee_plot = None
        self.UMAP_data = None
        self.UMAP_plot = {"static": {}, "html": {}}
        self.dblabels = None
        self.explained_variance_ratio = None
        self.DFA_results = None
        self.proportion_stats = None
        self.proportion_plot = None

    @classmethod
    def load_data(cls, data, ids_col: str = "id_name", set_col: str = "set"):
        """
        Load data and initialize the class by storing both the feature data and metadata.

        Parameters
        ----------
        data : pd.DataFrame
            Input dataset used for group analysis. Must contain both feature columns and
            metadata columns specified by `ids_col` and `set_col`.

        ids_col : str, optional
            Name of the column containing unique object identifiers.
            Default is ``'id_name'``.

        set_col : str, optional
            Name of the column specifying group or set assignment for each object.
            Default is ``'set'``.

        Notes
        -----
        This method performs in-place initialization of the class and does not return
        a separate object. All loaded data and metadata become available through the
        class attributes for downstream analysis.

        This method updates internal class attributes:

        - **input_data** : pd.DataFrame
          Cleaned feature table with index set to object IDs.

        - **tmp_data** : pd.DataFrame
          Copy of `input_data` used for temporary operations.

        - **input_metadata** : pd.DataFrame
          Metadata containing object IDs and group assignments.

        - **tmp_metadata** : pd.DataFrame
          Copy of `input_metadata` for temporary operations.
        """

        data = data.dropna()

        metadata = pd.DataFrame()
        metadata["id"] = data[ids_col]
        metadata["sets"] = data[set_col]

        data.index = data[ids_col]

        try:
            data.pop("id_name")
        except:
            None

        try:
            data.pop("Object Number")
        except:
            None

        return cls(data, metadata)

    @property
    def groups(self):
        """
        Return information about available groups in the metadata for ``self.DFA``.

        Returns
        -------
        dict
            Dictionary mapping each metadata column name to a list of unique groups
            available in that column.
        """

        try:
            return {
                "sets": set(self.tmp_metadata["sets"]),
                "full_name": set(self.tmp_metadata["full_name"]),
            }
        except:
            return {"sets": set(self.tmp_metadata["sets"])}

    def get_DFA(self):
        """
        Retrieve the DFA results produced by the ``DFA()`` method.

        Returns
        -------
        pd.DataFrame
            The DFA results stored in ``self.DFA_results``.
        """

        if None in self.DFA_results:
            print("\nNo results to return! Please run the DFA() method first.")
        else:
            return self.DFA_results

    def get_PCA(self):
        """
        Retrieve the PCA results produced by the ``PCA()`` method.

        Returns
        -------
        np.ndarray
            The PCA results stored in ``self.PCA_results``.
        """

        if None in self.PCA_results:
            print("\nNo results to return! Please run the PCA() method first.")
        else:
            return self.PCA_results

    def get_knee_plot(self, show: bool = True):
        """
        Retrieve the knee plot of cumulative explained variance generated by the ``var_plot()`` method.

        Parameters
        ----------
        show : bool, optional
            If ``True`` (default), the knee plot is displayed.

        Returns
        -------
        matplotlib.figure.Figure
            The figure object containing the knee plot.
        """

        if self.knee_plot is None:
            print("\nNo results to return! Please run the var_plot() method first.")
        else:
            if cfg._DISPLAY_MODE:
                if show is True:
                    self.knee_plot
                    try:
                        display(self.knee_plot)
                    except:
                        None

            return self.knee_plot

    def get_var_data(self):
        """
        Retrieve the explained variance data from the ``var_plot()`` method.

        Returns
        -------
        np.ndarray
            Array containing the explained variance values stored in ``self.var_data``.
        """

        if None in self.var_data:
            print("\nNo results to return! Please run the var_plot() method first.")
        else:
            return self.var_data

    def get_scaled_data(self):
        """
        Retrieve the scaled data produced by the ``data_scale()`` method.

        Returns
        -------
        np.ndarray
            Scaled data stored in ``self.scaled_data``.
        """

        if None in self.scaled_data:
            print("\nNo results to return! Please run the data_scale() method first.")
        else:
            return self.scaled_data

    def get_UMAP_data(self):
        """
        Retrieve the UMAP-transformed data generated by the ``UMAP()`` method.

        Returns
        -------
        np.ndarray
            UMAP-embedded data stored in ``self.UMAP_data``.
        """

        if None in self.UMAP_data:
            print("\nNo results to return! Please run the UMAP() method first.")
        else:
            return self.UMAP_data

    def get_UMAP_plots(self, plot_type: str = "static", show: bool = True):
        """
        Retrieve UMAP plots generated by the ``UMAP()`` and/or ``UMAP_on_clusters()`` methods.

        Parameters
        ----------
        show : bool, optional
            Whether to display the UMAP plots. Default is True.

        Returns
        -------
        dict of matplotlib.figure.Figure
            A dictionary containing the UMAP plots. Keys correspond to plot names, and values are the figure objects.
        """

        if plot_type == "html":

            if len(self.UMAP_plot["html"].keys()) == 0:
                print(
                    "\nNo results to return! Please run the UMAP() and / or UMAP_on_clusters() methods first."
                )
            else:
                if cfg._DISPLAY_MODE:
                    if show:
                        for k in self.UMAP_plot["html"].keys():
                            self.UMAP_plot["html"][k]
                            try:
                                display(self.UMAP_plot["html"][k])
                            except:
                                None

                return self.UMAP_plot["html"]

        else:

            if len(self.UMAP_plot["static"].keys()) == 0:
                print(
                    "\nNo results to return! Please run the UMAP() and / or UMAP_on_clusters() methods first."
                )
            else:
                if cfg._DISPLAY_MODE:
                    if show:
                        for k in self.UMAP_plot["static"].keys():
                            self.UMAP_plot["static"][k]
                            try:
                                display(self.UMAP_plot["static"][k])
                            except:
                                None

                return self.UMAP_plot["static"]

    def select_data(self, features_list: list = []):
        """
        Select specific features (columns) from the dataset for further analysis.

        Parameters
        ----------
        features_list : list of str, optional
            List of feature names (column names) to select from the dataset. Default is an empty list, which selects no features.

        Notes
        -----
        Modifies the `self.tmp_data` attribute to contain only the selected features from `self.input_data`.
        """

        dat = self.input_data.copy()

        not_in_columns = [name for name in features_list if name not in dat.columns]

        if not_in_columns:
            print("These names are not in data", not_in_columns)
        else:
            print("All names are present in data.")

        in_columns = [name for name in features_list if name in dat.columns]

        dat = dat[in_columns]

        self.tmp_data = dat

    def data_scale(self):
        """
        Scale the data using standardization (z-score normalization).

        This method applies `StandardScaler` from scikit-learn to the temporary dataset (`self.tmp_data`) and stores the scaled data.

        Notes
        -----
        Modifies the `self.scaled_data` attribute to contain the standardized version of `self.tmp_data`.
        """

        if None not in self.tmp_data:

            def is_id_column(name: str):
                name_lower = name.lower()
                return name_lower == "id" or "id_" in name_lower or "_id" in name_lower

            tmp = self.tmp_data

            cols_with_strings = [
                c
                for c in tmp.columns
                if tmp[c].apply(lambda x: isinstance(x, str)).any()
            ]

            cols_id_pattern = [c for c in tmp.columns if is_id_column(c)]

            cols_to_drop = list(set(cols_id_pattern + cols_with_strings))

            tmp = tmp.drop(columns=cols_to_drop)

            scaler = StandardScaler()

            self.scaled_data = scaler.fit_transform(tmp)

        else:
            print(
                "\nNo data to scale. Please use the load_data() method first, and optionally the select_data() method."
            )

    def PCA(self):
        """
        Perform Principal Component Analysis (PCA) on the scaled data.

        This method reduces the dimensionality of `self.scaled_data` while retaining the maximum variance.

        Notes
        -----
        Modifies the `self.PCA_results` attribute with the PCA-transformed data.
        """

        if None not in self.scaled_data:
            pca = PCA(n_components=self.scaled_data.shape[1])
            self.PCA_results = pca.fit_transform(self.scaled_data)
            self.explained_variance_ratio = pca.explained_variance_ratio_
        else:
            print("\nNo data for PCA. Please use the data_scale() method first.")

    def var_plot(self):
        """
        Plot the cumulative explained variance of the principal components from PCA.

        This method visualizes the cumulative explained variance to help determine how many components capture most of the variance.

        Notes
        -----
        Stores results in the following attributes:
        - `self.var_data` (np.ndarray): Explained variance ratio for each principal component.
        - `self.knee_plot` (matplotlib.figure.Figure): Figure of the cumulative explained variance plot.
        """

        if None not in self.PCA_results:

            fig, _ = plt.subplots(figsize=(15, 7))
            explained_var = self.explained_variance_ratio

            cumulative_var = np.cumsum(explained_var)

            # Plot the cumulative explained variance as a function of the number of components
            plt.plot(cumulative_var)
            plt.xlabel("Number of Components")
            plt.ylabel("Cumulative Explained Variance")
            plt.title("Explained variance of PCs")
            plt.xticks(np.arange(0, len(cumulative_var) + 1, step=1))

            self.var_data = explained_var
            self.knee_plot = fig

        else:

            print(
                "\nNo data for variance explanation analysis. Please use the PCA() method first."
            )

    def UMAP(
        self,
        PC_num: int = 5,
        factorize_with_metadata: bool = False,
        harmonize_sets: bool = True,
        n_neighbors: int = 25,
        min_dist: float = 0.01,
        n_components: int = 2,
    ):
        """
         Perform UMAP (Uniform Manifold Approximation and Projection) dimensionality reduction on PCA results.

         UMAP is applied to the top principal components, optionally using metadata labels to influence the embedding. Generates both 2D/3D embeddings and visualizations.

         Parameters
         ----------
         PC_num : int, optional
             Number of top principal components to use for UMAP embedding. Default is 5.

         factorize_with_metadata : bool, optional
             Whether to use metadata (e.g., 'sets') to factorize UMAP embedding. Default is False.

        harmonize_sets : bool, optional
             If True, applies harmonization across data sets before computing the UMAP embedding.
             Default is True.

         n_neighbors : int, optional
             Number of neighbors for UMAP to compute local structure. Default is 25.

         min_dist : float, optional
             Minimum distance between points in the low-dimensional embedding. Default is 0.01.

         n_components : int, optional
             Number of dimensions for the UMAP embedding. Default is 2.

         Notes
         -----
         Stores results in the following attributes:
         - `self.UMAP_data` (np.ndarray): UMAP-transformed data.
         - `self.UMAP_plot['static']['PrimaryUMAP']` (matplotlib.figure.Figure): Static visualization of UMAP embedding.
         - `self.UMAP_plot['html']['PrimaryUMAP']` (plotly.graph_objs.Figure): Interactive Plotly visualization of UMAP embedding.
        """

        if None not in self.PCA_results:

            reducer = umap.UMAP(
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=n_components,
                random_state=42,
            )

            pca_res = self.PCA_results

            if harmonize_sets:

                pca_res = np.array(pca_res)

                pca_res = np.array(
                    harmonize.run_harmony(
                        pca_res, self.input_metadata, vars_use="sets"
                    ).Z_corr
                ).T

            if factorize_with_metadata:
                numeric_labels = pd.Categorical(self.tmp_metadata["sets"]).codes

                umap_result = reducer.fit_transform(
                    pca_res[:, : PC_num + 1], y=numeric_labels
                )

            else:
                umap_result = reducer.fit_transform(pca_res[:, : PC_num + 1])

            umap_result_plot = pd.DataFrame(umap_result.copy())

            umap_result_plot["clusters"] = list(self.tmp_metadata["sets"])

            static_fig = umap_static(umap_result_plot, width=8, height=6)

            html_fig = umap_html(umap_result_plot, width=800, height=600)

            self.UMAP_data = umap_result

            self.UMAP_plot["static"]["PrimaryUMAP"] = static_fig
            self.UMAP_plot["html"]["PrimaryUMAP"] = html_fig

        else:

            print("\nNo data for UMAP. Please use the PCA() method first.")

    def db_scan(self, eps=0.5, min_samples: int = 10):
        """
        Perform DBSCAN clustering on UMAP-transformed data.

        DBSCAN identifies clusters based on density, labeling points in dense regions as clusters and others as noise.

        Parameters
        ----------
        eps : float, optional
            Maximum distance between two points to be considered neighbors. Default is 0.5.

        min_samples : int, optional
            Minimum number of points required to form a dense region (cluster). Default is 10.

        Notes
        -----
        Stores the results in the following attribute:
        - `self.dblabels` (list of str): Cluster labels assigned by DBSCAN for each point in the UMAP embedding.
        """

        from sklearn.cluster import DBSCAN

        if None not in self.UMAP_data:

            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            dbscan_labels = dbscan.fit_predict(self.UMAP_data)
            self.dblabels = [str(x) for x in dbscan_labels]

        else:

            print("\nNo data for DBSCAN. Please use the UMAP() method first.")

    def UMAP_on_clusters(self, min_entities: int = 50):
        """
        Generate UMAP visualizations based on clusters filtered by a minimum entity threshold.

        This method filters clusters with fewer than `min_entities` members and generates two UMAP plots:
        1. Cluster-only UMAP.
        2. Cluster + set identifier UMAP.

        Parameters
        ----------
        min_entities : int, optional
            Minimum number of entities required for a cluster to be included in the visualization. Default is 50.

        Notes
        -----
        Modifies the following attributes:
        - `self.UMAP_plot['static']['ClusterUMAP']` and `self.UMAP_plot['html']['ClusterUMAP']`: UMAP plots for filtered clusters.
        - `self.UMAP_plot['static']['ClusterXSetsUMAP']` and `self.UMAP_plot['html']['ClusterXSetsUMAP']`: UMAP plots combining clusters and set identifiers.
        - `self.tmp_data`: Filtered dataset based on clusters and sets.
        - `self.tmp_metadata`: Metadata associated with the filtered data.
        """

        if None not in self.UMAP_data:

            umap_result = pd.DataFrame(self.UMAP_data.copy())
            umap_result["id"] = self.tmp_metadata.index
            umap_result["clusters"] = self.dblabels
            umap_result = umap_result[umap_result["clusters"] != "-1"]
            tmp_metadata = self.tmp_metadata.copy()
            tmp_metadata["clusters"] = self.dblabels
            tmp_metadata = tmp_metadata[tmp_metadata["clusters"] != "-1"]
            tmp_data = self.tmp_data.copy()
            tmp_data.index = self.dblabels
            tmp_data = tmp_data[tmp_data.index != "-1"]

            label_counts_dict = Counter(self.dblabels)

            label_counts = pd.DataFrame.from_dict(
                label_counts_dict, orient="index", columns=["count"]
            )

            filtered_counts = label_counts[label_counts["count"] > min_entities]

            tmp_metadata["full_id"] = list(
                tmp_metadata["id"].astype(str) + " # " + tmp_metadata["sets"]
            )

            tmp_data.index = tmp_metadata["full_id"]
            umap_result["full_id"] = list(tmp_metadata["full_id"])

            umap_result = umap_result[
                umap_result["clusters"].isin(np.array(filtered_counts.index))
            ]
            tmp_metadata = tmp_metadata[
                tmp_metadata["clusters"].isin(np.array(filtered_counts.index))
            ]

            tmp_data = tmp_data[tmp_data.index.isin(np.array(tmp_metadata["full_id"]))]

            static_fig = umap_static(umap_result, width=8, height=6)

            html_fig = umap_html(umap_result, width=800, height=600)

            self.UMAP_plot["static"]["ClusterUMAP"] = static_fig
            self.UMAP_plot["html"]["ClusterUMAP"] = html_fig

            tmp_metadata["full_name"] = list(
                tmp_metadata["clusters"] + " # " + tmp_metadata["sets"]
            )

            label_counts_dict = Counter(list(tmp_metadata["full_name"]))

            label_counts = pd.DataFrame.from_dict(
                label_counts_dict, orient="index", columns=["count"]
            )

            filtered_counts = label_counts[label_counts["count"] > min_entities]

            tmp_data.index = tmp_metadata["full_name"]
            umap_result["clusters"] = list(tmp_metadata["full_name"])

            umap_result = umap_result[
                umap_result["clusters"].isin(np.array(filtered_counts.index))
            ]

            tmp_metadata = tmp_metadata[
                tmp_metadata["full_name"].isin(np.array(filtered_counts.index))
            ]

            tmp_data = tmp_data[tmp_data.index.isin(np.array(filtered_counts.index))]

            static_fig = umap_static(umap_result, width=8, height=6)

            html_fig = umap_html(umap_result, width=800, height=600)

            self.UMAP_plot["static"]["ClusterXSetsUMAP"] = static_fig

            self.UMAP_plot["html"]["ClusterXSetsUMAP"] = html_fig

            self.tmp_data = tmp_data
            self.tmp_metadata = tmp_metadata

        else:
            print(
                "\nNo data for visualization. Please use the UMAP() and db_scan() methods first."
            )

    ## save data
    def full_info(self):
        """
        Merge data with metadata based on the 'full_id' column.

        This method combines `self.tmp_data` and `self.tmp_metadata` into a single DataFrame if the metadata contains a 'full_id' column. If 'full_id' is not present, the method prints a warning to complete the preprocessing pipeline.

        Returns
        -------
        pd.DataFrame or None
            Merged DataFrame containing both data and metadata if 'full_id' exists; otherwise, None.
        """

        tmp_data = self.tmp_data.copy()
        tmp_metadata = self.tmp_metadata.copy()

        if "full_id" in tmp_metadata.columns:
            tmp_data.index = tmp_metadata["full_id"]

            merged_df = tmp_data.merge(
                tmp_metadata, left_index=True, right_on="full_id", how="left"
            )

            return merged_df

        else:

            print("\nMetadata is not completed!")

        #################################################################################

    def DFA(self, meta_group_by: str = "sets", sets: dict = {}, n_proc=5):
        """
        Perform Differential Feature Analysis (DFA) on specified data groups.

        This method conducts DFA using a grouping factor from metadata and a dictionary of sets for comparison. It allows for the identification of significant differences across defined sets.

        The analysis includes:
        - Mann–Whitney U test
        - Percentage of non-zero values
        - Means and standard deviations
        - Effect size metric (ESM)
        - Benjamini–Hochberg FDR correction
        - Fold-change and log2 fold-change

        Parameters
        ----------
        meta_group_by : str, optional
            Metadata column used for grouping during the analysis.
            Default is ``'sets'``.
            To view available grouping categories, use ``self.groups``.

        sets : dict, optional
            Dictionary defining groups for pairwise comparison.
            Keys correspond to group names, and values are lists of labels
            belonging to each group.

            Example
            -------
            >>> sets = {
            ...     'healthy': ['21q'],
            ...     'disease': ['71q', '77q', '109q']
            ... }
            In this configuration, the *healthy* group is compared against the
            aggregated *disease* groups.

        n_proc : int, optional
            Number of CPU cores used for parallel processing.
            Default is ``5``.

        Returns
        -------
        pandas.DataFrame or None
            A DataFrame containing statistical results for each feature, including:

            - ``feature`` : str
            - ``p_val`` : float
            - ``adj_pval`` : float
            - ``pct_valid`` : float
            - ``pct_ctrl`` : float
            - ``avg_valid`` : float
            - ``avg_ctrl`` : float
            - ``sd_valid`` : float
            - ``sd_ctrl`` : float
            - ``esm`` : float
            - ``FC`` : float
            - ``log(FC)`` : float
            - ``norm_diff`` : float
            - ``valid_group`` : str
            - ``-log(p_val)`` : float

            If ``sets`` is ``None``, results for each group are concatenated.

            Returns ``None`` in case of errors or invalid parameters.

        Notes
        -----
        - Columns containing only zeros are automatically removed.
        - p-values equal for both groups produce ``p_val = 1``.
        - Benjamini–Hochberg correction is applied separately within each group comparison.
        - Fold-change is stabilized using a small, data-derived ``low_factor``.
        - Uses ``Mann–Whitney U`` test with ``alternative='two-sided'``.

        """

        tmp_data = self.tmp_data.copy()

        tmp_data = tmp_data.select_dtypes(include="number")

        tmp_metadata = self.tmp_metadata.copy()

        if len(sets.keys()) >= 2:
            print("\nAnalysis strated on provided sets dictionary and meta_group_by...")
            tmp_data.index = list(tmp_metadata[meta_group_by])
            tmp_metadata["sets"] = tmp_metadata[meta_group_by]
            results = statistic(
                tmp_data.transpose(), sets=sets, metadata=tmp_metadata, n_proc=n_proc
            )

        else:
            print(
                "\nAnalysis strated on for all groups to each other in meta_group_by..."
            )
            tmp_data.index = list(tmp_metadata[meta_group_by])
            tmp_metadata["sets"] = tmp_metadata[meta_group_by]
            results = statistic(
                tmp_data.transpose(), sets=None, metadata=tmp_metadata, n_proc=n_proc
            )

        self.DFA_results = results

    def heatmap_DFA(self, p_value: float | int = 0.05, top_n: int = 5, figsize=(10, 5)):
        """
        Generate a heatmap of the top features from DFA results filtered by p-value and log fold change.

        Parameters
        ----------
        p_value : float or int, optional
            Significance threshold to filter features based on their p-value. Only features with p_val < p_value are included.
            Default is 0.05.

        top_n : int, optional
            Number of top features to select per group based on the 'esm' score. Default is 5.

        figsize : tuple, optional
            Size of the resulting matplotlib figure. Default is (10, 5).

        Notes
        -----
        The method displays the heatmap and stores the figure in `self.DFA_plot`.

        Conditions:
        - Only features with a positive log fold change ('log(FC)' > 0) are considered.
        - The heatmap values represent -log10(p_value) for visualization.
        """

        df_reduced = self.DFA_results.copy()

        df_reduced = df_reduced[df_reduced["log(FC)"] > 0]

        df_reduced = df_reduced[df_reduced["p_val"] < p_value]

        df_reduced = df_reduced.groupby("valid_group", group_keys=False).apply(
            lambda x: x.sort_values("esm", ascending=False).head(top_n)
        )

        df_reduced["-log(p_value)"] = -np.log10(df_reduced["p_val"])

        heatmap_data = df_reduced.pivot(
            index="feature", columns="valid_group", values="-log(p_value)"
        ).fillna(0)

        figure = plt.figure(figsize=figsize)
        sns.heatmap(
            heatmap_data,
            cmap="viridis",
            linewidths=0.5,
            linecolor="gray",
            cbar_kws={"label": "-log10(p_value)"},
            fmt=".2f",
        )
        plt.ylabel("Feature")
        plt.xlabel("Cluster")
        plt.xticks(rotation=30, ha="right")

        plt.tight_layout()

        if cfg._DISPLAY_MODE:
            plt.show()

        self.DFA_plot = figure

    def get_DFA_plot(self, show: bool = True):
        """
        Retrieve the heatmap figure generated by `heatmap_DFA()`.

        Parameters
        ----------
        show : bool, optional
            Whether to display the stored heatmap figure. Default is True.

        Returns
        -------
        matplotlib.figure.Figure
            The figure object containing the DFA heatmap.
        """

        if self.DFA_plot is None:
            print("\nNo results to return! Please run the heatmap_DFA() method first.")
        else:
            if cfg._DISPLAY_MODE:
                if show is True:
                    self.DFA_plot
                    try:
                        display(self.DFA_plot)
                    except:
                        None

            return self.DFA_plot

        df_reduced = self.DFA_results.copy()

        df_reduced = df_reduced[df_reduced["p_val"] < p_value]
        df_reduced = df_reduced[df_reduced["log(FC)"] > 0]

        df_reduced = df_reduced.groupby("valid_group", group_keys=False).apply(
            lambda x: x.sort_values("esm", ascending=False).head(top_n)
        )

        df_reduced["-log(p_value)"] = -np.log10(df_reduced["p_val"])

        heatmap_data = df_reduced.pivot(
            index="feature", columns="valid_group", values="-log(p_value)"
        ).fillna(0)

        figure = plt.figure(figsize=figsize)
        sns.heatmap(
            heatmap_data,
            cmap="viridis",
            linewidths=0.5,
            linecolor="gray",
            cbar_kws={"label": "-log10(p_value)"},
            fmt=".2f",
        )
        plt.ylabel("Feature")
        plt.xlabel("Cluster")
        plt.xticks(rotation=30, ha="right")

        plt.tight_layout()
        plt.show()

        self.DFA_plot = figure

    def print_avaiable_features(self):
        """
        Print the available features (columns) in the current dataset.

        This method lists all column names in `self.tmp_data` to help identify which features are available for analysis.

        Example
        -------
        >>> group_analysis.print_avaiable_features()
        """

        print("Avaiable features:")
        for cl in self.tmp_data.columns:
            print(cl)

    def proportion_analysis(
        self,
        grouping_col: str = "sets",
        val_col: str = "nuclei_per_img",
        grouping_dict=None,
        omit=None,
    ):
        """
        Perform proportion analysis by comparing the distribution of values across groups.

        This method analyzes the distribution of values (e.g., nuclei counts) across different groups defined in the dataset. It can optionally group categories, omit specific values, and produces both statistical results and a visualization.

        Parameters
        ----------
        grouping_col : str, optional
            Column to group by. Default is 'sets'.

        val_col : str, optional
            Column containing the values to analyze. Default is 'nuclei_per_img'.

        grouping_dict : dict or None, optional
            Dictionary mapping new group names to categories in `grouping_col`. If None, analysis is based on the original groups.

        omit : str, list, or None, optional
            Values to exclude from the analysis. Default is None.

        Attributes
        ----------
        proportion_stats : pd.DataFrame
            DataFrame containing chi-square test results for pairwise group comparisons.

        proportion_plot : matplotlib.figure.Figure
            Plot visualizing the proportions across groups.

        Example
        -------
        >>> group_analysis.proportion_analysis(
        ...     grouping_col='sets',
        ...     val_col='nuclei_per_img',
        ...     grouping_dict={'Group A': [1, 2], 'Group B': [3, 4]},
        ...     omit=5
        ... )
        """

        andata = self.tmp_data.copy()

        andata[grouping_col] = list(self.tmp_metadata[grouping_col])

        andata = andata[[grouping_col, val_col]]

        if omit is not None:
            if isinstance(omit, list):
                andata = andata[~andata[val_col].isin(omit)]
            else:
                andata = andata[andata[val_col] != omit]

        andata = andata.reset_index(drop=True)
        andata["index_col"] = andata.index

        if isinstance(grouping_dict, dict):
            for k in grouping_dict.keys():
                andata.loc[
                    andata[grouping_col].isin(grouping_dict[k]), grouping_col
                ] = k

        df_pivot = andata.pivot_table(
            index=val_col,
            columns=grouping_col,
            values="index_col",
            aggfunc="count",
            fill_value=0,
        )

        chi_df = chi_pairs(df_pivot)

        self.proportion_stats = chi_pairs(df_pivot)

        chi_df["Significance_Label"] = chi_df["p-value"].apply(get_significance_label)

        self.proportion_plot = prop_plot(df_pivot, chi_df)

    def get_proportion_plot(self, show: bool = True):
        """
        Retrieve the proportion bar plot generated by the `proportion_analysis()` method.

        Parameters
        ----------
        show : bool, optional
            Whether to display the proportion bar plot. Default is True.

        Returns
        -------
        matplotlib.figure.Figure
            The figure object containing the proportion bar plot.
        """

        if self.proportion_plot is None:
            print(
                "\nNo results to return! Please run the proportion_analysis() method first."
            )
        else:
            if cfg._DISPLAY_MODE:
                if show:
                    self.proportion_plot
                    try:
                        display(self.proportion_plot)
                    except:
                        None

            return self.proportion_plot

    def get_proportion_stats(self):
        """
        Retrieve the proportion statistics computed by the `proportion_analysis()` method.

        Returns
        -------
        pd.DataFrame
            The proportion statistics stored in `self.proportion_stats`.
        """

        if None in self.proportion_stats:
            print(
                "\nNo results to return! Please run the proportion_analysis() method first."
            )
        else:
            return self.proportion_stats
