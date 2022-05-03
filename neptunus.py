#!/usr/bin/env python3

"""
This is the very same as deus, but specialized
to work with tsunami grids.
The idea is the same as for volcanus to provide
the deus interface with a specialized intensity provider.
"""

import argparse
import glob
import os

import tellus

import fragility
import gpdexposure
import intensityprovider
import loss
import rasterintensityprovider


def main():
    """
    Runs the main method, which reads from
    the files,
    updates each exposure cell individually
    and prints out all of the updated exposure cells.
    """
    argparser = argparse.ArgumentParser(
        description="Updates the exposure model and the damage "
        + "classes of the Buildings"
    )
    argparser.add_argument(
        "intensity_file", help="File with tsunami wave height data"
    )
    argparser.add_argument("intensity_name", help="Name of the intensity")
    argparser.add_argument("intensity_unit", help="Unit of the intensity")
    argparser.add_argument("exposure_file", help="File with the exposure data")
    argparser.add_argument(
        "exposure_schema", help="The actual schema for the exposure data"
    )
    argparser.add_argument(
        "fragilty_file", help="File with the fragility function data"
    )
    argparser.add_argument(
        "--merged_output_file",
        default="output_merged.json",
        help="Filename for the merged output from all others",
    )
    current_dir = os.path.dirname(os.path.realpath(__file__))
    loss_data_dir = os.path.join(current_dir, "loss_data")
    files = glob.glob(os.path.join(loss_data_dir, "*.json"))
    loss_provider = loss.LossProvider.from_files(files, "USD")

    args = argparser.parse_args()

    intensity_provider = (
        rasterintensityprovider.RasterIntensityProvider.from_file(
            args.intensity_file,
            intensity=args.intensity_name,
            unit=args.intensity_unit,
        )
    )
    # ID for inundation (out of the maximum wave height)
    intensity_provider = intensityprovider.AliasIntensityProvider(
        intensity_provider,
        aliases={
            "ID": ["MWH"],
        },
    )
    fragility_provider = fragility.Fragility.from_file(
        args.fragilty_file
    ).to_fragility_provider()
    old_exposure = gpdexposure.read_exposure(args.exposure_file)

    worker = tellus.Child(
        intensity_provider,
        fragility_provider,
        old_exposure,
        args.exposure_schema,
        loss_provider,
        args,
    )
    worker.run()


if __name__ == "__main__":
    # Currently we can't pickle the raster intensity, so no parallel
    # processing is possible.
    gpdexposure.PARALLEL_PROCESSING = False
    main()
