#! /usr/bin/env python

# Carries out comparison of checksum in files from given directory
# and in data from HDF5 archive.

GET_FILENAME_TAG = 0
REQUEST_FILENAME_TAG = 1

import argparse
from mpi4py import MPI
from pathlib import Path
from sys import argv
#from os.path import join, isdir, isfile, getsize, basename, dirname, relpath
import numpy as np
import h5py
from sys import stdout
import time
import blosc2
import hashlib
import pandas as pd
from functools import reduce
import logging
from os import walk
from humanize import intcomma

logger = logging.getLogger(__name__)
logging.basicConfig(stream=stdout)

def get_files_to_check(tdir: str) -> list:
    filelist=[]

    for root,dirs,files in walk(tdir):
        for file in files:
            filelist.append(join(root, file))
        print(f"\rfound {intcomma(len(filelist))} files", end="")

    filelist=[relpath(item, tdir) for item in filelist]

    return filelist

def uncompress_buffer(buffdata: bytes, method: str, **kwargs) -> bytes:
    if method.lower() == "bz2":
        return bz2.decompress(buffdata)
    elif method.lower() in ["blosc", "blosc2"]:
        return blosc2.decompress(buffdata)

# flatten a lists of list (returned by mpi.gather) to list:
def flatten_list(inlist: list[list]) -> list:
    return reduce(lambda x,y: x+y, inlist)

# carried out by rank 0. gather info from provided archives and run some checks
def check_archive_files(archive_files: list):
    n_archives = len(archive_files)

    multifile = False if n_archives == 1 else True

    filelist_inarch = dict()
    cmethods={}

    archive_numbers={}

    qc_passed=True

    nfiles_inarch = 0

    for archive_file in archive_files:
        logger.info(f'Reading HDF5 attributes from {archive_file}...')
        if not Path(archive_file).is_file():
            logger.error(f"archive file {archive_file} does not exist or is not a regular file.")
            return None, None, None, False

        with h5py.File(archive_file, 'r') as hfile:
            if multifile:
                n_archives2=hfile.attrs["hdf5_number_of_archive_files"]
                if n_archives != n_archives2:
                    logger.error(f"number of archives in {archive_file} is inconsistent with number of files passed to program.")
                    qc_passed=False

                filenum=hfile.attrs["hdf5_archive_file_number"]
            else:
                if "hdf5_number_of_archive_files" in hfile.attrs.keys():
                    logger.error(f"{archive_file} attribute suggets multi-file-archive, but only one HdF5 file was provided.")
                    qc_passed=False
                filenum=0

            archive_numbers[archive_file] = filenum

            cmethods[archive_file] = hfile.attrs["compression"] 
            if cmethods[archive_file] not in ["bz2", "blosc", "blosc2"]:
                logger.error(f"{archive_file} uses unknown compression method {cmethod}.")
                qc_passed=False

            logger.info(f'Reading __filelist__ from {archive_file}...')
            try:
                _ = hfile["__filelist__"]
            except KeyError:
                logger.error(f"Error. Archive {archive_file} does not contain entry __filelist__. Quitting.")
                return None, None, None, False

            filelist_inarch[archive_file] = [nbytes.tobytes().decode() for nbytes in hfile["__filelist__"]]

            nfiles_inarch+=len(filelist_inarch[archive_file])

    #logger.info(f'Obtaining list of files in {target_dir}...')
    #filelist_ondisk= get_files_to_check(target_dir)

    if set(archive_numbers.values()) != set(range(n_archives)):
        logger.error('inconsistent file numbering')
        qc_passed=False

    if len(set(cmethods.values())) != 1:
        logger.error(f'inconsistent compression methods found in archives')
        qc_passed=False

    cmethod=cmethods.popitem()[1]

    return filelist_inarch, cmethod, nfiles_inarch, qc_passed

def run_verification(archive_files: list, filelist_inarch: list, target_dir: Path, cmethod: str, rank: int, comm: MPI.Comm, progress_step:int=100):
    success = True
    error_files = []

    # checksum information to be collected and stored
    filesize_ondisk = []
    filesize_inarch = []

    md5_ondisk = []
    md5_inarch = []

    file_passed = []
    identified_archive = []

    filelist = []

    # open all HDF5 files
    hfile={archive_file: h5py.File(archive_file, 'r') for archive_file in archive_files}

    finished = False
    n=0

    #for n in range(nfiles):
    while not finished:
        if rank==1:
            if n % progress_step == 0:
                logger.info(f"Processing file number {n} on rank {rank}")

        logger.debug(f'rank {rank}: requesting file from 0')
        comm.send(None, dest=0, tag=REQUEST_FILENAME_TAG)
        logger.debug(f'rank {rank}: waiting to receive file to verify')
        filename = comm.recv(source=0, tag=GET_FILENAME_TAG)

        if filename is None:
            logger.debug(f'rank {rank}: no more files left to verify')
            break

        n+=1

        diskfile = target_dir.joinpath(filename)

        filelist.append(filename)

        odata=open(diskfile, "rb").read()
        filesize_ondisk.append(len(odata))

        dset_name = filename + "." + cmethod

        # find in which archive this dataset is stored

        archive_file=None

        for afile in archive_files:
            if filename in filelist_inarch[afile]:
                archive_file=afile

        identified_archive.append(archive_file)

        if archive_file is None:
            success=False
            logger.error(f"FAIL: {dset_name} not found in any archive file")
            error_files.append(filename + "(missing)")
            filesize_inarch.append(0)
            md5_inarch.append('N/A')
            md5_ondisk.append('N/A')
            file_passed.append(False)
        else:
            rdata=uncompress_buffer(hfile[archive_file][dset_name][:].tobytes(), cmethod)

            filesize_inarch.append(len(rdata))

            if len(odata) != len(rdata):
                success=False
                logger.error(f"FAIL: size of {diskfile} ({len(odata)}) does not match size of dataset {dset_name} ({len(rdata)}) in {archive_file}")
                error_files.append(diskfile + "(size)")
                file_passed.append(False)
            else:
                md5_ondisk.append(hashlib.md5(odata).hexdigest())
                md5_inarch.append(hashlib.md5(rdata).hexdigest())

                if md5_ondisk[-1] != md5_inarch[-1]:
                    success=False
                    logger.error(f"FAIL: checksum {md5_ondisk[-1]} of {diskfile} != {md5_inarch[-1]} of {dset_name} in {archive_file}")
                    error_files.append(diskfile + "(md5)")
                    file_passed.append(False)
                else:
                    file_passed.append(True)

    for f in hfile.values():
        f.close()

    return success, file_passed, error_files, filesize_ondisk, filesize_inarch, md5_ondisk, md5_inarch, filelist, identified_archive

# this function is called by rank 0.  It scans the target directory for files and continuously passed the
# names of files it found to the other ranks, which do the verification
def scan_and_distribute_files(target_dir:Path, comm: MPI.Comm, ncpus:int, nfiles_inarch: int, progress_step:int=1000):
    if not target_dir.is_dir():
        logger.error(f"Target directory {target_dir} not found. Aborting.")
        comm.Abort()

    status=MPI.Status()
    nfiles_ondisk=0

    filelist_ondisk=[]

    for p in target_dir.rglob('*'):
        if p.is_file():
            filename_r = p.relative_to(target_dir)
            logger.debug(f"Rank 0: accepting request for filename...")

            comm.recv(None, source=MPI.ANY_SOURCE, tag=REQUEST_FILENAME_TAG, status=status)

            destination=status.Get_source()

            logger.debug(f"Rank 0: ready to send out filename {filename_r} to {destination}")
            comm.send(filename_r.as_posix(), dest=destination, tag=GET_FILENAME_TAG)
            nfiles_ondisk+=1

            if nfiles_ondisk % progress_step == 0:
                logger.info(f"Found {nfiles_ondisk} out of {nfiles_inarch} files, still scanning ...")

            filelist_ondisk.append(filename_r.as_posix())

    # notify each other rank that there are no more files left

    other_ranks = set([a for a in range(1, ncpus)])
    for n in range(1,ncpus):
        comm.recv(None, source=MPI.ANY_SOURCE, tag=REQUEST_FILENAME_TAG, status=status)
        destination=status.Get_source()
        logger.debug(f"Rank 0: sending None (= no more files to verify) to {destination}")
        comm.send(None, dest=destination, tag=GET_FILENAME_TAG)
        other_ranks.remove(destination)

    if len(other_ranks) > 0:
        logger.error(f"Ranks {other_ranks} were not notified of end of file scanning.")

    return nfiles_ondisk, filelist_ondisk

def compare_archive_checksums(target_dir: str, archive_files: str, summary_file: str|None):

    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    ncpus=comm.Get_size()

    # read the contents of each archive. make available to all ranks.
    if rank==0:
        filelist_inarch, cmethod, nfiles_inarch, qc_passed = check_archive_files(archive_files)
        if not qc_passed:
            logger.error("Archive files failed initial quality control")
            comm.Abort()

    else:
        filelist_inarch = {}
        cmethod=None
     
    filelist_inarch = comm.bcast(filelist_inarch, root=0)
    cmethod = comm.bcast(cmethod, root=0)

    if rank==0:
        nfiles_ondisk,filelist_ondisk=scan_and_distribute_files(target_dir, comm, ncpus, nfiles_inarch)
        logger.debug(f"Rank 0: done scanning, found {nfiles_ondisk}")

        success = True
        filesize_ondisk = []
        filesize_inarch = []
        md5_ondisk = []
        md5_inarch = []
        file_passed = []
        identified_archive = []
        filelist_ondisk = []
        error_files = []

    else:
        success, file_passed, error_files, filesize_ondisk, filesize_inarch, md5_ondisk, md5_inarch, filelist_ondisk, identified_archive = \
            run_verification(archive_files, filelist_inarch, target_dir, cmethod, rank, comm)

    comm.Barrier()

    # gather information from different processes
    overall_sucess = comm.allreduce(success, op=MPI.MIN)
    error_files_all = comm.gather(error_files)

    if rank==0:
        if overall_sucess:
            logger.info(f"archive(s) {archive_files} passed.")
        else:
            logger.error(f"archive(s) {archive_files} FAILED!.  The following files had errors:")
            logger.error(error_files_all)

    if summary_file is not None:

        filesize_ondisk_all = comm.gather(filesize_ondisk, root=0)
        filesize_inarch_all = comm.gather(filesize_inarch, root=0)
        
        md5_ondisk_all = comm.gather(md5_ondisk, root=0)
        md5_inarch_all = comm.gather(md5_inarch, root=0)

        file_passed_all = comm.gather(file_passed, root=0)
        # get the file list in the same order as the verification parameters
        filenames_all = comm.gather(filelist_ondisk, root=0)

        archives_all = comm.gather(identified_archive, root=0)

        if rank==0:
            filesize_ondisk_all

            summary_info=pd.DataFrame(
                    {"size_orig": flatten_list(filesize_ondisk_all),
                        "size_arch": flatten_list(filesize_inarch_all),
                        "md5_orig": flatten_list(md5_ondisk_all),
                        "md5_arch": flatten_list(md5_inarch_all),
                        "archive": flatten_list(archives_all),
                        "passed": flatten_list(file_passed_all)
                        },
                    index=flatten_list(filenames_all)
                    )

            summary_info.index.name = "filename"
            summary_info.to_json(summary_file)

    comm.Barrier()

            
def main():
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
                prog='hdf5vault_check',
                description='Parallel tool to verify contents of archive ')

    parser.add_argument('-d', '--directory', required=True, type=str, help='name of directory to verify archive content against')
    parser.add_argument('-f', '--files', nargs="+", required=True, type=str, help="HDF5 archive file(s)")
    parser.add_argument('-j', '--json', required=False, type=str, help='JSON summary file (default: None)')

    args=parser.parse_args()

    rank=MPI.COMM_WORLD.Get_rank()

    target_dir = Path(args.directory)
    archive_files = args.files
    summary_file = args.json

    if rank==0:
        logger.info(f"Checking directory {target_dir} against archvive file(s) {archive_files}.")

    compare_archive_checksums(target_dir, archive_files, summary_file)

if __name__ == '__main__':
    main()
